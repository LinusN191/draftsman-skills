# ISO 7200:2004 — Title Block Data Fields

International standard for technical drawing title block content. Covers 4 mandatory fields + 12 optional recommended fields, plus identification zone layout.

## Files in this folder

| File | Purpose |
|---|---|
| `meta.json` | Publication metadata, edition, scope |
| `title-block-fields.json` | §4 — mandatory (4) + optional (12) field definitions; engine-lookupable mandatory_fields list |
| `layout-conventions.json` | §5 — identification zone position, dimensions per sheet size |
| `field-definitions.md` | Narrative purpose of each field with examples |

## Engine-lookup keys

- `engine_lookup.mandatory_fields` → `["identification_number", "title_subtitle", "issuing_organization", "approval_date"]`
- `engine_lookup.by_sheet_size_id_zone_height_mm["A1"]` → 297

## Cross-references

- **ISO 5457** — sheet sizes + title block region location
- **ISO 5455** — scale field format
- **BS 1192 / ISO 19650** — revision + identification_number format

## Applies to jurisdictions

- **GB / KE / INT / EU** — primary standard
- **US** — often used alongside ANSI conventions in international projects
