# ANSI Z535.4 + NFPA 70E Arc-Flash Label Template

The canonical layout for arc-flash labels combining ANSI Z535.4 sign-format with NFPA 70E §130.5(H) required content.

## Layout (typical 100 × 75 mm label)

```
┌──────────────────────────────────────────────┐
│  [SIGNAL WORD PANEL]                          │  ← 15% height; Red/Orange/Yellow per severity
│  ⚡  DANGER                                    │
│      Arc Flash and Shock Hazard               │
├──────────────────────────────────────────────┤
│  Equipment:    MSB-1                          │  ← Equipment-ID panel; bold; ≥ 1.5× body height
│  Voltage:      480V AC, 3-phase               │
├──────────────────────────────────────────────┤
│  Incident Energy:        9.8 cal/cm² @ 455mm  │  ← Message panel; NFPA 70E required fields
│  Arc Flash Boundary:     1650 mm (65 in)      │
│  Limited Approach (M):   3050 mm (10 ft)      │
│  Limited Approach (F):   1070 mm (3.5 ft)     │
│  Restricted Approach:    305 mm (12 in)       │
│  PPE Category:           3                    │
│  PPE: AR suit + AR hood (ATPV ≥25 cal/cm²);   │
│  AR gloves; hard hat; safety glasses          │
├──────────────────────────────────────────────┤
│  Analysed: 2026-05-17                         │  ← Footer; small text
│  Engineer: [signature]                        │
│  [QR code: link to analysis]                  │
└──────────────────────────────────────────────┘
```

## Required NFPA 70E §130.5(H) fields

1. Nominal system voltage
2. Arc-flash boundary distance
3. Incident energy at working distance OR PPE category
4. Required PPE
5. Date of analysis
6. (Implied) Equipment identification
7. (Implied) Engineer / qualified-person attestation
8. (Recommended) Shock-approach boundaries (Limited + Restricted)

## Severity → Signal word mapping (Z535.4 §6.1)

| Incident energy range | PPE category | Signal word | Header colour |
|---|---|---|---|
| 1.2 ≤ E < 8 cal/cm² | 1-2 | WARNING | Safety Orange (PMS 152) |
| 8 ≤ E ≤ 40 cal/cm² | 3-4 | DANGER | Safety Red (PMS 199) |
| E > 40 cal/cm² | RESTRICTED | (distinct purple/black) | RESTRICTED |
| E < 1.2 cal/cm² | none | (no label per §130.5(H) exemption) | n/a |

## RESTRICTED variant

Above 40 cal/cm², the label uses distinct visual treatment:
- Purple/black banner (not red/orange/yellow)
- "ENERGIZED WORK PROHIBITED" replaces specific PPE category
- "Specialised assessment required — contact facility safety engineering"
- Other fields (IE, AFB, shock-approach) retained so reviewers see rationale
