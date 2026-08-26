#!/usr/bin/env bash
# Real deploy step for spencer.media.tcos.us -- syncs lab first, then
# deploys the *exact same bytes* to prod. Real policy (Spencer,
# 2026-08-26): "for the release, must be from real lab" -- lab is the
# source of truth, prod is a verbatim promotion of it, not an
# independently-generated copy.
#
# Real bug this replaces: an earlier version of this script
# substituted a fresh data-generated timestamp into the STAGED copy on
# every prod deploy, without writing it back to the tracked source or
# to lab -- so prod's "last update" kept advancing while lab and git
# stayed frozen at whatever was last hand-edited, a real, silent
# lab/prod drift caught live via an MD5 diff. Freshness is now set
# once, at real edit time (whoever changes the content updates
# data-generated themselves, same discipline as any other real edit),
# and this script never touches it -- it just promotes what's real.
#
# Usage: ./deploy.sh
# Requires: CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID set (or run
# via hee-cred), wrangler available via npx, real SSH access to `pve`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEDIA_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== syncing lab (pve container 107) ==="
tar -C "$MEDIA_ROOT" -cf - --exclude=deploy.sh --exclude=__pycache__ --exclude=.assetsignore --exclude=regen-keys.py . \
  | ssh pve "pct exec 107 -- tar -C /www/spencer-media -xf -"

echo "=== deploying the same bytes to prod ==="
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -r "$MEDIA_ROOT"/* "$STAGE/"
cp "$MEDIA_ROOT/.assetsignore" "$STAGE/.assetsignore" 2>/dev/null || true

: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (or run this via hee-cred)}"
: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID}"

cd "$STAGE"
npx --yes wrangler@4.86.0 deploy --name tcos-media --assets . --compatibility-date=2026-08-20

echo "=== verifying lab == prod ==="
for f in index.html tux-tattoo/index.html tux-tattoo/exif.html; do
  prod=$(curl -sL "https://spencer.media.tcos.us/$f" | md5sum | cut -d' ' -f1)
  lab=$(ssh pve "pct exec 103 -- curl -sL -H 'Host: spencer.media.lab.tcos.us' 'http://localhost/$f'" 2>/dev/null | md5sum | cut -d' ' -f1)
  if [ "$prod" = "$lab" ]; then
    echo "  $f: match"
  else
    echo "  $f: MISMATCH (prod=$prod lab=$lab)" >&2
  fi
done
