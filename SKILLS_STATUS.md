# DraftsMan Skills — Status

Status codes: `production` | `beta` | `draft` | `stub`

- **production** — complete: manifest, prompts, rules, constraints, evals (≥5), examples (≥3), schemas, docs
- **beta** — prompts written and tested; evals/examples may be partial
- **draft** — prompts drafted but not yet eval'd
- **stub** — manifest + README only; prompts not written

---

## Electrical

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| lighting-layout | `electrical/lighting-layout` | **production** | BS EN 12464-1:2021, Part L 2021 | 8/5 ✓ | Reference implementation. 8 evals (incl. rationale), 3 examples with rationale, full IR schema. |
| sld | `electrical/sld` | **beta** | BS 7671:2018, BS EN 60617 | 8/3 ✓ | v1.1.0 prompts complete. 8 evals, 4 examples. Separate eval YAML files pending. |
| db-layout | `electrical/db-layout` | **beta** | BS 7671:2018, IEC 60364, IEC 61439, NFPA 70 (NEC 2023), IEC 60617 | 8/3 ✓ | v1.1.0 — adds KE Nairobi industrial 100A TPN example (paired with earthing v1.3) + intent-out.json backfill for 3 existing examples. 4 worked examples total. |
| cable-containment | `electrical/cable-containment` | stub | BS 7671:2018, BS 1192 | — | — |
| riser | `electrical/riser` | stub | BS 7671:2018 | — | — |
| schematic | `electrical/schematic` | stub | BS EN 60617 | — | — |
| small-power | `electrical/small-power` | stub | BS 7671:2018 | — | — |
| earthing | `electrical/earthing` | **beta** | BS 7671:2018, IEC 60364, NFPA 70 (NEC 2023), KS 1700:2018, IEC 60617 | 9/3 ✓ | v1.3.0 — db-layout intent consumption across all 4 worked examples (WI4 pattern). eval-09 verifies cross-file circuit_id consistency. ARCHITECTURE.md §"Worked example pattern" subsection added. |
| emergency-lighting | `electrical/emergency-lighting` | stub | BS 5266-1, BS EN 1838 | — | — |
| cable-schedule | `electrical/cable-schedule` | stub | BS 7671:2018 | — | — |
| panel-schedule | `electrical/panel-schedule` | stub | BS 7671:2018, BS EN 61439 | — | — |
| load-schedule | `electrical/load-schedule` | stub | BS 7671:2018 | — | — |
| metering | `electrical/metering` | stub | Part L 2021, BS EN 62053 | — | — |
| transformer | `electrical/transformer` | stub | BS EN 60076 | — | — |
| generator | `electrical/generator` | stub | BS 7671:2018, BS ISO 8528 | — | — |
| ups | `electrical/ups` | stub | BS EN 62040 | — | — |
| solar-pv | `electrical/solar-pv` | stub | BS 7671:2018, G99/G98, MCS | — | — |
| lightning-protection | `electrical/lightning-protection` | stub | BS EN 62305 | — | — |
| hvac-power | `electrical/hvac-power` | stub | BS 7671:2018 | — | — |
| fire-alarm | `electrical/fire-alarm` | stub | BS 5839-1, BS EN 54 | — | — |
| access-control | `electrical/access-control` | stub | PD 6662, BS EN 50131 | — | — |
| cctv | `electrical/cctv` | stub | BS EN 62676 | — | — |
| nurse-call | `electrical/nurse-call` | stub | BS EN ISO 11073, HTM 08-03 | — | — |
| public-address | `electrical/public-address` | stub | BS EN 60849, BS 5839-8 | — | — |
| security | `electrical/security` | stub | BS EN 50131 | — | — |
| data-telecom | `electrical/data-telecom` | stub | TIA-568, ISO/IEC 11801 | — | — |
| arc-flash | `electrical/arc-flash` | **beta** | IEEE 1584:2018, NFPA 70E:2024, Lee 1982, Doan 2007, Stokes & Oppenlander 1991 | 9/3 ✓ | v1.0.0 Phase B. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (6 WI5 + 3 skill-specific), 3 worked examples (UK LV / INT MV / US PV+DCFC). 5-method fallback chain (2018→2002→Lee→table→pending; dc_doan for DC). Math deferred to calc.arc_flash_incident_energy runtime tool per WI3. Consumes fault-level + db-layout-rollup intents; emits arc-flash intent for future labelling skill. |
| arc-flash-labelling | `electrical/arc-flash-labelling` | **beta** | ANSI Z535.4:2023, ISO 7010:2019, BS 5499, NFPA 70E:2024 §130.5(H) | 8/3 ✓ | v1.0.0 (unified Phase A+B). 12-step generator, IR + intent schemas, 9 deterministic checks, 8 evals (5 WI5 + 3 skill-specific), 3 worked examples (US ANSI / UK BS-5499 / INT ISO-7010 with RESTRICTED). Jurisdiction-aware format selection + RESTRICTED override for IE > 40. SVG inline rendered; PDF/PNG deferred to calc.render_label per WI3. New 3 standards layers shipped alongside (ANSI-Z535-4 production + ISO-7010 new + BS-5499 new). |

