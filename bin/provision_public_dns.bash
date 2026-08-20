#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

ZONE_ID="8f10dd1cf4a09800045330e7ef048b81"
TOKEN="cfut_2PShpJvfLLBZbRapNAvMzSvZgwN0JvNblIkfrR1D1ab01c0d"

echo "=== INJECTING PHYSICAL DNS ROUTING LAYER PROXIES ==="
curl -X POST "${API_BASE}/zones/${ZONE_ID}/dns_records" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "CNAME",
       "name": "spencer.blog",
       "content": "resume-9wa.pages.dev",
       "ttl": 1,
       "proxied": true
     }'

echo -e "\n\n=== DNS Record Synchronized ==="
