#!/usr/bin/env bash
set -e

echo "=== Writing Ingress Configuration ==="
cat << 'W_EOF' > wrangler.toml
name = "tcos-ingress-proxy"
main = "packages/tcos-ingress-proxy/index.js"
compatibility_date = "2024-08-20"

[[routes]]
pattern = "tcos.us/people/*"
zone_id = "f7653a2322319cb118516b533d12a564"
W_EOF

echo "=== Publishing Worker Route to Cloudflare Edge ==="
npx wrangler deploy
