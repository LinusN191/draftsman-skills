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

## Running evals manually

To run these evals against the skill, paste each input into a DraftsMan
chat session with only the sld skill active, then check each output against
the pass/fail criteria above.

For automated testing, compare JSON output fields against expected values
using the test harness in `tests/`.

## Eval pass rate requirement

Before shipping a new skill version: all 5 evals must pass. Evals 01 and 03
are mandatory for any release (happy path and Fundamental Rule enforcement).
Evals 02, 04, and 05 must pass before marking the version as production-ready.
