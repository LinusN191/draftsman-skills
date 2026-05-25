# UK LV Switchgear — Worked Example

## Scenario

UK 400V TPN commercial office building. Two-node cascade:
- `MSB-1`: Main switchboard 2500A with ACB (t_clear 0.3s)
- `MSB-1.DB-L1`: DB-L1 sub-feeder 200A with MCCB (t_clear 0.2s)

Both consumed from fault-level + db-layout-rollup intents.

## Why both nodes fell back to Lee 1982

IEEE 1584:2018 Annex C Table 4 coefficients for VCB 600V class are currently pending-verification (null in Phase A). The fallback chain:

1. **ieee_1584_2018**: SKIPPED — coefficients pending-verification
2. **ieee_1584_2002**: SKIPPED — Doughty/Neal coefficients also pending-verification
3. **lee_1982**: APPLIED — theoretical formula always available; V_nom 400V within 50-15000V range

`LEE_1982_FALLBACK_USED` info-severity flag emitted. Lee 1982 gives a **conservative upper bound** — actual IE per IEEE 1584:2018 will likely be 2-5× lower when coefficients are transcribed.

## Per-node results

### MSB-1
- Lee 1982 formula: `E = 5.12 × 10⁵ × V × I_bf × t / D²`
- V = 0.4 kV, I_bf = 22.5 kA, t = 0.3 s, D = 18 inches (455 mm)
- E ≈ 9.8 cal/cm² → **PPE Category 3**
- AFB = 1650 mm (where E drops to 1.2 cal/cm²)
- Shock-approach from Table 130.4(C)(a) row 151V-750V

### MSB-1.DB-L1
- V = 0.4 kV, I_bf = 18 kA, t = 0.2 s
- E ≈ 5.2 cal/cm² → **PPE Category 2**
- AFB = 1050 mm
- Same shock-approach row (same voltage class)

## Electrode-config auto-inference

Both nodes auto-inferred to VCB:
- "metal-clad LV switchgear" → VCB pattern match
- "LV panelboard" → VCB pattern match

Engineer override not needed.

## Label recommendations

Both nodes `label_recommended: true`:
- LV switchgear ≥240V → NFPA 70E §130.5(H) — even in GB, this is best practice per HSG48
- LV panelboard ≥240V → same

Labels would carry: nominal voltage (400V), incident energy at 455mm (cal/cm² value), arc-flash boundary (mm), required PPE category, date of analysis.

## What changes when IEEE 1584:2018 coefficients ship

When the coefficient transcription micro-sprint completes:
- `method_applied` auto-promotes from `lee_1982` → `ieee_1584_2018`
- IE values drop by 2-5× (more realistic empirical values)
- PPE category may drop one level (e.g., MSB Cat 3 → Cat 2)
- AFB shrinks accordingly
- No skill code changes — fallback chain re-runs at runtime

This is the clean separation that came from doing Phase A and Phase B in separate sprints.

## tool_call_pending status

Both nodes carry `tool_call_pending: true`. The numeric values in `arc_flash` are senior-engineer estimates from the Lee 1982 formula — runtime tool will recompute when DraftsMan runtime ships.

## A.3 status — pending IEEE 1584-2018 transcription

Sprint A.3 (Path Z2-ext) on 2026-05-25 corrected a mislabel in the IEEE1584 standards layer: the original `method-2018-*-coefficients.json` files declared "IEEE 1584:2018" but their 7-coefficient log-linear shape is actually IEEE 1584-2002 Annex F (NOT the 2018 model). The misnamed files were renamed to `method-2002-annex-f-*.json` and the actual 2018 model files (`method-2018-tables-1-3-*.json`, with the correct 10-coef Iarc + 13-coef IE polynomial-in-V shape per Tables 1+3) were added alongside.

Coefficient values remain null on both tracks pending authoritative source-vetted transcription from IEEE Std 1584-2018 Annex A / Tables 1+3 (the standard is paywalled at IEEE Xplore; structural shape was confirmed against ETAP white papers, EasyPower release notes, and Bisson Ch. 5, but verbatim numerical coefficients require licensed access).

Until the 2018 coefficients are transcribed, this example continues to use the **Lee 1982 fallback** as the safe upper bound at LV. The emitted intent's top-level `calculation_meta.is_provisional` is set to `true`, and downstream labelling skill propagates the DRAFT marker on every label per the C2 cause-fix contract. Once the 2018 transcription completes, the fallback chain auto-promotes both nodes to `ieee_1584_2018` and IE values drop 2–5× to realistic empirical values.
