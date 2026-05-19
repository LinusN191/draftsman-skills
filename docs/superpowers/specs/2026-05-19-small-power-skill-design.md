# small-power skill v1.0 Design Spec

**Date:** 2026-05-19
**Skill target:** `electrical/small-power/` — NEW skill, v1.0.0 beta on first ship

**Sprint type:** Single-skill greenfield build. Leaf shape (no cross-skill intent consumption); v1.0 follows lighting-layout v1.3 pattern. Multi-skill consumption deferred to v1.1+ per SLD v1.3→v1.4 migration precedent.

**Origin:** 5th drawings skill on breadth-first sequence per [[build-strategy-breadth-first]] and "Close SLD chapter → small-power" priority direction. CLAUDE.md `## Build order > Drawings (8 skills) > small-power`. Closes the room-level electrical design layer alongside the production lighting-layout skill.

**Skill / runtime boundary preserved:** skill emits IR + intent; runtime renderer (separate project) consumes IR + drafting-standards lookups to produce drawings; calc tools (socket_diversity / ring_loop_zs / radial_zs) live in runtime project per [[runtime-project-boundary]].

---

## 1. Why this sprint

The drawings skill portfolio has 4 production skills (lighting-layout, sld, db-layout, earthing) + 4 pending (small-power, cable-containment, riser, schematic). small-power is the natural next skill — it's the canonical "socket outlet layout" deliverable on every electrical drawing package and pairs directly with lighting-layout (the gold-standard layout skill that's been in production since 2026-05-17).

Small-power v1.0 ships as a **leaf skill** (matches lighting-layout v1.3): produces small-power intent for future db-layout v1.x consumption; doesn't consume upstream intents in v1.0. v1.1+ migrates to multi-skill consumption (earthing system_type → RCD posture; fault-level PFC → breaker Icu verification) when the engineering case justifies the added complexity. This matches the proven SLD v1.3 → v1.4 incremental migration pattern.

## 2. Scope

### In scope (v1.0)

| Category | Count | Notes |
|---|---|---|
| Skill infrastructure | 4 | skill.manifest.json + inputs.json + README.md + CHANGELOG.md |
| Schemas | 2 | small-power-ir.schema.json + small-power-intent.schema.json |
| Prompts | 3 | generator.md (12-step) + validator.md (~10 INV) + reviewer.md (6 D-checks) |
| Examples | 20 | 4 examples × 5 files (input + output + intent-out + reasoning + sample-schedule) |
| Evals | 7-9 YAMLs | 5 WI5 categories + 2-4 skill-specific (ring-topology-by-jurisdiction; GFCI compliance; cross-room ring integrity; Zs deferral consistency) |
| Rules + constraints + validation | 6-8 YAMLs | Per-jurisdiction RCD + topology + special-locations rules |
| Ontology | 2-3 | socket-types.json (BS 1363 / Schuko / NEMA 5-15 / NEMA 5-20) + room-types reuse from shared/ontology |
| Symbols | 2-4 | socket symbols (single + double + RCD + FCU + outdoor + GFCI + tamper-resistant) in shared/symbols/electrical/sockets/ |
| Calc tool contracts | 3 | calc.socket_diversity + calc.ring_loop_zs + calc.radial_zs in shared/calculations/electrical/ |
| Standards layer additions | 3 | special-locations.json in shared/standards/electrical/{BS7671,NFPA70,IEC60364}/ |
| Bookkeeping | 2 | SKILLS_STATUS row + ARCHITECTURE.md "small-power skill (v1.0)" subsection |
| **Total** | **~67** | Comparable to SLD v1.5 (46) + lighting-layout v1.3 file shape |

### Out of scope (deferred)

- **EV charging** (BS 7671:2018+A2:2022 Part 7-722 / IEC 60364-7-722 / NEC 625) — future dedicated `ev-charging` skill
- **Cable containment / routing** — future `cable-containment` skill
- **Riser diagrams** across multiple parent DBs — future `riser` skill (small-power v1.0 stays within a single parent DB scope)
- **Multi-skill intent consumption** (earthing + fault-level) — deferred to small-power v1.1
- **3-phase socket outlets** (BS EN 60309 CEEform / industrial connectors) — future revision of socket-types.json ontology
- **Industrial process loads** (CNC machines, lathes, dedicated motor circuits) — handled by db-layout circuits[] directly with engineer-authored content
- **Lighting controls** — owned by lighting-layout skill

