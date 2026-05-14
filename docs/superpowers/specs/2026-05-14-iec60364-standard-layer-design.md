# IEC 60364 Standard Layer — Design Spec

**Date:** 2026-05-14
**Status:** Approved
**Scope:** Build the IEC 60364 shared standards layer to the same depth as the existing BS7671 layer.

---

## 1. Goal

Populate `shared/standards/electrical/IEC60364/` with machine-readable engineering data files and narrative reference files so that any DraftsMan skill can reference IEC 60364 values directly — the same way skills already reference BS7671.

IEC 60364 is the international parent standard from which most national codes derive (BS7671 UK, NF C 15-100 France, DIN VDE 0100 Germany, NIS 197 Nigeria, SANS 10142 South Africa, AS/NZS 3000 Australia). Having it as a standalone layer lets the platform support non-UK projects without routing through BS7671.

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| File independence | **Fully self-contained** — IEC-native values only | Skills reference one standard layer, no cross-dependency. IEC tables have genuine differences from BS7671 (reference ambient, voltage drop limits, country guidance). |
| File naming | **IEC clause-based** (`part4-41-xxx`, `part5-52-xxx`) | Traceable to standard clause numbers. Familiar analogy to BS7671 naming for engineers who know both. |
| Part 7 coverage | **Core 8 locations** (701, 702, 704, 705, 708, 710, 712, 722) | Covers 90% of real-world scenarios. Niche locations (sauna, fairgrounds, caravans) added later when a skill needs them. |
| Local codes | **Out of scope for this spec** | Nigeria, Kenya, South Africa are a separate brainstorm. This spec is IEC 60364 only. |

---

## 3. Current State

Two files already exist and are complete:

| File | Status |
|------|--------|
| `meta.json` | Complete — all 20+ parts catalogued with editions and amendments |
| `terminology.md` | Complete — all IEC 60364 symbols defined with formulas |

`README.md` exists as a stub (`# IEC60364`) and must be rewritten.

---

## 4. File Set — 27 Files Total

### 4.1 Already done (2)
- `meta.json`
- `terminology.md`

### 4.2 Rewrite (1)
- `README.md` — comprehensive index matching BS7671/README.md structure

### 4.3 JSON — machine-readable engineering data (16)

| File | IEC Source | Engineering Content |
|------|-----------|---------------------|
| `part4-41-electric-shock.json` | Part 4-41, Table 41.1 | ADS disconnection times for TN/TT/IT at all voltage levels. Zs_max tables for MCB types B/C/D and fuses at 230V. SELV/PELV voltage limits and requirements. |
| `rcd-requirements.json` | Part 4-41.3, Part 5-31 | Mandatory RCD locations. Types AC/A/F/B with use cases. Trip time requirements at IΔn and 5×IΔn. S-type delay for selectivity. |
| `part4-43-overcurrent.json` | Part 4-43 | Fundamental Rule Ib ≤ In ≤ Iz in full. Overload protection (Clause 433). Short-circuit protection (Clause 434). Coordination guidance. Permitted omissions. |
| `fault-current.json` | Part 4-43.4, Clause 543 | Adiabatic equation I²t ≤ k²S². k-values table: copper/PVC (115), copper/XLPE (143), aluminium/PVC (74), aluminium/XLPE (94), steel armour, CPCs. Worked example. |
| `part4-44-overvoltage.json` | Part 4-44, AMD2:2018 | SPD Types 1/2/3. Impulse withstand categories I–IV (IEC 60664-1). Uc and Up selection. Mandatory installation scope per AMD2. Coordination. Energy backup fuses. |
| `part5-52-cable-ratings-copper.json` | Part 5-52, Annex B | Copper cable current ratings for all reference methods A1, A2, B1, B2, C, D1, D2, E, F. Both PVC (70°C) and XLPE/EPR (90°C) insulation. Sizes 1.5mm² to 630mm². |
| `part5-52-cable-ratings-aluminium.json` | Part 5-52, Annex B | Aluminium cable ratings for methods C, D2, E. 16mm² to 630mm². Use-case guidance and termination requirements. |
| `part5-52-correction-factors.json` | Tables B.52.14–20 | Ca (ambient temperature, 10°C to 80°C, PVC and XLPE). Cg (grouping, 1–20 circuits, all methods). Ci (thermal insulation). Cs (soil thermal resistivity). Cd (depth of burial). Cf (harmonic current derating). |
| `part5-52-voltage-drop.json` | Part 5-52, Annex G | Recommended limits: 3% lighting, 5% other (informative). mV/A/m for all standard copper and aluminium sizes. Worked calculation example including fail case. Three-phase vs single-phase formula. |
| `part5-52-installation-methods.json` | Part 5-52, Clause 521, Annex B | Reference methods A1, A2, B1, B2, C, D1, D2, E, F, G — descriptions, conditions, which cable types apply, design notes. |
| `part5-52-ip-requirements.json` | Part 5-52, Clause 522, BS EN 60529 | IP code explanation (first digit solids, second digit water). Minimum IP by location type. IK impact codes. Common under-specification traps. |
| `part5-54-earthing.json` | Part 5-54, Clauses 541–544 | Minimum PE cross-section vs line conductor (Table 54.1). Main bonding conductor sizing. Supplementary bonding. Earth electrode types and resistance targets. TN/TT/IT earthing arrangement requirements. |
| `device-curves.json` | Part 5-53, IEC 60898, IEC 60269 | Time/current trip characteristics: MCB Types B, C, D. gG fuses. RCD trip times. Let-through energy I²t. Selectivity methods (current, time, energy, ZSI). Practical examples. |
| `part6-verification.json` | Part 6, Clauses 61–63 | Initial verification sequence (inspect first, then test). Test methods: continuity, insulation resistance, polarity, Zs, RCD, PSCC. Pass/fail criteria. Documentation requirements. Periodic inspection intervals. |
| `part7-special-locations.json` | Part 7 Sections 701, 702, 704, 705, 708, 710, 712, 722 | Zone definitions, IP requirements, prohibited/permitted equipment, RCD requirements, bonding requirements for each of the 8 locations. |
| `diversity-factors.json` | Part 3, IEC 60364-3 | Demand factors for domestic, commercial, industrial, EV charging. Maximum demand calculation method. Worked example. |

