# Schematic Skill — Changelog

## v1.0.0 — 2026-05-22

Initial release. Control + protection schematics with hybrid consumer pattern.

### Added
- Per-schematic IR (one schematic = one IR document)
- 7-value `schematic_type` enum with oneOf branching (control_motor_starter / control_changeover / control_sequence / protection_overcurrent / protection_differential / protection_motor / protection_busbar)
- 40 BS EN 60617 symbols (motor starter + protection + auxiliary + control logic)
- 8 jurisdictional examples: 4 control (KE/UK/INT/US) + 4 protection (KE/UK/INT/US)
- Hybrid consumer of `db-layout-rollup` + `fault-level` + `earthing` intents with leaf-mode fallback
- Terminal `schematic` intent emission for future tender-report / om-manual consumption

### Standards
- BS 7671:2018+A2:2022, BS EN 60617, BS EN 61082, BS EN 61009-1:2012+A12:2014 (UK)
- KS 1700:2018 routing to BS 7671 via §313 + IEC 60617 + IEC 60255 (KE)
- IEC 60364-X-XX + IEC 60617 + IEC 60255 + IEC 61850 (INT)
- NEC 2023 / NFPA 70 + IEEE Std 315 + IEEE C37.x (US)

### Lessons applied from Sprint 3-W2c
- Single-frame voltage references (no dual-frame % collision)
- No fabricated standard publication years
- Canonical enums (`main_switch_fused`, `§ 311.1`)
- Africa-first KE jurisdiction first-class
