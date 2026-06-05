# BSEN12464

Standards reference files for BS EN 12464-1:2021 — Light and lighting: Lighting of work places (indoor).

## Files

| File | Contents | Source clauses |
|---|---|---|
| `lux-levels.json` | Maintained illuminance (Em) targets by task/area type | BS EN 12464-1:2021 Table 5 + Table 6 |
| `lux-levels-reference.md` | Human-readable companion to lux-levels.json | As above |
| `area-definitions.json` | Machine-readable area-type/purpose definitions | §4.2.2.1/2/3 + Table 6 |
| `area-definitions-reference.md` | Human-readable companion to area-definitions.json | As above |

## v1.7 D5 additions (2026-06-05)

- **`area-definitions.json`** added — machine-readable transcription of §4.2.2.1/2/3 and Table 6 covering zone-purpose hierarchy (task / surrounding / background), ratio thresholds (surrounding ≥ ⅓ task; background ≥ ⅓ surrounding), and area-type classifications. Consumed by `electrical/lighting-layout` v1.7.0 INV-13/14/15.
- **`area-definitions-reference.md`** added — human-readable companion explaining each field and its normative source.
- **`lux-levels.json`** augmented with `em_target_lux` emergency columns cross-referenced from BS EN 1838:2013 §5.3 and BS EN 12464-1:2021 Table 5 footnotes.