## 3. Architecture decisions

### 3.1 — Leaf skill (`consumes_intents: []`) — matches lighting-layout v1.3 pattern

v1.0 is a producer only. Inputs are user-provided (jurisdiction, room briefs, parent DB designation as string reference). Engineer declares earthing system_type + parent DB context + PFC values as part of `input.json` rather than consuming upstream intents.

**Rationale:** lighting-layout v1.3 ships in production with `consumes_intents: []`. db-layout already consumes lighting-layout intent. The same pattern works here. v1.1+ migrates to consume earthing + fault-level intents when the engineering case justifies the added complexity (matches SLD v1.3 → v1.4 migration precedent).

### 3.2 — Hybrid IR shape: `circuits[]` + `rooms[]` with cross-references

Primary structure is `circuits[]` (each with topology + ocpd + cable + RCD posture). Secondary structure is `rooms[]` (each with `sockets[]` referencing circuit_ids). Cross-room rings naturally supported.

```jsonc
{
  "circuits": [
    {
      "circuit_id": "C01",
      "designation": "Kitchen + utility ring final circuit",
      "topology": "ring",
      "ocpd":  { "rating_a": 32, "type": "RCBO", "curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "breaking_capacity_ka": 6 },
      "cable": { "csa_mm2_or_awg": "2.5mm² + 1.5mm² CPC", "cores": 3, "length_m_total": 38, "material": "copper", "insulation": "PVC_70" },
      "rcd_posture": "type_a_30ma_per_§411_3_3",
      "verified_zs_ohm": 1.43,
      "estimated_max_load_kw": 5.0,
      "diversified_max_load_a": 14.5,
      "rooms_covered": ["kitchen", "utility"]
    }
  ],
  "rooms": [
    {
      "room_id": "kitchen",
      "room_type": "kitchen_domestic",
      "dimensions_m": { "length": 4.5, "width": 3.5, "height": 2.4 },
      "special_location": null,
      "sockets": [
        { "id": "K-S01", "type": "BS1363_2gang_switched", "mount": "wall", "height_mm": 1100, "circuit_id": "C01", "fed_by_spur": false },
        { "id": "K-S02", "type": "BS1363_2gang_switched", "mount": "above_worktop", "height_mm": 1200, "circuit_id": "C01", "fed_by_spur": false },
        { "id": "K-S03", "type": "BS1363_FCU_unswitched", "mount": "wall", "height_mm": 1200, "circuit_id": "C01", "fed_by_spur": true, "spur_load_kw": 0.3, "spur_purpose": "extractor_fan" }
      ]
    }
  ]
}
```

### 3.3 — Topology enum (3 values)

| Value | When to use | Engineering anchor |
|---|---|---|
| `ring` | GB ring final circuit | BS 7671:2018+A2:2022 §433.1.5 + IET OSG §8.4.4 (ring conditions, ≤100 m² floor area, ≤2 spurs per leg) |
| `radial` | Standard radial | All jurisdictions; default for KE/INT/US; also a valid alternative in GB |
| `dedicated_radial` | Single-load circuit (cooker, immersion heater, washing machine) | BS 7671 §433.1.4 / NEC 210.23 dedicated branch circuits |

INV check: `ring` topology only valid where `jurisdiction in {"GB", "KE"}` (KE inherits BS 7671 via KS 1700 §313 routing). **Note:** ring is *permitted* in KE via routing, NOT *mandated*. Kenyan engineering practice favours radial circuits at commercial scale (KE example in §4.2 deliberately chooses radial — engineer judgment + KPLC convention). UK domestic practice (§4.1) defaults to ring per OSG §8.4 unless floor area >100 m² or installation pattern doesn't suit.

### 3.4 — Special locations enum (6 values)

