# Reasoning — US Strip-Mall TSP-A Tenant Sub-Panel (Suite 100 apparel retail)

## Site context

TSP-A is the tenant sub-panel serving Suite 100 of Sunset Plaza, an apparel retail tenant. Upstream is MSP-A (the existing `us-strip-mall-panelboard` example at 240V split-phase 200A — note: this tenant feeder operates at the alternative 208Y/120V 3-phase building service typical for larger strip malls, which the MSP rolls up to). MSP-A has tenant feeders for Suite 100 (this TSP-A), Suite 200 (TSP-B), and a common-area panel (CA-P).

Single-board scope. Fed from MSP-A breaker = 100A 2-pole feeder at the landlord's main service. Tenant sub-feeder Ze ≈ 0.10Ω after the upstream service impedance.

## Step 1 — Discovery check

Single board, no cross_drawing_context. No fault-level intent. Engineer Ifault not declared → selectivity will defer (tool_call_pending) per WI3.

## Step 2 — Standards files loaded (US → NFPA 70 family)

- `shared/standards/electrical/NFPA70/art408-panelboards.json`
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/art220-load-calculations.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json` (cross-reference; NEMA not strictly within IEC 61439 scope)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

(BS 7671 and IEC 60364 NOT loaded — US jurisdiction.)

## Step 3 — Board classification

- `panelboard_nema` (US tenant sub-panel)
- NEMA Type 1 enclosure (indoor general purpose; back-of-house service closet)
- Per NEC Article 408 — maximum 42 overcurrent devices per panelboard section
- Ways: 30 total (commercial tenant panel; 22 ways spare for fit-out additions)

## Step 4 — Incoming supply

208Y/120V 3-phase 4-wire 60 Hz from MSP-A. 100A 2-pole feeder (tenant feeder). `phase_arrangement: TPN` (TPN per intent schema = 3-phase with neutral; building is Y-connected 208/120, branch circuits are 120V to neutral).

Ze 0.10Ω at TSP-A (cascade from utility service through MSP-A and the 100A tenant feeder).

`supply_class: non_essential` — tenant sub-feed; emergency lighting C08 is on a dedicated branch but the upstream supply is still standard utility.

## Step 5 — Busbar sizing

Connected load: 1.8 + 1.5 + 1.2 + 1.0 + 1.2 + 1.4 + 1.0 + 0.8 = 9.9 kW.
At 208V 3-phase: ~28A diversified at PF 0.95 (LED + electronic loads dominate).
Diversity 0.8 already applied per NEC 220.61 commercial retail.

100A busbar matches the upstream feeder OCPD — sized to feeder rating, not diversified load, per NEC 408.30 / 408.36.
IcW 10 kA per typical NEMA tenant sub-panel rating.

## Step 6 — Way assignment

8 circuits, all single-pole 120V branch circuits:
- C01-C06, C08 on 20A single-pole MCBs (W1-W6, W8)
- C07 on 15A single-pole MCB (W7)
Total 8 ways used, 22 ways spare for tenant fit-out additions (signage, additional receptacles, future EV charger, etc.).

## Step 7 — OCPD per circuit

US uses NEC ampacity tables (Table 310.16) — not BS 7671 / IEC equivalents.

- C01 (20A, 12 AWG): NEC 310.16 → 25A ampacity in conduit → 20 ≤ 25 ✓
- C02 (20A, 12 AWG): same as C01 ✓
- C03 (20A, 12 AWG): same ✓
- C04 (20A, 12 AWG): same ✓
- C05 (20A, 12 AWG): same ✓
- C06 (20A, 12 AWG): same ✓
- C07 (15A, 14 AWG): NEC 310.16 → 20A ampacity → 15 ≤ 20 ✓
- C08 (20A, 12 AWG): same as C01 ✓

EGC sizing per NEC 250.122: 12 AWG Cu EGC for 20A circuits; 14 AWG Cu EGC for the 15A HVAC control. (Cores = 3 reflects: 1 hot + 1 neutral + 1 EGC for single-phase branch.)

Icn 10 kA exceeds typical fault current at the tenant sub-panel after cascade from the utility service.

## Step 8 — GFCI assignment (NEC 210.8(B) commercial)

NEC 2023 expanded 210.8(B) to require GFCI on a wider range of commercial receptacles. For Suite 100 apparel retail:

- **C02 sales floor general receptacles:** GFCI 10mA Class A per NEC 210.8(B)(8) — receptacles within retail sales floor where mop / wash buckets are routinely used during cleaning.
- **C03 sales counter dedicated receptacles:** GFCI 10mA Class A per NEC 210.8(B) — counter-area receptacles in commercial occupancy.
- **C05 fitting room lighting + receptacles:** GFCI 10mA Class A per NEC 210.8(B) — fitting rooms are wet-equivalent locations (changing/garment hooks adjacent; sometimes within 6 ft of a customer washroom sink in tenant fit-out).
- **C04 POS dedicated:** EXEMPT per NEC 210.8(B) exception — dedicated outlet for electronic data-processing equipment that is not readily accessible. Verify with AHJ.
- **C01 lighting:** No GFCI required (lighting load, not a receptacle).
- **C06 stock room:** No GFCI required (back-of-house receptacles, no wet exposure).
- **C07 HVAC control:** No GFCI required (motor circuit; NEC 430 governs).
- **C08 emergency lighting:** NO GFCI per **NEC 700.6** and NFPA 101 life-safety availability principle — an earth-fault trip on an emergency lighting circuit would disable egress illumination at the moment of greatest need.

AFCI per NEC 210.12 applies to dwelling-unit branch circuits — **not** this retail fit-out.

## Step 9 — Cable selection

THWN-2 copper conductors in EMT conduit assumed. NEC Table 310.16 at 30°C ambient.

`cable_csa_awg` (string) used per US jurisdiction — schema accepts either `cable_csa_mm2` (number) OR `cable_csa_awg` (string) per circuit, never both.

## Step 10 — DB face schematic

Symbols emitted: `BUSBAR`, `MAIN_SWITCH` (100A 2-pole main lugs / main breaker), `MCB` (×8), `GFCI` (where C02/C03/C05 GFCI breakers used), `EARTH_GENERAL`.

## Step 11 — Selectivity verification

No fault-level intent. Engineer Ifault not declared → all 8 cascade pairs (MSP-A → C01..C08) emit:
- `source: "tool_call_pending"`
- `tool_call_pending: true`

Top-level flags include `TOOL-CALL-PENDING`.

When fault-level skill ships, the cascade pairing will re-verify upstream MSP-A 100A feeder OCPD against TSP-A 20A/15A branch circuit MCBs at the cascade fault level (≈10-15 kA at the tenant sub-panel after the MSP-A feeder impedance).

## Step 12 — Compliance flags

- **INFO:** GFCI scope per NEC 210.8(B) applied as engineering judgment to C02/C03/C05. AHJ to verify exact 6 ft proximity rule to any sink during tenant fit-out site survey.
- None critical.

## Step 13 — Rationale block

9-section taxonomy with NEC 2023 citations ONLY (no BS 7671, no IEC 60364).

## Downstream consumer

TSP-A's intent-out.json is consumed by:
- `electrical/sld/examples/us-strip-mall-msp-tenants/` (4-board cascade SLD: MSP-A → TSP-A + TSP-B + CA-P; generated in Phase B of the SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify 100A tenant feeder + branch circuits per NEC 310.16 + 250.122
- (Future) `electrical/fault-level/` — Zs verification + cascade fault current confirmation per NEC 110.9 and 240.86

## See also

- `electrical/db-layout/examples/us-strip-mall-panelboard/` (upstream — MSP-A landlord service panel)
- `electrical/db-layout/examples/us-strip-mall-tsp-b/` (peer — Suite 200 food-service tenant sub-panel)
- `electrical/db-layout/examples/us-strip-mall-common-area/` (peer — CA-P common-area + exterior lighting panel)
