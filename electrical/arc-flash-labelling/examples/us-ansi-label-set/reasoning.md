# US ANSI Label Set — Worked Example

## Scenario

US 480V industrial facility consuming the arc-flash intent from `electrical/arc-flash/examples/us-pv-with-dcfc/intent-out.json`. The arc-flash intent provided 5 nodes (3 AC + 2 DC). One node (PV-INV-1.DC-STR-1) was skipped per `label_recommended: false` (high-impedance PV combiner box where energized work is rare).

## Why ANSI Z535.4 format auto-selected

The project jurisdiction is `US`. Per `rules/jurisdiction-format-selection.yaml`, US default → `ansi_z535_4`. No RESTRICTED override applied (max IE was 12 cal/cm² at SERVICE-480V, under the 40 cal/cm² threshold).

## Per-node label generation

### SERVICE-480V (Main service entrance)
- IE: 12.0 cal/cm² → PPE Cat 3 → DANGER signal word
- ANSI Z535.4 format with Safety Red (#E00034) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safety.acme-engineering.com/projects/us-ind-af-labels-eg01/SERVICE-480V`

### SERVICE-480V.PV-INV-1 (PV inverter)
- IE: 7.0 cal/cm² → PPE Cat 2 → WARNING signal word
- ANSI Z535.4 format with Safety Yellow (#F28900) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safety.acme-engineering.com/projects/us-ind-af-labels-eg01/SERVICE-480V.PV-INV-1`

### SERVICE-480V.DCFC-1 (DC fast charger AC input)
- IE: 8.0 cal/cm² → PPE Cat 3 → DANGER signal word
- ANSI Z535.4 format with Safety Red (#E00034) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safety.acme-engineering.com/projects/us-ind-af-labels-eg01/SERVICE-480V.DCFC-1`

### DCFC-1.DC-OUT (DC fast charger output)
- IE: 6.0 cal/cm² → PPE Cat 2 → WARNING signal word
- ANSI Z535.4 format with Safety Yellow (#F28900) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- QR code: `https://safety.acme-engineering.com/projects/us-ind-af-labels-eg01/DCFC-1.DC-OUT`

### PV-INV-1.DC-STR-1 (SKIPPED)
- Label not generated per `label_recommended: false`
- PV combiner boxes are typically enclosed; energized work is rare on combiner inputs
- High-impedance DC source; IE 2.0 cal/cm² is below practical arc-flash concern

## Why SVG content is inline + PDF/PNG deferred

Per WI3, the SVG generation is inline (LLM-readable + LLM-writable from the Jinja-style template at `templates/ansi-z535-4-label.svg.template`). The actual PDF + PNG rasterisation needs a headless renderer; that's `calc.render_label` deferred per WI3.

Engineers can preview every SVG by:
1. Extracting `rendering.svg_content` from output.json
2. Saving as `.svg` file
3. Opening in browser (Chrome / Safari / Firefox all support SVG)

For physical label production, the runtime will call `calc.render_label(svg_content, 'pdf', {width:100, height:75})` to get a print-ready PDF.

## Reference SVG

See `sample-svg/MSB-1.svg` for an extracted standalone SVG file rendering the SERVICE-480V label. Drag it into a browser to preview.

## When IEEE 1584:2018 coefficients are transcribed (future)

The arc-flash intent currently uses `method_applied: lee_1982` (conservative upper bound). When IEEE 1584:2018 coefficients are transcribed, arc-flash regenerates with lower IE values; this labelling skill auto-regenerates with potentially-different PPE categories (e.g., Cat 3 → Cat 2 if IE drops below 8 cal/cm²). No code changes needed.

## Provenance & provisional status

This label set carries `provenance.is_provisional: true` because the upstream arc-flash calculation used the Lee 1982 fallback method at LV (480 V). Lee 1982 is a >15 kV theoretical model that over-predicts incident energy at low voltage; the correct method at 600 V class is IEEE 1584-2018, whose coefficients are still pending transcription (Sprint A.3). Because the C2 cause-fix landed at the IR schema level, every label `label_content.header_line` is prepended with `"DRAFT — NOT FOR FIELD INSTALLATION\n"` (ANSI Z535.4 family marker — US-localised) so downstream renderers cannot silently omit the draft state. Sprint A.3 will transcribe the IEEE 1584-2018 coefficients and allow recomputation; Sprint C.3 will add a non-provisional US example so the cleared-state path is also covered by examples. Until then, this label set MUST NOT be sent for field installation.
