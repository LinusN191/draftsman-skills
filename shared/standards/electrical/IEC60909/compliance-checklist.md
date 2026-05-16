# IEC 60909 Compliance Checklist

Verification checklist for any fault-level study deliverable produced by `electrical/fault-level` or referenced by downstream skills (db-layout, earthing, cable-sizing).

## Source data documented?

- [ ] Utility / DNO source: PSCC declared at primary, OR transformer kVA + Zpu + X/R documented
- [ ] HV-side voltage and network arrangement (radial / ring) stated
- [ ] Standby generator: X"d, X'd, Xd, kVA, voltage documented (if present)
- [ ] UPS: rated kVA, output current limit, bypass path described (if present)
- [ ] Motor load: total connected kW + ILR (locked-rotor current ratio) declared (if > 1% threshold)

## Cascade topology completeness?

- [ ] Every node in the cascade tree has a parent (single tree, no orphans)
- [ ] Cable impedance source declared per stage (BS 7671 App 4 / IEC 60364-5-52 / NEC Chapter 9 Table 9)
- [ ] All sub-DBs and final-circuit endpoints present (no gaps in the tree)

## Calculation method?

- [ ] IEC 60909-0:2016 method explicitly cited
- [ ] Voltage factor c selection documented: c=1.05 for Ik"max, c=0.95 for Ik"min
- [ ] Near-or-far-from-generator classification stated per source
- [ ] Peak factor κ derived from X/R at each node (not assumed constant)
- [ ] Multi-source superposition applied where utility + gen + UPS + motors are simultaneously active

## Output verification?

- [ ] Ik"max + Ik"min + ipk + X/R + Z_total emitted at every cascade node
- [ ] Breaker Icn ≥ Ik"max checked at every node — flagged if not
- [ ] Busbar Ipk_withstand ≥ ipk checked at every board — flagged if not
- [ ] Cable adiabatic check (I²t ≤ k²S²) verified at every cable using Ik"max
- [ ] Selectivity coordination notes flagged where upstream-downstream Icn relationship needs verification

## Tool execution status?

- [ ] If `calc.iec60909_cascade` runtime tool was invoked: results documented in IR
- [ ] If tool not available: `tool_call_pending: true` emitted per WI3 deferral pattern
- [ ] Engineer-input fault currents (fallback path) clearly distinguished from computed values in IR

## Cross-skill integration?

- [ ] Emitted `fault-level` intent satisfies the shape expected by `electrical/db-layout` v1.0.0
- [ ] db-layout selectivity tool_call_pending entries resolved when fault-level intent is present

## Rationale block?

- [ ] WI2 rationale block present at IR root
- [ ] 8 sections (Source Specification / Cascade Topology / HV-side Assumptions / Transformer + Source Impedances / Motor Contribution Assessment / Per-node Ifault Computation / Selectivity Implications / Compliance + Assumptions)
- [ ] chat_summary 40-500 chars
- [ ] All decisions cite IEC 60909-0 clauses verbatim
