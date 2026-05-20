# INT 3-Storey Commercial — Cable Sizing Worked Example (TX → MSB → Riser → Floors → Finals)

**Project:** `intl-commercial-3storey-eg01`
**Jurisdiction:** INT (IEC 60364 series)
**Scenario:** Generic INT 400 V TPN+E TN-S commercial building with a 1000 kVA
transformer secondary feeding MSB-1 (1600 A incoming), one riser feeder out to
the riser DB, and three floor tap-offs (L1 / L2 / L3) each feeding a sub-DB.
Two representative final circuits sit on the L3 tap-off: `L3.C04` (long
38 m socket-outlet final exercising `vd_cumulative` binding at the 5 % limit)
and `L3.C07` (server rack IT load exercising `harmonic_derating` per Annex E
with 30 % h3 triplen content and neutral upsize per §523.6.3).

This worked example demonstrates **four** properties of the walk-the-ladder
algorithm that the UK and KE examples do not exercise jointly:

1. **Seven-node cascade** with three intermediate tiers
   (`service_entrance → feeder → sub_feeder → final_circuit`).
2. **Parallel cables required at TX-1** — `parallel_required` binding per
   IEC 60364-5-52:2009 §523.6 (single 630 mm² insufficient; 2 × 500 mm² accepted).
3. **`vd_cumulative` binding at two stacked nodes** — `RISER.L3` walks up at
   design time to preserve headroom for the deepest leaf `L3.C04`.
4. **Harmonic derating + neutral upsize** on the IT load — Ch = 0.86 per
   Annex E Table E.1; neutral upsized to full phase csa per §523.6.3 because
   h3 ≥ 15 %.

All primary engineering citations in this example lead with
`IEC 60364-X-XX:YYYY §Z` form (no jurisdiction-routed BS / NEC primary).

---

## Project Supply + Jurisdiction

The site is fed from a 1000 kVA transformer at **400 V TPN+E TN-S** per the
INT default supply assumed in `IEC 60364-4-41:2017 §411` (fault protection by
automatic disconnection of supply, ADS). The engineer declares
**PSCC = 25 kA** at the TX-1 secondary busbar based on TX nameplate impedance
combined with the utility incoming impedance; downstream `parent_node_ifault_ka`
values are engineer-estimated attenuations along the cascade pending
`calc.fault_level` resolution.

`jurisdiction: "INT"` pins the design to the **IEC 60364 series**. The
operative clauses for cable sizing are:

| Clause | Subject |
|---|---|
| `IEC 60364-4-41:2017 §411` | Fault protection by ADS — TN-S earthing |
| `IEC 60364-4-43:2017 §433.1` | Ampacity rule: `Iz ≥ In` |
| `IEC 60364-5-52:2009 Annex B` | Correction factors (ambient, grouping, soil) |
| `IEC 60364-5-52:2009 Annex E` | Harmonic derating Ch (triplen h3 content) |
| `IEC 60364-5-52:2009 Annex G` | Voltage drop limits (lighting 3 % / power 5 %) |
| `IEC 60364-5-52:2009 §523.6` | Parallel cables (equal csa / length / installation) |
| `IEC 60364-5-52:2009 §523.6.3` | Neutral conductor upsize for harmonic content |
| `IEC 60364-5-54:2011 §543` | CPC adiabatic sizing |

The runtime calc tools — `calc.cable_ampacity`, `calc.voltage_drop`,
`calc.cpc_adiabatic` — are **deferred per WI3**; engineer Iz_corrected and Vd
values are placeholder estimates pending deterministic resolution. The IR
carries three `TOOL-CALL-PENDING:*` flags accordingly.

## Cascade Tree + Topology

The cascade is three-tier with a riser fan-out at the second tier:

