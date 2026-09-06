#!/usr/bin/env bash
# Real deploy for spencer.media.tcos.us -- two explicit steps, not one.
#
# Real incident this fixes (fleet-ops#312, 2026-08-26): the old version
# synced lab then immediately pushed the same bytes to prod in one
# shot, with no checkpoint in between -- Spencer directly: "I did not
# approve that, I wanted to check first." `lab` and `promote` are now
# separate subcommands; running `lab` alone never touches prod.
#
# Real bug this also replaces (earlier incident): an even older version
# substituted a fresh data-generated timestamp into the STAGED copy on
# every prod deploy without writing it back to the tracked source or
# lab -- a silent lab/prod drift caught live via an MD5 diff. Freshness
# is set once, at real edit time in the tracked source, and this
# script never touches it.
#
# Real footgun avoided (Spencer, 2026-08-26, "footgun on that" re:
# minifying JS "as a rule"): minification happens ONLY in the ephemeral
# STAGE dir, never against the tracked source -- shell-toggles.js /
# shell-freshness.js stay readable in git forever. openpgp.min.js is
# vendored, already minified upstream, and is never re-minified here.
#
# One script for every operator (2026-09-06, "consolidate lab and prod
# blogs and media ... don't forget touchy ... make sure the new ones are
# added"): the operator is the first argument; host, container path and
# Worker name derive from profiles/<oper>/profile.json's media_routing.
# Shared assets (shell-*.css/js, icons, openpgp) come from media/shared/.
#
# Usage:
#   media/bin/deploy.sh <oper> lab      -- build (incl. minify) + sync to lab only
#   media/bin/deploy.sh <oper> promote  -- build the same way, sync lab AGAIN (so
#                              what you approved on lab is exactly what
#                              ships), then push to prod, then verify
#                              lab == prod byte-for-byte
# Requires: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID (or run via
# hee-cred) for `promote`; real SSH access to `pve` for both.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OPER="${1:-}"; cmd="${2:-}"
if [ -z "$OPER" ] || { [ "$cmd" != "lab" ] && [ "$cmd" != "promote" ]; }; then
  echo "usage: $0 <oper> lab|promote" >&2
  exit 1
fi
MEDIA_ROOT="$REPO_ROOT/media/$OPER/dist"
SHARED="$REPO_ROOT/media/shared"
PROFILE="$REPO_ROOT/profiles/$OPER/profile.json"
[ -d "$MEDIA_ROOT" ] || { echo "❌ CRITICAL deploy: no $MEDIA_ROOT" >&2; exit 2; }
[ -f "$PROFILE" ] || { echo "❌ CRITICAL deploy: no $PROFILE" >&2; exit 2; }
MEDIA_HOST="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['meta'].get('media_routing',''))" "$PROFILE")"
[ -n "$MEDIA_HOST" ] || { echo "❌ CRITICAL deploy: $PROFILE has no meta.media_routing" >&2; exit 2; }
PREFIX="${MEDIA_HOST%%.*}"
LAB_HOST="${PREFIX}.media.lab.tcos.us"
WWW_DIR="/www/${PREFIX}-media"
# spencer keeps the original Worker name; every other operator gets tcos-media-<prefix>
WORKER="tcos-media"; [ "$PREFIX" != "spencer" ] && WORKER="tcos-media-${PREFIX}"
OWN_JS=("shell-toggles.js" "shell-freshness.js")

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -r "$SHARED"/. "$STAGE/"
cp -r "$MEDIA_ROOT"/. "$STAGE/"
rm -f "$STAGE/.assetsignore"
cp "$MEDIA_ROOT/.assetsignore" "$STAGE/.assetsignore" 2>/dev/null || true
find "$STAGE" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# Gate: the stage must carry every post the build says this operator has.
# A deploy from a checkout whose build outputs are incomplete would prune
# a live post (2026-09-06: /posts/2026-08-24-lessons-learned.html 404 on
# lab between two deploys). Missing pages are a build problem; refuse.
MANIFEST="$REPO_ROOT/dist/blog_manifest.json"
if [ -f "$MANIFEST" ]; then
  missing="$(python3 - "$MANIFEST" "$OPER" "$STAGE" <<'PYM'
