# ASHRAE 62.1 Table 6-1 — Reference

Companion to `ventilation-rates.json`. Source: **ANSI/ASHRAE Standard 62.1-2022 — Ventilation for Acceptable Indoor Air Quality** (Table 6-1, Minimum Ventilation Rates in Breathing Zone).

## Coverage

89 occupancy/space-type entries from Table 6-1's Ventilation Rate Procedure (VRP). Used for ventilation rate compliance checks in:

- **US jurisdiction** — adopted by reference in most state mechanical codes via IMC (International Mechanical Code) chapter 4. ASHRAE 62.1 is the de facto US commercial ventilation standard.
- **LEED certification** — IEQ Prerequisite Minimum Indoor Air Quality Performance and IEQ Credit Enhanced Indoor Air Quality Strategies both reference 62.1 VRP rates.
- **WELL Building Standard** — Air Concept Feature A01 references 62.1-2010 or later as the compliance floor.
- **International projects citing ASHRAE 62.1** — Middle East, Asia-Pacific, and select African jurisdictions where 62.1 is the contractually-specified ventilation standard.

## The breathing-zone equation

Total outdoor airflow rate required at the breathing zone:

    Vbz = Rp × Pz + Ra × Az

where:

- `Vbz` = breathing zone outdoor airflow rate, L/s (cfm)
- `Rp` = people outdoor air rate from Table 6-1, L/s per person (cfm/person)
- `Pz` = zone population — peak occupancy per § 6.2.1.1.7 (or average per Exception 1, or default density × area per Exception 2)
- `Ra` = area outdoor air rate from Table 6-1, L/s per m² (cfm/ft²)
- `Az` = zone net occupiable floor area, m² (ft²)

`Vbz` is then converted to `Voz` (zone outdoor airflow) via the zone air-distribution effectiveness `Ez` (Table 6-4):

    Voz = Vbz / Ez

The runtime calc engine owns `Vbz → Voz → Vot` (system outdoor airflow including the multi-zone equation per § 6.2.5); this standards file is the lookup target for `Rp` and `Ra` only.

## How room-types entries cross-reference

The `cross_references.ashrae_62_1` field on each room-types entry contains the key path into this file's `entries` dict. Example: a room-types entry like `commercial.office.open_plan` would carry `cross_references.ashrae_62_1: "office.open_plan"`.

Some room-types entries have no ASHRAE 62.1 Table 6-1 equivalent — e.g.:

- **Dwelling-unit interiors** (single-family bedrooms, multi-family kitchens, ensuites) — governed by ASHRAE 62.2, not 62.1. `cross_references.ashrae_62_1` is `null` and a parallel `cross_references.ashrae_62_2` field is back-filled where 62.2 transcription exists.
- **Industrial / heavy manufacturing / chemical-process spaces** — explicitly out of 62.1 scope per § 1.2 exceptions; ventilation is set by the EHS professional, often citing ANSI Z9 or sector-specific OSHA limits.
- **Healthcare patient-care areas** — § 1.2 exception (b) dispatches patient-care areas to ANSI/ASHRAE/ASHE Standard 170 (Ventilation of Health Care Facilities). 62.1 still applies to non-patient-care areas in healthcare buildings (offices, lobbies, public corridors).

For those entries `cross_references.ashrae_62_1` stays `null` and the relevant downstream standard is cited separately.

Cross-walk authoring happens at X.D.1; this file is the lookup target.

## When published rates may be inaccurate or insufficient

- **Edition drift.** ASHRAE updates 62.1 on a 3-year cycle (2019 → 2022 → 2025+). Table 6-1 values change infrequently between editions, but air-class assignments and OS eligibility have shifted across cycles. If the runtime needs a newer edition, re-source from the latest publicly-accessible PDF on ashrae.org and bump `_edition` + `_source_url`.
- **Unlisted occupancies (§ 6.2.1.1.1).** Where the proposed space is not listed in Table 6-1, the design engineer must choose the most similar listed category in terms of occupant density, activities, and building construction. The runtime cannot auto-resolve this — engineer judgement is required and must be recorded in the design rationale.
- **Unusual source strengths (§ 6.2.1.1.2).** Table 6-1 assumes typical contaminant sources. If unusual sources are expected (stored hazardous materials, theatrical smoke, dry ice, smoke-producing activities), the additional ventilation or air cleaning must be calculated using Section 6.3 (Indoor Air Quality Procedure) or criteria established by the EHS professional. The mirrored Rp + Ra values do NOT cover those cases.
- **Laboratory exception (§ 6.2.1.1.5).** Lab spaces complying with ANSI/AIHA Z9.5 in full are not required to comply with Table 6-1 rates. Where the Z9.5 exception applies, the Table 6-1 entry for `educational.science_laboratory` or `educational.university_laboratory` is a floor, not a ceiling.
- **Animal facility exception (§ 6.2.1.1.6).** Animal facilities with an EHS-completed risk evaluation are not required to comply with Table 6-1. The Animal Facilities entries are still useful as design starting points but are not regulatorily binding where the risk-evaluation exception is exercised.
- **Dwelling-unit air separation (§ 6.2.1.1.4).** Air from one dwelling unit with transient occupancy, or from any sleeping unit, shall NOT be recirculated or transferred to any other unit. This is a system-design constraint, not a per-space rate, but it affects multi-zone outdoor-air system selection.
- **Air density assumption (§ 6.2.1.1.3).** Rates assume dry-air density 1.2 kg/m³ at 21 °C and 101.3 kPa. Rates may be adjusted for actual density per § 6.2.1.1.3 but adjustment is not required for compliance. Altitude-sensitive projects (above ~1500 m) may benefit from the adjustment.
- **Zone population (§ 6.2.1.1.7).** The default occupant density is a fallback ONLY where actual peak (or fluctuating-average per Exception 1) occupancy cannot be established. Designers must use actual project occupancy when known; the default is the floor, not the design value.

## Banned-citation discipline

This file follows the Sprint X banned-citation discipline. The following tokens are banned (do NOT cite them in any ASHRAE 62.1 content):

- Lighting / electrical sub-clause tokens (those are electrical regulation IDs from BS 7671 / NEC; never cite them in HVAC ventilation content)
- The banned UK EV grant token (out-of-scope for ASHRAE)
- The banned legacy edition-number token (ASHRAE 62.1 edition is described by year, never as an edition number)
- The banned BS 7671 regulation token (BS 7671 is an electrical standard, never cite in ASHRAE content)
- The banned IES/CIBSE photometric symbols (lighting symbols, never cite in ventilation content)

ASHRAE 62.1 is cited as `ANSI/ASHRAE Standard 62.1-2022 § 6.2.1.1` (or the relevant clause number) or by table reference (`ANSI/ASHRAE Standard 62.1-2022 Table 6-1`).

## Source-mirror disclosure

The source URL declared at X.A.0 is a Squarespace mirror, not the ASHRAE publisher's own domain. This is acceptable for Sprint X transcription on condition that:

1. The X.E.4 reviewer cross-checks at least 5% of random entries against the **WBDG / UFC 3-410-01** flow chart and the ASHRAE addenda series.
2. Where any entry disagrees with WBDG or the addenda, the publisher-aligned value wins and the mirror entry is corrected.
3. Future edition refreshes prefer publisher-domain sources (ashrae.org direct download or ASHRAE Store excerpt) over third-party mirrors when those become publicly accessible.

This file's `_verification_status: "mirror_sourced"` flag on every entry signals that the entry was transcribed from the Squarespace mirror and is awaiting the X.E.4 cross-check.
