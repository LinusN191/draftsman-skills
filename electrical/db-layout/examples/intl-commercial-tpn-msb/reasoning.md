# Reasoning — INT Commercial TPN MSB (Form 4b)

## Step 1 — Discovery check
Engineer has declared fault currents for all 4 feeders — no need for fault-level intent or tool_call_pending. Single MSB feeding 4 sub-DBs.

## Step 2 — Standards files loaded (INT → IEC 60364 family)
- `shared/standards/electrical/IEC60364/part4-43-overcurrent.json`
- `shared/standards/electrical/IEC60364/part4-44-overvoltage.json`
- `shared/standards/electrical/IEC60364/rcd-requirements.json`
- `shared/standards/electrical/IEC60364/device-curves.json`
- `shared/standards/electrical/IEC60364/diversity-factors.json`
- `shared/standards/electrical/IEC60364/fault-current.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json`
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

(BS 7671 and NFPA 70 NOT loaded.)

## Step 3 — Board classification
- main_switchboard (commercial MSB)
- IEC 61439-2 PSC assembly; Form 4b (full compartmentalisation)
- IP30 (indoor electrical room)
- Ways: 20 total

## Step 4 — Incoming supply
400V TPN, 800A main ACB, fed from MAIN (utility transformer), Ze 0.05Ω.

## Step 5 — Busbar sizing
Sum of feeder loads: 80 + 150 + 100 + 12 = 342 kW = ~494A at 400V TPN.
Diversity 0.8 → 395A. Next standard busbar rating: 800A (selected to match incoming).
IcW: 36 kA per IEC 61439 PSC assembly default for this rating class.

## Step 6 — Way assignment
4 feeder MCCBs occupying 3-pole modules (12 ways total), 8 ways spare (exceeds minimum 4).

## Step 7 — OCPD per circuit
All MCCBs Type D curve (motor-friendly for sub-DB feeders feeding motor loads downstream).
- F01 (250A, 150mm²): Iz ≈ 380A at standard installation → 250 ≤ 380 ✓
- F02 (400A, 240mm²): Iz ≈ 504A → 400 ≤ 504 ✓
- F03 (250A, 150mm²): Iz ≈ 380A → 250 ≤ 380 ✓
- F04 (63A, 16mm²): Iz ≈ 85A → 63 ≤ 85 ✓
Icn = 36 kA exceeds declared 25 kA Ifault for all four.

## Step 8 — RCD assignment
No RCD at MSB level (sub-DBs handle their own RCD strategy per IEC 60364-4-41 411.5).
F04 (fire alarm feeder) is essential supply class — no RCD upstream.

## Step 9 — Cable selection
Cables provided in inputs (TPN 5-core LSF cables typical).

## Step 10 — DB face schematic
Symbols: `BUSBAR`, `MAIN_SWITCH` (800A ACB), `MCCB` (×4), `SPD`, `BUSBAR_RISER`.

## Step 11 — Selectivity verification
Cascade pairs:
- MAIN(800A ACB) → F01(250A MCCB) at 25 kA — manufacturer table: ACB-MCCB selective to 36 kA full discrimination ✓
- MAIN → F02(400A MCCB) at 25 kA — selective ✓
- MAIN → F03(250A MCCB) at 25 kA — selective ✓
- MAIN → F04(63A MCCB) at 22 kA — selective ✓
All emitted with `source: "engineer_declared"` (fault currents from engineer + cascade lookup against manufacturer table).

## Step 12 — Compliance flags
- INFO: F04 fire alarm feeder is essential supply class — recommend secondary supply via ATS at the FA1 sub-board
- None critical

## Step 13 — Rationale block
9-section taxonomy with IEC 60364 + IEC 61439 citations.

## Project rollup intent
Single MSB project — rollup contains MSB-01 plus 4 outgoing_circuits.
