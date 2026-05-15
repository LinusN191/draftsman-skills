# Changelog — lighting-layout

## v1.3.0 (current)
- Add `inputs.json` carrying full discovery taxonomy (15 items with answer_type, validators, defaults, depends_on)
- Add `inputs_path: "inputs.json"` to manifest pointing at the new taxonomy
- Bare-string `inputs: [...]` array retained for back-compat; will be removed in v2.0.0
- Conforms to new `shared/schemas/core/inputs.schema.json` metaschema (upstream Work Item 1)

## v1.2.0
- MF environment cross-check table (7 environment types)
- BS 8300 luminance ratios for entrance transition zones
- Door swing direction input and latch-side switch placement
- db_designation field in circuits and metadata

## v1.1.0
- Part L efficacy check and controls matrix
- Zone-based circuit naming (Z1 perimeter, Z2 interior)
- LLMF detection and design lumen conversion
- IP rating check by environment type
- CCT appropriateness table
- Dimming protocol comparison table
- UGR disclaimer on every layout
- Perimeter zone identification (2000mm from glazed wall)
- Vertical illuminance requirements (whiteboard, faces)

## v1.0.0
- Initial production release
- Lumen method calculation
- Grid layout with 50mm snap
- Circuit load check (10A MCB, 80% rule)
- BS EN 12464-1:2021 lux targets table
