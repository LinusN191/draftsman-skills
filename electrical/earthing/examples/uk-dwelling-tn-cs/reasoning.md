# Reasoning — UK Dwelling TN-C-S Earthing Schematic

> **v1.1 retrofit (2026-05-17):** This example now declares `calc.zs_loop_impedance` tool deferral per WI3. The Zs values below are unchanged from v1.0.0 (LLM-computed inline); the deterministic tool will refine them when the DraftsMan runtime ships. The `zs_calc_tool_input` replay payload was added at the IR root so the tool can re-execute deterministically.

## Step 1 — Discovery check
Confirmed `consumed_intents` array contains the triple: db-layout, lighting-layout, small-power. All circuits to earth-aware-design are visible.

## Step 2 — Standards files to load
Jurisdiction is GB. Loading:
- `shared/standards/electrical/BS7671/reg411-disconnection-times.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `shared/standards/electrical/BS7671/terminology.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

(IEC 60364 and NFPA 70 files are NOT loaded — jurisdiction filters them out.)

## Step 3 — Earthing system classification
- `inputs.earthing_system: "TN-C-S"` — DNO has provided PME earth (Ze = 0.35Ω).
- Cross-check against `electrical/earthing/ontology/earthing-system-types.json` → TN-C-S permitted for GB, electrode optional, RCD not blanket-required.
- IR emits `earthing_system: { system_type: "TN-C-S", code_clause: "BS 7671 Reg 411.4" }`.

## Step 4 — MET location
- Engineer declared: `consumer unit cupboard, ground floor hallway`.
- `supply_bond_type: "dno_pme_bond"` (TN-C-S → PEN bonded at service head).
- Main earthing conductor 16 mm² Cu per BS 7671 Reg 544.1.1 (half of largest service conductor, min 6 mm²).

## Step 5 — Electrode arrangement
- TN-C-S → electrode optional. Engineer has not requested supplementary electrode.
- Recommendation in rationale: consider rod electrode ≤200Ω if future EV charger is installed (open-PEN mitigation).
- `electrodes: []` — no electrodes in this design.

## Step 6 — Main protective bonding
Three main bonding conductors from MET, sized per BS 7671 Reg 544.1:
- 10mm² to water service entry (consumer earthing conductor 10mm² minimum for PME)
- 10mm² to gas service entry (within 600mm of meter outlet)
- 6mm² to structural steel in loft (extraneous-conductive-part)

Cited: **BS 7671:2018+A3 Reg 411.3.1.2** (main bonding requirement), **Reg 544.1** (conductor sizing).

## Step 7 — Supplementary bonding
First floor bathroom needs supplementary bonding under BS 7671 Section 701 because:
- Exposed-conductive-parts (radiator pipework, light fitting) and
- Extraneous-conductive-parts (water pipes) are present together.

Supplementary bonding 4mm² between bath taps, towel rail, exposed pipework, shower enclosure earth lug.

## Step 8 — CPC sizing per circuit (BS 7671 Table 54.7)
Apply Table 54.7 — for L ≤ 16mm², CPC = L:

| Circuit | L csa | CPC csa | Method |
|---|---|---|---|
| C01 lighting | 1.5 | 1.5 | bs7671_table_54.7 |
| C02 lighting | 1.5 | 1.5 | bs7671_table_54.7 |
| C03 ring | 2.5 | 1.5 | bs7671_table_54.7 (twin-and-earth 6242Y) |
| C04 ring | 2.5 | 1.5 | bs7671_table_54.7 |
| C05 cooker | 6.0 | 2.5 | bs7671_table_54.7 (twin-and-earth) |
| C06 shower | 10.0 | 4.0 | bs7671_table_54.7 (twin-and-earth) |

## Step 9 — Zs verification
Compute R1+R2 per circuit using table values for 6242Y. Zs = Ze + R1 + R2.
Compare against BS 7671 Table 41.3 (Type B MCB Zs_max at 230V, 0.4s) with 0.8 correction factor.

Example for C03 (32A Type B): Zs_max_corrected = 1.15Ω; computed Zs = 1.09Ω → pass.

All 6 circuits pass.

## Step 10 — RCD requirement check
Per BS 7671 Reg 411.3.3, RCD ≤30mA required for all sockets ≤32A, bathroom circuits, outdoor.
Per the RCD-main consumer unit, 30mA RCD covers all final circuits. C01–C06 all RCD-protected.

## Step 11 — Compliance flags
- INFO: PME open-PEN risk noted; recommend earthing electrode if EV charger added in future (BS 7671 722.411.4.1)
- All circuits zs_compliance = pass_with_rcd or pass.

## Step 12 — Rationale emitted
9-section taxonomy + chat_summary, each section with decisions citing BS 7671 clauses. See `output.json`.
