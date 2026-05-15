# Changelog — sld

## v1.2.0 (current)
- Add `inputs.json` carrying full discovery taxonomy (18 items including supply source, earthing, PSCC, transformer/generator/UPS, distribution-board struct_list, Form/IAC, SPD strategy)
- Add `inputs_path: "inputs.json"` to manifest pointing at the new taxonomy
- Bare-string `inputs: [...]` array retained for back-compat; will be removed in v2.0.0
- Conforms to new `shared/schemas/core/inputs.schema.json` metaschema (upstream Work Item 1)

## v1.1.0
- Zs disconnection time check (Tables 41.2/41.3)
- Protection coordination and selectivity
- Life safety circuits (FP200/FP400, essential bus)
- Cable type selection (LSZH, fire-rated)
- Neutral oversizing for harmonic loads
- Motor load starting current
- Switchgear Form of separation (BS EN 61439-1)
- ACB electronic trip unit settings
- SPD risk assessment (Reg 443.4)
- Part L sub-metering obligations
- G99/G98 regulatory submissions

## v1.0.0
- Initial production release
