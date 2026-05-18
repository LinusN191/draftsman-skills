# Reasoning — US Strip Mall NEC Earthing Schematic

> **v1.3 — db-layout intent consumption:** This example's `circuits[]` is derived from the upstream db-layout intent at `electrical/db-layout/examples/us-strip-mall-panelboard/intent-out.json`. The earthing skill adopts the circuit list verbatim and extends each circuit with EGC sizing (NEC Table 250.122, OCPD-keyed), effective ground-fault current path verification, and GFCI/AFCI assessment. Circuit IDs match the upstream 1:1 (C01-C04 with AWG cable sizing).

> **v1.1 retrofit (2026-05-17):** This example now declares `calc.zs_loop_impedance` tool deferral per WI3. The Zs values below are unchanged from v1.0.0 (LLM-computed inline); the deterministic tool will refine them when the DraftsMan runtime ships. The `zs_calc_tool_input` replay payload was added at the IR root so the tool can re-execute deterministically.

## Step 1 — Discovery
db-layout intent only. Consumed.

## Step 2 — Standards files (US jurisdiction)
- `shared/standards/electrical/NFPA70/art250-grounding-bonding.json`
- `shared/standards/electrical/NFPA70/grounding-and-bonding.json`
- `shared/standards/electrical/NFPA70/terminology.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`

BS 7671 and IEC 60364 NOT loaded — US uses NEC.

## Step 3 — Earthing system classification
NEC uses different taxonomy. This is a "grounded system" with EGC throughout — closest IEC equivalent is TN-S. The IR emits `earthing_system: { system_type: "TN-S", code_clause: "NEC 2023 Art 250.4(A)" }`.

## Step 4 — MET (NEC terminology: grounding busbar)
Main Service Panel grounding busbar. Supply bond type: `tn_s_separate_pe` (EGC separate throughout).

## Step 5 — Grounding electrode system (NEC 250.50)
NEC 250.50 requires bonding ALL existing grounding electrodes. Two electrodes declared per NEC 250.52(A) for supplemental grounding electrode system: UFER + metal water pipe. GEC = 4 AWG copper per Table 250.66 for 200A service.

## Step 6 — Main bonding jumper (NEC 250.28)
Three main bonds from main service panel: metal water service entry, gas pipe, structural steel. Per NEC 250.104 each requires connection to the grounding electrode conductor or grounded terminal.

## Step 7 — Supplementary bonding
None — no special location.

## Step 8 — EGC sizing (NEC Table 250.122 — by OCPD rating)

| Circuit | OCPD | EGC required | Method |
|---|---|---|---|
| C01 (20A) | 20A | 12 AWG | nec_table_250.122 |
| C02 (20A) | 20A | 12 AWG | nec_table_250.122 |
| C03 (30A) | 30A | 10 AWG | nec_table_250.122 |
| C04 (60A) | 60A | 10 AWG | nec_table_250.122 |

Note: NEC sizes by OCPD rating, NOT phase CSA — a key difference from BS 7671 / IEC 60364.

## Step 9 — Zs / fault current
NEC does not use "Zs" terminology — instead the ground-fault current path must be adequate (250.4(A)(5)). zs_compliance values reflect this check ("pass" given Ze=0.20Ω and short circuits).

## Step 10 — GFCI / AFCI
NEC requires GFCI on certain receptacles per 210.8 (bathrooms, kitchens, garages, outdoor, etc.). For general retail, not applicable here.

## Step 11 — Compliance
- INFO: confirm UFER (concrete-encased electrode) rebar is ≥20ft continuous and accessible at service before specifying.

## Step 12 — Rationale block emitted with NEC clause citations.
