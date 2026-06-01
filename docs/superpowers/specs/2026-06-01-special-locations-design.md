# special-locations v1.0 — Design Spec (Wave 1 Second Deliverable)

**Date:** 2026-06-01 (v1.0.1 — citation hygiene pass + §703 sauna re-zoning + §710 IT system depth correction)
**Spec author:** brainstorm session via `superpowers:brainstorming`
**Cluster context:** [2026-05-29-lighting-cluster-roadmap.md](2026-05-29-lighting-cluster-roadmap.md) Wave 1 second deliverable, parallel with `photometric-analysis` v1.0.0 (shipped 2026-05-30).
**Predecessor:** [2026-05-30-photometric-analysis-design.md](2026-05-30-photometric-analysis-design.md) (Wave 1 first deliverable; established cascade-contract pattern this spec extends).
**Target skill path:** `electrical/special-locations/`
**Target version:** 1.0.0 production (no prior stub; brand-new skill).

---

## 1. Identity & architecture

`special-locations` is a **calc-primitive companion skill** that derives BS 7671:2018+A2:2022 Part 7 zoning + electrical constraints from upstream architectural-drawing extraction. It emits a constraint intent + IR but does NOT produce a primary drawing. Three downstream skills consume + apply the constraints.

| Attribute | Value |
|---|---|
| Path | `electrical/special-locations/` |
| Version | `1.0.0` (production) |
| Discipline | Electrical (folder placement scopes discipline per [[sprint-3w2c-shipped]]) |
| Role | Calc-primitive companion (same role class as `photometric-analysis`) |
| Output | 1 IR + 1 intent payload (`special_locations_zoning`) |
| Consumers | 3 cascades wired at v1.0 ship (lighting-layout v1.6 + small-power v1.2 + db-layout v1.5) |
| Sprint shape | 4 phases × ~18 implementer tasks (mirrors photometric pattern, +5 for triple cascade) |

**Why this skill exists.** Lumen-method gives average illuminance; photometric-analysis closed the §4.4 per-point gap. Special-locations closes the **Part 7 spatial-constraint gap** — engineers cannot detect "230V socket inside Zone 1" or "IPx0 luminaire inside medical envelope" by reading a 2D plan alone. This is the spatial-compliance leg of the lighting cluster.

**Standards stack:**
- BS 7671:2018+A2:2022 Part 7 §§701, 702, 703, 710, 715 (v1.0 scope — see §2)
- IEC 60364-7-XXX parallel parts (INT jurisdiction routing)
- KS 1700 §313 (KE jurisdiction — routes to BS 7671 Part 7 verbatim)

---

## 2. Scope (locked)

### v1.0 included sections (5)

| Section | Title | Scope at v1.0 |
|---|---|---|
| §701 | Locations containing a bath or shower | Zone 0/1/2 + outside-zones; wet-room expansion; whirlpool variant |
| §702 | Swimming pools and other basins | Zone 0/1/2 + adjacent-room overlap; pool_main_equipotential_bonding |
| §703 | Saunas | **3 zones** (zone_1 around heater high-temp; zone_2 within sauna away from heater; zone_3 above 1.5 m for accessories); heat-rated cable as zone field; 30 mA RCD on all circuits except heater per §703.411.3.3 |
| §710 | Medical locations | Groups 0/1/2 full coverage; full medical IT system architecture (isolating transformer per BS EN 61557-8 IMD + **8 s alarm response time** + supplementary bonding ≤0.2Ω); HTM 06-01 NHS precedence + BS EN 60601 equipment standards cross-referenced |
| §715 | Extra-low voltage lighting | ELV barrier zones + cable spacing + barrier/label requirements; transformer short-circuit protection per BS EN 61558-2-6 (file-verified cross-reference) |

### Scope corrections from cluster roadmap §6.4 (auditable)

The cluster roadmap brief listed v1.0 scope as `§701 + §710 + §714 + §753`. Two were citation errors caught at brainstorm:

| Roadmap brief | Reality | Resolution |
|---|---|---|
| §714 "external lighting" | **Does not exist** in BS 7671:2018+A2:2022. The CLAUDE.md "no §714 anywhere" rule was established for exactly this reason. | Replaced with §715 (Extra-Low Voltage Lighting), which is the real ELV-for-external-installations section. "External lighting" generally routes through BS 5489-1 + §522 IP; not a Part 7 section. |
| §753 "floor/ceiling heating" | **Does not exist** in BS 7671:2018+A2:2022. IEC 60364-7-753 covers embedded heating internationally; BS 7671 chose not to adopt it. | Dropped from v1.0. UK heating compliance routes through §415 + §522 + manufacturer instructions; will be folded into a v1.1 `embedded_heating` sub-scope if engineer demand surfaces. |
| §702 swimming pools | Real (§702 exists). Listed as v1.1 in roadmap; promoted to v1.0 to give broader engineering coverage at launch. | Included in v1.0. |
| §703 saunas | Real (§703 exists). Listed as v1.1 in roadmap; promoted to v1.0. | Included in v1.0. |

Verified against `shared/standards/electrical/BS7671/part7-special-locations.json` (verification_status: `verified-against-source`). This avoids the D2.3 citation-misattribution class of bug at the brainstorm stage rather than the implementer stage.

### Verified citation table (v1.0.1 — every clause the skill cites)

Cross-checked against the verified standards file. **No other Part 7 sub-clause citations are valid** — if any prompt/INV/example needs to cite a clause not on this table, fall back to the section's top-level citation + a named cross-reference standard.

| Citation | Section | Verified in file | Used for |
|---|---|---|---|
| `BS 7671:2018 §701` | §701 | yes (top-level) | Generic §701 scope reference |
| `BS 7671:2018 §701.411.3.3` | §701 | yes | 30 mA RCD on all bathroom circuits |
| `BS 7671:2018 §701.414.4.5` | §701 | yes | SELV ≤12 V in Zone 0 |
| `BS 7671:2018 §701.415.2` | §701 | yes | Supplementary equipotential bonding |
| `BS 7671:2018 §701.512.2` | §701 | yes | IPx5 where water jets used (drives whirlpool pump IP) |
| `BS 7671:2018 §701.512.3` | §701 | yes | Socket outlet ≥3 m from zone 1 boundary |
| `BS 7671:2018 §702` | §702 | yes (top-level) | Generic §702 scope reference |
| `BS 7671:2018 §702.415.1` | §702 | yes | **Main equipotential bonding (NOT §702.55.1)** |
| `BS 7671:2018 §702.415.2` | §702 | yes | Pool supplementary bonding |
| `BS 7671:2018 §702.55.4` | §702 | yes | Zone 2 extension into changing rooms (barrier check) |
| `BS 7671:2018 §703` | §703 | yes (top-level) | Generic §703 scope reference |
| `BS 7671:2018 §703.411.3.3` | §703 | yes | 30 mA RCD on sauna circuits except heater |
| `BS 7671:2018 §710` | §710 | yes (top-level) | Generic §710 scope (Group 0/1/2 definitions); no sub-clauses valid in this file |
| `BS 7671:2018 §715` | §715 | yes (top-level) | Generic §715 scope (no sub-clauses valid in this file) |

