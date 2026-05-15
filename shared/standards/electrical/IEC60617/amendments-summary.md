# IEC 60617 — Amendments and Edition History

IEC 60617 has a different revision pattern from most IEC standards. It was originally published as a series of thirteen paper parts between 1983 and 2002, then migrated to a continuously-updated online database. This document summarises that history and what it means for symbol references in this layer.

---

## Phase 1 — Paper Parts (1983–2002)

The standard was issued in thirteen parts, each independently versioned:

| Part | Title | Last paper edition |
|---|---|---|
| 1 | Introduction (now withdrawn — content folded into Part 2) | 1985 |
| 2 | Symbol elements, qualifying symbols and other general symbols | 1996 |
| 3 | Conductors and connecting devices | 1996 |
| 4 | Basic passive components | 1996 |
| 5 | Semiconductors and electron tubes | 1996 |
| 6 | Production and conversion of electrical energy | 1996 |
| 7 | Switchgear, controlgear and protective devices | 1996 |
| 8 | Measuring instruments, lamps and signalling devices | 1996 |
| 9 | Telecommunications: switching and peripheral equipment | 1996 |
| 10 | Telecommunications: transmission | 1995 |
| 11 | Architectural and topographical installation plans | 1996 |
| 12 | Binary logic elements | 1997 |
| 13 | Analogue elements | 1997 |

During this period, an IEC reference number `IEC 60617-7, fig. 18-01` identified Part 7, section 18, symbol 01.

---

## Phase 2 — Database Edition (2002 onward)

In 2002, IEC migrated IEC 60617 from paper parts to a continuously-updated online database. The database is hosted at:

- Original URL: https://std.iec.ch/iec60617 (active)
- Earlier alias: https://www.graphical-symbols.info

Effects of the transition:

1. **No more periodic full-part revisions.** Individual symbols are added, deprecated, or revised as needed. The database carries a single live version rather than per-part edition numbers.
2. **Reference number format preserved.** A 2024-vintage symbol still references its parent part and section, in the form `IEC60617-PP-XX-YY`. New symbols added since 2002 use the same scheme.
3. **Withdrawal of paper parts.** The paper parts are no longer printed but remain the conceptual structure of the database. Part 1 has been folded into Part 2 and is no longer separately referenced.
4. **National adoptions track the database.** BS EN 60617, DIN EN 60617, NF EN 60617 etc. are adoptions of the database content. National standards bodies issue periodic snapshots of the database under their own designations.

This layer uses the database reference format throughout: `IEC60617-PP-XX-YY`.

---

## Notable Symbol Additions Since 2002

The transition to the database has enabled IEC to add symbols for technologies that did not exist in the 1996 paper editions. Of relevance to this layer:

| Symbol | Approximate added | Reason |
|---|---|---|
| Photovoltaic source (Part 6) | ~2005 | Rise of grid-tied PV installations |
| Wind turbine (Part 6) | ~2006 | Distributed generation |
| LED indicator (Part 8) | ~2010 | Replacement of incandescent indicator lamps |
| EV charging point (Part 11) | ~2018 | EV infrastructure on building plans |
| Battery storage (Part 6, distinct from UPS battery) | ~2020 | Behind-the-meter storage |
| Smart/AMR meter (Part 8) | ~2012 | Distinct symbol from analogue meter |
| SPD Type 1, 2, 3 distinctions (Part 7) | ~2010 | Coordination with IEC 61643-11 SPD classification |

---

## What This Means for Designers Using This Layer

1. **Quote the database reference.** When citing a symbol in design documentation, use the `IEC60617-PP-XX-YY` format from the `iec_ref` field, not the legacy paper-part `fig.` numbering.
2. **National differences are stylistic.** BS EN 60617 and DIN EN 60617 use the same reference numbers as the IEC database. Drawing-style preferences (e.g. North American IEEE/ANSI Y32.2 alternatives) are out of scope for this layer.
3. **Symbol shape stability.** Symbol geometry in this layer is stable across the database revisions — IEC has not historically changed the shape of an established symbol. New symbols use new reference numbers rather than overwriting old ones.
4. **Deprecated symbols.** Where the database flags a symbol as deprecated, this layer either omits it or marks it with `"status": "deprecated"` in a future revision (no deprecated symbols are present in v1.0.0).

---

## National Adoption Status (For Reference Only)

| National code | Country | Relationship to IEC 60617 |
|---|---|---|
| BS EN 60617 | United Kingdom | Direct adoption (CENELEC EN) |
| DIN EN 60617 | Germany | Direct adoption with German titles |
| NF EN 60617 | France | Direct adoption |
| SS-EN 60617 | Sweden | Direct adoption |
| NEN-EN-IEC 60617 | Netherlands | Direct adoption |
| IS/IEC 60617 | India | Direct adoption |
| AS/NZS IEC 60617 | Australia / New Zealand | Direct adoption (limited parts) |
| GB/T 4728 | China | Substantially aligned but with national variations |
| IEEE Std 315 / ANSI Y32.2 | United States | **Different standard** — not aligned with IEC 60617. Out of scope for this layer. |

A skill targeting a region listed above as "direct adoption" can cite the national designation in its drawing legend in addition to the IEC reference — both are correct.
