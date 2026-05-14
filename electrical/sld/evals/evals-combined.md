# EVALS — sld skill

Evaluation criteria for testing the sld skill. Each eval defines a test
input, the expected reasoning steps, and pass/fail criteria for the output.
Use these to verify a skill version before shipping.

---

## Eval 01 — Basic commercial office building (happy path)

**Input:**
```
Building: 3-storey office, 1500m² GIA
Supply: 3-phase TN-C-S, 400V/230V, 50Hz
Ze at supply terminals: 0.35 Ω (confirmed by DNO)
PSCC at supply: 657 A = 0.66 kA
Load schedule:
  SDB-GF (Ground Floor): 30 kVA total, PF 0.85, 3-phase
  SDB-L1 (Level 1):      28 kVA total, PF 0.85, 3-phase
  SDB-L2 (Level 2):      28 kVA total, PF 0.85, 3-phase
Diversity: general office loads
Generator: none
```

**Expected reasoning shown in chat:**

| Step | Expected | Pass criteria |
|---|---|---|
| Step 2 | Tree: MSB → SDB-GF, SDB-L1, SDB-L2 | Hierarchy shown before any calculation |
| Step 3 | Ib_GF = 30k / (0.6928 × 1000) = 43.3A → 44A | Ib within ±1A of 43A |
| Step 4 | Diversity applied: lighting 0.90, sockets 0.50 | All diversity flagged as [ASSUMPTION] |
| Step 5 | MCCBs: SDB incomers ≥ Ib; MSB incomer ≥ total demand | In never < Ib; Icu ≥ 0.66kA confirmed |
| Step 8 | PSCC at SDB-L2 ≤ PSCC at MSB | PSCC decreases as Ze increases down the chain |

**Expected JSON output:**

- `supply.ze_ohm` = 0.35
- `supply.pscc_ka_at_supply` ≥ 0.60
- Each `boards[].incomer.rating_a` ≥ that board's `maximum_demand_kva / 0.6928 / 1000`
- Each `boards[].incomer.breaking_capacity_ka` ≥ `pscc_ka` at that board
- `connections[]` has 3 entries (one per SDB)
- `calculation_summary.compliant` = true
- `calculation_summary.assumptions` non-empty (PF and diversity always assumed)
- `earthing.system` = "TN-C-S"
- `earthing.bonding_connections` includes gas, water, structural_steel

**Fail conditions:**
- Any board incomer `rating_a` < board `maximum_demand_kva / 0.6928 / 1000`
- Any device `breaking_capacity_ka` < `pscc_ka` at that board
- No [ASSUMPTION: ...] tags for diversity or PF
- `calculation_summary.assumptions` array empty
- PSCC at SDB-L2 > PSCC at MSB (PSCC must decrease downstream)
- JSON missing `earthing` top-level key

---

## Eval 02 — Missing supply PSCC data

**Input:**
```
Building: retail unit
Supply: 3-phase TN-C-S, 400V, 50Hz
Ze at supply: NOT PROVIDED
Load: 45 kVA total, PF 0.85
Boards: MSB → SDB-RETAIL
```

**Expected behaviour:**

The skill must flag the missing PSCC before proceeding with device selection.
It must not silently select a breaking capacity or assume Ze.

**Pass criteria:**
- Output includes `[NON-COMPLIANCE RISK: PSCC at supply not provided...]` in chat
- Output references BS EN 60947-2 (MCCB breaking capacity standard)
- Skill continues to produce a layout, but marks every device's breaking capacity
  with a flag — it does not silently assume a breaking capacity is adequate
- `calculation_summary.non_compliance_flags` non-empty in JSON
- `supply.pscc_ka_at_supply` = 0.0 in JSON (not a guessed value)
- A drawing note states "PSCC requires confirmation from DNO before tender"

**Fail conditions:**
- Skill selects an MCCB breaking capacity (e.g. 10kA) without flagging that PSCC
  is unconfirmed
- Skill refuses to produce any JSON output (it should produce output with flags)
- `supply.ze_ohm` contains a guessed value with no [ASSUMPTION] tag

---

## Eval 03 — Fundamental Rule violation check

**Input:**
```
Building: plant room sub-board
Supply: 3-phase TN-C-S, 400V
Ze: 0.40 Ω
SDB-PLANT incomer: engineer requests a 63A MCCB
Load on SDB-PLANT: 3 × 25kW pumps (PF 0.85, 3-phase each)
```

