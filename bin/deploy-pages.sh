#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# deploy-pages.sh
# The Cloudflare Pages side of resume (blog.tcos.us, media.tcos.us, every
# <prefix>.blog.tcos.us): build, gate, lab, promote -- two explicit steps,
# never one (HEE_POLICY 17). Until 2026-09-06 this surface shipped by a bare
# `wrangler pages deploy dist` with no gate, no session on the deployment and
# no prod tag; its last deploy was 2026-08-30, which is why every old blog
# URL still answered 200 a week after the redirect worker was written.
#
#   bin/deploy-pages.sh lab       ./convert.sh (dist + the redirect worker),
#                                 gate, push dist to the view container, run
#                                 media-item audit against lab
#   bin/deploy-pages.sh promote   clean tree on origin/main, rebuild from that
#                                 commit, gate, `wrangler pages deploy` with
#                                 the session signature as the commit message,
#                                 media-item audit --prod, GPG-signed
#                                 prod/resume-pages/<stamp> tag
#
# Requires: hee on PATH, ~/git/.github (lab), ssh to pve (lab), and for
# promote the sealed token:
#   hee cred -pass cloudflare-tcos-www -dir ~/git/tcos-www/.hee/secrets -exec bin/deploy-pages.sh promote
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cmd="${1:-}"
[ "$cmd" = lab ] || [ "$cmd" = promote ] || { echo "usage: $0 lab|promote" >&2; exit 1; }
PROJECT=resume
cd "$HERE"

if [ "$cmd" = promote ]; then
  # Prod deploys a commit that is on main; checked before anything is built.
  if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "❌ CRITICAL promote: uncommitted changes -- commit and merge first, prod deploys a commit" >&2; exit 2
  fi
  git fetch -q origin main
  if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "❌ CRITICAL promote: HEAD $(git rev-parse --short HEAD) is not origin/main $(git rev-parse --short origin/main) -- git switch main && git pull" >&2; exit 2
  fi
fi

# Build in a throwaway worktree of HEAD, never in the checkout: convert.sh
# rewrites 18 tracked files (dist/*.html, posts, profiles/*/dist/resume.*),
# so building here left the operator's tree dirty after every promote and
# the next promote refused (2026-09-06). The checkout stays exactly as it
# was; what ships is what the commit builds to.
BUILD="$(mktemp -d)"; LOG="$(mktemp)"
cleanup() { git worktree remove --force "$BUILD" >/dev/null 2>&1 || rm -rf "$BUILD"; rm -f "$LOG" "$LOG.mjs"; }
trap cleanup EXIT
git worktree add -q --detach "$BUILD" HEAD
echo "=== build (worktree of $(git rev-parse --short HEAD): convert.sh -> dist/, blog-redirect-worker -> dist/_worker.js) ==="
( cd "$BUILD" && ./convert.sh ) >"$LOG" 2>&1 || { echo "❌ CRITICAL build: convert.sh failed -- last lines:" >&2; tail -15 "$LOG" >&2; exit 2; }
cd "$BUILD"
[ -s dist/_worker.js ] || { echo "❌ CRITICAL build: dist/_worker.js missing -- the blog->media redirect would not ship" >&2; exit 2; }
[ -s dist/people.json ] || { echo "❌ CRITICAL build: dist/people.json missing -- the hubs would be empty" >&2; exit 2; }

echo "=== gates ==="
hee check all "$HERE" >/dev/null 2>&1 || { echo "❌ CRITICAL deploy: hee check all fails on $HERE -- stopping" >&2; exit 2; }
if grep -rIl -E '^(<<<<<<< |=======$|>>>>>>> )' dist --include='*.html' --include='*.js' --include='*.json' 2>/dev/null | grep -q .; then
  echo "❌ CRITICAL deploy: git conflict markers in dist -- stopping" >&2; exit 2
fi
for f in dist/index.html dist/blog-hub.html dist/media-hub.html; do
  grep -q 'gtag/js?id=G-' "$f" || { echo "❌ CRITICAL deploy: $f has no Google tag -- stopping" >&2; exit 2; }
done
# Every page Pages serves carries the Open Graph set (2026-09-06 sweep:
# two stale pages at the dist root had a <title> and nothing else).
for page in $(find dist -name '*.html' | sort); do
  for t in og:title og:description og:url; do
    grep -q "property=\"$t\"" "$page" || { echo "❌ CRITICAL deploy: $page has no $t -- every served page carries the Open Graph set" >&2; exit 2; }
  done
