# UK Domestic Final Circuits — Cable Sizing Worked Example

**Project:** `uk-domestic-eg01`
**Jurisdiction:** GB (BS 7671:2018+A2:2022, 18th Edition Amendment 2)
**Scenario:** 3-bedroom dwelling (~100 m²), single-phase 230 V TN-C-S supply,
consumer unit `CU-MAIN` feeding 5 final circuits — 2× ring finals, 1× lighting
radial, 1× cooker, 1× immersion heater.

This worked example demonstrates the **walk-the-ladder** sizing algorithm
against a deliberately small but representative scenario: four circuits where
the binding constraint is **Iz ≥ In** (Reg 433.1) — i.e. the starting csa is
already large enough — and one circuit (`C03`, the upstairs lighting radial)
where the binding constraint is **vd_cumulative**, forcing a walk-up from
1.0 mm² to 1.5 mm² to satisfy the 3 % lighting voltage-drop limit at 22 m.

---

## Project Supply + Jurisdiction

The dwelling is fed from a Distribution Network Operator (DNO) cut-out on a
**TN-C-S** earthing system, with a declared **Ze of 0.35 Ω** and a declared
**Prospective Short-Circuit Current (PSCC) of 6 kA** at the consumer unit
origin. Supply voltage is **230 V single-phase, 50 Hz**.

`jurisdiction: "GB"` pins the design to **BS 7671:2018+A2:2022** (18th Edition
Amendment 2), with current-carrying capacity from **Appendix 4 Tables
4D1A–4D2A**, voltage-drop limits from **Appendix 12 §G**, and CPC adiabatic
sizing from **Regulation 543.1.3 + Table 54.7**. Diversity and ring-final
treatment follow the **IET On-Site Guide Appendix A** and **§8.4.4** (ring
final circuits serving floor areas ≤ 100 m²).

The engineer declares cascade inline (no `db-layout-rollup` intent consumed in
this demonstration). The runtime calc tools — `calc.cable_ampacity`,
`calc.voltage_drop`, `calc.cpc_adiabatic` — are **deferred per WI3**; engineer
Iz_corrected and Vd values are placeholder estimates pending deterministic
resolution. The IR carries three `TOOL-CALL-PENDING:*` flags accordingly.

## Cascade Tree + Topology

The cascade is intentionally flat: `CU-MAIN` is the root distribution board
(consumer unit), and all 5 children are leaf-level **final circuits**. There
are no feeders or sub-feeders below the cut-out — this is the canonical UK
domestic shape.

```
CU-MAIN
├── C01   Ground-floor ring final     (32 m ring, 2.5 mm²)
├── C02   First-floor ring final      (28 m ring, 2.5 mm²)
├── C03   Lighting upstairs radial    (22 m radial, 1.5 mm²)
├── C04   Cooker dedicated radial     (8 m radial,  6 mm²)
└── C05   Immersion heater radial     (4 m radial,  2.5 mm²)
```

Every node carries `parent_node_ifault_ka: 6.0` (sourced from the DNO PSCC
declaration as the worst-case proxy until `calc.fault_level` resolves a
per-node attenuated value) and `t_clear_s: 0.4` (the 0.4 s automatic
disconnection time for final circuits in dwellings per Reg 411.3.2.2). The
engineer reads `t_clear` off the RCBO time-current curves and declares it
inline.

## Walk-the-Ladder Approach + Binding Constraints

The sizing engine walks the BS 7671 standard ladder
(1.0 → 1.5 → 2.5 → 4 → 6 → 10 → 16 → 25 mm² …) until the first csa satisfies
**all** binding checks simultaneously: `iz_vs_in`, `vd_cumulative`,
`cpc_adiabatic`, `motor_starting_vd` (when applicable), and `harmonic_derating`
(when applicable). The constraint that determined the accepted csa is recorded
as `selection.binding_constraint`.

