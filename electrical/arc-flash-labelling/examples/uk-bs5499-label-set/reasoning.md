# UK BS-5499 Label Set — Worked Example

## Scenario

UK 400V commercial facility consuming a simplified arc-flash intent from a hypothetical UK-based study. This example demonstrates BS-5499 format selection for GB jurisdiction, with HSG48 voluntary best-practice framing.

## Why BS-5499 format auto-selected

The project jurisdiction is `GB`. Per `rules/jurisdiction-format-selection.yaml`, GB default → `bs_5499`. No RESTRICTED override applied (max IE was 10.5 cal/cm², under the 40 cal/cm² threshold).

BS-5499 combines ISO 7010 symbols with English signal-word panels, making it the standard de facto practice in UK electrical installations, even though statutory compliance under EAWR requires only equipment labelling without arc-flash specificity.

## Per-node label generation

### MSB-1 (Main Switchboard 1)
- IE: 10.5 cal/cm² → PPE Cat 3 → DANGER signal word
- BS-5499 format with Safety Red (#E00034) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- No QR code (engineer discretion for this example)

### DB-L1 (Distribution Board Level 1)
- IE: 6.2 cal/cm² → PPE Cat 2 → WARNING signal word
- BS-5499 format with Safety Yellow (#F28900) signal-word panel
- All NFPA 70E §130.5(H) required content populated
- No QR code (engineer discretion for this example)

## HSG48 voluntary best-practice framing

The UK Health and Safety Executive's HSG48 guidance on electrical safety in construction recommends arc-flash labelling as good practice, even though it is not mandatory under the Electricity at Work Regulations 1989 (EAWR) or the Construction (Design and Management) Regulations 2015.

This example includes HSG48 framing in the label footer: "HSG48 voluntary best practice — not statutory". Engineers who prefer purely EAWR-compliant labelling (without HSG48 attribution) can omit this line in custom deployments.

## Why no QR codes on this example

UK installations often omit QR codes on printed labels to reduce complexity. The example shows `qr_code_base_url: null` in input.json, so all labels correctly render with `qr_code_url: null` and no QR placeholder in the SVG.

## SVG rendering + PDF/PNG deferment

Per WI3, SVG generation is inline. PDF + PNG rendering is deferred to the `calc.render_label` runtime tool. Engineers can preview every SVG by extracting from output.json and opening in a browser.

## When UK Standards update

BS-5499 is due for revision. When a new edition is published, this labelling skill will auto-regenerate with the new edition reference. No code changes needed.
