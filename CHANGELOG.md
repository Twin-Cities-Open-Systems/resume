# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_Nothing since the last release._

## [1.2.0] - 2026-09-11

### Added

- 2026-09-11 **thesis**: left-of-capex -- placed for the operator to edit ([#85](https://github.com/Twin-Cities-Open-Systems/resume/pull/85))
- 2026-09-11 **media**: URL kinds, not tags -- /blog/<slug>/, /gallery/<item>/, /thesis/<slug>/; galleries move under gallery/; theses render; old URLs redirect (_redirects on prod) ([#86](https://github.com/Twin-Cities-Open-Systems/resume/pull/86))
- 2026-09-10 **blog**: the two standalone pages are posts now; standalone-pages/ removed; publishing guide ([#83](https://github.com/Twin-Cities-Open-Systems/resume/pull/83))
- 2026-09-06 **release**: cut builds the whole repo into the release commit (hee#594) ([#80](https://github.com/Twin-Cities-Open-Systems/resume/pull/80))
- 2026-09-06 **media**: release beside commit in every root and item footer -- the tag on prod, describe-with-distance on lab ([#79](https://github.com/Twin-Cities-Open-Systems/resume/pull/79))

### Fixed

- 2026-09-11 **deploy**: the lab prune sorts and compares in byte order on both sides -- it pruned live gallery files and exited 1 ([#88](https://github.com/Twin-Cities-Open-Systems/resume/pull/88))

### Changed

- 2026-09-10 **release**: v1.1.0 ([#84](https://github.com/Twin-Cities-Open-Systems/resume/pull/84))
- 2026-09-08 **hee-check**: pin the hee checkout to `stable` ([#82](https://github.com/Twin-Cities-Open-Systems/resume/pull/82))

### Other

- 2026-09-07 easter egg HWOps For Life! ([#81](https://github.com/Twin-Cities-Open-Systems/resume/pull/81))

## [1.1.0] - 2026-09-10

### Added

- 2026-09-10 **blog**: the two standalone pages are posts now; standalone-pages/ removed; publishing guide ([#83](https://github.com/Twin-Cities-Open-Systems/resume/pull/83))
- 2026-09-06 **release**: cut builds the whole repo into the release commit (hee#594) ([#80](https://github.com/Twin-Cities-Open-Systems/resume/pull/80))
- 2026-09-06 **media**: release beside commit in every root and item footer -- the tag on prod, describe-with-distance on lab ([#79](https://github.com/Twin-Cities-Open-Systems/resume/pull/79))

### Changed

- 2026-09-08 **hee-check**: pin the hee checkout to `stable` ([#82](https://github.com/Twin-Cities-Open-Systems/resume/pull/82))

### Other

- 2026-09-07 easter egg HWOps For Life! ([#81](https://github.com/Twin-Cities-Open-Systems/resume/pull/81))

## [1.0.0] - 2026-09-06

### Added

- 2026-09-06 **release**: release.card.v1.yaml for hee release -- six surfaces, media before pages; prod tags take the release version ([#77](https://github.com/Twin-Cities-Open-Systems/resume/pull/77))
- 2026-09-06 **media**: every card's provenance names its page (og_for), kind, owner (Artist), title and host ([#76](https://github.com/Twin-Cities-Open-Systems/resume/pull/76))
- 2026-09-06 **media**: card icons from Lucide (ISC), chosen by the item's topic and kind, inlined for the theme ([#72](https://github.com/Twin-Cities-Open-Systems/resume/pull/72))
- 2026-09-06 **blog**: a post's header links -- repo, source file on GitHub, and the chip to the media root listing ([#73](https://github.com/Twin-Cities-Open-Systems/resume/pull/73))
- 2026-09-06 **people**: people.json carries each person's GitHub login (profile meta.github) ([#67](https://github.com/Twin-Cities-Open-Systems/resume/pull/67))
- 2026-09-06 **pages**: bin/deploy-pages.sh lab|promote -- the gated path for blog.tcos.us, media.tcos.us and every <prefix>.blog host ([#64](https://github.com/Twin-Cities-Open-Systems/resume/pull/64))
- 2026-09-06 **media**: the MN2600 item -- both people approved, consent recorded ([#62](https://github.com/Twin-Cities-Open-Systems/resume/pull/62))
- 2026-09-06 **media**: text size scales the root; layout tokens from the em-width -- same mechanism as tcos-www and Gold ([#59](https://github.com/Twin-Cities-Open-Systems/resume/pull/59))
- 2026-09-05 **media**: promote is gated, signed by the session, and tagged prod/<site>/<stamp> ([#56](https://github.com/Twin-Cities-Open-Systems/resume/pull/56))
- 2026-09-05 **media**: links that leave the host open in a new tab (synced from Gold) ([#55](https://github.com/Twin-Cities-Open-Systems/resume/pull/55))
- 2026-09-05 **media**: one media host per person -- posts on the media host, generic deploy, blog->media redirects (lab live) ([#53](https://github.com/Twin-Cities-Open-Systems/resume/pull/53))
- 2026-09-05 **media**: media-item builder -- tux-tattoo's design from a kind: Card manifest ([#49](https://github.com/Twin-Cities-Open-Systems/resume/pull/49))
- 2026-09-05 **site**: the org's Google tag on every page this repo publishes ([#48](https://github.com/Twin-Cities-Open-Systems/resume/pull/48))
- 2026-08-28 **gold**: port individual profile-page template to Gold ([#34](https://github.com/Twin-Cities-Open-Systems/resume/pull/34))
- 2026-08-26 **blog**: real ?hash= lookup on spencer.blog.tcos.us ([#14](https://github.com/Twin-Cities-Open-Systems/resume/pull/14))
- 2026-08-26 EOS blog posts, resume update, first-pass skill/all-time badges ([#18](https://github.com/Twin-Cities-Open-Systems/resume/pull/18))
- 2026-08-23 **convert.sh**: generic per-profile blog + resume, no more per-slug hardcoding ([#16](https://github.com/Twin-Cities-Open-Systems/resume/pull/16))
- 2026-08-23 **blog**: dogfood hash lookup with a new claude-intern-j2 badge ([#15](https://github.com/Twin-Cities-Open-Systems/resume/pull/15))
- 2026-08-20 **ingress**: styled not-found page for /people/<unknown-slug> (`7f07c36`)

### Fixed

- 2026-09-06 **media**: promote gates the staged images -- branding on every one, provenance on every generated one ([#75](https://github.com/Twin-Cities-Open-Systems/resume/pull/75))
- 2026-09-06 **pages**: hub hosts serve the hub under its clean name and send every other path to / ([#71](https://github.com/Twin-Cities-Open-Systems/resume/pull/71))
- 2026-09-06 **media**: the prod audit resolves *.tcos.us through public DNS ([#70](https://github.com/Twin-Cities-Open-Systems/resume/pull/70))
- 2026-09-06 **pages**: build in a detached worktree of HEAD, never in the checkout ([#69](https://github.com/Twin-Cities-Open-Systems/resume/pull/69))
- 2026-09-06 **pages**: media.tcos.us and blog.tcos.us serve the hubs; the item footer is optional ([#66](https://github.com/Twin-Cities-Open-Systems/resume/pull/66))
- 2026-09-06 **media**: prod audit and verify match what Cloudflare really does ([#65](https://github.com/Twin-Cities-Open-Systems/resume/pull/65))
- 2026-09-06 **deploy**: prod tags are made by hee git tag -- the signing key comes from the oper's keyring, not gitconfig ([#68](https://github.com/Twin-Cities-Open-Systems/resume/pull/68))
- 2026-09-06 **media**: promote reads the token hee cred injects and derives the account id ([#63](https://github.com/Twin-Cities-Open-Systems/resume/pull/63))
- 2026-09-06 **media**: the Google-tag guard accepts the apex form (synced from hee_gtag) ([#60](https://github.com/Twin-Cities-Open-Systems/resume/pull/60))
- 2026-09-06 **resume**: pandoc links bare URLs in the resume (+autolink_bare_uris) ([#58](https://github.com/Twin-Cities-Open-Systems/resume/pull/58))
- 2026-09-06 **media**: the root's lu is owned by the builder ([#57](https://github.com/Twin-Cities-Open-Systems/resume/pull/57))
- 2026-09-05 **post**: drop the slop section; state the cycle as the Glossary does; Diff tab = changes since first published ([#54](https://github.com/Twin-Cities-Open-Systems/resume/pull/54))
- 2026-09-05 **blog**: render every post to a Gold HTML page -- no more raw markdown ([#45](https://github.com/Twin-Cities-Open-Systems/resume/pull/45))
- 2026-08-30 **og**: add real OG RDFa prefix + fb:app_id to spencer.blog post pages ([#42](https://github.com/Twin-Cities-Open-Systems/resume/pull/42))
- 2026-08-30 **index**: scope blog-post render to the resolved profile, not every profile ([#40](https://github.com/Twin-Cities-Open-Systems/resume/pull/40))
- 2026-08-30 **assets**: replace red-square/Tux-penguin og:image fallbacks with a real, deterministic org logo ([#41](https://github.com/Twin-Cities-Open-Systems/resume/pull/41))
- 2026-08-30 **index**: real Gold redesign, link-based blog entries, real favicons ([#38](https://github.com/Twin-Cities-Open-Systems/resume/pull/38))
- 2026-08-29 two real bugs that made the automated build pipeline never actually work ([#35](https://github.com/Twin-Cities-Open-Systems/resume/pull/35))
- 2026-08-28 **blog**: real lab-aware links, category hubs, set-and-forget media_dns, README ([#31](https://github.com/Twin-Cities-Open-Systems/resume/pull/31))
- 2026-08-26 **deploy**: real dist/profiles mirror -- fixes a live regression I caused (`d8d98db`)
- 2026-08-26 **bin**: stop hardcoding a Cloudflare Global API Key in plaintext ([#21](https://github.com/Twin-Cities-Open-Systems/resume/pull/21))
- 2026-08-26 **convert.sh**: wire the root dist/resume-<slug>.html copy in (`dc6b1f3`)
- 2026-08-26 **blog**: real per-host profile detection + Resume/Media links ([#25](https://github.com/Twin-Cities-Open-Systems/resume/pull/25))
- 2026-08-20 **security**: swap remaining 6 hardcoded CF credentials for env vars (`6598561`)
- 2026-08-20 **cf**: correct wrong zone ID hardcoded across all bin/ scripts (`94d559a`)
- 2026-08-20 **ingress**: make /people/<name> redirect actually work for all people (`ef42e91`)

### Documentation

- 2026-08-31 **governance**: import org PROMPTING_RULES via CLAUDE.md ([#43](https://github.com/Twin-Cities-Open-Systems/resume/pull/43))
- 2026-08-30 **blog**: real, honest mid-session troubled-state log ([#39](https://github.com/Twin-Cities-Open-Systems/resume/pull/39))
- 2026-08-30 **standalone-pages**: real record of two pages published to prod ([#37](https://github.com/Twin-Cities-Open-Systems/resume/pull/37))
- 2026-08-28 **blog**: real, living draft -- soup-to-nuts vanity call sign hunt ([#30](https://github.com/Twin-Cities-Open-Systems/resume/pull/30))
- 2026-08-19 align repo documentation architecture with master TCOS blueprint (`c7dc352`)

### Changed

- 2026-08-31 add the org CI baseline (PROMPTING_RULES rule 16) ([#44](https://github.com/Twin-Cities-Open-Systems/resume/pull/44))
- 2026-08-20 **dns**: working, added records to square and cf ([#11](https://github.com/Twin-Cities-Open-Systems/resume/pull/11))
- 2026-08-20 **fixing**: more 'this is it scripts' ([#10](https://github.com/Twin-Cities-Open-Systems/resume/pull/10))
- 2026-08-20 **hack**: fixing ... maybe ([#9](https://github.com/Twin-Cities-Open-Systems/resume/pull/9))
- 2025-04-19 update resume after Groq ([#4](https://github.com/Twin-Cities-Open-Systems/resume/pull/4))

### Other

- 2026-09-06 feat/media icons ([#74](https://github.com/Twin-Cities-Open-Systems/resume/pull/74))
- 2026-08-28 reskin blog-hub/media-hub off view.lab's token system ([#33](https://github.com/Twin-Cities-Open-Systems/resume/pull/33))
- 2026-08-26 **touchy-claude**: 003 -- Publishing the Thing That Publishes This (`137d28b`)
- 2026-08-26 thin JSON index, fetch real post content from .md on demand (`5875739`)
- 2026-08-26 add touchy-claude's 002 post to the live root blog_manifest.json (`60c1318`)
- 2026-08-26 **touchy-claude**: 002 -- Tools to Build the Tools to Build the Empires (`d34b22b`)
- 2026-08-26 Spencer's first personal GPG signature on published prod content ([#26](https://github.com/Twin-Cities-Open-Systems/resume/pull/26))
- 2026-08-25 chat-mach-dude-kthxbai -- the 2017 PlutoTV/Slim Jim callback ([#13](https://github.com/Twin-Cities-Open-Systems/resume/pull/13))
- 2026-08-20 feature/wrangler per repo only ([#8](https://github.com/Twin-Cities-Open-Systems/resume/pull/8))
- 2026-08-19 docs/follow roadmap to mono repo ([#7](https://github.com/Twin-Cities-Open-Systems/resume/pull/7))
- 2026-06-15 summer updates (`28c02aa`)
- 2024-08-03 Update README.md (`a4d5214`)
- 2023-12-19 Honeycomb is now a Client of TCOS (`59311dc`)
- 2023-03-06 2023 - Back at Honeycomb (`dee8998`)
- 2020-11-30 added UPPER (`eda207e`)
- 2020-11-04 post KW update ([#3](https://github.com/Twin-Cities-Open-Systems/resume/pull/3))
- 2019-11-19 Added convert.sh (`ea4788e`)
- 2019-11-18 Added alternate formats. (`26a1bf0`)
- 2019-11-18 Spencer (`10b908f`)
- 2019-11-18 Spencer (`c738748`)
- 2019-11-18 Spencer (`bf7742f`)