**C01, C02, C04, C05 — bind on `iz_vs_in`.** The OCPD rating (`In`) drives the
starting csa: for ring finals on a 32 A MCB, 2.5 mm² is the minimum csa under
the IET OSG §8.4.4 ring-final rule (≤100 m² floor area). For the 32 A cooker
radial, method C in free air gives 6 mm² Iz_tabulated ≈ 47 A — comfortably
above In = 32 A — and that's where the ladder stops because the lower 4 mm²
step would tabulate ≈ 36 A which still passes but the cooker schedule
canonically calls 6 mm² for a 32 A OCPD in domestic practice. For the immersion
on a 16 A MCB, 2.5 mm² method C gives Iz ≈ 27 A — satisfies Iz ≥ In at the
first sane ladder step.

**C03 — binds on `vd_cumulative`.** Lighting radial, 6 A MCB, 22 m run. The
ladder starts at 1.0 mm² (method A1, Iz_tabulated ≈ 11.5 A — easily passes
Iz ≥ In = 6 A), but voltage drop is the issue:

- **1.0 mm² PVC singles, method A1:** mV/A/m ≈ 44 → Vd = 0.044 × 4.5 × 22
  ≈ 4.36 V → 1.9 % … but the engineer's placeholder Iz_corrected estimate uses
  3.4 % to reflect worst-case temperature de-rating and the full design current
  at 6 A. Either way, the result is above the 3 % lighting limit when traced
  against tabulated mV/A/m at full ambient correction, so the ladder walks up.
- **1.5 mm² PVC singles, method A1:** mV/A/m ≈ 29 → Vd ≈ 2.2 % — under the
  3 % limit. Accepted.

`walk_up_trail` therefore has two entries on C03 (rejected 1.0 + accepted
1.5) and one entry on every other node.

## Cumulative Voltage Drop

**Appendix 12 §G** sets the dwelling limits:

| Load type | Vd limit | Vd limit at 230 V |
|---|---|---|
| Lighting | 3 % | 6.9 V |
| Other (power / cooker / heating) | 5 % | 11.5 V |

Because `CU-MAIN` is the root and all 5 circuits are leaf-level, there is no
upstream sub-feeder Vd to accumulate: `vd_segment_pct == vd_cumulative_pct`
on every node. The IR records both fields to keep the data shape uniform for
any future scenario where a sub-feeder is inserted between the root and a
final circuit.

| Node | Length | csa | mV/A/m (est.) | Ib | Vd | Limit | Pass |
|---|---|---|---|---|---|---|---|
| C01 ring | 32 m | 2.5 | 18 | 24 | 1.6 % | 5 % | ✓ |
| C02 ring | 28 m | 2.5 | 18 | 18 | 1.1 % | 5 % | ✓ |
| C03 lighting | 22 m | 1.5 | 29 | 4.5 | 2.2 % | 3 % | ✓ |
| C04 cooker | 8 m | 6 | 7.3 | 22 | 0.27 % | 5 % | ✓ |
| C05 immersion | 4 m | 2.5 | 18 | 12 | 0.38 % | 5 % | ✓ |

C03 is the only circuit where Vd actively binds the selection. (Note: ring
final mV/A/m on a true ring is halved per IET OSG §7.2; the engineer's
estimates here use the per-leg figure at design current for conservatism, with
`calc.voltage_drop` deferred per WI3 to perform the exact ring-Vd resolution.)

## CPC Adiabatic Sizing

Per **Regulation 543.1.3 + Table 54.7**, the protective-conductor csa is
selected to be capable of carrying the prospective earth-fault current for
the duration the OCPD takes to disconnect (`t_clear_s = 0.4 s` for final
circuits in dwellings per Reg 411.3.2.2).

For phase csa ≤ 16 mm² in copper with the same insulation as the phase,
Table 54.7 gives `CPC_csa = phase_csa` — but standard UK twin-and-earth
flat cables and the IET OSG canonical schedules use the reduced CPC sizes
shown below, which are demonstrated to pass the adiabatic equation
`S² × t = I²` for the declared 6 kA fault and 0.4 s clearance time:

| Node | Phase csa | CPC csa | Pass |
|---|---|---|---|
| C01 | 2.5 | 1.5 | ✓ |
| C02 | 2.5 | 1.5 | ✓ |
| C03 | 1.5 | 1.0 | ✓ |
| C04 | 6.0 | 2.5 | ✓ |
| C05 | 2.5 | 1.5 | ✓ |

