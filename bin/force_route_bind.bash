#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

echo "=== BINDING ROUTE TO EDGE LAYER ==="
curl -X POST "${API_BASE}/zones/8f10dd1cf4a09800045330e7ef048b81/workers/routes" \
     -H "Authorization: Bearer cfut_2PShpJvfLLBZbRapNAvMzSvZgwN0JvNblIkfrR1D1ab01c0d" \
     -H "Content-Type: application/json" \
     --data '{"pattern": "tcos.us/people/spencer*", "script": "tcos-ingress-proxy"}'

echo -e "\n\n=== Edge Binding Rule Dispatched ==="
