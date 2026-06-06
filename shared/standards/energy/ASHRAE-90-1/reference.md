# ASHRAE 90.1 Table 9.5.2.1 — Reference

Companion to `lpd-table-9-6-1.json`. Source: **ANSI/ASHRAE/IES Addendum ba to Standard 90.1-2019** (effective 2022-09-09), which renumbered the historical Table 9.6.1 → Table 9.5.2.1 (Addendum ad) and split it into Tables 9.5.2.1-1 (common space types) + 9.5.2.1-2 (building-specific space types).

The file name retains `lpd-table-9-6-1.json` for backwards searchability with project archives that still reference the legacy Table 9.6.1 number. The post-addendum table identifier (9.5.2.1-1 or 9.5.2.1-2) is preserved per entry in `_ashrae_table`.

## Coverage

~120 space types from ASHRAE's Space-by-Space Method. Used for Lighting Power Density (LPD) compliance checks in:

- **US jurisdiction** (state energy codes that adopt ASHRAE 90.1 by reference — most US states + CEC Title 24 cross-references)
- **LEED Energy & Atmosphere credits** (EA Prerequisite Minimum Energy Performance + EA Credit Optimize Energy Performance)
- **ENERGY STAR submissions** (Portfolio Manager benchmarking and the Designed to Earn the ENERGY STAR pathway)
- **International projects citing ASHRAE 90.1** (Middle East, Asia-Pacific, and select African jurisdictions where ASHRAE 90.1 is the de facto commercial energy standard)

## How room-types entries cross-reference

The `cross_references.ashrae_90_1` field on each room-types entry contains the key path into this file's `entries` dict. Example: a room-types entry like `commercial.office.open_plan` would carry `cross_references.ashrae_90_1: "office.open_plan"`.

Some room-types entries have no ASHRAE 90.1 equivalent — e.g.:

- **Residential dwelling rooms** (bedroom, kitchen, ensuite) — ASHRAE 90.1 covers commercial/institutional buildings; residential is out of scope except for the small "Guest Room" + "Dormitory—living quarters" subset that appears under hospitality/correctional building types.
- **Single-family residential garages, basements, attics** — out of ASHRAE 90.1 scope.

For those entries `cross_references.ashrae_90_1` stays `null`.

Cross-walk authoring happens at X.D.1; this file is the lookup target.

## When LPD values may be inaccurate or insufficient

- **Edition drift.** ASHRAE updates 90.1 on a 3-year cycle (2019 → 2022 → 2025+). Addendum ba (Sep 2022) is the latest substantive change to the Space-by-Space LPD allowances at the time of transcription. If the runtime needs a newer edition, re-source from the latest publicly-accessible addendum PDF on ashrae.org and bump `_edition` + `_addendum`.
- **Addendum ba split.** Building-specific space types that used to live under the common Table 9.6.1 are now isolated in Table 9.5.2.1-2. Some building-specific space types **shadow** common space types (e.g. "Audience seating area" appears as both common and correctional-specific). When both apply, the building-specific row wins per Table 9.5.2.1-2 footnote (a).
- **Pre-addendum legacy values.** The published addendum PDF prints two stacked numbers in many cells — the top is the current addendum-ba value, the lower is the pre-addendum legacy value. This file records the **current** (top) value only. Engineers comparing against pre-2022 design files must consult the legacy 90.1-2019 base (without Addendum ba) for the lower value.
- **Unit conversions.** The standard publishes both W/m² (SI) and W/ft² (I-P) tables. Values in this file are taken directly from each table — they are NOT computed from one another. The implementer-observed rounding pattern is that ASHRAE rounds independently in each unit, so dividing W/ft² by 0.0929 will not always reproduce the printed W/m² exactly (and vice versa).
- **Space-type ambiguity.** ASHRAE's `office.open_plan` may map cleanly to an OmniClass office space, but the LPD allowance assumes specific design conditions (RCR, ceiling height, daylit zone, control strategy). Engineers must verify per-project that the assumed space conditions hold; the LPD allowance is a compliance ceiling, not a target design value.
- **RCR thresholds and width thresholds** are not strict bounds — they are the room geometry assumed by ASHRAE when calibrating the LPD value. Spaces with significantly different RCR (e.g. very tall narrow rooms) may need engineering judgement; the printed LPD is still the regulatory ceiling.
- **Additional allowances.** Some rows publish an additional allowance for specific lighting subsystems (e.g. electrical/mechanical rooms — Table 9.5.2.1-1 footnote 7 allows +5.6 W/m² for separately-controlled task lighting). Those allowances are captured in `_additional_allowance_note` and must be added to the base LPD per the footnote's controlled-circuit requirement.

## Supplemental cross-checks

The implementer cross-checked the verbatim PDF extraction against publicly-cited tables in:

- **Whole Building Design Guide (WBDG)** — NIBS lighting-energy chapters
- **PNNL prototype-building reports** — Pacific Northwest National Laboratory 90.1 reference building energy models
- **GSA / DOE building energy publications** — federal energy compliance guidance

Where supplemental sources and the primary ashrae.org Addendum ba PDF disagree (typically because the supplemental source predates Addendum ba), the primary mirror wins and Addendum ba values are used.

## Banned-citation discipline

This file follows the Sprint X banned-citation discipline. The following tokens are banned (do NOT cite them in any ASHRAE content):

- Lighting-related sub-clauses (the banned electrical sub-clause tokens) — those are electrical regulation IDs, never cite them in ASHRAE 90.1 content
- The banned UK EV grant token — never cite, out-of-scope for ASHRAE
- The banned legacy edition-number token (ASHRAE 90.1 edition is described by year, never cite as an edition number)
- The banned BS 7671 regulation token — never cite in ASHRAE content
- The banned IES/CIBSE photometric symbols — never cite in LPD content

ASHRAE 90.1 is cited as `ANSI/ASHRAE/IES Standard 90.1-2019 Addendum ba § 9.5.2.1` or by table reference.
