#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# media-item.py -- build one <oper>.media.tcos.us item (a gallery of signed
# files with an EXIF detail page) from a Card-shaped manifest, in the exact
# design of the first real item, tux-tattoo: every file's bytes inlined so
# the page verifies the real detached GPG signature over them in the
# viewer's browser; an EXIF badge per file into exif.html?id=<stem> with
# the complete exiftool output embedded at build time; the media shell
# (shell-theme.css / shell-toggles.js / shell-freshness.js); full Open
# Graph on both pages.
#
# Operator, 2026-09-05: "let's look at the exif for spencer.media.tcos.us/
# tux-tattoo/ and replicate this design (this still needs to be converted
# to Kind: Card, but for now let's just use the same tools)". So: the
# markup, CSS and JS are tux-tattoo's, lifted into media/templates/ with
# only the item-specific strings parametrized; the manifest is already a
# kind: Card so the conversion is done rather than pending.
#
# The tools: hee-exif embed-exif (EXIF_DATA), hee-exif regen-pubkey
# (PUBKEY_ARMORED from github.com/<login>.gpg), and the .asc files
# hee-exif gpg-sign wrote beside each file (SIGNATURES). Found at
# $HEE_REPO_DIR or ~/git/human-execution-engine, never vendored.
#
# Usage:
#   media/bin/media-item.py build <item-dir>        # <item-dir>/item.card.v1.yaml -> index.html + exif.html
#   media/bin/media-item.py build <item-dir> --no-network   # skip regen-pubkey (offline check)
#   media/bin/media-item.py root <media-dist> [--posts MANIFEST --oper SLUG --posts-src DIR]
#       regenerate the media root's <ul class="items"> from every item card
#       under <media-dist>, plus this oper's blog posts (copied into
#       <media-dist>/posts/ from the rendered Gold pages). Operator,
#       2026-09-05: "get *blog.lab migrated to *media.lab to prepare to sync
#       to prod" -- one host per person, posts and galleries on it.
import base64
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from string import Template

import yaml
from PIL import Image

HERE = Path(__file__).resolve().parent
# The org's Google tag, one source for every generator (hee_gtag in
# human-execution-engine); the ID from the branding card via $HEE_BRANDING.
# Immediately after <head> on both pages -- tcos-www#52.
sys.path.insert(0, str(Path(os.environ.get("HEE_REPO_DIR", Path.home() / "git" / "human-execution-engine")) / "library" / "py"))
try:
    import hee_gtag
    GTAG = hee_gtag.snippet_or_empty()
except ImportError:
    print("⚠️  WARNING hee_gtag not importable -- media pages ship without the Google tag", file=sys.stderr); GTAG = ""
TEMPLATES = HERE.parent / "templates"
HEE_EXIF = Path(os.environ.get("HEE_REPO_DIR", Path.home() / "git" / "human-execution-engine")) / "tooling" / "bin" / "hee-exif"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def esc(s):
    return html.escape(str(s), quote=True)


def data_uri(path):
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# Inline a file's bytes only up to this size. tux-tattoo inlined everything
# and its photos are small; a 1.9 MB GIF becomes a 2.5 MB data: URI, which
# browsers cap at about 2 MB -- measured 2026-09-05: the GIF was in the
# page byte-for-byte and the operator could not see it. Larger files are
# referenced by URL and the GPG check fetches them instead.
INLINE_MAX = 1024 * 1024


def figure(item, item_dir, signatures):
    f = item_dir / item["file"]
    stem = f.stem
    src = data_uri(f) if f.stat().st_size <= INLINE_MAX else esc(f.name)
    exif_badge = (f'<a class="evidence-hover exif-badge" tabindex="0" href="exif.html?id={esc(stem)}" target="_blank" rel="noopener">'
                  f'EXIF: {esc(item.get("exif_label", "real, embedded"))}</a>')
    gpg = (f'<span class="gpg-badge" data-photo="{esc(stem)}" tabindex="0"><span class="gpg-dot"></span><span class="gpg-text">verifying…</span></span>'
           if stem in signatures else '<span class="exif-badge none">unsigned</span>')
    return f'''    <figure class="photo" data-tag="{esc(item.get("tag", "item"))}" data-date="{esc(item.get("date", ""))}">
      <img id="img-{esc(stem)}" src="{src}" alt="{esc(item["title"])}" loading="lazy" tabindex="0">
      <figcaption>
        <span class="ft">{esc(item["title"])}</span>
        <span class="fc">{esc(item.get("caption", ""))}</span>
        <span class="fmeta">{exif_badge}</span>
        <span class="fmeta">{gpg}</span>
      </figcaption>
    </figure>'''


