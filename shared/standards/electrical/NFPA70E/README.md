# NFPA 70E:2024 — Standard for Electrical Safety in the Workplace

**Status:** `production` — Article 130 + relevant annexes fully transcribed
**Standard body:** NFPA
**Edition:** 2024 (current)
**Layer version:** 1.0.0
**Scope:** Workplace electrical safety: arc-flash risk assessment, shock-approach boundaries, PPE selection, plus DC arc-flash calculation methods (Annex D).

## What this layer contains

| Category | Files |
|---|---|
| Article 130 sections | 130.2 (safe work), 130.3 (precautions), 130.4 (shock boundaries), 130.5 (arc-flash risk assessment), 130.7 (PPE) |
| Shock-approach tables | 130.4(C)(a) AC + 130.4(C)(b) DC |
| Risk-assessment tables | 130.5(C) likelihood + 130.5(G) equipment + 130.5(H) label requirements |
| PPE-selection tables | 130.7(C)(15)(a) AC tasks + (b) DC tasks + (c) PPE categories + 130.7(C)(16) required clothing |
| Annex D DC arc-flash methods | Doan 2007 + Stokes & Oppenlander 1991 |
| Reference annexes | H (PPE guidance), K (general hazards), L (typical safeguards) |

Total: 25 files in this layer.

## Related skills

- `electrical/arc-flash` (planned v1.0.0 — next sprint) — primary consumer
- Future: `electrical/protection-coordination` (uses NFPA 70E §130.5 risk-assessment framework)

## How to use this layer

A skill manifest references specific files:

```json
{
  "standards": [
    "shared/standards/electrical/NFPA70E/section-130-5-arc-flash-risk-assessment.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-c-ppe-categories.json",
    "shared/standards/electrical/NFPA70E/table-130-5-H-label-requirements.json"
  ]
}
```

The skill picks tables based on AC vs DC, equipment type, and whether incident energy was computed (full study) or only equipment table-method was used (fallback).

## Edition + versioning policy

NFPA 70E revises on a 3-year cycle. Next revision: 2027 (estimated).

When NFPA 70E:2027 is published:
- Update content in-place
- Bump `edition` in `meta.json` to `"2027"`
- Bump `layer_version` to `"2.0.0"`
- Add 2024→2027 deltas to `amendments-summary.md` (not present at v1.0.0 — added at first edition bump)
- Consuming `arc-flash` skill bumps to its v2.0.0

## License + reuse

Standards content is © NFPA. This repo stores clause references + factual thresholds + brief paraphrase only.

See `compliance-checklist.md` for what a workflow satisfying NFPA 70E demonstrates.
