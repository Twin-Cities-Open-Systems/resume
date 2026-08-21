#!/usr/bin/env bash
set -e

echo "=== Step 1/3: Compiling Fresh Matrix Ledgers ==="
./bin/hee-pipeline-control full-cycle

echo "=== Step 2/3: Aligning Local Profile Data Paths ==="
mkdir -p dist/profiles/spencer
cp -v profiles/spencer/profile.json dist/profiles/spencer/
cp -v profiles/spencer/profile.json dist/profiles/spencer/profile_professional.json

echo "=== Step 3/3: Direct Deploy Static Build to Pages ==="
# Deploying natively via wrangler pages to completely bypass the broken worker route paths
npx wrangler pages deploy dist --project-name="resume"

echo -e "\n=== Production Blog Deployment Completed Successfully ==="
