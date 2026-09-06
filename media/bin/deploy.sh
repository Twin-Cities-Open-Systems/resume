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
echo "=== promoting: deploying the exact same (already-synced) bytes to prod ==="
: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (or run this via hee-cred)}"
: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"

cd "$STAGE"
npx --yes wrangler@4.86.0 deploy --name "$WORKER" --assets . --compatibility-date=2026-08-20

echo "=== verifying lab == prod ==="
# every item's two pages, not a hand-kept list -- a new item is one more
# directory with an item.card.v1.yaml, nothing to remember here
ITEM_PAGES="index.html"
for card in "$MEDIA_ROOT"/*/item.card.v1.yaml "$MEDIA_ROOT"/tux-tattoo/index.html; do
  [ -f "$card" ] || continue
  d="$(basename "$(dirname "$card")")"; ITEM_PAGES="$ITEM_PAGES $d/index.html $d/exif.html"
done
for f in $ITEM_PAGES; do
  prod=$(curl -sL "https://$MEDIA_HOST/$f" | md5sum | cut -d' ' -f1)
  lab=$(ssh pve "pct exec 103 -- curl -sL -H 'Host: $LAB_HOST' 'http://localhost/$f'" 2>/dev/null | md5sum | cut -d' ' -f1)
  if [ "$prod" = "$lab" ]; then
    echo "  $f: match"
  else
    echo "  $f: MISMATCH (prod=$prod lab=$lab)" >&2
  fi
done
