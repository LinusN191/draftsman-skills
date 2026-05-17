# US PV + DCFC Unified AC/DC Cascade — Worked Example

## Scenario

US 480V AC service with dual renewable integration:
- 100 kW rooftop PV + inverter (600V DC combiner input)
- 50 kW DC fast charger for EV charging (500V DC output)

Five-node unified cascade:
- `SERVICE-480V`: 480V main service entrance (AC)
- `SERVICE-480V.PV-INV-1`: PV inverter 100 kW AC output (AC)
- `PV-INV-1.DC-STR-1`: PV combiner 600V DC input (DC, 8-string)
- `SERVICE-480V.DCFC-1`: DCFC AC input 50 kW (AC)
- `DCFC-1.DC-OUT`: DCFC 500V DC output to vehicle (DC)

Both consumed from fault-level + db-layout-rollup intents.

## Unified AC + DC cascade in a single IR

This example demonstrates how arc-flash analysis handles mixed current types in a single cascade tree. The key insight: **AC methods and DC methods are fundamentally different**, so the cascade tracks both but applies method-specific calculations per node.

## AC Nodes: SERVICE-480V, PV-INV-1, DCFC-1

All three AC nodes fall back to **Lee 1982** because IEEE 1584:2018 coefficients for VCB 600V are pending-verification:

### SERVICE-480V (480V AC, VCB)
- Lee 1982: V = 0.48 kV, I_bf = 25 kA, t = 0.3 s, D = 455 mm
- IE ≈ 12 cal/cm² → **PPE Category 3**
- AFB = 1800 mm
- Shock-approach: Table 130.4(C)(a) row 151V–750V

### PV-INV-1 (480V AC, VCB)
- Inverter output: lower fault current than service (12 kA vs 25 kA)
- Lee 1982: IE ≈ 7 cal/cm² → **PPE Category 2**
- AFB = 1100 mm
- Same shock-approach row (same voltage class)

### DCFC-1 (480V AC, VCB)
- DCFC input: medium fault current (18 kA)
- Lee 1982: IE ≈ 8 cal/cm² → **PPE Category 2** (boundary between Cat 1 and Cat 2)
- AFB = 1250 mm
- Same shock-approach row

All three carry `tool_call_pending: true` + Lee 1982 fallback flag.

## DC Nodes: PV-INV-1.DC-STR-1, DCFC-1.DC-OUT

**Why DC nodes use a different method:** IEEE 1584 is an AC-only empirical model. DC arc behavior is fundamentally different:
- DC arcs do not self-extinguish at zero-crossing
- DC fault current is limited by source impedance (no network contribution)
- Duration is dictated by DC contactor or fuse clearing time

Therefore: **dc_doan method per NFPA 70E Annex D** (Doan 2007 + Stokes & Oppenlander 1991).

### PV-INV-1.DC-STR-1 (600V DC, PV Combiner)

**Why Category 1 despite 600V?**

The PV source is extremely high-impedance (Z ≈ 1200 ohm):
- Each PV string = ~10 kW × 60% efficiency ÷ 600V = 10A nominal
- Short-circuit current capped by string impedance + junction box fuses
- Measured Ibf_max = 0.5 kA (very low for 600V)

DC Doan calculation:
- Ibf = 0.5 kA, t = 0.004 s (DC fuse clearing)
- IE ≈ 2 cal/cm² → **PPE Category 1**
- AFB = 450 mm (very small)
- Label: **Not recommended** (low IE + high impedance → optionally labeled per NFPA 70E)

### DCFC-1.DC-OUT (500V DC, DCFC Charger Output)

**Why Category 2 despite DC?**

The DCFC converter is lower-impedance (Z ≈ 100 ohm):
- DCFC rectifier + controller capable of 5 kA short-circuit current
- Contactor clearing time: 20 ms (slow for DC — designed for safe ramp-down)

DC Doan calculation:
- Ibf = 5 kA, t = 0.02 s (contactor opening + arc extinction)
- IE ≈ 6 cal/cm² → **PPE Category 2**
- AFB = 850 mm
- Label: **Recommended** (accessible at vehicle connector; NFPA 70E §130.5(H))

## Electrode Configuration: AC Only

- AC nodes: `electrode_config: "VCB"` (vertical-center-bank, standard for switchgear + inverter + DCFC input)
- DC nodes: `electrode_config: null` + `electrode_config_source: "not_applicable_dc"`

The IEEE 1584 electrode concept (VCB, HCB, etc.) does not apply to DC. The IR and intent documents mark this explicitly.

## Shock-Approach: Two Different Table Rows