---

## Mechanical

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| hvac-layout | `mechanical/hvac-layout` | stub | CIBSE Guide B, BSRIA | — | — |
| duct-routing | `mechanical/duct-routing` | stub | CIBSE Guide C, SMACNA | — | — |
| ventilation | `mechanical/ventilation` | stub | BB 101, HTM 03-01, CIBSE | — | — |
| pipe-routing | `mechanical/pipe-routing` | stub | CIBSE Guide C | — | — |
| chilled-water | `mechanical/chilled-water` | stub | CIBSE Guide B2 | — | — |
| plantroom-layout | `mechanical/plantroom-layout` | stub | CIBSE Guide B | — | — |
| mechanical-riser | `mechanical/mechanical-riser` | stub | CIBSE Guide B | — | — |
| isometric | `mechanical/isometric` | stub | BS 1192 | — | — |
| kitchen-extract | `mechanical/kitchen-extract` | stub | DW172, BS 9999 | — | — |
| smoke-extract | `mechanical/smoke-extract` | stub | BS EN 12101, BS 9999 | — | — |
| toilet-extract | `mechanical/toilet-extract` | stub | Building Regs F, HTM 03-01 | — | — |
| refrigerant-piping | `mechanical/refrigerant-piping` | stub | BS EN 378, F-Gas Regulation | — | — |
| controls | `mechanical/controls` | stub | CIBSE Guide H, BACnet | — | — |
| equipment-schedule | `mechanical/equipment-schedule` | stub | CIBSE | — | — |

---

## Plumbing

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| hot-cold-water | `plumbing/hot-cold-water` | stub | BS EN 806, Water Regs 1999 | — | — |
| sanitary-layout | `plumbing/sanitary-layout` | stub | BS EN 12056, Building Regs G | — | — |
| drainage | `plumbing/drainage` | stub | BS EN 12056-2, BS EN 752 | — | — |
| stormwater | `plumbing/stormwater` | stub | BS EN 12056-3, SUDS | — | — |
| sewer | `plumbing/sewer` | stub | BS EN 752, Sewers for Adoption | — | — |
| plumbing-riser | `plumbing/plumbing-riser` | stub | BS EN 806 | — | — |
| plumbing-schematic | `plumbing/plumbing-schematic` | stub | BS EN 806, BS 1192 | — | — |
| isometric | `plumbing/isometric` | stub | BS 1192 | — | — |
| water-supply | `plumbing/water-supply` | stub | BS EN 806, Water Regs 1999 | — | — |
| booster-pump | `plumbing/booster-pump` | stub | BS EN 806, Water Regs 1999 | — | — |
| manhole-layout | `plumbing/manhole-layout` | stub | BS EN 752, Sewers for Adoption | — | — |

