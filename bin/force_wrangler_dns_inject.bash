#!/usr/bin/env bash
set -e

# Establish the secure global tracking configuration directory
mkdir -p ~/.config/.wrangler

# Inject the active permission token profile directly into Wrangler's global authentication configuration matrix
cat << W_EOF > ~/.config/.wrangler/config.toml
api_token = "cfut_2PShpJvfLLBZbRapNAvMzSvZgwN0JvNblIkfrR1D1ab01c0d"
W_EOF

echo "=== PROVISIONING AUTHORITATIVE SUBDOMAIN POINTER VIA WRANGLER ==="
# Execute the native command payload to inject your CNAME string into your live zone topology
npx wrangler dns create "f7653a2322319cb118516b533d12a564" "spencer.blog" --type="CNAME" --content="://cfargotunnel.com" --proxied=true

echo -e "\n=== Routing Core Synchronized Successfully ==="
