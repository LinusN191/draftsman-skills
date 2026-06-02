# Reasoning — cascade-small-power-uk-external-elv-with-violation (FAIL HIGH)

## Cascade context — FAIL HIGH

The second FAIL HIGH cascade — failure-mode demo for §715 ELV/LV
separation enforcement. The synthetic upstream small-power intent (at
`electrical/small-power/examples/uk-elv-violation-cascade-source/intent-out.json`)
ADDS a violating 230 V LV socket inside the `elv_barrier_zone` of
`elv_bollard_1`.

`compliant=false`; 1 critical `non_compliance_flag` with
`_cascaded_from: special-locations`. INV-07 still PASSes
(`elv_separation` constraint IS present); INV-08 + INV-10 FAIL.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` includes 6 compliant ELV luminaires + 1 violating
  LV socket.
- D-5 (external/no ambient temp) + D-1 (bollard_6 inferred provenance)
  reviewer judgments carry forward from C.1 source.

## Step 1 — Room classification

Identical to C.1 source: `external_landscape`; 20 000 × 15 000 mm
landscape area; ceiling 3 000 mm; `is_external: true`.

## Step 2 — Anchor inventory

Identical to C.1 source: 6 ELV bollard anchors (elv_bollard_1 through
elv_bollard_6). elv_bollard_1 through 5 sourced via
`architectural_drawing_extraction` (strongest) or `engineer_manual_entry`
(mid); elv_bollard_6 via `inferred_from_room_type` (weakest tier — drives
D-1 informational flag).

## Step 3 — Zone derivation (BS 7671:2018 §715)

6 elv_barrier_zones, one per bollard. Each is a 500 mm-radius 12-sided
polygon around the bollard centroid; height 0-1500 mm. Properties:

- `max_voltage_v: 12` (SELV only).
- `ip_rating_min: IPx4`.
- `prohibited_fixture_types: [socket_230v, luminaire_lv_non_selv]`.
- `_clause_citation: "BS 7671:2018 §715 + BS EN 61558-2-6 (no §715
  sub-clauses in verified file)"`.

The barrier zone IS the §715 separation rule encoded geometrically.

## Step 4 — Electrical constraint derivation

Single constraint: `elv_separation` per §715 + BS EN 61558-2-6.

## Step 5 — Consume small-power intent (the FAILURE)

7 fixtures consumed: 6 compliant ELV luminaires (on bollard centroids)
+ 1 VIOLATING LV socket:

| fixture_id              | type            | position (x,y,z)       | derived_zone_id                | status     |
|-------------------------|-----------------|------------------------|--------------------------------|------------|
| `elv_bollard_1..6`      | elv_luminaire   | (on each bollard)      | own barrier zone               | compliant  |
| `lv_socket_violation_1` | **socket_230v** | **(3200, 3000, 800)**  | **zone_elv_bollard_1_barrier** | **VIOLATION** |

`lv_socket_violation_1` at (3200, 3000, 800):

- Plan distance to `elv_bollard_1` centroid (3000, 3000) = 200 mm
  (Euclidean) < 500 mm barrier radius → INSIDE the barrier in plan.
- Vertical z = 800 mm INSIDE barrier height range 0-1500 mm.
- `derived_zone_id: zone_elv_bollard_1_barrier`.

## Step 6 — INV-07 PASS — constraint IS present

INV-07 verifies the `elv_separation` constraint is present in
`electrical_constraints[]` when ELV anchors exist. The constraint IS
present (carried forward from C.1 source) — the §715 + BS EN 61558-2-6
separation rule is correctly derived.

**INV-07 PASSes.**

The §715 violation is at the FIXTURE-AUDIT layer (INV-08 sub-rule), not
at the constraint-derivation layer. This decoupling is per spec §7.2:
constraint derivation and fixture audit are independent invariants.

## Step 7 — INV-08 sub-rule walk-through (the FAILURE)

For `lv_socket_violation_1`:

- **(a) type_prohibited** would fire: `socket_230v` is in
  `elv_barrier_zone.prohibited_fixture_types`.
- **(b) ip_below_min:** IPx5 ≥ IPx4 minimum. PASS.
- **(c) switch_distance_too_close:** N/A on barrier zone (no
  switch-distance rule on ELV barriers). PASS.
- **(d) voltage_above_max FIRES:** 230 V > zone.max_voltage_v 12 V SELV
  per §715. **FAIL.**

The audit records **`voltage_above_max`** as the primary sub-rule
because §715 is fundamentally a VOLTAGE-separation rule — the barrier
zone EXISTS to enforce voltage separation between ELV and LV cabling.
(Sub-rule (a) `type_prohibited` is a derived consequence of the voltage
ban; the underlying §715 mechanism is voltage separation.)

`violation_sub_rule: voltage_above_max`. `violation_clause: BS 7671:2018
§715`. `severity: critical`.

The other 6 fixtures (ELV luminaires on bollard centroids) all pass —
they sit on their own bollard centroid, IPx5 ≥ IPx4 minimum, 12 V ≤
zone max 12 V, no switch-distance rule on barrier. **6 compliant + 1
violation; 1 critical violation; 1 non_compliance_flag.**

## Step 8 — non_compliance_flag emitted

