# Utilisation Factors and Maintenance Factors — Reference Tables

Reference data for the lighting-layout skill. These are indicative values
only. Always use manufacturer's photometric data where available.

---

## Utilisation Factors (UF) — Indicative Values

UF depends on Room Index, room reflectances, and luminaire photometric distribution.
Values below are indicative for standard reflectances (ceiling 70%, walls 50%, floor 20%).

**Critical note:** These are approximations for preliminary design only.
For tender-stage drawings, obtain the actual flux fraction table from the
luminaire manufacturer's IES/LDT photometric file.

### LED Recessed Panel (600×600, diffuse opal or microprismatic)

| Room Index | UF (indicative) |
|---|---|
| 0.75 | 0.47 |
| 1.00 | 0.54 |
| 1.25 | 0.59 |
| 1.50 | 0.63 |
| 2.00 | 0.68 |
| 2.50 | 0.72 |
| 3.00 | 0.75 |
| 4.00 | 0.78 |
| 5.00 | 0.80 |

### LED Recessed Downlight (wide beam, 90°+ cut-off)

| Room Index | UF (indicative) |
|---|---|
| 0.75 | 0.40 |
| 1.00 | 0.48 |
| 1.25 | 0.54 |
| 1.50 | 0.58 |
| 2.00 | 0.63 |
| 2.50 | 0.67 |
| 3.00 | 0.70 |
| 4.00 | 0.73 |
| 5.00 | 0.75 |

### LED Linear (recessed, 1200mm, diffuse)

| Room Index | UF (indicative) |
|---|---|
| 0.75 | 0.44 |
| 1.00 | 0.52 |
| 1.25 | 0.57 |
| 1.50 | 0.61 |
| 2.00 | 0.66 |
| 2.50 | 0.70 |
| 3.00 | 0.73 |
| 4.00 | 0.76 |
| 5.00 | 0.78 |

### LED Highbay (symmetric, 60° beam)

| Room Index | UF (indicative) |
|---|---|
| 0.75 | 0.50 |
| 1.00 | 0.57 |
| 1.25 | 0.62 |
| 1.50 | 0.66 |
| 2.00 | 0.70 |
| 2.50 | 0.73 |
| 3.00 | 0.76 |
| 4.00 | 0.79 |
| 5.00 | 0.81 |

### Interpolation

For RI values between table entries, interpolate linearly:
```
UF = UF_lower + (RI − RI_lower) / (RI_upper − RI_lower) × (UF_upper − UF_lower)
```

---

## Maintenance Factor (MF) Components

**MF = LLMF × LSF × LMF × RSMF**

### LLMF — Lamp Lumen Maintenance Factor

Fraction of initial luminaire lumens at the end of the maintenance period.

| Technology | Maintenance period | LLMF |
|---|---|---|
| LED module, L70 rated | 25,000h | 0.85 |
| LED module, L80 rated | 25,000h | 0.90 |
| LED module, L80 rated | 50,000h | 0.80 |
| LED module, L90 rated | 50,000h | 0.90 |
| LED module, L70 rated | 50,000h | 0.70 |

Use the manufacturer's stated L-value and rated life to select LLMF.
Default for design: **LLMF = 0.90** (L80 rated, 3-year cycle typical for offices).

### LSF — Lamp Survival Factor

Probability that a lamp is still working at end of maintenance period.

| Technology | LSF |
|---|---|
| LED module (no moving parts) | 1.00 |
| LED driver (higher failure rate) | 0.98 |

Default: **LSF = 1.00** for LED systems.

### LMF — Luminaire Maintenance Factor

Reduction in luminaire light output due to dirt accumulation on optical components.

| Environment type | Cleaning interval | LMF |
|---|---|---|
| Very clean (cleanroom, lab) | Annual | 0.97 |
| Clean (sealed office) | Annual | 0.95 |
| Normal (open plan office) | Annual | 0.90 |
| Normal (open plan office) | 6-monthly | 0.93 |
| Dirty (workshop, canteen) | Annual | 0.80 |
| Very dirty (manufacturing) | 6-monthly | 0.75 |
| Industrial (dusty) | Quarterly | 0.72 |

IP rating affects LMF: IP44+ and IP65+ luminaires have better LMF than open fittings.

### RSMF — Room Surface Maintenance Factor

Reduction due to dirt accumulation on room surfaces (walls, ceiling, floor).

| Environment type | Cleaning interval | RSMF |
|---|---|---|
| Very clean | Annual | 0.98 |
| Clean | Annual | 0.96 |
| Normal office | Annual | 0.94 |
| Normal | 6-monthly | 0.96 |
| Dirty | Annual | 0.85 |
| Very dirty | Annual | 0.80 |

### Combined MF — Typical values

| Scenario | MF |
|---|---|
| Clean office, LED L80, annual clean | 0.95 × 1.00 × 0.92 × 0.96 = **0.84** |
| Normal office, LED L80, annual clean | 0.90 × 1.00 × 0.90 × 0.94 = **0.76** |
| Normal office, LED (no L-value), annual | — | Use **0.80** as default |
| Industrial, LED, 6-monthly clean | 0.80 × 1.00 × 0.75 × 0.85 = **0.51** |
| Warehouse, LED, annual clean | 0.85 × 1.00 × 0.80 × 0.88 = **0.60** |

**Design default for normal office with LED luminaires: MF = 0.80**
Always flag as [ASSUMPTION: ...] and state components assumed.

---

## UF Adjustment for Non-Standard Reflectances

When room reflectances differ from standard (70/50/20), adjust UF:

| Ceiling | Walls | Floor | Adjustment to UF |
|---|---|---|---|
| 70% | 70% | 20% | +0.03 to +0.05 |
| 70% | 50% | 20% | 0 (baseline) |
| 70% | 30% | 20% | −0.03 to −0.05 |
| 50% | 50% | 20% | −0.03 to −0.06 |
| 30% | 30% | 20% | −0.08 to −0.12 |

Dark or highly absorptive finishes (dark walls, dark ceiling tiles) significantly
reduce UF. Always flag as [ASSUMPTION: ...] if reflectances are not confirmed.

---

*These values are for preliminary design only. For tender-stage and
construction-issue drawings, use manufacturer photometric data (IES or
Eulumdat format). Contact the luminaire manufacturer or use lighting
calculation software (DIALux, Relux, AGi32) for verified results.*
