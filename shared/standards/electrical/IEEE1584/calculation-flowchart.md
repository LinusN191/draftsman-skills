# IEEE 1584:2018 — Calculation Flowchart

Step-by-step method walkthrough. The arc-flash skill's generator prompt (built next sprint) will reference this file.

## Inputs (collected before starting)

1. **Equipment context** → electrode_config (VCB/VCBB/HCB/VOA/HOA), nominal voltage V_nom, gap_distance G, working_distance D, enclosure dimensions if non-standard.
2. **Fault data** → bolted fault current I_bf (from fault-level intent), source X/R ratio.
3. **Protection data** → OCPD clearing time t_clear at the predicted I_arc (NOT at I_bf — see step 6).

## Step 1: Identify voltage class

```
if 208 V ≤ V_nom ≤ 600 V:    class = "600V"
elif 601 V ≤ V_nom ≤ 2700 V: class = "2700V"
elif 2701 V ≤ V_nom ≤ 15000 V: class = "14300V"
else: raise out-of-range error
```

For intermediate voltages (e.g., 1000V, 4160V), §7.4 interpolation applies.

## Step 2: Compute predicted arcing current `I_arc`

From `arc-current-formula.json`. The formula takes V_nom, I_bf, G, and electrode config as inputs.

```
I_arc = f(V_class, I_bf, G, electrode_config)
```

Typically `I_arc / I_bf` ≈ 0.5 to 0.95 (the arc resistance reduces current below the bolted fault value).

## Step 3: Arc-current variation (worst case)

From `arc-current-variation-high-low.json` (§10.2 of IEEE 1584:2018).

```
I_arc_high = 1.00 × I_arc
I_arc_low  = 0.85 × I_arc
```

Steps 4–6 are computed TWICE — once with `I_arc_high`, once with `I_arc_low`. The worst-case (higher incident energy) is the reported value.

**Why low-current can be worse**: a slower-clearing OCPD allows longer arcing time at the lower current → more total energy delivered.

## Step 4: Determine clearing time `t_clear` per scenario

Look up the OCPD's time-current characteristic at `I_arc_high` and `I_arc_low` separately. The clearing time is what each OCPD takes to interrupt at THAT current level.

This step requires the fault-level intent (which provides `t_clear_at_ifault` per node) OR engineer-declared OCPD curves.

## Step 5: Compute incident energy

From `incident-energy-formula.json`:

```
E = f(V_class, I_arc, t_arc, G, D, electrode_config)
```

Units: cal/cm² at the working distance D.

## Step 6: Apply adjustment factors

If any of the following deviate from standard, apply the appropriate adjustment factor:

| Condition | Adjustment file |
|---|---|
| Gap distance G ≠ tabulated | `adjustment-factor-non-standard-gap.json` |
| Working distance D ≠ default | `adjustment-factor-non-standard-distance.json` |
| Enclosure dimensions ≠ standard | `adjustment-factor-enclosure-size.json` |

Apply factors multiplicatively where stated; never compound when the standard says otherwise.

## Step 7: Compute arc-flash boundary

From `boundary-distance-formula.json`:

```
AFB = D × (E / 1.2) ^ (1/x)
```

Where `x` is the distance exponent from the relevant coefficient table. 1.2 cal/cm² is the 2nd-degree burn threshold.

## Step 8: Select PPE category

Use the resulting E to look up the PPE category from `NFPA70E/table-130-7-C-15-c-ppe-categories.json`:

| Range | Category |
|---|---|
| 1.2 – 4 cal/cm² | 1 |
| 4 – 8 cal/cm² | 2 |
| 8 – 25 cal/cm² | 3 |
| 25 – 40 cal/cm² | 4 |

For E > 40 cal/cm², the equipment is restricted — energized work only by specialised teams per facility risk assessment.

## Step 9: Document + label

Emit the analysis output. The future `arc-flash-labelling` skill consumes the result and generates physical-label content per NFPA 70E §130.5(H).
