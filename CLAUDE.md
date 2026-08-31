# resume

Org governance is canonical in `human-execution-engine` and imported
below -- read it before doing real work in this repo.

@~/git/human-execution-engine/prompts/PROMPTING_RULES.md

That import assumes this org's own convention of every repo being checked
out under `~/git/<repo>` (per `bin/init-org.sh`'s `WORKSPACE_DIR`).
`~` is the most portable form Claude Code's `@import` supports -- there
is no `$HOME`/env-var expansion and no workspace-relative mechanism. On a
machine that does not follow that layout the import silently resolves to
nothing, so if you are unsure it loaded, read the file directly rather than
assume it did.

<!-- Repo-specific guidance belongs below this line, never above it. -->