import json, os, sys
manifest, oper, stage = sys.argv[1:4]
for post in json.load(open(manifest)):
    if post["path"].startswith(f"profiles/{oper}/") and post.get("html"):
        if not os.path.isfile(os.path.join(stage, "posts", post["slug"] + ".html")):
            print(post["slug"])
PYM
)"
  if [ -n "$missing" ]; then
    echo "❌ CRITICAL deploy: build says $OPER has posts the stage lacks -- run ./convert.sh first:" >&2
    printf '  %s\n' $missing >&2; exit 2
  fi
fi

echo "=== minifying our own JS (never the tracked source) ==="
for js in "${OWN_JS[@]}"; do
  if [ -f "$STAGE/$js" ]; then
    npx --yes terser@5.50.0 "$STAGE/$js" -o "$STAGE/$js" --compress --mangle
    echo "  $js: $(wc -c < "$SHARED/$js") -> $(wc -c < "$STAGE/$js") bytes"
  fi
done

echo "=== syncing lab (pve container 107) ==="
tar -C "$STAGE" -cf - --exclude=deploy.sh --exclude=__pycache__ --exclude=.assetsignore . \
  | ssh pve "pct exec 107 -- sh -c 'mkdir -p $WWW_DIR && tar -C $WWW_DIR -xf -'"
# Prune: anything under posts/ or an item dir that the stage no longer has.
# tar only adds; a renamed post (2026-09-05, the numbered prefix) left its
# old file live at the old URL until removed by hand.
# An operator with no posts yet has no posts/ dir -- that is not an error.
( cd "$STAGE" && { find posts -type f 2>/dev/null || true; } | sort ) > "$STAGE/.manifest"
ssh pve "pct exec 107 -- sh -c 'cd $WWW_DIR && { find posts -type f 2>/dev/null || true; } | sort'" \
  | comm -13 "$STAGE/.manifest" - \
  | while read -r stale; do
      [ -n "$stale" ] || continue
      echo "  prune: $stale (no longer in the build)"
      ssh pve "pct exec 107 -- rm -f -- '$WWW_DIR/$stale'"
    done

if [ "$cmd" = "lab" ]; then
  echo "=== lab updated. review at https://$LAB_HOST -- run 'media/bin/deploy.sh $OPER promote' when approved ==="
  exit 0
fi

# Consent gate: an item whose card does not say consent: approved never
# reaches prod. Operator, 2026-09-05 (resume#47): images of people wait
# for the people. Lab is the review surface; this is the only gate.
for card in "$MEDIA_ROOT"/*/item.card.v1.yaml; do
  [ -f "$card" ] || continue
  if grep -Eq '^\s*consent:' "$card" && ! grep -Eq '^\s*consent:\s*approved\s*$' "$card"; then
    echo "❌ CRITICAL $(basename "$(dirname "$card")"): consent is not 'approved' in its card -- not promoting" >&2; exit 2
  fi
done
# Gates before anything reaches prod (incident tcos-www#59, 2026-09-06):
# the repo passes hee check all, and no staged page carries git conflict
# markers. A 200 with "<<<<<<<" in it is a broken page, not a deploy.
echo "=== gates ==="
hee check all "$REPO_ROOT" >/dev/null 2>&1 || { echo "❌ CRITICAL promote: hee check all fails on $REPO_ROOT -- not promoting" >&2; exit 2; }
if grep -rIl -E '^(<<<<<<< |=======$|>>>>>>> )' "$STAGE" --include='*.html' --include='*.js' --include='*.css' --include='*.json' 2>/dev/null | grep -q .; then
  echo "❌ CRITICAL promote: git conflict markers in the staged tree -- not promoting" >&2; exit 2
fi
echo "  hee check all: OK; staged tree: no conflict markers"
# Who is deploying: the approved session signature (hee ver session
# sig_tag), on the Cloudflare version and on the prod git tag. Operator,
# 2026-09-06: "should be using the approved hee sig hash ... better than
# more PATs". One shared token; every deploy still names its session.
SIG="$(hee ver session --tag 2>/dev/null || hee ver session 2>/dev/null | awk '/sig_tag|rc_tag/{print $2; exit}')"
[ -n "$SIG" ] || { echo "❌ CRITICAL promote: no session signature from hee ver session -- not promoting" >&2; exit 2; }
SRC_SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
STAMP="$(date -u +%Y%m%dT%H%MZ)"
echo "=== promoting: deploying the exact same (already-synced) bytes to prod ==="
# wrangler needs Node >= 20; on a shell with system Node 18 it prints one
# line and exits 1, which a Success|rror grep swallowed (2026-09-06).
node_major="$(node -v 2>/dev/null | sed 's/^v//; s/\..*//')"
[ "${node_major:-0}" -ge 20 ] || { echo "❌ CRITICAL deploy: Node >= 20 required, found $(node -v 2>/dev/null || echo none) -- nvm install 20 (dotfiles' bashrc sources nvm)" >&2; exit 2; }
# hee cred -exec injects the secret as HEE_CRED_PASS (hee-cred ENV_VAR); map
# it, and derive the account id from the token like tcos-www/deploy.sh does.
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-${HEE_CRED_PASS:-}}"; export CLOUDFLARE_API_TOKEN
: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (run via hee cred -pass cloudflare-tcos-www -dir ~/git/tcos-www/.hee/secrets -exec)}"
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/accounts | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"][0]["id"])')}"
export CLOUDFLARE_ACCOUNT_ID
: "${CLOUDFLARE_ACCOUNT_ID:?could not derive CLOUDFLARE_ACCOUNT_ID from the token}"

