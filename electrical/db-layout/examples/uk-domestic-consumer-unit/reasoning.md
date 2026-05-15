# Reasoning — UK Domestic Consumer Unit (TN-C-S)

## Step 1 — Discovery check
Inputs all present. No `cross_drawing_context` (no fault-level intent supplied). Single-board project — emit one IR + a rollup intent with this one board.

## Step 2 — Standards files loaded (GB)
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
- `shared/standards/electrical/BS7671/reg434-fault-current.json`
- `shared/standards/electrical/BS7671/reg443-spd.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `shared/standards/electrical/BS7671/appendix3-device-curves.json`
- `shared/standards/electrical/BS7671/diversity-factors.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json`
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

(IEC 60364 and NFPA 70 files NOT loaded — jurisdiction filters them out.)

## Step 3 — Board classification
- consumer_unit (UK domestic)
- IEC 61439-3 DBO assembly; Form 1
- IP2X (indoor dry — under-stair cupboard)
- Ways: 12 total

## Step 4 — Incoming supply
230V single-phase, 100A main switch, fed from MAIN, Ze 0.35 Ω (DNO declared PME).

## Step 5 — Busbar sizing
Sum of way loads: 0.8 + 0.7 + 5.0 + 4.0 + 7.5 + 9.0 = 27 kW = ~117A at 230V.
With diversity 0.4: 47A. Standard 100A busbar adequate.
IcW: 6 kA per typical consumer unit (BS EN 60439 / IEC 61439-3 DBO).

## Step 6 — Way assignment
6 circuits = 6 ways used (all single-pole MCBs). 6 ways spare. Meets minimum 2.

## Step 7 — OCPD per circuit
All MCBs Type B (domestic standard). Coordination check:
- C01 (6A on 1.5mm²): Iz=14A after grouping correction → 6 ≤ 14 ✓
- C03 (32A on 2.5mm² ring): special ring formula — Iz_effective ≈ 20A from each leg, 32A total ✓
- C06 (40A on 10mm²): Iz=57A → 40 ≤ 57 ✓
Icn 6 kA exceeds typical TN-C-S fault current 1-3 kA at this point.

## Step 8 — RCD assignment
All 6 circuits RCBO-protected via consumer unit's main 30mA RCD. Per BS 7671 411.3.3 + Section 701 (bathroom).

## Step 9 — Cable selection
Cables already provided in inputs. No upstream lighting/small-power intent to consume.

## Step 10 — DB face schematic
Symbols: `BUSBAR`, `MAIN_SWITCH`, `RCD_GROUP`, `MCB` (×6), `EARTH_GENERAL`.

## Step 11 — Selectivity verification
Cascade pairs to verify:
- MAIN → C01 ... C06 (each MCB downstream of the 100A main isolator)
Engineer Ifault not declared, fault-level intent not present → emit `tool_call_pending: true` for all selectivity_results entries.
Top-level flags includes `TOOL-CALL-PENDING`.

## Step 12 — Compliance flags
- INFO: Selectivity verification pending fault-level intent / engineer Ifault declaration
- None critical

## Step 13 — Rationale block
9-section taxonomy emitted with BS 7671 / IEC 61439 citations. See output.json.

## Project rollup intent (alongside per-board IR)
Single-board project — rollup contains just CU-G plus the 6 outgoing_circuits. Shape verified against earthing's expected payload.
