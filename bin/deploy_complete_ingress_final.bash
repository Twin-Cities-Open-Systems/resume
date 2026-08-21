#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

: "${CF_API_TOKEN:?Set CF_API_TOKEN before running this script}"
TOKEN="$CF_API_TOKEN"
ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
ZONE_ID="f7653a2322319cb118516b533d12a564"

echo "=== [Step 1/2] Uploading Worker JavaScript Module ==="
curl -X PUT "${API_BASE}/accounts/${ACCOUNT_ID}/workers/scripts/tcos-ingress-proxy" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/javascript" \
     --data-binary @./packages/tcos-ingress-proxy/index.js

echo -e "\n\n=== [Step 2/2] Injecting Custom Domain Subpath Route Target ==="
curl -X POST "${API_BASE}/zones/${ZONE_ID}/workers/routes" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     --data '{"pattern": "tcos.us/people/spencer*", "script": "tcos-ingress-proxy"}'

echo -e "\n\n=== Success: Routing Matrix Transmitted ==="