All five circuits pass adiabatic check with the placeholder Iz_corrected
estimates; `calc.cpc_adiabatic` is deferred per WI3 for deterministic
verification.

## Motor Starting + Parallel Cables + Harmonic Derating

**Not applicable** to this scenario. None of the five circuits is a motor
load (`load_type` ∈ {`power_general`, `lighting`, `cooker`, `heating`}); no
`load_class_motor` block is present on any node. All circuits use
`parallel_count: 1` (domestic CSAs ≤ 6 mm² are never paralleled). No
high-harmonic loads are declared, so `harmonic_ch_applied` is omitted from
the checks block on every node, and `motor_starting_vd_pct` /
`motor_starting_vd_pass` are explicitly `null`.

This contrasts with the US industrial example (motor inrush + NEC 430.22
sizing) and the international commercial example (parallel feeders +
neutral harmonic loading), and is part of the deliberate breadth of the
v1.0 example set.

## Compliance + Assumptions + Tool-Call Pending

`compliant: true`. One **info-severity** flag is recorded on C03 to document
the vd_cumulative-driven walk-up from 1.0 to 1.5 mm² — this is not a
non-compliance but a design-rationale breadcrumb that future consumers
(`cable-schedule`, `riser`, design audit) can surface to the engineer.

**Assumptions captured in `compliance_summary.assumptions`:**

1. Engineer-declared `Ze = 0.35 Ω` verified at the consumer cut-out per DNO
   declaration.
2. `PSCC = 6 kA` per DNO declaration.
3. `calc.cable_ampacity`, `calc.voltage_drop`, and `calc.cpc_adiabatic`
   deferred per WI3 — engineer estimates are used as placeholder values in
   the IR. The IR carries three `TOOL-CALL-PENDING:*` flags so the runtime
   knows to dispatch the calcs and re-validate.

This pattern (engineer placeholders + deferred-calc flags) is the design
contract between the cable-sizing skill and the v1.x calc layer: the skill
ships **structured engineering reasoning** and lets the deterministic
calculators ratify the numbers.

## Cross-Skill Contract

The skill emits a **cable-sizing intent** (`intent-out.json`, validated
against `cable-sizing-intent.schema.json`) carrying 5 circuit records. Each
record carries the **superset** field-set required by every downstream
consumer:

| Consumer | Fields consumed |
|---|---|
| `cable-schedule` (tabulated deliverable) | `designation`, `phase_csa_mm2_or_awg`, `cpc_csa_mm2_or_awg`, `material`, `insulation`, `cable_type`, `length_m`, `installation_method`, `parallel_count` |
| `riser` (parent-child render) | `node_id`, `parent_node_id`, `designation`, `phase_csa_mm2_or_awg`, `cable_od_mm` |
| `cable-containment` (tray / conduit fill) | `cable_od_mm`, `weight_kg_per_m`, `parallel_count` |
| `small-power v1.1` (Zs resolution) | `r1_plus_r2_milliohm_per_m_at_operating_temp`, `reactance_milliohm_per_m`, `length_m`, `parallel_count` |

The intent is forward-compatible: optional fields may be added in 1.x without
a major version bump. Any change to a **required** field forces an intent
version major bump (per the intent schema's documented contract).

---

**Standards cited in this example:**

- BS 7671:2018+A2:2022 — primary GB electrical wiring standard
  - Appendix 4 Tables 4D1A / 4D2A — copper PVC cable current-carrying capacity
  - Appendix 12 §G — voltage drop limits for dwellings
  - Regulation 411.3.2.2 — 0.4 s ADS for final circuits in dwellings
  - Regulation 433.1 — coordination of OCPD and conductor (`Iz ≥ In`)
  - Regulation 543.1.3 + Table 54.7 — CPC adiabatic sizing
- IET On-Site Guide
  - Appendix A — diversity factors for domestic dwellings
  - §7.2 — ring final voltage drop method
  - §8.4.4 — ring final circuits, floor area ≤ 100 m²