---

## Fire Protection

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| sprinkler-layout | `fire-protection/sprinkler-layout` | stub | BS EN 12845, NFPA 13 | — | — |
| sprinkler-schematic | `fire-protection/sprinkler-schematic` | stub | BS EN 12845 | — | — |
| hydrant-layout | `fire-protection/hydrant-layout` | stub | BS 9990, BS EN 671 | — | — |
| hose-reel | `fire-protection/hose-reel` | stub | BS EN 671-1 | — | — |
| fp-riser | `fire-protection/fp-riser` | stub | BS EN 12845 | — | — |
| fire-pump-room | `fire-protection/fire-pump-room` | stub | BS EN 12845 | — | — |

---

## Calculations

### Electrical

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| cable-sizing | `electrical/cable-sizing` | **beta** | BS 7671:2018 App 4 + App 12 + Reg 433/434/521 + 543, IEC 60364-5-52 + 5-54, NEC 2023 Ch 9 + 310.16 + 215.2 + 220 + 240 + 250.122 + 310.10(H) + 430.6 + 110.14(C) | 9/3 ✓ | v1.0.0 IEC/BS/NEC cable selection. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (6 WI5 + 3 skill-specific), 3 worked examples (UK domestic / INT cascade with vd_cumulative / US industrial with parallel + motor-starting). Math deferred to calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic runtime tools per WI3. |
| voltage-drop | `electrical/voltage-drop` | stub | BS 7671:2018 Appendix 12, IEC 60364-5-52 §G, NEC 215.2 IN | — | — |
| load-schedule | `electrical/load-schedule` | stub | BS 7671:2018 App 1, NEC 220, IEC 60364-1 Annex C | — | — |
| fault-level | `electrical/fault-level` | **beta** | IEC 60909-0:2016, BS 7671 Reg 434, IEC 60364-4-43, NEC 110.9 + 240.86, IEC 60617 | 9/3 ✓ | v1.0.0 IEC 60909 HV+LV cascade. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (all WI5 + 3 skill-specific), 3 worked examples (UK / INT+gen / US+motors). New IEC60909 standards layer (13 files) shipped alongside. Cascade math deferred to calc.iec60909_cascade runtime tool per WI3. |
| generator-sizing | `electrical/generator-sizing` | stub | BS ISO 8528 | — | — |
| power-factor | `electrical/power-factor` | stub | BS EN 60831 | — | — |
| arc-flash | `electrical/arc-flash` | stub | IEEE 1584, BS EN 50110 | — | — |
| breaker-sizing | `electrical/breaker-sizing` | stub | BS 7671:2018, IEC 60947-2 | — | — |
| harmonic-analysis | `electrical/harmonic-analysis` | stub | G5/5, IEC 61000-3-2 | — | — |
| selectivity-study | `electrical/selectivity-study` | stub | IEC 60947-2 | — | — |

### Lighting

(Lighting calc folded into `electrical/lighting-layout` v1.3.0 production via `shared/calculations/lighting/lumen-method.json` inline contract.)

### HVAC

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| cooling-load | `mechanical/cooling-load` | stub | CIBSE Guide A, ASHRAE 90.1 | — | — |
| heating-load | `mechanical/heating-load` | stub | CIBSE Guide A | — | — |
| duct-sizing | `mechanical/duct-sizing` | stub | CIBSE Guide C, SMACNA | — | — |
| ventilation-rate | `mechanical/ventilation-rate` | stub | CIBSE Guide B2, Building Regs F | — | — |

### Plumbing

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| pipe-sizing | `plumbing/pipe-sizing` | stub | BS EN 806-3, CIBSE Guide G | — | — |
| pump-head | `plumbing/pump-head` | stub | CIBSE Guide G | — | — |
| tank-sizing | `plumbing/tank-sizing` | stub | Water Regs 1999, CIBSE Guide G | — | — |

---

