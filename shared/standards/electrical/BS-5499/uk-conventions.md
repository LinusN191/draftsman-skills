# BS 5499 — UK Conventions for Arc-Flash Labels

## Regulatory framing

| Aspect | UK Status |
|---|---|
| Arc-flash analysis | Voluntary best practice per HSG48 + IET Code of Practice for In-Service Inspection |
| Arc-flash labels | Voluntary — not statutory under UK Health & Safety at Work Act |
| ISO 7010 symbols | Adopted by BS 5499; the canonical UK warning symbol for electricity is W012 (yellow triangle + black lightning) |
| English signal words | UK convention adds "DANGER" / "WARNING" text supplementary to symbols (Z535.4-style influence) |

UK arc-flash labels are recommended where energized maintenance work is anticipated. HSE guidance (HSG48) encourages employers to undertake risk assessment + provide hazard awareness.

## Signal-word vocabulary

| English signal word | UK convention | Maps to PPE |
|---|---|---|
| DANGER | High-severity hazard requiring specialised PPE | NFPA 70E Cat 3-4 (8 ≤ IE ≤ 40 cal/cm²) |
| WARNING | Hazard requiring AR clothing + standard PPE | NFPA 70E Cat 1-2 (1.2 ≤ IE < 8 cal/cm²) |
| RESTRICTED | Above 40 cal/cm² — energized work prohibited | DraftsMan extension; uses purple/black banner |

## PPE language

UK labels reference BS EN ISO 11611 (arc-rated welding clothing) + BS EN IEC 61482-2 (arc-rated PPE) for clothing certification. NFPA 70E Table 130.7(C)(16) descriptions are translated to UK equivalents:

| NFPA 70E text | UK equivalent |
|---|---|
| "Arc-rated shirt + trousers (ATPV ≥4 cal/cm²)" | "BS EN IEC 61482-2 Class 1 arc-rated overall (ATPV ≥4 cal/cm²)" |
| "AR hood" | "BS EN IEC 61482-2 arc-rated full-face hood" |
| "leather gloves" | "EN 388 mechanical-rated leather gloves" |

The skill can render either NFPA 70E or BS EN style PPE descriptions — engineer-declared per project.

## Bilingual support

BS 5499 is symbol-first, so bilingual support is feasible. v1.0 ships English only; Welsh-English bilingual labels deferred to v1.1.

## BS 7671 cross-references

Where applicable, UK labels reference BS 7671:2018 (the Wiring Regulations) for any installation-method or earthing-context language. The labelling skill includes optional `bs_7671_reference` field on labels for installations where the engineer wants to call out a specific regulation.
