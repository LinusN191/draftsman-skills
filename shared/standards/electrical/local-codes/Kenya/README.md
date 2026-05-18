# Kenya — Country Electrical Context

**Country code:** KE
**Currency:** KES (Kenyan Shilling)
**Capital:** Nairobi
**Population:** ~55 million (2024)
**Climate zones:** 4 (highland, coastal, inland tropical, arid northern — see Annex G)

## Primary standards (canonical content lives elsewhere)

| Topic | Layer in this repo |
|---|---|
| Electrical wiring code (primary) | `shared/standards/electrical/KS1700/` |
| Parent international standard | `shared/standards/electrical/IEC60364/` |
| Parent British standard (adopted via KS Annex E) | `shared/standards/electrical/BS7671/` |

## Country-specific content (this folder)

| File | Purpose |
|---|---|
| `country-meta.json` | DNO/regulator/jurisdiction codes |
| `adoption-pathway.md` | Legal mandate (Cap 496) + KEBS publishing process + EPRA enforcement |
| `README.md` | This file — overview + pointer to canonical layers |

This folder holds country-context (DNO, regulator, market, legal pathway). Canonical standards content lives in the standalone standards layers in `shared/standards/electrical/<standard>/`.

## DNOs and regulators

| Entity | Role |
|---|---|
| Kenya Power and Lighting Company (KPLC) | Primary LV/MV distribution network operator |
| Kenya Electricity Transmission Company (KETRACO) | Transmission system operator (HV) |
| Energy and Petroleum Regulatory Authority (EPRA) | Regulator; enforces electrical installation inspection regime |
| Kenya Bureau of Standards (KEBS) | Standards publisher; certification mark issuer |
| Kenya National Highways Authority (KENHA) | Outdoor / street lighting installations |

## Supply characteristics

- Nominal: 240V single-phase / 415V three-phase, 50 Hz
- Voltage tolerance: ±6% per EPRA Regulation 2017
- Default system: TN-C-S (PME) for modern urban; TN-S for legacy industrial; TT for off-grid rural
- Typical declared PFC: 6 kA (single-phase rural), 9.8 kA (single-phase metro), 16 kA (three-phase industrial), 25 kA (substation-adjacent)

## Related skills

- `electrical/earthing` v1.2+ — full KS 1700 jurisdiction support
- Future: cable-sizing, db-layout, lighting-layout will add KS 1700 jurisdiction in their respective sprints

## See also

- `KS1700/README.md` — canonical KS 1700 standards layer
- `KS1700/annex-E-bs7671-adoption-table.json` — clause-by-clause KS↔BS mapping
- `KS1700/ks-unique-deviations.json` — Kenya-specific deviations
