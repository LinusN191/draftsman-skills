# IEEE 1584 — Arc Flash Incident Energy & Boundary (dual-track)

**Status:** `production-dual-track` — both 2002 Annex F and 2018 Tables 1+3 anchors present; numerical coefficients pending source-vetted transcription on both tracks.
**Standard body:** IEEE
**Edition:** 2018 (current authoritative anchor) + 2002 Annex F (retained for relabel correctness)
**Layer version:** 1.1.0
**Scope:** Calculate arc-flash incident energy (cal/cm²) + arc-flash boundary distance for AC equipment 208V – 15kV. The IEEE 1584-2018 §7 + Tables 1+3 polynomial-in-V model is the current authoritative anchor; the IEEE 1584-2002 Annex F simplified regression (7-term log-linear with K + x) is retained alongside for traceability of pre-2018 labels.

> **Sprint A.3 correction (2026-05-25):** The original `method-2018-*-coefficients.json` files were mis-labelled — their 7-coefficient log-linear shape matches IEEE 1584-2002 Annex F, NOT the IEEE 1584-2018 model (which uses 13-coef IE + 10-coef Iarc polynomial-in-V per Tables 1+3). The misnamed files were renamed to `method-2002-annex-f-*.json` and the actual 2018 model files were added alongside as `method-2018-tables-1-3-*.json`. See `meta.json` `dual_track_rationale` for full context.

## What this layer contains

| Category | Files |
|---|---|
| Core formulas (2002 Annex F anchor) | arc-current-formula.json, incident-energy-formula.json, boundary-distance-formula.json |
| Core formulas (2018 Tables 1+3 anchor) | arc-current-formula-2018.json, incident-energy-formula-2018.json |
| 2002 Annex F coefficient sets | method-2002-annex-f-{600V,2700V,14300V}-coefficients.json (7-term log-linear, k1..k7 + x) |
| 2018 Tables 1+3 coefficient sets | method-2018-tables-1-3-{600V,2700V,14300V}-coefficients.json (10-term Iarc + 13-term IE polynomial-in-V) |
| Voltage classes | 600V (208-600V), 2700V (601-2700V), 14300V (2701V-15kV), intermediate interpolation |
| Electrode configs | VCB, VCBB, HCB, VOA, HOA (2018 introduced HCB+VOA+HOA; 2002 covered VCB+VCBB only) |
| Adjustment factors | Non-standard gap, non-standard distance, enclosure-size correction |
| Legacy theoretical methods | Lee 1982 (cited by both 2002 and 2018), Doughty/Neal 2002 (empirical) — for reproducing pre-2018 labels |
| Reference data | Voltage classes, gap distances, working distances, equipment classification |

Total: 33 files in this layer.

## Related skills

- `electrical/arc-flash` (planned v1.0.0 — next sprint after this Phase A) — primary consumer
- Future: `electrical/protection-coordination` (consumes via arc-flash intent for clearing-time validation)

## How to use this layer

A skill manifest references specific files from this layer:

```json
{
  "standards": [
    "shared/standards/electrical/IEEE1584/method-2018-tables-1-3-600V-coefficients.json",
    "shared/standards/electrical/IEEE1584/arc-current-formula-2018.json",
    "shared/standards/electrical/IEEE1584/incident-energy-formula-2018.json",
    "shared/standards/electrical/IEEE1584/boundary-distance-formula.json"
  ]
}
```

To reproduce a pre-2018 label, point at the 2002 Annex F anchor instead (`method-2002-annex-f-*.json` + `incident-energy-formula.json` + `arc-current-formula.json`).

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
