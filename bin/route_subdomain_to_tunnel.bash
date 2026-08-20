#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

ZONE_ID="f7653a2322319cb118516b533d12a564"
TOKEN="cfut_2PShpJvfLLBZbRapNAvMzSvZgwN0JvNblIkfrR1D1ab01c0d"
TUNNEL_ID="03966180-2af4-42e6-ba6b-a73e7558ba84"
EMAIL="spencerunderground@gmail.com"

echo "=== INJECTING PUBLIC ROUTING INTERFACE TO LOCAL TUNNEL ==="
curl -X POST "${API_BASE}/zones/${ZONE_ID}/dns_records" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "X-Auth-Email: ${EMAIL}" \
     -H "Content-Type: application/json" \
     --data "{
       \"type\": \"CNAME\",
       \"name\": \"spencer.blog\",
       \"content\": \"${TUNNEL_ID}.cfargotunnel.com\",
       \"ttl\": 1,
       \"proxied\": true
     }"

echo -e "\n\n=== DNS Tunnel Mapping Synchronized Globally ==="
