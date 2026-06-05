# Sprint X Source Provenance Spec

**Date:** 2026-06-05
**Companion to:** `docs/superpowers/specs/skill-input-design-rationale.md` (Sprint F.0 design rationale, commit `8c59304`)
**Sets:** citation-discipline contract for all Phase X.B per-category OmniClass transcription tasks + Phase X.C ASHRAE tasks + Phase X.A.3 IFC subset

---

## 1. OmniClass Table 13 mirror selection

### Primary mirror

- **URL:** https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.3_Omniclass_Table_13_Spaces_by_Function.pdf
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13 — Spaces by Function, **May 2011** (incorporated by reference into NBIMS-US V3, published 2015 by the National Institute of Building Sciences buildingSMART alliance)
- **Coverage estimate:** Authoritative wrapper PDF — confirms scope, normative references (ISO 12006-2, ISO TR 14177), and bibliography, but the embedded May 2011 table is referenced by inclusion rather than re-typeset in full. Use as the **authority citation** for code legitimacy; pair with the secondary mirror below for the verbatim code list.
- **Code format observed:** Canonical `13-XX XX XX XX XX` (five-level hierarchy), consistent with the published May 2011 edition.

### Secondary mirror (verbatim code list)

- **URL:** https://pdfcoffee.com/omniclass-13-2012-05-16-pdf-free.html
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13 — Spaces by Function, **2012-05-16** (next minor revision after May 2011; National Standard status)
- **Coverage estimate:** ~250–300 code entries across all parent categories; covers ~70–80% of the expected ~600-entry projection in Sprint X portion 1. Gaps are concentrated in deepest level-5 entries (13-XX XX XX XX XX) within Healthcare (13-51) and Environmentally Controlled (13-49).
- **Parent categories confirmed present:** 13-11 Space Planning Types, 13-13 Void Areas, 13-15 Wall Spaces, 13-17 Encroachment Spaces, 13-21 Parking Spaces, 13-23 Facility Service Spaces, 13-25 Circulation Spaces, 13-31 Education and Training Spaces, 13-33 Recreation Spaces, 13-35 Government Spaces, 13-37 Artistic Spaces, 13-41 Museum Spaces, 13-45 Library Spaces, 13-47 Spiritual Spaces, 13-49 Environmentally Controlled Spaces, 13-51 Healthcare Spaces.

### Backup mirror (corroboration only)

- **URL:** https://www.scribd.com/document/958191411/13-OmniClass
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13, 2012-05-16 edition (same as secondary mirror)
- **Use:** Spot-check the secondary mirror's level-5 codes if any individual code reads suspect.

### Authoritative source (paid, NOT used)

- **URL:** http://www.omniclass.org/tables.asp (CSI Construction Specifications Institute)
- **Status:** Licensed-only access via CSI Dynamic Standards. Sprint X does NOT acquire. Future Sprint Y when CSI license granted will back-fill `_verification_status: occs_verified` on entries that round-trip against this canonical source.

---

## 2. ASHRAE source mirrors

### ASHRAE 90.1 Table 9.5.2.1 (Space-by-Space LPD, formerly Table 9.6.1)

- **URL:** https://www.ashrae.org/file%20library/technical%20resources/standards%20and%20guidelines/standards%20addenda/90_1_2019_ba_20220909.pdf
- **Access date:** 2026-06-05
- **Edition reflected:** ANSI/ASHRAE/IES Addendum **ba** to Standard 90.1-2019 (effective 2022-09-09). Note: Addendum **ad** renumbered Table 9.6.1 → Table 9.5.2.1; Addendum **ba** split the renumbered table into Table 9.5.2.1-1 (common space types) and Table 9.5.2.1-2 (building-specific space types). Sprint X consumes the post-addendum numbering and back-references the historical Table 9.6.1 ID in `cross_references.ashrae_901_table` for searchability.
- **Coverage estimate:** ~120 of expected ~120 entries (full I-P and SI versions of both tables are present in the addendum PDF, hosted on the official ashrae.org domain).
- **Notes:** This is the canonical publisher mirror — no third-party intermediary.

### ASHRAE 62.1 Table 6-1 (Minimum Ventilation Rates in Breathing Zone)

