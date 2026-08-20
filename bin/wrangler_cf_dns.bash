#!/usr/bin/env bash
set -euo pipefail

export CLOUDFLARE_ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
export CLOUDFLARE_API_TOKEN=""

npx wrangler pages domains add resume spencer.blog.tcos.us

