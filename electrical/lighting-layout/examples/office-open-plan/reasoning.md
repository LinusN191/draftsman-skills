# Example: Open Plan Office — Reasoning

## Step 1 — Check inputs
Room 10×8m, ceiling 3.0m. Luminaire: 600×600 LED panel, 4500 lm design, 36W, IP20.
No initial lumens flag — design lumens used directly.
No glazed walls specified — no perimeter zone required.
New build England — Part L efficacy check required.
Efficacy = 4500 / 36 = 125 lm/W >> 65 lm/W target. PASS.

## Step 2 — Target illuminance
Room type: open plan office → Em = 500 lux, UGR ≤ 19, Ra ≥ 80.
Source: BS EN 12464-1:2021 Table 5.3.

## Step 3 — Room Index
Hm = 3.0 - 0.75 = 2.25m
RI = (10 × 8) / (2.25 × (10 + 8)) = 80 / 40.5 = 1.98 → use 2.00

## Step 4 — Utilisation Factor
UF from table for RI = 2.00, reflectances 70/50/20: UF = 0.67
[ASSUMPTION: UF = 0.67 from standard reflectance table. Confirm from photometric data.]

## Step 5 — Maintenance Factor
MF = LLMF × LSF × LMF × RSMF = 0.90 × 1.00 × 0.90 × 0.94 = 0.76 → use 0.80 standard
[ASSUMPTION: MF = 0.80 for clean office, LED luminaire. Confirm cleaning schedule with FM.]

## Step 6 — Fixture count
N = (500 × 80) / (4500 × 0.67 × 0.80)
N = 40,000 / 2,412 = 16.58 → round UP to 17

## Step 7 — Spacing check
S_max = 1.5 × 2.25 = 3.375m
Grid: try 4 columns × 5 rows = 20 luminaires
Spacing x = 10/4 = 2.5m ≤ 3.375m ✓
Spacing y = 8/5 = 1.6m ≤ 3.375m ✓

## Step 8 — Positions (snapped to 600mm grid)
Row spacing y: 800, 2400, 4000, 5600, 7200 mm
Col spacing x: 1250, 3750, 6250, 8750 mm → snap to 1200, 3600, 6000, 8400 mm

## Step 9 — Achieved illuminance
E = (20 × 4500 × 0.67 × 0.80) / 80 = 48,240 / 80 = 603 lux ✓ (≥ 500)

## Step 10 — Circuits
20 × 36W = 720W total. 720W < 1840W → 1 circuit.
Circuit L1-Z2: all 20 luminaires, 720W on DB L1.
Switch position: latch side of main door, 1200mm AFF.
