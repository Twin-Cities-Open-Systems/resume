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

* [2026-08-23] feat(blog): dogfood hash lookup with a new claude-intern-j2 badge (#15)
* feat(blog): real ?hash= lookup, static, no backend

Real ask: "can we turn those into short urls... must link to use" ->
"static is perfect". Reads ?hash= client-side, checks it against a
static manifest.json (same data hee-qr -manifest already writes, no
new format), renders the matching recipe if found. Works for any real
hash going forward, not just this one -- exact query-param shape may
get refined later, this is the simple, fast first version.

Real-browser tested via a local playwright run (not just eyeballed):
found/not-found/no-hash paths all verified working.

* feat(blog): add the real manifest.json data file (dist/ is gitignored, force-added same as dist/index.html already is)

* feat(blog): dogfood the hash lookup with a new claude-intern-j2 badge

Real, one-shot test of the full "hee-key hole" loop end to end for a
brand-new identity: rendered a real mt-logo-render badge for
claude-intern-j2 (hex/green, matching the existing intern-tier
naming convention), read the hash back two independent ways
(render.py's own PNG-metadata reader, and hee-qr's QR scan --
they agreed, d9ad910d..., confirming the anchor round-trips clean),
published it into manifest.json, and confirmed locally (headless
Chromium against a static server, no live deploy) that /?hash=<id>
resolves to the real recipe -- the "other side of the key" a stranger
scanning the QR would actually see.

Found and fixed a real hee-qr bug along the way (see
human-execution-engine touchy/hee-qr branch, PR #291): the
URL->hash extraction only ran in -manifest mode, so a plain
`hee-qr image.png` printed the raw QR payload URL instead of the
bare hash.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011tVMcJAK7j2m3vUoqxteYY

---------

Co-authored-by: Spencer Butler <spencerunderground@gmail.com>
Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
* [2026-08-23] feat(convert.sh): generic per-profile blog + resume, no more per-slug hardcoding (#16)
* feat(convert.sh): generic per-profile blog + resume content, no more per-slug hardcoding

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

* feat(convert.sh): real multi-format resume conversion for every profile

"that reservation should be able to convert everybody's resume that
has a mono repo there... convert all of them to the same simple
formats" -- the actual pandoc conversion pipeline (SpencerButler.md ->
.html/.pdf/.txt) only ever ran for spencer's own root-level file, never
extended to the generic per-profile resume.md this same PR just added.

Now every profile gets real .html/.pdf/.txt output alongside its .md,
generated the same way for everyone: pandoc for html, wkhtmltopdf as
the pdf engine (avoids a full texlive-latex-recommended install for
something this simple), same sed-based header-strip for plain text the
original SpencerButler pipeline already used.

Installed pandoc + wkhtmltopdf on this host to build and verify this
for real -- not simulated. All three current profiles (spencer,
touchy-claude, claude-intern-j2) produce real, verified output: `file`
confirms real PDF documents, txt output spot-checked clean.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011tVMcJAK7j2m3vUoqxteYY

---------

Co-authored-by: Spencer Butler <spencerunderground@gmail.com>
Co-authored-by: Claude Sonnet 5 <noreply@anthropic.com>
* [2026-08-25] feat(media): spencer.media -- Tux Tattoo gallery, GPG-signed, client-verified
Self-contained gallery page (11 photos, embedded base64) with
client-side GPG signature verification (openpgp.js) per photo. Built
and lab-verified this session on pve container 107
(view.lab.tcos.us / spencer.media.lab.tcos.us via HAProxy path
rewrite). Deployed here to its own Cloudflare Pages project rather
than the shared `resume` project -- that project's per-domain content
routing isn't actually built yet (confirmed live: touchy.blog.tcos.us
currently serves spencer's content, a real separate bug, tracked
elsewhere) and this shouldn't be coupled to that gap.

Canonical, signed source images + detached .asc files remain at
/mnt/nuc1-pool/storage/docs/media-archive/spencer/tux-tattoo/ -- this
is the compiled artifact, same convention as profiles/*/dist/ already
being committed in this repo.

* [2026-08-25] feat(media): add back-link to spencer.media root from tux-tattoo page

* [2026-08-25] sign: Spencer's first personal GPG signature on published prod content
Real milestone: Spencer personally reviewed and GPG-signed a real
promotion attestation for the Tux Tattoo gallery -- his own signature
on the prod-promotion event, alongside the existing touchy-claude
per-photo lab signatures, per the just-ratified content-signing-v1
split (lab builds sign their own work; prod promotion is signed by
whoever actually performed it -- here, both apply, made explicit).

Independently verified (gpg --verify, separate checkout, not just the
signing session's own output): Good signature from Spencer Butler.

* [2026-08-25] feat(tux-tattoo): live in-browser verification for Spencer's promotion attestation too
Second real GPG signature, verified the same way as the per-photo
lab signatures -- fetches the actual served attestation file + its
detached signature, checks both live against Spencer's real public
key (embedded, same pattern as the existing touchy-claude key --
GitHub's github.com/<login>.gpg endpoint would be the real canonical
source, but has no CORS headers so can't be fetched client-side
cross-origin, confirmed live -- fleet-ops#310 tracks a real fix).

Now visitors see two live-verified signatures, not one flashy badge
and one plain unverified link.

* [2026-08-25] feat(tux-tattoo): regen-keys.py -- front-load embedded pubkeys from github.com/<login>.gpg
Spencer's ask: don't hand-copy keys once, front-load them from the
real canonical source (GitHub already serves this for free, confirmed
working for both identities) so a future key rotation is a re-run of
this script, not another manual copy-paste. Still has to embed the
result at generation time, not fetch client-side -- github.com/*.gpg
has no CORS headers (confirmed live), so a browser fetch from a
different origin is silently blocked.

Real bug caught and fixed before this shipped: the first version used
re.subn(pattern, replacement_string, content) -- Python's re module
re-processes backslash escapes in a *string* replacement (for \g<name>
group references), which silently turned the key's literal "\n"
sequences into real newline characters, breaking the JS syntax. Fixed
by passing a function as repl instead (its return value is inserted
as-is, no re-processing). Verified: round-trip is now a true no-op
diff against the already-correct committed content.

* [2026-08-25] fix(tux-tattoo): source link pointed at the wrong file (root landing page instead of its own source)

* [2026-08-25] fix(media): serve .asc files as text/plain, not application/pgp-keys
Real UX inconsistency, not a security footgun: .asc files were
downloading instead of displaying inline (application/pgp-keys isn't
a browser-renderable type), while the paired .txt displayed fine.
_headers has to live at the deploy root -- Cloudflare Pages doesn't
read it from subdirectories.

* [2026-08-25] fix(tux-tattoo): attestation verification used wrong OpenPGP message mode
Real bug, caught live by Spencer ("gpg on image verified is still
only yours, should be 2 greenies"): the promotion-attestation
verification used openpgp.createMessage({text: ...}), which applies
OpenPGP text-mode line-ending canonicalization -- but gpg --detach-sign
signed the raw file bytes (binary mode, the default). Mismatch made
verification silently fail even though the signature is genuinely
valid. Fixed to binary mode, matching how the per-photo verification
above already does it correctly.

Also relabels the two badges to make the lab/prod distinction real
instead of two identical "GPG verified" badges: "Lab verified" for
the per-photo touchy-claude signatures, "Prod verified" for Spencer's
promotion attestation.

* [2026-08-25] feat(media): real Tux favicon, generated from the actual embedded reference image
Spencer's ask: spencer.media needs icons, "a real tux for that first
post is perfect." Extracted the actual Tux reference JPEG already
embedded in the tux-tattoo page (not a fabricated/stock icon),
generated a real favicon set (16/32/48px + favicon.ico, apple-touch-icon
180px, 192/512px for PWA-style use) via PIL, wired into both the
media landing page and the tux-tattoo page's <head>.

* [2026-08-25] feat(media): standard header/footer/toggle for the landing page, matching tux-tattoo
Spencer's ask: spencer.media needs standard header, footer, and font
size toggle -- was a bare minimal page before. Now shares the exact
same light/dark + S/M/L/XL toggle system as tux-tattoo (copied
verbatim, same tokens), not a second bespoke implementation.

* [2026-08-25] fix(media): dedup shared theme/toggle CSS+JS into shell-theme.css/shell-toggles.js
Real incident (resume#27): the toggle system was built once for
tux-tattoo, then copy-pasted verbatim into the landing page instead
of extracted. Both pages now reference the shared files instead of
embedding a copy each.

Also fixes the freshness banner's real lie, caught live: data-generated
was hand-typed once and never updated through many later edits, so
"updated Xh Ym ago" was stale/wrong. Relabeled to "last update:" and
added deploy.sh, which substitutes the real current UTC time on every
deploy instead of relying on a manual edit.

* [2026-08-25] chore: ignore __pycache__ (leaked into a deploy via regen-keys.py's compiled cache)

* [2026-08-25] fix(tux-tattoo): freshness display -- fancy human date + real ISO on hover, fix deploy.sh leak
Real timeline bug: the "5h1m ago" Spencer caught was genuinely
accurate (data-generated was only manually refreshed once, many edits
ago) -- deploy.sh existed but wasn't actually being used for several
deploys in a row. Now used for real.

Display upgraded per Spencer's ask: short "lu:" label, real
human-readable calendar date (weekday, month, ordinal day, year) as
the primary claim, squeezed relative time in muted parens, and the
real raw ISO timestamp available on hover (title attr) -- honest
technical value until hee-epoch owns real epoch tracking.

Also fixed a real bug in deploy.sh itself, caught on its very first
real run: wrangler creates its own .wrangler/ cache dir inside the
assets dir during the same invocation, and deploy.sh's own script
file was being uploaded as a public asset. Added .assetsignore
(Cloudflare's real ignore-file mechanism for Workers static assets)
to exclude both.

* [2026-08-25] fix(tux-tattoo): use 'last update:' not 'lu:' -- clearer, not cryptic

* [2026-08-25] revert: back to 'lu:' per Spencer's actual preference

* [2026-08-25] feat(tux-tattoo): real EXIF full-detail page + adopt hee-exif for key/data regen
New exif.html: click any photo's EXIF badge to see the complete,
real, non-blank exiftool output in a new tab -- not just the 2-field
hover tooltip. Same embedded-at-build-time pattern as the GPG
signatures, sourced from the real canonical files.

Fixed a real bug found while building the proper hee-exif tooling for
this (human-execution-engine#383): the original manual extraction had
exiftool's own "11 image files read" summary line leak into one
field's key name. Removed the one-off regen-keys.py script -- its
logic now lives as real hee-exif subcommands (regen-pubkey,
embed-exif), per Spencer's direct instruction to keep tools under hee
rather than scattering one-offs per repo.

* [2026-08-25] fix(deploy): deploy.sh now syncs lab first, then promotes verbatim bytes to prod
Real drift bug caught live (Spencer: "make sure that lab is going to
be synced to prod for real" -> found genuinely mismatched via MD5
diff): the old deploy.sh substituted a fresh data-generated timestamp
into the STAGED copy on every prod deploy, without writing it back to
the tracked source or to lab. Prod's "last update" kept silently
advancing while lab and git stayed frozen -- exactly the kind of
lab/prod divergence the whole lab-first architecture exists to
prevent.

Real policy, stated directly: "for the release, must be from real
lab." deploy.sh now: (1) syncs lab from the tracked source verbatim,
(2) deploys the *same* bytes to prod, no independent substitution,
(3) self-verifies lab == prod via MD5 on 3 key files before
finishing. Freshness (data-generated) is set once, at real edit time,
same discipline as any other content change -- not silently
regenerated at deploy time.

* [2026-08-26] fix(resume): resume.md was rendering persona copy, not real facts
Real bug, Spencer direct (2026-08-26): the live spencer.blog.tcos.us
resume page said "Systems Engineer specializing in... multi-agent
evaluation runtimes" -- that's the "professional" language_profiles
paradigm blurb (a blog voice/tone variant), not his real, factual work
history. convert.sh's generic per-profile resume.md generation reused
sane.md's title/paradigm source for every profile including the one
document that's supposed to be strictly factual.

Fix: resume.md is now built from a real per-profile source document
(REAL_RESUME_SOURCES map; spencer -> SpencerButler.md, his actual
resume) when one exists. A profile without a real source gets no
resume.md/html/pdf/txt at all -- no fabricated fallback. Only spencer
has a real source today; touchy-claude and claude-intern-j2 correctly
get nothing until they have real content.

Per Spencer's explicit instruction, language-profile-driven resume
generation is NOT being redesigned to work correctly here -- it's
removed for now, to be reintroduced properly later (backlog).

Also fixes a real crash: resume-theme.html (referenced by convert.sh's
pandoc -H flag since an earlier session) didn't actually exist in this
checkout, so every run of convert.sh was aborting partway through
(set -euo pipefail) the moment it reached a profile with a real
resume. Recreated it -- the dark-theme snippet matching
media/spencer/dist/shell-theme.css's real token values, not a new
palette.

* [2026-08-26] fix(spencer.media): cross-env links, freshness widget, tux icon, dedup
Real bugs Spencer caught live, all on spencer.media.lab.tcos.us /
spencer.media.tcos.us:

- Breadcrumb "<- Twin Cities Open Systems" pointed at tcos.us/people,
  should be tcos.us itself.
- Same breadcrumb, plus the "spencer.blog.tcos.us" note link, silently
  bounced a lab reviewer to PROD -- no tcos.lab.tcos.us or
  spencer.blog.lab.tcos.us mirror exists yet (confirmed via DNS, they
  don't resolve). Fixed via a real host-aware link handler
  (shell-toggles.js's new IIFE): any a[data-cross-site] with no real
  lab target goes inert with a visible "(prod only)" label on lab,
  instead of linking to prod silently.
- Root landing page had no "lu:" freshness banner and no icon next to
  the "Tux Tattoo" list item, both real per earlier asks that were
  only ever built on the tux-tattoo subpage, never the root page.
- tux-tattoo page hardcoded "live on spencer.media.tcos.us" and the
  footer domain -- both literally false when served from lab. Now
  computed from window.location.hostname at load time via a generic
  [data-host] handler ("remove all static content... exception not
  rule").
- The eyebrow ("SPENCER.MEDIA") is now a self-link; a second
  eyebrow-styled line for spencer.blog sits under it, replacing the
  old prose note link (Spencer: "add the blog link under it just like
  that, I like that style").
- Freshness widget (.freshness/.fr-dot/.fr-rel CSS + the "lu:" render
  logic) was inline-duplicated on tux-tattoo/index.html; extracted to
  shared shell-theme.css + a new shell-freshness.js, this being the
  second real use (never dup, always dedup).
- deploy.sh: real incident (fleet-ops#312) -- it synced lab then
  pushed the same bytes to prod in one shot, no checkpoint, so a lab
  edit auto-promoted to prod before Spencer could review it. Split
  into `deploy.sh lab` (sync only) and `deploy.sh promote` (lab sync +
  prod push + lab==prod verify) -- prod is never touched by `lab`.
- deploy.sh also now minifies shell-toggles.js/shell-freshness.js via
  terser, but ONLY inside the ephemeral build stage dir -- never the
  tracked source (real footgun Spencer flagged: minifying source in
  place would make future edits happen on unreadable code).

* [2026-08-26] feat(spencer.media): real Open Graph / Twitter Card previews
Real gap, Spencer direct (2026-08-26), caught live from an actual
Facebook post: sharing the tux-tattoo link showed a bare link card,
no image, no real title -- no og:*/twitter:* meta tags existed at
all.

og:image/twitter:image use a real, purpose-built 1200x630 banner
(og-banner.jpg), not a stretched square icon -- composited from three
of the actual progression photos (outline / more-fill / finished),
each scaled only mildly (max ~1.5x) to avoid the blur a single
283x432 source photo would produce at that target size. Real pixels,
not upscaled guesswork.

* [2026-08-26] chore(resume): regenerate spencer dist output with real-facts fix
convert.sh's REAL_RESUME_SOURCES fix (74f90d6) landed but the
regenerated dist/ artifacts were never committed -- picking that
up now, no source change.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01NjgMEU5Zu6QrnRjjpE9uNz

* [2026-08-26] fix(media): declare og RDFa prefix on spencer.media pages
Facebook's Sharing Debugger was folding twitter:* meta tags into a
synthetic og:temporal:twitter:* namespace because <html> never
declared the OG RDFa prefix per the ogp.me spec. Adds
prefix="og: https://ogp.me/ns#" to all three spencer.media pages.

fb:app_id warning still open -- no real Facebook App ID exists yet
for TCOS, not fabricating a placeholder.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01NjgMEU5Zu6QrnRjjpE9uNz

* [2026-08-26] fix(media): add real fb:app_id, closes Facebook debugger warning
Real Meta app "spencer.media" (App ID 1083442627963213), dev-mode
is sufficient -- no publish/business-verification needed just to
attribute link-preview scrapes.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01NjgMEU5Zu6QrnRjjpE9uNz
