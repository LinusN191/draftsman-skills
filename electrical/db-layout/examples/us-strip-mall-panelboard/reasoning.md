# Reasoning — US Strip-Mall NEMA Panelboard (NEC Art 408)

## Step 1 — Discovery check
Single board, no cross_drawing_context. No fault-level intent, no engineer Ifault → selectivity will defer (tool_call_pending).

## Step 2 — Standards files loaded (US → NFPA 70 family)
- `shared/standards/electrical/NFPA70/art408-panelboards.json`
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/art220-load-calculations.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json` (form-separations not strictly applicable to NEMA but loaded as cross-reference)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

(BS 7671 and IEC 60364 NOT loaded.)

## Step 3 — Board classification
- panelboard_nema (US retail fit-out)
- NEMA Type 1 enclosure (indoor general purpose)
- Per NEC Article 408 — maximum 42 overcurrent devices per panelboard section
- Ways: 24 total

## Step 4 — Incoming supply
240V single-phase split (120/240V three-wire), 200A main breaker. Fed from MAIN (utility service).
Ze 0.20Ω (POCO declared service grounding).

## Step 5 — Busbar sizing
Sum of loads: 1.5 + 1.5 + 3 + 11 = 17 kW = ~71A at 240V split-phase.
Diversity 0.8 → 57A. Standard NEMA 200A busbar.
IcW: 10 kA per typical commercial NEMA panelboard.

## Step 6 — Way assignment
4 circuits, of which 1 (C04 RTU) is 2-pole on a 60A MCCB:
- C01, C02, C03 = single-pole MCBs (W1, W2, W3)
- C04 = 2-pole MCCB (W4-W5)
Total 5 ways used, 19 ways spare.

## Step 7 — OCPD per circuit
US uses NEC ampacity tables (Table 310.16) — not BS 7671 / IEC equivalents.
- C01 (20A, 12 AWG): NEC 310.16 → 25A ampacity in conduit → 20 ≤ 25 ✓
- C02 (20A, 12 AWG): same as C01 ✓
- C03 (30A, 10 AWG): NEC 310.16 → 35A ampacity → 30 ≤ 35 ✓
- C04 (60A, 6 AWG): NEC 310.16 → 65A ampacity → 60 ≤ 65 ✓
Icn 10 kA exceeds typical service fault current.

## Step 8 — RCD assignment (NEC GFCI terminology)
None applicable for this retail layout — NEC 210.8 GFCI required only for bathrooms, kitchens, garages, outdoor, near sinks; this is back-of-house retail with no such locations.
AFCI per NEC 210.12 applies to dwelling unit branch circuits — not this retail fit-out.

## Step 9 — Cable selection
AWG cables provided in inputs. THWN-2 copper conductors in EMT conduit assumed.

## Step 10 — DB face schematic
Symbols: `BUSBAR`, `MAIN_SWITCH` (200A main breaker), `MCB` (×3), `MCCB` (×1), `EARTH_GENERAL`.

## Step 11 — Selectivity verification
No fault-level intent, no engineer Ifault → all 4 cascade pairs (MAIN → C01..C04) emit:
- `source: "tool_call_pending"`
- `tool_call_pending: true`
Top-level flags includes `TOOL-CALL-PENDING`.

## Step 12 — Compliance flags
- INFO: GFCI not required for this layout per NEC 210.8 (verify with AHJ if any receptacle is within 6 ft of a sink in tenant fit-out).
- None critical.

## Step 13 — Rationale block
9-section taxonomy with NEC 2023 citations ONLY (no BS 7671, no IEC 60364).

## Project rollup intent
Single panelboard project — rollup contains PB-1 plus 4 outgoing_circuits.
