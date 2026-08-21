#!/usr/bin/env bash
set -e

echo "=== Injecting Base Path Properties into Core Application ==="
# Hardcoding the base asset reference route to look for its json files on your live pages link
cat << 'W_EOF' > wrangler.toml
name = "resume"
pages_build_output_dir = "dist"

[vars]
BASE_PATH = "/people/spencer"
W_EOF

echo "=== Compiling Project with Subdirectory Target Routes ==="
./bin/hee-pipeline-control full-cycle

echo "=== Pushing Assets to Cloudflare Host Asset Bucket ==="
npx wrangler pages deploy dist --project-name="resume"

echo -e "\n=== Local Infrastructure Alignment Complete ==="
