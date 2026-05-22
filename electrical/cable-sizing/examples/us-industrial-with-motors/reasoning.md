# US Industrial 480V — Cable Sizing Worked Example (1200A Service → Aluminium Feeder → 500 hp Motor + Pump + Receptacle)

**Project:** `us-industrial-eg01`
**Jurisdiction:** US (NEC 2023 / NFPA 70)
**Scenario:** US 480 V 3-phase 3-wire TN-C-S industrial facility with a 1200 A
service entrance feeding MCC-1 via a 400 A aluminium feeder. The MCC carries
three representative finals: a 500 hp NEMA Design B motor M01 (parallel
feeder + motor-starting Vd binding), a 200 hp NEMA Design B pump motor M02
(single-run motor sizing), and a 20 A 120 V receptacle branch (smallest
allowed conductor per NEC small-conductor rule).

This worked example demonstrates **four** properties of the walk-the-ladder
algorithm specific to the US jurisdiction that the UK / KE / INT examples do
not exercise jointly:

1. **AWG / kcmil ladder + Article 110.14(C) terminal-temperature cap** — all
   ampacities read from `NEC 2023 Article 310.16` 75 °C columns even though
   the insulation (THWN-2 / XHHW-2) is rated 90 °C wet/dry.
2. **`parallel_required` binding twice** — `SERVICE.1200A` (4 × 350 kcmil Cu)
   and `MCC-1.M01` (2 × 500 kcmil Cu), each parallel ≥ 1/0 AWG per
   `NEC 2023 Article 310.10(H)(1)`.
3. **Motor 125% FLC sizing per `NEC 2023 Article 430.22`** — both motors
   sized to 125% of full-load current (M01 738 A design, M02 300 A design).
4. **Motor-starting Vd modeled as Vd_running × LRA factor 6.0** per
   `NEC 2023 Article 430.6(A)(1)` + NEMA MG-1 — M01 reaches 9.0% (within the
   10% advisory limit; info-flag); M02 reaches 5.4%.

All primary engineering citations in this example lead with
`NEC 2023 Article X.Y` form (no jurisdiction-routed BS / IEC / KS primary).

---

## Project Supply + Jurisdiction

The site is fed from a utility transformer at **480 V 3-phase 3-wire TN-C-S**
(utility-grounded with separate equipment grounding) per
`NEC 2023 Article 250.20` grounded-systems requirements. The engineer declares
**PSCC = 35 kA** at the 1200 A service disconnect based on utility transformer
nameplate impedance + service-conductor impedance; downstream
`parent_node_ifault_ka` values are engineer-estimated attenuations along the
cascade pending `calc.fault_level` resolution.

`jurisdiction: "US"` pins the design to **NEC 2023 (NFPA 70)**. The operative
articles for cable sizing are:

| Article | Subject |
|---|---|
| `NEC 2023 Article 110.10` | Short-circuit current ratings + system coordination |
| `NEC 2023 Article 110.14(C)` | **Terminal temperature limitation** — Iz capped to lowest terminal column (60 °C / 75 °C / 90 °C) |
| `NEC 2023 Article 215.2(A)(1) IN 2` | Voltage drop targets (feeder 3% / combined 5%) |
| `NEC 2023 Article 220.40` | Feeder load calculation |
| `NEC 2023 Article 240.4(B)` | Next-size-up OCPD rounding rule |
| `NEC 2023 Article 240.4(D)` | Small-conductor OCPD limits (14 AWG → 15 A; 12 AWG → 20 A; 10 AWG → 30 A) |
| `NEC 2023 Article 250.122 Table 250.122` | **EGC sizing by upstream OCPD rating** |
| `NEC 2023 Article 310.10(H)(1)` | Parallel conductors minimum 1/0 AWG |
| `NEC 2023 Article 310.10(H)(2)` | Parallel impedance balance (equal length / CSA / raceway) |
| `NEC 2023 Article 310.16` | Ampacity tables for cables in raceway / cable tray |
| `NEC 2023 Article 430.6(A)(1)` | Motor FLC + LRA for circuit sizing (NEMA MG-1) |
| `NEC 2023 Article 430.22` | Motor branch-circuit conductor 125% FLC |
| `NEC 2023 Chapter 9 Table 9` | AC impedance + reactance per 1000 ft |