- **URL:** https://static1.squarespace.com/static/6320b844c3820725e4d5688f/t/6372af076022e56f815dc7f5/1668460297956/ASHRAE+62.1-2022+(1).pdf
- **Access date:** 2026-06-05
- **Edition reflected:** ANSI/ASHRAE Standard **62.1-2022** (supersedes 62.1-2019). Table 6-1 spans pp. 16–18 of the standard with occupancy categories grouped by Animal Facilities, Correctional, Educational, Food and Beverage, General, Hotels/Motels/Resorts/Dormitories, Office, Public Assembly, Residential, Retail, Sports and Entertainment, and Miscellaneous.
- **Coverage estimate:** ~150 of expected ~150 occupancy categories (full Table 6-1 present, including I-P and SI default values for Rp, Ra, occupant density, air class, and OS — operational schedule references per §6.2.6.1.4).
- **Notes:** Third-party Squarespace hosting — not the ASHRAE publisher domain. Acceptable for Sprint X transcription on condition the X.E.4 reviewer cross-checks 5% of random entries against the WBDG flow chart (https://www.wbdg.org/FFC/DOD/UFC/ufc_3_410_01_ashrae_62.1_flow_chart.pdf) and the ASHRAE addenda series, both of which confirm the 62.1-2022 numbering and table structure.

---

## 3. IFC ISO 16739 source

- **URL:** https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/ (buildingSMART canonical, copyright 1996–2020 buildingSMART International Ltd.)
- **Access date:** 2026-06-05
- **Edition reflected:** IFC 4 (Final/official release), the ISO 16739 standardised schema
- **Entities transcribed (X.A.3 scope):** `IfcSpace`, `IfcSpaceTypeEnum` (SPACE / PARKING / GFA / INTERNAL / EXTERNAL / USERDEFINED / NOTDEFINED — confirmed verbatim from https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcspacetypeenum.htm), `IfcClassification`, `IfcClassificationReference`, `IfcRelAssociatesClassification`, `IfcLocalPlacement`, `IfcAxis2Placement3D` (room-type-relevant subset; ~200 lines).
- **Notes:** IFC4 Final is the published edition Sprint X consumes. IFC4.3 ADD2 / IFC4.3.x (ISO 16739-1:2024) supersedes for transport-infrastructure additions but does NOT alter the `IfcSpace` / `IfcSpaceTypeEnum` subset Sprint X uses; back-references to ISO 16739-1:2024 are documented in `_verification_status: mirror_sourced` notes per entry.

---

## 4. Verification status taxonomy

Per-entry `_verification_status` field carries one of:

- **`mirror_sourced`** — code transcribed verbatim from a declared mirror URL above. **Default state for Sprint X.** All entries land here unless flagged otherwise.
- **`occs_verified`** — code cross-checked against the canonical OmniClass Construction Classification System (OCCS) Table 13 PDF licensed via CSI. **Sprint X does NOT set this state.** Reserved for future Sprint Y when CSI licence acquired.
- **`inferred`** — code synthesised from hierarchy structure where mirror coverage is incomplete (e.g. mirror has parent `13-37 31 00 00` but not child `13-37 31 21 11`; child code synthesised from OmniClass numbering pattern). **MUST be honest-disclosed in per-entry `_inference_note`** explaining the parent code consulted and the numbering convention applied.

---

## 5. CIBSE + NRM2 deferred (documented blocker)

- **CIBSE LG1 / LG2 / LG5 / LG7 / LG10 / LG12 / Guide A / Guide F / SLL Code for Lighting** — paid CIBSE membership required for digital PDF access. Sprint X does NOT transcribe. `cross_references.cibse_lg` stays `null` on every entry.
- **NRM2 (RICS New Rules of Measurement 2)** — paid RICS member PDF required. Sprint X does NOT transcribe. `cross_references.nrm2` stays `null` on every entry.

Future Sprint Y when these source-access blockers cleared will back-fill the `cross_references.cibse_lg` and `cross_references.nrm2` fields without breaking existing `_verification_status` values.

---

## 6. Fabrication prevention contract

**NO IMPLEMENTER MAY FABRICATE OMNICLASS / ASHRAE / IFC CODES.** If a category cannot be sourced from a declared public mirror within reasonable coverage (≥70% of expected entries):

1. Implementer flags the gap in `_source_mirror.coverage_actual_pct` on the parent category record
2. Implementer ships the partial transcription with `_verification_status: mirror_sourced` on what they DID transcribe
3. Implementer documents the gap in `shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md`
4. Sprint X.E.4 final review verdict downgrades to **SHIP-WITH-NOTED-CONCERNS** but does NOT FAIL — partial coverage is acceptable when honestly disclosed; fabrication is not.

The X.E.4 reviewer spot-checks 5% of randomly-selected codes against the declared primary mirror (Section 1) and the ASHRAE addenda PDF (Section 2). If spot-check fails (codes absent from the mirror, or codes that do not match the mirror's hierarchy), the sprint verdict = **FIX-FIRST**.

Implementers who detect a mirror-vs-mirror discrepancy (e.g. NIBS 2011 wrapper vs 2012-05-16 secondary mirror disagree on a code) MUST defer to the **later edition** (2012-05-16) and record the discrepancy in `_inference_note`. This matches the OmniClass May 2011 → May 2012 minor-revision trajectory and avoids regression to the older edition.
