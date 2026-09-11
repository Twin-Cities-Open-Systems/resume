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
#   media/bin/media-item.py kit <item-dir>          # spec.kit -> watermark, avatar, banner PNGs, stamped and signed
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
from PIL import Image, ImageOps

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
    url = f"https://{host}/gallery/{slug}/"   # items live under their kind since resume#86
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
        # A photo stored sideways with an EXIF rotate flag looks right in a
        # browser and wrong everywhere that ignores the flag (the og card,
        # link previews, some viewers). Straighten the pixels BEFORE signing:
        # rotating a signed file breaks its signature. Operator, 2026-09-11,
        # on 36th 23rd street: "in future we want correct photo orientation".
        try:
            with Image.open(item_dir / it["file"]) as _im:
                _orient = _im.getexif().get(0x0112, 1)
        except Exception:  # noqa: BLE001 -- not an image this check can read
            _orient = 1
        if _orient not in (0, 1):
            print(f"⚠️  WARNING  {slug}: {it['file']} is stored rotated (EXIF Orientation {_orient}) -- "
                  "rotate the pixels and reset Orientation to 1 before signing (exiftool can't; e.g. PIL ImageOps.exif_transpose)")

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
    # Social cards crop to ~1.91:1 (Facebook and X cut the top line off a
    # 4:3 frame, measured 2026-09-06); Discord shows the whole thing. So the
    # og:image is a 1200x630 JPEG with the frame letterboxed on the card's
    # og_bg (default near-black), built here from the same file; the GIF
    # stays the first item. og_bg: "#rrggbb" on the card to change the bars.
    og_src = og_file
    with Image.open(og_src) as im:
        im.seek(0)
        frame = ImageOps.exif_transpose(im).convert("RGB")   # the card shows the photo upright, whatever its flag
    W, H = 1200, 630
    bg = spec.get("og_bg", "#0b0f0b").lstrip("#")
    canvas = Image.new("RGB", (W, H), tuple(int(bg[i:i + 2], 16) for i in (0, 2, 4)))
    scale = min(W / frame.width, H / frame.height)
    fitted = frame.resize((max(1, round(frame.width * scale)), max(1, round(frame.height * scale))), Image.LANCZOS)
    canvas.paste(fitted, ((W - fitted.width) // 2, (H - fitted.height) // 2))
    og_file = item_dir / "og.jpg"
    canvas.save(og_file, "JPEG", quality=88, optimize=True, progressive=True)
    # the org's standard metadata on the derived card, like every published
    # file: provenance (from which source file), agent signature, branding
    env = dict(os.environ)
    if not env.get("HEE_BRANDING") and (Path.home() / "git/tcos-audit/policy/branding.card.v1.yaml").is_file():
        env["HEE_BRANDING"] = str(Path.home() / "git/tcos-audit/policy/branding.card.v1.yaml")
    # A personal item stamps its og card with its own identity, the card's
    # kit.branding (or top-level branding). The page's Google tag still comes
    # from the org card, since the page lives on the org's host.
    own = spec.get("branding") or (spec.get("kit") or {}).get("branding")
    if own:
        own = os.path.expanduser(own)
        if not Path(own).is_file():
            sys.exit(f"media-item: branding card {own} not found -- a personal item must not fall back to the org's card")
        env["HEE_BRANDING"] = own
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
    subprocess.run([str(HEE_EXIF), "provenance", str(og_file), "--tool", "resume/media-item", "--commit", commit,
                    "--job", str(card_path), "--source", str(og_src), "--kv", "shape=card 1200x630 letterboxed",
                    "--kv", f"og_for=https://{host}/gallery/{slug}/", "--kv", "page=gallery", "--kv", f"owner={spec.get('owner', '')}",
                    "--kv", f"title={spec['title'].replace(';', ',')}", "--kv", f"host={host}"], check=True, capture_output=True, env=env)
    subprocess.run([str(HEE_EXIF), "sign", str(og_file)], check=True, capture_output=True, env=env)
    if env.get("HEE_BRANDING"):
        subprocess.run([str(HEE_EXIF), "brand", str(og_file), "--artist", spec.get("owner", "Twin Cities Open Systems")], check=True, capture_output=True, env=env)
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
        OG_IMAGE=esc(f"https://{host}/gallery/{slug}/{og_file.name}"), OG_IMAGE_ALT=esc(spec.get("og_image_alt", spec["title"])),
        OG_IMAGE_W=og_w, OG_IMAGE_H=og_h,
        EYEBROW=esc(spec.get("eyebrow", spec["title"].lower())), SUB=spec.get("sub_html") or esc(spec.get("sub", spec["description"])),
        STATS=stats, CREDIT=credit_html, GENERATED=generated,
        SOURCE_URL=esc(spec.get("source_url", f"https://github.com/Twin-Cities-Open-Systems/resume/blob/main/media/{host.split('.')[0]}/dist/gallery/{slug}/item.card.v1.yaml")),
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
    index = Template((TEMPLATES / "item-index.html.tmpl").read_text()).safe_substitute(values)
    index = index.replace("var SIGNATURES = {};", "var SIGNATURES = " + json.dumps(signatures) + ";")
    (item_dir / "index.html").write_text(index)
    exif_page = Template((TEMPLATES / "item-exif.html.tmpl").read_text()).safe_substitute(values)
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
    # the root lists it as href="/<slug>/" (busybox needs the slash); both
    # forms count, or every rebuild appended a duplicate card (2026-09-06)
    if root.is_file() and f'href="/{slug}/"' not in root.read_text() and f'href="/{slug}"' not in root.read_text():
        li = (f'    <li>\n      {tile_for_card(card, item_dir, "gallery")}\n      <div>\n'
              f'        <a href="/{esc(slug)}">{esc(spec["title"])}</a>\n        <p>{esc(spec["description"])}</p>\n      </div>\n    </li>\n')
        r = root.read_text()
        r = r.replace("  </ul>\n  <p class=\"note\">", li + "  </ul>\n  <p class=\"note\">", 1)
        root.write_text(r)
        print(f"[+] listed on {root}")
    return 0


ITEMS_RE = re.compile(r'(  <ul class="items">\n)(.*?)(  </ul>\n)', re.S)


ROOT_TMPL = Path(__file__).resolve().parent.parent / "templates" / "root-index.html.tmpl"


# Card tiles: rendered by the org's own meme-factory `tile` generator
# (fleet-ops/tools/meme-factory/tile/tile.py): a two-color gradient, one
# motif, a monogram -- deterministic from the card, no icon set. Operator,
# 2026-09-06: "just make our own with the meme-factory", after two
# open-source sets ("drab", emoji). Palette from the topic label, motif
# from the kind, monogram from the title; a card may set
#   tile: { text: "26", palette: ember, motif: rings }
# to override any of the three. Missing generator -> WARNING, no tile.
TILE_PY = Path(os.environ.get("MEME_FACTORY_TILE", Path.home() / "git/fleet-ops/tools/meme-factory/tile/tile.py"))
PALETTE_BY_TOPIC = {"meme": "ember", "tattoo": "violet", "photo": "ocean", "photos": "ocean", "video": "sunset",
                    "audio": "coral", "music": "coral", "code": "teal", "talk": "mint", "book": "lime",
                    "hardware": "teal", "gif": "ember", "linux": "lime"}
MOTIF_BY_KIND = {"gallery": "rings", "post": "diagonals", "resume": "grid"}
PALETTE_NAMES = ["ember", "violet", "lime", "sunset", "ocean", "mint", "coral", "teal"]


def monogram(title):
    words = [w for w in re.split(r"[^A-Za-z0-9]+", title) if w]
    return ("".join(w[0] for w in words[:2]) or title[:2]).upper()


def tile_png(out_png, *, text, palette, motif, seed, extra=None):
    """Render one tile with meme-factory; returns the served path or ''."""
    if not TILE_PY.is_file():
        print(f"⚠️  WARNING  media-item: meme-factory tile generator not found at {TILE_PY}; cards get no tile", file=sys.stderr)
        return False
    import hashlib, tempfile
    job = {"output": str(out_png), "size": 256, "text": text, "seed": seed, "motif": motif, **(extra or {})}
    sys.path.insert(0, str(TILE_PY.parent))
    import importlib; tile = importlib.import_module("tile")
    job["palette"] = tile.PALETTES.get(palette) or tile.PALETTES["lime"]
    tile.render_job(job)
    return True


def tile_for_card(card, item_dir, page="gallery"):
    spec = card.get("spec", {}); labels = (card.get("metadata") or {}).get("labels") or {}
    t = spec.get("tile") or {}
    text = t.get("text") or monogram(spec.get("title", item_dir.name))
    palette = t.get("palette") or PALETTE_BY_TOPIC.get(str(labels.get("topic", "")).lower(), "lime")
    motif = t.get("motif") or MOTIF_BY_KIND.get(page, "rings")
    host = spec.get("host", "")
    extra = {"for": f"https://{host}/{item_dir.name}/" if host else "", "page": page, "owner": spec.get("owner", ""), "title": spec.get("title", ""), "host": host}
    if tile_png(item_dir / "tile.png", text=text, palette=palette, motif=motif, seed=item_dir.name, extra={k: v for k, v in extra.items() if v}):
        return f'<img class="item-icon" src="/{item_dir.name}/tile.png" alt="" width="40" height="40">'
    return ""


def tile_for_post(page_dir, slug, title, host="", owner="", kind_dir="blog"):
    import hashlib
    palette = PALETTE_NAMES[int(hashlib.sha256(slug.encode()).hexdigest(), 16) % len(PALETTE_NAMES)]
    extra = {k: v for k, v in {"for": f"https://{host}/{kind_dir}/{slug}/" if host else "", "page": "post", "owner": owner, "title": title, "host": host}.items() if v}
    if tile_png(page_dir / "tile.png", text=monogram(title), palette=palette, motif="diagonals", seed=slug, extra=extra):
        return f'<img class="item-icon" src="/{kind_dir}/{slug}/tile.png" alt="" width="40" height="40">'
    return ""


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
    _root_html = (media_dist / "index.html").read_text() if (media_dist / "index.html").is_file() else ""
    _m = re.search(r'<meta property="og:url" content="https://([^/"]+)/', _root_html)
    root_host = _m.group(1) if _m else ""
    try:
        root_owner = json.loads((media_dist.parent.parent.parent / "profiles" / media_dist.parent.name / "profile.json").read_text())["meta"]["entity"]
    except Exception:  # noqa: BLE001
        root_owner = ""
    for card_path in sorted(media_dist.glob("gallery/*/item.card.v1.yaml")):
        card = yaml.safe_load(card_path.read_text()); spec = card["spec"]
        slug = card_path.parent.name
        when = spec.get("date") or max((it.get("date", "") for it in spec.get("items", [])), default="")
        rows.append((when, "gallery", f"/gallery/{slug}/", spec["title"], spec["description"], tile_for_card(card, card_path.parent, "gallery")))  # trailing slash: busybox httpd does not redirect a bare dir
    if posts_manifest and oper:
        # URL kinds, not tags (operator, 2026-09-11): every rendered page lives in
        # its own directory under its kind -- /blog/<slug>/, /thesis/<slug>/ --
        # with index.html, og.jpg and tile.png beside it, like a gallery.
        for post in json.loads(Path(posts_manifest).read_text()):
            if not post["path"].startswith(f"profiles/{oper}/") or not post.get("html"):
                continue
            src = Path(posts_src or ".") / post["html"]
            if not src.is_file():
                print(f"⚠️  WARNING  media-item root: rendered page missing, skipped: {src}", file=sys.stderr); continue
            kind = post.get("kind", "post"); kind_dir = "blog" if kind == "post" else kind
            page_dir = media_dist / kind_dir / post["slug"]; page_dir.mkdir(parents=True, exist_ok=True)
            (page_dir / "index.html").write_bytes(src.read_bytes())
            card = src.with_suffix(".og.jpg")   # the page's social preview, rendered by render-blog
            if card.is_file():
                (page_dir / "og.jpg").write_bytes(card.read_bytes())
            label = {"post": "Blog post", "thesis": "Thesis"}.get(kind, kind.capitalize())
            rows.append((post["date"], kind, f"/{kind_dir}/{post['slug']}/", post["title"],
                         f"{label}, {post['date']}.", tile_for_post(page_dir, post["slug"], post["title"], host=root_host, owner=root_owner, kind_dir=kind_dir)))
    rows.sort(key=lambda r: r[0], reverse=True)
    li = "".join(
        f'    <li data-page="{esc(kind)}">\n      {icon}\n      <div>\n'
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
        expected = [f"/{k}/{d.name}/" for k in ("blog", "thesis") for d in sorted((oper_dir / k).glob("*/")) if (d / "index.html").is_file()]
        expected += [f"/gallery/{c.parent.name}/" for c in sorted(oper_dir.glob("gallery/*/item.card.v1.yaml"))]
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

    # 2c. every page a media host serves carries the Open Graph set. The
    # resume shipped with a <title> and nothing else (2026-09-06, operator:
    # "how did that slip through?") because nothing looked. Static check on
    # the tracked pages, so it fails before a deploy, not after.
    NEED = ("og:title", "og:description", "og:url", "og:image")
    served = [p_["slug"] for p_ in people if p_.get("media_dns")]
    resumes = [repo_root / "profiles" / s_ / "dist" / "resume.html" for s_ in served]
    for page in sorted(list(repo_root.glob("media/*/dist/**/*.html")) + [r for r in resumes if r.is_file()]):
        html_ = page.read_text(errors="replace")
        missing = [t for t in NEED if f'property="{t}"' not in html_]
        if missing:
            print(f"🔴 CRITICAL audit: {page.relative_to(repo_root)} lacks {', '.join(missing)}"); worst = 2

    # 2d. every generated image (tiles, cards) carries the org's provenance
    # and branding in its metadata, like every other file we publish.
    # Operator, 2026-09-06: "all of these og images have our standard
    # exif, right?" -- they did not, and nothing had looked.
    # Generated images (tiles, cards) must carry provenance; every image a
    # media host serves -- authored ones included, like og-banner.jpg --
    # must carry the org branding. The shared tree is checked once.
    generated = re.compile(r"(^|/)(tile\.png|og\.jpg|[^/]+\.og\.jpg)$")
    imgs = sorted(set(list(repo_root.glob("media/*/dist/**/*.png")) + list(repo_root.glob("media/*/dist/**/*.jpg"))
                      + list(repo_root.glob("media/shared/*.jpg")) + list(repo_root.glob("media/shared/*.png"))
                      + [repo_root / "profiles" / s_ / "dist" / "resume.og.jpg" for s_ in served]))
    for img in imgs:
        if not img.is_file():
            continue
        # -T prints "-" for an absent tag, so the columns never shift (-s3 drops it)
        r = subprocess.run(["exiftool", "-T", "-XMP-dc:Description", "-XMP-dc:Publisher", str(img)], capture_output=True, text=True)
        cols = (r.stdout.strip().split("\t") + ["-", "-"])[:2]
        desc, publisher = [("" if c == "-" else c) for c in cols]
        missing = []
        if generated.search(str(img)) and not desc.startswith("provenance:"):
            missing.append("provenance")
        if not publisher:
            missing.append("branding")
        if missing:
            print(f"🔴 CRITICAL audit: {img.relative_to(repo_root)} lacks {' and '.join(missing)} metadata"); worst = 2

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
        # Blog hosts are deprecated (operator, 2026-09-11: "blog is deprecated ...
        # should redirect to media, and will be removed in future"). Only posts
        # ever lived there, so only posts have old blog URLs to keep landing; a
        # thesis was born on the media host and has none.
        if post.get("kind", "post") != "post":
            continue
        oper = post["path"].split("/")[1]
        prefix, media = prefix_of.get(oper, (None, None))
        if not media:
            continue
        names = {post["path"]} | former.get(post["path"], set())
        target = f"https://{media.replace('.tcos.us', suffix)}/{'blog' if post.get('kind', 'post') == 'post' else post['kind']}/{post['slug']}/"
        for name in sorted(names):
            for ext in (".md", ".html"):
                url = f"https://{prefix}.blog{suffix}/" + name[:-3] + ext
                code, final = code_and_final(url); n += 1
                # The media Workers serve assets with clean URLs: /posts/x.html
                # answers 307 -> /posts/x, so the final URL a reader lands on
                # is the target without its .html. Both forms are the target.
                landed = final.rstrip("/") + "/"
                if code != 200 or landed != target:
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


# ---- kit: a channel's brand images, from the same card ---------------------
#
# Operator, 2026-09-11, on the YouTube channel page: "need watermark with full
# exif and og and made with mt-logo in the mix ... also need fresh images for
# this ... I need to establish my YaW! brand". So `kit` renders a watermark,
# an avatar and a banner from spec.kit on the item's card, checks each against
# the platform's published limits, and stamps every file the way every
# published file here is stamped: provenance, agent signature, branding, an
# embedded GPG signature and a detached .asc. `build` then makes the page and
# its og card from the same card, like any gallery.
#
# MT-logo-render draws the round badges and the Morse dots. Today it renders
# only filled discs -- hex, stripes and labels are open issues #22 and #25 in
# that repo -- so the lettering is drawn here with Pillow.
LOGO_RENDER = Path(os.environ.get("MT_LOGO_RENDER", Path.home() / "git/MT-logo-render/target/release/logo-render"))
KIT_FONTS = {
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "serif": "/usr/share/fonts/opentype/urw-base35/C059-Bold.otf",
    "narrow": "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf",
    "sans": "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf",
    "italic": "/usr/share/fonts/opentype/urw-base35/C059-BdIta.otf",
}
# YouTube Studio's own wording, 2026-09-11: watermark "150 x 150 pixels is
# recommended ... 1MB or less"; banner "at least 2048 x 1152 pixels and 6MB or
# less"; picture "at least 98 x 98 pixels and 4MB or less". The banner's safe
# area, visible on every device, is the centered 1546 x 423.
KIT_SLOTS = {
    "watermark": {"size": (150, 150), "rule": "exact", "max_bytes": 1024 * 1024},
    "avatar": {"size": (800, 800), "rule": "min", "min": (98, 98), "max_bytes": 4 * 1024 * 1024},
    "banner": {"size": (2560, 1440), "rule": "min", "min": (2048, 1152), "max_bytes": 6 * 1024 * 1024},
}
MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
         "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
         "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
         "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----."}


def _rgb(hexstr, a=255):
    h = hexstr.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _font(key, size):
    from PIL import ImageFont
    return ImageFont.truetype(KIT_FONTS[key], max(8, int(size)))


class _Discs:
    """Round sprites from MT-logo-render, cached per (color, diameter)."""

    def __init__(self, workdir):
        self.root = Path(workdir); self.used = {}
        commit = subprocess.run(["git", "-C", str(LOGO_RENDER.parent.parent.parent), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        self.commit = commit or "unknown"

    def disc(self, color, diameter):
        diameter = int(diameter)
        # the renderer's disc is 80% of its canvas, so ask for a canvas that makes the wanted diameter
        canvas = max(16, min(4096, round(diameter / 0.8)))
        recipe = {"shape": "circle", "size": f"{canvas}x{canvas}", "base_color": color, "fill": "solid"}
        r = subprocess.run([str(LOGO_RENDER), "--asset-root", str(self.root), "render", "--targets", "png", json.dumps(recipe)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"media-item kit: MT-logo-render failed for {recipe}: {r.stderr.strip()[:300]}")
        out = json.loads(r.stdout[r.stdout.index("{"):])["outputs"]["png"]
        self.used[out["path"]] = {"sha256": out["sha256"], "recipe": recipe}
        with Image.open(out["path"]) as im:
            im = im.convert("RGBA")
        box = im.getbbox() or (0, 0, canvas, canvas)
        sprite = im.crop(box)
        return sprite.resize((diameter, diameter), Image.LANCZOS)


def _ransom(word, height, pal):
    """The wordmark as cut-out letters: each glyph its own block, face and tilt."""
    from PIL import ImageDraw
    styles = [("mono", pal["ground"], pal["hazard"], -6, 0.00),
              ("serif", pal["ink"], pal["ground"], 4, 0.05),
              ("narrow", pal["ground"], pal["accent"], -3, -0.03),
              ("sans", pal["hazard"], pal["ground"], 7, 0.04)]
    pieces = []
    for i, ch in enumerate(word):
        face, fg, bg, tilt, drop = styles[i % len(styles)]
        f = _font(face, height * 0.8)
        l, t, r, b = f.getbbox(ch)
        pad = height * 0.14
        w, h = int(r - l + 2 * pad), int(height)
        block = Image.new("RGBA", (w, h), _rgb(bg))
        d = ImageDraw.Draw(block)
        if bg == pal["ground"]:
            d.rectangle([0, 0, w - 1, h - 1], outline=_rgb(pal["ink"]), width=max(2, int(height * 0.035)))
        d.text(((w - (r - l)) / 2 - l, (h - (b - t)) / 2 - t), ch, font=f, fill=_rgb(fg))
        pieces.append((block.rotate(tilt, resample=Image.BICUBIC, expand=True), int(drop * height)))
    overlap = int(height * 0.05)
    total_w = sum(p.width for p, _ in pieces) - overlap * (len(pieces) - 1)
    total_h = max(p.height + abs(dy) for p, dy in pieces) + int(height * 0.1)
    out = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    x = 0
    for p, dy in pieces:
        out.alpha_composite(p, (x, (total_h - p.height) // 2 + dy))
        x += p.width - overlap
    return out.crop(out.getbbox())


def _fit(img, max_w, max_h):
    s = min(max_w / img.width, max_h / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def _kit_watermark(k, discs):
    from PIL import ImageDraw
    pal = k["palette"]; W = 150
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.alpha_composite(discs.disc(pal["ground"], W), (0, 0))
    ImageDraw.Draw(out).ellipse([2, 2, W - 3, W - 3], outline=_rgb(pal["accent"]), width=5)
    mark = _fit(_ransom(k["wordmark"], 120, pal), 112, 70)
    out.alpha_composite(mark, ((W - mark.width) // 2, (W - mark.height) // 2))
    return out


def _kit_avatar(k, discs):
    from PIL import ImageDraw
    pal = k["palette"]; W = 800
    out = Image.new("RGBA", (W, W), _rgb(pal["ground"]))
    out.alpha_composite(discs.disc(pal["accent"], W), (0, 0))
    inner = 716
    out.alpha_composite(discs.disc(pal["ground"], inner), ((W - inner) // 2, (W - inner) // 2))
    mark = _fit(_ransom(k["wordmark"], 360, pal), 560, 300)
    out.alpha_composite(mark, ((W - mark.width) // 2, 400 - mark.height // 2 - 40))
    d = ImageDraw.Draw(out)
    line = k.get("avatar_line", "")
    if line:
        f = _font("mono", 34); l, t, r, b = f.getbbox(line)
        d.text(((W - (r - l)) // 2 - l, 400 + 150), line, font=f, fill=_rgb(pal["dim"]))
    return out.convert("RGB")


def _morse_row(img, discs, text, y, color, unit):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    seq = []
    for wi, word in enumerate(text.split()):
        if wi:
            seq.append(("gap", 7))
        for li, ch in enumerate(word):
            if li:
                seq.append(("gap", 3))
            for ei, el in enumerate(MORSE[ch]):
                if ei:
                    seq.append(("gap", 1))
                seq.append(("dot", 1) if el == "." else ("dash", 3))
    width = sum(n for _, n in seq) * unit
    x = (img.width - width) // 2
    dot = discs.disc(color, unit)
    for kind, n in seq:
        if kind == "dot":
            img.alpha_composite(dot, (x, y))
        elif kind == "dash":
            d.rounded_rectangle([x, y, x + 3 * unit - 1, y + unit - 1], radius=unit // 2, fill=_rgb(color))
        x += n * unit


def _kit_banner(k, discs):
    from PIL import ImageDraw
    pal = k["palette"]; W, H = 2560, 1440
    SX, SY, SW, SH = (W - 1546) // 2, (H - 423) // 2, 1546, 423
    img = Image.new("RGBA", (W, H), _rgb(pal["ground"]))
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = ImageDraw.Draw(over)
    for y in range(0, H, 6):
        o.line([(0, y), (W, y)], fill=_rgb(pal["ink"], 7))
    step = 30
    for gy in range(step // 2, H, step):
        for gx in range(step // 2, W, step):
            inside = SX - 40 < gx < SX + SW + 40 and SY - 40 < gy < SY + SH + 40
            if inside:
                continue
            fx = gx / W
            # dots grow toward both outer edges, the same on each side: teal left, hazard right
            edge = abs(fx - 0.5) * 2
            r = 8.5 * edge ** 1.6 * (0.6 + 0.4 * abs(gy - H / 2) / (H / 2))
            if r >= 1.5:
                col = pal["accent"] if fx < 0.5 else pal["hazard"]
                o.ellipse([gx - r, gy - r, gx + r, gy + r], fill=_rgb(col, 55))
    img.alpha_composite(over)
    _morse_row(img, discs, k.get("morse", "YAW 73"), SY - 90, pal["accent"], 22)
    # the second row carries the professional half; operator, 2026-09-11: "the morse code for tcos is ... this might be a cool use of mt-logo"
    _morse_row(img, discs, k.get("morse_bottom", k.get("morse", "YAW 73")), SY + SH + 68, pal["hazard"], 22)
    d = ImageDraw.Draw(img)
    d.text((SX + 40, SY + 12), k["prompt"], font=_font("mono", 36), fill=_rgb(pal["accent"]))
    mark = _fit(_ransom(k["wordmark"], 300, pal), 760, 262)
    img.alpha_composite(mark, (SX + 40, SY + 76))
    rx = SX + 40 + mark.width + 90
    d.text((rx, SY + 84), k["motto"], font=_font("italic", 70), fill=_rgb(pal["ink"]))
    f73 = _font("narrow", 150)
    d.text((rx, SY + 170), "73", font=f73, fill=_rgb(pal["hazard"]))
    l, t, r, b = f73.getbbox("73")
    d.text((rx + (r - l) + 30, SY + 238), k.get("signoff", "de YaW!"), font=_font("mono", 56), fill=_rgb(pal["ink"]))
    tape = Image.new("RGBA", (SW - 60, 76), _rgb(pal["hazard"]))
    ft = _font("narrow", 56); td = ImageDraw.Draw(tape)
    l, t, r, b = ft.getbbox(k["tagline"])
    td.text(((tape.width - (r - l)) // 2 - l, (tape.height - (b - t)) // 2 - t), k["tagline"], font=ft, fill=_rgb(pal["ground"]))
    tape = tape.rotate(-1.2, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(tape, (SX + 30, SY + SH - tape.height - 2))
    foot = k.get("footer", "")
    if foot:
        ff = _font("mono", 30); l, t, r, b = ff.getbbox(foot)
        d.text((W - 60 - (r - l), H - 70), foot, font=ff, fill=_rgb(pal["dim"]))
    return img.convert("RGB")


def kit(item_dir):
    item_dir = Path(item_dir).resolve()
    card_path = item_dir / "item.card.v1.yaml"
    card = yaml.safe_load(card_path.read_text()); spec = card["spec"]; k = spec.get("kit")
    if not k:
        sys.exit(f"media-item kit: {card_path} has no spec.kit")
    if not LOGO_RENDER.is_file():
        sys.exit(f"media-item kit: MT-logo-render not found at {LOGO_RENDER} (set MT_LOGO_RENDER)")
    import tempfile
    work = Path(tempfile.mkdtemp(prefix="media-kit-"))
    discs = _Discs(work)
    makers = {"watermark": _kit_watermark, "avatar": _kit_avatar, "banner": _kit_banner}
    env = dict(os.environ)
    branding = k.get("branding") and os.path.expanduser(k["branding"])
    if branding:
        if not Path(branding).is_file():
            sys.exit(f"media-item kit: branding card {branding} not found -- a personal kit must not fall back to the org's card")
        env["HEE_BRANDING"] = branding
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=item_dir).stdout.strip() or "unknown"
    worst = 0
    for slot, name in k["outputs"].items():
        discs.used = {}
        img = makers[slot](k, discs)
        out = item_dir / name
        for stale in (out, Path(str(out) + ".asc")):
            if stale.exists():
                stale.unlink()
        img.save(out, "PNG", optimize=True)
        lim = KIT_SLOTS[slot]
        w, h = img.size; size = out.stat().st_size
        want = lim["size"] if lim["rule"] == "exact" else lim["min"]
        ok_size = (w, h) == want if lim["rule"] == "exact" else (w >= want[0] and h >= want[1])
        ok = ok_size and size <= lim["max_bytes"]
        worst = max(worst, 0 if ok else 2)
        print(f"{'🟢 OK' if ok else '🔴 CRITICAL'}  kit {slot}: {name} {w}x{h}, {size / 1024:.0f} KB "
              f"({lim['rule']} {want[0]}x{want[1]}, at most {lim['max_bytes'] // 1024} KB)")
        main_src = max(discs.used, key=lambda p: discs.used[p]["recipe"]["size"]) if discs.used else ""
        recipes = sorted({json.dumps(v["recipe"], sort_keys=True).replace(";", ",") for v in discs.used.values()})
        run = lambda *a: subprocess.run([str(HEE_EXIF), *a], check=True, capture_output=True, text=True, env=env)
        run("provenance", str(out), "--tool", "resume/media-item kit", "--commit", commit, "--job", str(card_path),
            *(["--source", main_src] if main_src else []),
            "--kv", f"slot={slot} {w}x{h}", "--kv", f"mt_logo_render={discs.commit}",
            "--kv", f"mt_discs={len(discs.used)}: " + " | ".join(recipes),
            "--kv", f"owner={spec.get('owner', '')}", "--kv", f"page=https://{spec['host']}/gallery/{item_dir.name}/")
        run("sign", str(out))
        run("brand", str(out), "--artist", spec.get("owner", ""), "--force")
        run("embed-sig", str(out))
        run("gpg-sign", str(out))
        v = subprocess.run([str(HEE_EXIF), "verify", str(out)], capture_output=True, text=True, env=env)
        worst = max(worst, 0 if v.returncode == 0 else 2)
        print(f"{'🟢 OK' if v.returncode == 0 else '🔴 CRITICAL'}  kit {slot}: provenance, signature, branding, embedded and detached GPG -- verify exit {v.returncode}")
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
    if len(argv) >= 2 and argv[0] == "kit":
        return kit(argv[1])
    if len(argv) < 2 or argv[0] != "build":
        print(__doc__ or "usage: media-item.py build <item-dir> [--no-network] | root <media-dist> [--init --name N --host H] | audit [--prod]"); return 2
    return build(argv[1], network="--no-network" not in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