**Cross-reference standards verified in the file (cited by the skill where Part 7 itself lacks sub-clauses):**

| Cross-reference | Used for |
|---|---|
| `HTM 06-01` (NHS technical memorandum) | Medical electrical services; takes precedence in NHS sites; safety service categories live here, NOT in §710 |
| `BS EN 60601` series | Medical electrical equipment safety (cross-ref for §710 medical) |
| `BS EN 61557-8` | Insulation monitoring devices (IMD) for medical IT systems — defines the 8 s alarm response time for §710 Group 2 |
| `BS EN 61558-2-6` | Transformer short-circuit protection for §715 ELV lighting |
| `BS 5266-1` + `HTM 06-01` | Emergency lighting in medical locations (3 h operating-light backup; 24 h escape) |
| `BS 5489-1` | External road/area lighting (NOT a Part 7 section; routes external installations generically through BS 7671 §522 IP) |

**Banned citations (would fail INV / fix-pass):** `§701.32`, `§701.55`, `§702.55.1`, `§702.55.2`, `§702.32`, `§703.55`, `§703.512`, `§703.413`, `§710.413.1.5`, `§710.314`, `§710.411.3.3`, `§715.560.4`, `§715.521`, `§715.422`. These were transcribed during brainstorm but do not exist in the verified file; using them would replicate the §714/Reg 559 class of error.

### v1.1 deferrals (declared, not built)

- §722 EV charging — exists in Part 7; intersects with EV-Charge skill; defer until that skill matures
- §704 construction sites / §705 agricultural / §708 caravan parks / §709 marinas — niche, build when first project requirement lands
- Embedded heating (§415 + §522 routing) — fold into v1.1 `embedded_heating` scope
- IEC 60364-7-XXX worked examples (INT jurisdiction) — v1.0 ships citation routing only; full INT examples come with first INT project
- US NEC Article 680 / 517 — separate sibling skill (`electrical/special-locations-us/`) when first US project lands; NOT in this skill

### v2.0 candidates

- §710 Group 2 split-out into sibling `electrical/medical-electrical/` skill IF the medical IT system architecture grows beyond a single `electrical_constraints[]` block (currently fits cleanly)
- MRI rooms (`electrical/medical-mri/` sibling) — IEC 60601-1 + Faraday cage specs are a different standards stack
- Anchor extraction from native BIM/IFC by the runtime (currently the runtime extracts from architectural drawing; BIM-direct is a runtime concern, not a skill concern)

---

## 3. Architecture decisions (locked at brainstorm)

| Decision | Choice | Rationale |
|---|---|---|
| v1.0 scope | §701 + §702 + §703 + §710 + §715 (5 sections) | Widest defensible scope; all 5 verified in standards file |
| Zone derivation | Auto-derive from upstream anchor positions | Matches DraftsMan calc-primitive pattern; engineering-judgment value at launch |
| Anchor source | Top-level `anchor_fixtures[]` input (sourced by runtime from architectural extraction) | Skill stays independent of plumbing/medical-gas skill maturity; runtime provenance carried via `_extraction_source` field |
| Cascade consumers | 3 (lighting-layout v1.6 + small-power v1.2 + db-layout v1.5) | Full cross-discipline coverage; replaces "lighting-only" misconception |
| Intent shape | Single flat intent with `zone_type` discriminator (**13 values** = 3 bath + 3 pool + 3 sauna + 3 medical + 1 ELV) | Pure additive growth for v1.1+ sections; one cascade contract per consumer; mirrors db-layout `board_kind` pattern |
| Geometry depth | 2.5D — plan polygon + height_min/max + parametric cylinder | Captures 3D accuracy where it matters (shower head height, medical envelope) without forcing 3D vertex authoring |
| §710 medical depth | Groups 0/1/2 + full IT system (isolating transformer + IMD per **BS EN 61557-8 8 s alarm response** + supplementary bonding ≤0.2Ω + HTM 06-01 NHS precedence) | Most engineering-valuable scope at launch; sibling skill split deferred to v2.0 only if needed |
| Cross-check pattern | Hybrid (authoritative source + thin consumer cross-check) | Defense in depth without re-evaluation drift; matches photometric INV-11 sub-check 3 pattern |

---

## 4. Input model (`inputs.json` — 7 items)

Per CLAUDE.md, inputs.json declares the WI1 interview taxonomy validated against `shared/schemas/core/inputs.schema.json`.

### 4.1 `anchor_fixtures[]` (REQUIRED)

Top-level list. Drives auto-zone-derivation. Sourced by the DraftsMan runtime from architectural-drawing extraction; engineer can supply manually as fallback.

**Anchor `type` enum (6 values):**

```
bath_basin | shower_position | pool_basin | sauna_heater
medical_patient_position | elv_lighting_circuit_anchor
```

**Per-anchor fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `type` | enum (6 values above) | yes | |
| `id` | string | yes | Engineer-stable reference (e.g. `bath_1`, `pool_main`) |
| `position` | `{x_mm, y_mm, z_floor_mm}` | yes | Room-local coords; z is floor-to-anchor-base |
| `dimensions` | `{length_mm, width_mm, height_mm}` | conditional | Required when `shape_kind = rectangular` |
| `shape_kind` | `rectangular \| cylinder` | yes | `cylinder` for pool/medical/sauna_heater |
| `radius_mm` | number | conditional | Required when `shape_kind = cylinder` |
| `bath_kind` | `standard \| whirlpool` | conditional | Required when `type = bath_basin`. Whirlpool variant triggers INV-06 + D-3 (§701 + §701.512.2 IPx5 where water jets used; no §701.55 sub-clause in verified file) |
| `medical_group` | `0 \| 1 \| 2` | conditional | Required when `type = medical_patient_position` |
| `shower_head_height_mm` | number | conditional | Required when `type = shower_position`; drives Zone 1 ceiling (per `BS 7671:2018 §701` — sub-clause not cited per verified-file constraint; ceiling math + 2.25 m floor per §701 zone-table common-knowledge) |
| `whirlpool_pump_position` | `{x_mm, y_mm, z_mm}` | optional | Defaulted to bath edge if absent + flagged as assumption by reviewer D-3. Citation: `BS 7671:2018 §701 + §701.512.2` (IPx5 where water jets used) |
| `_extraction_source` | enum (3 values) | yes | `architectural_drawing_extraction \| engineer_manual_entry \| inferred_from_room_type` |
| `_provenance_note` | string (≥40 char) | yes | Honest disclosure (INV-09) |