| Value | Standard reference | RCD requirement |
|---|---|---|
| `null` | General location | Per jurisdictional default (typically 30mA Type A on sockets) |
| `bathroom_zone_1` | BS 7671 Part 7-701 §701.412.5 / IEC 60364-7-701 §701.512 | NO sockets permitted (except SELV shaver units) |
| `bathroom_zone_2` | BS 7671 Part 7-701 §701.512 | Shaver supply units only (BS EN 61558-2-5); RCD ≤30mA mandatory |
| `bathroom_zone_3` | BS 7671 Part 7-701 §701.512 (outside zones 0/1/2) | Sockets allowed with RCD ≤30mA Type A; min 0.6m from zone 1 |
| `outdoor` | BS 7671 §522.6.201 + IEC 60364-5-52 §522.6 + NEC 210.8(A)(3) | IP-rated socket + RCD ≤30mA Type A (BS) or GFCI (US) |
| `wet_area` | NEC 210.8 (US: laundry, kitchen, basement, garage) | GFCI required (US-specific) |

Maps to `special-locations.json` in shared/standards/electrical/{BS7671,NFPA70,IEC60364}/ (3 NEW small JSON files in Phase A of the sprint).

### 3.5 — RCD posture enum (3 values)

| Value | When |
|---|---|
| `type_a_30ma_per_§411_3_3` | Standard sockets ≤32A per BS 7671 §411.3.3 / IEC 60364-4-41 §411.3.3 |
| `type_b_30ma_per_§531_3_3` | IT-equipment circuits with DC leakage per IEC 60364-5-53 §531.3.3 (matches db-layout intl-dbcomms-data pattern) |
| `no_rcd_with_documented_§411_exception` | Engineer-declared exception with explicit BS 7671 §411.3.3 omitted-RCD justification (e.g., FELV circuit, supplementary RCD not required because feed-side already RCD-protected). Use sparingly; reasoning.md MUST cite the exception clause. |

### 3.6 — WI3 calc tool deferral (3 tools)

| Calc tool | Inputs | Outputs | Standard |
|---|---|---|---|
| `calc.socket_diversity` | room_type + socket count + jurisdiction | diversified_max_load_a per circuit | IET OSG Appendix A (already in shared/standards/electrical/BS7671/diversity-factors.json — verified-against-source) |
| `calc.ring_loop_zs` | ring length + csa + supply Ze | verified_zs_ohm at furthest socket | BS 7671 §433.1.5 + IET OSG §8.4 |
| `calc.radial_zs` | radial length + csa + supply Ze | verified_zs_ohm at end of radial | BS 7671 §411.4 / IEC 60364-4-41 §411.4 |

