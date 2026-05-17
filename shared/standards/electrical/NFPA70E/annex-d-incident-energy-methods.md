# NFPA 70E Annex D — Incident Energy Calculation Methods

NFPA 70E:2024 Annex D provides reference methods for incident energy calculation. For AC, it references IEEE 1584. For DC, it provides specific methods documented here.

## Where each method applies

| Method | Use case | Voltage range | Source |
|---|---|---|---|
| IEEE 1584:2018 | AC arc-flash, all voltage classes | 208V – 15 kV AC | `IEEE1584/` layer |
| Doan 2007 | DC arc-flash (most common for batteries/PV/EV DC) | 250V – 1000V DC | This folder — `annex-d-1-doan-method.json` |
| Stokes & Oppenlander 1991 | DC arc-voltage characteristic (input to Doan) | Various | This folder — `annex-d-2-stokes-oppenlander-method.json` |

## The Doan method (most-used DC method)

Doan's 2007 paper formalised the DC arc-flash incident energy calculation:

```
P_max = V_arc × I_arc           (maximum power transferred during arc)
E = P_max × t_arc × 10⁴ / (4π × D²) × adj_enclosure    (incident energy)
```

Where:
- V_arc is the arc voltage, computed via Stokes & Oppenlander
- I_arc is the predicted DC arcing current
- t_arc is the clearing time
- D is the working distance
- adj_enclosure is 1.5× for an enclosed arc, 1.0× for open air (per Doan)

## The Stokes & Oppenlander method (used for V_arc)

Their 1991 empirical fit gives DC arc voltage characteristic:

```
V_arc = (20 + 0.534 × G) × I_arc^0.12
```

Where G is the gap distance (mm) and V_arc is in volts.

Combined with Doan's incident-energy formula, this gives the complete DC arc-flash calculation.

## Workflow (next-sprint arc-flash skill)

1. Identify system type: AC or DC.
2. If AC: use IEEE 1584:2018 per IEEE1584 layer.
3. If DC: use Stokes & Oppenlander to compute V_arc, then Doan to compute incident energy.
4. Look up PPE category from `table-130-7-C-15-c-ppe-categories.json` (same threshold table for both AC and DC).
5. Apply NFPA 70E §130.5(H) label requirements.