def build(item_dir, network=True):
    item_dir = Path(item_dir).resolve()
    card_path = item_dir / "item.card.v1.yaml"
    if not card_path.is_file():
        sys.exit(f"media-item: {card_path} missing")
    card = yaml.safe_load(card_path.read_text())
    if card.get("apiVersion") != "hee/v1" or card.get("kind") != "Card":
        sys.exit(f"media-item: {card_path} is not an apiVersion hee/v1 kind Card")
    spec = card["spec"]
    slug = item_dir.name
    if spec.get("consent") not in (None, "approved"):
        print(f"⚠️  WARNING  {slug}: consent is {spec['consent']!r} -- build for lab review only; deploy.sh promote will refuse")
    host = spec["host"]                                  # e.g. spencer.media.tcos.us
    host_short = host.split(".tcos.us")[0]              # spencer.media
    url = f"https://{host}/{slug}/"
    items = spec["items"]
    stems = {}
    for it in items:
        if not (item_dir / it["file"]).is_file():
            sys.exit(f"media-item: {it['file']} named in the card is not in {item_dir}")
        # the file stem is the id everywhere -- exif.html?id=, SIGNATURES,
        # EXIF_DATA, the <img id> -- so two files may not share one
        # (bofh.gif + bofh.jpg would silently drop one from every table)
        st = Path(it["file"]).stem
        if st in stems:
            sys.exit(f"media-item: {it['file']} and {stems[st]} share the stem {st!r}; rename one")
        stems[st] = it["file"]

    # signatures: <file>.asc beside each file, as hee-exif gpg-sign writes them
    signatures = {}
    for it in items:
        asc = item_dir / (it["file"] + ".asc")
        if asc.is_file():
            signatures[Path(it["file"]).stem] = asc.read_text()

    # The og:image is the content, never a generic banner. Operator,
    # 2026-09-05: "make sure that the og image is always pertinent to the
    # content. for this mn2600, og gif should be used." So it must be one
    # of the item's own files; default is the first item.
    og_name = spec.get("og_image", items[0]["file"])
    if og_name not in {it["file"] for it in items}:
        sys.exit(f"media-item: og_image {og_name!r} is not one of this item's files -- the preview must show the content itself")
    og_file = item_dir / og_name
    with Image.open(og_file) as im:
        og_w, og_h = im.size
    stats = ""
    if spec.get("stats"):
        stats = '  <div class="stat-row">\n' + "\n".join(
            f'    <div class="stat"><div class="n">{esc(s["n"])}</div><div class="l">{esc(s["l"])}</div></div>' for s in spec["stats"]) + "\n  </div>\n"
    credit = spec.get("credit", {})
    credit_html = f'    <span class="headline">{credit.get("headline_html") or esc(credit.get("headline", ""))}</span>\n'
    for note in credit.get("notes", []):
        credit_html += f'    <span class="note">{note}</span>\n'
    tags = {it.get("tag", "item"): it.get("tag", "item").replace("-", " ").title() for it in items}
    tags.update(spec.get("tag_labels", {}))
    group_toolbar = ""
    if len(tags) > 1:
        group_toolbar = '''  <div class="group-toolbar" role="group" aria-label="Group items">
    <span class="gt-label">Group:</span>
    <button type="button" class="gt-btn active" data-group="none">None</button>
    <button type="button" class="gt-btn" data-group="date">Date</button>
    <button type="button" class="gt-btn" data-group="tag">Kind</button>
  </div>
'''
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    signer = spec.get("signer", {})
    attester = spec.get("attester", {})
    values = dict(
        TITLE=esc(spec["title"]), OWNER=esc(spec.get("owner", "")), DESCRIPTION=esc(spec["description"]),
        HOST=esc(host), HOST_SHORT=esc(host_short), SLUG=esc(slug), OG_URL=esc(url), OG_URL_EXIF=esc(url + "exif.html"),
        OG_IMAGE=esc(f"https://{host}/{slug}/{og_file.name}"), OG_IMAGE_ALT=esc(spec.get("og_image_alt", spec["title"])),
        OG_IMAGE_W=og_w, OG_IMAGE_H=og_h,
        EYEBROW=esc(spec.get("eyebrow", spec["title"].lower())), SUB=spec.get("sub_html") or esc(spec.get("sub", spec["description"])),
        STATS=stats, CREDIT=credit_html, GENERATED=generated,
        SOURCE_URL=esc(spec.get("source_url", f"https://github.com/Twin-Cities-Open-Systems/resume/blob/main/media/{host.split('.')[0]}/dist/{slug}/item.card.v1.yaml")),
        SOURCE_LABEL=esc(spec.get("source_label", "item.card.v1.yaml")),
        GROUP_TOOLBAR=group_toolbar,
        FIGURES="\n".join(figure(it, item_dir, signatures) for it in items),
        # a card with no footer gets no dangling separator; the footer is
        # optional (operator, 2026-09-06: "kill this cruft")
        FOOTER=(" &middot; " + (spec.get("footer_html") or esc(spec["footer"]))) if (spec.get("footer_html") or spec.get("footer")) else "",
        OPENPGP_SRC=esc(spec.get("openpgp_src", "/openpgp.min.js")),
        SIGNER_LABEL=esc(signer.get("label", signer.get("github_login", "signer"))),
        ATTESTER_LABEL=esc(attester.get("label", "")),
        TAG_LABELS_JSON=json.dumps(tags),
        GTAG=GTAG.replace("$", "$$"),
    )
    index = Template((TEMPLATES / "item-index.html.tmpl").read_text()).substitute(values)
    index = index.replace("var SIGNATURES = {};", "var SIGNATURES = " + json.dumps(signatures) + ";")
    (item_dir / "index.html").write_text(index)
    exif_page = Template((TEMPLATES / "item-exif.html.tmpl").read_text()).substitute(values)
    (item_dir / "exif.html").write_text(exif_page)
    print(f"[+] {item_dir / 'index.html'} ({len(items)} item(s), {len(signatures)} signed)")

    # the org's tools fill the two data vars
    exts = ",".join(sorted({Path(it["file"]).suffix.lstrip(".").lower() for it in items}))
    subprocess.run([str(HEE_EXIF), "embed-exif", str(item_dir / "exif.html"), "EXIF_DATA", str(item_dir), "--ext", exts], check=True)
    if network and signer.get("github_login"):
        subprocess.run([str(HEE_EXIF), "regen-pubkey", str(item_dir / "index.html"), "PUBKEY_ARMORED", signer["github_login"]], check=True)
    if network and attester.get("github_login"):
        subprocess.run([str(HEE_EXIF), "regen-pubkey", str(item_dir / "index.html"), "PUBKEY_ARMORED_SPENCER", attester["github_login"]], check=True)

    # the media root lists every item; add this one if it is not there
    root = item_dir.parent / "index.html"
    if root.is_file() and f'href="/{slug}"' not in root.read_text():
        li = (f'    <li>\n      {icon_for_card(card, "gallery")}\n      <div>\n'
              f'        <a href="/{esc(slug)}">{esc(spec["title"])}</a>\n        <p>{esc(spec["description"])}</p>\n      </div>\n    </li>\n')
        r = root.read_text()
        r = r.replace("  </ul>\n  <p class=\"note\">", li + "  </ul>\n  <p class=\"note\">", 1)
        root.write_text(r)
        print(f"[+] listed on {root}")
    return 0


