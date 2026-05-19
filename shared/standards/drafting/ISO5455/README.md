# ISO 5455:1979 — Technical Drawing Scales

International standard for technical drawing scales. Covers enlargement (>1:1), full size (1:1), reduction (<1:1) scales + use guidance per discipline.

## Files in this folder

| File | Purpose |
|---|---|
| `meta.json` | Publication metadata, edition, scope |
| `scales.json` | Full enum: 5 enlargement + 1:1 + 12 reduction + NTS special case |
| `use-guidance-per-discipline.json` | Industry practice — recommended primary + alternative scales per drawing type |

## Engine-lookup keys

- `engine_lookup.by_scale["1:100"]` → 0.01
- `engine_lookup.by_scale["NTS"]` → null (special case)
- `engine_lookup.by_drawing_type_primary["sld_single_line"]` → "NTS"
- `engine_lookup.by_drawing_type_primary["lighting_layout"]` → "1:100"

## Applies to jurisdictions

- **GB / KE / INT / EU** — primary standard
- **US** — ANSI scales (1/4"=1', 1/2"=1', 1"=1', etc.) typically used; ISO scales applied for international projects