| Node Type | Table | Row | Limited Movable | Limited Fixed | Restricted |
|-----------|-------|-----|-----------------|---------------|-----------|
| **AC** (SERVICE, PV-INV, DCFC) | 130.4(C)(a) | 151V–750V | 3050 mm | 1070 mm | 305 mm |
| **DC** (PV combiner, DCFC out) | 130.4(C)(b) | 301V–1 kV | null | 1070 mm | 305 mm |

DC safety boundaries do not include "limited approach movable" because DC arc hazard is different (arc sticks, doesn't release).

## Why both methods fall back on their respective chains

### AC fallback (SERVICE, PV-INV, DCFC):
1. **ieee1584_2018**: SKIPPED — VCB 600V coefficients null
2. **ieee1584_2002**: SKIPPED — same coefficients null
3. **lee_1982**: APPLIED — conservative upper bound

### DC direct application (PV combiner, DCFC out):
1. **ieee1584_2018**: SKIPPED — AC method, current_type=dc
2. **ieee1584_2002**: SKIPPED — AC method, current_type=dc
3. **dc_doan**: APPLIED — DC-specific per NFPA 70E Annex D

No fallback needed for DC because `dc_doan` is always available (empirical data, not coefficient-dependent).

## Current-Type Auto-Inference

The skill infers `current_type` from `equipment_type`:
- "metal-clad switchgear" → ac
- "inverter output breaker" → ac
- "PV combiner box" → dc
- "DCFC AC input breaker" → ac
- "DC fast charger output" → dc

This allows the cascade tree to be built once, then branched into AC and DC sub-analyses at runtime.

## Parent-Child Relationships in Mixed Cascade

```
SERVICE-480V (AC)
  ├─ SERVICE-480V.PV-INV-1 (AC)
  │  └─ PV-INV-1.DC-STR-1 (DC) ← Child of AC parent
  └─ SERVICE-480V.DCFC-1 (AC)
     └─ DCFC-1.DC-OUT (DC) ← Child of AC parent
```

Two **AC→DC transitions**:
1. Inverter AC output → DC combiner (upstream DC equipment)
2. DCFC AC input → DC output (downstream DC equipment)

The parent-child pointers remain valid across current-type boundaries. The skill does not reject DC children under AC parents; instead, it applies the appropriate analysis method per node's `current_type`.

## Label Recommendations

| Node | Label Recommended | Reason |
|------|-------------------|--------|
| SERVICE-480V | true | AC switchgear ≥240V → NFPA 70E §130.5(H) |
| PV-INV-1 | true | Inverter AC ≥240V → §130.5(H) |
| PV-STR-1 | **false** | DC ≤1.2 kV + low IE → optional |
| DCFC-1 | true | DCFC AC input ≥240V → §130.5(H) |
| DCFC-OUT | true | DC but accessible at connector → recommended |

The PV combiner (high impedance, IE 2 cal/cm²) is optionally labeled because Category 1 equipment with <4 cal/cm² is generally not labeled per NFPA 70E practice. However, the DCFC output is recommended because it is physically accessible at the vehicle connector (frequent personnel contact point).

## What changes when IEEE 1584:2018 coefficients ship

- AC nodes: `method_applied` auto-promotes `lee_1982` → `ieee1584_2018`
- AC IE values drop by 2–5×
- AC PPE categories may downgrade (e.g., SERVICE Cat 3 → Cat 2)
- DC nodes: unchanged (dc_doan is permanent, not method-dependent)
- No skill code changes required — method selection re-runs at runtime

## tool_call_pending Status

All 5 nodes carry `tool_call_pending: true`:
- AC nodes: Lee 1982 estimates from senior engineer; runtime IEEE 1584 tool will refine
- DC nodes: Doan estimates; runtime DC arc-flash tool will verify

## Why this is a good test case

Example 3 validates:
1. **Unified AC+DC cascade**: Mixed current types in a single project IR
2. **Method diversity**: Lee 1982 + dc_doan in the same cascade
3. **Current-type auto-inference**: PV combiner and DCFC output correctly inferred as DC
4. **Electrode config nullability**: DC nodes with null electrode_config + proper source notation
5. **Shock-approach table diversity**: Table 130.4(C)(a) vs (C)(b) applied correctly per current type
6. **Parent-child crossing**: AC parent → DC child transitions (inverter output, DCFC output)
7. **Impedance-driven results**: PV combiner (high Z, low IE) vs DCFC output (low Z, higher IE) both at similar voltage but vastly different categories
8. **Label logic diversity**: Optional labeling for high-impedance DC vs recommended for accessible DC