The runtime calc tools — `calc.cable_ampacity`, `calc.voltage_drop`,
`calc.cpc_adiabatic` — are **deferred per WI3**; engineer estimates from
NEC 2023 Article 310.16 + Chapter 9 Table 9 + Table 250.122 serve as
placeholders pending deterministic resolution. The IR carries three
`TOOL-CALL-PENDING:*` flags accordingly.

## Cascade Tree + Topology

The cascade is two-tier with a MCC-1 fan-out:

```
SERVICE.1200A                  1200A 480V 3-phase service        ( 950/1200 A, 4 × 350 kcmil Cu THWN-2 parallel,  3 m)
└── MCC-1.F01                  Feeder → MCC-1                    ( 320/ 400 A, 900 kcmil Al XHHW-2,              30 m)
    ├── MCC-1.M01              500 hp DOL motor M01              ( 590/ 700 A, 2 × 500 kcmil Cu THWN-2 parallel, 25 m)
    ├── MCC-1.M02              200 hp pump motor M02             ( 240/ 300 A, 350 kcmil Cu THWN-2,              18 m)
    └── MCC-1.F02.B01          20A 120V receptacle branch        (  16/  20 A, 12 AWG Cu THWN-2,                  22 m)
```

`parent_node_ifault_ka` attenuates root → leaf per the engineer's cable
impedance estimate: SERVICE.1200A 35 kA → MCC-1.F01 32 kA → MCC-1.M01 28 kA /
MCC-1.M02 29 kA / MCC-1.F02.B01 10 kA. These are placeholder values pending
`calc.fault_level` resolution.

Per `NEC 2023 Article 220.40` the feeder is sized for the calculated load
(continuous Ib × 1.25 + non-continuous Ib) plus motor sizing per
`NEC 2023 Article 430.22`.

## Walk-the-Ladder Approach + Binding Constraints

The sizing engine walks the **AWG / kcmil ladder**
(14 → 12 → 10 → 8 → 6 → 4 → 3 → 2 → 1 → 1/0 → 2/0 → 3/0 → 4/0 AWG → 250 → 300
→ 350 → 400 → 500 → 600 → 750 → 1000 kcmil) until the first csa satisfies
**all** binding checks simultaneously:

- `iz_vs_in` — `NEC 2023 Article 310.16` + `Article 110.14(C)` (75 °C column
  cap)
- `vd_cumulative` — `NEC 2023 Article 215.2(A)(1) Informational Note 2`
- `cpc_adiabatic` — `NEC 2023 Article 250.122 Table 250.122` (EGC sized by
  upstream OCPD)
- `parallel_required` — `NEC 2023 Article 310.10(H)(1)` + `Article 310.10(H)(2)`
- `motor_starting_vd` — `NEC 2023 Article 430.6(A)(1)` + NEMA MG-1 LRA factor

Binding constraint per node:

| Node | csa | Binding constraint | Notes |
|---|---|---|---|
| `SERVICE.1200A` | 4 × 350 kcmil Cu | `parallel_required` | 1000 kcmil single Iz_75 ≈ 545 A < 1200 A In; 4 × 350 = 1240 A |
| `MCC-1.F01` | 900 kcmil Al | `iz_vs_in` | 750 kcmil Al Iz_75 ≈ 385 A < 400 A required; 900 kcmil Al XHHW-2 Iz_75 ≈ 425 A accepted |
| `MCC-1.M01` | 2 × 500 kcmil Cu | `parallel_required` | 125% FLC = 738 A; 2 × 500 = 760 A; motor-starting Vd 9.0% (info flag) |
| `MCC-1.M02` | 350 kcmil Cu | `iz_vs_in` | 125% FLC = 300 A; single 350 kcmil Iz_75 ≈ 310 A |
| `MCC-1.F02.B01` | 12 AWG Cu | `iz_vs_in` | 14 AWG capped at 15 A per Article 240.4(D); 12 AWG Iz_75 = 25 A ≥ 20 A |

