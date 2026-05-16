# IEC 60909-0:2016 — Amendments and National Derivations

## Edition history

- **IEC 60909-0:1988** — first edition, three-phase symmetrical short-circuit calculation
- **IEC 60909-0:2001** — Edition 2.0, expanded to cover unbalanced faults
- **IEC 60909-0:2016** — Edition 3.0 (current), refined induction motor contribution, voltage factor c clarifications

## Key 2016 amendments

- **§3.5 near-from-generator** — clarified subtransient time interval to first peak (≤10 ms)
- **§4.2 voltage factor c** — Table 1 updated to align with IEC 60038 (Standard voltages) Edition 7
- **§4.5 induction motor contribution** — threshold tightened: motors with sum ≥ 1% of supply Sk" must be considered
- **Annex A** — equivalent voltage source method now mandatory for short-circuits supplied by interconnected meshed networks

## National derivations / equivalents

### UK (BS 7671:2018+A3)

- Reg 434.5: Adiabatic protection check uses Ik" per IEC 60909
- App 3 device curves: time-current characteristic verified at Ik" computed per IEC 60909
- IET commentary: UK practice in dwellings typically uses DNO-declared Ze + an X/R ratio of 1.0 (resistive supply assumption) — IEC 60909 method preserves this as a limiting case

### EU (IEC 60364)

- IEC 60364-4-43 cites IEC 60909 directly for cable adiabatic protection
- IEC 60364-5-53 cites IEC 60909 for selectivity coordination
- National CENELEC HDs add minor formatting differences but the method is preserved

### US (NFPA 70 / NEC)

- NEC 110.9: equipment "interrupting rating sufficient for the available fault current" — IEC 60909 Ik" is the calculation method accepted by AHJs
- NEC 110.24: marking of available fault current at service equipment — typically computed per IEEE 141 (Red Book) which converges with IEC 60909 for utility-source cases
- NEC 240.86: series ratings — IEC 60909 cascade method aligns with the series-rating verification path
- NEC Chapter 9 Table 9 provides R + X for ac-rated conductors (used in this skill's Step 9 cable impedance lookup)

## Cross-skill alignment

- `electrical/db-layout` v1.0.0 — `selectivity_results[*].source` enum includes `"iec_60909_calc"` to record when fault-level (via this layer) was the basis
- `electrical/earthing` v1.0.0 — accepts engineer-declared Ze (DNO PME convention) OR a fault-level intent reference; future v1.1 will cross-validate against this layer