```
TX-1                            TX secondary 1000 kVA → MSB-1   (1450/1600 A, 2 × 500 mm² Cu XLPE parallel)
└── MSB-1.F-RISER               MSB → riser DB feeder           ( 320/ 400 A, 185 mm² Cu XLPE)
    ├── RISER.L1                Riser tap-off → L1 sub-DB       (  80/ 100 A,  35 mm² Cu XLPE)
    ├── RISER.L2                Riser tap-off → L2 sub-DB       ( 110/ 125 A,  50 mm² Cu XLPE)
    └── RISER.L3                Riser tap-off → L3 sub-DB       ( 130/ 160 A,  70 mm² Cu XLPE)
        ├── RISER.L3.C04        L3 long socket-outlet final     (  16/  20 A,   4 mm² Cu PVC, 38 m)
        └── RISER.L3.C07        L3 server rack IT load          (  24/  32 A,   6 mm² Cu XLPE, 18 m, 30 % h3)
```

`parent_node_ifault_ka` attenuates root → leaf per the engineer's cable
impedance estimate: TX-1 25 kA → MSB-1.F-RISER 22 kA → RISER.L3 14 kA →
L3.C04 8 kA / L3.C07 8.5 kA. These are placeholder values pending
`calc.fault_level` resolution. `t_clear_s = 0.4 s` for final circuits per the
INT TN-S ADS rule in `IEC 60364-4-41:2017 §411.3.2.3` Table 41.1.

Per `IEC 60364-3:2008 §314` the installation is divided into circuits to
minimise inconvenience on fault and enable selective discrimination — the
three floor sub-DBs implement that division below the riser.

## Walk-the-Ladder Approach + Binding Constraints

The sizing engine walks the standard IEC ladder
(1.0 → 1.5 → 2.5 → 4 → 6 → 10 → 16 → 25 → 35 → 50 → 70 → 95 → 120 → 150 → 185
→ 240 → 300 → 400 → 500 → 630 mm²) until the first csa satisfies **all**
binding checks simultaneously: `iz_vs_in` (`IEC 60364-4-43:2017 §433.1`),
`vd_cumulative` (`IEC 60364-5-52:2009 Annex G`), `cpc_adiabatic`
(`IEC 60364-5-54:2011 §543`), `parallel_required` (`IEC 60364-5-52:2009 §523.6`),
and `harmonic_derating` (`IEC 60364-5-52:2009 Annex E`).

Binding constraint per node:

| Node | csa (mm²) | Binding constraint | Notes |
|---|---|---|---|
| `TX-1` | 2 × 500 Cu XLPE | `parallel_required` | Single 630 mm² gives Iz ≈ 1090 A < 1600 A In; 2 × 500 parallel gives Iz ≈ 1830 A |
| `MSB-1.F-RISER` | 185 Cu XLPE | `iz_vs_in` | 430 A Iz ≥ 400 A In; Vd 0.5 % well under 5 % power limit |
| `RISER.L1` | 35 Cu XLPE | `iz_vs_in` | 140 A Iz ≥ 100 A In; cumulative Vd 1.3 % |
| `RISER.L2` | 50 Cu XLPE | `iz_vs_in` | 175 A Iz ≥ 125 A In; cumulative Vd 1.3 % |
| `RISER.L3` | 70 Cu XLPE | `vd_cumulative` | 50 mm² Iz-passes but rejected — leaves insufficient headroom for L3.C04 downstream |
| `RISER.L3.C04` | 4 Cu PVC | `vd_cumulative` | 2.5 mm² rejected at cumulative 6.6 %; 4 mm² accepted at 4.5 % (within 5 % limit) |
| `RISER.L3.C07` | 6 Cu XLPE | `harmonic_derating` | 4 mm² rejected (Ch = 0.86 gives Iz 30.1 A < 32 A In); 6 mm² accepted (Iz 41 A) |

`walk_up_trail` shows two entries on `TX-1`, `RISER.L3`, `RISER.L3.C04`, and
`RISER.L3.C07` (each shows one rejected attempt + one accepted) and one entry
on every other node.

## Cumulative Voltage Drop

`IEC 60364-5-52:2009 Annex G` sets the Vd limits:

