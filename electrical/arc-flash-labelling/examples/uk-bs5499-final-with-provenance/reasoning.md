# UK BS 5499 — Non-Provisional Label Set with Verified Provenance

## Scenario

UK commercial facility — 400 V TPN supply with a metal-clad LV switchgear cascade (MSB-1 incomer + MSB-1.DB-L1 sub-feeder). This example exists specifically to exercise the **non-provisional** branch of the arc-flash-labelling skill — the OPERATIONAL FIELD-USE counterpart to the existing `uk-bs5499-label-set` example (which exercises the provisional / DRAFT branch).

The consumed arc-flash intent is `electrical/arc-flash/examples/uk-lv-switchgear/intent-out.json` — the same upstream intent used by the existing label-set example, but treated here as **verified** post Sprint A.3 (IEEE 1584-2018 600V VCB coefficients now transcribed; upstream Lee-1982 fallback is no longer in play).

## What this example proves

The provenance disclosure path operates in BOTH states:

| State | Existing example | This example |
|-------|------------------|--------------|
| `provenance.is_provisional` | `true` | **`false`** |
| `header_line` prefix | `"DRAFT — NOT FOR FIELD USE\n"` | (no DRAFT prefix) |
| Field use approved | NO | YES |
| Upstream method | Lee 1982 fallback | IEEE 1584-2018 (verified) |

Both states populate the SAME schema-required provenance block (`method_applied`, `computed_at`, `calc_tool_version`, `is_provisional`, `provenance_note`). What changes between them is the **state of the `is_provisional` boolean** and the downstream consequence (DRAFT marker emission on the label).

## Provenance block — verified non-provisional

```json
{
  "method_applied": "ieee_1584_2018",
  "computed_at": "2026-05-25T11:00:00Z",
  "calc_tool_version": "shared/calculations/electrical/arc-flash@1.1.0",
  "is_provisional": false,
  "provenance_note": "Upstream arc-flash IE values verified using IEEE 1584-2018 600V VCB coefficients (Sprint A.3 transcription). Both nodes ... sit well below the 40 cal/cm² RESTRICTED ceiling. Provenance.is_provisional = false → DRAFT marker SUPPRESSED on label header_line. Labels approved for OPERATIONAL FIELD USE ..."
}
```

Every field is required per the C2 cause-fix schema patch (Sprint A.2). The `provenance_note` carries the human-readable narrative that explains WHY the labels are non-provisional — Sprint A.3 IEEE 1584-2018 coefficient transcription verified the upstream IE values without resort to Lee 1982 fallback.

## Header-line construction — DRAFT marker SUPPRESSED

The label generator decision logic:

```
if provenance.is_provisional is True:
    header_line = "DRAFT — NOT FOR FIELD USE\n" + signal_word + ": ARC FLASH AND SHOCK HAZARD"
else:
    header_line = signal_word + ": ARC FLASH AND SHOCK HAZARD"
```

For this example (`is_provisional = false`), the header_line is the pure signal-word form:

- `MSB-1`: `"DANGER: ARC FLASH AND SHOCK HAZARD"`
- `MSB-1.DB-L1`: `"WARNING: ARC FLASH AND SHOCK HAZARD"`

No DRAFT prefix. The label is ready to print, laminate, and affix to the equipment. INV-09 in the IR's `invariants[]` asserts this explicitly: it scans both `header_line` fields for the `DRAFT — NOT FOR FIELD USE` substring and reports its absence as evidence.

## Signal-word distribution (mirrors uk-bs5499-label-set)

- `MSB-1` — PPE Cat 3, IE 9.8 cal/cm² → **DANGER** signal word (per ANSI Z535.4 §6.2 thresholds, also adopted by BS 5499 in practice)
- `MSB-1.DB-L1` — PPE Cat 2, IE 5.2 cal/cm² → **WARNING** signal word

Both well below the 40 cal/cm² RESTRICTED ceiling. The RESTRICTED branch is exercised by the companion `electrical/arc-flash/examples/intl-hv-restricted-substation` upstream example.

