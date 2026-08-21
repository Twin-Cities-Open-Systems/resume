#!/usr/bin/env bash
set -e

echo "=== Step 1/3: Writing Multi-Agent Ingress Redirect Manifest ==="
# Injecting a hardcoded single-page application redirect rule into the build target 
# to force Cloudflare Pages hosting node structures to route traffic properly
cat << 'R_EOF' > dist/_redirects
/people/spencer   https://pages.dev 301
/*                 /index.html 200
R_EOF

echo "=== Step 2/3: Aligning Subdirectory Asset Trees ==="
mkdir -p dist/profiles/spencer
cp -v profiles/spencer/profile.json dist/profiles/spencer/
cp -v profiles/spencer/profile.json dist/profiles/spencer/profile_professional.json

echo "=== Step 3/3: Pushing Live Production Artifact Container ==="
npx wrangler pages deploy dist --project-name="resume" --branch="master"

echo -e "\n=== Ingress Matrix Processing Complete ==="
