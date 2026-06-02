# small-power Skill v1.0

Socket outlet layouts for general-purpose power circuits. Produces structured IR with circuit topology, per-room socket placement, RCD posture, and circuit-to-room cross-references.

## v2.0.0 highlights (Wave 2 first deliverable, 2026-06-02)

D4 closes the within-skill-depth program for small-power. Promoted from
beta to **production**. Bump 1.2.0 → 2.0.0 is bump-as-signaling, not
bump-as-breakage (see manifest `_v2_breaking_change_note`).

### What's new in v2.0
- NEW top-level optional `building_diversity` IR field mirroring verified
  diversity-factors.json office/industrial/healthcare profiles (BLD-01..05)
- NEW 4 Part-7 worked examples: pool (§702.415.1) + medical Group 2 (§710 IT)
  + EV charging (§722) + sauna (§703.411.3.3)
- NEW 4 topology depth rules: TOP-09 ring continuity + TOP-10 floor-area
  cross-check + TOP-11 OCPD-topology coordination + TOP-12 AMD 2 FCU spur
  (existing files had more rules than plan expected; rules ended up as
  TOP-09..12 not TOP-06..09 — same engineering content)
- NEW EV-charge demand coordination: RCD Type A/B selection per
  Reg 722.531.3.101 + no-diversity per IET CoP for EV (4th Ed) +
  dedicated-circuit rule + BS EN 61851-1 + BS EN 62196
- NEW INV-13..INV-19 (7 new INVs); catalogue now 19 total
- NEW D-8 / D-9 / D-10 reviewer judgment checks
- INV-19 verifies cable-sizing cascade integration with building_diversity

### Verified citation discipline (per spec §2.3)
All citations trace to verified standards files. Banned at the spec stage:
§526.2 + §433.2 (not transcribed in verified BS 7671 file — IET OSG §8.4.4
is the anchor) + OZEV CoP (correct name is IET CoP for EV Charging
Equipment Installation) + 3rd Edition EV CoP (correct is 4th Ed).

## What this skill produces

For a given parent DB + jurisdiction + room briefs, the skill emits:

- **Per-circuit data:** circuit_id, topology (ring/radial/dedicated_radial), OCPD selection, cable specification, RCD posture, diversified max load, rooms_covered array
- **Per-room data:** dimensions, special_location flag, sockets[] array with each socket's circuit_id reference + mount + height
- **Compliance summary:** non_compliance_flags + assumptions + WI3 deferral flags
- **Rationale block:** 8-section narrative + chat_summary ≤500 chars

## Architecture: leaf skill v1.0

- `consumes_intents: []` — no cross-skill consumption in v1.0 (matches lighting-layout v1.3 production pattern)
- `produces_intent: "small-power"` — future db-layout v1.x consumes this for general_power circuits
- Engineer declares earthing system_type, supply Ze, PSCC, parent DB context as user inputs
- v1.1+ migrates to consume earthing + fault-level intents per SLD v1.3→v1.4 precedent

## Jurisdictions supported

- **GB** — BS 7671:2018+A2:2022 (ring final circuits + Part 7-701 bathroom zones + IET OSG diversity)
- **KE** — KS 1700:2018 §313 routes to BS 7671 (radial typically preferred at commercial scale; ring permitted)
- **INT** — IEC 60364-4-41 / -5-53 / -7-701 (Schuko sockets; Type B RCD for IT loads per §531.3.3)
- **US** — NEC 2023 Article 210 (210.52 spacing, 210.8 GFCI, 210.12 AFCI, 406.12 tamper-resistant)

## Examples

| Folder | Scenario |
|---|---|
| `examples/uk-3bed-dwelling/` | UK 3-bedroom dwelling, 2 rings + dedicated cooker/immersion/shaver radials + Part 7-701 bathroom + outdoor |
| `examples/ke-nairobi-small-office/` | KE 80m² commercial office, 4 radials + BS 1363 + KS 1700 §313 + KPLC TN-S 415V |
| `examples/intl-open-plan-floor/` | INT 350m² commercial open-plan, 8 radials including UPS-fed Type B RCD for server room + ISO 19650 + IEC 60364-7-701 toilets + outdoor |
| `examples/us-residential-dwelling/` | US 160m² residential dwelling, 8 circuits + NEC 210.52 + 210.8 GFCI + 210.12 AFCI + duplex receptacles |

## Out of scope (v1.0)

- **Socket x/y coordinates / physical placement on a drawing.** small-power is a **topology + cross-reference** skill, not a placement skill. Each `room.sockets[]` entry carries `circuit_id`, `mount`, `height_mm`, `type`, and a logical position descriptor — but NOT explicit floor-plan x/y. Placement coordinates belong to a future **socket-placement** drawing skill (currently unscoped — closest analogue is `electrical/lighting-layout` for luminaires). A downstream drawing/rendering layer consumes the small-power intent + a room/floor-plan IR + applies BS 7671 §553 spacing rules to derive coordinates. *Flagged by Reviewer 1's re-test as "small-power invents 100% of socket positions" — clarification: it doesn't carry positions at all; positions are explicitly deferred.*
- EV charging (BS 7671 Part 7-722 / NEC 625) — future ev-charging skill (stub at `electrical/ev-charging/` per Sprint D follow-up)
- Cable containment / routing — future cable-containment skill (stub at `electrical/cable-containment/`)
- Multi-skill intent consumption — deferred to v1.1+
- 3-phase socket outlets (BS EN 60309 CEEform) — future revision

See `CHANGELOG.md` for version history and `docs/supported-standards.md` for the full standards reference.
