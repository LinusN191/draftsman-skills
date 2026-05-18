# KS 1700:2018 — Terminology

KS 1700:2018 adopts BS 7671 terminology substantially via Annex E. This file documents KS-specific terms and Kenya-supply-context vocabulary that supplement the BS terms.

## Kenya supply context

| Term | Definition |
|---|---|
| KPLC | Kenya Power and Lighting Company — primary LV/MV distribution network operator (DNO) for the national grid |
| KETRACO | Kenya Electricity Transmission Company — transmission system operator for HV networks |
| EPRA | Energy and Petroleum Regulatory Authority — regulator for the electricity sector; mandates electrical installation inspection regime |
| KEBS | Kenya Bureau of Standards — standards publisher; publishes KS 1700, KS ISO 7010, and equipment certification marks |
| KENHA | Kenya National Highways Authority — relevant for outdoor / street lighting installations |
| Wayleave | KPLC infrastructure-easement reference; cited per supply connection (e.g., "KPLC-NRB-IND-2143") |
| EPRA Inspection | Mandatory periodic inspection of electrical installations: ≤5 years commercial/industrial, ≤10 years domestic |
| KEBS Mark | Certification mark required on consumer-side electrical equipment for legal sale and installation |

## Supply system terminology (adopted from BS 7671 + KS adaptations)

| Term | KS 1700 reference | Note |
|---|---|---|
| TN-S | §411.4 | Adopts BS terminology. Legacy KPLC industrial supplies; declared Ze typically 0.65-1.0 Ω |
| TN-C-S (PME) | §411.4 | Adopts BS terminology. Modern KPLC default for domestic + commercial; declared Ze typically 0.20-0.35 Ω |
| TT | §411.5 | Adopts BS terminology. Off-grid / rural / solar-PV installations |
| Ze | §411.3.2 | External earth fault loop impedance, declared by KPLC at intake |
| Ra | §411.5.2 | Electrode resistance (TT systems); design target per §411.5.3 (Ra × IΔn ≤ 50V) |

## Climate-zone vocabulary (KS Annex G — KS-unique)

| Zone | Description | Design ambient |
|---|---|---|
| Highland | Above 1500m altitude — Nairobi, Nakuru, Eldoret, Nyeri | 25°C indoor / 30°C outdoor |
| Coastal | Sea-level, high humidity — Mombasa, Kilifi, Lamu | 35°C indoor / 40°C outdoor |
| Inland tropical | 500-1500m altitude — Kisumu, Kakamega, Meru | 30°C indoor / 35°C outdoor |
| Arid northern | Below 800m altitude, dry climate — Marsabit, Garissa, Wajir | 35°C indoor / 45°C outdoor |

Default in absence of zone declaration: 30°C indoor / 40°C outdoor (conservative for engineering design across Kenya).

## See also

- BS7671/terminology.md — for adopted-verbatim BS terms
- IEC60364/terminology.md — for IEC-source terms KS 1700 routes through
