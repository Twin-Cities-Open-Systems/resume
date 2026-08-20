#!/usr/bin/env bash
set -euo pipefail

export CLOUDFLARE_ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
export CLOUDFLARE_API_TOKEN="cfut_4MrkMUsI8gPcJYOtdyDBFUSA1MsEqwwjYU4ndKLLf303d575"

npx wrangler pages domains add resume spencer.blog.tcos.us

