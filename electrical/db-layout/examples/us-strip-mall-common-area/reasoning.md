# Reasoning — US Strip-Mall CA-P Common-Area + Exterior Lighting Panel

## Site context

CA-P is the landlord-controlled common-area and exterior lighting panel for Sunset Plaza. Fed from MSP-A (existing `us-strip-mall-panelboard` example). Smaller intake (60A) than the two tenant feeders (100A each) reflecting the lighter landlord-managed load: parking lot LEDs, façade signage, corridor egress lighting, common-area receptacles, fire pump controller (life-safety), and site security.

Single-board scope. Ze ≈ 0.12Ω at CA-P after cascade from utility service through MSP-A.

## Step 1 — Discovery check

Single board, no cross_drawing_context. No fault-level intent. Engineer Ifault not declared → selectivity defers (tool_call_pending) per WI3.

## Step 2 — Standards files loaded (US → NFPA 70 family)

- `shared/standards/electrical/NFPA70/art408-panelboards.json`
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/art220-load-calculations.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json` (cross-reference)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

**NEC 695** (Fire Pumps) loaded for C05 fire pump controller — primary article governing dedicated supply, OCPD coordination, and feeder sizing requirements.

**NEC 700** (Emergency Systems) loaded for C03 corridor lighting and the GFCI-exemption rationale on life-safety circuits.

(BS 7671 and IEC 60364 NOT loaded — US jurisdiction.)

## Step 3 — Board classification

- `panelboard_nema` (US common-area panel)
- NEMA Type 1 enclosure (indoor general purpose; landlord service room)
- Per NEC Article 408 — maximum 42 overcurrent devices per panelboard section
- Ways: 20 total (smaller panel reflecting smaller intake)

## Step 4 — Incoming supply

208Y/120V 3-phase 4-wire 60 Hz from MSP-A. 60A 2-pole feeder. `phase_arrangement: TPN` (Y-connected building service).

Ze 0.12Ω at CA-P (further from utility service than tenant TSPs because of the lower-rated 60A feeder impedance contribution).

`supply_class: non_essential` at the panel level — but note that C03 corridor lighting and C05 fire pump are life-safety classified per NEC 700/695 and require special treatment.

## Step 5 — Busbar sizing — DESIGN TENSION FLAGGED

Connected load: 3.5 + 1.8 + 1.2 + 1.5 + 11.0 + 0.6 = 19.6 kW.

**Critical issue:** C05 fire pump branch alone is 11 kW (≈30A at 208V 3-phase FLA, with LRA potentially 180 A inrush). At full LRA, C05 would draw three times the 60A intake feeder rating. **This violates NEC 695.4(A)** which requires the fire pump to be supplied by an **independent source** — a dedicated direct connection to the utility service, an on-site generator, or a dedicated feeder tap **upstream of the main service disconnect**. Routing a fire pump as a branch off a common-area panelboard is not compliant.

**Engineer action required:** Re-route C05 as a dedicated feeder tap from upstream of MSP-A's main service disconnect, with its own fire pump controller per NEC 695.6 and dedicated transfer-switch arrangement per NEC 695.3. The 60A MCCB + 6 AWG Cu feeder remain correctly sized per NEC 695.7 voltage-drop limits.

After the corrective re-route, CA-P's busbar 60A is appropriate for the remaining common-area load (~7-8 kW ~ 22 A diversified at 208V 3-phase).

This board is represented as-drawn with CRITICAL compliance flags rather than silently engineering-corrected. The example value is precisely in surfacing this kind of design tension.

IcW 10 kA per typical NEMA panel rating (C05 specifies 22 kA Icu separately for fire pump motor LRA + cascade requirements per NEC 695.4(B)(2)).

## Step 6 — Way assignment

6 circuits, 7 ways used:
- C01 on 30A single-pole Type C MCB (parking lot LED, 240V line-line branch)
- C02, C03 on 20A single-pole Type C MCBs
- C04 on 20A single-pole Type C MCB with 10mA GFCI
- C05 on 60A 2-pole Type D MCCB (motor, NEC 695.5)
- C06 on 15A single-pole Type C MCB

Total 7 ways used, 13 spare for future common-area additions (additional exterior LED zones, EV charging islands, etc.).

## Step 7 — OCPD per circuit

US uses NEC ampacity tables (Table 310.16):

- C01 (30A, 10 AWG Cu): NEC 310.16 → 35A ampacity → 30 ≤ 35 ✓ — parking lot LED, ~17A at 240V line-line
- C02 (20A, 12 AWG): NEC 310.16 → 25A → 20 ≤ 25 ✓
- C03 (20A, 12 AWG): same ✓
- C04 (20A, 12 AWG): same ✓
- C05 (60A, 6 AWG): NEC 310.16 → 65A ampacity → 60 ≤ 65 ✓. Cable is 4-core (3-phase + EGC); EGC per NEC 250.122 = 6 AWG also.
- C06 (15A, 14 AWG): NEC 310.16 → 20A → 15 ≤ 20 ✓

EGC sizing per NEC 250.122 matched to OCPD ratings throughout.

Icn 10 kA on common-area MCBs. C05 fire pump MCCB rated 22 kA Icu — NEC 695.4(B)(2) requires the fire-pump OCPD to coordinate with the cascade fault current AND must not open on motor inrush.

## Step 8 — Fire pump OCPD (NEC 695.5)

C05 fire pump branch is dimensioned to permit:
- Continuous full-load current ≈ 30 A (≈ 11 kW / 208V √3 / 0.9 PF)
- LRA inrush during start ≈ 180 A (~6× FLA) for ~100 ms
- Locked-rotor coordination per NEC 695.5(C) — the OCPD must hold during the entire locked-rotor period (typically 5 seconds for a sized motor) without opening, then the controller's own thermal overload takes over

A 60A Type D MCCB satisfies this — Type D Ia ≈ 10-20× In = 600-1200 A, well above the ~180 A LRA, with a thermal element rating long enough to hold through the locked-rotor period. **Crucially**, NEC 695.5(B) prohibits any thermal trip on the dedicated feeder OCPD — only short-circuit trip allowed. This is what differentiates a fire-pump-rated MCCB from a general-purpose MCCB.

## Step 9 — GFCI assignment (NEC 210.8(B) commercial)

NEC 2023 Article 210.8(B) requires GFCI on a wide range of commercial receptacles:

- **C04 common area receptacles (janitor + outdoor maintenance):** GFCI 10mA Class A per NEC 210.8(B)(7) outdoor + 210.8(B)(8) janitor utility receptacles.
- **C01 parking lot lighting:** No GFCI required — lighting circuit, not a receptacle.
- **C02 façade + signage lighting:** No GFCI required — lighting circuit.
- **C03 corridor egress lighting:** NO GFCI per **NEC 700.6** — life-safety availability principle.
- **C05 fire pump:** NO GFCI per **NEC 695.5** + 695.6 — earth-fault trip would defeat the entire purpose of a fire pump.
- **C06 site security:** No GFCI required — equipment is fixed/hard-wired, not receptacle.

AFCI per NEC 210.12 applies to dwelling-unit branch circuits — **not** this commercial common-area.

## Step 10 — Cable selection

THWN-2 copper conductors in EMT conduit. NEC Table 310.16 at 30°C ambient.

`cable_csa_awg` (string) used per US jurisdiction.

C01 parking lot 60m run: 10 AWG at 30A — voltage drop estimate ≈ (30 × 60 × 2 × 1.0)/12000 ≈ 0.3% at 240V (10 AWG resistance ~1.0 mΩ/m round trip) — well within NEC 215.2(A)(1) 3% feeder + branch combined recommendation.

C05 fire pump 18m: 6 AWG, 4-core. Voltage drop per NEC 695.7 limit (5% combined feeder + branch + motor terminal) — verify in cable-sizing skill.

## Step 11 — DB face schematic

Symbols emitted: `BUSBAR`, `MAIN_SWITCH` (60A 2-pole main), `MCB` (×5), `MCCB` (×1 for fire pump), `GFCI` (on C04 breaker position), `EARTH_GENERAL`.

## Step 12 — Selectivity verification

No fault-level intent. Engineer Ifault not declared → all 6 cascade pairs (MSP-A → C01..C06) emit `tool_call_pending: true` per WI3.

Top-level flags include `TOOL-CALL-PENDING`.

C05 fire pump cascade pair is special — NEC 695.5(C) requires that the fire-pump OCPD shall NOT trip during a fault upstream until the motor naturally de-energizes; this is opposite-direction selectivity vs typical OCPD cascade. Coordination must be verified with the fire-pump controller manufacturer.

## Step 13 — Compliance flags

- **CRITICAL:** NEC 695.4(A) violation — fire pump must have independent source, not a panelboard branch.
- **HIGH:** 60A intake + 60A fire pump branch leaves no busbar headroom at fire pump LRA (~180A draw vs 60A bus rating).
- **INFO:** GFCI on C04 per NEC 210.8(B).

Note this example intentionally demonstrates a real design tension that an engineer would surface during design review — the value of the example is in modelling how db-layout intent + compliance flags work together to communicate non-compliance.

## Rationale block

9-section taxonomy with NEC 2023 citations ONLY (no BS 7671, no IEC 60364).

## Downstream consumer

CA-P's intent-out.json is consumed by:
- `electrical/sld/examples/us-strip-mall-msp-tenants/` (4-board cascade SLD: MSP-A → TSP-A + TSP-B + CA-P)
- (Future) `electrical/cable-sizing/` — voltage-drop verification on the 60m parking-lot LED run + NEC 695.7 fire-pump cable sizing
- (Future) `electrical/fault-level/` — cascade fault verification including the NEC 695.5(C) reverse-selectivity rule
- (Future) `electrical/lux/` — parking-lot illuminance design per IES RP-20

## See also

- `electrical/db-layout/examples/us-strip-mall-panelboard/` (upstream — MSP-A landlord service panel)
- `electrical/db-layout/examples/us-strip-mall-tsp-a/` (peer — Suite 100 apparel retail tenant sub-panel)
- `electrical/db-layout/examples/us-strip-mall-tsp-b/` (peer — Suite 200 food-service retail tenant sub-panel)
