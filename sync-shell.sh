#!/bin/sh
# sync-shell.sh -- copy tcos-app's shared shell into this repo's two web roots,
# or check that the copies have not drifted.
#
#   sync-shell.sh [--check] [TCOS_APP_DIR]
#
# tcos-app OWNS the files named in its shell.manifest (operator, 2026-10-01:
# tcos-app is the home of every TCOS web page); the copies here are derived and
# never edited by hand. They live in media/shared/, which media/bin/deploy.sh
# stages at the root of every <who>.media host; convert.sh copies them into dist/
# (build output) for the blog and media hub pages. TCOS_APP_DIR
# defaults to $TCOS_APP_DIR, then ~/git/tcos-app. --check changes nothing and
# exits 1 on any difference.
set -eu
check=0
if [ "${1:-}" = "--check" ]; then check=1; shift; fi
case "${1:-}" in
  -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
esac
src="${1:-${TCOS_APP_DIR:-$HOME/git/tcos-app}}"
here="$(cd "$(dirname "$0")" && pwd)"
[ -f "$src/shell.manifest" ] || { echo "CRITICAL: $src/shell.manifest not found -- pass a tcos-app checkout" >&2; exit 2; }
bad=0
dest=media/shared
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if [ "$check" = 1 ]; then
    cmp -s "$src/$f" "$here/$dest/$f" || { echo "DRIFT: $dest/$f differs from tcos-app" >&2; bad=1; }
  else
    mkdir -p "$here/$dest/$(dirname "$f")"
    cp "$src/$f" "$here/$dest/$f"
    echo "synced $dest/$f"
  fi
done < "$src/shell.manifest"
[ "$bad" = 0 ] || { echo "run: sh sync-shell.sh   (then commit)" >&2; exit 1; }
[ "$check" = 0 ] || echo "shell matches tcos-app"