`walk_up_trail` shows two entries on each node (one rejected + one accepted).

## Cumulative Voltage Drop

`NEC 2023 Article 215.2(A)(1) Informational Note 2` sets the Vd targets:

| Portion | Target Vd | Vd at 480 V (L-L) |
|---|---|---|
| Feeder only | 3 % | 14.4 V |
| Combined feeder + branch | 5 % | 24.0 V |

These are **informational** — not mandatory — but used as standard US
industrial design targets.

Vd accumulates along the cascade root → leaf:

| Path | SERVICE.1200A | MCC-1.F01 | Leaf (segment) | Leaf (cumulative) |
|---|---|---|---|---|
| Path → M01 | 0.1 % | 0.9 % | 1.5 % | **2.5 %** |
| Path → M02 | 0.1 % | 0.9 % | 0.9 % | **1.9 %** |
| Path → B01 | 0.1 % | 0.9 % | 2.3 % | **3.3 %** |

All three paths pass with margin against the 5% combined target.

Vd_segment estimates use NEC 2023 Chapter 9 Table 9 effective impedance Z at
75 °C in steel conduit (Cu / Al; combined R + jX cos φ + X sin φ).

`calc.voltage_drop` deferred per WI3 — placeholder values pending
deterministic resolution.

## CPC Adiabatic Sizing

Per `NEC 2023 Article 250.122 Table 250.122` the **equipment grounding
conductor (EGC)** is sized by upstream OCPD rating rather than by direct
adiabatic equation. The table is itself validated against
IEEE 80 / IEEE 837 fault-clearing time analysis, so the table lookup is the
NEC-canonical equivalent of the adiabatic check.

EGC selections from `NEC 2023 Table 250.122` Cu column:

| Node | Upstream OCPD | EGC csa | Rule |
|---|---|---|---|
| `SERVICE.1200A` | 1200 A | 3/0 AWG Cu | Table 250.122 |
| `MCC-1.F01` | 400 A | 1/0 AWG Cu | Table 250.122 |
| `MCC-1.M01` | 700 A motor OCPD | 2/0 AWG Cu | Table 250.122 |
| `MCC-1.M02` | 300 A | 4 AWG Cu | Table 250.122 |
| `MCC-1.F02.B01` | 20 A | 12 AWG Cu | Table 250.122 |

Per `NEC 2023 Article 250.4(A)(5)` the EGC must be capable of safely carrying
the maximum prospective ground-fault current; Table 250.122 sizes are
validated against the fault-clearing time data for typical OCPD time-current
curves.

For motor circuits (M01 + M02) the OCPD rating used for Table 250.122 is the
**motor branch-circuit short-circuit and ground-fault protective device**
rating per `NEC 2023 Article 430 Part IV` (typically 250-300% of FLC for
inverse-time breakers per Table 430.52 — here 700 A for M01 and 300 A for
M02 after rounding to nearest standard frame).

`calc.cpc_adiabatic` deferred per WI3 — engineer-confirmed Table 250.122
lookups pending deterministic resolution.

## Motor Starting + Parallel Cables + Harmonic Derating

### Motor starting Vd

Per `NEC 2023 Article 430.6(A)(1)` + NEMA MG-1, motor branch-circuit sizing
uses motor FLC from NEC Tables 430.247-430.250 (or nameplate). Locked-rotor
current is approximated as **FLC × LRA factor**, with LRA factor = 6.0 for
NEMA Design B per NEMA MG-1.

Motor-starting Vd at the motor terminals during DOL start is modeled as:

```
Vd_starting = Vd_running × LRA_factor
```

This is the standard IEEE 141 (Red Book) §3 running-vs-starting Vd
relationship — at locked rotor the motor draws current proportional to LRA
factor, so the voltage drop across the source + cable scales by the same
factor (assuming source PSCC is large compared with motor LRA — which holds
here: PSCC 28 kA at M01 vs LRA ≈ 590 × 6 = 3540 A; ratio 8:1).

