# Reasoning — cascade-small-power-uk-bathroom-violation (FAIL HIGH)

## Cascade context — FAIL HIGH

This is a **failure-mode** cascade — the central engineering value demo
for the small-power consumer hand-off. The synthetic upstream
small-power intent (at
`electrical/small-power/examples/uk-bathroom-violation-cascade-source/intent-out.json`)
ADDS a violating 230 V socket on top of the 3 compliant fixtures
from cascade #9.

`compliant=false`; 1 critical `non_compliance_flag` with
`_cascaded_from: special-locations` (this skill is the authoritative
side of the §701 zone-table rule).

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` includes 3 compliant + 1 violating
  fixture with `_consumed_from` markers.
- `consumed_lighting_layout_intent` in intent-out points at the synthetic
  upstream small-power intent.

## Step 1 — Room classification

Identical to cascade #9: bathroom; 2 700 × 2 100 mm; ceiling 2 400 mm.

## Step 2 — Anchor inventory

Identical to cascade #9: `bath_1` + `shower_1`.

## Step 3 — Zone derivation (BS 7671:2018 §701)

5 zones (same as cascade #9). bath_zone_1 polygon = `(500, 0)-(2200, 700)`,
height range 550-2250 mm, `max_voltage_v: 230`,
`prohibited_fixture_types: [socket_230v, switch_230v, luminaire_non_ip_rated]`.

## Step 4 — Per-zone safety properties

Identical to cascade #9. Critical for this cascade: bath_zone_1's
`prohibited_fixture_types` includes `socket_230v` — sockets are
prohibited in Zone 1 per §701 zone-table.

## Step 5 — Electrical constraint derivation

Identical to cascade #9: `rcd_blanket_by_room` per §701.411.3.3.

## Step 6 — Consume small-power intent (the FAILURE)

4 fixtures consumed: 3 compliant (cascade #9 set) + 1 VIOLATING:

| fixture_id            | type            | position (x,y,z)       | derived_zone_id        | status     |
|-----------------------|-----------------|------------------------|------------------------|------------|
| `lum_1`               | luminaire       | (1350, 1400, 2400)     | null                   | compliant  |
| `lum_2`               | luminaire       | (1050, 350, 2400)      | null                   | compliant  |
| `shaver_1`            | shaver_socket   | (2400, 1800, 1400)     | null                   | compliant  |
| `socket_violation_1`  | **socket_230v** | **(1200, 350, 1100)**  | **zone_bath_1_z1**     | **VIOLATION** |

`socket_violation_1` at (1200, 350, 1100):

- Plan position (1200, 350): INSIDE bath_zone_1 polygon
  `(500, 0)-(2200, 700)` — checking: 500 ≤ 1200 ≤ 2200 ✓ AND 0 ≤ 350 ≤
  700 ✓.
- Vertical: z=1100 INSIDE bath_zone_1 height range 550-2250 mm.
- `derived_zone_id: zone_bath_1_z1` (the §701 derivation places this
  socket squarely INSIDE Zone 1).

## Step 7 — INV-08 sub-rule walk-through (the FAILURE)

For `socket_violation_1`:

- **(a) type_prohibited FIRES.** `socket_230v` is in
  `bath_zone_1.prohibited_fixture_types` per §701 zone-table. Sockets
  are prohibited in Zone 1 entirely. **FAIL.**
- **(b) ip_below_min** (would fail conceptually — IPx0 socket in
  Zone 1 which requires IPx4 — but (a) is the recorded primary fail
  per §701 fixture-audit convention).
- **(c) switch_distance_too_close** (trivially violated — the position
  is IN Zone 1, not just within 3 m of it — but again (a) is the
  primary fail).
- **(d) voltage_above_max** (230 V ≤ Zone 1 max_voltage 230 V, so this
  sub-rule actually PASSes for Zone 1 — Zone 1 permits 230 V class_1/2
  with RCD, just not socket fixture types).

`violation_sub_rule: type_prohibited`. `violation_clause: BS 7671:2018
§701.512.3`. `severity: critical`.

The other 3 fixtures pass all 4 sub-rules (cascade #9 set). Total
audit: **3 compliant + 1 violation; 1 critical violation; 1
non_compliance_flag**.

## Step 8 — non_compliance_flag emitted

```json
{
  "flag": "socket_in_zone_1",
  "severity": "critical",
  "fixture_id": "socket_violation_1",
  "zone_id": "zone_bath_1_z1",
  "clause": "BS 7671:2018 §701.512.3",
  "message": "230V socket_violation_1 placed at (1200, 350, 1100) sits INSIDE bath_zone_1 polygon ... Remediation: relocate ... AND re-type as shaver_socket if it must remain ...",
  "_cascaded_from": "special-locations"
}
```

`_cascaded_from: special-locations` tells consumer skills: **this skill
is the authoritative side of the §701 zone-table rule**. small-power
must propagate this flag, not override it.

## Step 9 — Invariants

- **INV-01** zone catalogue integrity. PASS (zone derivation is
  unchanged from cascade #9).
- **INV-02** audit ↔ flags 1:1. PASS (1 violation entry ↔ 1
  non_compliance_flag; catalogue integrity holds).
- **INV-03** medical IT N/A. PASS vacuously.
- **INV-04** rcd_blanket_by_room PRESENT. PASS.
- **INV-05** main equipotential bonding N/A. PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** sub-rule audit: 12 sub-rule evaluations for the 3
  compliant fixtures all PASS; 1 sub-rule (type_prohibited) for
  `socket_violation_1` FAILS. **INV-08 FAILS overall.**
- **INV-09** anchor provenance strongest tier. PASS.
- **INV-10** rollup self-consistency: compliant=false because
  violation_count_critical=1 > 0; self-consistency holds (the
  compliant flag correctly mirrors the violation count). The check
  semantics: compliant ⟺ no critical/high violations + empty flags. The
  compliant=false verdict ⟺ violation_count_critical=1 + 1 flag.
  **INV-10 FAILS in the sense that the rollup is non-compliant (the
  passes flag tracks the COMPLIANT-AND-CONSISTENT criterion). The
  cascade-core failure signal is the compliant=false verdict propagating
  downstream correctly.**

## Step 10 — Consumer-side hand-off — small-power INV-12 FAIL HIGH

When small-power v1.2 consumes this special-locations intent:

1. **Zone exclusion** sub-check 1 iterates the consumed socket
   catalogue. `socket_violation_1` is inside `zone_bath_1_z1`
   polygon AND inside its vertical envelope → small-power INV-12 sub-check
   1 FIRES with severity=critical.
2. Propagates a non_compliance_flag with `clause: BS 7671:2018
   §701.512.3`, `severity: critical`, and `_cascaded_from:
   special-locations` PRESERVED (the small-power side doesn't change
   the provenance marker; the authoritative side remains
   special-locations).
3. small-power's output IR's `compliant` flag flips to false; its
   `calculation_summary.violation_count_critical` bumps to 1.

The cascade chain integrity is preserved end-to-end. The non-compliance
is detected at the special-locations layer and surfaces faithfully at
every downstream layer.

## Step 11 — Remediation

Per `non_compliance_flags[0].message`:

1. **Relocate the socket OUTSIDE Zone 2 polygon** — Zone 2 unclipped
   extends to `(-100, -600)-(2800, 1300)`. After room clipping the
   socket must be at y ≥ 3700 (3 m from Zone 1 y=700 boundary).
2. **OR re-type as `shaver_socket`** — BS EN 61558-2-5 isolating-
   transformer shaver sockets are explicitly permitted in Zone 2 per
   §701 zone-table derogation, even at IPx0.

For a typical UK domestic bathroom 2 700 × 2 100 mm, option (1) is
geometrically impossible (room max y = 2 100 < required y ≥ 3 700).
Option (2) — `shaver_socket` re-type + relocate to Zone 2 — is the
standard remediation.

## Step 12 — Honest disclosures

- **Synthetic upstream small-power intent.** small-power v1.2 hand-off
  not yet shipped; cascade contract integrity verified via golden CI
  Pass 4.
- **The FAIL HIGH outcome is the CENTRAL ENGINEERING VALUE.** This
  cascade demonstrates that the cascade chain catches the §701 zone-table
  violation at the special-locations layer (NOT at the downstream small-
  power layer). The non_compliance_flag's `_cascaded_from:
  special-locations` marker tells consumer skills "this is the
  authoritative side of the rule; don't try to override".
- **Sub-rule recording convention.** Even though multiple sub-rules
  conceptually fire for the violating socket, §701 fixture-audit
  records the PRIMARY sub-rule (here: `type_prohibited`). Consumer
  skills only need the primary sub-rule + clause to take action.

## Step 13 — Failure modes considered

If `socket_violation_1` were re-typed as `shaver_socket` (the
remediation), the BS EN 61558-2-5 derogation would apply for Zone 2
ONLY. The socket would STILL violate Zone 1 (at z=1100, inside Zone 1
vertical range 550-2250 + inside Zone 1 plan polygon). To pass, the
socket must be EITHER (a) outside both Zone 1 plan polygon and Zone 2
3m-exclusion ring (geometrically impossible in this room) OR (b) inside
Zone 2 only (above the bath polygon but below z=2250) AS A SHAVER_SOCKET
ONLY (BS EN 61558-2-5 isolating-transformer derogation).

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-bathroom-standard-bath-and-shower/`
- Compliant cascade: cascade #9 (`cascade-lighting-layout-uk-bathroom`)
- Spec §9.2 cascade row 12: FAIL HIGH case (the central engineering
  value demo)
- Plan portion 3 Task C.2 Step 3
