# Reasoning — UK 3-storey Office MSB-MAIN

## Site context

3-storey UK commercial office, 1200m² GIA total (400m² per floor). DNO TN-C-S 400V TPN supply with declared Ze=0.35Ω + PFC=9.8kA. Ground-floor plant room location for the main switchboard.

## Board sizing — 400A intake

Peak design load per floor: ~30 kVA (12kW lighting + 10kW sockets + 5kW IT + 3kW HVAC FCU). Total 3-floor load: 86 kVA at PF 0.85 = 73 kW.

Design current per phase: 86,000 / (√3 × 400 × 0.85) = ~146A.

Applying diversity factor 0.8 (commercial spec-office norm per CIBSE Guide F + BCO Guidance at the building-aggregate level — distinct from per-circuit / per-load-type diversity that BS 7671:2018+A2:2022 § 311.1 + IET OSG Appendix A prescribes on individual instantaneous loads): ~117A. With 25% growth margin: ~146A peak.

400A TPN intake gives ~63% headroom — generous for spec office where tenant fit-out can dramatically change loads. Standard practice for commercial multi-tenant buildings.

## MCCB selection for feeders (Type D, 100A each)

Each sub-DB is sized at 100A. The feeder breakers are 100A MCCBs Type D:
- Type D curve (Ia = 20×In) handles potential inrush from downstream LED lighting transformers + UPS-fed IT loads
- 100A rating matches downstream sub-DB intake rating
- 36kA Icu breaking capacity matches DNO declared PFC + intake fault path

## Selectivity verification

Upstream 400A MCCB selectively trips against 100A feeder MCCBs:
- Current selectivity ratio: 4:1 (BS EN 60947-2 typical achieves selectivity up to 5:1)
- Time selectivity: short-time delay (STD) at 400A MCCB further enhances selectivity
- Breaking capacity: 36kA on both upstream + downstream (matched)

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/uk-commercial-office-3storey/` (SLD generates the system-wide single-line diagram)
- Sub-DBs SDB-GF, SDB-L1, SDB-L2 are authored as separate db-layout examples (Tasks 2-4)
- (Future) `electrical/cable-sizing/` for feeder cable sizing verification
- (Future) `electrical/fault-level/` for cascade fault current verification

## See also

- electrical/db-layout/examples/uk-commercial-sdb-gf/ (downstream — ground floor sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l1/ (downstream — level 1 sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l2/ (downstream — level 2 sub-DB)
