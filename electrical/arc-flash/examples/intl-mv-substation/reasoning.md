# INT MV/LV Substation — Worked Example

## Scenario

International industrial 11 kV / 400 V substation with transformer-mediated cascade:
- `MV-SWB`: 11 kV main switchboard with drawout ACBs (t_clear 0.5s)
- `MV-SWB.TX-1.LV-MSB`: 400 V LV main switchboard downstream of 11kV/400V 2MVA transformer (t_clear 0.3s ACB electronic)

Both consumed from fault-level + db-layout-rollup intents.

## Voltage-class crossing: 11 kV (HCB) → 400 V (VCB)

This example demonstrates a transformer-mediated cascade where arc-flash analysis must account for two distinct voltage classes, each with its own electrode configuration and shock-approach boundaries.

### MV-SWB: HCB (Horizontal-Center-Bank)

**Why HCB?** The designation "drawout switchgear" indicates a horizontal draw-out breaker mechanism:
- Breaker carriage slides horizontally out of the switchboard
- Electrodes arranged horizontally across the breaker path
- IEEE 1584:2018 Table 4 profiles this as HCB geometry

Lee 1982 formula with:
- V_nom = 11 kV
- I_bf = 12 kA (max)
- t_clear = 0.5 s (intentional-delay ACB at service entrance)
- D = 910 mm (36 inches working distance)
- Result: IE ≈ 14 cal/cm² → **PPE Category 3**
- AFB ≈ 2200 mm

Shock-approach from **Table 130.4(C)(a) row "751V to 15 kV"** (MV-level distances are larger than LV).

### LV-MSB: VCB (Vertical-Center-Bank)

**Why VCB?** Standard LV switchgear geometry:
- Electrodes arranged vertically
- Breaker mounted vertically in cabinet
- IEEE 1584:2018 Table 4 baseline for LV panels

Lee 1982 formula with:
- V_nom = 0.4 kV
- I_bf = 35 kA (max, downstream of 2MVA TX at 400V)
- t_clear = 0.3 s (electronic ACB at LV)
- D = 455 mm (18 inches)
- Result: IE ≈ 8.5 cal/cm² → **PPE Category 3** (still Cat 3, despite lower IE, because fault current is higher at 400V)
- AFB ≈ 1300 mm

Shock-approach from **Table 130.4(C)(a) row "151V to 750V"** (standard LV row).

## Cascade tree threading

The cascade is declared as:
```
MV-SWB (parent_node_id=null)
  └─ MV-SWB.TX-1.LV-MSB (parent_node_id="MV-SWB")
```

The node naming scheme `MV-SWB.TX-1.LV-MSB` encodes the transformer as part of the path, indicating that the LV node is downstream of the same transformer (TX-1) that steps down the MV supply.

### Why both fall back to Lee 1982

IEEE 1584:2018 Annex C Table 4 coefficients for:
- **HCB 14300V class** (pending-verification, null in Phase A)
- **VCB 600V class** (pending-verification, null in Phase A)

Fallback chain for both nodes:

1. **ieee1584_2018**: SKIPPED — coefficients null
2. **ieee1584_2002**: SKIPPED — Doughty/Neal coefficients also null (legacy pending)
3. **lee_1982**: APPLIED — theoretical formula always available for 50V–15,000V

`LEE_1982_FALLBACK_USED` info-severity flag emitted for compliance tracking. Actual IE values will drop by 2–5× when coefficients are transcribed.

## Electrode-config auto-inference

- "drawout switchgear" → **HCB** pattern match (horizontal draw-out mechanism)
- "LV switchgear" → **VCB** pattern match (standard vertical cabinet)

Both auto-inferred; no engineer override needed.

## Label recommendations

Both nodes `label_recommended: true`:
- MV drawout switchgear ≥240V → IEEE 1584 best practice for INT; mandatory under NFPA 70E §130.5(H) if installed in US
- LV switchgear ≥240V → same

## What changes when IEEE 1584:2018 coefficients ship

When the Phase A standards layer coefficients are transcribed:
- `method_applied` auto-promotes from `lee_1982` → `ieee1584_2018` on next run
- **MV node**: IE will drop from 14 to ~5–7 cal/cm², possibly downgrading to Cat 2
- **LV node**: IE will drop from 8.5 to ~3–5 cal/cm², downgrading to Cat 1 or Cat 2
- AFB shrinks accordingly on both nodes
- Shock-approach boundaries remain unchanged (NFPA 70E Table 130.4(C)(a) rows are empirical, not IEEE 1584 derived)
- No skill code changes — fallback chain re-runs automatically at runtime

## tool_call_pending status

Both nodes carry `tool_call_pending: true`. The numeric values in `arc_flash` are conservative senior-engineer estimates from Lee 1982 — runtime tool will recompute when DraftsMan runtime ships.

## Why this is a good test case

Example 2 validates:
1. **Voltage-class crossing**: Two different voltage regimes (11 kV vs 400 V) in a single cascade
2. **Electrode configuration diversity**: HCB (MV drawout) vs VCB (LV standard)
3. **Shock-approach table selection**: Two different rows of Table 130.4(C)(a) applied correctly per voltage
4. **Parent-child cascade threading**: LV node correctly references MV parent via transformer path
5. **Lee 1982 fallback at both nodes**: Demonstrates graceful degradation when coefficients are null
