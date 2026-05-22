# Cable-Sizing Skill — Design Refresh (2026-05-20)

**Date:** 2026-05-20
**Status:** Approved — ready for implementation plan
**Target:** `electrical/cable-sizing` v1.0.0 beta
**Base spec:** `docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md` (commit c47a077)
**Refresh scope:** 3 deltas locked in 2026-05-20 brainstorming — everything else inherits from base

---

## 0. Why this refresh

The 2026-05-16 base spec is structurally sound and approved. Four sprints have shipped since (SLD v1.4 / v1.5 / drafting standards v1.6 / small-power v1.0), and 3 specific drift points emerged that need to be captured before the implementation plan is written:

1. **small-power v1.0 ships with `tool_call_pending_for_zs_verification: true` on every circuit** — cable-sizing intent now has a 4th natural downstream consumer that the base spec does not enumerate
2. **The intent contract should carry Zs-resolution helper fields** (`r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m`) so the small-power consumer can resolve those pending Zs flags by table lookup rather than rerunning ampacity
3. **The Africa-first 4-jurisdiction pattern** (earthing v1.4 / small-power v1.0 / db-layout v1.3 all ship 4-jurisdiction examples) now requires a KE example for cable-sizing v1.0

This refresh document is a delta. The 14-step generator, 10-INV validator, 8-D reviewer, walk-the-ladder algorithm, project-scoped cascade IR, 22-standards-file consumption list, 3 calc contracts, 5 rules / 4 constraints / 4 validation YAMLs, 9 evals, manifest shape, versioning policy, and all out-of-scope items are inherited verbatim from the 2026-05-16 base spec.

---

## 1. Delta 1 — Intent schema: Zs-resolution helper fields

**Section affected:** Base spec §4.3 (Output intent — slim downstream subset).

**Add two new fields per circuit** to `cable-sizing-intent.schema.json`:

```json
{
  "node_id": "MSB-1.F03.DB-L1.C07",
  "designation": "Lighting circuit L1-C07",
  "phase_csa_mm2_or_awg": "2.5 mm²",
  "cpc_csa_mm2_or_awg": "1.5 mm²",
  "material": "copper",
  "insulation": "pvc_70",
  "cable_type": "pvc_singles",
  "parallel_count": 1,
  "cable_od_mm": 8.4,
  "weight_kg_per_m": 0.18,
  "length_m": 32,
  "installation_method": "B1",
  "parent_node_id": "MSB-1.F03.DB-L1",
  "r1_plus_r2_milliohm_per_m_at_operating_temp": 14.4,
  "reactance_milliohm_per_m": 0.08
}
```

### 1.1 Field semantics

| Field | Unit | Source | Notes |
|---|---|---|---|
| `r1_plus_r2_milliohm_per_m_at_operating_temp` | mΩ/m | Lookup table (jurisdiction-specific) | Combined phase + CPC resistance per metre at the cable's *operating* temperature (PVC 70°C / XLPE 90°C / MICC 90°C). Reads from `BS 7671:2018 App 4 Tables 4F1–4F3` (GB) / `IEC 60364-5-52 Table B.52.5` (INT) / `NEC Chapter 9 Table 9` (US). |
| `reactance_milliohm_per_m` | mΩ/m | Lookup table (jurisdiction-specific) | Cable reactance per metre. Same source tables. Negligible (<0.1 mΩ/m) for small csa ≤16 mm² but material above 25 mm². |

### 1.2 Operating-temperature choice rule

The selected operating temperature is determined by the cable's `insulation` field:

| `insulation` value | Operating temp |
|---|---|
| `pvc_70` | 70°C |
| `xlpe_90`, `epr_90` | 90°C |
| `mineral_micc_90` | 90°C |
| `fp200_90`, `cwz_90` | 90°C |
| `thwn_2_90`, `thhn_90`, `xhhw_2_90` (US NEC) | 90°C |

The intent emits the value at the cable's chosen operating temp — no need for the consumer to apply a temperature correction itself. The lookup happens during cable-sizing's Step 12 (cable physical data lookup) and rides through unchanged.