### 4.4 MD — narrative reference (8)

| File | Content |
|------|---------|
| `earthing-systems.md` | TN-S, TN-C, TN-C-S, TT, IT — ASCII diagrams, when to use each, common errors |
| `protective-device-types.md` | MCB B/C/D, RCBO, RCD, fuse gG/aM, MCCB, ACB — selection by application |
| `cable-types-overview.md` | PVC, XLPE, EPR, MICC, SWA, LSZH — selection by application and environment |
| `compliance-checklist.md` | End-of-design checklist — 30+ items with clause references, traceable evidence |
| `pscc-determination.md` | How to obtain or calculate PSCC at any point. Methods: measured, calculated, DNO data |
| `verification.md` | Part 6 narrative — initial verification, periodic inspection, test certificates |
| `relationship-to-national-codes.md` | IEC 60364 vs BS7671, NF C 15-100, DIN VDE 0100, AS/NZS 3000, NIS 197 — what's the same, what differs |
| `amendments-summary.md` | Key amendments across all active parts — what changed, practical impact |

---

## 5. Content Standards

Every file must match the depth of the BS7671 layer:

- **JSON files**: Include `_title`, `_reference` (clause number), `_note` (usage guidance), `_version`. All values annotated with source clause. Include worked examples where BS7671 equivalents have them.
- **MD files**: Engineering narrative quality — not summaries, not bullet lists. An engineer should be able to use these files to make a design decision without consulting the standard.
- **No invented values**: Every number must trace to a published IEC 60364 clause, annex table, or a directly derived calculation (formula shown).

---

## 6. File Tree (final state)

```
IEC60364/
├── README.md                              ← rewrite
├── meta.json                              ← done
│
├── Reference & narrative (.md)
│   ├── terminology.md                     ← done
│   ├── earthing-systems.md
│   ├── protective-device-types.md
│   ├── cable-types-overview.md
│   ├── compliance-checklist.md
│   ├── pscc-determination.md
│   ├── verification.md
│   ├── relationship-to-national-codes.md
│   └── amendments-summary.md
│
└── Machine-readable data (.json)
    ├── part4-41-electric-shock.json
    ├── rcd-requirements.json
    ├── part4-43-overcurrent.json
    ├── fault-current.json
    ├── part4-44-overvoltage.json
    ├── part5-52-cable-ratings-copper.json
    ├── part5-52-cable-ratings-aluminium.json
    ├── part5-52-correction-factors.json
    ├── part5-52-voltage-drop.json
    ├── part5-52-installation-methods.json
    ├── part5-52-ip-requirements.json
    ├── part5-54-earthing.json
    ├── device-curves.json
    ├── part6-verification.json
    ├── part7-special-locations.json
    └── diversity-factors.json
```

---

## 7. Out of Scope

- Local codes (Nigeria, Kenya, South Africa) — separate brainstorm
- IEC 60617 symbol updates — separate standard layer
- IEC 61439 switchgear layer — separate standard layer
- Fire-rated cable product data (FP200/FP400) — UK-specific, stays in BS7671 layer
- Skills that consume this layer — this spec covers the data layer only