done
# Every image Pages serves carries the org branding (the favicons are
# copied from dist/icons at build time; both were bare until 2026-09-06).
for img in $(find dist -type f \( -name '*.png' -o -name '*.jpg' -o -name '*.gif' \) | sort); do
  [ -n "$(exiftool -s3 -XMP-dc:Publisher "$img" 2>/dev/null)" ] || { echo "❌ CRITICAL deploy: $img has no org branding metadata -- hee exif brand $img" >&2; exit 2; }
done
# the worker is an ES module (export default), so --check it as one
cp dist/_worker.js "$LOG.mjs" && node --check "$LOG.mjs" 2>/dev/null && rm -f "$LOG.mjs" \
  || { echo "❌ CRITICAL deploy: dist/_worker.js does not parse" >&2; rm -f "$LOG.mjs"; exit 2; }
echo "  hee check all: OK; no conflict markers; tag on the three hubs; worker parses"

if [ "$cmd" = lab ]; then
  make -C "$HOME/git/.github" RESUME="$BUILD" lab-blog >/dev/null
  echo "=== audit (lab) ==="
  python3 media/bin/media-item.py audit || true
  echo "=== lab updated -- review https://blog.lab.tcos.us and https://media.lab.tcos.us, then bin/deploy-pages.sh promote ==="
  exit 0
fi

SIG="$(hee ver session --tag 2>/dev/null || hee ver session 2>/dev/null | awk '/sig_tag|rc_tag/{print $2; exit}')"
[ -n "$SIG" ] || { echo "❌ CRITICAL promote: no session signature from hee ver session" >&2; exit 2; }
SRC_SHA="$(git rev-parse --short HEAD)"
STAMP="${RELEASE_VERSION:-$(date -u +%Y%m%dT%H%MZ)}"   # prod/resume-pages/<version> under hee release
# wrangler needs Node >= 20; on a shell with system Node 18 it prints one
# line and exits 1, which a Success|rror grep swallowed (2026-09-06).
node_major="$(node -v 2>/dev/null | sed 's/^v//; s/\..*//')"
[ "${node_major:-0}" -ge 20 ] || { echo "❌ CRITICAL deploy: Node >= 20 required, found $(node -v 2>/dev/null || echo none) -- nvm install 20 (dotfiles' bashrc sources nvm)" >&2; exit 2; }
# hee cred -exec injects the secret as HEE_CRED_PASS (hee-cred ENV_VAR).
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-${HEE_CRED_PASS:-}}"; export CLOUDFLARE_API_TOKEN
: "${CLOUDFLARE_API_TOKEN:?run via hee cred -pass cloudflare-tcos-www -dir ~/git/tcos-www/.hee/secrets -exec}"
CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/accounts | python3 -c 'import sys,json; print(json.load(sys.stdin)["result"][0]["id"])')}"
export CLOUDFLARE_ACCOUNT_ID
: "${CLOUDFLARE_ACCOUNT_ID:?could not derive CLOUDFLARE_ACCOUNT_ID from the token}"

echo "=== promote: pages project $PROJECT, src=$SRC_SHA session=$SIG ==="
npx --yes wrangler@4.86.0 pages deploy dist --project-name "$PROJECT" --branch main \
  --commit-hash "$(git rev-parse HEAD)" --commit-message "hee:$SIG resume pages src=$SRC_SHA lab-verified" --commit-dirty=false 2>&1 \
  | grep -E 'Deployment complete|Success|rror|requires|https://'
[ "${PIPESTATUS[0]}" = 0 ] || { echo "❌ CRITICAL promote: wrangler pages deploy failed -- nothing verified, nothing tagged" >&2; exit 2; }

echo "=== verify prod ==="
bad=0
for u in https://media.tcos.us/ https://blog.tcos.us/ https://media.tcos.us/people.json; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$u")"; printf '  %-40s %s\n' "$u" "$code"; [ "$code" = 200 ] || bad=1
done
python3 media/bin/media-item.py audit --prod || bad=1
[ "$bad" = 0 ] || { echo "❌ CRITICAL promote: prod verification failed -- fix forward or redeploy the previous commit" >&2; exit 2; }

TAG="prod/resume-pages/$STAMP"
cd "$HERE"
hee git tag "$TAG" -m "prod promotion: blog.tcos.us, media.tcos.us, *.blog.tcos.us
pages project: $PROJECT
source: $SRC_SHA
session: $SIG
verified: hubs 200, media-item audit --prod OK" "$SRC_SHA" --yes --push \
  || { echo "⚠️ WARNING promote: deployed and verified, but the prod tag could not be created/pushed -- hee git tag $TAG -m ... $SRC_SHA --yes --push" >&2; }
