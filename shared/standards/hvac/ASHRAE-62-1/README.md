# ASHRAE 62.1 Table 6-1 — Minimum Ventilation Rates in Breathing Zone

Transcription of ANSI/ASHRAE Standard **62.1-2022** Table 6-1 (Minimum Ventilation Rates in Breathing Zone) — the canonical lookup for the Ventilation Rate Procedure (VRP) people-and-area outdoor airflow rates.

**Source:** `https://static1.squarespace.com/static/6320b844c3820725e4d5688f/t/6372af076022e56f815dc7f5/1668460297956/ASHRAE+62.1-2022+(1).pdf` (third-party Squarespace mirror declared in `docs/superpowers/specs/sprint-X-source-provenance.md`; X.E.4 reviewer must cross-check ≥5% of random entries against the WBDG UFC 3-410-01 flow chart and ASHRAE addenda)
**Edition:** ANSI/ASHRAE Standard **62.1-2022** (supersedes 62.1-2019)
**Access date:** 2026-06-05
**Coverage:** 89 occupancy/space-type entries spanning Table 6-1's 12 printed occupancy categories (Animal Facilities, Correctional, Educational, Food and Beverage, General, Hotels/Motels/Resorts/Dormitories, Miscellaneous, Office Buildings, Public Assembly, Residential, Retail, Sports and Entertainment).

Used by `shared/standards/spaces/room-types/*.json` entries' `cross_references.ashrae_62_1` field (back-filled at X.D.1).

## Files

- `ventilation-rates.json` — verbatim entries (key = ASHRAE snake_case `category.space_type`, value = Rp + Ra in SI and I-P + default occupant density + air class + OS eligibility)
- `reference.md` — companion: usage notes, the breathing-zone equation, dwelling-unit handoff to 62.2, and when published rates may be insufficient

## Key conventions

- **Keys** use ASHRAE's snake_case taxonomy mirroring the printed table headings (e.g. `office.open_plan`, `educational.classroom_age_9_plus`, `sports.swimming_pool_deck`). These are NOT the same identifiers as our OmniClass `canonical_id` values — the cross-walk lives in `room-types/*.json` at `cross_references.ashrae_62_1` (back-filled at X.D.1).
- **Values** are taken from the SI table (L/s) and the I-P table (cfm) in the same Standard 62.1-2022 PDF. ASHRAE publishes both independently and does NOT derive one from the other; values are transcribed verbatim without conversion.
- **Air class** is the integer 1, 2, 3, or 4 per the recirculation-control rules in Section 5.13 and Tables 6-2 / 6-3. Where the printed cell is blank (e.g. `educational.libraries`), `air_class` is `null` and `_air_class_note` documents the implementer's reading.
- **OS eligibility** (`os_eligible`) is `true` where the printed table marks "OS" in the rightmost column for § 6.2.6.1.4 occupant-standby reduction; `false` otherwise.
- **Null Rp / null default occupancy.** Three spaces are area-based only — `general.corridor`, `residential.common_corridor`, `sports.swimming_pool_deck`, plus the intermittent-occupancy `miscellaneous.telephone_closet`. Those entries publish `null` Rp + `null` default occupancy; `_rate_note` records the standard's rationale.
- **Default occupancy convention.** The table publishes occupant density as "#/1000 ft² or #/100 m²" — these two are dimensionally identical (1000 ft² ≈ 92.9 m², close enough that ASHRAE uses one number per row). Stored as `default_occupancy_per_100m2` only.

## What is NOT in this file

- **Single-family dwellings + interiors of multi-family dwelling units** — Section 6.2.1.1.7.1 dispatches these to **ANSI/ASHRAE Standard 62.2** (Ventilation and Acceptable Indoor Air Quality in Residential Buildings). 62.2 ventilation rates are NOT mirrored here.
- **Table 6-2 (Minimum Exhaust Rates)** — separate exhaust airflow rates for spaces like commercial kitchens, paint booths, parking garages, restrooms. Future X.C sub-task may transcribe Table 6-2 into a sibling file; out of scope for X.C.2.
- **Table 6-3 (Airstreams or Sources)** — air-class assignments for individual airstreams (e.g. kitchen grease hood = Class 4); referenced from Section 5.13 recirculation rules. Out of scope for X.C.2.
- **Table 6-4 (Zone Air Distribution Effectiveness, Ez)** — the air-distribution multiplier used to convert Vbz → Voz. Lives in the runtime calc engine, not the standards mirror.

## When to extend

- **Edition refresh.** ASHRAE publishes 62.1 on a 3-year cycle (2019 → 2022 → 2025). When a new edition ships, refresh from the latest publicly-accessible PDF or addendum, bump `_edition`, and update `_source_url`.
- **Table 6-2 / 6-3 transcription** — separate file under this folder when needed (`exhaust-rates.json`, `airstream-classes.json`).

## Supplemental cross-checks

The implementer cross-checked the verbatim PDF extraction against:

- **DOD WBDG / UFC 3-410-01** flow-chart for ASHRAE 62.1 VRP application
- **ASHRAE addenda series** for 62.1-2022 (no published addenda affect Table 6-1 values at access date)
- **AHRI / SMACNA** secondary documentation citing the same Rp + Ra values

Where supplemental sources and the primary Squarespace mirror disagree, the primary mirror wins.