Sub-fields cover whirlpool + wet-room variants without enum bloat. MRI is explicitly out of scope (separate standards stack — IEC 60601-1).

### 4.2 `room` (REQUIRED)

**Room `room_type` enum (9 values):**

```
bathroom | shower_room | swimming_pool_hall | sauna
medical_group_0_area | medical_group_1_ward | medical_group_2_theatre
external_landscape | other
```

**Per-room fields:** `room_polygon_mm` (plan boundary in room-local coords), `ceiling_height_mm`, `floor_finish` (`tiles | vinyl | carpet | screed | external_ground`), `is_external` (boolean — drives §715/§522 IP routing), `is_wet_room` (boolean — expands Zone 1 to full floor area per `BS 7671:2018 §701` + IET GN7 wet-room commentary; no §701 sub-clause for this in the verified file, generic §701 citation applies), `ambient_temperature_c` (optional — drives ELV de-rating per reviewer D-5).

### 4.3 `jurisdiction` (REQUIRED)

Enum: `GB | KE | INT`. Drives `_clause_citation` routing per CLAUDE.md jurisdiction discipline:
- `GB` → `BS 7671:2018+A2:2022 §X`
- `KE` → `KS 1700:2018 §313 (route to BS 7671 §X)`
- `INT` → `IEC 60364-7-XXX § Y`

### 4.4 `existing_fixtures[]` (OPTIONAL)

Per-fixture cross-check data. Used when consumed lighting-layout / small-power intents are not yet available (early-design pre-check). Each entry: `{type, position, ip_rating, voltage_v, is_rcd_protected, source_skill?, source_skill_intent_path?}`. Skill iterates this list against derived zones → flags violations into `non_compliance_flags[]`.

When the consumed lighting-layout intent IS present, the skill prefers reading `existing_fixtures[]` from the intent over the engineer-supplied input (intent is the more recent authoritative source).

### 4.5 `zone_polygon_override[]` (OPTIONAL)

Engineer overrides specific derived zones for irregular geometry (corner baths, L-shaped pools). Each entry: `{zone_id, replacement_polygon_mm, _reason: "<≥40 char prose>"}`. Original derivation polygon preserved in IR with `_overridden_by_engineer: true` flag.

### 4.6 `medical_it_system_override` (OPTIONAL)

For §710 Group 2 rooms when engineer has commissioned IT system data ahead of compliance check:

```yaml
{
  isolating_transformer_va: <int>,
  insulation_monitoring_device_present: <bool>,
  imd_alarm_response_time_s_observed: <int>,            # 8 s typical per BS EN 61557-8
  supplementary_bonding_verified: <bool>,
  supplementary_bonding_resistance_ohm_observed: <number>,  # ≤ 0.2 Ω per §710 verified-file body
  safety_service_category: 1 | 2 | 3                    # per HTM 06-01 NHS technical memorandum (NOT a BS 7671 sub-clause)
}
```

### 4.7 `ies_lookup_paths[]` (OPTIONAL)

For ELV §715 luminaire-IP cross-check via consumed lighting-layout intent. Mirrors photometric-analysis IES handling at v1.0 (synthetic_reference_C3 fallback at `shared/photometric/ies/<type>.ies` if project IES unavailable).

### 4.8 Consumed upstream intents

**One intent consumed (optional):** `lighting-layout.intent` when `room.room_type ∈ {bathroom, shower_room, swimming_pool_hall, medical_*, external_landscape}`. Needed to populate `existing_fixtures[]` when the engineer didn't supply it directly. If no lighting-layout intent exists, skill emits zoning + constraints only (no fixture-violation flags), and INV-08 emits "cross-check skipped — engineer must verify fixture placement manually."

---

## 5. IR shape (`special-locations-ir.schema.json`)

10 top-level properties; 8 required. Single flat shape per the discriminator pattern.

### 5.1 Top-level properties

| # | Property | Type | Required | Notes |
|---|---|---|---|---|
| 1 | `drawing_type` | const `"special_locations_zoning"` | yes | Schema-level constant |
| 2 | `version` | string | yes | Skill version `"1.0.0"` |
| 3 | `mode` | enum `full_analysis \| screening_only` | yes | `screening_only` = early-design pre-check (zones only, no fixture audit) |
| 4 | `jurisdiction` | enum (GB \| KE \| INT) | yes | |
| 5 | `room` | object | yes | Mirror of inputs.4.2 |
| 6 | `anchor_fixtures[]` | array | yes | Echo of inputs.4.1 with resolved sub-fields |
| 7 | `zones[]` | array | yes | Discriminated by `zone_type` (12 values) |
| 8 | `electrical_constraints[]` | array | conditional | Required when mode == full_analysis OR Group 2 medical present |
| 9 | `existing_fixtures_audit[]` | array | conditional | Populated only when mode == full_analysis AND consumed lighting-layout intent OR `existing_fixtures[]` input is present |
| 10 | `calculation_summary` | object | yes | Rollup |

Plus: `invariants[]` (validator INVs), `rationale` (chat_summary + sections per `[[rationale.schema.json]]`).

### 5.2 `zones[]` discriminated by `zone_type` (13 values)

```
bath_zone_0 | bath_zone_1 | bath_zone_2                            # §701
pool_zone_0 | pool_zone_1 | pool_zone_2                            # §702
sauna_zone_1 | sauna_zone_2 | sauna_zone_3                         # §703 (3 zones per verified file: zone_1 around heater high-temp; zone_2 within sauna away from heater; zone_3 above 1.5 m for accessories)
medical_envelope_group_0 | medical_envelope_group_1 | medical_envelope_group_2  # §710 (separate values — see §3 decision)
elv_barrier_zone                                                    # §715
```

**§703 sauna zone geometry note:** The verified file specifies sauna_zone_1 = "around the heater (high temperature zone)" — small rectangular footprint near heater anchor; sauna_zone_2 = "within the sauna room, away from heater" — sauna room polygon minus zone_1; sauna_zone_3 = "above 1.5 m for accessories" — full sauna room footprint, height_min_mm = 1500. The zone-derivation library (A.4) implements this 3-zone split.

