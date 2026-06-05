# ISO 16739 IFC — Reference

Companion to `space-types.json`, `classification.json`, `placement.json` in this folder.

## What this layer covers

- `IfcSpaceTypeEnum` — 7-value coarse IFC space classifier (see `space-types.json`)
- `IfcClassification` + `IfcClassificationReference` + `IfcRelAssociatesClassification` — entities for attaching OmniClass Table 13 codes to spaces (see `classification.json`)
- `IfcLocalPlacement` + `IfcAxis2Placement3D` — parent-relative positioning (justifies the 4-value placement_convention enum from skill-manifest.schema.json) (see `placement.json`)

## What this layer does NOT cover

- Full IFC schema (1500+ pages). When the runtime needs additional entities for BIM export, extend this folder following the same pattern.
- Geometry primitives (IfcShapeRepresentation, IfcGeometricRepresentationContext, etc.) — only the placement subset is transcribed.
- Property sets (IfcPropertySet, IfcPropertySingleValue) — out of scope for room-type taxonomy.

## How this layer is consumed

1. `Room.classification` field in SkillInput (added by X.D.2) uses IfcClassificationReference structure (`source` + `edition` + `code` + `reference_uri`)
2. `placement_convention` enum from skill-manifest.schema.json is justified by IfcLocalPlacement parent-relative pattern (room/floor/site-local correspond to IfcSpace/IfcBuildingStorey/IfcSite respectively)
3. `ifc_space_type` field on room-types entries (X.B.* transcriptions) uses IfcSpaceTypeEnum 7-value enum directly

## Citation

ISO 16739:2018 — Industry Foundation Classes (IFC) for data sharing in the construction and facility management industries — Part 1: Data schema.

buildingSMART canonical specification: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/
