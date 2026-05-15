# NFPA 70 (NEC) ↔ IEC 60364 — Divergence Catalogue

The single most-consumed cross-jurisdiction reference. Skills working across
US/Europe/international project teams load this MD to surface differences at
design time.

---

## 1. Terminology — the silent breakers

| NEC | IEC | Why it matters |
|---|---|---|
| **Grounding** | **Earthing** | Same concept, different word. Never mix in a single drawing/spec. |
| **Grounded conductor** | **Neutral** | NEC's "grounded" because in TN-C-S the neutral IS grounded at the service |
| **Equipment grounding conductor (EGC)** | **Circuit protective conductor (CPC)** | Sizing rules differ — see Section 4 below |
| **Grounding electrode conductor (GEC)** | (no exact term; closest: main earthing conductor) | Different sizing rule |
| **Main bonding jumper (MBJ)** | Main earthing terminal connection | NEC has explicit hardware concept |
| **GFCI** Class A (4-6 mA trip) | **RCD** (typically 30 mA general use) | GFCI more sensitive than IEC RCD — different protection scope |
| **AFCI** | (no exact equivalent in IEC 60364 base) | NEC mandates; IEC 62606 (AFDD) is optional in IEC base |
| **AWG / kcmil** | **mm²** | AWG decreases as size increases; mm² is direct |
| **Branch circuit** | **Final circuit** | Same idea |
| **Feeder** | **Sub-main / distribution circuit** | NEC keeps "feeder" as distinct legal category |
| **Service** | **DNO/utility supply intake** | NEC has detailed service rules; IEC less prescriptive |
| **Ampacity** | **Current-carrying capacity (Iz)** | Same |
| **Disconnecting means** | **Isolating switch** | Same |
| **Hospital grade** | (no exact term) | NEC-specific receptacle classification (UL 498) |

---

## 2. Earthing systems

| Topic | NEC | IEC |
|---|---|---|
| TN-C permissible scope | ONLY within service equipment (250.142). After the service disconnect, neutral and EGC must be separate. | TN-C permitted throughout an installation for cables ≥10 mm² Cu / 16 mm² Al. |
| Required electrodes (250.50 / 542) | Concrete-encased electrode (Ufer) REQUIRED when present at new buildings (250.50(A)(3)). All present electrodes must be bonded together. | Concrete-encased optional. Specific electrodes mandated by national supplement. |
| Earthing system declarations | NEC does not classify systems as "TN-S / TN-C-S / TT / IT" — uses prescriptive rules (250.20 mandates grounding for certain system configurations) | IEC classifies explicitly per IEC 60364-1 Clause 312 |

---

## 3. Voltage and equipment ratings

| Topic | NEC | IEC |
|---|---|---|
| Nominal voltage (residential) | 120 V single-phase (split 240/120) | 230 V single-phase |
| Nominal voltage (3-phase commercial) | 208Y/120 V, 480Y/277 V (US wye); 240V delta common | 400Y/230 V (Europe), 415Y/240 V (UK) |
| Frequency | 60 Hz | 50 Hz |
| Working clearance (NEC 110.26) | Tabulated in ft/in by voltage × condition (1/2/3) | IEC 60364-7-729 less prescriptive — metric, fewer condition tiers |
| Termination temperature rule | NEC 110.14(C) limits conductor ampacity to terminal temperature rating | No equivalent — IEC ampacity tables (Annex B) assume terminations rated to conductor |

---

## 4. Conductor / cable sizing — the largest divergence area

| Topic | NEC | IEC |
|---|---|---|
| Conductor identification | AWG (decreasing number = larger) + kcmil (large) | mm² (direct) |
| Ampacity tables | Table 310.16 (raceway/cable), 310.17 (free air); columns by temperature rating (60/75/90 °C) | Annex B (60364-5-52); rows by installation method (A1/A2/B1/B2/C/D/E/F) and insulation type (PVC/XLPE/EPR) |
| Ambient correction | Table 310.15(B)(1) — by ambient temp × conductor temp rating | Annex B Tables B.52.14, B.52.15 |
| Grouping correction | Table 310.15(C)(1) — 4-6: 80%, 7-9: 70%, etc. | Annex B Table B.52.17 |
| EGC / CPC sizing | NEC Table 250.122 — by OCPD rating | IEC Table 54.1 — by line-conductor CSA, OR adiabatic |
| GEC sizing | NEC Table 250.66 — by largest ungrounded service conductor | No exact analogue — main earthing conductor sized adiabatically or per local supplement |

### EGC vs CPC — same circuit, different sizes

**Example:** Branch circuit on a 100 A OCPD with #4 AWG (~21 mm²) phase conductors.

- **NEC EGC (250.122):** #8 AWG (~8 mm²) — sized from the 100 A OCPD rating.
- **IEC CPC (Table 54.1):** For S = 21 mm² (>16 mm²), CPC = S/2 = ~10 mm².

The IEC CPC is larger than the NEC EGC on this example. The reverse can be true on circuits with high OCPD rating relative to phase conductor.

---

## 5. Protective devices