**Per-zone common fields:**

```yaml
{
  zone_id: string,
  zone_type: <enum 12 values>,
  source_anchor_id: string,
  derivation_clause: "BS 7671:2018 §701 / §702 / §702.415.1 / §702.55.4 / §703 / §703.411.3.3 / §710 / §715 — only verified clauses per §3 table",
  boundary_plan_polygon_mm: [[x,y], …],       # ≥3 vertices; ≥12 sides for cylindrical zones
  height_min_mm: number,
  height_max_mm: number,                       # height_min ≤ height_max enforced at schema level
  ip_rating_min: "IPx0" | "IPx4" | "IPx5" | "IPx7" | "IPx8",
  max_voltage_v: 12 | 25 | 50 | 230 | null,
  rcd_required_ma: 30 | null,
  isolation_required: boolean,
  allowed_equipment_classes: ["class_1", "class_2", "class_3_SELV"],
  prohibited_fixture_types: ["socket_230v", "switch_230v", "luminaire_non_ip_rated", ...],
  switch_position_min_distance_mm: number | null,
  overlapping_with_zone_ids: [string],         # populated when this zone overlaps siblings (INV-01)
  _clause_citation: "<routed per jurisdiction>",
  _derivation_note: "<40-800 char honest-disclosure prose>"
}
```

**Discriminator-conditional required fields** (enforced via JSON Schema `allOf` per-value branches):

| zone_type | additional required |
|---|---|
| `medical_envelope_group_2` | sibling `electrical_constraints[]` entry with `constraint_type == "medical_it_system"` whose `applies_to_zone_ids[]` includes this `zone_id` |
| `medical_envelope_group_1` | sibling `supplementary_equipotential_bonding` constraint |
| `pool_zone_0 / 1 / 2` | sibling `pool_main_equipotential_bonding` constraint |
| `sauna_zone_1` | heat-rated cable as zone field; 30 mA RCD-exempt-for-heater note per §703.411.3.3 |
| `sauna_zone_2 / 3` | 30 mA RCD on all circuits per §703.411.3.3 |
| `elv_barrier_zone` | sibling `elv_separation` constraint |
| `bath_*` zones in `is_wet_room: true` room | Zone 1 polygon spans full floor area |

### 5.3 `electrical_constraints[]` discriminated by `constraint_type` (6 values)

```
medical_it_system                        # §710 Group 2 only
supplementary_equipotential_bonding      # §701 + §710 Group 1
pool_main_equipotential_bonding          # §702.415.1 (verified)
whirlpool_pump_circuit                   # §701 + §701.512.2 IPx5 (whirlpool sub-clause not in verified file)
rcd_blanket_by_room                      # §701: 30 mA RCD on ALL circuits
elv_separation                           # §715
```

**Per-constraint common fields:** `constraint_type`, `applies_to_room_polygon: bool`, `applies_to_zone_ids: [string] | null`, `_clause_citation`, `_derivation_note`.

**Constraint-type-specific fields:**

```yaml
medical_it_system:
  isolating_transformer_va_min: int                        # typical 3.15-8 kVA (reviewer D-4)
  insulation_monitoring_device_required: bool              # IMD per BS EN 61557-8
  imd_alarm_response_time_s_max: int                       # 8 per BS EN 61557-8 (NOT 0.5 s — that was a prior misattribution)
  safety_service_category: 1 | 2 | 3                       # per HTM 06-01 NHS technical memorandum (NOT a BS 7671 sub-clause)
  supplementary_bonding_required: bool
  supplementary_bonding_max_resistance_ohm: 0.2            # per §710 verified-file body
  hospital_precedence: "HTM 06-01"                         # NHS-site mandatory cross-reference
  equipment_standard: "BS EN 60601 series"                 # medical equipment cross-reference
  _verified_cross_refs: ["BS EN 61557-8", "HTM 06-01", "BS EN 60601"]

supplementary_equipotential_bonding:
  metallic_parts_listed: [string]
  bonding_conductor_csa_min_mm2: number                    # typical 2.5 / 4 mm² per §701.415.2

pool_main_equipotential_bonding:
  extraneous_parts_listed: [string]                        # ladders, springboards, pipe fittings, pool surrounds, …
  conductor_csa_min_mm2: 10                                # per §702.415.1 (NOT §702.55.1 — that does not exist in verified file)

whirlpool_pump_circuit:
  pump_position_zone: string                               # zone_id where pump sits
  requires_local_isolation: bool
  ip_rating_min: "IPx5"                                    # per §701.512.2 (water jets clause)
  _whirlpool_general_citation: "BS 7671:2018 §701 (no sub-clause for whirlpools in verified file)"

rcd_blanket_by_room:
  rcd_rating_ma: 30                                        # per §701.411.3.3 (bathrooms) and §703.411.3.3 (saunas)
  applies_to_circuit_types: ["lighting", "sockets", "shower_unit", "fixed_equipment"]
  sauna_heater_excluded: bool                              # per §703.411.3.3 the heater circuit is exempt

elv_separation:
  lv_cable_spacing_mm_min: number
  barrier_required: bool
  label_required: bool
  transformer_short_circuit_protected: bool                # per BS EN 61558-2-6 (verified-file cross-reference)
  _elv_general_citation: "BS 7671:2018 §715 + BS EN 61558-2-6 (no §715 sub-clauses in verified file)"
```

### 5.4 `existing_fixtures_audit[]` (conditional)

Per-fixture-vs-zone analysis. **Populated only when `mode == full_analysis` AND fixture data exists** (from consumed intent OR `existing_fixtures[]` input). Empty otherwise.

```yaml
{
  fixture_id: string,
  fixture_type: string,                     # socket_230v / luminaire / isolator / etc.
  position_xyz: {x_mm, y_mm, z_mm},
  derived_zone_id: string | null,           # null if outside all zones
  compliance_status: "compliant" | "violation",
  violation_sub_rule: "type_prohibited" | "ip_below_min" | "voltage_above_max" | "switch_distance_too_close" | null,
  violation_clause: string | null,          # routed citation
  severity: "critical" | "high" | null
}
```

**Drift guard via INV-02:** every `compliance_status == "violation"` entry MUST have a corresponding `calculation_summary.non_compliance_flags[]` entry (one-to-one). Validator enforces.

### 5.5 `calculation_summary` (rollup)