**Expected behaviour:**

The design current for 3 × 25kW at PF 0.85 three-phase is:
```
Ib = (3 × 25 × 1000) / (1.732 × 400 × 0.85) = 75,000 / 587.9 = 127.6A → 128A
```

A 63A MCCB with Ib = 128A violates the Fundamental Rule. The skill must refuse
to accept the 63A device and propose compliant sizing.

**Pass criteria:**
- Skill calculates Ib = 127–129A for the combined load
- Skill explicitly states: "63A MCCB violates Regulation 433.1.1 (Ib ≤ In not
  satisfied: 128A > 63A)"
- Skill proposes In ≥ 128A — minimum acceptable device is 160A MCCB
- `calculation_summary.non_compliance_flags` non-empty
- Final JSON uses 160A (or greater) device, not 63A
- 63A device does not appear in the boards array

**Fail conditions:**
- Skill accepts 63A device without flagging Fundamental Rule violation
- Skill flags the violation but still emits JSON with 63A device
- Ib calculation differs by more than 5A from 128A
- No reference to Regulation 433.1.1 in the non-compliance flag

---

## Eval 04 — RCD protection identification

**Input:**
```
Building: open plan office floor
Board: SDB-L1 with the following outgoing circuits:
  Way 1: Lighting — 3×10A MCBs, 3-phase
  Way 2: General socket outlets — 6×16A MCBs, single-phase
  Way 3: Dedicated IT outlets — 4×16A MCBs, single-phase
  Way 4: HVAC FCU circuit — 32A MCB, 3-phase
  Way 5: Outdoor equipment socket — 1×16A MCB, single-phase
```

**Expected behaviour:**

The skill must identify which circuits require 30mA RCD protection per
Regulation 411.3.3:
- Way 2 (socket outlets ≤ 32A): RCD required
- Way 3 (socket outlets ≤ 32A): RCD required
- Way 5 (outdoor equipment socket ≤ 32A): RCD required
- Way 1 (lighting): RCD not mandatory (but recommended in some positions)
- Way 4 (HVAC FCU, fixed equipment): RCD not mandatory

**Pass criteria:**
- Ways 2, 3, and 5 have `rcd: true` and `rcd_sensitivity_ma: 30`
- Way 4 (HVAC) has `rcd: false`
- Skill explicitly cites Regulation 411.3.3 for each RCD requirement
- Skill notes Way 5 as "outdoor circuit" requiring 30mA protection
- `calculation_summary.rcd_protected_ways` = 3
- If Way 1 lighting RCD is recommended but not mandatory, that is flagged as a
  recommendation, not an error

**Fail conditions:**
- Ways 2, 3, or 5 have `rcd: false`
- Way 4 (HVAC fixed equipment) incorrectly has `rcd: true` without explanation
- No Regulation 411.3.3 citation for RCD requirements
- `rcd_sensitivity_ma` is null for any RCD-protected way

---

## Eval 05 — Diversity calculation with multiple load types

**Input:**
```
Building: 4-storey office and retail mixed-use
Supply: 3-phase TN-C-S, 400V, Ze = 0.28 Ω
MSB feeds:
  SDB-RETAIL  — Retail floor: 20kW lighting, 15kW sockets, PF 0.85
  SDB-OFFICE  — Office floors: 18kW lighting, 25kW sockets, 10kW IT, PF 0.85
  SDB-HVAC    — HVAC plant: 40kW chillers (continuous), 15kW FCUs, PF 0.85
  SDB-LIFT    — Lift plant: 2 lifts × 7.5kW each, PF 0.85
```

**Expected behaviour:**

The skill must apply correct diversity to each load type and produce a
defensible maximum demand figure.

| Board | Load breakdown | Expected max demand (approx) |
|---|---|---|
| SDB-RETAIL | 20kW lighting @ 0.90 + 15kW sockets @ 0.50 | ~47A |
| SDB-OFFICE | 18kW @ 0.90 + 25kW @ 0.50 + 10kW @ 0.80 | ~72A |
| SDB-HVAC | 40kW @ 1.00 + 15kW @ 0.75 | ~100A |
| SDB-LIFT | 7.5kW @ 1.00 + 7.5kW @ 0.50 | ~22A |
| MSB total | Sum with building diversity | ~220–240A |