## Documents

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| tender-report | `documents/tender-report` | stub | BS 7671, CDM 2015, CIBSE | — | — |
| bq | `documents/bq` | stub | NRM2 | — | — |
| method-statement | `documents/method-statement` | stub | CDM 2015 | — | — |
| cable-schedule | `documents/cable-schedule` | stub | BS 7671:2018 | — | — |
| specification | `documents/specification` | stub | NBS format | — | — |
| om-manual | `documents/om-manual` | stub | BSRIA BG 29, SFG20 | — | — |
| design-statement | `documents/design-statement` | stub | Planning requirements, Part L | — | — |

---

## Coordination

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| combined-services | `coordination/combined-services` | stub | BS 1192, ISO 19650 | — | — |
| clash-detection | `coordination/clash-detection` | stub | ISO 19650, BS 8541 | — | — |
| ceiling-coordination | `coordination/ceiling-coordination` | stub | BS 1192 | — | — |
| builders-work | `coordination/builders-work` | stub | BS 1192, CDM 2015 | — | — |
| 3d-routing | `coordination/3d-routing` | stub | ISO 19650 | — | — |
| ifc-export | `coordination/ifc-export` | stub | IFC 4x3, ISO 16739 | — | — |
| revit-mapping | `coordination/revit-mapping` | stub | ISO 19650 | — | — |

---

## Summary

| Status | Count |
|--------|-------|
| production | 1 |
| beta | 6 |
| draft | 0 |
| stub | 69 |
| **Total** | **76** |

**Beta (6):** `electrical/sld`, `electrical/db-layout`, `electrical/earthing`, `electrical/fault-level`, `electrical/cable-sizing`, `electrical/arc-flash`
**Production (1):** `electrical/lighting-layout`

---

## Standards layers (canonical content)

| Layer | Body | Status | Version | Jurisdiction | Verification |
|---|---|---|---|---|---|
| BS7671 | IET / BSI | production | 1.x | GB | verified-against-source |
| IEC60364 | IEC | production | 1.x | EU / INT | verified-against-source (most files; part5-52-cable-impedance.json marked draft) |
| NFPA70 | NFPA | production | 1.x | US | verified-against-source |
| KS1700 | KEBS | production | 1.0.0 | KE | draft-from-bs7671-derivative-needs-source-verification (new in earthing v1.2 — 2026-05-18) |

Skills consume one or more layers per their jurisdiction routing. See each skill's `skill.manifest.json` `standards` array for specific files referenced.

---

## Roadmap — next skills to promote

Tier 1 sequence (live):

1. ✅ Tighten calc contracts in `shared/calculations/electrical/` (shipped)
2. ✅ `electrical/fault-level` v1.0.0 beta (shipped 2026-05-16)
3. ✅ `electrical/cable-sizing` v1.0.0 beta (shipped 2026-05-16)
4. ✅ Phase A: IEEE 1584 + NFPA 70E standards layers (shipped 2026-05-17)
5. ✅ Phase B: `electrical/arc-flash` v1.0.0 beta (shipped 2026-05-17)
6. ✅ clause_ref retrofit for 93 pre-existing files (shipped 2026-05-17)
7. ✅ `electrical/arc-flash-labelling` v1.0.0 beta + ANSI-Z535-4 + ISO-7010 + BS-5499 (shipped 2026-05-17)
8. ✅ `electrical/earthing` v1.1.0 — TN-S + Zs table + KE example (shipped 2026-05-17)
9. ✅ `electrical/earthing` v1.2.0 — KS 1700 standards layer + citation refactor (shipped 2026-05-18)
10. `electrical/db-layout` v1.1 — DC distribution + Type B RCD
10. `electrical/voltage-drop` (or fold into cable-sizing)
11. `electrical/sld` v1.2 — eval split

Tier 2 (next):
- `electrical/small-power` — high-demand skill, BS 7671 socket-outlet layouts
- `electrical/emergency-lighting` — depends on lighting-layout patterns
- `documents/cable-schedule` — consumes `cable-sizing` intent