### 1.3 Why this shape (rationale)

- **Data-natural:** Matches the published table form in BS 7671 / IEC 60364-5-52 / NEC Chapter 9 exactly — no pre-multiplication, no information loss
- **Reusable:** Any downstream skill that needs to resolve a Zs, a voltage drop, or an impedance calc can use these two fields with its own length value
- **Decoupled from length:** Pre-multiplying by `length_m` would lock the value at intent-emit time and create a dual-source-of-truth risk if a consumer tracks its own length differently
- **No new tool calls:** All values come from existing standards tables that cable-sizing already loads in Step 6 (cable ampacity lookup); negligible runtime cost

### 1.4 Schema diff

Update `cable-sizing-intent.schema.json` `circuits[].items.properties` to add the two fields. Both fields are **required on every circuit** in the intent — populated from the standards tables based on the circuit's selected `phase_csa_mm2_or_awg` + `cpc_csa_mm2_or_awg` + `insulation` + `material`. The lookup runs unconditionally during cable-sizing's existing Step 12 (cable physical data lookup) — whether the csa was chosen by walk-the-ladder or pre-declared by the engineer.

---

## 2. Delta 2 — Cross-skill contract: add small-power as 4th consumer

**Section affected:** Base spec §12 (Cross-skill contract verification).

Bump the downstream consumer table from 3 entries to 4:

| Downstream skill | Consumes for | Required fields from `cable-sizing` intent |
|---|---|---|
| `cable-schedule` (unchanged) | Formal tabulated deliverable | Full per-circuit set: csa, type, length, designation, OCPD ref |
| `riser` (unchanged) | LV riser diagrams floor-by-floor | Feeder-level + `parent_node_id` for parent-child rendering |
| `cable-containment` (unchanged) | Tray/conduit fill calculations | `cable_od_mm`, `weight_kg_per_m`, `parallel_count` per segment |
| **`small-power` (NEW — v1.1 migration target)** | Resolve `TOOL-CALL-PENDING:calc.zs_loop_impedance` flags on every small-power circuit | `phase_csa_mm2_or_awg` + `cpc_csa_mm2_or_awg` + `length_m` + `insulation` + `parent_node_id` + `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` |

**Forward-compatibility contract:**

