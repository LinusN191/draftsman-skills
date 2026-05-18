# Reasoning — UK 3-Storey Commercial Office Earthing

> **Cross-skill alignment (v1.4):** This earthing example pairs with the SLD UK `uk-commercial-office-3storey` (4-board cascade) and the fault-level UK `uk-commercial-3storey` (HV+LV cascade). All three use the same DNO declaration: TN-C-S, Ze=0.35Ω, PSCC=9.8 kA at MSB. Boards, feeder topology, and circuit IDs match the upstream db-layout intents verbatim (`uk-commercial-msb-3storey`, `uk-commercial-sdb-gf`, `uk-commercial-sdb-l1`, `uk-commercial-sdb-l2`). The `intent_type:"earthing"` payload at `intent-out.json` declares `system_type:"TN-C-S"` so the SLD cross-skill invariant INV-11 lines up.

> **Tool deferral (WI3):** `calc.zs_loop_impedance` deterministic execution is deferred. Zs values in `output.json` are LLM-estimates; `zs_calc_tool_input` captures the replay payload (feeders + 21 final circuits) so the deterministic tool can refine when the runtime ships.

---

## 1. System Identification

`inputs.earthing_system: "TN-C-S"` is the UK DNO default in central London — UK Power Networks supplies a TN-C-S (PME) service with declared Ze=0.35Ω and PSCC=9.8 kA at the MSB intake. The PEN bond is made at the supplier cut-out; within the installation N and PE are kept separate per **BS 7671:2018+A2 Reg 411.4**. Cross-check against the `earthing-system-types` ontology confirms TN-C-S is a permitted system for GB, electrode is optional, and RCD additional protection is not blanket-required (only on socket and outdoor-mobile-equipment circuits per AMD 2).

The supply Ze and PSCC are taken as binding boundary values for downstream design per **BS 7671:2018+A2 Reg 313.1** — the same posture used by the fault-level UK example, so the two skills agree at the MSB intake.

## 2. Ze + Zs Strategy

Ze = 0.35Ω at MSB-MAIN intake. The 95mm² Cu XLPE feeders to SDB-GF/L1/L2 (15/30/45m) contribute negligible R1+R2 (~7-21 mΩ loop), so Zs at each SDB intake is roughly:

| Board | Cascade Zs (Ω) | Notes |
|---|---|---|
| MSB-MAIN | 0.35 | declared Ze |
| SDB-GF | 0.357 | +7 mΩ feeder R1+R2 |
| SDB-L1 | 0.364 | +14 mΩ feeder R1+R2 |
| SDB-L2 | 0.371 | +21 mΩ feeder R1+R2 |

Zs at each final-circuit termination then = SDB intake Zs + final-circuit R1+R2. The Zs_max values applied:

| Device | Disconnection time | Table | Zs_max (Ω) at 230V |
|---|---|---|---|
| MCB-B 6A | 0.4s | 41.3 | 7.28 / 5.82 (corrected) |
| MCB-B 10A | 0.4s | 41.3 | 4.37 / 3.49 (corrected) |
| MCB-B 20A | 0.4s | 41.3 | 2.19 / 1.74 (corrected) |
| MCB-B 32A | 0.4s | 41.3 | 1.37 / 1.09 (corrected) |
| MCCB-D 100A | 5s | 41.5 | 0.488 |

Tabulated values already include the 0.8 temperature correction per Appendix 14. All 24 protective devices Zs-compliant; margin tightest on G04 / L104 (32A B-curve at long socket-ring lengths) where Zs ≈ 1.04–1.07Ω vs Zs_max 1.09Ω.

## 3. CPC Sizing

All final circuits use 6242Y twin-and-earth with manufacturer-stated reduced CPCs sized per **BS 7671:2018+A2 Table 54.7**:

| Line csa | CPC csa | Application |
|---|---|---|
| 1.5mm² | 1.0mm² | lighting (6A/10A) |
| 2.5mm² | 1.5mm² | socket rings (32A) |
| 4mm² | 2.5mm² | hand-dryer/FCU radials (20A) |

The 3 SDB feeders use 95mm² Cu XLPE 5-core SY cable with 25mm² Cu PE — Table 54.7 banded sizing for L > 35mm² uses CPC ≥ k×L formula; 25mm² satisfies for 95mm² line conductors at 70°C.

The **main earthing conductor** is **25mm² Cu**. For a 400A TN-C-S incoming service:
- Table 54.7 rule (half-of-largest-PE): 95mm² × 4 incoming busbar → service equivalent ~95mm² → half = ~50mm² unprotected, but 25mm² protected by enclosure
- PME minimum 16mm² (per supplier requirements)
- 25mm² chosen with engineering margin to handle full fault current over the 400A service rating

Cited: **BS 7671:2018+A2 Reg 544.1.1** (main earthing conductor sizing).