| Node | FLC | LRA | Vd_running_pct | Vd_starting_pct | Limit | Status |
|---|---|---|---|---|---|---|
| `MCC-1.M01` | 590 A | 6.0 | 1.5 % | **9.0 %** | 10 % advisory | ✓ within limit (info flag) |
| `MCC-1.M02` | 240 A | 6.0 | 0.9 % | **5.4 %** | 10 % advisory | ✓ comfortable margin |

The 10% advisory limit is from IEEE 141 (Red Book) §3 — at higher starting
Vd the motor stalls or fails to reach rated speed during run-up. M01 is
**within** the limit but close, so an info-severity flag in the compliance
summary recommends a soft-starter or reduced-voltage starting review if
source-impedance margin shrinks at construction time.

### Parallel cables — two sites

**`SERVICE.1200A`:** 1200 A In × 1.0 (already at OCPD) = 1200 A design. Per
`NEC 2023 Article 310.16` Cu 75 °C column, the largest standard single
conductor (1000 kcmil) gives Iz_75 ≈ 545 A — insufficient. Engineer walks to
**4 × 350 kcmil Cu THWN-2 parallel** per `NEC 2023 Article 310.10(H)(1)`:

1. Each parallel conductor ≥ 1/0 AWG per `Article 310.10(H)(1)`. ✓ (350 kcmil
   > 1/0)
2. Equal length (3 m each at service-entrance termination). ✓
3. Equal csa, material, insulation, raceway per `Article 310.10(H)(2)`. ✓
4. Terminated on common 1200 A switchgear busbars at both ends. ✓
5. Iz_corrected = 4 × 310 = **1240 A** ≥ 1200 A In. ✓

`binding_constraint: "parallel_required"`; `parallel_count: 4`.

**`MCC-1.M01` (500 hp motor):** 125% FLC = 590 × 1.25 = **738 A design** per
`NEC 2023 Article 430.22`. Single 1000 kcmil Iz_75 ≈ 545 A insufficient.
**2 × 500 kcmil Cu THWN-2 parallel** accepted:

1. Each parallel ≥ 1/0 AWG. ✓ (500 kcmil > 1/0)
2. Equal length 25 m, same material / insulation / raceway. ✓
3. Iz_corrected = 2 × 380 = **760 A** ≥ 738 A. ✓

`binding_constraint: "parallel_required"`; `parallel_count: 2`.

### Aluminium feeder MCC-1.F01

750 kcmil Al XHHW-2 at the 75 °C terminal column gives Iz ≈ 385 A — less
than the Ib_continuous × 1.25 = 320 × 1.25 = 400 A required per
`NEC 2023 Article 215.2(A)(1)` continuous-load 125% rule. Engineer walks up
to **900 kcmil Al XHHW-2** at Iz ≈ 425 A ≥ 400 A. The In = 400 A OCPD ratings
matches Ib_continuous × 1.25 exactly per Article 240.4(B) standard rating
selection.

Note that aluminium feeders are common in US industrial service entrances for
cost reasons; the engineer's design intent ratifies aluminium for the
service-to-MCC feeder with copper at terminations + motor branches per
NEC industrial design practice.

### Harmonic derating

Not triggered — no harmonic content declared on any branch
(`harmonic_content_pct: 0` for all five nodes). The `harmonic_ch_applied`
field is omitted from every node's `checks` block.

## Compliance + Assumptions + Tool-Call Pending

`compliant: true`. Four **info-severity** flags document binding-constraint
walk-ups (not non-compliances):

1. **SERVICE.1200A parallel_required** — 4 × 350 kcmil Cu accepted per
   Article 310.10(H)(1).
2. **MCC-1.F01 aluminium feeder Iz** — 900 kcmil Al XHHW-2 sized at 75 °C
   terminal column per Article 110.14(C).
3. **MCC-1.M01 parallel + motor-starting Vd 9.0%** — 2 × 500 kcmil Cu;
   starting Vd within 10% advisory limit per Article 430.6(A)(1); soft-start
   review recommended if source margin shrinks.
4. **MCC-1.M02 motor sizing** — 350 kcmil Cu single accepted; starting Vd
   5.4% comfortable margin.