## QR code emission

The input declares `qr_code_base_url = "https://buildtech.example/labels"`. Per `rules/label-content-population.yaml`, when the base URL is present, each label gets a QR encoding `<base>/<node_id>`:

- `MSB-1` → `https://buildtech.example/labels/MSB-1`
- `MSB-1.DB-L1` → `https://buildtech.example/labels/MSB-1.DB-L1`

Scanning the QR code in the field surfaces the full arc-flash study + provenance block for the operator before approach. This is the principal mechanism by which the label's compact summary stays linked to the underlying engineering work.

## SVG content — non-provisional rendering details

The inline SVG carries the same BS 5499 structure as the existing example (red DANGER bezel / orange WARNING bezel + lightning-bolt symbol + content lines). Two changes worth noting:

1. **Footer line replaced.** Where the provisional example emits `"HSG48 voluntary best practice — not statutory"` in the footer, this version emits `"Method: IEEE 1584-2018 (verified) | QR: <full-url>"` — the operator's field-side cue is the verification status + scannable link to the source study.
2. **Title element annotated.** The SVG `<title>` element carries `(verified, non-provisional)` for downstream PDF metadata. This is purely informational; it does not affect rendering.

`tool_call_pending_for_pdf_png` remains `true` on both labels — the SVG inline rendering is complete, but PDF/PNG conversion is the runtime calc-tool's job (per WI3) and is deferred.

## How this exercises INV-09 (new invariant for this example)

The provenance disclosure invariant fires explicitly on this example:

```
INV-09 PASS:
- provenance.is_provisional == false
- For every labels[].label_content.header_line:
    assert "DRAFT — NOT FOR FIELD USE" not in header_line
- All 5 provenance fields populated (method_applied / computed_at /
  calc_tool_version / is_provisional / provenance_note)
- provenance_note minLength 20 + maxLength 800 satisfied
```

(INV-09 is asserted by the IR's `invariants[]` block per the schema spec, not by the canonical validator.md INV-01-08 set; it documents the cause-fix C2 invariant the schema introduced.)

## Why this is a good test case

This example validates:

1. **Non-provisional provenance branch fires correctly** — DRAFT marker suppressed; labels approved for FIELD USE.
2. **All 5 schema-required provenance fields populated** — closes the C2 cause-fix loop end-to-end.
3. **QR-code emission path operates** — base URL → per-node URL substitution.
4. **PPE Cat ↔ signal-word consistency** (INV-04) holds at both nodes.
5. **Counterpart to existing `uk-bs5499-label-set`** — the SAME upstream cascade produces DIFFERENT label output depending on `is_provisional` state, demonstrating that the provenance disclosure mechanism is a genuine decision gate, not cosmetic metadata.

## What changes operationally between provisional and non-provisional

| Operational consequence | Provisional (DRAFT) | Non-provisional (this example) |
|--------------------------|---------------------|---------------------------------|
| Print and laminate | NO | YES |
| Affix to equipment | NO | YES |
| Use as field-side decision aid | NO (engineer-aid only) | YES |
| Re-issue required after upstream re-run? | YES (every time) | Only if method changes |
| Audit-trail signature required? | NO | YES (qualified person on label) |

The non-provisional state is the operational endpoint of the workflow. It is the state that justifies the existence of the labelling skill — provisional labels are an intermediate engineering artefact; non-provisional labels are the safety-critical deliverable.

## Citations (compact)

- BS 5499-4:2013 — Safety signs (UK baseline; format + colour spec)
- BS EN ISO 7010 — Graphical symbols / safety signs
- NFPA 70E:2024 §130.5(H) — Arc-flash label content requirements
- NFPA 70E:2024 Table 130.7(C)(15)(c) — PPE categories and thresholds
- ANSI Z535.4 §6.2 — Signal-word selection logic (incident-energy thresholds)
- IEEE 1584-2018 §10 + §11 — upstream IE / AFB derivation (referenced via provenance.calc_tool_version)
