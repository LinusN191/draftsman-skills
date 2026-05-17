# INT ISO-7010 Label Set with RESTRICTED Override — Worked Example

## Scenario

International 11kV/400V substation with mixed voltage tiers. The arc-flash intent provided 3 nodes with varying arc-flash severity. One node (MV-SWB at 33 kV) exceeds the NFPA 70E Category 4 incident-energy ceiling (>40 cal/cm²), triggering an automatic RESTRICTED format override.

## Why ISO-7010 + RESTRICTED override

The project jurisdiction is `INT`. Per `rules/jurisdiction-format-selection.yaml`, INT default → `iso_7010`. However, the MV-SWB node has IE = 47.2 cal/cm² > 40 cal/cm², which exceeds the NFPA 70E Category 4 upper bound. Per `rules/restricted-equipment-override.yaml`, this node is automatically re-classified to `restricted_format`, overriding the jurisdiction default.

## Per-node label generation

### MSB-1 (Main Switchboard 1 — 11 kV)
- IE: 18.5 cal/cm² → PPE Cat 3 → DANGER signal word
- ISO-7010 format with Safety Red (#E00034) signal-word panel
- W012 arc-flash hazard symbol (standard ISO 7010 alerting triangle)
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safetydb.europower.de/labels/MSB-1`

### DB-L1 (Distribution Board Level 1 — 400V)
- IE: 12.3 cal/cm² → PPE Cat 2 → WARNING signal word
- ISO-7010 format with Safety Yellow (#FFB81C) signal-word panel
- W012 arc-flash hazard symbol
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safetydb.europower.de/labels/DB-L1`

### MV-SWB (Medium Voltage Switchboard — 33 kV)
- IE: 47.2 cal/cm² → EXCEEDS Category 4 ceiling (>40 cal/cm²) → RESTRICTED signal word
- Restricted format (purple/black visual treatment, diagonal stripes, prohibition circle overlay)
- Header: "DO NOT OPERATE" + "ENERGIZED WORK PROHIBITED"
- ppe_category: null (not applicable — energized work is prohibited, not just restricted)
- ppe_clothing_description: "De-energise + LOTO + Ground before approach" (administrative control requirement)
- QR code: `https://safetydb.europower.de/labels/MV-SWB`

## Why RESTRICTED format is triggered

NFPA 70E Table 130.7(C)(16) defines PPE Categories 1–4 by incident energy:
- Category 1: 1.2–4 cal/cm²
- Category 2: 4–8 cal/cm²
- Category 3: 8–25 cal/cm²
- Category 4: 25–40 cal/cm²

When IE > 40 cal/cm², energized work is **prohibited** per industry best practice (NFPA 70E §130.2(f)(8)). The RESTRICTED format communicates this unambiguously: **no personnel approach unless de-energised**.

## SVG rendering + PDF/PNG deferment

Per WI3, SVG generation is inline. The RESTRICTED label uses a distinct template (`templates/restricted-label.svg.template`) with:
- Purple (#663399) signal-word banner
- Diagonal stripe background (safety convention for forbidden zones)
- Prohibition circle overlay (ISO 3864-1 prohibition symbol)
- "DO NOT OPERATE" + "ENERGIZED WORK PROHIBITED" text

PDF + PNG rendering is deferred to `calc.render_label`. Engineers can preview every SVG by extracting from output.json and opening in a browser.

## When incident energy changes

If the arc-flash intent is recalculated (e.g., due to equipment replacement or fault coordination changes):
- If IE for MV-SWB drops to ≤40 cal/cm², it will automatically revert to iso_7010 format (Cat 4, DANGER)
- If IE increases further, RESTRICTED format is retained
- No manual reconfiguration needed

## Reference SVG

See `sample-svg/MV-SWB.svg` for an extracted standalone SVG file rendering the RESTRICTED label. Open in any browser to preview the distinct purple/prohibition visual treatment.