## 4. RCD Requirements (Amendment 2)

**BS 7671:2018+A2 Reg 411.3.3** (after Amendment 2) requires 30mA RCD additional protection on:
1. ALL socket circuits ≤32A (regardless of building type — no exemption for commercial)
2. ALL circuits supplying mobile equipment for use outdoors ≤32A

Applied to:
- 12 socket-ring circuits: G04/G05/G06 (GF), L104/L105/L106 (L1), L204/L205/L206 (L2) — all 32A B-curve
- 3 hand-dryer/FCU radials: G07, L107, L207 — 20A B-curve serving washroom socketed appliances

NOT applied to:
- 3 MCCB-D 100A feeders (distribution circuits, not final circuits — see §531.3.5)
- 3 emergency lighting circuits (G03, L103, L203) — no sockets and not socket-supplied
- 6 general/feature lighting circuits (G01/G02, L101/L102, L201/L202) — same rationale

All RCDs are **Type A 30mA** per the default policy in `inputs.rcd_type_default`. Engineer may upgrade to Type B if EV chargepoint is added in a future revision.

## 5. Bonding Strategy

**Main bonding** per **BS 7671:2018+A2 Reg 411.3.1.2** is applied to every extraneous-conductive-part entering the building:

| Bond | Target | csa | Sizing rationale |
|---|---|---|---|
| B1 | metal water service (incoming) | 10mm² Cu | PME minimum per §544.1.1 |
| B2 | metal gas service (incoming) | 10mm² Cu | PME minimum per §544.1.1 |
| B3 | structural steel — ground floor | 16mm² Cu | long-run margin above 10mm² PME minimum |
| B4 | structural steel — level 1 | 16mm² Cu | long-run margin |
| B5 | structural steel — level 2 | 16mm² Cu | long-run margin |

The structural-steel bonds are upsized to 16mm² to handle the long horizontal runs across each floor's perimeter column grid; the 10mm² PME minimum is the lower bound, not the design target for these distances.

**Supplementary bonding** per **BS 7671:2018+A2 Reg 415.2** is applied at the plant-room wash-hand basin where exposed-conductive-parts (heating pipework) coexist with extraneous-conductive-parts (water service). 4mm² Cu bonds tap pillars, exposed pipework, and metallic partition.

No supplementary bonding required at general washrooms (each floor) under the BS 7671:2018+A2 §701.415.2 exemption (all circuits 30mA RCD-protected; no exposed metal pipework expected in modern office washrooms with concealed services). Engineer flag: confirm at architect tender stage.

## 6. SPD Assessment

**Type 2 SPD required at MSB-MAIN intake** per **BS 7671:2018+A2 Reg 443.4** risk assessment:
- Building type: commercial occupancy (continuous use by >100 occupants)
- Location: urban central London, moderate lightning ground-flash density (~0.5 strikes/km²/yr)
- Lightning protection system: none (LPS not installed per `inputs.has_lightning_protection: false`)
- → Type 2 SPD baseline (not Type 1, as no LPS); no Type 3 needed at SDBs given cable lengths ≤45m and indoor commercial location

This matches the SLD UK example's `spd_assessment_verdict: "required_type_2"` — cross-skill consistency holds.

## 7. Compliance Summary

**Overall compliant.** All 24 protective devices Zs-compliant against tabulated Zs_max:
- 3 MCCB-D 100A feeders: pass (Zs 0.358-0.371Ω vs 0.488Ω limit, +24-27% margin)
- 9 lighting/emergency circuits: pass without RCD (margins +83-91%)
- 12 socket circuits: pass with mandatory 30mA RCD per AMD 2 (tightest margin G04 at +4.6%)

**Main bonding + supplementary bonding** complete per §411.3.1.2 + §415.2. **Type 2 SPD** specified at MSB intake per §443. No non-compliance flags.

**Tool-call pending:** `calc.zs_loop_impedance` deferred per WI3 — Zs values above are LLM-estimates derived from R1+R2 mΩ/m loop tables at 70°C PVC operating temperature. Deterministic refinement will run when the DraftsMan runtime ships. The `zs_calc_tool_input` replay payload at IR root captures all 21 final circuits + 3 feeders for re-execution.

## 8. Cross-Skill Invariants Verified

| Invariant | Source | Field | Value | Verified |
|---|---|---|---|---|
| INV-11 (system_type alignment) | SLD UK supply_summary | system_type | TN-C-S | ✓ matches earthing intent |
| Ze alignment | fault-level UK source | Ze_ohm | 0.35 | ✓ matches earthing intent |
| Board topology | db-layout × 4 | board_ids | MSB-MAIN, SDB-GF, SDB-L1, SDB-L2 | ✓ all 4 consumed |
| SPD verdict | SLD UK | spd_assessment_verdict | required_type_2 | ✓ matches earthing.spd_assessment |