```yaml
{
  compliant: boolean,                       # AND of (no zone overlaps unflagged, all required constraints present, all fixtures compliant)
  zone_count: int,
  constraint_count: int,
  violation_count_critical: int,
  violation_count_high: int,
  non_compliance_flags: [
    {flag, severity, fixture_id?, zone_id?, clause, message, _cascaded_from?}
  ],
  assumptions: [string],                    # e.g. "Whirlpool pump position defaulted to bath edge; IPx5 per BS 7671:2018 §701.512.2"
  _zone_derivation_engine: "auto_from_anchors_v1.0",
  _engineering_judgments: [string]          # reviewer flags surface here
}
```

### 5.6 Mode-conditional `allOf`

```yaml
allOf:
  - if: { properties: { mode: { const: "screening_only" } } }
    then: { not: { required: ["existing_fixtures_audit"] } }
    else: { required: ["existing_fixtures_audit", "electrical_constraints"] }

  - if: { ... medical_envelope_group_2 in zones[] ... }
    then: { ... medical_it_system in electrical_constraints[] ... }
    # (medical Group 2 IT system requirement enforced declaratively at schema level)
```

### 5.7 Geometry validation (schema-level)

- `boundary_plan_polygon_mm` items: minItems: 3
- `height_min_mm <= height_max_mm`
- Cylindrical zones: polygon ≥ 12-sided regular polygon centred on anchor; `_derivation_note` records approximation
- All distances in mm; no float epsilon problems with int-only fields where possible

### 5.8 INV evidence size budget

