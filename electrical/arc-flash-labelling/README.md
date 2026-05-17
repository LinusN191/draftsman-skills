# `arc-flash-labelling` — Printable Arc-Flash Label Generation

**Status:** `stub` — folder placeholder, full skill build queued

**What this skill will do (when built):**

Consume the `arc-flash` intent (produced by `electrical/arc-flash`) and render printable arc-flash warning labels per ANSI Z535.4 (sign formatting standard) + NFPA 70E §130.5(H) (required label content).

Per equipment node in the intent, produce:
- A printable label (PDF / SVG) with:
  - "DANGER" header (Cat 3-4 + restricted) or "WARNING" header (Cat 1-2)
  - Standardised ANSI Z535.4 symbol + colour scheme
  - Equipment ID, nominal voltage, date of analysis
  - Incident energy at working distance (cal/cm²)
  - Arc-flash boundary distance
  - Limited + Restricted shock-approach boundaries
  - Required PPE category + clothing description from NFPA 70E Table 130.7(C)(16)
  - Engineering company name + qualified-person signature block

Plus a project-wide label index (PDF) with QR-coded references to electronic copies.

## Cross-skill contract

| Direction | Intent | Source |
|---|---|---|
| Consumes | `arc-flash` | `electrical/arc-flash/` (when shipped) |
| Produces | none (terminal output is the printable label) | — |

## Standards consumed

- `shared/standards/electrical/ANSI-Z535-4/` (label format + colour + symbol spec — currently stub)
- `shared/standards/electrical/NFPA70E/section-130-5-arc-flash-risk-assessment.json` (required content)
- `shared/standards/electrical/NFPA70E/table-130-5-H-label-requirements.json` (where labels are mandatory)
- `shared/standards/electrical/NFPA70E/table-130-7-C-16-ppe-required-items.json` (clothing description per category)

## Why a separate skill from `arc-flash`

| Concern | `electrical/arc-flash` | `electrical/arc-flash-labelling` |
|---|---|---|
| Domain | Engineering analysis | Document production |
| Output | JSON IR + intent | PDF / SVG / printable file |
| Updates when | IEEE 1584 / NFPA 70E revise (rare) | Company branding, label format changes |
| Audience | Safety engineers, system designers | HSE officers, electricians on-site |

## Sprint priority

Queued for the next-next sprint (after this one ships + clause_ref retrofit micro-sprint).

## Build estimate (when promoted from stub)

- ~25-30 files (smaller than arc-flash skill — mostly templates + format rules)
- 1 new standards layer: `shared/standards/electrical/ANSI-Z535-4/` (warning sign format spec — currently stub)
- ~3 evals + 3 worked examples (UK BS-style label / INT IEC-style / US ANSI Z535-style)
- ~3 days of focused work

See repo root `shared/standards/electrical/ROADMAP.md` for the broader sprint sequence.
