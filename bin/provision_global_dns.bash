#!/usr/bin/env bash
set -e

# Format base targets separately to secure the channel
API_GATEWAY="https://cloudflare.com"
API_PATH="${API_GATEWAY}/client/v4"

ACCOUNT_ID="a33d047ae2835100b8ea875863913f96"
ZONE_ID="8f10dd1cf4a09800045330e7ef048b81"
EMAIL="spencerunderground@gmail.com"
GLOBAL_KEY="cfk_mv70928DQaYYO7GmiZHf5HWa51U5LsJooWHVV3op7af913c6"

SUB_TARGET="spencer"
SUB_TARGET+=".blog"

echo "=== STEP 1: Deploying Isolated Proxied Route Entry ==="
curl -X POST "${API_PATH}/zones/${ZONE_ID}/dns_records" \
     -H "X-Auth-Email: ${EMAIL}" \
     -H "X-Auth-Key: ${GLOBAL_KEY}" \
     -H "Content-Type: application/json" \
     --data "{\"type\":\"CNAME\",\"name\":\"${SUB_TARGET}\",\"content\":\"resume-9wa.pages.dev\",\"ttl\":1,\"proxied\":true}"

echo -e "\n\n=== STEP 2: Binding Ingress Target onto Project Worker Mapping ==="
curl -X POST "${API_PATH}/accounts/${ACCOUNT_ID}/pages/projects/resume/domains" \
     -H "X-Auth-Email: ${EMAIL}" \
     -H "X-Auth-Key: ${GLOBAL_KEY}" \
     -H "Content-Type: application/json" \
     --data "{\"name\":\"${SUB_TARGET}.tcos.us\"}"

echo -e "\n\n=== Direct Verification Pipeline Complete ==="
