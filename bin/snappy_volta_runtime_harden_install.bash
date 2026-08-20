# bin/snappy_volta_runtime_harden_install.bash

# Install the Volta binary controller framework
curl https://get.volta.sh | bash
source ~/.bashrc

# Lock down the Node v22 runtime dependency globally across the host
volta install node@22
volta install wrangler

# Deploy your edge matrix mapping configurations
wrangler worker deploy --var PEOPLE_MANIFEST="$(cat dist/people.json)"