**Assumptions captured in `compliance_summary.assumptions`** include US
supply declaration, NEC 2023 Article 110.14(C) 75 °C terminal cap, parallel
requirements per Article 310.10(H)(1), motor 125% FLC per Article 430.22,
NEMA MG-1 LRA factor 6.0 for Design B motors, Table 250.122 EGC lookups,
Article 215.2(A)(1) IN 2 Vd targets, aluminium feeder design intent, and
WI3 calc deferrals.

This pattern (engineer placeholders + deferred-calc flags) is the design
contract between the cable-sizing skill and the v1.x calc layer: the skill
ships **structured engineering reasoning** and lets the deterministic
calculators ratify the numbers.

## Cross-Skill Contract

The skill emits a **cable-sizing intent** (`intent-out.json`, validated
against `cable-sizing-intent.schema.json`) carrying 5 circuit records. Each
record carries the **superset** field-set required by every downstream
consumer:

| Consumer | Fields consumed |
|---|---|
| `cable-schedule` (tabulated deliverable) | `designation`, `phase_csa_mm2_or_awg`, `cpc_csa_mm2_or_awg`, `material`, `insulation`, `cable_type`, `length_m`, `installation_method`, `parallel_count` |
| `riser` (parent-child render) | `node_id`, `parent_node_id`, `designation`, `phase_csa_mm2_or_awg`, `cable_od_mm` |
| `cable-containment` (tray / conduit fill) | `cable_od_mm`, `weight_kg_per_m`, `parallel_count` |
| `small-power v1.1` (Zs resolution) | `r1_plus_r2_milliohm_per_m_at_operating_temp`, `reactance_milliohm_per_m`, `length_m`, `parallel_count` |

**AWG / kcmil string identifiers** used throughout per US convention: phase
and CPC csa values encoded as strings matching the schema pattern
`^([1-4]/0 AWG|[1-9][0-9]* AWG|[1-9][0-9]{2,} kcmil)$`. Per-metre impedance
values from `NEC 2023 Chapter 9 Table 9` 75 °C copper / aluminium in steel
conduit (combined R + jX).

The intent is forward-compatible: optional fields may be added in 1.x without
a major version bump. Any change to a **required** field forces an intent
version major bump (per the intent schema's documented contract).

The hierarchical `node_id` form (`MCC-1.F02.B01`) lets `riser` reconstruct
the full cascade tree from the intent alone without needing the IR. The
`parent_node_id` on every non-root circuit confirms parentage explicitly.

---

**Standards cited in this example:**

- `NEC 2023 Article 110.10` — Short-circuit current ratings + system
  coordination
- `NEC 2023 Article 110.14(C)` — Terminal temperature limitation (60 °C /
  75 °C / 90 °C ampacity column selection)
- `NEC 2023 Article 215.2(A)(1) Informational Note 2` — Voltage drop targets
  (feeder 3 % / combined 5 %)
- `NEC 2023 Article 220.40` — Feeder load calculation
- `NEC 2023 Article 240.4(B)` — Next-size-up OCPD rounding rule
- `NEC 2023 Article 240.4(D)` — Small-conductor OCPD limits
- `NEC 2023 Article 250.20` — Grounded-systems requirements
- `NEC 2023 Article 250.4(A)(5)` — EGC effective ground-fault current path
- `NEC 2023 Article 250.122 Table 250.122` — EGC sizing by upstream OCPD
  rating
- `NEC 2023 Article 310.10(H)(1)` — Parallel conductors minimum 1/0 AWG
- `NEC 2023 Article 310.10(H)(2)` — Parallel impedance balance
- `NEC 2023 Article 310.16` — Ampacity tables for cables in raceway / cable
  tray
- `NEC 2023 Article 430.6(A)(1)` — Motor FLC + LRA for circuit sizing
  (NEMA MG-1)
- `NEC 2023 Article 430.22` — Motor branch-circuit conductor 125% FLC
- `NEC 2023 Chapter 9 Table 9` — AC impedance + reactance per 1000 ft
- NEMA MG-1 — Motor design code definitions (LRA factor for Design A / B / C
  / D)
- IEEE 141 (Red Book) §3 — Running-vs-starting Vd guidance; 10% advisory
  limit