| Topic | NEC | IEC |
|---|---|---|
| OCPD interrupting rating | "Interrupting rating" (AIC) — single value | Icu (ultimate) and Ics (service) — two values per device |
| Series ratings | Permitted (240.86) under tested combinations | Cascading permitted (IEC 60364-4-43 Annex D) but more cautious |
| AFCI | Mandatory (210.12) — combination AFCI (UL 1699) | Optional in IEC 60364 base; IEC 62606 AFDD emerging |
| GFCI | Class A 4-6 mA (UL 943) — personnel protection | RCD 30 mA general use (IEC 61008/61009) — broader scope |
| SPD (NEC 242 / IEC 60364-4-44) | UL 1449 types 1, 2, 3, 4 | IEC 61643-11 types 1, 2, 3 |

---

## 6. Hazardous locations

| Topic | NEC | IEC |
|---|---|---|
| Classification system | Two parallel: Division (Arts 500-503, legacy US) and Zone (Arts 505-506, IEC-aligned) | Zone only (IEC 60079) |
| Gas groups | A (acetylene), B (hydrogen), C (ethylene), D (propane/methane) | IIA, IIB, IIC (with IIC most severe — covers acetylene + hydrogen) |
| Dust groups | E (metal), F (carbon), G (grain) | IIIA, IIIB, IIIC |

Equipment certified for NEC Division and IEC Zone are not freely interchangeable.
See `hazardous-locations-classification.json` for the full conversion matrix.

---

## 7. Specific applications

### EV charging

| Aspect | NEC 625 | IEC 60364-7-722 |
|---|---|---|
| Cable sizing | 125% of EVSE input current (625.41(B)) | 100% of EVSE rated current — no diversity |
| GFCI / DC leakage protection | Class A or EGFCI (625.54) integral to EVSE | Type B RCD where DC leakage > 6 mA |
| PME / TN-C-S broken-PEN protection | Not explicitly addressed | Required (IEC 60364-7-722 + national supplements) |

### PV

| Aspect | NEC 690 | IEC 60364-7-712 |
|---|---|---|
| Max voltage | 600 V dwelling, 1000 V or 1500 V non-dwelling | Typically 1500 V per national supplements |
| DC arc fault | Mandatory ≥80 V DC (690.11) | No equivalent (DC AFD emerging in IEC 60947) |
| Rapid shutdown | Mandatory on rooftop PV (690.12) | No equivalent in IEC base |
| OCPD sizing | 125% × 125% (156% of module Isc) | Iz × design current — no cascading multiplier |

### Healthcare

| Aspect | NEC 517 | IEC 60364-7-710 |
|---|---|---|
| Patient care classification | Categories 1-4 | Group 0/1/2 + safety/critical/general categories |
| Essential Electrical System | Type 1 (three branches: Life Safety / Critical / Equipment), Type 2, Type 3 | Equivalent essential power supply via 60364-7-710 |
| Isolated power | LIM (Line Isolation Monitor) per UL 1022 | IMD (Insulation Monitoring Device) per IEC 61557-8 |

### Pools / spas

| Aspect | NEC 680 | IEC 60364-7-702 |
|---|---|---|
| Receptacle clearances | Imperial (5 ft / 6-20 ft / 20 ft for pools; 10 ft for spas) | Zone-based (Zone 0, 1, 2) with metric envelopes |
| Equipotential bonding | Mandatory grid, #8 AWG solid Cu, includes pool steel + deck + fittings (680.26) | Supplementary bonding required — less prescriptive on grid construction |

---

## 8. Working clearances (110.26 vs IEC 60364-7-729)

| Voltage to ground | NEC 110.26(A)(1) — Condition 1 (live one side, no live other) | IEC 60364-7-729 |
|---|---|---|
| 0–150 V | 36 in (~915 mm) | ~700 mm typical (national variations) |
| 151–600 V | 36 in | ~700 mm |
| 601–1000 V | 36 in | 1000 mm |

NEC requires width ≥30 in OR equipment width; headroom ≥6.5 ft. IEC less prescriptive.

---

## 9. Receptacle outlet rules

| Topic | NEC | IEC |
|---|---|---|
| Spacing rule (dwelling) | "No point along wall > 6 ft from outlet" (210.52(A)) | No NEC-like rule — national supplements vary |
| Tamper-resistant requirement | Mandatory in dwelling units (406.12) | No equivalent (relies on socket design — BS 1363 shutters, Schuko, etc.) |
| Outdoor weather resistance | Listed for damp/wet + in-use cover where wet (406.9) | IP rating per IEC 60529 |
| GFCI receptacle | Class A (4-6 mA) per UL 943 | Local-RCD (30 mA general) per IEC 61008 |

---

## 10. The bottom line for designers

**On a US-only project:** Use NEC consistently. Do not introduce IEC terminology.

**On a project in an IEC jurisdiction:** Use IEC 60364 + the relevant national
supplement (BS 7671 UK, AS/NZS 3000 Australia, etc.).

**On a project with both US and IEC elements** (e.g. US-owned factory in
Europe, multinational data centre, US navy facility abroad):
- Set the primary jurisdiction in the design brief.
- Document the terminology choice (one OR the other).
- Cross-reference both standards on items with significant divergence (grounding,
  conductor sizing, hazardous locations, healthcare, EV/PV).
- Engage the AHJ early — they decide which standard applies and which deviations
  are acceptable.

This MD covers the most-cited differences. For the full divergence per article,
each NEC article's `divergence_notes` field in the per-article JSON files
captures the specific divergence at that article level.
