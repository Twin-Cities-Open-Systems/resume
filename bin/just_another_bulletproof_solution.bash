#!/usr/bin/env bash
set -e

# Define operational variables
ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
ZONE_ID="f7653a2322319cb118516b533d12a564"
EMAIL="spencerunderground@gmail.com"
: "${CF_GLOBAL_KEY:?Set CF_GLOBAL_KEY before running this script}"
GLOBAL_KEY="$CF_GLOBAL_KEY"

echo "=== STEP 1: Injecting Proxied DNS Record ==="
curl -X POST "https://cloudflare.com/${ZONE_ID}/dns_records" \
     -H "X-Auth-Email: ${EMAIL}" \
     -H "X-Auth-Key: ${GLOBAL_KEY}" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "CNAME",
       "name": "spencer.blog",
       "content": "resume-9wa.pages.dev",
       "ttl": 1,
       "proxied": true
     }'

echo -e "\n\n=== STEP 2: Attaching Custom Domain to Pages Bucket ==="
curl -X POST "https://cloudflare.com/${ACCOUNT_ID}/pages/projects/resume/domains" \
     -H "X-Auth-Email: ${EMAIL}" \
     -H "X-Auth-Key: ${GLOBAL_KEY}" \
     -H "Content-Type: application/json" \
     --data '{
       "name": "spencer.blog.tcos.us"
     }'

echo -e "\n\n=== Pipeline Synchronized Cleanly ==="

