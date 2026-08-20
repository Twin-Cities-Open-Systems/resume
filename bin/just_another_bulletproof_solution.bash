#!/usr/bin/env bash
set -e

# Define operational variables
ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
ZONE_ID="8f10dd1cf4a09800045330e7ef048b81"
EMAIL="spencerunderground@gmail.com"
GLOBAL_KEY="cfk_mv70928DQaYYO7GmiZHf5HWa51U5LsJooWHVV3op7af913c6"

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

