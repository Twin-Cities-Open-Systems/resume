# SPENCER BUTLER — MASTER TECHNICAL LEDGER (DEBUG)

## Chronological Commits & System Evolutions
* [2019-11-18] Initial commit

* [2019-11-18] Spencer

* [2019-11-18] Spencer

* [2019-11-18] Spencer

* [2019-11-18] Added alternate formats.

* [2019-11-19] Added convert.sh

* [2020-11-04] post KW update (#3)

* [2020-11-30] added UPPER

* [2023-03-06] 2023 - Back at Honeycomb

* [2023-12-19] Honeycomb is now a Client of TCOS

* [2024-08-03] Update README.md
On the fly update, still need to convert.
* [2025-04-19] chore: update resume after Groq (#4)
Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-06-15] summer updates
Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-19] docs: align repo documentation architecture with master TCOS blueprint

* [2026-08-19] docs/follow roadmap to mono repo (#7)
* feat(resume-revamp): mono-repo, direct people link and soa for people info, easter eggs?

* feat(expand) more features than you can shake a stick at.

* feat(profile): add fun language selection for profiles

* feat(pipeline) preparing for the full end to end pipeling to oper.blog.tcos.us

---------

Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-20] feature/wrangler per repo only (#8)
* feat(ingress): migrate repo structure and implement native worker proxy bypass

* feat(ingress): migrate repo structure and implement native worker proxy bypass

* chore(security): formalize .env ignore rules and sync profile metadata

* chore(computer-will-never-beat-me): adding files, will sort in next pass if needed

* chore(creds): new security is mean. moved wrangler* files to my homebin

---------

Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-20] chore(hack): fixing ... maybe (#9)
Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-20] chore(fixing): more 'this is it scripts' (#10)
Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-20] chore(dns): working, added records to square and cf (#11)
Co-authored-by: Spencer Butler <dev@tcos.us>
* [2026-08-20] fix(ingress): make /people/<name> redirect actually work for all people
The ingress Worker only redirected /people/spencer, and even then sent
users to bare tcos.us instead of spencer.blog.tcos.us. touchy-claude's
entry in people.json had no DNS record, no route match, and no redirect
logic at all.

- packages/tcos-ingress-proxy/index.js: redirect any /people/<slug> to
  its real public_dns (sourced from people.json), 301 to the correct
  target instead of the site root.
- deploy_worker_route.bash / force_route_bind.bash: widen the Worker
  route from tcos.us/people/spencer* to tcos.us/people/* so it's not
  spencer-only; swap hardcoded CF token for CF_API_TOKEN env var
  (leaked token tracked in fleet-ops#196).
- provision_public_dns.bash: loop over both subdomain prefixes so
  touchy.blog gets its CNAME too, not just spencer.blog; same env var
  swap.

Not run against live Cloudflare from here -- needs a rotated
CF_API_TOKEN per fleet-ops#196 before someone runs
provision_public_dns.bash + force_route_bind.bash (or
deploy_worker_route.bash) to actually publish this.

* [2026-08-20] feat(ingress): styled not-found page for /people/<unknown-slug>
Bare "Not found" text -> a small dark-themed page that explains no one
by that slug exists and auto-redirects to tcos.us/people after 3s
(plus a manual link), instead of leaving people on a dead end.

Deployed directly via the Workers API from this session (rotated
CF_API_TOKEN, used in-memory only, not written to disk or committed).

* [2026-08-20] fix(cf): correct wrong zone ID hardcoded across all bin/ scripts
Every deploy/DNS script had zone_id 8f10dd1cf4a09800045330e7ef048b81
hardcoded, which isn't tcos.us's real zone -- confirmed live against
the Cloudflare API (real tcos.us zone tag: f7653a2322319cb118516b533d12a564,
same one already visible on the active spencer.blog.tcos.us Pages
domain record). Every zone-scoped call in these scripts (DNS records,
worker routes) was silently authentication-failing against a
nonexistent/inaccessible zone -- the actual root cause of "the redirect
still isn't working."

* [2026-08-20] fix(security): swap remaining 6 hardcoded CF credentials for env vars
Last 6 of 8 files from fleet-ops#196 -- force_route_bind.bash and
provision_public_dns.bash were already fixed earlier. Now none of
resume/bin/*.bash has a live credential value in it:

- Global API Key -> CF_GLOBAL_KEY (provision_global_dns.bash,
  just_another_bulletproof_solution.bash)
- Scoped token -> CF_API_TOKEN (route_subdomain_to_tunnel.bash,
  deploy_complete_ingress_final.bash, force_wrangler_dns_inject.bash)
- Scoped token -> CLOUDFLARE_API_TOKEN, kept as the pre-existing name
  in that one file rather than introducing a 3rd var name for the same
  secret (deploy_complete_ingress_v4.bash)

Confirmed via grep across the whole repo: zero remaining matches for
either old credential value.

Note, out of scope for this commit: several of these scripts have
other pre-existing bugs unrelated to credentials (wrong API base host
in provision_global_dns.bash/just_another_bulletproof_solution.bash --
missing the api. subdomain and/or /client/v4 path; a malformed
--content value in force_wrangler_dns_inject.bash's wrangler dns
create call; deploy_complete_ingress_{v4,final}.bash still target the
spencer-only route pattern superseded by deploy_worker_route.bash).
Flagging on fleet-ops#196 rather than fixing blind -- most of these
look like abandoned trial-and-error attempts already superseded by
the scripts that actually got run successfully.

* [2026-08-22] feat(convert.sh): generic per-profile blog + resume content, no more per-slug hardcoding
"nice on the people! if in people/ should auto create \${oper}.blog" --
convert.sh's content generation was hardcoded per-slug (if slug ==
"spencer" ... if slug == "touchy-claude" ...), so a new profile
dropped into profiles/ got a subdomain assignment and a people.json
entry, but no actual blog content -- someone had to hand-write a new
if-block in the script first. Replaced with one generic renderer
driven entirely by profile.json's language_profiles payloads.

dist/sane.md and the new dist/resume.md ("and our own resume, so they
all get an entry in resume") default to the "professional" payload
specifically, not active_default -- spencer's real active_default is
his own unfiltered "spencer" mode, which is exactly wrong for a resume
or the "sane" fallback. Caught this by actually diffing the generated
output before committing, not just checking the script ran clean:
first pass silently regenerated spencer's sane.md with profanity in it.

Real proof case: profiles/claude-intern-j2/profile.json, a brand-new
profile added with zero new script logic, produces correct dist/sane.md
and dist/resume.md output on the first run.

Kept spencer's real personal achievement content (filter-pass.md) and
git-log ledger (debug.md) as genuinely spencer-specific, not templated
-- those don't generalize to every profile.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011tVMcJAK7j2m3vUoqxteYY
