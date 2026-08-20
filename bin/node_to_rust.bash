export VOLTA_HOME="$HOME/.volta" && export PATH="$VOLTA_HOME/bin:$PATH" && volta install node@22 && git reset && git add .gitignore package.json bin/ profiles/ tests/ convert.sh && npx wrangler worker deploy --var PEOPLE_MANIFEST="$(cat dist/people.json)"

