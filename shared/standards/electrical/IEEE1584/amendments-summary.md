# IEEE 1584 — Amendments Summary

## 2002 → 2018 (current edition)

The 2018 revision replaced a single empirical model with three models keyed by voltage class, plus introduced three new electrode configurations.

### What changed

| Aspect | IEEE 1584:2002 | IEEE 1584:2018 |
|---|---|---|
| Empirical model | Single formula for all voltages | Three models (600V, 2700V, 14300V class) |
| Electrode configs | 2 (VCB, VCBB) | 5 (VCB, VCBB, HCB, VOA, HOA) |
| Voltage range | 0.208 – 15 kV | 0.208 – 15 kV (unchanged) |
| Arc-current variation | Simple ratio | High/low bracket per §10.2 |
| Box-size correction | Implicit (one box assumed) | Explicit adjustment factor (§10.5) |
| Iarc prediction | Single formula | Voltage-class-specific formulas |

### Compatibility notes for the consuming skill

- Existing arc-flash labels (pre-2018) were computed with the 2002 method. To verify or update them, use `method-2002-*-formula.json` files; do NOT mix 2002 and 2018 results in one study.
- New studies should use the 2018 method exclusively.
- The Lee 1982 theoretical formula remains useful as a sanity-check upper bound for incident energy calculations.

## Future: when IEEE 1584:2028 ships

Per repo policy, in-place update of this layer:
- `meta.json` `edition` → `"2028"`
- `meta.json` `layer_version` → `"2.0.0"`
- This file gets a new `## 2018 → 2028` section
- Method files for the 2018 edition remain as `method-2018-*.json` (legacy)
- New `method-2028-*.json` files added for the new edition
- The consuming `arc-flash` skill bumps its version to follow
