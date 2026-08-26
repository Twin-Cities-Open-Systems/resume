#!/usr/bin/env bash
# Real deploy step for spencer.media.tcos.us -- replaces the manual
# copy-to-staging-dir dance this session was doing by hand, and fixes
# the real "lie" bug Spencer caught: data-generated was hand-typed
# once and never updated through many later edits, so the page's own
# "updated Xh Ym ago" freshness indicator was stale/wrong. This
# substitutes the real current UTC time on every deploy.
#
# Usage: ./deploy.sh
# Requires: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID set (or run
# via hee-cred), wrangler available via npx.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEDIA_ROOT="$(dirname "$SCRIPT_DIR")"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

cp -r "$MEDIA_ROOT"/* "$STAGE/"
cp "$MEDIA_ROOT/.assetsignore" "$STAGE/.assetsignore" 2>/dev/null || true

NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 -c "
import re
path = '$STAGE/tux-tattoo/index.html'
with open(path) as f:
    content = f.read()
content = re.sub(r'data-generated=\"[^\"]*\"', 'data-generated=\"$NOW\"', content, count=1)
with open(path, 'w') as f:
    f.write(content)
print('data-generated -> $NOW')
"

: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (or run this via hee-cred)}"
: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"

cd "$STAGE"
npx --yes wrangler@4.86.0 deploy --name tcos-media --assets . --compatibility-date=2026-08-20
