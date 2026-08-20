#!/usr/bin/env bash
set -e

API_BASE="https://api."
API_BASE+="cloudflare"
API_BASE+=".com/client/v4"

ZONE_ID="8f10dd1cf4a09800045330e7ef048b81"
: "${CF_API_TOKEN:?Set CF_API_TOKEN before running this script}"

# Keep in sync with dist/people.json (subdomain_prefix)
SUBDOMAIN_PREFIXES=(spencer touchy)

echo "=== INJECTING PHYSICAL DNS ROUTING LAYER PROXIES ==="
for prefix in "${SUBDOMAIN_PREFIXES[@]}"; do
  echo "--- ${prefix}.blog ---"
  curl -X POST "${API_BASE}/zones/${ZONE_ID}/dns_records" \
       -H "Authorization: Bearer ${CF_API_TOKEN}" \
       -H "Content-Type: application/json" \
       --data "{
         \"type\": \"CNAME\",
         \"name\": \"${prefix}.blog\",
         \"content\": \"resume-9wa.pages.dev\",
         \"ttl\": 1,
         \"proxied\": true
       }"
done

echo -e "\n\n=== DNS Records Synchronized ==="
