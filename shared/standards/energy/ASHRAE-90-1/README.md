# ASHRAE 90.1 Table 9.5.2.1 — Lighting Power Density (LPD) by Space Type

Transcription of ASHRAE Standard 90.1-2019 Addendum **ba** Table 9.5.2.1 (Lighting Power Density Allowances Using the Space-by-Space Method). Addendum ba renumbered the historical Table 9.6.1 → Table 9.5.2.1 (Addendum ad) then split it into two parts (Addendum ba):

- **Table 9.5.2.1-1** — Common space types found across multiple building types
- **Table 9.5.2.1-2** — Building-specific space types found in a single building type

The historical Table 9.6.1 reference is preserved in the file name and in `cross_references.ashrae_901_table` (back-filled at X.D.1) for searchability across older project archives.

**Source:** `https://www.ashrae.org/file%20library/technical%20resources/standards%20and%20guidelines/standards%20addenda/90_1_2019_ba_20220909.pdf` (canonical publisher mirror — no third-party intermediary)
**Edition:** ANSI/ASHRAE/IES Addendum **ba** to Standard 90.1-2019 (effective 2022-09-09)
**Access date:** 2026-06-05
**Coverage:** ~120 space types (full I-P + SI versions of both tables transcribed verbatim)

Used by `shared/standards/spaces/room-types/*.json` entries' `cross_references.ashrae_90_1` field (back-filled at X.D.1).

## Files

- `lpd-table-9-6-1.json` — verbatim entries (key = ASHRAE snake_case space label, value = LPD in W/m² + W/ft²)
- `reference.md` — companion: usage notes + when LPD values may be inaccurate

## Key conventions

- **Keys** use ASHRAE's snake_case taxonomy (e.g. `office.open_plan`, `corridor.hospital`, `audience_seating_area.auditorium`). These are NOT the same identifiers as our OmniClass `canonical_id` values — the cross-walk lives in `room-types/*.json` at `cross_references.ashrae_90_1` (back-filled at X.D.1).
- **Values** are taken from the SI table (W/m²) and the I-P table (W/ft²) in the same Addendum ba PDF. Where the published addendum shows two stacked numbers (the top is the addendum-ba current value, the lower is the pre-addendum legacy value), this file records the **current** (top) value only.
- **RCR** (Room Cavity Ratio) thresholds are preserved on entries that publish them — see `_rcr_threshold` (only present where the standard publishes one).
- **Atrium** rows have height-dependent LPD allowances per Table 9.5.2.1-1; each height band is a separate entry.
- **Sports Arena Playing Area** rows (Class I/II/III/IV per IES RP-6) live under Table 9.5.2.1-2 — each class is a separate entry.

## When to extend

Future ASHRAE editions (2025+) — back-fill new entries here; bump `_edition` field and update `_source_url` to the new addendum PDF on ashrae.org.

## Supplemental references

The implementer cross-checked the verbatim PDF extraction against:

- **Whole Building Design Guide (WBDG / NIBS)** — lighting-energy chapters that cite Table 9.6.1 / 9.5.2.1
- **PNNL prototype-building reports** — 90.1 reference building energy models
- **GSA / DOE building energy publications** — 90.1 compliance guidance

Where supplemental sources and the primary ashrae.org mirror disagree, the primary mirror wins.
