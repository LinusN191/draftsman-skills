# Engineering Philosophy — Arc-Flash Labelling

This skill renders printable arc-flash labels rather than running engineering analysis. The model:

## 1. Engineering data is upstream; this skill is documentation production

The `arc-flash` skill produces the engineering data (incident energy, boundary, PPE category, shock-approach). This skill's job is to render that data into compliant labels per regional safety standards. No engineering calculations happen here.

## 2. Jurisdiction-aware format, not format-blindness

US installations need ANSI Z535.4 labels; EU + INT need ISO 7010; UK needs BS 5499 with English signal-word supplementation. The skill auto-selects format from the project's `jurisdiction` input — engineers never pick the format unless they want to override.

## 3. RESTRICTED override supersedes jurisdiction

IE > 40 cal/cm² triggers a distinct purple/black RESTRICTED format regardless of regional convention. This is safety-critical: no standard PPE category applies above 40, and a normal red DANGER label might suggest "wear Cat 4 PPE and proceed" — which is wrong. RESTRICTED labels visually distinguish equipment where energized work is prohibited.

## 4. SVG inline, PDF/PNG deferred

SVG is structured text — LLMs can produce it faithfully from a Jinja-style template. Engineers can preview SVG labels in any browser without waiting for the DraftsMan runtime. PDF + PNG rendering needs a headless renderer; that's `calc.render_label` deferred per WI3.

## 5. Shock-approach bundled in every label

NFPA 70E §130.5(H) requires both thermal (arc-flash boundary) AND shock (limited + restricted approach) distances on labels. Some skills ship arc-flash labels with only thermal data; this skill bundles both because every label needs them.

## 6. Dual-unit display (metric + imperial)

Distance fields always show both `{mm} mm ({inches} in)` — UK + EU + US convention. Engineers in different regions read the units they're familiar with; no jurisdiction-specific conversion logic needed downstream.

## 7. Optional QR code, never invented

QR codes link to project-scoped URLs (`<base_url>/<node_id>`). When `qr_code_base_url` is declared, every label gets a QR code; when absent, no labels do. The skill never invents URLs.

## 8. Hard rules over soft guidance

The generator MUST never:
- Invent label content fields (when arc-flash data missing → "Not computed" placeholder)
- Set `format_applied` or `signal_word` outside controlled vocabularies
- Skip nodes with `label_recommended == true`
- Produce non-XML SVG content

The validator enforces all these mechanically.

## 9. Forward-compatible intent for facility-management

The `labels` intent is designed as a contract for facility-management / digital-twin systems. When a facility's asset register integrates this skill, it can render the labels into PDFs (via runtime), feed digital-twin systems the structured metadata, and provide on-site personnel QR-code lookups to engineering analysis.
