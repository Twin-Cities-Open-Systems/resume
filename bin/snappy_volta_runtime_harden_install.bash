# bin/snappy_volta_runtime_harden_install.bash

# Install the Volta binary controller framework
curl https://get.volta.sh | bash
# the user's own rc, not a file this repo ships
# shellcheck disable=SC1090
source ~/.bashrc

# Lock down the Node v22 runtime dependency globally across the host
volta install node@22
volta install wrangler

# Deploy your edge matrix mapping configurations
wrangler worker deploy --var PEOPLE_MANIFEST="$(cat dist/people.json)"