**Pass criteria:**
- Diversity factor for HVAC continuous plant is 1.00 (no diversity applied)
- Diversity factor for lighting ≥ 0.85 (not lower — lighting is near-continuous)
- Diversity factor for sockets ≤ 0.65
- Second lift at 0.50 diversity (not 1.00)
- MSB MCCB selected as next standard size above total maximum demand
- All diversity factors flagged as [ASSUMPTION] with load category stated
- `calculation_summary.overall_diversity_factor` between 0.60 and 0.80

**Fail conditions:**
- Continuous HVAC load has diversity < 1.00 applied
- Both lifts at 1.00 diversity (only first lift is 1.00)
- No diversity applied to socket loads (treating as 1.00)
- `calculation_summary.overall_diversity_factor` > 0.90 (implies insufficient
  diversity applied — inflates the MSB rating unnecessarily)
- MSB incomer In < total maximum demand current

---

## Eval 06 — Zs disconnection time compliance check

**Input:**
```
Building: office floor sub-board
Board: SDB-L3 fed from MSB
Supply: TN-C-S, Ze at MSB = 0.45 Ω
Cable: MSB → SDB-L3: 50m, 10mm² 4C+CPC Cu, method E
Outgoing circuit at SDB-L3:
  Way 1: Socket outlets, 20A Type C MCB
  Cable SDB-L3 → Way 1 sockets: 30m, 2.5mm² 2C+CPC
```

**Expected reasoning:**

```
Step 7 — Ze at SDB-L3:
  Zcable_MSB_to_SDB = (2 × 0.0225 × 50) / 10 = 0.225Ω
  Ze_SDB-L3 = 0.45 + 0.225 = 0.675Ω
  PSCC at SDB-L3 = 230 / 0.675 = 341A = 0.34kA → MCB Icu 3kA >> 0.34kA ✓

Step 8 — Zs for socket circuit (Way 1):
  R1 = 0.0225 × 30 / 2.5 = 0.270Ω  (phase conductor)
  R2 = 0.0225 × 30 / 1.5 = 0.450Ω  (CPC, 1.5mm² per Table 54.7)
  Zs = 0.675 + 0.270 + 0.450 = 1.395Ω

  Zs_max for 20A Type C MCB (0.4s, Table 41.2) = 1.15Ω

  1.395Ω > 1.15Ω → NON-COMPLIANCE
```

**Pass criteria:**
- Skill calculates Ze at SDB-L3 = 0.67–0.68Ω
- Skill calculates Zs for Way 1 socket circuit = 1.38–1.40Ω
- Skill identifies Zs_max for 20A Type C MCB = 1.15Ω (from Table 41.2)
- Output includes `[NON-COMPLIANCE RISK: Zs = 1.40Ω exceeds Zs_max = 1.15Ω...]`
- Skill proposes at least one remediation option: reduce cable length,
  increase CPC size, change to Type B MCB, or install 30mA RCD
- `boards[SDB-L3].zs_compliant` = false in JSON
- `calculation_summary.zs_check_compliant` = false
- `calculation_summary.non_compliance_flags` non-empty

**Fail conditions:**
- Skill calculates Zs without showing R1 and R2 separately
- Skill states Zs_max from Table 41.3 (5s) instead of Table 41.2 (0.4s for ≤32A)
- Skill does not propose any remediation
- `zs_compliant` = true when Zs > Zs_max
- No reference to BS 7671:2018 Table 41.2 in output

---

## Eval 07 — Life safety circuit identification

**Input:**
```
Building: 3-storey office with life safety systems
Supply: TN-C-S, 3-phase, 400V
Ze = 0.35Ω
Load schedule includes:
  - Fire alarm and detection panel (BS 5839-1): 2kVA, single-phase
  - Emergency lighting (BS 5266-1): 1.5kVA, single-phase
  - Smoke extract fan: 7.5kW, 3-phase, dedicated circuit
  - General office distribution: 60kVA across 3 floors
Generator: 20kVA diesel standby
```

**Expected behaviour:**

The skill must identify the three life safety circuits, specify fire-rated
cables, assign them to the essential bus, and separate them from general
distribution.

**Pass criteria:**
- Fire alarm circuit: `fire_rated: true`, `cable_type: "FP200"`,
  `fire_rating_minutes: 30`, `life_safety: true` in circuit and connection
- Emergency lighting circuit: `fire_rated: true`, `cable_type: "FP200"`,
  `fire_rating_minutes: 60`, `life_safety: true`
