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
            fi
            sed -e 's/^#*[[:space:]]//g' "$profile_dir/dist/resume.md" > "$profile_dir/dist/resume.txt"
        else
            echo "  [i] no real resume source for '$slug' yet -- skipping resume.{md,html,pdf,txt}" >&2
        fi
    fi
done

echo "" >> "$OUTPUT_WEB_DIR/people.json"
echo "]" >> "$OUTPUT_WEB_DIR/people.json"
