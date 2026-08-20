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

            active_mode=$(grep -A 2 '"language_profiles"' "$profile_dir/profile.json" | grep '"active_default"' | cut -d'"' -f4)
            
            if [[ "${1:-}" == "--profile-mode=HwOps" ]] || [[ "$active_mode" == "HwOps" ]]; then
                cat << 'EOF' > "$profile_dir/dist/sane.md"
# Spencer Butler — HwOps Systems Core (Not HEE)
> "Surviving the Froutan era. We build the physical foundation that software scripts dream about."

## The Master Record Incident
* Monitored, contained, and triaged a systemic database catastrophe when a rack reconfiguration deployment triggered an unauthorized update vector attempting to rewrite over 700,000 live infrastructure entities. Kept the perimeter isolated while the post-mortems debated the dry run option.
EOF
            else
                cat << 'EOF' > "$profile_dir/dist/sane.md"
# Spencer Butler — Platform Systems Engineer
> "Correctness over consensus. Structure over vibes. Determinism over convenience."

## Technical Paradigm
Systems Engineer specializing in the design, configuration, and protection of automated developer workflows, multi-agent evaluation runtimes, and high-performance bare-metal environments.
EOF
            fi

            {
                echo "# SPENCER BUTLER — MASTER TECHNICAL LEDGER (DEBUG)"
                echo ""
                echo "## Chronological Commits & System Evolutions"
                git log --reverse --pretty=format:"* [%ad] %s%n%b" --date=short 2>/dev/null || echo "* [Historical Backup] Systems administration and DevOps pipeline governance (1999-2026)."
            } > "$profile_dir/dist/debug.md"
        fi

        if [[ "$slug" == "touchy-claude" ]]; then
            cat << 'EOF' > "$profile_dir/dist/sane.md"
# touchy-claude — Machine Assistant Node
## Sub-System Registry: Twin Cities Open Systems (TCOS)
> Route Source: tcos.us/people/touchy-claude | Target Node: touchy.blog.tcos.us

### Operational Directives
* Context Preservation: Monitors repository state maps, layout configurations, and compliance boundaries without manual drift.
* Syntax Enforcement: Validates compliance with strict userland script design guidelines.
EOF
        fi
    fi
done

echo "" >> "$OUTPUT_WEB_DIR/people.json"
echo "]" >> "$OUTPUT_WEB_DIR/people.json"