```json
{
  "flag": "lv_socket_in_elv_barrier_zone",
  "severity": "critical",
  "fixture_id": "lv_socket_violation_1",
  "zone_id": "zone_elv_bollard_1_barrier",
  "clause": "BS 7671:2018 §715",
  "message": "230V LV socket_violation_1 placed at (3200, 3000, 800) sits INSIDE the elv_barrier_zone of elv_bollard_1 (500mm radius around bollard at (3000, 3000); z=800 within height range 0-1500). socket_230v at 230V is in zone.prohibited_fixture_types per BS 7671:2018 §715 (ELV/LV separation barrier) — max_voltage_v in this zone is 12V SELV. Remediation: relocate the LV socket OUTSIDE the 500mm barrier radius around every elv_bollard AND ensure ≥100mm cable separation between ELV and LV cabling per §715 + BS EN 61558-2-6.",
  "_cascaded_from": "special-locations"
}
```

## Step 9 — Invariants

- **INV-01** zone catalogue: 6 anchors → 6 barrier zones. PASS.
- **INV-02** audit ↔ flags 1:1. PASS (1 violation ↔ 1 flag; integrity
  holds).
- **INV-03** medical IT N/A. PASS vacuously.
- **INV-04** rcd_blanket N/A (external landscape). PASS vacuously.
- **INV-05** main equipotential bonding N/A. PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** elv_separation constraint PRESENT. **PASS** — the cascade-
  core teaching point: INV-07 verifies CONSTRAINT presence, not
  fixture-audit correctness.
- **INV-08** sub-rule audit: 24 sub-rule evaluations for the 6
  compliant fixtures all PASS; 1 sub-rule (voltage_above_max) for
  `lv_socket_violation_1` FAILS. **INV-08 FAILS overall.**
- **INV-09** anchor provenance: weakest tier is
  `inferred_from_room_type` (elv_bollard_6) → D-1 informational flag.
  ≥40-char provenance notes maintained. PASS.
- **INV-10** rollup self-consistency: compliant=false because
  violation_count_critical=1 > 0. The compliant flag correctly mirrors
  the violation count. The check's passes flag tracks the COMPLIANT-
  AND-CONSISTENT criterion. **INV-10 FAILS** (the rollup is
  non-compliant).

## Step 10 — Consumer-side hand-off — small-power INV-12 FAIL HIGH

When small-power v1.2 consumes this special-locations intent:

1. **Zone exclusion** sub-check 1 iterates the consumed socket
   catalogue. `lv_socket_violation_1` is inside
   `zone_elv_bollard_1_barrier` polygon AND inside its vertical
   envelope → small-power INV-12 FIRES with severity=critical.
2. Propagates a non_compliance_flag with `clause: BS 7671:2018 §715`,
   `severity: critical`, `_cascaded_from: special-locations` PRESERVED.
3. small-power's output IR's `compliant` flag flips to false; its
   `calculation_summary.violation_count_critical` bumps to 1.

## Step 11 — Remediation

Per `non_compliance_flags[0].message`:

1. **Relocate the LV socket OUTSIDE the 500 mm barrier radius around
   every elv_bollard** (6 barriers total in this installation —
   geometric constraint).
2. **Ensure ≥100 mm cable separation** between ELV and LV cabling per
   §715 + BS EN 61558-2-6.

Typical landscape practice: route LV cabling along a separate
trench/duct or via a fixed barrier (concrete edging) from the ELV
bollard circuit. A common solution is to feed the LV socket from a
dedicated LV circuit ending at a weatherproof socket assembly OUTSIDE
all barrier zones.

## Step 12 — D-5 + D-1 reviewer judgments — carried forward

- **D-5** — external installation (`room.is_external=true`) without
  `ambient_temperature_c` supplied. Default 30 °C cable de-rating per
  BS 7671:2018 Appendix 4 Table 4B1 assumed; engineer-of-record to
  verify against installation-site temperature data before sign-off.
- **D-1 (informational, not blocking)** — `elv_bollard_6` sourced via
  `inferred_from_room_type` (weakest provenance tier per INV-09);
  engineer-of-record to verify final feature-tree centroid position.

Both flags carry forward from C.1 source. They do NOT change the
`compliant=false` verdict (which is driven by the §715 critical
violation, not the reviewer judgments). The downstream cascade
consumers should surface both judgments alongside the §715 violation.

## Step 13 — Honest disclosures

- **Synthetic upstream small-power intent.** small-power v1.2 hand-off
  not yet shipped; cascade contract integrity verified via golden CI
  Pass 4.
- **The FAIL HIGH outcome is the CENTRAL ENGINEERING VALUE.** This
  cascade demonstrates that the cascade chain catches the §715
  ELV/LV-separation violation at the special-locations layer. The
  non_compliance_flag's `_cascaded_from: special-locations` marker
  preserves authoritative-side provenance through the chain.
- **INV-07 PASS + INV-08 FAIL is by design.** The §715 elv_separation
  constraint is correctly DERIVED (so INV-07 passes); the fixture
  AUDIT catches the violation (so INV-08 fails). Decoupling
  constraint-derivation from fixture-audit is the cascade-architecture
  teaching point per spec §7.2.

## Step 14 — Failure modes considered

If `lv_socket_violation_1` were re-typed as `elv_luminaire` at 12 V,
sub-rule (d) `voltage_above_max` would NOT fire (12 V ≤ 12 V), sub-rule
(a) `type_prohibited` would NOT fire (elv_luminaire permitted), and the
cascade verdict would flip to compliant=true. This isn't a remediation
(it's a different fixture type entirely) but it illustrates the §715
voltage-separation mechanism.

If the LV socket were placed at (4000, 3000, 800) — 1 000 mm from
elv_bollard_1 centroid AND outside all 6 barrier zones — the cascade
verdict would flip to compliant=true. This IS the remediation path.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-external-landscape-elv-lighting/`
- Spec §9.2 cascade row 14: FAIL HIGH case
- Plan portion 3 Task C.2 Step 5