ITEMS_RE = re.compile(r'(  <ul class="items">\n)(.*?)(  </ul>\n)', re.S)


ROOT_TMPL = Path(__file__).resolve().parent.parent / "templates" / "root-index.html.tmpl"


# Card icons: Fluent Emoji, color style (Microsoft, MIT; vendored at a
# pinned commit under media/shared/icons/fluent/, LICENSE and SOURCE beside
# them), inlined SVG. Chosen from the item's `topic` label, then its kind; a
# card may say `icon: <name>` (the file's name) to override. Operator,
# 2026-09-06: "open source icons besides just the tux ... match to some
# group relevant, or something we can automate", then on a line-icon set:
# "those are drab and same as text. need colors, modern". An unknown name
# falls back to the kind's icon and says so, never to a broken image.
ICON_DIR = Path(__file__).resolve().parent.parent / "shared" / "icons" / "fluent"
ICON_BY_TOPIC = {"meme": "party_popper", "tattoo": "paintbrush", "photo": "camera", "photos": "camera",
                 "video": "clapper_board", "audio": "musical_notes", "music": "musical_notes", "code": "laptop",
                 "talk": "microphone", "book": "open_book", "hardware": "wrench", "gif": "film_frames",
                 "linux": "penguin"}
ICON_BY_KIND = {"gallery": "framed_picture", "post": "memo", "resume": "page_facing_up"}


