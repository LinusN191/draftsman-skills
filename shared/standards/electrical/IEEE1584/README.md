# IEEE 1584:2018 — Arc Flash Incident Energy & Boundary

**Status:** `production` — fully transcribed for arc-flash skill consumption
**Standard body:** IEEE
**Edition:** 2018 (current)
**Layer version:** 1.0.0
**Scope:** Calculate arc-flash incident energy (cal/cm²) + arc-flash boundary distance for AC equipment 208V – 15kV using the IEEE 1584:2018 empirical model.

## What this layer contains

| Category | Files |
|---|---|
| Core formulas | arc-current, arc-current-variation, incident-energy, boundary-distance |
| Voltage classes | 600V (208-600V), 2700V (601-2700V), 14300V (2701V-15kV), intermediate interpolation |
| Electrode configs | VCB, VCBB, HCB, VOA, HOA (5 configurations × 7-coefficient sets) |
| Adjustment factors | Non-standard gap, non-standard distance, enclosure-size correction |
| Legacy methods | Lee 1982 (theoretical), Doughty/Neal 2002 (empirical) — for reproducing pre-2018 labels |
| Reference data | Voltage classes, gap distances, working distances, equipment classification |

Total: 28 files in this layer.

## Related skills

- `electrical/arc-flash` (planned v1.0.0 — next sprint after this Phase A) — primary consumer
- Future: `electrical/protection-coordination` (consumes via arc-flash intent for clearing-time validation)

## How to use this layer

A skill manifest references specific files from this layer:

```json
{
  "standards": [
    "shared/standards/electrical/IEEE1584/method-2018-600V-coefficients.json",
    "shared/standards/electrical/IEEE1584/arc-current-formula.json",
    "shared/standards/electrical/IEEE1584/incident-energy-formula.json",
    "shared/standards/electrical/IEEE1584/boundary-distance-formula.json"
  ]
}
```

The skill's generator prompt walks the appropriate formula files based on voltage class + electrode config + jurisdiction.

## Edition + versioning policy

When IEEE 1584:2028 (estimated) is published, we update this layer in-place:
- Bump `edition` in `meta.json` to `"2028"`
- Bump `layer_version` to `"2.0.0"`
- Add 2018→2028 deltas section to `amendments-summary.md`
- The consuming `arc-flash` skill bumps to its v2.0.0

Legacy 2002 method files remain alongside for backward compatibility.

## License + reuse

Standards content is © IEEE. This repo stores clause references + numeric coefficients (factual data, not copyrighted expression) + brief paraphrase only. Full standard text is never reproduced.

See `compliance-checklist.md` for what a study satisfying IEEE 1584 must demonstrate.
