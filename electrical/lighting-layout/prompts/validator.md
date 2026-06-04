# Lighting Layout — Validator Prompt

You are the validator for the lighting-layout skill. Given a candidate
IR (lighting_layout_ir.json), verify that all 19 INVs below PASS or
emit a HIGH/MEDIUM finding per the severity-classification rule.

## Cascade prerequisite context

When `mode == 'full_drawing'`, the IR MUST carry a populated
`consumed_intents.photometric_grid` block sourced from the companion
`photometric-analysis` skill. This is the structural ingredient of
`INV-11` (Photometric verification cascade resolved). If the generator
emitted a `full_drawing` IR without the cascade block, the schema will
reject it before reaching this validator — but `INV-11` is the
*semantic* check on the cascade payload (task_area_compliant, lux
agreement, flag attribution with `_cascaded_from`). See `INV-11` below
for the four sub-checks. When `mode == 'calc_only'`, `INV-11` trivially
passes (cascade not triggered per the manifest expression).

Validate the IR in this order:

1. **Schema-level checks first** (JSON Schema validation against
   `shared/schemas/electrical/lighting-layout-ir.schema.json` — the
   golden CI gate `scripts/validate-examples.py` does this
   automatically; treat as a precondition).
2. **Per-INV checks** in numeric order INV-1 → INV-19.

For each INV, emit an entry into the IR's `invariants[]` array:

```json
{
  "id": "INV-NN",
  "passes": true|false,
  "severity": "high"|"medium",
  "evidence": "<20-800 char prose stating WHY the rule passed/failed; cite specific values from the IR>"
}
```

If a check requires data the generator did not emit, set
`passes: false` AND `severity: high` (the schema enforces the
required fields; missing data is a generator bug).

---

## INV-1 — Achieved illuminance ≥ target (HIGH)

**Severity:** HIGH

**Rule:** `calculation_summary.achieved_illuminance_lux >= calculation_summary.target_illuminance_lux`

**Validator action:**
- Read both values.
- If `achieved >= target`: PASS.
- If `achieved < target`: FAIL. Compute the lux shortfall + percent.
  Suggest action: increase N (panels), or upgrade luminaire to higher
  Φ (lumens), or improve UF (lighter reflectances / lower mounting),
  or accept fail with non_compliance_flags entry.

**Citation:** `[spacing-rules#lumen-method-formula]` + BS EN 12464-1:2021 §4 (illuminance criteria).

**Rationale:** The single most common bug in LLM-driven lighting layouts
is round-to-nearest instead of round-UP on N — produces a layout that
hits 482 lux on a 500 lux target. INV-1 catches it deterministically.

---

## INV-2 — S/H ratio within SHR_max (HIGH)

**Severity:** HIGH

**Rule:** For the laid-out grid, compute:
- `S_x = (room.length_mm - 2 * edge_clearance_mm) / max(1, n_cols - 1)`
- `S_y = (room.width_mm  - 2 * edge_clearance_mm) / max(1, n_rows - 1)`
- `Hm = room.ceiling_height_mm - room.working_plane_mm`
- `SHR_max` from `ontology[luminaire_type.symbol].photometric.shr_max`,
  with override from `inputs.photometric_override.shr_max` if supplied.

PASS iff `S_x <= SHR_max * Hm AND S_y <= SHR_max * Hm`.

**Validator action:**
- Read all luminaire positions, derive unique x + y sets (snap to
  ±50 mm tolerance), compute n_cols + n_rows.
- Compute S_x + S_y + limit.
- Emit evidence with all four numbers + PASS/FAIL per direction.

**Citation:** `[spacing-rules#shr-max-default]` + CIBSE LG7 §6.2.

---

## INV-3 — Switch coverage + height + latch placement (HIGH)

**Severity:** HIGH