| Load type | Vd limit | Vd at 400 V (L-L) / 230 V (L-N) |
|---|---|---|
| Lighting | 3 % | 12.0 V / 6.9 V |
| Power / other | 5 % | 20.0 V / 11.5 V |

Vd accumulates along the cascade root → leaf:

| Path | TX-1 | F-RISER | L3 | C04 (segment) | C04 (cumulative) |
|---|---|---|---|---|---|
| % at 400 V | 0.3 % | 0.5 % | 0.7 % | 3.0 % | **4.5 %** |

**`RISER.L3` walk-up (binding sub-feeder):**

- 50 mm² Cu XLPE method E: mV/A/m ≈ 0.92 (per IEC 60364-5-52:2009 Annex B
  Table B.52.5). Vd_segment = (0.92 × 130 × 8) / 1000 = 0.96 V → 0.9 % at
  400 V L-L. Cumulative = 0.3 + 0.5 + 0.9 = **1.7 %**. The L3.C04 final
  downstream needs 3.0 % segment headroom (4 mm² PVC singles at 38 m), so the
  cascade-aware budget allocator **rejects** 50 mm² to leave only 3.3 %
  remaining (would push C04 cumulative to 5.0 % exactly — no margin for
  numerical error). **Rejected.**
- 70 mm² Cu XLPE method E: mV/A/m ≈ 0.66. Vd_segment = (0.66 × 130 × 8) /
  1000 = 0.69 V → 0.7 % at 400 V L-L. Cumulative = 0.3 + 0.5 + 0.7 =
  **1.5 %**. Leaves 3.5 % headroom for C04. **Accepted.**

**`RISER.L3.C04` walk-up (binding remote final):**

- 2.5 mm² Cu PVC method B1, single-phase 230 V: mV/A/m ≈ 18 (Table B.52.5
  PVC singles). Vd_segment = (18 × 16 × 38) / 1000 = 10.9 V → **5.1 %** at
  230 V L-N. Cumulative = 1.5 + 5.1 = **6.6 %**. **Rejected.**
- 4 mm² Cu PVC method B1: mV/A/m ≈ 11. Vd_segment = (11 × 16 × 38) / 1000 =
  6.69 V → **3.0 %** at 230 V L-N. Cumulative = 1.5 + 3.0 = **4.5 %**.
  Within the 5 % power limit. **Accepted** (info flag in compliance summary).

This cascade stacking is the headline behaviour of the cable-sizing skill:
engineering judgement walks the sub-feeder up at design time to preserve
downstream headroom rather than over-sizing the final circuit alone.

## CPC Adiabatic Sizing

Per `IEC 60364-5-54:2011 §543`, the protective-conductor csa is selected to
carry the prospective earth-fault current for the OCPD operating time.

For phase csa **≤ 16 mm²** with the same insulation as the phase, Table 54.2
gives `CPC_csa = phase_csa` as the conservative default — this applies to
`RISER.L3.C04` (4 / 2.5 — reduced per Table 54.2 column for steel armour
acting as CPC; engineer verifies adiabatic) and `RISER.L3.C07` (6 / 6).

For phase csa **≥ 25 mm²** (TX-1 500, F-RISER 185, L1 35, L2 50, L3 70 mm²),
reduced CPC is verified via the **adiabatic equation S² ≥ I²t / k²**
(k = 143 for Cu/XLPE per `IEC 60364-5-54:2011 Table 54.3`; t = 0.4 s per
`t_clear_s`). For TX-1 at 25 kA prospective earth-fault: S_min =
(25000 × √0.4) / 143 ≈ 110 mm² — **240 mm² CPC** passes with margin.

CPC selections:

| Node | Phase | CPC | Rule |
|---|---|---|---|
| TX-1 | 500 | 240 | §543 adiabatic (reduced) |
| MSB-1.F-RISER | 185 | 95 | §543 adiabatic (reduced) |
| RISER.L1 | 35 | 16 | §543 adiabatic (reduced) |
| RISER.L2 | 50 | 25 | §543 adiabatic (reduced) |
| RISER.L3 | 70 | 35 | §543 adiabatic (reduced) |
| RISER.L3.C04 | 4 | 2.5 | Table 54.2 (twin-and-earth conventional + adiabatic) |
| RISER.L3.C07 | 6 | 6 | Table 54.2 (equal csa, IT-load conservative) |

All seven pass adiabatic check with placeholder estimates; `calc.cpc_adiabatic`
deferred per WI3 for deterministic verification.

## Motor Starting + Parallel Cables + Harmonic Derating

**Motor starting:** No motors declared on this cascade. `motor_starting_vd_pct`
and `motor_starting_vd_pass` are `null` on every node.

**Parallel cables at TX-1:**

The 1000 kVA TX secondary delivers 1450 A Ib (1600 A In) at 400 V. Per
`IEC 60364-5-52:2009 Annex B Table B.52.5`, single 630 mm² Cu XLPE method F
three-phase has Iz ≈ 1090 A — **insufficient**. The next ladder step (800 mm²)
is uneconomic and difficult to terminate. The engineer steps to **2 × 500 mm²
Cu XLPE parallel**, giving Iz_corrected = 2 × 915 ≈ **1830 A** ≥ 1600 A In.

Per `IEC 60364-5-52:2009 §523.6` parallel cables must satisfy:

1. Equal length (8 m each). ✓
2. Equal csa (500 mm² each). ✓
3. Same material (copper), insulation (XLPE), installation method (F). ✓
4. Terminated on common busbars at both ends (MSB-1 incoming). ✓
5. Mutual impedance neglected per §523.6 second paragraph for spacing > 2D. ✓

`binding_constraint: "parallel_required"`; `parallel_count: 2`.

**Harmonic derating on `RISER.L3.C07` (server rack IT load):**

The L3.C07 load carries `harmonic_content_pct: 30` (h3 triplen). Per
`IEC 60364-5-52:2009 Annex E Table E.1`, the 15-33 % h3 band gives a derating
factor **Ch = 0.86** (interpolated value within the band) applied to the
3-phase 4-wire ampacity.

- 4 mm² Cu XLPE method B1: Iz_table ≈ 35 A; Iz_corrected = 35 × 0.86 ≈
  **30.1 A** < 32 A In. **Rejected.**
- 6 mm² Cu XLPE method B1: Iz_table ≈ 48 A; Iz_corrected = 48 × 0.86 ≈
  **41 A** ≥ 32 A In. **Accepted.**

Per `IEC 60364-5-52:2009 §523.6.3`, when h3 content ≥ 15 % the neutral
conductor must be sized for the triplen current — which can approach
1.73 × phase current at 100 % h3 content. The engineer adopts **full phase
csa for the neutral (6 mm²)** as a conservative measure within the 15-33 %
band. The schema doesn't carry a separate `neutral_csa` field, so this choice
is documented as an `info`-severity flag on `RISER.L3.C07` in the compliance
summary.

`binding_constraint: "harmonic_derating"`; `harmonic_ch_applied: 0.86` on the
checks block.

## Compliance + Assumptions + Tool-Call Pending

`compliant: true`. Four **info-severity** flags document binding-constraint
walk-ups (not non-compliances):

1. **TX-1 parallel_required** — 2 × 500 mm² accepted per §523.6.
2. **RISER.L3 vd_cumulative walk-up** — 50 → 70 mm² to preserve C04
   headroom.
3. **RISER.L3.C04 vd_cumulative at 4.5 %** — within 5 % limit; engineer
   confirms acceptable.
4. **RISER.L3.C07 harmonic Ch = 0.86 + neutral upsized** — Annex E +
   §523.6.3.

**Assumptions captured in `compliance_summary.assumptions`:**

1. INT 400 V TPN+E TN-S supply per `IEC 60364-4-41:2017 §411` ADS;
   engineer-declared PSCC = 25 kA at TX-1 secondary.
