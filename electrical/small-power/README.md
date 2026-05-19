# small-power Skill v1.0

Socket outlet layouts for general-purpose power circuits. Produces structured IR with circuit topology, per-room socket placement, RCD posture, and circuit-to-room cross-references.

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

- EV charging (BS 7671 Part 7-722 / NEC 625) — future ev-charging skill
- Cable containment / routing — future cable-containment skill
- Multi-skill intent consumption — deferred to v1.1+
- 3-phase socket outlets (BS EN 60309 CEEform) — future revision

See `CHANGELOG.md` for version history and `docs/supported-standards.md` for the full standards reference.
