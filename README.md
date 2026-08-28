# resume

A real, live mono-repo: one person's profile per directory, each one
driving that person's own `<person>.blog.tcos.us` (and, for people who
have one, `<person>.media.tcos.us`) presence automatically. Built and
maintained by dogfooding it on my own resume -- this isn't a demo repo,
it's the real thing [spencer.blog.tcos.us](https://spencer.blog.tcos.us/) runs from.

<spencer@tcos.us>

---

## How it works

Add a person, get a real presence -- no per-person wiring:

```
profiles/<slug>/profile.json   -- the only file a new person needs
        ├── public_routing     -- their real <slug>.blog.tcos.us
        ├── media_routing      -- optional: their real <slug>.media.tcos.us
        └── language_profiles  -- resume content, multiple real voices
```

`convert.sh` reads every real `profiles/*/profile.json` and generates
`people.json` -- the one real source of truth every page on this site
reads from at request time. Add `media_routing` to a profile and the
"Media →" link and the `media.tcos.us` hub both pick it up on the next
deploy. Nothing else to touch, no second list to remember to update --
that duplication was a real bug here once (`spencer.media.tcos.us`
hardcoded in two separate files, already drifting), fixed by making
this the one real place it's declared.

Two real category-level hubs list every operator with one --
`blog.tcos.us` and `media.tcos.us`, live on the lab clone
([blog.lab.tcos.us](https://blog.lab.tcos.us/) /
[media.lab.tcos.us](https://media.lab.tcos.us/)) as of 2026-08-28, not
yet promoted to prod. `<person>.blog.tcos.us` / `<person>.media.tcos.us`
is that person's own instance -- this repo currently hosts real
profiles for `spencer`, `touchy-claude`, and `claude-intern-j2`.

## My own resume, dogfooded

- **Live, generated**: [spencer.blog.tcos.us/resume-spencer.html](https://spencer.blog.tcos.us/resume-spencer.html) -- rendered from `profiles/spencer/profile.json` by the same real pipeline every profile in this repo goes through
- **Live, full stream**: [spencer.blog.tcos.us](https://spencer.blog.tcos.us/) -- blog posts, media links, the works
- **Old-school markdown**: [spencer.blog.tcos.us/SpencerButler.md](https://spencer.blog.tcos.us/SpencerButler.md) -- the plain-text version this whole system grew out of, kept around on purpose rather than deleted once the generated version existed. (Also browsable in-repo: [SpencerButler.md](SpencerButler.md).)

---

## Global Alignment & Invariants

This codebase adheres to the core engineering principles, scripting
standards, and structural invariants mandated by Twin Cities Open
Systems. All userland scripts (`.sh`, `.py`, `.awk`) enforce the
portable shebang syntax and a mandatory 4-line metadata header block.
For the full architecture manifest, see the [TCOS Command Center Config](../.github).

---

## SpencerButler.md, in full

# Spencer Butler Resume

<spencer@tcos.us>

### Summary

Infrastructure Engineer with 20+ years of experience operating and deploying large-scale systems across datacenter and production environments. Proven track record in hardware bring-up, failure analysis, and infrastructure deployment, including early datacenter expansion at Google and rapid deployment environments at Groq. Known for identifying complex system issues early and driving them to resolution across hardware and software layers.

### Core Skills

- Datacenter Operations & Deployment
- Infrastructure Bring-up & Hardware Validation
- Linux / Unix Systems (FreeBSD, OpenBSD, Linux)
- Automation
- Monitoring & Observability
- Failure Analysis & Debugging
- Quality Assurance
- Tool Development

### Professional Experience

#### Groq — Infrastructure Engineer (Systems)

July 2024 – April 2025

- Supported rapid deployment of datacenter infrastructure in a high-growth AI environment
- Worked closely with local AI techs to deliver clusters for QA and deployment
- Worked closely with the Infrastructure team to bring clusters online at speed while maintaining operational stability
- Contributed to hardware deployment, system validation, and early-stage infrastructure operations
- SME for Groq LPU deployment and failure analysis in the Data Center

#### Honeycomb Internet Services — Unix Systems Administrator / DevOps

June 2017 – November 2023

- Designed and implemented monitoring systems across server and network infrastructure using Check_MK (Nagios) and LibreNMS
- Developed Puppet-based automation for deploying and configuring monitoring agents across heterogeneous systems
- Built internal tools and APIs (Flask, Python) to support infrastructure visibility and operational workflows
- Wrote custom monitoring plugins for Linux, OpenBSD, and FreeBSD environments
- Diagnosed and resolved complex system and application issues across production environments
- Developed and built custom FreeBSD image, with Puppet backend, for MN Snow Plows

#### Reflected Networks — Linux Systems Administrator

July 2010 – September 2015

- Maintained high-availability infrastructure supporting critical customer-facing services
- Deployed and managed web and application stack (HAProxy, Nginx, Apache, MySQL)
- Supported high-traffic CDN origin systems using Lighttpd
- Collaborated with distributed teams to ensure reliability and uptime across production systems

#### Google — Data Center Technician / Infrastructure Operations

October 2006 – September 2009

- Played a key role in turning up Google's Iowa datacenter, including infrastructure deployment and team leadership
- Worked directly with Platforms Development teams to test and validate new server hardware
- Identified hardware and deployment issues during early platform rollouts, improving system reliability
- Produced extensive operational documentation supporting large-scale infrastructure deployment

#### Twin Cities Open Systems — Infrastructure Consultant (self employ)

August 2001 – Current

- Infrastructure consulting, custom systems, and software solutions across diverse environments
- Linux-based systems, automation workflows, and monitoring solutions
- Currently building a doctrine-first, multi-agent execution framework (HEE) and org-wide governance/automation fleet, including API-driven Proxmox lab infrastructure and 0-token operational tooling
