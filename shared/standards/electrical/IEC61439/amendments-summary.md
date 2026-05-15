# IEC 61439 — Amendments and Edition History

IEC 61439 superseded IEC 60439 in 2009 with a fundamentally restructured approach. The standard has continued to evolve through 2nd-edition releases per part and addition of new Part 7 sub-parts.

---

## Edition history (per part)

| Part | First edition | Current edition | Major changes |
|---|---|---|---|
| 61439-1 (General) | 2009 | 2020 (3rd ed of -1) | Verification trio formalised, terminology aligned |
| 61439-2 (PSC-Assemblies) | 2009 | 2020 (2nd ed) | Forms unchanged; Annex 101 expanded |
| 61439-3 (DBO) | 2012 | 2012 (1st ed) | Defines DBO concept distinctly from PSC |
| 61439-4 (ACS) | 2012 | 2012 (1st ed) | IK ≥ 08 mandatory; RCD requirements aligned with IEC 60364-7-704 |
| 61439-5 (PENDA) | 2010 | 2014 (2nd ed) | Vandal-resistance and solar gain criteria refined |
| 61439-6 (BTS) | 2012 | 2012 (1st ed) | Replaces IEC 60439-6 |
| 61439-7-1 (Marinas/Camping) | 2014 | 2014 (1st ed) | New scope, was IEC 60439-4 (pre-2014) |
| 61439-7-2 (EV Charging) | 2018 | 2018 (1st ed) | Type B RCD requirements, mode-specific clauses |
| 61439-7-3 (Safety services) | 2018 | 2018 (1st ed) | Source-changeover classes, monitoring |
| 61439-7-4 (PV) | 2022 | 2022 (1st ed) | DC-side specifics, AFCI provisions |
| 61439-7-5 (Transformer-incorporated) | 2022 | 2022 (1st ed) | Medical IT and isolation transformer assemblies |

---

## Key changes that affect designers

### 2009–2014 — From IEC 60439 to IEC 61439

The withdrawal of IEC 60439 (all parts withdrawn 2014) and replacement by IEC 61439 introduced three changes that designers must internalise:

1. **Verification by test, calculation, or comparison with reference design.** IEC 60439 required type-test certificates; IEC 61439 accepts three equivalent paths. This dramatically lowers the cost of producing verified-to-standard assemblies for low-volume specials.

2. **Original Manufacturer (OM) vs Assembly Manufacturer (AM) responsibility split.** Formerly any "tested" assembly was simply tested by the supplier. IEC 61439 makes explicit that the OM provides the verified design (with type tests, calculations, or reference design certificates); the AM builds individual units within the OM's verified envelope. Many UK panel-builders are AMs licensed by an OM such as ABB or Schneider.

3. **Rated Diversity Factor (RDF).** Replaces the old assumption that all functional units operate at full rating simultaneously. Designer specifies the RDF (or accepts the OEM's default), and the OEM verifies temperature rise under that condition rather than 100% load.

### 2018 — Part 7-2 EV charging

The introduction of Part 7-2 reflects the rapid build-out of EV infrastructure. Two requirements affect MEP design:

- **Type B RCD (or equivalent DC-leakage protection).** Required where DC leakage > 6 mA is possible. Standard for Mode 4 fast chargers; required for unmanaged Mode 3 unless the EVSE itself has Type A + 6 mA DC.
- **Cable rated at 100% of EVSE rated current.** No diversity factor applies to the cable to the EVSE. A 32 A EVSE requires a 32 A continuous-rated cable regardless of load management.

### 2020 — Part 1 third edition

The 2020 third edition of Part 1 introduced no fundamental rule changes but consolidated 11 years of amendments. Practical impact:

- Annex E (temperature rise calculation) is more usable for design engineers without OEM-specific data.
- Annex P (short-circuit verification) clarifies the calculation path for non-standard assemblies.
- The terminology around assembly types (PSC vs DBO vs ACS vs PENDA) is rigorously distinguished.

### 2022 — Parts 7-4 (PV) and 7-5 (Transformer-incorporated)

These two new Part 7 sub-parts reflect modern application needs:

- **Part 7-4 (PV).** Codifies the DC-side requirements (1500 V Ue, DC-rated isolators, SPD at DC input). Some jurisdictions (US NEC 690) require AFCI in addition.
- **Part 7-5 (Transformer-incorporated).** Used heavily in medical Group 2 IT panels and in 110 V CTE reduced-voltage power tools supply.

---

## Withdrawn IEC 60439 — what to do with existing equipment

Assemblies installed under IEC 60439 before 2014 remain valid for their service life. They were verified to a different (test-only) standard and cannot be retro-claimed as IEC 61439-compliant.

For new designs: never reference IEC 60439. For extensions or modifications to existing IEC 60439 boards: extend per the original verification chain, document the boundaries, and consider whether a partial replacement to IEC 61439 is more cost-effective than continuing to verify against a withdrawn standard.

---

## National adoption status

| National code | Country | Relationship to IEC 61439 |
|---|---|---|
| BS EN 61439   | United Kingdom | Direct CENELEC adoption |
| DIN EN 61439  | Germany | Direct adoption |
| NF EN 61439   | France | Direct adoption |
| SS-EN 61439   | Sweden | Direct adoption |
| AS/NZS 61439  | Australia / New Zealand | Direct adoption with limited national variants |
| IS/IEC 61439  | India | Direct adoption |
| GB/T 7251     | China | Substantially aligned, with national variations on form codes |
| UL 891 / UL 67 | United States | Different standards family — NOT aligned with IEC 61439 |

A skill targeting a region with direct adoption can cite the national designation in the drawing legend alongside the IEC reference — both are correct.