Per [[feedback-no-trim-non-consequential]] precedent (D.2 raised photometric's evidence maxLength 800→1200), special-locations IR `invariants[].evidence` will declare **`maxLength: 1200`** from v1.0 to avoid the same retrofit. Failure-mode INV-08 evidence carries fixture-id + zone-id + violation sub-rule + clause + remediation guidance — legitimately exceeds 800 chars on multi-violation cases.

---

## 6. Produced intent payload (`special-locations-zoning-intent.schema.json`)

**Flat shape, no envelope wrap** per the photometric-analysis precedent.

```yaml
{
  intent_version: "1.0.0",
  skill: "special-locations",
  consumed_lighting_layout_intent: "<path | null>",

  special_locations_zoning: {
    zones: [<full IR zone entries — compact fingerprints>],
    electrical_constraints: [<full IR constraint entries>],
    compliant: bool,
    zone_count: int,
    constraint_count: int,
    violation_count_critical: int,
    violation_count_high: int,
    non_compliance_flags: [{flag, severity, fixture_id?, zone_id?, clause, message, _cascaded_from: "special-locations"}],
    anchor_source_summary: {
      all_extracted: bool,                                    # true if every anchor came from architectural drawing
      extraction_source_lowest: "architectural_drawing_extraction" | "engineer_manual_entry" | "inferred_from_room_type"
    }
  }
}
```

**Six `consumed_fields` per consumer manifest:**
`zones`, `electrical_constraints`, `compliant`, `violation_count_critical`, `non_compliance_flags`, `anchor_source_summary`.

**Why consumers need the full `zones[]` array, not just a count:** consumer INV sub-check 3 (thin sanity cross-check) walks each consumer's own placed fixtures (`luminaires[]` / `sockets[]` / `boards[].outgoing_ways[]`) and asks "which zone does this sit inside?" That requires the actual polygon geometry, not just a count.

---

## 7. Validator INV catalogue (10 INVs)

Two-digit ids `INV-01..INV-10` matching IR schema regex `^INV-[0-9]{2,3}$`.

### 7.1 Structural / IR integrity (3 INVs, all HIGH)

**INV-01 — Anchor-zone catalogue integrity** | HIGH
Every `anchor_fixtures[]` entry produces ≥1 `zones[]` entry. Detected overlaps flagged via `overlapping_with_zone_ids[]` cross-references — no silent merges. Catches anchor-extraction round-trip bugs.

**INV-02 — Fixture-audit ↔ flags drift guard** | HIGH
Every `existing_fixtures_audit[i].compliance_status == "violation"` has a corresponding entry in `calculation_summary.non_compliance_flags[]` and vice versa. One-to-one enforced. Prevents drift between the two arrays.

**INV-10 — Compliant rollup self-consistency** | HIGH
`compliant == true` ⇒ `violation_count_critical == 0 AND non_compliance_flags is empty AND no zones marked overlapping`. Catches IR self-contradiction.

### 7.2 Compliance-required-by-context (5 INVs, all HIGH)

**INV-03 — §710 Group 2 → medical IT system mandatory** | HIGH
`medical_envelope_group_2` zone present ⇒ sibling `medical_it_system` constraint with `applies_to_zone_ids[]` containing the Group 2 zone id AND `imd_alarm_response_time_s_max == 8` AND `supplementary_bonding_max_resistance_ohm == 0.2`. Citation: `BS 7671:2018 §710` + `BS EN 61557-8` (IMD alarm response 8 s) + `HTM 06-01` (NHS precedence).

**INV-04 — §701 bathroom + §703 sauna → 30 mA RCD blanket** | HIGH
`room_type ∈ {bathroom, shower_room}` ⇒ `rcd_blanket_by_room` constraint with `rcd_rating_ma == 30` per `BS 7671:2018 §701.411.3.3`. `room_type == sauna` ⇒ same constraint with `sauna_heater_excluded: true` per `BS 7671:2018 §703.411.3.3` (heater circuit is exempt).

**INV-05 — §702 pool → main equipotential bonding** | HIGH
`room_type == swimming_pool_hall` ⇒ `pool_main_equipotential_bonding` constraint with `extraneous_parts_listed[]` non-empty AND `conductor_csa_min_mm2 >= 10`. Citation: `BS 7671:2018 §702.415.1` (NOT §702.55.1 — that does not exist in the verified file).

**INV-06 — Whirlpool bath → pump circuit constraint** | HIGH
`bath_basin` anchor with `bath_kind == whirlpool` ⇒ `whirlpool_pump_circuit` constraint with `pump_position_zone`, `requires_local_isolation: true`, `ip_rating_min >= IPx5`. Citation: `BS 7671:2018 §701` + `§701.512.2` (IPx5 where water jets used).

**INV-07 — ELV §715 anchor → separation constraint** | HIGH
`elv_lighting_circuit_anchor` ⇒ `elv_separation` constraint with `lv_cable_spacing_mm_min`, `barrier_required`, `label_required`, `transformer_short_circuit_protected: true`. Citation: `BS 7671:2018 §715` + `BS EN 61558-2-6` (transformer short-circuit protection).

### 7.3 Fixture-vs-zone compliance (1 INV, HIGH)

**INV-08 — Existing fixture placement compliance** | HIGH
For every fixture in consumed lighting-layout intent OR `existing_fixtures[]` input:
- (a) fixture type ∉ containing zone's `prohibited_fixture_types[]`
- (b) fixture `ip_rating` ≥ containing zone's `ip_rating_min`
- (c) fixture position respects `switch_position_min_distance_mm` if switch
- (d) fixture `max_voltage_v` ≤ containing zone's `max_voltage_v`

Each violation produces one `non_compliance_flags[]` entry + one `existing_fixtures_audit[]` entry. INV-08 is the **central engineering value** of the skill.

### 7.4 Provenance (1 INV, MEDIUM)

**INV-09 — Anchor extraction provenance disclosure** | MEDIUM
Every `_extraction_source` in 3-tier enum + every `_provenance_note` ≥40 chars. Honest-disclosure hygiene; preserves D2.3 lineage end-to-end.

### 7.5 Severity ladder summary

- **HIGH (9):** INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07, INV-08, INV-10
- **MEDIUM (1):** INV-09

Heavier on HIGH than photometric (7 HIGH + 2 MEDIUM) because Part 7 violations are safety-critical. Honest-disclosure stays MEDIUM (engineering hygiene, not safety).

---

## 8. Reviewer D-checks (5)

Judgment-layer checks beyond the deterministic INV catalogue. Findings → `flags[]` + optionally `calculation_summary.non_compliance_flags[]`.

**D-1 — Anchor-extraction confidence vs derivation criticality**
Anchor with `_extraction_source == "inferred_from_room_type"` driving a `medical_envelope_group_2` / `pool_zone_0` / `bath_zone_0` zone → flag for engineer re-verification.

**D-2 — §702 pool Zone 2 cross-room overlap**
`pool_zone_2` boundary within 200 mm of room polygon edge → check adjacent room's `pool_barrier_present` flag; flag if unknown (per §702.55.4).

**D-3 — Whirlpool pump position assumption**
`bath_kind == whirlpool` with no `whirlpool_pump_position` supplied → flag default-placement assumption (skill places pump at bath edge by §701 general convention; IPx5 required per `BS 7671:2018 §701.512.2`).

**D-4 — Medical Group 2 isolating-transformer VA plausibility**
`medical_it_system` constraint with `isolating_transformer_va_min < 3.15 kVA OR > 8 kVA` → flag possible under-/over-sizing (LIM threshold mis-tunes outside typical band, producing spurious alarms during procedures). Citation: `BS 7671:2018 §710` + `BS EN 61557-8` (IMD spec) + `HTM 06-01` (NHS technical memorandum).

**D-5 — §715 ELV external-installation thermal de-rating**
`room.is_external == true` AND `elv_lighting_circuit_anchor` present AND no `ambient_temperature_c` supplied → flag default 30°C assumption; direct engineer to BS 7671 Appendix 4 Table 4B1.

---

## 9. Examples (17 total: 8 standalone + 9 cascade)

### 9.1 Standalone (8)

| # | Example name | Jurisdiction | Section(s) | Demonstrates |
|---|---|---|---|---|
| 1 | `uk-bathroom-standard-bath-and-shower` | GB | §701 | Happy path — all 10 INVs PASS |
| 2 | `uk-bathroom-whirlpool-with-pump` | GB | §701 + §701.512.2 | INV-06 + D-3 reviewer flag (whirlpool IPx5 per water-jets clause) |
| 3 | `uk-shower-room-wet-room-floor` | GB | §701 (wet-room expansion per IET GN7 commentary; no §701 sub-clause in verified file) | Wet-room Zone 1 expansion |
| 4 | `uk-pool-hall-with-changing-room-adjacency` | GB | §702 + §702.415.1 + §702.55.4 | D-2 reviewer flag + ≥10 mm² main bonding |
| 5 | `uk-sauna-with-3-zone-derivation` | GB | §703 + §703.411.3.3 | 3-zone sauna split (zone_1 heater + zone_2 sauna body + zone_3 above 1.5 m); RCD blanket with heater exemption |
| 6 | `uk-medical-or-group-2-with-it-system` | GB | §710 + BS EN 61557-8 + HTM 06-01 | Full medical_it_system constraint (IMD 8 s alarm response + 0.2Ω supplementary bonding) |
| 7 | `uk-medical-ward-group-1-bonding` | GB | §710 + §701.415.2 | supplementary_equipotential_bonding |
| 8 | `uk-external-landscape-elv-lighting` | GB | §715 + BS EN 61558-2-6 + BS 7671 §522 IP | D-5 reviewer flag + elv_separation + transformer short-circuit protection |

### 9.2 Cascade (9)

| # | Cascade dir | Consumer | Source anchor | Pass/Fail |
|---|---|---|---|---|
| 9 | `cascade-lighting-layout-uk-bathroom` | lighting-layout v1.6 | Example 1 | PASS |
| 10 | `cascade-lighting-layout-uk-pool-hall` | lighting-layout v1.6 | Example 4 | PASS |
| 11 | `cascade-lighting-layout-uk-medical-group-2` | lighting-layout v1.6 | Example 6 | PASS |
| 12 | `cascade-small-power-uk-bathroom-violation` | small-power v1.2 | Example 1 + 230V socket in Zone 1 | **FAIL HIGH** — INV-08 + INV-12 cascade |
| 13 | `cascade-small-power-uk-medical-group-2-isolation` | small-power v1.2 | Example 6 | PASS |
| 14 | `cascade-small-power-uk-external-elv-with-violation` | small-power v1.2 | Example 8 + LV socket in ELV barrier zone | **FAIL HIGH** — INV-07 + INV-08 + INV-12 cascade |
| 15 | `cascade-db-layout-uk-bathroom-rcd-enforcement` | db-layout v1.5 | Example 1 | PASS — INV-04 → INV-16 cascade |
| 16 | `cascade-db-layout-uk-medical-group-2-it-distribution` | db-layout v1.5 | Example 6 | PASS — IT panel + ME terminal modelled |
| 17 | `cascade-multi-jurisdiction-ke-bathroom-route-to-bs` | lighting-layout v1.6 | KE jurisdiction | PASS — KS 1700 §313 routing |

### 9.3 Jurisdiction coverage

- **GB:** 16 examples (covers all 5 sections × 3 consumers + failure modes)
- **KE:** 1 example (#17) — demonstrates KS 1700 §313 → BS 7671 routing
- **INT:** 0 examples in v1.0 — citation routing supported by emitting IEC 60364-7-XXX clauses; full INT examples deferred to v1.1 (per `[[build-strategy-breadth-first]]`)

### 9.4 Failure-mode demonstrations (3)

- #12 — 230V socket in Zone 1 (central engineering value test)
- #14 — LV socket in ELV barrier zone (§715 separation)
- INV-03 enforces Group 2 IT system structurally (no cascade-emission failure example needed)

---

## 10. Cascade contracts (3 consumers)

Each consumer gets 3-part wiring: (a) IR schema `consumed_intents` + 2nd `allOf` clause, (b) manifest `consumes_intents[]` entry, (c) new INV in `prompts/validator.md`.

### 10.1 Cascade A — `lighting-layout` v1.5.0 → v1.6.0

**Trigger:** `mode == 'full_drawing' AND room.room_type IN [bathroom, shower_room, swimming_pool_hall, sauna, medical_*, external_landscape]`

**Consumed fields:** 6 standard fields (`zones`, `electrical_constraints`, `compliant`, `violation_count_critical`, `non_compliance_flags`, `anchor_source_summary`).

**INV-12 — Special-locations zoning cascade resolved** | HIGH (4 sub-checks):
1. `consumed_intents.special_locations_zoning` present
2. `payload.compliant == true`
3. Thin sanity cross-check: walk `luminaires[]`; for each, find containing zone; verify (a) luminaire type ∉ zone.prohibited_fixture_types, (b) luminaire IP rating ≥ zone.ip_rating_min, (c) luminaire max_voltage_v ≤ zone.max_voltage_v
4. Flag propagation with `_cascaded_from: "special-locations"`

### 10.2 Cascade B — `small-power` v1.1.0 → v1.2.0 (cascade-wiring only)

**Trigger:** `mode == 'full_drawing' AND room.room_type IN [...same set...]`

**Consumed fields:** same 6.

**INV-12 — Special-locations zoning cascade resolved** | HIGH (4 sub-checks):
1. Same as A
2. Same as A
3. Thin sanity cross-check: walk `sockets[] + isolators[] + connection_points[]`; specifically catches:
   - 230V socket in bath_zone_1 / bath_zone_2 (≥3 m boundary rule per `BS 7671:2018 §701.512.3`)
   - Shaver socket missing BS EN 61558-2-5 compliance flag
   - Pump/heater isolator outside local-isolation reach (`BS 7671:2018 §701` + `§710` medical equipment isolation)
4. Same flag propagation as A

**Important scope distinction:** This task wires the **cascade only** at v1.2.0. The full **D4 depth engineering content** (PVC/SWA tables, building-level diversity, EV-charge consumption per §722) is a separate Wave 2 sprint that brings small-power to v1.2.x via additional minor bumps.

### 10.3 Cascade C — `db-layout` v1.4.0 → v1.5.0

**Trigger:** any room in upstream lighting-layout's `room_adjacency_graph` matches `room_type IN [...same set...]`. (db-layout has no `mode` field — trigger fires whenever a downstream room demands it.)

**Consumed fields:** 4 of 6 (`electrical_constraints` primary; `compliant`, `non_compliance_flags`, `anchor_source_summary`). Excludes `zones[]` array (not relevant to circuit-level concerns) + `violation_count_critical` (already covered by flag set).

**INV-16 — Special-locations distribution cascade resolved** | HIGH (4 sub-checks):
1. `consumed_intents.special_locations_zoning` present
2. `payload.compliant == true`
3. Thin sanity cross-check: walk `boards[].outgoing_ways[]`; verify:
   - 30 mA RCD present if `rcd_blanket_by_room` constraint
   - Circuit routed via Medical IT panel if `medical_it_system` constraint
   - Supplementary bonding terminal modelled if `supplementary_equipotential_bonding` constraint
   - Main equipotential bond ≥10 mm² at ME terminal if `pool_main_equipotential_bonding` constraint
4. Same flag propagation pattern (`_cascaded_from`)

### 10.4 Cascade wiring summary

| Consumer | Version bump | New INV | Sub-check 3 iterates | Trigger |
|---|---|---|---|---|
| lighting-layout | 1.5→1.6 | INV-12 | `luminaires[]` | `mode==full_drawing AND room IN Part7-set` |
| small-power | 1.1→1.2 | INV-12 | `sockets[]+isolators[]+connection_points[]` | `mode==full_drawing AND room IN Part7-set` |
| db-layout | 1.4→1.5 | INV-16 | `boards[].outgoing_ways[]` | `adjacency.any_room IN Part7-set` |

### 10.5 Wave 2 plan re-scoping (consequence)

The cluster roadmap §5 originally placed `small-power v1.2.0 D4` + `lighting-layout v1.5.0 extensions` in Wave 2. Wiring 3 cascades into special-locations v1.0 shifts:

| Wave 2 item | Original | Updated |
|---|---|---|
| small-power v1.2.x | Full D4 depth + cascade wiring | D4 depth engineering content ONLY (cascade wired in Wave 1 special-locations sprint) |
| lighting-layout v1.6.x | task/ambient split + 3D placement + cascade wiring | task/ambient split + 3D placement ONLY (cascade wired in Wave 1) |
| db-layout v1.5.x | Not previously planned for Wave 2 | Cascade-wiring done in Wave 1; future depth in unscheduled later sprint |

Wave 2 stays parallel-pair-shaped; the cascade-wiring offload makes Wave 2 lighter, not heavier.

---

## 11. Sprint shape

### 11.1 Phase A — Foundations (4 tasks)

| Task | Model | Description |
|---|---|---|
| A.1 | Sonnet | Skill scaffolding — folder + manifest stub→production + README + CHANGELOG |
| A.2 | Sonnet | IR + intent schemas — 10-property IR + flat intent + mode-conditional allOf |
| A.3 | Sonnet | inputs.json + 3 rules YAML files (zone-derivation + constraint-required-by-context + provenance-disclosure) |
| A.4 | Opus | Shared zone-derivation library at `shared/special-locations/zone-derivation/` — Python stdlib (bath/pool/sauna/medical/elv geometry); reference impl for unit tests; no runtime tool contract (skill IS the contract) |

### 11.2 Phase B — Prompts (3 tasks, all Opus)

| Task | Model | Description |
|---|---|---|
| B.1 | Opus | Generator prompt (~280 lines, Step 0 cascade-prereq + 12 numbered steps) |
| B.2 | Opus | Validator prompt (~310 lines, full 10-INV catalogue) |
| B.3 | Opus | Reviewer prompt (~180 lines, 5 D-checks) |

### 11.3 Phase C — Examples + evals (3 tasks)

| Task | Model | Description |
|---|---|---|
| C.1 | Opus | 8 standalone examples per §9.1 table |
| C.2 | Opus | 9 cascade examples per §9.2 table (includes KE jurisdiction in #17) |
| C.3 | Sonnet | 7 evals YAML (categories: skill_specific × 4, validation_trap × 2, compliance_failure × 1; canonical 9-value enum) |

### 11.4 Phase D — Cascade integration ×3 + ship (6 tasks)

| Task | Model | Description |
|---|---|---|
| D.1 | Sonnet | lighting-layout v1.6.0 wiring — schema + manifest + INV-12 |
| D.2 | Opus | lighting-layout examples retrofit (~5-7 examples touching Part-7 room types) |
| D.3 | Sonnet | small-power v1.2.0 cascade-wiring — schema + manifest + INV-12 |
| D.4 | Opus | small-power examples retrofit (~5-7 examples) |
| D.5 | Sonnet | db-layout v1.5.0 cascade-wiring — schema + manifest + INV-16 |
| D.6 | Sonnet + Opus | db-layout examples retrofit (~3-4 examples) + Sprint ship (11-check fence + 3 CHANGELOGs + memory + push) |

**Total: 16 implementer tasks** (4 + 3 + 3 + 6). Plus ~5-7 fix-pass commits expected per `[[sprint-D3-shipped]]` history (10/11 D3 tasks needed fix-passes). Estimated **23-25 commits** total.

### 11.5 Process discipline (locked, mirrors photometric-analysis)

- Sonnet for mechanical (scaffolding, schemas, manifests, eval YAML, cascade wiring) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (geometry library, prompts, all examples, retrofits, all reviews)
- Two-stage Opus review after every implementer task — fix-pass commit when HIGH/CRITICAL findings surface
- **Cross-check plan-template citations against `shared/standards/electrical/BS7671/part7-special-locations.json` BEFORE implementer copies** (locked lesson from `[[sprint-D2-shipped]]` Reg 559 + photometric §714 catches — already applied at this brainstorm in §2)
- Pre-ship Sonnet 11-check verification fence
- Final cross-sprint Opus integration review before push
- Push deferred to user authorisation per CLAUDE.md "shared state" rule

---

## 12. Honest disclosures

### 12.1 Verification status discipline (mirrors photometric)

- All anchor inputs flagged with `_extraction_source` in 3-tier enum (architectural_drawing_extraction → engineer_manual_entry → inferred_from_room_type, strongest to weakest)
- `_provenance_note` ≥40 chars per anchor — enforced by INV-09
- Reviewer D-1 catches the "weak provenance + safety-critical zone" combination

### 12.2 Standards citation hygiene

- §714 / §753 explicitly NOT cited (do not exist in BS 7671:2018+A2:2022 per verified standards file)
- Every `_clause_citation` carries jurisdiction-routed form per §4.3
- KE jurisdiction uses explicit "KS 1700:2018 §313 (route to BS 7671 §X)" form per CLAUDE.md
- INT jurisdiction uses "IEC 60364-7-XXX § Y" form
- No "see Reg 559" or similar misattribution allowed (lesson from D2.3)

### 12.3 Scope boundaries declared

- MRI rooms NOT in scope at v1.0 (separate standards stack: IEC 60601-1 + Faraday cage). Declared in README + manifest `_v1_limitations`.
- US NEC parallel (Article 680 pools, 517 healthcare) NOT in scope — separate sibling skill when first US project requirement lands.
- INT jurisdiction worked examples NOT in scope at v1.0 (citation routing supported; full examples in v1.1).
- §722 EV charging NOT in scope at v1.0 (intersects with EV-Charge skill; defer until that skill matures).
- Embedded heating NOT in scope at v1.0 (no §753 in BS 7671; v1.1 candidate via §415 + §522 routing).

### 12.4 Runtime boundary preserved

Per `[[runtime-project-boundary]]`: this repo ships the IR contract + intent schema + reference Python zone-derivation library. The actual runtime executor that reads architectural drawings + extracts anchors + dispatches the skill DAG lives in the separate runtime project. Anchor input is the contract boundary.

---

## 13. v1.1 + v2.0 deferrals (declared)

### v1.1 candidates (12-18 months out)

| Item | Trigger to build |
|---|---|
| §722 EV charging coverage | When EV-Charge skill matures + first EV project demands it |
| §704 construction sites | First construction-site project |
| §708 caravan parks / §709 marinas | Niche-project-driven |
| Embedded heating via §415 + §522 | First underfloor-heating project |
| INT jurisdiction full examples | First INT project |

### v2.0 candidates

| Item | Trigger |
|---|---|
| §710 Group 2 split into `medical-electrical/` sibling | If medical_it_system grows beyond 1 `electrical_constraints[]` block |
| MRI room sub-skill | First MRI project |
| US NEC parallel sibling (`special-locations-us/`) | First US project |
| Anchor extraction from native IFC | Runtime BIM-direct support |

---

## 14. Cross-references

- Spec predecessor: `2026-05-30-photometric-analysis-design.md` (Wave 1 first deliverable)
- Cluster roadmap: `2026-05-29-lighting-cluster-roadmap.md` §3.4 + §6.4
- Standards source (verified): `shared/standards/electrical/BS7671/part7-special-locations.json`
- Pattern parent (calc primitive): `electrical/photometric-analysis/`
- Pattern parent (cascade consumer): `electrical/lighting-layout/`
- Cascade DSL precedent: `electrical/cable-sizing/` consumes_intents pattern + photometric-analysis 3-layer wiring
- Memory cross-refs: `[[photometric-analysis-shipped]]`, `[[sprint-D3-shipped]]`, `[[sprint-D2-shipped]]`, `[[runtime-project-boundary]]`, `[[feedback-no-haiku-sonnet-opus-only]]`, `[[feedback-no-trim-non-consequential]]`, `[[build-strategy-breadth-first]]`

---

## 15. Next action

After user approval of this spec:

1. Invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-06-01-special-locations-sprint.md`.
2. Plan portions 1-4 committed sequentially (matches photometric portion-by-portion pattern).
3. Sprint execution via `superpowers:subagent-driven-development` — 16 implementer tasks across 4 phases.

Estimated commit count: 23-25. Estimated wall-clock: comparable to photometric (~one session of focused execution).

After ship: Wave 1 complete. Cluster roadmap Wave 2 begins (`small-power v1.2.x D4 depth` + `lighting-layout v1.6.x extensions`).
