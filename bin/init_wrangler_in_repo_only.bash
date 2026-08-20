# bin/init_wrangler_in_repo_only.bash

# 1. Initialize a clean local node module workspace boundary
npm init -y

# 2. Save Wrangler directly into your project dependencies
npm install --save-dev wrangler

# 3. Verify the local execution boundary clears cleanly
npx wrangler --version