- Smoke extract circuit: `fire_rated: true`, `cable_type: "FP400"`,
  `fire_rating_minutes: 120`, `life_safety: true`
- All three circuits assigned `power_source: "essential_bus"` in
  `life_safety_circuits[]`
- `calculation_summary.life_safety_circuits_count` = 3
- Life safety circuits NOT fed from the same board as general office loads
  (separate essential board or dedicated ways clearly segregated)
- Drawing note states fire-rated cable standard (IEC 60331-1 or IEC 60331-21)
- Smoke extract diversity factor = 1.00 (no diversity ever on life safety)

**Fail conditions:**
- Any life safety circuit has `fire_rated: false`
- Fire alarm circuit specifies standard XLPE cable
- Smoke extract uses FP200 instead of FP400 (FP200 not rated for 120min)
- Life safety circuits share a board with general office loads without segregation note
- `diversity_factor` < 1.00 applied to any life safety circuit
- `life_safety_circuits` array absent from JSON output

---

## Eval 08 — SPD assessment and neutral oversizing

**Input:**
```
Building: new-build office, 4-storey, England
Supply: TN-C-S, 3-phase, 400V, Ze = 0.30Ω
Overhead supply from DNO (rural location, overhead lines)
Lightning protection system (LPS): present on roof
Non-linear loads:
  - IT equipment: 30kVA (servers, workstations)
  - VFDs (HVAC): 20kVA
  - UPS (server room): 15kVA
  - General lighting and power: 35kVA (linear)
Total: 100kVA
New-build: yes (England) — Part L sub-metering required
```

**Expected behaviour — SPD assessment:**

Overhead supply + LPS present = Type 1 SPD mandatory at origin.

```
[ASSUMPTION: SPD risk assessment not completed by lightning specialist.
Type 1 SPD specified at MSB (LPS present, overhead supply — both trigger Type 1).
Type 2 SPD specified at each SDB. Confirm Type 1/Type 2 coordination
(≥10m cable separation or coordination inductor) with SPD manufacturer.]
```

**Expected behaviour — neutral oversizing:**

Non-linear loading = (30 + 20 + 15) / 100 = 65% of total load.
65% >> 15% threshold → neutral must be oversized.

**Pass criteria — SPD:**
- `spd_assessment.spd_required` = true
- `spd_assessment.lps_on_building` = true
- `spd_assessment.overhead_supply` = true
- `spd_assessment.spd_type_at_origin` = "T1"
- MSB board has `spd_type: "T1"` and each SDB has `spd_type: "T2"`
- Output includes SPD [ASSUMPTION] flag noting risk assessment not completed
- Drawing note references BS EN 61643-11 and Regulation 443.4

**Pass criteria — neutral oversizing:**
- Skill calculates non-linear loading % = 65% (or 60–70% accepted range)
- Skill flags neutral oversizing requirement:
  `[ASSUMPTION: Non-linear loading ~65% of total. Neutral conductor upsized
  to 150% of phase conductor to accommodate triplen harmonic current.]`
- `connections[].neutral_size_mm2` ≥ 1.5 × `conductor_size_mm2` on sub-main
  cables serving IT/VFD loads
- `calculation_summary.neutral_oversized` = true
- `calculation_summary.harmonic_loading_pct` = 60–70

**Pass criteria — Part L sub-metering:**
- `metering_schedule[]` includes at least: MSB landlord meter, IT/server room
  meter (>50kWh/day), HVAC plant meter (>50kWh/day)
- Each meter entry has `part_l_required: true` where applicable

**Fail conditions:**
- LPS present but only Type 2 SPD specified (Type 1 required when LPS fitted)
- Neutral not oversized despite 65% non-linear loading
- `neutral_size_mm2` = `conductor_size_mm2` (no oversizing applied)
- No Part L sub-metering entries in `metering_schedule[]` for new-build
- `spd_assessment` object absent from JSON

---

## Running evals manually

To run these evals against the skill, paste each input into a DraftsMan
chat session with only the sld skill active, then check each output against
the pass/fail criteria above.

For automated testing, compare JSON output fields against expected values
using the test harness in `tests/`.

## Eval pass rate requirement

Before shipping a new skill version: all 8 evals must pass. Evals 01, 03,
and 06 are mandatory for any release (happy path, Fundamental Rule, and Zs
disconnection check). Evals 02, 04, 05, 07, and 08 must pass before marking
the version as production-ready.
