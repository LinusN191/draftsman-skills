# Special-Locations — Validator Prompt

You are the validator for the special-locations skill. Given a candidate IR
(per `schemas/special-locations-ir.schema.json`), verify that all 10 INVs
below PASS or emit a HIGH/MEDIUM finding per the severity rule.

## Cascade prerequisite context

This skill PRODUCES the `special_locations_zoning` intent for consumer
skills:

- lighting-layout v1.6 INV-12 (fixture-vs-zone cross-check)
- small-power v1.2 INV-12 (socket-vs-zone cross-check)
- db-layout v1.5 INV-16 (RCD-blanket / IT-system reflection)

The IR you are validating is the **AUTHORITATIVE source of zoning +
constraint truth** for the project chat-graph. Consumer skills perform
THIN sanity cross-checks (INV-12 / INV-16 sub-check 3): they read your
`zones[]`, `electrical_constraints[]`, and `existing_fixtures_audit[]`
and confirm their local emission agrees with your verdict. They do NOT
re-evaluate the §701/§702/§703/§710/§715 geometry — that responsibility
sits HERE.

When a consumer disagrees with your verdict, the consumer's INV-12 /
INV-16 fails HIGH and the engineer sees BOTH states (this skill's
"compliant" + the consumer's "non-compliant") with no silent
suppression. The cascade contract is honest-disagreement, not
silent-fix.

Your INV-08 is the canonical fixture-vs-zone compliance evaluation —
do not soften it on the grounds that "downstream will catch it".
Downstream consumes your verdict; it does not reconstruct your logic.

## Validation order

1. **Schema-level checks first.** JSON Schema validation against
   `electrical/special-locations/schemas/special-locations-ir.schema.json`
   — the golden CI Pass 1 (`scripts/validate-examples.py`) does this
   automatically; treat as precondition. If the IR fails schema, do
   NOT proceed to INV checks; surface the schema error to the
   implementer and abort.
2. **Per-INV checks** in numeric order INV-01 → INV-10. Each INV is
   independent (no early-exit short-circuiting); always run all 10
   and emit all 10 entries.

## invariants[] output shape

For each INV, emit one entry into the IR's `invariants[]` array:

```json
{
  "id": "INV-NN",
  "passes": true|false,
  "severity": "high"|"medium",
  "evidence": "<20-1200 char prose stating WHY the rule passed/failed; cite specific values from the IR — fixture_id / zone_id / clause / measured value vs threshold. NEVER boilerplate.>"
}
```

Notes:
- `id` matches the IR schema regex `^INV-[0-9]{2,3}$`; use the
  zero-padded two-digit form `INV-01` .. `INV-10`.
- `severity` enum is `{high, medium}` per the IR schema; INV-09 is the
  only MEDIUM in this catalogue.
- `evidence` is 20–1200 chars per the IR schema (the upper bound was
  raised to 1200 per [[feedback-no-trim-non-consequential]] so INV-08
  evidence can legitimately carry fixture-id + zone-id + violation
  sub-rule + clause + remediation across multi-violation cases).
- Missing IR data that the schema declares required is a generator bug
  — emit `passes: false`, `severity: high`, and call out the missing
  field by name.

---

## INV-01 — Anchor-zone catalogue integrity (HIGH)

**Severity:** HIGH

**Rule:** Every `anchor_fixtures[]` entry produces ≥1 `zones[]` entry
attributed to it via `derived_from_anchor_id`. Detected overlaps are
declared via `overlapping_with_zone_ids[]` cross-references on BOTH
overlapping zones — no silent merges or trims.

**Validator action:**
- Enumerate `anchor_fixtures[].anchor_id` values.
- For each anchor, count `zones[]` entries where
  `zone.derived_from_anchor_id == anchor.anchor_id`. Require ≥1.
- For every `zones[i].overlapping_with_zone_ids[j]`, verify the
  reciprocal entry exists on the referenced zone (set the IR-internal
  symmetry property).
- If every anchor has ≥1 zone AND every overlap link is reciprocal:
  PASS. Evidence cites the anchor count + zone count + overlap-pair
  count.
- If any anchor has 0 zones OR any overlap link is one-way: FAIL HIGH.
  Evidence cites the orphan anchor_id OR the one-way overlap pair
  (zone_id_a → zone_id_b without the reverse).

**Citation:** BS 7671:2018 §701 / §702 / §703 / §710 / §715
(top-level Part 7 special-location sections — anchors and zones derive
from these; sub-clause precision applies in INV-03..INV-07).

**Rationale:** Catches anchor-extraction round-trip bugs where the LLM
emitted an anchor and forgot to derive its zone, or detected an overlap
and forgot to declare it. INV-01 is the structural floor — without it,
INV-08 has no zone catalogue to evaluate against. Downstream consumers
relying on the intent payload's `zones_summary[]` depend on this
integrity.

---

## INV-02 — Fixture-audit ↔ flags drift guard (HIGH)

**Severity:** HIGH

**Rule:** One-to-one correspondence:
1. Every `existing_fixtures_audit[i]` with `compliance_status == "violation"`
   has at least one corresponding entry in
   `calculation_summary.non_compliance_flags[]` whose `fixture_id`
   matches the audit entry's `fixture_id`.
2. Conversely, every `non_compliance_flags[j]` whose `fixture_id` field
   is populated points to an `existing_fixtures_audit[i]` with
   `compliance_status == "violation"`.

**Validator action:**
- Build set A: `{fixture_id : audit.compliance_status == "violation"}`.
- Build set B: `{fixture_id : flag.fixture_id is populated}`.
- Verify A ⊆ B AND B ⊆ A (set equality).
- If sets agree: PASS. Evidence cites the count + a representative
  matched pair.
- If A \\ B is non-empty: FAIL HIGH. Evidence names the offending
  audit fixture_id whose violation is missing a flag.
- If B \\ A is non-empty: FAIL HIGH. Evidence names the offending
  flag fixture_id whose audit row says "compliant".

**Citation:** Skill-internal consistency (no external standard — this
is a self-consistency gate on the IR's two redundant arrays).

**Rationale:** Prevents drift between the two arrays that both express
the same fixture-violation truth. Engineers reading the IR look at
either array first; a one-sided emission silently downgrades the
violation visibility on whichever side the reader trusts. INV-02 keeps
both arrays in lockstep.

---

## INV-03 — §710 Group 2 → medical IT system mandatory (HIGH)

**Severity:** HIGH

**Rule:** Every `zones[]` entry with `zone_kind ==
"medical_envelope_group_2"` has a sibling `electrical_constraints[]`
entry with ALL of:
1. `constraint_kind == "medical_it_system"`.
2. `applies_to_zone_ids[]` contains the Group 2 zone's id.
3. `imd_alarm_response_time_s_max == 8`.
4. `supplementary_bonding_max_resistance_ohm == 0.2`.

**Validator action:**
- Enumerate Group 2 zones.
- For each Group 2 zone, search `electrical_constraints[]` for a
  matching `medical_it_system` constraint covering that zone id.
- Verify both numeric thresholds match exactly (8 s, 0.2 Ω).
- If every Group 2 zone has a conformant constraint: PASS. Evidence
  cites the Group 2 zone count + the constraint ids + the verified
  thresholds.
- If any Group 2 zone lacks the constraint OR the thresholds drift:
  FAIL HIGH. Evidence names the Group 2 zone_id + the missing /
  incorrect field + the threshold drift.

**Citation:** `BS 7671:2018+A2:2022 §710` (Part 7 medical locations
top-level) + `BS EN 61557-8` (insulation-monitoring-device alarm
response 8 s) + `HTM 06-01` (NHS Estates precedence on Group 2 IT
sourcing).

**Rationale:** Group 2 is life-support territory (cardiac/intracardiac
procedures, theatres where loss of supply during surgery is fatal). The
IT system + IMD is the §710 mandated isolation/monitoring approach;
the 8 s threshold is BS EN 61557-8's alarm-response limit; the 0.2 Ω
bonding figure is the equipotential floor for galvanic isolation. Any
missing element breaks the cascade life-safety guarantee. INV-03 is
the most safety-critical INV in the catalogue alongside INV-04 + INV-05
+ INV-08.

---

## INV-04 — §701 bathroom + §703 sauna → 30 mA RCD blanket (HIGH)

**Severity:** HIGH

**Rule:**
1. `inputs.room_type ∈ {bathroom, shower_room}` ⇒ an
   `electrical_constraints[]` entry with
   `constraint_kind == "rcd_blanket_by_room"` AND `rcd_rating_ma == 30`
   per `BS 7671:2018+A2:2022 §701.411.3.3`.
2. `inputs.room_type == sauna` ⇒ the same constraint with
   `sauna_heater_excluded: true` per
   `BS 7671:2018+A2:2022 §703.411.3.3` (the sauna heater circuit is
   the exempt circuit; the rest of the sauna remains under the 30 mA
   blanket).

**Validator action:**
- Read `inputs.room_type`.
- If room_type ∈ {bathroom, shower_room, sauna}, search
  `electrical_constraints[]` for an `rcd_blanket_by_room` entry.
- Verify `rcd_rating_ma == 30` exactly.
- For sauna, additionally verify `sauna_heater_excluded == true`.
- If present + correct: PASS. Evidence cites the constraint_id +
  rcd_rating_ma + (for sauna) the heater-excluded flag.
- If missing: FAIL HIGH. Evidence cites room_type + the missing
  constraint.
- If rcd_rating_ma drifts (e.g. 100 mA, 300 mA): FAIL HIGH. Evidence
  cites the drift value + the §701.411.3.3 / §703.411.3.3 verified
  threshold.
- If sauna AND sauna_heater_excluded is missing or false: FAIL HIGH.
  Evidence cites the sauna heater being incorrectly blanketed under
  30 mA RCD.

**Citation:** `BS 7671:2018+A2:2022 §701.411.3.3` (bathroom / shower
30 mA RCD) + `BS 7671:2018+A2:2022 §703.411.3.3` (sauna with explicit
heater circuit exemption).

**Rationale:** 30 mA RCDs are the §701 / §703 baseline life-safety
device for wet-area circuits; ≤30 mA disconnects fast enough to
prevent ventricular fibrillation. The sauna heater is the named
exemption because thermal-cycling RCD nuisance trips are a documented
failure mode AND the heater circuit is dedicated + supervised. Missing
the blanket exposes occupants; missing the heater exclusion guarantees
heater nuisance trips. INV-04 catches both.

---

## INV-05 — §702 pool → main equipotential bonding (HIGH)

**Severity:** HIGH

**Rule:** `inputs.room_type == swimming_pool_hall` ⇒ an
`electrical_constraints[]` entry with:
1. `constraint_kind == "pool_main_equipotential_bonding"`.
2. `extraneous_parts_listed[]` non-empty (the bonded extraneous
   conductive parts — pool shell rebar, ladder, handrail, dive board,
   filtration plant mass, balance tank, etc.).
3. `conductor_csa_min_mm2 >= 10` (10 mm² Cu equivalent — the §702
   main bonding conductor floor).

**Validator action:**
- Read `inputs.room_type`.
- If room_type == swimming_pool_hall, search
  `electrical_constraints[]` for the pool_main_equipotential_bonding
  constraint.
- Verify the constraint exists.
- Verify `extraneous_parts_listed[]` has ≥1 entry.
- Verify `conductor_csa_min_mm2 ≥ 10`.
- If all three pass: PASS. Evidence cites the bonded-parts count +
  the csa value + the constraint_id.
- Else: FAIL HIGH. Evidence cites which sub-condition failed (missing
  constraint / empty list / csa below 10 mm²) and the offending value.

**Citation:** `BS 7671:2018+A2:2022 §702.415.1` (pool main
equipotential bonding) — explicitly NOT §702.55.1 or §702.55.2 (those
sub-clauses do not exist in the verified Part 7-702 file per spec §3.2
banned-citation register; the verified §702.415.1 is the correct
reference).

**Rationale:** Pool environments couple step-and-touch voltages
through pool-water conductance + simultaneous body contact with
multiple metallic surfaces. The §702.415.1 main equipotential bond
equalises every extraneous conductive part to a single reference
potential so even an L-PE fault elsewhere on site cannot energise the
bonded metalwork above the pool reference. Missing the bond is a
documented pool electrocution failure mode. The disambiguation
matters because prior agents repeatedly invented the banned
alternative (NOT §702.55.1 — it does not exist in the verified Part
7-702 file); this validator both detects the §702.415.1 presence AND
rejects the banned alternative as a citation.

---

## INV-06 — Whirlpool bath → pump circuit constraint (HIGH)

**Severity:** HIGH

**Rule:** Any `anchor_fixtures[]` entry with `anchor_kind == "bath_basin"`
AND `bath_kind == "whirlpool"` ⇒ an `electrical_constraints[]` entry
with:
1. `constraint_kind == "whirlpool_pump_circuit"`.
2. `pump_position_zone` populated (Zone 1 or Zone 2 per the anchor's
   derived zones).
3. `requires_local_isolation: true`.
4. `ip_rating_min` ≥ IPx5 (the §701.512.2 ingress-protection floor
   where water jets are present).

**Validator action:**
- Filter `anchor_fixtures[]` to entries with anchor_kind == bath_basin
  AND bath_kind == whirlpool.
- For each such anchor, search `electrical_constraints[]` for the
  whirlpool_pump_circuit constraint.
- Verify the constraint exists.
- Verify the 4 sub-fields above.
- If all sub-fields pass: PASS. Evidence cites the anchor_id +
  pump_position_zone + ip_rating_min + the verified flags.
- Else: FAIL HIGH. Evidence cites the anchor_id + which sub-field is
  missing or wrong.

**Citation:** `BS 7671:2018+A2:2022 §701` (Part 7-701 top-level —
bathroom envelope) + `BS 7671:2018+A2:2022 §701.512.2` (IPx5 selection
where water jets present — applies to whirlpool agitation/jet streams).

**Rationale:** Whirlpool baths embed a pump in the same envelope as the
bather; the pump cable + isolation + IP rating drive whether a
seal-failure flashes the water or trips the protective device. IPx5 is
the §701.512.2 baseline because whirlpool jets are categorical "water
jets". Local isolation lets the bather kill the pump from the bath
without crossing the room. Missing any sub-condition exposes the
bather. INV-06 is the only INV that gates on a per-anchor attribute
(bath_kind) rather than the room_type.

---

## INV-07 — ELV §715 anchor → separation constraint (HIGH)

**Severity:** HIGH

**Rule:** Any `anchor_fixtures[]` entry with `anchor_kind ==
"elv_lighting_circuit_anchor"` ⇒ an `electrical_constraints[]` entry
with:
1. `constraint_kind == "elv_separation"`.
2. `lv_cable_spacing_mm_min` populated (the §715 LV ↔ ELV cable spacing
   floor).
3. `barrier_required: true` (where the spacing alone cannot guarantee
   isolation).
4. `label_required: true` (the §715 ELV-circuit label).
5. `transformer_short_circuit_protected: true` (the BS EN 61558-2-6
   short-circuit-protected safety transformer requirement).

**Validator action:**
- Filter `anchor_fixtures[]` to elv_lighting_circuit_anchor entries.
- For each anchor, search `electrical_constraints[]` for the
  elv_separation constraint.
- Verify the 5 sub-fields above.
- If all pass: PASS. Evidence cites the anchor_id + the spacing value +
  the boolean flags.
- Else: FAIL HIGH. Evidence cites the anchor_id + which sub-field
  failed.

**Citation:** `BS 7671:2018+A2:2022 §715` (Part 7-715 ELV lighting
top-level) + `BS EN 61558-2-6` (safety isolating transformers —
short-circuit-protected variant required for §715 SELV/PELV systems).

**Rationale:** §715 ELV lighting depends structurally on
electrical-separation discipline: the LV side must never bleed into the
ELV side via cable proximity, shared trunking, or transformer fault.
The cable-spacing floor, barrier requirement, label, and
short-circuit-protected transformer are the four §715 / BS EN 61558-2-6
controls that together preserve the SELV/PELV touch-voltage guarantee.
Missing any one degrades the separation. INV-07 enforces all four
simultaneously.

---

## INV-08 — Existing fixture placement compliance (HIGH)

**Severity:** HIGH

**Rule:** For every fixture in `consumed_intents.lighting_layout`
(fixtures from upstream lighting-layout) OR `inputs.existing_fixtures[]`
(engineer-supplied existing layout), evaluate ALL FOUR sub-rules
against the fixture's containing zone (the `zones[]` entry whose
polygon contains the fixture's (x_mm, y_mm) position):

- **(a) Prohibited fixture type:** `fixture.fixture_type` ∉
  `containing_zone.prohibited_fixture_types[]`.
- **(b) IP rating floor:** `fixture.ip_rating` ≥
  `containing_zone.ip_rating_min` (compare per the IPx digit ordering
  — IPX4 < IPX5 < IPX7 etc).
- **(c) Switch position distance:** if `fixture.fixture_type ==
  "switch"`, the switch's horizontal distance to the nearest Zone 1
  boundary ≥ `containing_zone.switch_position_min_distance_mm`.
  (Switch fixtures sited inside Zone 1 itself are always non-compliant
  in §701 envelopes — emit the violation regardless of distance.)
- **(d) Voltage cap:** `fixture.max_voltage_v` ≤
  `containing_zone.max_voltage_v`.

Each violation produces:
1. One `existing_fixtures_audit[]` entry with
   `compliance_status == "violation"` and `severity ∈ {critical, high}`.
2. One `calculation_summary.non_compliance_flags[]` entry naming the
   fixture_id + the offending sub-rule + the clause + ≥40-char message.

**Validator action:**
- Build the merged fixture list: union of
  `consumed_intents.lighting_layout` fixtures + `inputs.existing_fixtures[]`.
- For each fixture, find the containing zone via polygon-point test.
- Evaluate (a)/(b)/(c)/(d) in turn.
- Count violations.
- Verify each violation appears in BOTH the audit array AND the flags
  array (cross-check with INV-02).
- If zero violations: PASS. Evidence cites the fixture count + the
  zone-coverage map.
- If violations present: emit one INV-08 evidence string per violation
  group (within the 1200-char cap) naming fixture_id + zone_id +
  sub-rule letter + the specific value vs threshold +
  recommended remediation (e.g. "relocate to Zone 2", "swap for IPx5
  variant", "increase switch standoff to 600 mm"). INV-08 passes if
  every detected violation is correctly recorded in both arrays; it
  fails HIGH if a violation was DETECTED but not recorded, or recorded
  with the wrong sub-rule letter.

**Citation:** `BS 7671:2018+A2:2022 §701.512.3` (socket / switch
position in bathrooms — sub-rule c) + `BS 7671:2018+A2:2022 §710`
(medical fixture type restrictions — sub-rule a) + `BS 7671:2018+A2:2022
§715` (ELV voltage cap — sub-rule d) + `BS 7671:2018+A2:2022 §522`
(general IP / ingress protection by external influence — sub-rule b).

**Rationale:** INV-08 is the **central engineering value** of the
special-locations skill. The 4 sub-rules collectively express the
fixture-vs-zone safety contract that §701/§702/§703/§710/§715 each
encode in their own terms; rather than carrying 5 parallel sub-INVs,
the catalogue consolidates them into one rule with 4 sub-checks.
Consumer skills (lighting-layout INV-12 / small-power INV-12 /
db-layout INV-16) read this INV's verdict + non_compliance_flags[] and
cascade the failure into their own non_compliance_flags[]. If INV-08
silently passes a violation, the downstream cascade never trips and
the engineer ships a non-compliant layout. INV-08 is the most
load-bearing INV in this skill's catalogue.

---

## INV-09 — Anchor extraction provenance disclosure (MEDIUM)

**Severity:** MEDIUM

**Rule:** Every `anchor_fixtures[]` entry has:
1. `_extraction_source` in the 3-tier enum
   `{ifc_attribute, geometry_inference, engineer_supplied}` per the
   skill's honest-disclosure register.
2. `_provenance_note` ≥40 chars (the threshold preserves the D2.3
   minimum that carries archetype + source + caveat + date in human
   prose; shorter strings cannot carry all four content elements).

**Validator action:**
- For each anchor in `anchor_fixtures[]`:
  - Verify `_extraction_source` ∈ the 3-tier enum.
  - Verify `len(_provenance_note) ≥ 40`.
- If every anchor passes both: PASS. Evidence cites the anchor count +
  a representative provenance snippet.
- Else: FAIL MEDIUM. Evidence cites the offending anchor_id + which
  field failed (enum value vs string length).

**Citation:** Skill honest-disclosure discipline per spec §3.2 +
D2.3 lineage pattern (no external standard — engineering hygiene gate).

**Rationale:** Provenance under 40 chars routinely loses the
manufacturer / archetype / date / caveat content that downstream
reviewers need to judge anchor reliability. INV-09 is MEDIUM rather
than HIGH because a weak provenance string degrades reviewer
confidence but does not by itself create a §701/§702/§703/§710/§715
non-compliance — failing INV-09 does NOT toggle
`calculation_summary.compliant` to false (only HIGH/critical fails do
that). The flag still ships so the engineer sees the hygiene issue.

---

## INV-10 — Compliant rollup self-consistency (HIGH)

**Severity:** HIGH

**Rule:** If `calculation_summary.compliant == true`, then ALL of:
1. `calculation_summary.violation_count_critical == 0`.
2. `calculation_summary.violation_count_high == 0`.
3. `calculation_summary.non_compliance_flags[]` is empty.
4. No `zones[]` entry has a non-empty `overlapping_with_zone_ids[]`.

Conversely, if any of the above is non-zero / non-empty, `compliant`
MUST be false.

**Validator action:**
- Read `calculation_summary.compliant`.
- Cross-check the 4 sub-conditions.
- If `compliant == true` AND all 4 sub-conditions hold: PASS. Evidence
  cites all four zero/empty values.
- If `compliant == false` AND at least one sub-condition is violated:
  PASS. Evidence cites the first non-zero / non-empty value that
  justifies the false rollup.
- If `compliant == true` BUT any sub-condition is violated: FAIL HIGH.
  Evidence names the contradicting field (e.g. "compliant=true but
  violation_count_critical=2").
- If `compliant == false` BUT all 4 sub-conditions hold: FAIL HIGH.
  Evidence states the rollup is needlessly pessimistic (engineer
  should be told the IR is clean).

**Citation:** Skill-internal consistency (no external standard — this
gate prevents the IR from contradicting its own summary).

**Rationale:** Engineers read `calculation_summary.compliant` first
when triaging an IR; if that flag contradicts the violation counts /
flags / overlap state, the rollup misleads them either toward false
confidence or false alarm. INV-10 keeps the summary honest. Combined
with INV-02 (fixture-audit ↔ flags drift), the IR's three summary
surfaces (compliant flag + counts + flags array) stay in lockstep.

---

## Validator output

After running all 10 INVs, the IR's `invariants[]` array carries 10
entries in numeric order INV-01 → INV-10. Each entry includes
example-specific evidence (NOT boilerplate; cite IR values).

### Citation discipline

Every `invariants[].evidence` string and every
`non_compliance_flags[].clause` MUST cite ONLY verified clauses from
spec §3.2 standards xref table. The full verified sub-clause set
permitted in evidence / clause fields:

- `§701.411.3.3` (bathroom 30 mA RCD)
- `§701.512.2` (IPx5 where water jets used — whirlpool)
- `§701.512.3` (socket / switch position in bathrooms)
- `§701.414.4.5` (SELV ≤12 V Zone 0)
- `§701.415.2` (supplementary bonding bathroom)
- `§702.415.1` (pool main equipotential bonding — INV-05)
- `§702.415.2` (pool supplementary bonding)
- `§702.55.4` (Zone 2 changing-room overlap — D-2)
- `§703.411.3.3` (sauna RCD with heater exemption — INV-04)
- `§522` (general IP by external influence — INV-08 sub-rule b)
- Top-level Part 7 anchors: `§701`, `§702`, `§703`, `§710`, `§715`
- Cross-refs: `HTM 06-01`, `BS EN 61557-8`, `BS EN 61558-2-6`,
  `BS EN 60601`, `BS 5266-1`, `IET GN7`

### Banned-citation guard

The following 14 sub-clauses were invented by prior agents and are
BANNED at spec §3.2. They MUST NOT appear in any
`invariants[].evidence`, `non_compliance_flags[].clause`, or
constraint rationale. Written in dot-notation to avoid grep
self-trips:

> `§701` dot 32, `§701` dot 55, `§702` dot 55 dot 1, `§702` dot 55 dot 2,
> `§702` dot 32, `§703` dot 55, `§703` dot 512, `§703` dot 413,
> `§710` dot 413 dot 1 dot 5, `§710` dot 314, `§710` dot 411 dot 3 dot 3,
> `§715` dot 560 dot 4, `§715` dot 521, `§715` dot 422.

These do NOT exist in the verified BS 7671:2018+A2:2022 file. If any
appear in your output, the golden CI banned-citation grep will flag
them and the implementer review will reject the IR. When you need a
rule that one of these would have covered, cite the generic top-level
(§701 / §702 / §703 / §710 / §715) PLUS a verified cross-reference
(HTM 06-01 / BS EN 61557-8 / BS EN 61558-2-6 / BS EN 60601 /
BS 5266-1 / IET GN7).

### non_compliance_flags[] emission for FAILED INVs

For each FAILED INV, append a `calculation_summary.non_compliance_flags[]`
entry with:

- `flag`: short stable identifier matching the INV id (e.g.
  `"inv_03_medical_it_missing"`).
- `severity`:
  - `critical` when the failure is INV-03 (medical IT) OR INV-04
    (30 mA RCD missing entirely, NOT just heater-exclusion drift) OR
    INV-05 (pool bonding) OR INV-08 sub-rules (a)/(b)/(d) on a
    §710 medical envelope.
  - `high` for all other INV-01 / INV-02 / INV-04 (heater-exclusion
    drift only) / INV-06 / INV-07 / INV-08 (non-medical envelopes) /
    INV-10 failures.
  - `warning` for INV-09 failures (provenance hygiene; non-safety).
  - `info` is reserved — do not emit for INV failures.
- `clause`: a verified citation per the standards xref table above
  (banned clauses rejected per the dot-notation register).
- `message`: ≥40 char prose stating the violation + a remediation hint
  the engineer can act on (e.g. "Relocate switch S03 from Zone 1 to a
  position ≥600 mm horizontally outside Zone 1 boundary, OR specify a
  Zone 1-rated cord-operated switch.").
- `fixture_id` / `zone_id` populated where the failure attributes to a
  specific fixture or zone (INV-08 always populates fixture_id +
  zone_id).

### compliant-flag toggling

- Any FAILED INV with severity `critical` or `high`
  → set `calculation_summary.compliant = false`.
- A FAILED INV-09 (severity `warning`) does NOT toggle `compliant` to
  false but DOES add the flag entry — the engineer sees the
  provenance issue without the rollup contradicting itself.
- INV-10 then verifies the `compliant` flag agrees with the rollup; a
  drift here is itself a HIGH failure (the rollup self-consistency
  gate).

### Cross-skill cascade

When this skill's IR has any FAILED INV among INV-03, INV-04, INV-05,
INV-06, INV-07, INV-08, the intent payload (`special_locations_zoning`
shape per `schemas/special-locations-intent.schema.json`) carries the
non_compliance_flags[] forward so consumer skills can react:

- lighting-layout v1.6 INV-12 reads
  `consumed_intents.special_locations_zoning.non_compliance_flags[]` +
  flips its own non_compliance_flags[] HIGH for fixture violations
  inside zones.
- small-power v1.2 INV-12 does the equivalent for sockets.
- db-layout v1.5 INV-16 reflects the §701/§703 30 mA RCD blanket and
  the §710 IT system into board-side protection devices.

This is the canonical special-locations → consumer-skill failure
propagation path established in spec §3 (cross-skill cascade
contract). The reviewer prompt (`prompts/reviewer.md`) runs after
this validator and exercises engineering-judgment D-checks that sit
beyond validator-enforceable rules (anchor-extraction defensibility,
Zone-2 changing-room overlap judgement, medical group sourcing,
sauna heater exemption boundary, ELV separation across multiple
fixtures).