def icon_svg(name, kind="gallery"):
    for candidate in (name, ICON_BY_KIND.get(kind, "framed_picture")):
        if not candidate:
            continue
        f = ICON_DIR / f"{candidate}.svg"
        if f.is_file():
            # referenced, not inlined: Fluent color SVGs carry gradient ids
            # that collide when several sit in one document
            return f'<img class="item-icon" src="/icons/fluent/{candidate}.svg" alt="" width="36" height="36">'
        if candidate == name:
            print(f"⚠️  WARNING  media-item: no vendored icon {name!r}; using the {kind} default", file=sys.stderr)
    return ""


def icon_for_card(card, kind="gallery"):
    spec = card.get("spec", {}); labels = (card.get("metadata") or {}).get("labels") or {}
    return icon_svg(spec.get("icon") or ICON_BY_TOPIC.get(str(labels.get("topic", "")).lower()), kind)


def root_init(media_dist, oper_name, media_host, blog_host=None, description=None):
    """Write a fresh root page for an operator from the shared template --
    the page spencer's was hand-written as, with name and hosts filled in.
    One host per person: <prefix>.media.tcos.us. Operator, 2026-09-06:
    "make sure the new ones are added (will be just the base with no blogs
    yet)"."""
    import datetime as dt
    import string
    media_dist = Path(media_dist).resolve(); media_dist.mkdir(parents=True, exist_ok=True)
    index = media_dist / "index.html"
    if index.exists():
        print(f"⚠️  WARNING  media-item root --init: {index} exists, not overwriting", file=sys.stderr)
        return 1
    short = media_host.replace(".tcos.us", "")
    # The sub-line under the host is the operator's resume when the build
    # has one (profiles/<oper>/dist/resume.html, staged as /resume.html on
    # the media host). Never the blog host: it is a redirect now, and the
    # first prod promote sent readers of the resume to the media root
    # (operator, 2026-09-06: "remove old blog link, where is my resume?").
    has_resume = (media_dist.parent.parent.parent / "profiles" / media_dist.parent.name / "dist" / "resume.html").is_file()
    blog_line = '  <p class="eyebrow eyebrow-sub"><a href="/resume.html">resume</a></p>\n' if has_resume else ""
    if not description:
        # From the operator's own profile (title + role), never another
        # person's page text. Operator, 2026-09-06: the new roots carried
        # spencer's tattoo-page description verbatim.
        prof = media_dist.parent.parent.parent / "profiles" / media_dist.parent.name / "profile.json"
        try:
            pj = json.loads(prof.read_text())
            title = pj["language_profiles"]["payloads"]["professional"]["title"]
            description = f"{title} at Twin Cities Open Systems -- posts, galleries and verified media."
        except Exception:
            description = f"{oper_name} at Twin Cities Open Systems -- posts, galleries and verified media."
    page = string.Template(ROOT_TMPL.read_text()).safe_substitute(
        OPER_NAME=esc(oper_name), MEDIA_HOST=media_host, MEDIA_SHORT=short, BLOG_LINE=blog_line, DESCRIPTION=esc(description),
        LU_ISO=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    index.write_text(page)
    print(f"[+] {index}: root for {oper_name} at https://{media_host}/")
    return 0


def root(media_dist, posts_manifest=None, oper=None, posts_src=None):
    """The media root lists galleries (every item.card.v1.yaml below it, by
    date) and this oper's blog posts, copied in from the rendered Gold
    pages. The <ul class="items"> block is the only generated region of
    the root page; everything around it stays hand-written."""
    media_dist = Path(media_dist).resolve()
    rows = []
    for card_path in sorted(media_dist.glob("*/item.card.v1.yaml")):
        card = yaml.safe_load(card_path.read_text()); spec = card["spec"]
        slug = card_path.parent.name
        when = spec.get("date") or max((it.get("date", "") for it in spec.get("items", [])), default="")
        rows.append((when, "gallery", f"/{slug}/", spec["title"], spec["description"], icon_for_card(card, "gallery")))  # trailing slash: busybox httpd does not redirect a bare dir
    if posts_manifest and oper:
        posts_dir = media_dist / "posts"; posts_dir.mkdir(exist_ok=True)
        for post in json.loads(Path(posts_manifest).read_text()):
            if not post["path"].startswith(f"profiles/{oper}/") or not post.get("html"):
                continue
            src = Path(posts_src or ".") / post["html"]
            if not src.is_file():
                print(f"⚠️  WARNING  media-item root: rendered post missing, skipped: {src}", file=sys.stderr); continue
            dst = posts_dir / (post["slug"] + ".html")
            dst.write_bytes(src.read_bytes())
            rows.append((post["date"], "post", f"/posts/{post['slug']}.html", post["title"],
                         f"Blog post, {post['date']}.", icon_svg(None, "post")))
    rows.sort(key=lambda r: r[0], reverse=True)
    li = "".join(
        f'    <li data-kind="{esc(kind)}">\n      {icon}\n      <div>\n'
        f'        <a href="{esc(href)}">{esc(title)}</a>\n        <p><span class="mono">{esc(when)} &middot; {esc(kind)}</span> &mdash; {esc(desc)}</p>\n      </div>\n    </li>\n'
        for when, kind, href, title, desc, icon in rows)
    index = media_dist / "index.html"
    s = index.read_text()
    m = ITEMS_RE.search(s)
    if not m:
        sys.exit(f"media-item root: no <ul class=\"items\"> block in {index}")
    new_s = s[:m.start()] + m.group(1) + li + m.group(3) + s[m.end():]
    # lu: this page's last-updated. It was a hand-set stamp the deploy never
    # touched, so it read 2026-08-26 under a listing rewritten daily
    # (operator, 2026-09-06: "lu: is wrong"). The builder owns it now: when
    # the listing changes, or the stamp is older than the newest item, lu is
    # the build time. Unchanged content keeps its stamp.
    import datetime as dt
    lu_re = re.compile(r'(<time class="lu-iso" datetime=")([^"]*)(">)([^<]*)(</time>)')
    lm = lu_re.search(new_s)
    newest = max((r[0] for r in rows), default="")
    if lm:
        old_lu = lm.group(2)
        if new_s != s or (newest and old_lu[:10] < newest[:10]):
            now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            new_s = lu_re.sub(lambda mm: f"{mm.group(1)}{now}{mm.group(3)}{now}{mm.group(5)}", new_s, count=1)
    index.write_text(new_s)
    print(f"[+] {index}: {sum(1 for r in rows if r[1]=='gallery')} gallery(ies), {sum(1 for r in rows if r[1]=='post')} post(s)")
    return 0


def audit(repo_root, env="lab"):
    """Is every page indexed somewhere, and does every old blog URL land?
    Operator, 2026-09-06: "make sure all of redirects are correct from blog
    to media and there are no 404s and our audit tool is smart enough to
    notice when a page is not indexed somewhere. media.tcos.us should be
    the index of all the subs."
      1. every operator with media_dns is listed by the media hub's data
         (people.json on the hub host) and answers 200;
      2. every post and gallery under media/<oper>/dist is linked from that
         operator's root page;
      3. every post URL a reader may hold -- current name, every former
         (numbered) name, .md and .html -- on <prefix>.blog.<env> 301s to
         the media host and the target answers 200.
    Nagios exit: 0 OK, 1 WARNING (unlisted), 2 CRITICAL (404/bad redirect)."""
    import subprocess
    import urllib.request
    import urllib.error
    repo_root = Path(repo_root).resolve()
    suffix = ".lab.tcos.us" if env == "lab" else ".tcos.us"
    if env == "prod":
        # Prod names resolve through public DNS, whatever the LAN resolver
        # does. On kiosk ns1 REFUSES public names and the search list hands
        # them to the crooked.tcos.us wildcard (Traefik default cert), which
        # read as four dead media hosts on the first prod run (fleet-ops#399).
        import socket
        _real = socket.getaddrinfo
        _cache = {}
        def _public(host, port, family=0, type=0, proto=0, flags=0):
            if isinstance(host, str) and host.endswith(".tcos.us") and not host.endswith(".lab.tcos.us"):
                if host not in _cache:
                    out = subprocess.run(["dig", "+short", "+time=3", "A", host + ".", "@1.1.1.1"], capture_output=True, text=True).stdout.split()
                    _cache[host] = [a for a in out if a.replace(".", "").isdigit()]
                if _cache[host]:
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in _cache[host]]
                raise socket.gaierror(f"{host}: no public A record (1.1.1.1)")
            return _real(host, port, family, type, proto, flags)
        socket.getaddrinfo = _public
    people = json.loads((repo_root / "dist" / "people.json").read_text())
    worst = 0

    def code_and_final(url):
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "media-item audit"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, url
        except Exception as e:
            return None, str(e)[:60]

    # 1. the hub
    hub = f"https://media{suffix}/people.json"
    try:
        # Cloudflare answers 403 to the default Python-urllib user agent on
        # the Pages hosts (measured 2026-09-06: same URL, 200 with any
        # other agent). Every request here names itself.
        with urllib.request.urlopen(urllib.request.Request(hub, headers={"User-Agent": "media-item audit"}), timeout=8) as r:
            hub_people = json.loads(r.read().decode())
        hub_hosts = {p["media_dns"] for p in hub_people if p.get("media_dns")}
    except Exception as e:
        print(f"🔴 CRITICAL audit: media hub data unreachable: {hub} ({e})"); hub_hosts = set(); worst = 2
    for p in people:
        if not p.get("media_dns"):
            continue
        host = p["media_dns"].replace(".tcos.us", suffix)
        code, _ = code_and_final(f"https://{host}/")
        if code != 200:
            print(f"🔴 CRITICAL audit: {host}/ -> {code}"); worst = 2
        if p["media_dns"] not in hub_hosts:
            print(f"🟡 WARNING audit: {p['media_dns']} is not in the media hub's index"); worst = max(worst, 1)

    # 2. every page indexed on its root
    for root_index in sorted(repo_root.glob("media/*/dist/index.html")):
        oper_dir = root_index.parent; oper = oper_dir.parent.name
        index = root_index.read_text()
        expected = [f"/posts/{f.name}" for f in sorted((oper_dir / "posts").glob("*.html"))]
        expected += [f"/{c.parent.name}/" for c in sorted(oper_dir.glob("*/item.card.v1.yaml"))]
        for href in expected:
            if f'href="{href}"' not in index:
                print(f"🟡 WARNING audit: {oper}: {href} exists but the root does not list it"); worst = max(worst, 1)

    # 2b. every root's og:description is its own, and og:title names the operator
    descs = {}
    for root_index in sorted(repo_root.glob("media/*/dist/index.html")):
        oper = root_index.parent.parent.name; html_ = root_index.read_text()
        m1 = re.search(r'<meta property="og:description" content="([^"]*)"', html_)
        m2 = re.search(r'<meta property="og:title" content="([^"]*)"', html_)
        d = m1.group(1) if m1 else ""
        descs.setdefault(d, []).append(oper)
        name = json.loads((repo_root / "profiles" / oper / "profile.json").read_text())["meta"]["entity"]
        if not m2 or name.split()[0].lower() not in m2.group(1).lower():
            print(f"🟡 WARNING audit: {oper}: og:title does not name the operator: {m2.group(1) if m2 else '(none)'}"); worst = max(worst, 1)
    for d, opers in descs.items():
        if len(opers) > 1:
            print(f"🟡 WARNING audit: same og:description on {', '.join(opers)}: {d[:70]!r}"); worst = max(worst, 1)

    # 3. every blog URL a reader may hold
    former = {}
    log = subprocess.run(["git", "log", "--diff-filter=R", "--name-status", "--format=", "-M", "--", "profiles/*/blog/*.md"],
                         cwd=repo_root, capture_output=True, text=True).stdout
    for line in log.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].startswith("R"):
            former.setdefault(parts[2], set()).add(parts[1])
    prefix_of = {p["slug"]: (p["subdomain_prefix"], p.get("media_dns")) for p in people}
    manifest = json.loads((repo_root / "dist" / "blog_manifest.json").read_text())
    n = 0
    for post in manifest:
        oper = post["path"].split("/")[1]
        prefix, media = prefix_of.get(oper, (None, None))
        if not media:
            continue
        names = {post["path"]} | former.get(post["path"], set())
        target = f"https://{media.replace('.tcos.us', suffix)}/posts/{post['slug']}.html"
        for name in sorted(names):
            for ext in (".md", ".html"):
                url = f"https://{prefix}.blog{suffix}/" + name[:-3] + ext
                code, final = code_and_final(url); n += 1
                # The media Workers serve assets with clean URLs: /posts/x.html
                # answers 307 -> /posts/x, so the final URL a reader lands on
                # is the target without its .html. Both forms are the target.
                landed = final.rstrip("/")
                if code != 200 or landed not in (target, target[:-5]):
                    print(f"🔴 CRITICAL audit: {url} -> {code} {final} (expected {target})"); worst = 2
    # 4. the resume: on the media host, and every old blog URL for it lands there
    for p in people:
        media = p.get("media_dns")
        if not media or not (repo_root / "profiles" / p["slug"] / "dist" / "resume.html").is_file():
            continue
        host = media.replace(".tcos.us", suffix)
        code, final = code_and_final(f"https://{host}/resume.html"); n += 1
        if code != 200:
            print(f"🔴 CRITICAL audit: https://{host}/resume.html -> {code}"); worst = 2
        if env == "prod":
            for old_url in (f"https://{p['subdomain_prefix']}.blog{suffix}/resume-{p['slug']}.html",
                            f"https://{p['subdomain_prefix']}.blog{suffix}/profiles/{p['slug']}/dist/resume.html"):
                code, final = code_and_final(old_url); n += 1
                if code != 200 or final.rstrip("/") not in (f"https://{host}/resume.html", f"https://{host}/resume"):
                    print(f"🔴 CRITICAL audit: {old_url} -> {code} {final} (expected https://{host}/resume.html)"); worst = 2
    label = {0: "🟢 OK", 1: "🟡 WARNING", 2: "🔴 CRITICAL"}[worst]
    print(f"{label} media-item audit ({env}): {sum(1 for p in people if p.get('media_dns'))} media host(s), "
          f"{n} blog URL(s) probed, {len(list(repo_root.glob('media/*/dist/index.html')))} root(s) checked")
    return worst


def main(argv):
    if argv and argv[0] == "audit":
        env = "prod" if "--prod" in argv else "lab"
        return audit(Path(__file__).resolve().parent.parent.parent, env)
    if len(argv) >= 2 and argv[0] == "root":
        flags = [a for a in argv[2:] if a == "--init"]
        rest = [a for a in argv[2:] if a != "--init"]
        opts = dict(zip(rest[0::2], rest[1::2]))
        if flags:
            if not (opts.get("--name") and opts.get("--host")):
                sys.exit("usage: media-item.py root <media-dist> --init --name NAME --host <prefix>.media.tcos.us [--blog-host HOST]")
            return root_init(argv[1], opts["--name"], opts["--host"], opts.get("--blog-host"))
        return root(argv[1], opts.get("--posts"), opts.get("--oper"), opts.get("--posts-src"))
    if len(argv) < 2 or argv[0] != "build":
        print(__doc__ or "usage: media-item.py build <item-dir> [--no-network] | root <media-dist> [--init --name N --host H] | audit [--prod]"); return 2
    return build(argv[1], network="--no-network" not in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
