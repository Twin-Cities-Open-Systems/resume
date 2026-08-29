#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# convert.sh
# Manages the resume MonoRepo

set -euo pipefail

if [[ ! -d "profiles" ]]; then
    echo "[-] Execution Error: Run this tool from the resume repository root." >&2
    exit 1
fi

declare -A ASSIGNED_SUBDOMAINS
OUTPUT_WEB_DIR="dist"
mkdir -p "$OUTPUT_WEB_DIR"

# Real resume source per profile -- a factual document, never the
# language_profiles persona copy (that's a voice/tone variant for blog
# pages, not resume content). Real bug, Spencer direct (2026-08-26):
# the live resume-spencer page was showing "Systems Engineer
# specializing in... multi-agent evaluation runtimes" (the "professional"
# language-profile paradigm blurb) instead of his real, factual work
# history (Groq, Honeycomb, Reflected Networks, Google...). Fix:
# resume.md is built from a real per-profile source file when one
# exists; language-profile reintegration for resumes is deferred
# (Spencer: "remove the lang-profile stuff for now, we will put it
# back in later, issue that for backlog" -- see resume#<TBD>).
declare -A REAL_RESUME_SOURCES=(
    [spencer]="SpencerButler.md"
)

echo "[" > "$OUTPUT_WEB_DIR/people.json"
FIRST_ENTRY=true

