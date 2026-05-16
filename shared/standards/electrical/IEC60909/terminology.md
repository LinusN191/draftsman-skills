# IEC 60909 Terminology — Cross-Reference

Glossary aligning IEC 60909 terms with BS 7671 / NEC equivalents used in `electrical/fault-level` and downstream skills.

## Core terms

| IEC 60909 Term | Symbol | Unit | BS 7671 Equivalent | NEC Equivalent | Description |
|---|---|---|---|---|---|
| Initial symmetrical short-circuit current | Ik" | A (kA) | PSCC (prospective short-circuit current) | Available fault current | RMS value of the AC symmetrical component at instant of fault |
| Peak short-circuit current | ipk | A (kA) | i_p, peak fault current | Peak short-circuit current | First-cycle maximum instantaneous value |
| Voltage factor | c | dimensionless | — | — | 1.05 for Ik"max; 0.95 for Ik"min; per Table 1 |
| Peak factor | κ (kappa) | dimensionless | — | — | ipk / (√2 × Ik"); depends on R/X |
| Near-from-generator | NG | — | — | — | Synchronous machine within calculation path with declining contribution |
| Far-from-generator | FG | — | — | — | Source contribution stays constant over fault duration |
| Per-unit impedance | Zpu | % or pu | — | — | Transformer impedance referenced to its rated capacity |
| Symmetrical breaking current | Ib | A (kA) | Icn (breaking capacity) | Interrupting Rating | RMS at instant of contact separation |
| Steady-state short-circuit current | Ik | A (kA) | — | — | RMS at end of transient |

## Source contribution terms

| Term | Symbol | Description |
|---|---|---|
| Synchronous generator subtransient reactance | X"d | First-cycle reactance, smallest |
| Synchronous generator transient reactance | X'd | Reactance after subtransient decay, ~100ms |
| Synchronous generator synchronous reactance | Xd | Steady-state reactance, ~seconds |
| Induction motor locked-rotor reactance | X"M | First-cycle motor back-feed reactance |
| Transformer short-circuit impedance | Zk | Equivalent positive-sequence impedance referred to rated voltage |
| Network feeder impedance | ZQ | Equivalent network impedance from feeder substation perspective |

## Calculation method terms

| Term | Description |
|---|---|
| Equivalent voltage source method | The IEC 60909 method: replace all active sources with a single equivalent EMF c × Un at fault point |
| Voltage factor c_max | 1.05 (LV systems with Un ≥ 100 V); for maximum Ik" — drives breaker rating verification |
| Voltage factor c_min | 0.95 (LV systems with Un ≥ 100 V); for minimum Ik" — drives ADS protection setting verification |
| Source path | Series chain of impedances from supply to fault location |

## Jurisdiction-specific terms

**UK (BS 7671):** "PSCC" (prospective short-circuit current) maps to Ik". UK practice typically uses LV TN-C-S Ze (declared by DNO) as a shortcut to derive PSCC at the LV service.

**EU/INT (IEC 60364):** IEC 60909 terminology used directly. Ik" + ipk are the standard reporting values for switchgear and protection sizing.

**US (NEC):** "Available fault current" maps to Ik". NEC 110.9 requires equipment to be rated for the available fault current. NEC 110.24 requires marking of available fault current on service equipment.