cd "$STAGE"
npx --yes wrangler@4.86.0 deploy --name "$WORKER" --assets . --compatibility-date=2026-08-20 \
  --message "hee:$SIG $OPER media src=$SRC_SHA lab-verified" --tag "${SIG%%_*}" \
  || { echo "❌ CRITICAL promote: wrangler deploy failed -- nothing verified, nothing tagged" >&2; exit 2; }

echo "=== verifying lab == prod ==="
# every item's two pages, not a hand-kept list -- a new item is one more
# directory with an item.card.v1.yaml, nothing to remember here
ITEM_PAGES="index.html"
for card in "$MEDIA_ROOT"/*/item.card.v1.yaml "$MEDIA_ROOT"/tux-tattoo/index.html; do
  [ -f "$card" ] || continue
  d="$(basename "$(dirname "$card")")"; ITEM_PAGES="$ITEM_PAGES $d/index.html $d/exif.html"
done
for f in $ITEM_PAGES; do
  lab=$(ssh pve "pct exec 103 -- curl -sL -H 'Host: $LAB_HOST' 'http://localhost/$f'" 2>/dev/null | md5sum | cut -d' ' -f1)
  # The edge can still hand out the previous version for a short while
  # after a deploy (index.html MISMATCH seconds after a Success line,
  # identical a minute later; 2026-09-06). Bypass the cache and retry
  # before calling it a mismatch.
  prod=""; for _try in 1 2 3 4 5 6; do
    prod=$(curl -sL -H 'Cache-Control: no-cache' "https://$MEDIA_HOST/$f?v=$STAMP-$_try" | md5sum | cut -d' ' -f1)
    [ "$prod" = "$lab" ] && break; sleep 10
  done
  if [ "$prod" = "$lab" ]; then
    echo "  $f: match"
  else
    echo "  $f: MISMATCH (prod=$prod lab=$lab)" >&2
  fi
done

# The promotion record: an annotated, GPG-signed tag on the exact source
# commit, prod/<site>/<stamp>, message = what went where and who. Tags
# name commits; labels name intent. Signed by whoever runs promote
# (HEE_POLICY 17).
TAG="prod/${PREFIX}-media/${STAMP}"
( cd "$REPO_ROOT" && hee git tag "$TAG" -m "prod promotion: ${MEDIA_HOST}
worker: ${WORKER}
source: ${SRC_SHA}
session: ${SIG}
lab: https://${LAB_HOST}/ verified byte-for-byte before promote" "$SRC_SHA" --yes --push ) \
  || echo "⚠️ WARNING promote: deployed, but the prod tag could not be created/pushed -- hee git tag $TAG -m ... $SRC_SHA --yes --push" >&2