for profile_dir in profiles/*; do
    if [[ -d "$profile_dir" && -f "$profile_dir/profile.json" ]]; then
        slug=$(grep -o '"roster_slug": "[^"]*' "$profile_dir/profile.json" | cut -d'"' -f4)
        type_raw=$(grep -o '"type": "[^"]*' "$profile_dir/profile.json" | head -n1 | cut -d'"' -f4)
        public_dns=$(grep -o '"public_routing": "[^"]*' "$profile_dir/profile.json" | cut -d'"' -f4)
        # Real "set it and forget it" fix (2026-08-28): media_dns used
        # to be a hand-maintained MEDIA_HOSTS list duplicated in both
        # index.html and media-hub.html -- real drift risk, explicitly
        # flagged in both files' own comments. Now reads the same real
        # per-profile source every other real routing field already
        # comes from; a new person with a media presence just adds
        # media_routing to their own profile.json, nothing else to
        # touch. Empty string (not omitted) when absent, so downstream
        # JS can check `if (media_dns)` without a missing-key branch.
        # Real bug, found 2026-08-28: grep -o finds zero matches (correctly)
        # for any profile with no media_routing field, exits 1, and under
        # this script's set -e that was fatal -- silently broke every real
        # build for any roster entry lacking a media presence, contradicting
        # this exact comment's own stated intent one line above. `|| true`
        # lets an empty match through as intended instead of aborting.
        media_dns=$( { grep -o '"media_routing": "[^"]*' "$profile_dir/profile.json" || true; } | cut -d'"' -f4)

        fuzzy_prefix=$(echo "$public_dns" | cut -d'.' -f1)

        if [[ -n "${ASSIGNED_SUBDOMAINS[$fuzzy_prefix]+x}" ]]; then
            echo "[!] CRITICAL CONFLICT IDENTIFIED: Subdomain prefix '$fuzzy_prefix' is already occupied by ${ASSIGNED_SUBDOMAINS[$fuzzy_prefix]}." >&2
            echo "[?] Enter manual disambiguation modifier string: " >&2
            read -r manual_override < /dev/tty
            fuzzy_prefix=$(echo "$manual_override" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')
            public_dns="$fuzzy_prefix.blog.tcos.us"
        fi

        ASSIGNED_SUBDOMAINS[$fuzzy_prefix]="$slug"
        mkdir -p "$profile_dir/dist"

        if [ "$FIRST_ENTRY" = true ]; then
            FIRST_ENTRY=false
        else
            echo "," >> "$OUTPUT_WEB_DIR/people.json"
        fi

        cat <<- EOF >> "$OUTPUT_WEB_DIR/people.json"
  {
    "slug": "$slug",
    "type": "$type_raw",
    "subdomain_prefix": "$fuzzy_prefix",
    "public_dns": "$public_dns",
    "media_dns": "$media_dns",
    "route_path": "people/$slug"
  }
EOF

        # Generic per-profile blog content, driven entirely by profile.json --
        # no per-slug special-casing. dist/sane.md and dist/resume.md default
        # to the "professional" payload specifically, NOT active_default --
        # the filename says why (spencer's real active_default is his own
        # unfiltered "spencer" mode, not something that belongs in a resume
        # or the "sane" fallback by default). --profile-mode=<X> overrides
        # for any profile that actually supports mode X (silently ignored
        # otherwise, falls back to professional, then active_default if a
        # profile somehow has neither).
        active_mode=$(grep -A 2 '"language_profiles"' "$profile_dir/profile.json" | grep '"active_default"' | cut -d'"' -f4)
        if grep -q '"professional":' "$profile_dir/profile.json"; then
            requested_mode="professional"
        else
            requested_mode="${active_mode}"
        fi
        for arg in "$@"; do
            case "$arg" in
                --profile-mode=*)
                    candidate="${arg#--profile-mode=}"
                    if grep -q "\"${candidate}\":" "$profile_dir/profile.json"; then
                        requested_mode="$candidate"
                    fi
                    ;;
            esac
        done

        entity=$(grep -o '"entity": "[^"]*' "$profile_dir/profile.json" | cut -d'"' -f4)
        payload_title=$(python3 -c "
import json
d = json.load(open('$profile_dir/profile.json'))
p = d.get('language_profiles', {}).get('payloads', {}).get('$requested_mode', {})
print(p.get('title', ''))
")
        payload_paradigm=$(python3 -c "
import json
d = json.load(open('$profile_dir/profile.json'))
p = d.get('language_profiles', {}).get('payloads', {}).get('$requested_mode', {})
print(p.get('paradigm', ''))
")

        cat > "$profile_dir/dist/sane.md" <<- SANEEOF
# ${payload_title}
> Route Source: tcos.us/people/${slug} | Target Node: ${public_dns}

## Profile
${payload_paradigm}
SANEEOF

        # Spencer-specific extras: real, personal achievement content and the
        # git-log ledger. Not generic -- these don't make sense for every
        # profile, kept as real spencer-only content, not a template.
        if [[ "$slug" == "spencer" ]]; then
            cat << 'EOF' > "$profile_dir/dist/filter-pass.md"
# SPENCER BUTLER
## High-Impact Systems Architecture & Platform Engineering
> Route Source: tcos.us/people/spencer | Target Node: spencer.blog.tcos.us

### CORE VALUES & SYSTEMIC METRICS
* Standardized and managed a 19-repository platform ecosystem via automated layouts.
* Protected baseline runtime environments via custom invariant-gated SAST static analysis layers.
* Optimized distributed processing architectures using deterministic systemd user timers.
EOF

            {
                echo "# SPENCER BUTLER — MASTER TECHNICAL LEDGER (DEBUG)"
                echo ""
                echo "## Chronological Commits & System Evolutions"
                git log --reverse --pretty=format:"* [%ad] %s%n%b" --date=short 2>/dev/null || echo "* [Historical Backup] Systems administration and DevOps pipeline governance (1999-2026)."
            } > "$profile_dir/dist/debug.md"
        fi

        # Real per-profile resume -- only generated when a real, factual
        # source document exists (REAL_RESUME_SOURCES above). No
        # fabricated fallback: a profile without a real resume yet
        # simply doesn't get one, rather than showing persona copy
        # dressed up as facts.
        if [[ -n "${REAL_RESUME_SOURCES[$slug]+x}" ]] && [[ -f "${REAL_RESUME_SOURCES[$slug]}" ]]; then
            cp "${REAL_RESUME_SOURCES[$slug]}" "$profile_dir/dist/resume.md"
            # Real gap, caught live (2026-08-28): the original source
            # file (SpencerButler.md) sat at the repo root, never
            # copied into dist/ -- README linked to it, but a real
            # visitor on the live site had no way to reach it, only
            # someone browsing the repo on GitHub did. Root-level copy,
            # same real reason resume.html gets one (this is what
            # `wrangler pages deploy dist` actually serves).
            cp "${REAL_RESUME_SOURCES[$slug]}" "$OUTPUT_WEB_DIR/${REAL_RESUME_SOURCES[$slug]}"

            if command -v pandoc >/dev/null 2>&1; then
                pandoc -s "$profile_dir/dist/resume.md" -t html5 \
                    --metadata pagetitle="${entity} Resume" \
                    -H resume-theme.html \
                    -o "$profile_dir/dist/resume.html" 2>/dev/null
                if command -v wkhtmltopdf >/dev/null 2>&1; then
                    pandoc -s "$profile_dir/dist/resume.md" \
                        --metadata pagetitle="${entity} Resume" \
                        --pdf-engine=wkhtmltopdf \
                        -o "$profile_dir/dist/resume.pdf" 2>/dev/null
                fi

                # Real bug, caught live (2026-08-26): this root-level copy
                # is what `wrangler pages deploy dist` actually serves at
                # /resume-<slug> -- PR#25 introduced it as a one-off manual
                # cp, never wired into convert.sh itself, so it silently
                # kept serving stale content through this exact fix.
                cp "$profile_dir/dist/resume.html" "$OUTPUT_WEB_DIR/resume-${slug}.html"
            fi
            sed -e 's/^#*[[:space:]]//g' "$profile_dir/dist/resume.md" > "$profile_dir/dist/resume.txt"
        else
            echo "  [i] no real resume source for '$slug' yet -- skipping resume.{md,html,pdf,txt}" >&2
        fi
    fi
done

echo "" >> "$OUTPUT_WEB_DIR/people.json"
echo "]" >> "$OUTPUT_WEB_DIR/people.json"

# Real bug, found 2026-08-28: blog_manifest.json was entirely
# hand-maintained -- nothing generated it, so profiles/spencer/blog/
# 004-callsign-hunt.md (written the same day, real content) silently
# never made it in and never rendered on the live site. Same drift-risk
# class as every other hand-duplicated list already fixed in this file
# (media_dns, people.json) -- scan the real .md files on disk instead of
# trusting a list to stay in sync with itself.
echo "[" > "$OUTPUT_WEB_DIR/blog_manifest.json"
FIRST_POST=true
for profile_dir in profiles/*; do
    [ -f "$profile_dir/profile.json" ] || continue
    slug=$(grep -o '"roster_slug": "[^"]*' "$profile_dir/profile.json" | cut -d'"' -f4)
    [ -d "$profile_dir/blog" ] || continue
    for post_file in "$profile_dir"/blog/*.md; do
        [ -f "$post_file" ] || continue
        post_slug=$(basename "$post_file" .md)
        title=$(sed -n '1s/^#*[[:space:]]*//p' "$post_file")
        # Real bug, found live building this exact fix: a post with no
        # "**Date:**" line on line 2 (002-cloudflare-wrangler-convergence.md
        # -- separately flagged 2026-08-28 as fabricated/unreviewed
        # content, see fleet-ops#332) makes grep -oE find zero matches,
        # exit 1, fatal under this script's set -e -- the same bug class
        # just fixed for media_dns, reproduced in this same commit's own
        # new code. `|| true` so one malformed post can't crash the
        # entire build for every real one.
        # Real fallback chain, all real data, never fabricated: not every
        # real post follows the "**Date:**" line-2 convention (found
        # live -- chat-mach-dude-kthxbai.md and others are just prose,
        # no metadata block at all). Try the content date first, then a
        # date embedded in the filename itself (real, common pattern:
        # "003-2026-08-24-lessons-learned.md"), then the file's own real
        # mtime -- never a fake placeholder like 1970-01-01.
        date=$( { sed -n '2p' "$post_file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || true; } | head -1)
        if [ -z "$date" ]; then
            date=$(basename "$post_file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1 || true)
        fi
        if [ -z "$date" ]; then
            date=$(date -u -r "$post_file" +%Y-%m-%d)
        fi
        [ "$FIRST_POST" = true ] || echo "," >> "$OUTPUT_WEB_DIR/blog_manifest.json"
        FIRST_POST=false
        # Real values passed via env vars, not interpolated into Python
        # source text -- a title containing a quote/apostrophe (real,
        # expected in real prose) would otherwise break the generated
        # source rather than just being real, safely-escaped JSON data.
        POST_SLUG="$post_slug" POST_DATE="$date" POST_TITLE="$title" \
        POST_PATH="profiles/$slug/blog/$(basename "$post_file")" \
        python3 -c "
import json, os
print(json.dumps({
    'slug': os.environ['POST_SLUG'],
    'date': os.environ['POST_DATE'],
    'title': os.environ['POST_TITLE'],
    'raw_fallback': '(see full post)',
    'path': os.environ['POST_PATH'],
}), end='')
" >> "$OUTPUT_WEB_DIR/blog_manifest.json"
    done
done
echo "" >> "$OUTPUT_WEB_DIR/blog_manifest.json"
echo "]" >> "$OUTPUT_WEB_DIR/blog_manifest.json"