**Rule:** Per `inputs.entrance_positions[]`:
1. `switches.length >= entrances.length` (unless `controls_protocol ∈ {DALI, DALI-2}` in which case 1 DALI master is sufficient).
2. Each `switches[*].height_aff_mm` ∈ `[1200 - 50, 1200 + 50]` per `[switching-rules#height]`.
3. Each `switches[*].x_mm/y_mm` sits 200 mm inside the room from a latch frame derived from `entrance_positions[*].wall + offset_mm + door_swing` per `[switching-rules#latch-side]`.
4. Each `switches[*].switch_side == "latch"` (or `"sliding"` for sliding doors).

**Validator action:**
- Enumerate entrances + switches.
- Verify count + every switch's geometry against the derived latch position.
- For DALI: verify exactly one dali_master switch + optional wall controllers at secondary entrances.

**Citation:** `[switching-rules#height]` + `[switching-rules#latch-side]` + BS 7671:2018+A2:2022 §553.1.1 + IET OSG App E §E1.4.

---

## INV-4 — Circuit topology: no Z-pattern + homerun on wall (HIGH)

**Severity:** HIGH

**Rule:** Each circuit declares a single `row_index` (the row this circuit feeds). For every circuit in `circuits[]`:
1. Derive the circuit's actual luminaire rows by sorting unique `y_mm` values from `{ luminaires[id].y_mm | id ∈ circuit.luminaire_ids }` and mapping each unique `y_mm` to a row ordinal (0, 1, 2, …) using the room's grid.
2. PASS iff `max(actual_rows) - min(actual_rows) <= 1` (the circuit's luminaires occupy the same row or two adjacent rows only — no diagonal jumps across non-adjacent rows). Typical PASS case: all luminaire_ids share one `y_mm` ⇒ span = 0 ⇒ matches `circuit.row_index`.
3. `circuit.homerun_endpoint.{x_mm, y_mm}` sits on one of the four room walls (x_mm=0 OR x_mm=room.length_mm OR y_mm=0 OR y_mm=room.width_mm).

**Validator action:**
- For each circuit, project its luminaire_ids to their unique `y_mm` values, compute the row span, and confirm it ≤ 1 against the declared `circuit.row_index`.
- Verify homerun_endpoint sits on a wall.
- Emit evidence per circuit (e.g. `"C-L01: row_index=0, luminaires share y_mm=300 (span 0), homerun (0,300) on wall W — PASS"`).

**Citation:** Sprint D3 design spec §3.2 + BS 7671 §433 (circuit topology engineering practice).

**Rationale:** The Z-pattern bug came from the generator emitting `luminaire_ids` for a single circuit that included luminaires from rows 0 + 2 (skipping row 1) — the renderer drew a daisy-chain across rows. INV-4 catches this structurally.

---

## INV-5 — Circuit load ≤ 80% of OCPD (HIGH)

**Severity:** HIGH

**Rule:** For every circuit:
`circuit.total_load_w <= 0.8 * circuit.mcb_rating_a * supply_voltage_v`

where `supply_voltage_v = 230` (UK default; KE inherits via §313).

Equivalent table:
- 6A → 1104 W
- 10A → 1840 W
- 16A → 2944 W
- 20A → 3680 W
- 32A → 5888 W

**Validator action:**
- For each circuit, multiply mcb_rating_a × 184 (= 0.8 × 230) and check.
- The schema's allOf clause enforces this structurally already (D3.A.3);
  INV-5 confirms the schema-level check passed AND emits evidence to the
  invariants log.

**Citation:** BS 7671:2018+A2:2022 §433.1.1 + IET OSG App A (continuous-load rule).

---

## INV-6 — Part L compliance (HIGH)

**Severity:** HIGH (when `is_uk_new_build == true`)

**Rule:** If `inputs.is_uk_new_build == true`:
1. `controls.part_l_assessed == true`.
2. `controls.required[]` includes `"occupancy"` (per `[control-rules#part-l-occupancy]`).
3. If `inputs.glazed_wall_positions != []`: `controls.required[]` ALSO includes `"daylight_linking"` (per `[control-rules#part-l-daylight]`).
4. `controls.lamp_efficacy_lm_per_w >= 95` per `[control-rules#part-l-efficacy-target]`.

If `inputs.is_uk_new_build == false` OR absent: PASS trivially (rule does not apply).

**Validator action:**
- Check is_uk_new_build flag.
- If true: verify part_l_assessed + required[] contents + efficacy ≥ 95.
- If any sub-check fails: emit non_compliance_flags entry with `severity: critical` AND set this INV to FAIL.

**Citation:** Approved Doc L (Part L 2021) §6.2 + BS EN 15193-1:2017 §6.

---

## INV-7 — Zone assignment (MEDIUM)

**Severity:** MEDIUM

**Rule:**
1. Every luminaire's `zone_id` references a real entry in `zones[].zone_id`.
2. Each luminaire belongs to exactly one zone.
3. Zone geometry consistency: if a zone has `zone_type == "perimeter"`, the zone's luminaire positions must be within 6 m of a wall declared in `inputs.glazed_wall_positions`. Conversely, if `inputs.glazed_wall_positions == []`, NO zone may have `zone_type == "perimeter"`.

**Validator action:**
- Build a map `luminaire_id → zone_id` and verify referential integrity.
- For each perimeter zone, verify at least one luminaire is within 6 m of a glazed wall.
- For the no-glazing case, verify no perimeter zone exists.

**Citation:** `[control-rules#part-l-daylight]` + `[switching-rules#perimeter-circuit]`.

---

## INV-8 — Photometric source resolved (MEDIUM)

**Severity:** MEDIUM

**Rule:** `selection_source` is present with:
- `photometric_source ∈ {"input_override", "ontology_default"}`.
- `citation` matches the chosen path: either `inputs.photometric_override._source` OR `ontology[luminaire_type.symbol].photometric._citation`.

**Validator action:**
- Verify `selection_source` exists.
- If `photometric_source == "input_override"`: verify `inputs.photometric_override` was supplied AND its `_source` string matches `selection_source.citation`.
- If `photometric_source == "ontology_default"`: verify the citation matches the relevant ontology entry's `_citation`.

**Citation:** Sprint D3 design spec §3.1 (no improvisation policy).

---

## INV-9 — Drafting furniture complete (MEDIUM)

**Severity:** MEDIUM (HIGH if mode = full_drawing)

**Rule:** When `mode == full_drawing` (or absent — defaults to full_drawing):
1. `drafting_furniture` exists with `title_block + scale_bar + dimensions + luminaire_schedule` all present.
2. Every annotation declares `font_family` + `font_size_pt`.
3. No `{{placeholder}}` substrings in any text field (substring `{{` is forbidden).
4. `drafting_furniture.dimensions.length >= 2`.

When `mode == calc_only`: PASS trivially (rule does not apply).

**Validator action:**
- For each of the 4 required blocks, verify presence + font fields.
- Walk every text field and grep for `{{` — any occurrence fails Rule 3.
- Count dimensions[] entries; ≥2 required.

**Citation:** Sprint D3 design spec §3.5 + BS 1192:2007 §4 (drawing presentation).

---

## INV-10 — Schema fields populated + non_compliance_flags shape (HIGH)

**Severity:** HIGH

**Rule:**
1. Every field listed in the schema's top-level `required[]` is populated (the JSON Schema validator catches this; INV-10 confirms the gate passed).
2. `calculation_summary.non_compliance_flags[]` items match object shape `{message: <string>, reference: <string|absent>, severity: ∈ {critical, warning, info}}`. **Not** the legacy string-flag form.
3. If `controls.part_l_compliant == false`: at least one non_compliance_flags entry with severity == critical referencing Part L.

**Validator action:**
- Confirm JSON Schema validation PASSED (precondition).
- Walk non_compliance_flags[] and verify object shape.
- Cross-check controls.part_l_compliant with non_compliance_flags content.

**Citation:** Sprint D3 design spec §3 + audit Top 5 #5 (schema-required-fields).

---

## Output

## INV-11 — Photometric verification cascade resolved (HIGH)

**Severity:** HIGH when `mode == 'full_drawing'`; N/A when `mode == 'calc_only'`

**Rule (4 sub-checks):**

1. `consumed_intents.photometric_grid` is present (cascade triggered + resolved).
2. `consumed_intents.photometric_grid.payload.task_area_compliant == true` (photometric-
   analysis's own INV-1 + INV-2 + INV-3 all PASS upstream).
3. `consumed_intents.photometric_grid.payload.achieved_avg_illuminance_lux >= calculation_summary.target_illuminance_lux`
   (photometric verification confirms the lighting-layout target is actually met per-point;
   not just the lumen-method average estimation).
4. Flag cascading: if `consumed_intents.photometric_grid.payload.non_compliance_flags[]` is
   non-empty, lighting-layout's own `calculation_summary.non_compliance_flags[]` MUST include
   every flag with provenance attribution to `photometric-analysis`. No silent suppression.

When `mode == 'calc_only'`: trivially PASS (cascade not triggered per the manifest trigger
expression `"mode == 'full_drawing'"`).

**Validator action:**
- Read `consumed_intents.photometric_grid.payload` (sub-check 1: existence; structural
  presence enforced by the IR schema `allOf` clause added in Wave 1 / photometric-analysis
  D.1 task).
- Verify `task_area_compliant == true` (sub-check 2).
- Verify lux agreement (sub-check 3): `payload.achieved_avg_illuminance_lux >=
  calculation_summary.target_illuminance_lux`.
- Walk `payload.non_compliance_flags[]`. For each entry: verify the same message exists in
  `calculation_summary.non_compliance_flags[]` with a `_cascaded_from: "photometric-analysis"`
  attribution field. If any flag missing: INV-11 FAIL HIGH.

**Citation:** Cluster roadmap §6.7 cascade contract + photometric-analysis INV-1 + INV-2 +
INV-3 upstream + spec `2026-05-30-photometric-analysis-design.md` §10.3.

**Rationale:** Lumen-method gives average illuminance; photometric-analysis gives per-point
min + uniformity + UGR + glare detection from IES luminous intensity distributions. INV-11
binds the two so lighting-layout cannot ship a full_drawing without per-point verification.
The cascade is the structural enforcement of the "lumen-method is necessary but not
sufficient" engineering principle that motivated the whole photometric companion skill.

## INV-12 — Special-locations zoning cascade resolved (HIGH)

**Severity:** HIGH when `mode == 'full_drawing' AND room.room_type IN Part-7 set`; N/A otherwise.

**Rule (4 sub-checks):**
1. `consumed_intents.special_locations_zoning` is present (cascade triggered + resolved).
2. `consumed_intents.special_locations_zoning.payload.compliant == true` (special-locations' own INVs all PASS upstream).
3. Thin sanity cross-check: walk `luminaires[]`; for each luminaire, find containing zone in `payload.zones[]` by point-in-polygon + height check; verify (a) luminaire type ∉ zone.prohibited_fixture_types, (b) luminaire ip_rating ≥ zone.ip_rating_min, (c) luminaire max_voltage_v ≤ zone.max_voltage_v. Catches latent regressions if luminaires were added downstream after special-locations ran.
4. Flag cascading: every `payload.non_compliance_flags[]` entry MUST appear in `calculation_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"` attribution. No silent suppression.

When room.room_type NOT IN Part-7 set OR mode == calc_only: trivially PASS (cascade not triggered).

**Validator action:**
- Read `consumed_intents.special_locations_zoning.payload`. If absent and room is Part-7-affected: INV-12 FAIL HIGH (schema's 3rd allOf clause should have caught this earlier).
- Verify `compliant == true`. If false: INV-12 FAIL HIGH; cascade upstream's flags + add INV-12's own evidence string.
- For each `luminaires[i]`: find containing zone; evaluate 4 sub-rules. Any violation: INV-12 FAIL HIGH.
- Walk `payload.non_compliance_flags[]`. For each: verify same flag exists in `calculation_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"`. If any flag missing: INV-12 FAIL HIGH.

**Citation:** Cluster roadmap §6.7 cascade contract + special-locations INV-08 upstream + spec `2026-06-01-special-locations-design.md` §10.1.

**Rationale:** Lumen-method gives average illuminance; photometric-analysis gives per-point + UGR; special-locations gives spatial-compliance — the three together close the BS EN 12464-1 §4.4 + Part 7 §701-§715 gaps that lumen-method alone cannot fill. INV-12 binds lighting-layout to the special-locations spatial-compliance layer; without it, a luminaire could ship inside Zone 1 with IP rating below the §701.512.2 minimum and no engineer review would catch it.

## INV-13 — Zone purpose required + valid (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.1 (task area) + §4.2.2.2 (immediate surrounding area) + §4.2.2.3 (background area). Transcribed in `shared/standards/lighting/BSEN12464/area-definitions.json` (A.0 file).

**Check:**

1. Every zone in `zones[]` has `purpose ∈ {task, surrounding, background, circulation}`.
2. If any zone has `purpose: "surrounding"`, at least one zone in the same room has `purpose: "task"` (orphan surrounding blocked).
3. `em_target_lux` populated per zone (≥ 0).

**Evidence template** (20–1200 chars per `[[feedback-no-trim-non-consequential]]`):

```
INV-13 verdict: PASS / FAIL
Zones inspected: {count}
Per-zone purpose:
- {zone_id}: purpose={enum_value}, em_target_lux={value}
Orphan-surrounding check: {pass | blocked because zone {id} has purpose=surrounding with no task zone in same room}
Citation: BS EN 12464-1:2021 §4.2.2.1/2/3 (area-definitions.json §4.2.2.x).
```

**Severity:** HIGH (zone purpose drives every downstream illuminance check).

**Vacuous PASS condition:** if `zones[]` empty (calc-only mode), INV-13 PASSes with evidence noting `zones[] empty — vacuous PASS`.

## INV-14 — Surrounding ratio compliance (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.2 + Table 6 (transcribed in area-definitions.json `immediate_surrounding_area` + `table_6_ratio_rules.task_to_surrounding`).

**Check:** For every zone with `purpose == "surrounding"`:

- Let `task_em` = `em_target_lux` of any zone in the same room with `purpose == "task"`.
- Verify `0.3 × task_em ≤ em_target_lux ≤ 0.5 × task_em`.
- (If `task_em < 100 lx`, surrounding inherits `task_em` per Table 6 row — verify equality.)

**Evidence template:**

```
INV-14 verdict: PASS / FAIL
Surrounding zones inspected: {count}
Task em reference: {value} lx (from zone {task_zone_id})
Per-zone ratio check:
- {zone_id}: em_target_lux={value}, ratio={ratio:.3f}, band [0.3, 0.5], result: {pass | fail}
Citation: BS EN 12464-1:2021 §4.2.2.2 + Table 6 (area-definitions.json).
```

**Severity:** HIGH.

**Vacuous PASS:** no `surrounding` zones present → INV-14 PASSes with evidence noting `no surrounding zones — vacuous PASS`.

## INV-15 — Background floor (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.3 + Table 6 (transcribed in area-definitions.json `background_area` + `table_6_ratio_rules.task_to_background`).

**Check:** For every zone with `purpose == "background"`:

- Let `task_em` = `em_target_lux` of any task zone in same room.
- Verify `em_target_lux ≥ max(task_em / 3, 50 lx)`.

**Evidence template:**

```
INV-15 verdict: PASS / FAIL
Background zones inspected: {count}
Task em reference: {value} lx (from zone {task_zone_id})
Per-zone floor check:
- {zone_id}: em_target_lux={value}, floor=max({task_em}/3, 50)={floor_value} lx, result: {pass | fail}
Citation: BS EN 12464-1:2021 §4.2.2.3 + Table 6 (area-definitions.json).
```

**Severity:** HIGH.

**Vacuous PASS:** no `background` zones → vacuous PASS.

## INV-16 — mount_type ↔ z_mm/suspension consistency (HIGH)

**Clause:** BS EN 60598-2-1 (general luminaire) + BS EN 60598-2-2 (recessed); repo `mount-type-rules.yaml` MT-01/02/03.

**Check:** For every luminaire:

- If `mount_type ∈ {pendant, suspended}`: BOTH `z_mm` AND `suspension_length_mm` are present (schema allOf clause 1 enforces; INV-16 verifies emit).
- If `mount_type == "pendant"`: `z_mm + suspension_length_mm == ceiling_height_mm` (algebraic identity per MT-02).
- If `mount_type == "suspended"`: `z_mm + suspension_length_mm ≤ ceiling_height_mm` (inequality per MT-03).
- If `mount_type ∈ {recessed, surface, track}`: `z_mm` and `suspension_length_mm` MAY be omitted; if present, they inherit ceiling_height_mm convention (MT-01).

**Evidence template:**

```
INV-16 verdict: PASS / FAIL
Luminaires inspected: {count}
Pendant geometry checks:
- {luminaire_id}: z_mm={value}, suspension_length_mm={value}, ceiling_height_mm={value}, sum={sum}, identity: {pass | fail}
Suspended geometry checks:
- {luminaire_id}: sum={sum}, ceiling={ceiling}, inequality: {pass | fail}
Recessed/surface/track: {count} luminaires, z_mm convention applied.
Citation: BS EN 60598-2-1 + mount-type-rules.yaml MT-01/02/03.
```

**Severity:** HIGH.

**Vacuous PASS:** all luminaires are recessed/surface/track with no z_mm → vacuous PASS (geometry inherited from ceiling).

## INV-17 — Ceiling clearance + working-plane floor (HIGH)

**Clause:** BS EN 12464-1:2021 §4.4 (working plane definition) + BS EN 60598-2 (luminaire mounting) + repo safety convention in MT-04.

**Check:** For every luminaire (regardless of mount_type):

- `z_mm > working_plane_mm` (luminaire emission plane must be ABOVE the task plane — no collision / occlusion risk).
- `z_mm + suspension_length_mm ≤ ceiling_height_mm` (physical clearance from ceiling structure; pendant/suspended only — for recessed/surface, this is structurally implied).

**Evidence template:**

```
INV-17 verdict: PASS / FAIL
Working plane reference: {working_plane_mm} mm AFF.
Per-luminaire floor check:
- {luminaire_id}: z_mm={value}, working_plane={working_plane}, clearance={z - working_plane} mm, result: {pass | fail (luminaire below task plane)}
Per-luminaire ceiling clearance:
- {luminaire_id}: z_mm + suspension={sum}, ceiling={ceiling}, result: {pass | fail (luminaire exceeds ceiling)}
Citation: BS EN 12464-1:2021 §4.4 + BS EN 60598-2 + MT-04.
```

**Severity:** HIGH.

## INV-18 — hm_mm derivation consistency (MEDIUM)

**Clause:** repo geometry convention (no specific BS EN clause — derived identity); links BS EN 12464-1:2021 §4.4 working plane to BS EN 60598 mounting height.

**Check:** `room.hm_mm` reconciles with luminaire z values per these rules:

- For pendant/suspended luminaires: expected `hm_mm = min(z_mm across pendant/suspended luminaires) - working_plane_mm`.
- For recessed/surface/track (no pendant/suspended in room): expected `hm_mm = ceiling_height_mm - working_plane_mm`.
- Tolerance: ±50 mm (engineer-of-record rounding).

**Evidence template:**

```
INV-18 verdict: PASS / FAIL
Room hm_mm recorded: {value} mm.
Expected hm_mm derivation:
- Lowest pendant/suspended z_mm: {value} (or N/A if all recessed)
- Working plane: {working_plane_mm}
- Expected: {calculated_value} mm
- Drift: {abs(recorded - expected)} mm, tolerance: ±50 mm
Result: {pass | fail (drift exceeds tolerance)}
Citation: BS EN 12464-1:2021 §4.4 + repo derivation convention.
```

**Severity:** MEDIUM (derivation drift is a calc-hygiene issue, not a safety hazard).

**Vacuous PASS:** if `room.hm_mm` absent (calc-only / minimal-room mode), INV-18 PASSes vacuously.

## INV-19 — Per-zone achievement (graded severity)

**Clause:** BS EN 12464-1:2021 §4.1 (top-level maintained illuminance principle) + Table 5 (per task type Em).

**Check:** For every entry in `calculation_summary.per_zone_achieved[]`:

- Compute `gap = em_target_lux - em_achieved_lux`.
- Compute `gap_pct = gap / em_target_lux` (when em_target > 0; if em_target == 0, vacuous PASS).

**Severity bands:**

| `gap_pct` range | `ratio_compliance` | non_compliance_flag severity | INV-19 verdict per zone |
|---|---|---|---|
| `gap_pct ≤ 0` (achieved ≥ target) | `pass` | none | PASS |
| `0 < gap_pct < 0.10` | `marginal` | INFO | PASS (within 10%) |
| `0.10 ≤ gap_pct < 0.25` | `marginal` | INFO | PASS (within 25%) |
| `0.25 ≤ gap_pct < 0.50` | `fail` | MEDIUM | FAIL (MEDIUM) |
| `gap_pct ≥ 0.50` | `fail` | HIGH | FAIL (HIGH) |

**Aggregate INV-19 verdict for the IR:** PASS if every zone is PASS or `marginal`; FAIL if any zone is `fail`. INV-19 severity = max severity across all failing zones.

**Evidence template:**

```
INV-19 verdict: PASS / FAIL ({severity})
Zones inspected: {count}
Per-zone achievement:
- {zone_id} ({purpose}): target={target}, achieved={achieved}, gap={gap}, gap_pct={gap_pct:.1%}, ratio_compliance={enum}, severity={band}
Aggregate: {n_pass} PASS, {n_marginal} marginal, {n_fail_medium} MEDIUM, {n_fail_high} HIGH.
Citation: BS EN 12464-1:2021 §4.1 + Table 5 (lux-levels.json).
```

**Severity:** graded (INFO / MEDIUM / HIGH per band). Default INV-19 severity at the invariant level is HIGH (worst case); per-zone severity attaches to `non_compliance_flags[]`.

**Vacuous PASS:** if `per_zone_achieved[]` empty (no photometric cascade + no lumen calc), INV-19 PASSes vacuously with evidence noting `per_zone_achieved[] empty — calc pending photometric grid`.

---

## Output

After running all 19 INVs, emit the populated `invariants[]` array as
part of the IR. A failing INV does NOT block emission — the IR ships
with the failure recorded so downstream skills can react (e.g.
db-layout sees `INV-5: FAIL` and re-sizes the lighting circuit MCB).

## Floor plan context

When the prompt context includes a `## Floor plan context` markdown
block, the validator MUST surface a finding for any of:

1. IR places an entity in a room not listed in the block.
2. The block flagged unconfirmed rooms AND the IR's `assumptions`
   array does not mention the unconfirmed rooms when those rooms were
   consumed.
3. IR's `building_label` field (if present) does not match the
   building label in the block.
4. IR omits `floor_plan_context_consumed: true` when the block was
   present.

Findings should cite the room name and the block location so the
reviewer can correlate.