2. Parallel cables at TX-1 sized per `IEC 60364-5-52:2009 §523.6`: 2 × 500 mm²
   Cu XLPE method F, equal length 8 m, terminated at common MSB-1 busbar.
3. Cumulative Vd budget allocated across the cascade per `IEC 60364-5-52:2009
   Annex G`; RISER.L3 walked up at design time.
4. Harmonic derating on L3.C07 per `Annex E Table E.1`: 30 % h3 → Ch = 0.86;
   neutral upsized to full phase csa per `§523.6.3`.
5. CPC sized per `IEC 60364-5-54:2011 §543`; reduced CPC on ≥ 25 mm² phase
   verified by adiabatic equation.
6. Engineer design intent: XLPE for feeders and IT load, PVC singles for the
   long socket-outlet final.
7. Parent-node Ifault attenuation along cascade is engineer-estimated;
   `calc.fault_level` deferred per WI3.
8. `calc.cable_ampacity`, `calc.voltage_drop`, `calc.cpc_adiabatic` deferred
   per WI3 — engineer estimates from IEC 60364-5-52 Annex B / G / E serve as
   placeholders.

This pattern (engineer placeholders + deferred-calc flags) is the design
contract between the cable-sizing skill and the v1.x calc layer: the skill
ships **structured engineering reasoning** and lets the deterministic
calculators ratify the numbers.

## Cross-Skill Contract

The skill emits a **cable-sizing intent** (`intent-out.json`, validated against
`cable-sizing-intent.schema.json`) carrying 7 circuit records. Each record
carries the **superset** field-set required by every downstream consumer:

| Consumer | Fields consumed |
|---|---|
| `cable-schedule` (tabulated deliverable) | `designation`, `phase_csa_mm2_or_awg`, `cpc_csa_mm2_or_awg`, `material`, `insulation`, `cable_type`, `length_m`, `installation_method`, `parallel_count` |
| `riser` (parent-child render) | `node_id`, `parent_node_id`, `designation`, `phase_csa_mm2_or_awg`, `cable_od_mm` |
| `cable-containment` (tray / conduit fill) | `cable_od_mm`, `weight_kg_per_m`, `parallel_count` |
| `small-power v1.1` (Zs resolution) | `r1_plus_r2_milliohm_per_m_at_operating_temp`, `reactance_milliohm_per_m`, `length_m`, `parallel_count` |

The intent is forward-compatible: optional fields may be added in 1.x without
a major version bump. Any change to a **required** field forces an intent
version major bump (per the intent schema's documented contract).

The hierarchical `node_id` form (`RISER.L3.C04`) lets `riser` reconstruct the
full cascade tree from the intent alone without needing the IR. The
`parent_node_id` on every non-root circuit confirms parentage explicitly.

---

**Standards cited in this example:**

- `IEC 60364-3:2008 §314` — Division of installation into circuits
- `IEC 60364-4-41:2017 §411` — Fault protection by automatic disconnection
  of supply (ADS); TN-S earthing; t_clear_s per Table 41.1
- `IEC 60364-4-43:2017 §433.1` — Coordination of conductor and protective
  device: Iz ≥ In
- `IEC 60364-5-52:2009 Annex B` — Correction factors (ambient temperature,
  grouping, soil thermal resistivity)
- `IEC 60364-5-52:2009 Annex E Table E.1` — Harmonic-content reduction factor
  Ch (triplen h3)
- `IEC 60364-5-52:2009 Annex G` — Voltage drop limits (lighting 3 % / power
  5 %)
- `IEC 60364-5-52:2009 §523.6` — Parallel cables (equal length / csa /
  material / installation; mutual impedance)
- `IEC 60364-5-52:2009 §523.6.3` — Neutral conductor upsize for high-h3
  content
- `IEC 60364-5-54:2011 §543` — Protective conductor (CPC) sizing; adiabatic
  equation S² ≥ I²t / k²; Table 54.2 (CPC ≥ phase rule) / Table 54.3 (k
  factors)