- Cable-sizing v1.0 ships the union superset (all 4 consumers' fields present in every emitted intent)
- Small-power v1.0 is leaf (`consumes_intents: []`) and ignores cable-sizing intent for now
- Small-power v1.1 migration consumes the slim subset above and replaces its `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag with a resolved `verified_zs_ohm` value per circuit
- Pattern parent: SLD v1.3 (leaf) → v1.4 (multi-skill consumer) migration

**Validation:**

The existing `validation/intent-shape.yaml` (4 checks in base spec §3) is extended to assert the new 2 fields are present whenever `phase_csa_mm2_or_awg` is populated. No new validation YAML file needed.

---

## 3. Delta 3 — Add KE worked example (3 → 4)

**Section affected:** Base spec §10 (Worked examples).

Bump from 3 examples to 4. Add a new KE example between the UK and INT examples:

| Example | Demonstrates |
|---|---|
| `uk-domestic-final-circuits/` (unchanged) | 230V single-phase domestic, copper PVC, 1.5–10 mm², lighting + power radial + 32A ring. Vd binding on lighting circuits. |
| **`ke-nairobi-commercial-with-msb/` (NEW)** | 415V TPN KPLC TN-S supply per **KS 1700:2018 §313** routing to BS 7671. 60–200 m² Nairobi commercial office: MSB (315A incoming) → sub-DB (Lighting + Small-Power + HVAC) → final circuits. Cumulative Vd binding on a 45 m sub-DB feeder. All citations lead with `KS 1700:2018 §X` — never bare `BS 7671` and never the forbidden `"adopted by KS 1700"` annotation. |
| `intl-commercial-with-feeders/` (unchanged) | 400V TPN: TX → MSB → riser → DB-L1 → final circuits. Cumulative Vd, XLPE feeders, copper. Cumulative-Vd binding on a long final circuit. |
| `us-industrial-with-motors/` (unchanged) | 480V industrial: aluminium feeder + AWG sizing + 500 hp motor with starting-Vd check + parallel cables for 1200A service entrance. |

### 3.1 KE example engineering scenario

- **Supply:** 415V TPN+E, KPLC TN-S declared, Ze ≈ 0.45 Ω, declared PFC at MSB busbar ≈ 9 kA
- **Cascade:** Service entrance → MSB-1 (315A 4-pole MCCB) → 3× sub-DB feeders (DB-L1 lighting + DB-P1 small-power + DB-M1 HVAC) → final circuits
- **Notable cable runs:**
  - 35 m MSB-to-DB-P1 sub-feeder (4-core 25 mm² XLPE Cu, 80A MCCB) — cumulative-Vd binding when summed with downstream
  - 45 m DB-P1 to remote small-power final circuit (2-core 4 mm² PVC Cu, 20A MCB) — Vd binding at end of run
  - 18 m DB-M1 to small chiller pump (4-core 6 mm² XLPE Cu, 32A MCB with motor-starting Vd dip check)
- **Citation form audit:** All standards references use `KS 1700:2018 §X` primary form; routing notes use `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y` explicit form (matches small-power v1.0 KE example convention shipped 2026-05-19)
- **Drafting standards consumption:** sheet_size=A1, drawing_scale=1:50, drawing_standard="BS 1192:2007+A2:2016" (KE convention adopting UK BS standards, per drafting standards v1.6 layer)

### 3.2 File count

KE example adds 4 files: `input.json` + `output.json` + `intent-out.json` + `reasoning.md`. Total skill file count goes from ~50 (base spec) to ~54.

---

## 4. Sections unchanged from base spec

Everything in the 2026-05-16 base spec that this refresh does NOT touch ships verbatim. For completeness, the inherited scope is:

- **§1 Overview** — drawing_type, version, status, pattern parent
- **§2 Scope** — 5 jurisdictions, copper + aluminium, IEC + AWG, all 10 installation methods, 4 extra checks
- **§3 File structure** — file tree (with KE example folder added)
- **§4.1 Inputs (hybrid mode)** — db-layout-rollup + fault-level consumption + engineer-declared overlay
- **§4.2 IR shape** — project-scoped cascade tree per node
- **§5 CSA-selection algorithm** — walk-the-ladder + binding-constraint trail
- **§6 Extra engineering checks** — cumulative Vd, motor-starting Vd, parallel cables, harmonic derating
- **§7 Prompts** — 14-step generator / 10 INV validator / 8 D reviewer
- **§8 Rules / Constraints / Validation** — 5 + 4 + 4 YAMLs (12 checks total)
- **§9 Evals** — 9 evals (6 WI5 + 3 skill-specific). Eval-09 `intent-shape.yaml` already covers per-circuit intent field presence; the 2 new helper fields fall under its existing assertion pattern (extend the 2 added field assertions to its checks[] array)
- **§11 Manifest** — 22 standards files + 3 calc contracts referenced
- **§13 Known limitations** — DC scope deferred, IEC 60287 advanced thermal deferred, comms/data cables deferred, time-graded protection coordination deferred
- **§14 Versioning policy** — minor / major / patch bump rules

---

## 5. Approval

Approved by user 2026-05-20 (3 deltas locked via brainstorming dialogue). Ready for implementation plan.

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-20-cable-sizing-skill-sprint.md` covering the merged scope (base spec + this refresh).

The implementation plan is expected to deliver:

- ~54 files under `electrical/cable-sizing/`
- 4 jurisdictional worked examples (UK + KE + INT + US)
- IR schema + intent schema (with Zs-resolution helper fields)
- 14-step generator + 10-INV validator + 8-D reviewer prompts
- 5 rules + 4 constraints + 4 validation YAMLs
- 9 evals
- Manifest declaring multi-skill consumption (`db-layout-rollup` + `fault-level`) + intent production (`cable-sizing`)
- SKILLS_STATUS + ARCHITECTURE updates
- Production commit cadence (one task = one commit + per-task two-stage review)
