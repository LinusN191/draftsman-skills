# Lighting Cluster Build Plan — Roadmap Skeleton

**Date:** 2026-05-29
**Status:** SKELETON — each companion skill below requires its own brainstorm → plan → execute cycle per CLAUDE.md sprint workflow. This document captures the cluster-level decisions + per-skill briefs + sequencing.
**Predecessor:** Sprint D3 (lighting-layout depth) shipped 2026-05-29 via `sprint-D3-shipped` tag, commit `634eee5`. See `[[sprint-D3-shipped]]`.
**Successor:** 6 companion-skill spec docs + 1 in-skill extension spec (deferred to per-skill brainstorm sessions).

---

## 1. Why this cluster exists

D3 closed the bad-CAD-output bugs and made lighting-layout production-ready for **average-illuminance interior layouts**. But the user's maturity audit surfaced 10 dimensions that lighting-layout does NOT cover. Of those 10:

- **6 are companion skills** (independent engineering identity + own standards stack + cross-skill applicability)
- **2 are in-skill extensions** (tightly coupled to layout geometry)
- **1 is runtime-only** (DXF/SVG/PDF rasterisation per `[[runtime-project-boundary]]`)
- **1 is a dependency** of multiple companions (point-grid is the calc primitive)

This roadmap names them, classifies them, sets the build order, and pre-locks the enforcement machinery so lighting-layout *cannot ship a layout for a real project without invoking the right companions*.

## 2. Cluster-level architecture decisions (lock before any per-skill brainstorm)

### 2.1 Companion invocation enforcement (4-layer)

Already operational in the repo for cable-sizing → db-layout-rollup dependency. Re-use the pattern:

| Layer | Mechanism | Where it lives |
|---|---|---|
| 1 — Manifest | `consumes_intents[]` array with `{name, version_pin, trigger}` per companion | `electrical/lighting-layout/skill.manifest.json` |
| 2 — IR validator | HIGH-severity INVs (INV-11..15) that fail when triggered companion intent is absent | `prompts/validator.md` |
| 3 — Discovery cascade | `cascades_to` field on inputs.json questions that fan out to the companion's interview | `inputs.json` |
| 4 — Reviewer | D-7..D-12 D-checks confirming companion results are integrated, not just present | `prompts/reviewer.md` |

Pattern parent: `electrical/cable-sizing/skill.manifest.json` (declares db-layout-rollup + fault-level consumption) + `electrical/small-power/v1.1` (cascade pattern for Zs resolution).

### 2.2 Shared calc primitive — `calc.lumen_grid_solver`

Three companions (lighting-photometric, emergency-lighting, daylight) all need a point-grid illuminance computation. Build it **once** as a calc contract under `shared/calculations/lighting/lumen-grid-solver.json` (the contract stub already exists per [[runtime-project-boundary]]; back-port the full I/O spec from D3.B.1 Step 6.5 generator content).

Avoid the cable-sizing duplication where 3 calc contracts were authored per consumer. Reused calc, distinct skill-level wrappers.

### 2.3 Intent payload naming convention

Per the lessons of A.3 (`circuits` vs `circuits_topology` name collision) — every companion's intent declares fields under a clearly-namespaced prefix. Lock now:

- `lighting-photometric.intent` → `photometric_grid.*`
- `emergency-lighting.intent` → `emergency_coverage.*`
- `daylight.intent` → `daylight_model.*`
- `electrical-special-locations.intent` → `part7_zones.*`
- `lighting-controls.intent` → `controls_program.*`
- `energy-leni.intent` → `leni_result.*`

Lighting-layout's IR consumes each via `consumed_intents.{prefix}` — zero name collisions across the cluster.

### 2.4 Citation hygiene — locked from day one

Apply the D2.3 Reg 559 + D3 §714 lessons:

- Every clause cite in every companion plan-template **cross-checked against `shared/standards/electrical/` BEFORE plan ships**.
- Where a standard is repo-stub (BS 5266, BS EN 17037, IEC 62386, etc.) — explicit `_note` honest disclosure per the D3 pattern.
- No fabricated citations. Where a value is industry-typical not pinpoint-clauseable, mark `verification_status: engineer_typical_C2` and disclose.

### 2.5 Two-stage Opus review per task — pattern held

D3 had 10/11 tasks needing a fix-pass commit after two-stage review. The pattern caught real defects (Reg 559, schema-vs-prompt coord conflict, multi-entrance switch inconsistency, etc.) and is worth keeping. Each companion skill build runs the same per-task review discipline.

## 3. Companion skill briefs (6)

Each section below is a SKELETON for the per-skill brainstorm to expand. Open questions are flagged explicitly so the brainstorm session has clear starting points.

### 3.1 `lighting-photometric` — point-grid + U₀ + UGR

**Standards stack:** CIBSE LG7 §6 + BS EN 12464-1:2021 §4.4 (uniformity U₀) + CIE 117 (UGR formula) + IES LM-79 (luminaire photometric data exchange).

**Inputs (high-level):**
- Room geometry (from lighting-layout intent)
- Luminaire photometric data (from lighting-layout's ontology OR per-input override)
- Task plane height (room-type-dependent per spacing-rules#working-plane-defaults)
- Viewing positions for UGR (default centre-of-room facing each wall + 4 oblique angles)
- Calculation grid resolution (default 500 mm)

**Outputs (intent payload — `photometric_grid.*`):**
- `point_grid_result`: array of (x_mm, y_mm, illuminance_lux) at task plane
- `uniformity_u0`: number 0..1 (E_min / E_avg)
- `uniformity_u1`: number 0..1 (E_min / E_max)
- `ugr_per_view_position`: array of {view_x, view_y, view_direction, ugr_value}
- `_calc_method`: `lumen_method_simplified | full_point_grid`
- Honest disclosure if simplified vs full

**Consumes:**
- `lighting-layout.intent` (luminaire positions + types + room)

**Triggers lighting-layout INV-11.**

**Open questions for per-skill brainstorm:**
- Grid resolution policy (500 mm default vs adaptive)?
- UGR view-position heuristic vs explicit input?
- IES file ingestion path (parse LM-63 .ies → ontology override)?
- Photometric-data verification status (mark `pending_runtime_ies_parser` when input is generic vs manufacturer file)?
- Output shape: 2D array vs flat list? Renderer + downstream consumer impact.

**Why this companion first:** unblocks INV-11 + is consumed by emergency-lighting + daylight. Highest-leverage build.

---

### 3.2 `emergency-lighting` — BS 5266-1 escape + anti-panic + high-risk

**Standards stack:** BS 5266-1:2016 + BS EN 1838:2013 + BS EN 62034:2012 (automatic test systems) + Approved Document B (fire safety).

**Inputs (high-level):**
- Room geometry + circulation routes (escape route polygon set)
- Building occupancy class (office / assembly / industrial / healthcare)
- Required durations (3h default offices, 1h reduced-evacuation)
- Existing emergency luminaires from lighting-layout (if any — Z4 emergency zone)
- Test regime preference (self-test DALI vs manual log)

**Outputs (intent payload — `emergency_coverage.*`):**
- `escape_route_coverage`: array of {route_id, min_lux_centre_line, achieves_1lux_min, uniformity_ratio}
- `open_area_coverage`: floor coverage map vs 0.5 lux + 40:1 uniformity
- `high_risk_task_coverage`: per-task-area lux + uniformity
- `emergency_luminaire_schedule`: complete count + positions + circuits + battery type
- `test_regime`: self-test | manual + monthly + annual schedule
- `non_coverage_flags[]`: areas below minimum with honest deficit values

**Consumes:**
- `lighting-layout.intent` (general lighting positions for daylight-failure scenario calc)
- `lighting-photometric.intent` (point-grid calc engine)

**Triggers lighting-layout INV-12.**

**Open questions for per-skill brainstorm:**
- Escape route polygon input — engineer draws or auto-derive from room geometry + entrance positions?
- Battery type ontology (central battery vs self-contained vs hybrid)?
- BS 5266 stub directory build alongside (or rely on published standard with honest disclosure)?
- BS EN 1838 exit sign placement separate output or part of this skill?
- Failure mode if no escape route declared in non-trivial space — block or flag?

**Engineering note:** D3 warehouse anti-panic example was honestly disclosed as coverage-count-sized-not-point-grid-verified. This skill closes that honest-debt.

---

### 3.3 `daylight` — DF + sDA + ASE + Part L LENI input

**Standards stack:** BS EN 17037:2018 (daylight in buildings) + Approved Document L (Part L 2021) §6 LENI methodology + BREEAM HEA-01 (daylighting) + CIBSE LG10 (daylight design) + LEED IEQc7.

**Inputs (high-level):**
- Building geometry + orientation (extends well beyond single-room scope)
- Glazing positions + sizes + visible light transmittance
- External obstructions (other buildings, trees)
- Climate file (sky model — typically CIE Standard Overcast Sky for DF; climate-based for sDA/ASE)
- Internal reflectances per room
- Target daylight metrics per BREEAM/LEED/Part L

**Outputs (intent payload — `daylight_model.*`):**
- `daylight_factor_average`: number per room
- `sda_300_50pct`: spatial Daylight Autonomy (≥300 lux for ≥50% of occupied hours)
- `ase_1000_250hrs`: Annual Sunlight Exposure (1000 lux for ≥250 hours)
- `useful_daylight_illuminance`: UDI 100–2000 lux ranges
- `dimming_setpoint_schedule`: hour-by-hour daylight-linked dimming target for the lighting-controls companion to consume
- `leni_daylight_factor`: input to energy-leni

**Consumes:**
- `lighting-layout.intent` (room geometry + glazed_walls)
- `lighting-photometric.intent` (point-grid engine)
- `architecture-massing` (NEW — building envelope + orientation; may NOT exist yet — flag dependency)

**Triggers lighting-layout INV-13.**

**Open questions for per-skill brainstorm:**
- Architecture-massing skill dependency — does it exist? If not, daylight skill needs its own building-envelope inputs OR cluster grows by 1 more upstream skill.
- Climate file source: bundled with skill OR engineer-supplied per project?
- Simulation engine: pure calc contract (defer to runtime Radiance/DAYSIM call) OR ship simplified DF formula in-prompt?
- Sky model selection per metric (CIE Overcast vs CIE Sunny vs climate-based)?
- BREEAM vs LEED vs Part L threshold conflicts — output all, let engineer pick OR force per-jurisdiction?

**Engineering note:** This is the heaviest skill in the cluster. Real daylight simulation runs through Radiance — calc contract will be substantial. Consider phased build (DF-only v1.0 → climate-based sDA/ASE v2.0).

---

### 3.4 `electrical-special-locations` — BS 7671 Part 7 zones

**Standards stack:** BS 7671:2018+A2:2022 Part 7 (§701 baths/showers; §702 swimming pools; §703 saunas; §710 medical Groups 1/2/3; §714 external lighting; §721 caravan parks; §753 floor/ceiling heating). Plus IEC 60364-7-XXX parallel parts.

**Inputs (high-level):**
- Location type (per Part 7 enum)
- Room geometry + boundary surfaces (e.g. bathtub edge → §701 Zone 0/1/2 derivation)
- Zone-relevant fixtures (showers, taps, gas medical outlets, etc.)
- Jurisdiction (BS 7671 vs IEC 60364-7-XXX vs NEC parallel)

**Outputs (intent payload — `part7_zones.*`):**
- `zones[]`: array of {zone_id, zone_type, location_clause, boundary_polygon, ip_rating_min, isolation_required, rcd_required, switch_position_restrictions}
- `prohibited_fixture_types[]`: per zone (e.g. §701 Zone 0 prohibits 230V switches)
- `mandatory_fixture_overrides[]`: e.g. §710 Group 2 medical IT system requires isolating transformer
- `non_compliance_flags[]` for any incoming fixture violation

**Consumes:**
- Room geometry from any drawing skill (lighting-layout, small-power, db-layout, etc.)

**Triggers INV-14 in lighting-layout AND parallel INVs in small-power / db-layout (cross-discipline).**

**Open questions for per-skill brainstorm:**
- Per-part scope: ship §701 + §714 + §710 in v1.0; defer §702/§703/§721/§753 to v2.0?
- §710 medical Group 2 is its own beast (IT system isolation, line-isolation monitor) — split into `medical-electrical` sub-skill?
- Zone-derivation algorithm: explicit polygon engineering input OR auto-derive from fixture positions (bathtub → Zone 0 cylinder etc.)?
- US NEC parallel (Article 680 pools, 517 healthcare) — same skill or jurisdiction-specific sibling?
- Cross-discipline scope: this skill provides constraints for sockets/switches/heaters too — naming should not imply lighting-only.

**Naming reconsideration:** "lighting-special-locations" would mis-scope. Per-discipline rename: **`part7-zones`** OR **`special-locations`** (electrical generic).

---

### 3.5 `lighting-controls` — DALI scene programming + application controllers

**Standards stack:** IEC 62386-101/102/103 (DALI), -207 (LED control gear extensions), -209 (colour control) + KNX ISO/IEC 14543-3 + DMX512 (ANSI E1.11) + Casambi/Bluetooth-Mesh proprietary.

**Inputs (high-level):**
- Controls protocol (from lighting-layout)
- Luminaire group definitions (per zone)
- Scene definitions (engineer-supplied OR template per room-type)
- Time-of-day schedule (occupancy + daylight integration)
- Daylight setpoints (from daylight companion if shipped)

**Outputs (intent payload — `controls_program.*`):**
- `dali_addressing_plan`: luminaire short-addresses + group memberships + scene memberships
- `application_controller_config`: panel-mount controllers + bus topology per IEC 62386-103
- `scene_schedule`: scene-N → luminaire-group → output-level mappings + time triggers
- `daylight_link_setpoints`: hour-by-hour target lux per zone (consuming daylight intent)
- `commissioning_plan`: per-luminaire addressing walk + scene programming sequence

**Consumes:**
- `lighting-layout.intent` (luminaire IDs + zone assignment)
- `daylight.intent.dimming_setpoint_schedule` (optional, if daylight shipped)

**Triggers lighting-layout INV-15.**

**Open questions for per-skill brainstorm:**
- DALI vs DALI-2 (IEC 62386-103 application controller) — separate or unified?
- Bus topology computation (≤64 short addresses per line, fan-out to multiple lines)?
- Scene library — per-room-type template OR fully engineer-defined?
- Casambi/Bluetooth-mesh wireless protocols — same skill or sibling?
- Commissioning-plan output downstream consumer (commissioning skill not yet built)?

---

### 3.6 `energy-leni` — Part L LENI + annual kWh + payback

**Standards stack:** Approved Document L (Part L 2021) LENI methodology + CIBSE TM54 (operational performance evaluation) + ISO 50001 (energy management) + LEED EAc1.

**Inputs (high-level):**
- Lighting load + control schedule (from lighting-layout + lighting-controls)
- HVAC load + schedule (from `mechanical-systems` skill if exists — likely NOT yet)
- Small-power load (from small-power skill)
- Occupancy hours per zone
- Daylight contribution (from daylight companion if shipped)
- Tariff + carbon intensity (engineer-supplied OR jurisdiction default)

**Outputs (intent payload — `leni_result.*`):**
- `leni_kwh_per_m2_per_year`: per Part L 2021 §6 LENI formula
- `meets_target_leni`: boolean vs building-type target (e.g. office target 28 kWh/m²/yr per Part L 2021)
- `annual_kwh`: total + per-system breakdown (lighting / HVAC / small-power)
- `annual_carbon_kg_co2e`: per declared grid intensity
- `payback_analysis`: per-intervention payback (LED vs halogen, DALI vs switched, daylight-link vs no-link)
- `compliance_summary` for Part L sign-off

**Consumes:**
- `lighting-layout.intent` + `lighting-controls.intent` + `daylight.intent`
- `mechanical-systems.intent` (NEW dependency — flag)
- `small-power.intent`

**Triggers lighting-layout INV (cross-skill — likely INV-16 reserved).**

**Open questions for per-skill brainstorm:**
- Lighting-only LENI v1.0 (subset of Part L) OR full-building LENI v2.0?
- mechanical-systems skill dependency — does it exist? Flag if not.
- Payback economics — bundled or separate `energy-economics` skill?
- Carbon factor source (Defra/EIA/local utility) — bundled or engineer-input?
- Cross-jurisdiction: NEC ASHRAE 90.1 LPD vs Part L LENI — same skill or jurisdiction sibling?

**Engineering note:** Cross-discipline skill. Likely the most-deferred of the 6 because real LENI requires HVAC + small-power inputs that may not yet have shipped IRs.

## 4. In-skill extensions (2) — lighting-layout v1.5.0 minor bump

### 4.1 Task/ambient split

**Scope:** schema gains `luminaire_purpose: ambient | task | accent | emergency` enum on each luminaire. Generator Step 11 (zone assignment) extended to handle multi-luminaire-type layouts (e.g. recessed LED panels for ambient + adjustable spotlights for task). Per-purpose lumen-method target (e.g. ambient 300 lux + task 500 lux at desk position).

**Effort:** ~1 day. Schema + generator step + 1 new example (private office with task lighting).

**No new skill.**

### 4.2 3D placement (pendant height + suspension)

**Scope:** schema gains `mounting_type: recessed | surface | suspended | pendant` + `suspension_drop_mm` per luminaire. Spacing-rules#hm-calculation tightened to use luminaire's effective height (ceiling − suspension_drop − working_plane). Affects RI + UF lookup chain.

**Effort:** ~1 day. Schema + spacing-rules update + 1 new example (high-ceiling warehouse with suspended highbays).

**No new skill.**

Both extensions ship as `lighting-layout v1.5.0` — a single minor bump after the v1.4.0 D3 ship.

## 5. Build sequence — locked

Optimised for: maximum parallelisation, minimum blocked-deps, safety-relevant + cross-discipline skills front-loaded, D4 interleaved at the point where its dependencies resolve.

### Wave 1 — parallel pair (no file overlap)
- **`special-locations`** — cross-discipline (consumed by small-power D4 + lighting + db-layout); ship first so D4 can consume its intent
- **`lighting-photometric`** — calc primitive; unblocks `lighting-layout` INV-11 + 2 downstream cluster skills

### Wave 2 — parallel pair (Wave 1 deps now satisfied)
- **`small-power` v1.2.0 D4 (depth)** — special-locations §702/§710/§722 + building-level diversity; NOW consumes `special-locations` intent properly
- **`lighting-layout` v1.5.0 extensions** — task/ambient split + 3D placement; minor bump (~2 days)

### Wave 3 — parallel pair (safety + controls)
- **`emergency-lighting`** — BS 5266-1 escape + anti-panic + high-risk; consumes `lighting-photometric` + `special-locations`
- **`lighting-controls`** — DALI scenes + commissioning prep; consumes `lighting-layout` zones only

### Wave 4 — sequential (heaviest + integration)
- **`daylight`** — DF + sDA + ASE; ships with self-contained building-envelope inputs (see §6.2)
- **`energy-leni`** — LENI v1.0 lighting-only; consumes lighting-layout + lighting-controls + daylight; full-building LENI v2.0 deferred (see §6.3)

### Cost estimate
D3 averaged ~20 commits per skill (10 implementer + 8 fix-pass + sweep + ship). 8 deliverables in the wave plan × ~20 commits = ~160 commits. Wave parallelisation reduces wall-clock from sequential ~3-4 weeks to ~2 weeks. Each per-skill brainstorm → plan → execute cycle stays intact — parallelism is between pairs, not within a single skill's discipline.

## 6. Cluster-level decisions — RESOLVED

Applying the "most enhanced + most scalable" rubric: prefer in-repo conventions, prefer self-contained skills, prefer parallel-able work, prefer existing runtime patterns over new ones.

### 6.1 Cluster naming — RESOLVED
**Decision:** No new namespace. Skills live as siblings under existing discipline folders (`electrical/`, `mechanical/`, `plumbing/` etc.) with `lighting-*` prefix where lighting-specific. The word "cluster" is documentation shorthand only — no manifest-level grouping.

**Final names + folder paths:**
| Skill | Folder path | Discipline scope |
|---|---|---|
| lighting-layout | `electrical/lighting-layout/` | existing — lighting interior |
| lighting-photometric | `electrical/lighting-photometric/` | NEW — lighting calc primitive |
| emergency-lighting | `electrical/emergency-lighting/` | NEW — life-safety |
| lighting-controls | `electrical/lighting-controls/` | NEW — DALI + KNX |
| daylight | `electrical/daylight/` | NEW — folder under electrical because Part L LENI compliance is electrical sign-off scope |
| special-locations | `electrical/special-locations/` | NEW — discipline folder does the scoping; skill name stays clean |
| energy-leni | `electrical/energy-leni/` v1.0 → `compliance/energy-leni/` v2.0 | NEW — moves to compliance/ when full-building LENI lands per §6.3 |

**Why:** matches existing repo convention (`electrical/earthing/` not `electrical-earthing/`); folder placement is the discipline namespace; no new naming layer to maintain.

### 6.2 architecture-massing dependency for daylight — RESOLVED
**Decision:** daylight ships with **self-contained building-envelope inputs** v1.0. No upstream architecture-massing dependency.

**Inputs taxonomy added to daylight v1.0:**
- `building_orientation_deg` (0–359 from true north)
- `glazing_areas[]` per façade (already partial in lighting-layout via glazed_walls)
- `obstruction_polygons[]` (other buildings, trees — engineer-supplied as ≥3-vertex polygons with height)
- `internal_reflectances` (per room, per surface — ceiling/wall/floor split)
- `external_reflectance` (ground albedo default 0.2)

**Honest disclosure** in skill README + inputs.json `_note`: "v1.0 ships self-contained building-envelope inputs. When `architecture-massing` skill ships, daylight v2.0 will consume its intent; manual inputs become fallback."

**Why scalable:** no blocking dependency on a not-yet-built upstream skill; v2.0 migration path declared; manual inputs are the engineer's reality anyway in early-design phases when architecture is fluid.

### 6.3 mechanical-systems dependency for energy-leni — RESOLVED
**Decision:** energy-leni ships **v1.0 lighting-only LENI** under `electrical/energy-leni/`. Full-building LENI (lighting + HVAC + small-power + DHW) deferred to v2.0 + folder migration to `compliance/energy-leni/`.

**v1.0 scope (electrical/energy-leni/):**
- Lighting-only LENI per Part L 2021 §6 (the formal LENI formula for the lighting component)
- Consumes: `lighting-layout.intent` + `lighting-controls.intent` + `daylight.intent`
- Outputs: `leni_lighting_kwh_per_m2_per_year` + `meets_lighting_lpd_target` + `lighting_annual_kwh` + `lighting_annual_carbon`

**v2.0 deferred** (waits on shipped mechanical-systems + small-power intents to expose annual energy):
- Full-building LENI + HVAC LPD + DHW + plug-load
- Migrates to `compliance/energy-leni/`
- Same honest disclosure pattern

**Why scalable:** delivers user-visible value immediately (lighting LENI is the most common project requirement); does not block on mechanical-systems which doesn't yet exist; folder migration v1→v2 is a documented expectation, not surprise rework.

### 6.4 special-locations skill rename — RESOLVED
**Decision:** Skill name = `special-locations` at folder path `electrical/special-locations/`. Discipline scoping via folder placement (matches `electrical/earthing/` precedent). NOT `part7-zones` (BS-specific) and NOT `electrical-special-locations` (folder already conveys discipline).

**v1.0 standards scope:**
- BS 7671 Part 7: §701 (baths/showers), §710 (medical Group 1/2/3), §714 (external lighting — the real one), §753 (floor/ceiling heating)
- IEC 60364-7-XXX parallel parts for INT jurisdiction
- KS 1700 §313 route-to-BS for KE jurisdiction

**v1.1 deferred:** §702 (swimming pools), §703 (saunas), §721 (caravan parks). Build when first project requirement lands.

**US NEC parallel** (Article 680 pools, Article 517 healthcare) — separate sibling skill `electrical/special-locations-us/` when first US project requirement lands. Same shape, different standards stack.

### 6.5 Cluster vs D4 priority — RESOLVED (interleaved per Wave plan)
**Decision:** **Interleaved per §5 wave plan.** D4 (small-power depth) ships in **Wave 2**, after `special-locations` lands in Wave 1. This is strictly better than either pure ordering:
- D4-first would build small-power depth without consuming special-locations intent (would need rework)
- Cluster-first would defer D4 indefinitely (within-skill-depth program closure waits)
- Interleaved: D4's natural dependency (special-locations) is already shipped when D4 starts; D4 closes the depth program cleanly; cluster build continues without pause

**Updated within-skill-depth program closure narrative:** D1 + D2 + D3 shipped; D4 ships in Wave 2 of the lighting skill family build, consuming the `special-locations` companion shipped in Wave 1. After D4, the within-skill-depth program is fully complete AND the lighting family has the first 4 deliverables shipped.

### 6.6 Parallelisation policy — RESOLVED (yes, per Wave plan)
**Decision:** YES — parallelise within each Wave per §5. Specifically:

- **Wave 1**: `special-locations` + `lighting-photometric` parallel (zero file overlap — different folders, different shared paths)
- **Wave 2**: `small-power` D4 + `lighting-layout` v1.5.0 parallel (different skills, different schemas)
- **Wave 3**: `emergency-lighting` + `lighting-controls` parallel (minimal overlap — both consume from lighting-layout intent but write to different folders + different validator INVs)
- **Wave 4**: sequential (daylight → energy-leni — strict dependency)

**Mechanism:** Per `superpowers:using-git-worktrees`, each parallel skill builds in its own worktree branch off `main`; merge back to `main` at Wave completion. Two-stage Opus review discipline held per task within each worktree. Cross-worktree integration check at Wave completion runs the validate-examples + functional_audit gates on the merged result.

**Risk surface:** shared schemas under `shared/schemas/electrical/` could collide. Mitigate by declaring at Wave start which shared files each parallel skill will touch; if overlap is detected, serialise that pair.

### 6.7 Cross-skill INV cascade — RESOLVED (existing runtime pattern reused)
**Decision:** Reuse the existing manifest `consumes_intents[]` cascade pattern that cable-sizing → db-layout-rollup already uses today. No new runtime machinery required.

**Implementation:**
- Each companion's manifest declares it `produces_intents[]`
- `lighting-layout/skill.manifest.json` declares `consumes_intents[]` with `{name, version_pin, trigger}` per companion
- The `trigger` field is a **JSONPath-style expression** over the IR (e.g. `"glazed_walls != []"` for the daylight conditional, `"room_type IN [bathroom, swimming_pool, medical_group2]"` for special-locations). Same DSL the runtime already evaluates for cable-sizing's `tool_call_pending` conditional fields.
- If runtime DSL doesn't yet support a particular trigger expression: skill ships with **unconditional** consumes declaration + the IR-level INV handles the conditional check (cascade dependency unconditional, but the failure scope is conditional). Skills repo loses nothing; runtime gets a future-enhancement TODO.

**Verification before Wave 1 ships:** cluster-roadmap appendix documents the 5 trigger expressions needed (INV-11 always-on; INV-12/13/14/15 conditional). Coordinate with runtime team via spec doc handoff. Expected: 4 of 5 expressions are existing DSL primitives (set membership + non-empty array); 1 (`is_uk_new_build AND glazed_walls != []`) needs AND-conjunction support which may be new.

## 7. What's NOT in the lighting skill family (scope guard)

## 7. What's NOT in the cluster (scope guard)

- **Exterior lighting design** (façade, landscape, security floodlighting) — `external-lighting` is a separate skill in the breadth-first stub pool. Cluster is interior-focused.
- **Stage / theatrical / entertainment lighting** — out of scope (DMX-controlled, different design discipline).
- **Horticultural / UV-A / IR lighting** — out of scope.
- **Sports / road / area lighting** — out of scope; separate skill family (`sports-lighting` per BS EN 12193, `road-lighting` per BS EN 13201).
- **DALI commissioning execution** — the runtime owns the commissioning robot/tool integration. Skill ships commissioning plan only.

## 8. Memory + cross-references

- `[[sprint-D3-shipped]]` — lighting-layout v1.4.0 ship + the 10-dimension audit that surfaced this cluster
- `[[within-skill-depth-plan]]` — depth program (D1+D2+D3) complete; this cluster is part of the breadth-first pivot
- `[[build-strategy-breadth-first]]` — finish 100% of skills before scaling jurisdictions
- `[[runtime-project-boundary]]` — calc executors + renderers + project graph live in runtime; cluster ships contracts only
- `[[feedback-no-haiku-sonnet-opus-only]]` — model selection (mechanical→Sonnet, judgment→Opus, reviews→Opus)
- `[[feedback-no-trim-non-consequential]]` — preserve engineering content; raise schema caps when needed
- `[[drafting-standards-deferred-sprint]]` — drafting-furniture cross-skill harmonisation remains deferred; cluster does NOT subsume it

## 9. Next action — Wave 1 starts

Per §5 + §6.5 + §6.6: **Wave 1 = `special-locations` + `lighting-photometric` in parallel worktrees.** Per CLAUDE.md sprint workflow:

1. **Two parallel brainstorm sessions** (`superpowers:brainstorming` per skill):
   - `special-locations` v1.0 brainstorm — resolve per-skill open questions in §3.4: per-part scope (§701 + §710 + §714-real + §753 in v1.0), zone-derivation algorithm choice, US NEC parallel timing, etc.
   - `lighting-photometric` brainstorm — resolve per-skill open questions in §3.1: grid resolution policy, UGR view-position heuristic, IES file ingestion path, output shape.

2. **Two parallel writing-plans sessions** after each brainstorm approves.

3. **Two parallel executing sessions** in separate worktrees per `superpowers:using-git-worktrees`.

4. **Wave 1 ship** = both skills merged to `main` + cross-skill integration check (validate-examples + functional_audit both green).

5. **Wave 2 dispatch** = `small-power` D4 + `lighting-layout` v1.5.0 in parallel, now consuming Wave 1 deliverables.

**Repeat the wave pattern for Waves 3 and 4.** Expected total wall-clock from Wave 1 start to energy-leni v1.0 ship: ~2 weeks with 4 wave-pairs running in parallel.

**Process discipline preserved:** per-skill two-stage Opus review + fix-pass on each task per the D2/D3 pattern; pre-ship Sonnet fence at each Wave completion; honest disclosure on every fabricated-citation risk; citation cross-check against `shared/standards/electrical/` BEFORE every plan template ships.
