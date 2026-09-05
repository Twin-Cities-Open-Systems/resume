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
# Usage:
#   media/spencer/deploy.sh lab      -- build (incl. minify) + sync to lab only
#   media/spencer/deploy.sh promote  -- build the same way, sync lab AGAIN (so
#                              what you approved on lab is exactly what
#                              ships), then push to prod, then verify
#                              lab == prod byte-for-byte
# Requires: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID (or run via
# hee-cred) for `promote`; real SSH access to `pve` for both.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEDIA_ROOT="$SCRIPT_DIR/dist"
OWN_JS=("shell-toggles.js" "shell-freshness.js")

cmd="${1:-}"
if [ "$cmd" != "lab" ] && [ "$cmd" != "promote" ]; then
  echo "usage: $0 lab|promote" >&2
  exit 1
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -r "$MEDIA_ROOT"/. "$STAGE/"
rm -f "$STAGE/.assetsignore"
cp "$MEDIA_ROOT/.assetsignore" "$STAGE/.assetsignore" 2>/dev/null || true
find "$STAGE" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

echo "=== minifying our own JS (never the tracked source) ==="
for js in "${OWN_JS[@]}"; do
  if [ -f "$STAGE/$js" ]; then
    npx --yes terser@5.50.0 "$STAGE/$js" -o "$STAGE/$js" --compress --mangle
    echo "  $js: $(wc -c < "$MEDIA_ROOT/$js") -> $(wc -c < "$STAGE/$js") bytes"
  fi
done

echo "=== syncing lab (pve container 107) ==="
tar -C "$STAGE" -cf - --exclude=deploy.sh --exclude=__pycache__ --exclude=.assetsignore . \
  | ssh pve "pct exec 107 -- tar -C /www/spencer-media -xf -"

if [ "$cmd" = "lab" ]; then
  echo "=== lab updated. review at https://spencer.media.lab.tcos.us -- run './deploy.sh promote' when approved ==="
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
npx --yes wrangler@4.86.0 deploy --name tcos-media --assets . --compatibility-date=2026-08-20

echo "=== verifying lab == prod ==="
# every item's two pages, not a hand-kept list -- a new item is one more
# directory with an item.card.v1.yaml, nothing to remember here
ITEM_PAGES="index.html"
for card in "$MEDIA_ROOT"/*/item.card.v1.yaml "$MEDIA_ROOT"/tux-tattoo/index.html; do
  [ -f "$card" ] || continue
  d="$(basename "$(dirname "$card")")"; ITEM_PAGES="$ITEM_PAGES $d/index.html $d/exif.html"
done
for f in $ITEM_PAGES; do
  prod=$(curl -sL "https://spencer.media.tcos.us/$f" | md5sum | cut -d' ' -f1)
  lab=$(ssh pve "pct exec 103 -- curl -sL -H 'Host: spencer.media.lab.tcos.us' 'http://localhost/$f'" 2>/dev/null | md5sum | cut -d' ' -f1)
  if [ "$prod" = "$lab" ]; then
    echo "  $f: match"
  else
    echo "  $f: MISMATCH (prod=$prod lab=$lab)" >&2
  fi
done
