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
| lighting-layout | `electrical/lighting-layout` | **production** | BS EN 12464-1:2021, Part L 2021 | 7/5 ✓ | Reference implementation. 7 evals, 3 examples, full IR schema. |
| sld | `electrical/sld` | **beta** | BS 7671:2018, BS EN 60617 | 8/3 ✓ | v1.1.0 prompts complete. 8 evals, 4 examples. Separate eval YAML files pending. |
| db-layout | `electrical/db-layout` | stub | BS 7671:2018, BS EN 61439 | — | — |
| cable-containment | `electrical/cable-containment` | stub | BS 7671:2018, BS 1192 | — | — |
| riser | `electrical/riser` | stub | BS 7671:2018 | — | — |
| schematic | `electrical/schematic` | stub | BS EN 60617 | — | — |
| small-power | `electrical/small-power` | stub | BS 7671:2018 | — | — |
| earthing | `electrical/earthing` | stub | BS 7671:2018 Part 5-54 | — | — |
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
| cable-sizing | `calculations/electrical/cable-sizing` | stub | BS 7671:2018 Appendix 4 | — | — |
| voltage-drop | `calculations/electrical/voltage-drop` | stub | BS 7671:2018 Appendix 12 | — | — |
| load-schedule | `calculations/electrical/load-schedule` | stub | BS 7671:2018 | — | — |
| fault-level | `calculations/electrical/fault-level` | stub | IEC 60909 | — | — |
| generator-sizing | `calculations/electrical/generator-sizing` | stub | BS ISO 8528 | — | — |
| power-factor | `calculations/electrical/power-factor` | stub | BS EN 60831 | — | — |
| arc-flash | `calculations/electrical/arc-flash` | stub | IEEE 1584, BS EN 50110 | — | — |
| breaker-sizing | `calculations/electrical/breaker-sizing` | stub | BS 7671:2018, IEC 60947-2 | — | — |
| harmonic-analysis | `calculations/electrical/harmonic-analysis` | stub | G5/5, IEC 61000-3-2 | — | — |
| selectivity-study | `calculations/electrical/selectivity-study` | stub | IEC 60947-2 | — | — |

### Lighting

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| lux | `calculations/lighting/lux` | stub | CIBSE SLL Code 2012, BS EN 12464-1 | — | — |

### HVAC

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| cooling-load | `calculations/hvac/cooling-load` | stub | CIBSE Guide A, ASHRAE 90.1 | — | — |
| heating-load | `calculations/hvac/heating-load` | stub | CIBSE Guide A | — | — |
| duct-sizing | `calculations/hvac/duct-sizing` | stub | CIBSE Guide C, SMACNA | — | — |
| ventilation-rate | `calculations/hvac/ventilation-rate` | stub | CIBSE Guide B2, Building Regs F | — | — |

### Plumbing

| Skill | Path | Status | Standards | Evals | Notes |
|-------|------|--------|-----------|-------|-------|
| pipe-sizing | `calculations/plumbing/pipe-sizing` | stub | BS EN 806-3, CIBSE Guide G | — | — |
| pump-head | `calculations/plumbing/pump-head` | stub | CIBSE Guide G | — | — |
| tank-sizing | `calculations/plumbing/tank-sizing` | stub | Water Regs 1999, CIBSE Guide G | — | — |

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
| beta | 1 |
| draft | 0 |
| stub | 74 |
| **Total** | **76** |

---

## Roadmap — next skills to promote

Priority order based on engineering dependency chain:

1. `calculations/electrical/cable-sizing` — prerequisite for db-layout, sld verification
2. `calculations/electrical/voltage-drop` — referenced in cable-sizing
3. `electrical/db-layout` — depends on cable-sizing + sld
4. `calculations/electrical/load-schedule` — feeds db-layout and sld
5. `calculations/lighting/lux` — extends lighting-layout calculations
6. `electrical/small-power` — high-demand skill, independent of above
7. `electrical/earthing` — required for sld completion
8. `electrical/emergency-lighting` — depends on lighting-layout patterns
