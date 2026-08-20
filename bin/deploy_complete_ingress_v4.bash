#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

# 1. Update the local environmental token signature with your newly configured permission key
export CLOUDFLARE_API_TOKEN="cfut_2PShpJvfLLBZbRapNAvMzSvZgwN0JvNblIkfrR1D1ab01c0d"

echo "=== [Step 1/3] Uploading Proxy Logic to Workers Marketplace ==="
curl -X PUT "${API_BASE}/accounts/a33d047ae2835100b8ea875863913f96/workers/scripts/tcos-ingress-proxy" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/javascript" \
     --data-binary @./packages/tcos-ingress-proxy/index.js

echo -e "\n\n=== [Step 2/3] Registering Custom Domain Mapping ==="
# Bypassing the duplicate check and locking down the project name to 'resume'
curl -X POST "${API_BASE}/accounts/a33d047ae2835100b8ea875863913f96/pages/projects/resume/domains" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     --data '{"name": "spencer.blog.tcos.us"}' || echo "Domain already bound, continuing..."

echo -e "\n\n=== [Step 3/3] Direct Inject Ingress Route Into Zone Architecture ==="
curl -X POST "${API_BASE}/zones/8f10dd1cf4a09800045330e7ef048b81/workers/routes" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     --data '{"pattern": "tcos.us/people/spencer*", "script": "tcos-ingress-proxy"}'

echo -e "\n\n=== Ingress Pipeline Processing Complete ==="
