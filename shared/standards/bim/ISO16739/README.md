# ISO 16739 — Industry Foundation Classes (IFC) — Subset

Transcription of room-type-relevant IFC entities from ISO 16739:2018 (IFC 4 final).

**Source:** https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/ (buildingSMART canonical specification)
**Access date:** 2026-06-05
**Subset transcribed:** IfcSpace + IfcSpaceTypeEnum + IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification + IfcLocalPlacement + IfcAxis2Placement3D

This is a deliberate subset — the full ISO 16739 specification is 1500+ pages defining the complete IFC schema. Sprint X transcribes only the entities relevant to room-type taxonomy (`ifc_space_type` field in room-types entries) and placement justification (the `placement_convention` enum from skill-manifest.schema.json).

## Files

- `space-types.json` — IfcSpaceTypeEnum (7 values: PARKING / GFA / BERTHING / EXTERNAL / INTERNAL / USERDEFINED / NOTDEFINED)
- `classification.json` — IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification entity definitions
- `placement.json` — IfcLocalPlacement + IfcAxis2Placement3D entity definitions (justifies placement_convention 4-value enum)
- `reference.md` — companion human-readable reference

## When to extend this layer

When the runtime needs full IfcLocalPlacement round-tripping or richer IFC entity coverage for BIM export, author the additional entities here. The current subset suffices for:

1. Room.classification.source: "IFC IfcClassificationReference" pattern in SkillInput
2. placement_convention BIM justification in skill-manifest.schema.json
3. ifc_space_type field on room-types entries