Each calc tool ships a contract in `shared/calculations/electrical/<calc-name>.json` (matches existing pattern from earthing's calc.zs_loop_impedance shipped in earthing v1.1).

WI3 deferral flag: `tool_call_pending_for_zs_verification: true` until runtime tools execute. SLD v1.3 + earthing v1.1 precedent.

### 3.7 — Drafting standards consumption (v1.6 just shipped)

`drawing_standard` + `sheet_size` + `scale` are part of the IR (consumes the v1.6 drafting standards layer):

- Sheet size lookup: `shared/standards/drafting/ISO5457/sheet-sizes.json` (or `ISO7200` for title block)
- Scale lookup: `shared/standards/drafting/ISO5455/use-guidance-per-discipline.json` — `small_power_layout: ["1:50", "1:100"]`
- Layer naming lookup: `shared/standards/drafting/BS1192/cad-layers.json` or AIA equivalent per jurisdiction

Per-jurisdiction sheet defaults match SLD v1.5 conventions (GB=A1, KE=A1, INT=A1, US=Arch_D).

## 4. The 4 jurisdictional examples (engineering scenarios)

### 4.1 — UK: 3-bedroom dwelling (`uk-3bed-dwelling`)

**Scenario:** 3-bedroom 2-storey UK domestic dwelling. ~100 m² floor area. TN-C-S DNO supply per BS 7671:2018+A2:2022. Consumer unit (CU) is a 12-way amendment-3 board.

**Engineering content:**
- **Ring final circuits (2):**
  - C01: Ground-floor ring (kitchen + utility + dining) — 32A RCBO Type A 30mA, 2.5mm² ring + 1.5mm² CPC, ~32m total ring length, 14 sockets + 2 FCUs (fridge + extractor)
  - C02: First-floor ring (3 bedrooms + landing) — 32A RCBO Type A 30mA, 2.5mm² ring, ~28m total, 10 sockets
- **Dedicated radials (3):**
  - C03: Cooker outlet (DEDICATED — 32A switch-fused outlet on 6mm² T+E radial)
  - C04: Immersion heater (DEDICATED — 16A radial on 2.5mm² T+E)
  - C05: Bathroom shaver outlet (BS EN 61558-2-5 shaver supply unit on 6A radial)
- **Bathroom Part 7-701 zones**: bathroom marked `special_location: "bathroom_zone_3"`; explicit no-sockets-in-zone-1 documented in rationale §4
- **Outdoor IP**: garden socket marked `special_location: "outdoor"`, IP65 weatherproof BS EN 60670, RCD 30mA Type A

**Citations:** BS 7671:2018+A2:2022 §433.1.5 (ring) + §411.3.3 (RCD) + Part 7-701 (bathrooms) + IET OSG Appendix A (diversity).

**Drafting:** A1 ISO + BS 1192:2007+A2:2016 layer naming + 1:50 floor plan + ISO 7200 title block.

### 4.2 — KE: Small office in Nairobi (`ke-nairobi-small-office`)

**Scenario:** 80 m² ground-floor commercial office unit in Nairobi. 4 workstation positions + 1 reception desk + 1 kitchenette + 1 toilet/cleaner's cupboard. KPLC TN-S 415V TPN supply per KS 1700:2018 §313 (routes to BS 7671 §313.1).

**Engineering content:**
- **Radial circuits (4):**
  - C01: Workstation power circuit 1 (workstations 1-2 + reception) — 20A MCB Type B + 30mA RCD (board-level), 2.5mm² T+E radial, 6 sockets
  - C02: Workstation power circuit 2 (workstations 3-4) — 20A MCB Type B + 30mA RCD, 2.5mm² T+E radial, 4 sockets
  - C03: Kitchenette radial (kettle, microwave, dishwasher) — 20A MCB + 30mA RCD, 2.5mm² T+E radial (NOT a ring; KE follows radial-only practice for kitchenettes despite BS 7671 routing), 3 sockets + 1 FCU
  - C04: Toilet shaver supply (BS EN 61558-2-5) — 6A MCB radial, dedicated
- **Sockets:** BS 1363 13A double-gang switched sockets at 300mm AFF (workstations) and 1100mm AFF (above worktop kitchenette)
- **Special locations:** Toilet marked `bathroom_zone_3` per BS 7671 Part 7-701 routing
- **KS 1700 routing:** All citations carry direct `"KS 1700:2018 §701..."` form per Kenya jurisdictional policy

**Citations:** KS 1700:2018 §701 (routes to BS 7671 Part 7-701) + KS 1700:2018 §433.1 (routes to BS 7671 §433.1.4 radial circuit) + KPLC declared PSCC.

**Drafting:** A1 ISO + KS 1700:2018 §313 routes to BS 1192 layer naming + 1:50 floor plan.

### 4.3 — INT: Commercial open-plan office floor (`intl-open-plan-floor`)

**Scenario:** 350 m² open-plan office floor (ground level of a multi-storey building). Commercial supply 400V TPN. 24 workstation positions across the floor + 2 meeting rooms + 1 kitchenette + 1 server cabinet area + 1 male/female toilet block.

**Engineering content:**
- **Radial circuits (8):**
  - C01-C02: Workstation power circuits (12 workstations per circuit, dual workstation socket per position = 24 sockets per circuit) — 20A MCB Type C + 30mA Type A RCD, 2.5mm² Cu PVC radial
  - C03-C04: Meeting room power + AV — 16A MCB Type C + 30mA Type A RCD, 2.5mm² radial
  - C05: Kitchenette appliances (kettle/microwave/dishwasher) — 20A MCB + 30mA Type A RCD, 2.5mm² radial
  - C06: Server cabinet small-power (3-phase UPS-fed via UPS DB) — Type B 30mA RCD per IEC 60364-5-53 §531.3.3 (matches db-layout intl-dbcomms-data pattern)
  - C07: Toilet block — shaver outlet only (BS EN 61558-2-5) on 6A radial
  - C08: Outdoor sockets (smoking shelter + bin store) — IP65 + 30mA Type A RCD
- **Sockets:** Schuko CEE 7/4 single + double-gang at 300mm AFF (workstations) and 1100mm AFF (kitchenette)
- **Special locations:** Toilets marked `bathroom_zone_3`; outdoor sockets marked `outdoor`
- **Cross-skill alignment:** UPS-fed server-room circuit C06 references the same Type B RCD policy as db-layout's intl-dbcomms-data shipped example

**Citations:** IEC 60364-4-41 §411.3.3 (RCD) + IEC 60364-5-53 §531.3.3 (Type B RCD for IT loads) + IEC 60364-7-701 (toilets/bathrooms) + ISO 19650:2018 (CDE layer naming).

**Drafting:** A1 ISO + ISO 19650:2018 + BS 1192:2007+A2:2016 (generic INT) + 1:100 floor plan + ISO 7200 title block.

### 4.4 — US: Residential dwelling (`us-residential-dwelling`)

**Scenario:** Single-family residential dwelling, ~160 m² (1700 ft²), 1-storey. NEC 2023 Article 210 + 120/240V split-phase supply (typical US residential — center-tapped single-phase from utility transformer, providing 120V branch circuits for general loads and 240V for high-load appliances).

**Engineering content:**
- **Receptacle circuits (per NEC 210.52 spacing):**
  - C01: Kitchen small appliance branch circuit 1 (NEC 210.52(B) — minimum two 20A circuits required) — 20A AFCI + GFCI receptacles per NEC 210.8(A)(6) + 210.12(B)
  - C02: Kitchen small appliance branch circuit 2 — same spec
  - C03: General receptacles — bedrooms + living room — 15A AFCI per NEC 210.12(A)
  - C04: Bathroom GFCI receptacle — 20A GFCI per NEC 210.8(A)(1) + 210.11(C)(3)
  - C05: Garage GFCI receptacles — 20A GFCI per NEC 210.8(A)(2)
  - C06: Outdoor receptacles (front + back yard, weatherproof) — 20A GFCI per NEC 210.8(A)(3)
  - C07: Basement GFCI receptacles — 20A GFCI per NEC 210.8(A)(5)
  - C08: Laundry circuit — 20A dedicated radial per NEC 210.11(C)(2)
- **Receptacles:** NEMA 5-15 duplex (standard) + NEMA 5-20 (kitchen + dedicated 20A circuits). Tamper-resistant per NEC 406.12 (dwelling units).
- **Special locations enum:** Bathrooms / kitchen / outdoor / garage / basement → `wet_area` (new enum value for US GFCI scope) or per-zone-explicit
- **NEC 210.52 spacing rules:** Any point along wall ≤6 ft (1.83 m) from a receptacle (i.e., no point more than 12 ft = 3.66 m apart). Sockets on every wall ≥2 ft (0.61 m) wide.

**Citations:** NEC 2023 Article 210 (branch circuits) + Article 250 (grounding) + 210.52 (receptacle spacing) + 210.8 (GFCI) + 210.12 (AFCI) + 406.12 (tamper-resistant).

**Drafting:** Arch_D ANSI + AIA CAD Layer Guidelines 2007 + 1/4"=1' floor plan + ISO 7200 title block.

### 4.5 — Cross-example consistency

| Property | UK | KE | INT | US |
|---|---|---|---|---|
| Jurisdiction | GB | INT (KE label via KS 1700) | INT | US |
| Supply | TN-C-S 230V 1ph | KPLC TN-S 415V TPN | TN-S 400V TPN | TN-C-S 240V split-phase |
| Default RCD | 30mA Type A | 30mA Type A | 30mA Type A | GFCI |
| Ring circuits | YES (2 rings) | NO (radial only) | NO | NO |
| Special location standard | BS 7671 Part 7-701 | KS 1700 §701 → BS 7671 | IEC 60364-7-701 | NEC 210.8 (GFCI scope) |
| Diversity source | IET OSG App A | IET OSG App A (via KS routing) | IEC 60364-1 §132.12 | NEC 220.40 |
| Sheet size | A1 ISO | A1 ISO | A1 ISO | Arch_D ANSI |
| Layer naming | BS 1192 | KS 1700 → BS 1192 | ISO 19650 + BS 1192 | AIA CAD Layer Guidelines 2007 |
| Drawing scale | 1:50 | 1:50 | 1:100 | 1/4"=1' (≈ 1:48) |

## 5. Generator + Validator + Reviewer

### 5.1 — Generator prompt (12-step pattern)

Mirrors SLD/earthing/cable-sizing/fault-level/arc-flash 12-step structure:

1. Determine jurisdiction + parent DB context (engineer-declared input)
2. Identify rooms + dimensions + special_location flags
3. Determine circuit topology decisions (ring vs radial vs dedicated_radial) per jurisdictional default + engineering judgment
4. Allocate circuits to rooms (build rooms_covered cross-reference)
5. Determine socket type per jurisdiction (BS 1363 / Schuko / NEMA / etc.) + per-room mount height + special-location compliance
6. RCD posture per circuit (Type A / Type B / no-RCD-exception)
7. OCPD selection (rating + curve + breaking capacity) + cable sizing (engineer-declared, validated against ocpd)
8. Diversity application (engineer estimates max load; calc.socket_diversity contract pending)
9. Zs verification flag (tool_call_pending_for_zs_verification: true)
10. Compliance summary + assumptions
11. Build intent-out (slim subset per intent schema)
12. Rationale block (WI2, 8 sections + chat_summary ≤500 chars)

### 5.2 — Validator INV checks (~10 checks)

- INV-1: schema shape conformance (circuits[] + rooms[] structure intact)
- INV-2: cross-reference integrity — every socket's circuit_id resolves to a circuits[] entry
- INV-3: cross-reference integrity reverse — every circuit's rooms_covered[] resolves to rooms[] entries
- INV-4: topology-by-jurisdiction — `ring` topology only allowed for `jurisdiction in {"GB", "KE"}`
- INV-5: special-location enforcement — bathroom_zone_1 has NO sockets; bathroom_zone_2 has shaver-only; bathroom_zone_3 + outdoor have 30mA RCD
- INV-6: RCD posture validity — Type A 30mA default for sockets ≤32A; Type B for IT loads with documented IEC 60364-5-53 §531.3.3 citation; no-rcd-exception requires explicit BS 7671 §411 citation
- INV-7: diversified_max_load_a < ocpd.rating_a per circuit (engineer estimate sanity check)
- INV-8: Zs verification deferral consistency — `tool_call_pending_for_zs_verification: true` AND `flags[]` contains `TOOL-CALL-PENDING:calc.<tool>` for every circuit
- INV-9: chat_summary ≤500 chars
- INV-10: drafting standards consumed — drawing_standard + sheet_size + drawing_scale present per jurisdiction default

### 5.3 — Reviewer D-checks (6 checks)

- D-1: rationale chat_summary captures essential engineering story ≤500 chars
- D-2: citations carry year qualifier per jurisdiction (BS 7671:2018+A2:2022 / KS 1700:2018 / IEC 60364-X:YYYY / NEC 2023)
- D-3: jurisdictional citation form rigor (no BS 7671 in INT/US examples except routing notes; no NEC in GB examples)
- D-4: WI3 deferral consistency (tool_call_pending + flag pair) + engineer assumptions documented
- D-5: cross-example shape consistency (4 examples follow same IR structure; no rogue fields)
- D-6: drafting standards consumed correctly (sheet_size + scale + layer naming match jurisdiction)

## 6. Evals (7-9 YAMLs)

### 6.1 — WI5 standard 5 categories (5 evals)

- eval-01-happy-path.yaml (UK ring + bathroom + outdoor pass)
- eval-02-edge-case.yaml (no-RCD exception declared with proper citation)
- eval-03-validation-trap.yaml (engineer attempts ring in US example → INV-4 fires)
- eval-04-rationale-block.yaml (chat_summary length + 8 sections)
- eval-05-jurisdiction-switch.yaml (correct citation form per jurisdiction)

### 6.2 — Skill-specific evals (2-4 evals)

- eval-06-ring-topology-by-jurisdiction.yaml — verifies INV-4 fires for non-GB/KE ring attempts
- eval-07-special-locations-compliance.yaml — verifies bathroom zones + outdoor + wet_area RCD requirements per jurisdiction
- eval-08-cross-room-ring-integrity.yaml — verifies UK example's cross-room ring (kitchen + utility) bidirectional cross-reference integrity
- eval-09-gfci-scope-us.yaml — verifies US example's NEC 210.8 GFCI requirements per circuit

## 7. Bookkeeping

| File | Change |
|---|---|
| `electrical/small-power/skill.manifest.json` | NEW — v1.0.0 beta declaration |
| `electrical/small-power/CHANGELOG.md` | NEW — v1.0.0 entry |
| `SKILLS_STATUS.md` | NEW row — drawings skills 5 of 8 production |
| `ARCHITECTURE.md` | NEW "small-power skill (v1.0)" subsection under drawings layer |

## 8. Sequencing (5 phases, 17 tasks)

### Phase A — Infrastructure (Tasks 1-3)

1. Skill skeleton: skill.manifest.json + inputs.json + README.md + CHANGELOG.md
2. Schemas: small-power-ir.schema.json + small-power-intent.schema.json
3. Standards + calc contract additions: special-locations.json (BS7671 + NFPA70 + IEC60364) + calc.socket_diversity / calc.ring_loop_zs / calc.radial_zs contracts

### Phase B — Prompts (Tasks 4-6)

4. Generator prompt (12-step)
5. Validator prompt (~10 INV checks)
6. Reviewer prompt (6 D-checks)

### Phase C — Examples (Tasks 7-10)

7. UK 3-bedroom dwelling (5 files)
8. KE Nairobi small office (5 files)
9. INT commercial open-plan office floor (5 files)
10. US residential dwelling (5 files)

### Phase D — Evals + ontology + symbols + rules (Tasks 11-15)

11. Ontology: socket-types.json + room-types reuse
12. Symbols: socket symbols (single + double + RCD + FCU + outdoor + GFCI + tamper-resistant)
13. Rules YAMLs: per-jurisdiction RCD + topology + special-location rules
14. Constraints + validation YAMLs
15. Evals: 7-9 YAMLs

### Phase E — Bookkeeping + final review + push (Tasks 16-17)

16. SKILLS_STATUS row + ARCHITECTURE subsection
17. Cross-cutting validation + code-reviewer agent + push

## 9. Acceptance criteria

- [ ] skill.manifest.json declares `consumes_intents: []` (leaf v1.0 per §3.1)
- [ ] `produces_intent: "small-power"` + intent schema valid
- [ ] All 4 examples ship 5 files each (input + output + intent-out + reasoning + sample-schedule)
- [ ] All 4 examples' intent-out.json validates against small-power-intent.schema.json (strict additionalProperties:false)
- [ ] UK example uses ring topology (verified by validator INV-4); KE example uses radial-only (INV-4: KE jurisdiction → no `ring` topology in circuits[])
- [ ] INT example C06 (server-room small-power) uses Type B 30mA RCD per IEC 60364-5-53 §531.3.3 (consistent with db-layout intl-dbcomms-data shipped example)
- [ ] US example uses GFCI per NEC 210.8 + AFCI per 210.12; AIA layer naming; Arch_D sheet
- [ ] All 4 examples carry chat_summary ≤500 chars
- [ ] All 4 examples reference WI3 deferral (`tool_call_pending_for_zs_verification: true`)
- [ ] Citations form per jurisdiction: GB = "BS 7671:2018+A2:2022"; KE = "KS 1700:2018"; INT = "IEC 60364..."; US = "NEC 2023 Article ..."
- [ ] Validator has ~10 INV checks; ring-topology-only-in-GB/KE INV explicit
- [ ] Reviewer has 6 D-checks
- [ ] 3 calc tool contracts shipped in shared/calculations/electrical/ (socket_diversity + ring_loop_zs + radial_zs)
- [ ] 3 special-locations.json shipped in shared/standards/electrical/{BS7671,NFPA70,IEC60364}/
- [ ] SKILLS_STATUS row + ARCHITECTURE subsection
- [ ] Final code review verdict APPROVE

## 10. Risks + mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Ring topology engineering judgment hard to validate (engineer-declared per OSG §8.4) | Medium | INV-4 check verifies ring conditions (≤100 m² floor area + ≤2 spurs per leg) from declared values; engineer rationale required in reasoning.md §4 |
| Cross-room ring representation is novel — engineers may mis-map socket→circuit | Low | `rooms_covered` field on circuit + circuit_id on each socket → bidirectional check by validator (INV-2 + INV-3 cross-ref integrity); eval-08 verifies the round-trip |
| GFCI/AFCI requirements in NEC 2023 differ from prior NEC editions | Medium | Cite NEC 2023 explicitly (no NEC 2017/2020 fallback) + cross-ref AFCI added scope; flag in US reasoning.md §3 |
| Diversity factor application — engineer might over-diversify (skill doesn't enforce min loads) | Low | calc.socket_diversity contract is engineer-input-driven; max_load_a is engineer-declared per circuit, validated against ocpd rating |
| BS 7671 §411.3.3 exception cases poorly understood (when can you OMIT 30mA RCD?) | Medium | rcd_posture enum has `no_rcd_with_documented_§411_exception` — requires explicit BS 7671 §411 reference in reasoning.md when used; UK example doesn't use this exception (all sockets RCD-protected) |
| EV charging in scope by accident (e.g., engineer adds EVSE circuit in UK example garage) | Low | INV check: dedicated_radial with downstream_load_kw > 5.0 → emit `INV-N:possible-ev-circuit` warning suggesting future ev-charging skill |
| INT example IEC 60364-7-701 sometimes interpreted differently across European countries | Medium | Document the interpretation chosen + cite IEC 60364-7-701 directly (no national-annex routing in v1.0); engineer override valid for national annexes |
| Future db-layout consumption of small-power intent creates circular dependency | Low | small-power v1.0 deliberately leaves db-layout consumption asymmetric (small-power → db-layout, not reverse); v1.1 multi-skill consumption adds earthing + fault-level only (not db-layout) |

## 11. Versioning

- **v1.0.0 beta** (this sprint) — leaf skill, no cross-skill consumption, 4 jurisdictional examples, hybrid circuits[]+rooms[] model
- **v1.1.0** (future sprint) — multi-skill consumption (consume earthing + fault-level intents); INV-N cross-skill consistency checks; matches SLD v1.3→v1.4 migration pattern
- **v2.0.0** (future) — schema-breaking changes; possibly multi-board consumption (small-power spanning N parent DBs across a building); EV charging integration if not deferred to ev-charging skill

## 12. Pattern parents

- **lighting-layout v1.3** (production) — leaf-skill shape; room-based pattern; symbols + ontology + drafting + calculations folder structure; full skill scaffolding
- **SLD v1.5** (shipped 2026-05-19) — 4-jurisdiction example pattern; drafting standards consumption (sheet/scale/layer from v1.6); v1.0 → v1.1 multi-skill migration precedent
- **earthing v1.3** (shipped 2026-05-18) — single-board WI4 producer pattern; 4-jurisdiction examples (UK + KE + INT + US); KS 1700 routing convention for KE
- **db-layout v1.3** (shipped 2026-05-19) — future consumer of small-power intent (when db-layout v1.x adds small-power consumption); existing intl-dbcomms-data + intl-dbp1-power examples set the circuit shape precedent
- **arc-flash-labelling** (shipped 2026-05-17) — jurisdiction-aware standards consumption + 17-check validator + 6 D-check reviewer pattern
- **drafting standards v1.6** (shipped 2026-05-19) — sheet template + scale + layer naming consumption per jurisdiction

## 13. Cross-references

- Pattern parent: `electrical/lighting-layout/` v1.3 — gold-standard layout skill (file structure + scaffolding + room-based model)
- Pattern parent: `electrical/sld/` v1.5 — drafting standards consumption + multi-skill migration precedent
- Memory: [[build-strategy-breadth-first]] — small-power closes the 5-of-8 drawings-skill milestone
- Memory: [[sld-deferred-followups-queue]] — small-power named as next after SLD chapter
- Memory: [[runtime-project-boundary]] — calc.socket_diversity / calc.ring_loop_zs / calc.radial_zs runtime tools deferred per WI3
- Future: db-layout v1.x adds small-power consumption (similar to its existing lighting-layout consumption)
- Future: small-power v1.1 adds earthing + fault-level consumption (SLD v1.4 pattern)
- Future: ev-charging skill picks up BS 7671 Part 7-722 / NEC 625 / IEC 60364-7-722 EV-specific scope
