# Known Limitations — Arc-Flash Labelling v1.0.0

What v1.0.0 does NOT cover. Deliberate scope boundaries, not bugs.

## Out of scope (v1.0.0)

| Topic | Why not | Where it goes |
|---|---|---|
| Physical label printing | The skill produces files; printing is downstream | User's chosen label-printer + adhesive label stock |
| PDF / PNG generation | Needs headless renderer | `calc.render_label` runtime tool (WI3 deferred) |
| Custom company branding | Beyond placeholder support; needs graphic-design tooling | Future v1.1; meanwhile users post-process SVG output |
| Multi-language labels | English only at v1.0 | v1.1 — Welsh-English UK + French-English Canada + ... |
| Old NFPA 70E:2018 label format | We render to 2024 standard | If demand surfaces, add format-version override |
| Tactile / Braille labels | Specialty market | Specialist accessibility skill (not in roadmap) |
| Australian AS 1319 / Canadian CSA Z460 | Beyond initial scope | v1.x as demand surfaces |
| Bilingual signs (one label, two languages side-by-side) | Layout complexity | v1.2 |

## Inputs the skill cannot derive

- `jurisdiction` — engineer-declared per project
- `company_name` + `qualified_person` — project metadata
- `qr_code_base_url` — optional; project-scoped URL pattern
- `default_label_size_mm` — project standard (or use 100×75mm default)
- `branding_overlay_svg_path` — optional company-logo file

If `arc-flash` intent is absent: skill emits empty `labels[]` + assumption log.

## Renderings status

| Format | v1.0 status |
|---|---|
| SVG | Inline (LLM-produced from template); engineer-previewable in browser |
| PDF | Tool call pending (`calc.render_label`); runtime tool not yet shipped |
| PNG | Same — pending |
| Project label-index PDF | Pending — runtime bundles per-equipment PDFs |

When the DraftsMan runtime ships `calc.render_label`:
- No skill code changes
- Each label's `rendering.tool_call_pending_for_pdf_png` flips to `false`
- `rendered_bytes` populated per format

## Cross-cutting tech debt

None. All 14 standards-layer references in the manifest exist on disk + carry `clause_ref` per the convention (3 layers shipped this sprint).

## Forward-compatibility caveats

- The `labels` intent's optional fields (qr_code_url, label_size_mm) can be added without major version bump
- Required-field changes require major intent_version bump
- New label formats added (e.g., AS 1319) extend `label-formats.json` ontology + add new SVG template; format_applied enum gets the new value
- Renderings status changes (PDF/PNG support added) flip `tool_call_pending_for_pdf_png` flag; no schema change
