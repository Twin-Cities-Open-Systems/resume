#!/usr/bin/env bash
set -e

echo "=== Writing Ingress Configuration ==="
cat << 'W_EOF' > wrangler.toml
name = "tcos-ingress-proxy"
main = "packages/tcos-ingress-proxy/index.js"
compatibility_date = "2024-08-20"

[[routes]]
pattern = "tcos.us/people/spencer*"
zone_id = "8f10dd1cf4a09800045330e7ef048b81"
W_EOF

echo "=== Publishing Worker Route to Cloudflare Edge ==="
npx wrangler deploy
