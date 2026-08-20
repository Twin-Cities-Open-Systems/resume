# bin/init_cf_token_auth.bash

# 1. Export the verified, authoritative Pages token value into your active environment
# export CLOUDFLARE_API_TOKEN="your_newly_generated_tcos_www_worker_edit_secret_string_here"

# 2. Append the verified variables directly into your non-tracked project file
cat << EOF > .env
CLOUDFLARE_ACCOUNT_ID="07f9c2d13b482a6ea0039bc5e172efd2"
CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN"
EOF

# 3. Force the non-interactive production Cloudflare Pages project initialization loop
CLOUDFLARE_ACCOUNT_ID="07f9c2d13b482a6ea0039bc5e172efd2" npx wrangler pages project create resume --production-branch-name master || true

# 4. Trigger the static asset deployment sync directly to the edge
CLOUDFLARE_ACCOUNT_ID="07f9c2d13b482a6ea0039bc5e172efd2" npx wrangler pages deploy dist --project-name=resume

