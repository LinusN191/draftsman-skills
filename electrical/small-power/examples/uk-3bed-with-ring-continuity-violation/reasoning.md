# uk-3bed-with-ring-continuity-violation — reasoning walkthrough

**Example purpose.** Sprint D4 Phase C.9 — the canonical **FAIL HIGH**
demonstration of the new `INV-14` (ring final circuit continuity) rule
that ships in small-power `v2.0.0`. This is the **FAIL counterpart** to
C.8 (`uk-3bed-with-ring-continuity` PASS). Same 3-bed dwelling geometry;
two deliberate install defects engineered into the two rings (one per
INV-14 sub-check) so the example exercises **both failure modes
independently**.

`INV-14` FIRES HIGH on BOTH rings:

- **C01 sub-check 1 FAIL** — `mcb_way_id` consistency broken
  (`endpoint_b` misterminated at `CU-MAIN-WAY-2` instead of the
  design-intended `CU-MAIN-WAY-1`).
- **C02 sub-check 2 FAIL** — `continuity_verified: false` because the
  engineer-of-record never performed the IET OSG Appendix H ring
  continuity verification at first fix.

The IR is **STRUCTURALLY VALID** against `small-power-ir.schema.json`
(`ring_endpoints` object present on both rings with all required fields
populated); the engineering is broken, not the schema shape.
`compliance_summary.compliant: false` per the FAIL-by-design discipline.

---

## Why this example exists

`INV-14` needs both PASS and FAIL coverage in the eval harness to assert
that the rule fires in both directions. The C.8 + C.9 pair is the
canonical coverage pattern:

- **C.8 PASS** — both rings correctly engineered (matching `mcb_way_id`
  on both legs + `continuity_verified: true`).
- **C.9 FAIL** — both rings with broken continuity engineering, one per
  sub-check.

Same geometry, opposite verdicts. The split failure modes (C01 = sub-check
1 FAIL, C02 = sub-check 2 FAIL) exercise both `INV-14` sub-checks
independently per ring.

---

## C01 violation walkthrough — endpoint_b misterminated (sub-check 1 FAIL)

The IR schema captures **one `mcb_way_id` field per `ring_endpoints`
object**, not one per endpoint. The structural field carries the
design-intended way (`CU-MAIN-WAY-1`). The first-fix wiring survey
recorded `endpoint_b` actually terminated at `CU-MAIN-WAY-2` — physically
a different MCB way at the consumer unit.

A ring landing at two different MCB ways is structurally **TWO RADIALS
sharing conductors**, not a real ring:

- The design-intended ring loop (phase + neutral + CPC loop) is broken at
  the consumer unit.
- Current would flow as two parallel radials with halved cable
  cross-section per leg under fault conditions.
- The `Zs` / cable thermal protection assumptions for ring topology no
  longer apply.

The Appendix H end-to-end resistance reading recorded an anomalous `r1`
(approximately half the expected loop value per leg — the **classic
broken-ring signature**), so `continuity_verified: false`.

### Where the violation is captured in the IR

The schema-level violation surfaces in:

1. **`circuits[0].ring_endpoints._citation`** prose explicitly recording
   the wrong-way termination at install.
2. **`circuits[0].designation`** prose flagging the misterminated
   endpoint.
3. **`compliance_summary.non_compliance_flags[0]`** entry with
   `severity: "critical"` (IR schema enum mapping for HIGH — see honest
   disclosure #2 below).
4. **`invariants[INV-14].evidence`** text describing both sub-check
   failures.

### Remediation

Engineer-of-record reterminates `endpoint_b` at `CU-MAIN-WAY-1`, re-runs
the Appendix H `r1`/`rn`/`r2` readings, and re-issues
`continuity_verified: true` after confirming the readings match the
paired-equality pattern (`r1 ≈ rn`, `r2 ≈ 1.67 × r1` for the
`2.5 / 1.5` phase/CPC composition).

---

## C02 violation walkthrough — Appendix H verification never performed (sub-check 2 FAIL)

Both legs of C02 are documented as landing at the intended
`CU-MAIN-WAY-2` — `INV-14` sub-check 1 (`mcb_way_id` consistency) would
have **passed**. But the engineer-of-record never performed the IET OSG
Appendix H ring continuity verification at first fix; the
`r1`/`rn`/`r2` end-to-end resistance readings are absent from the
Schedule of Test Results.

The design cannot attest that the ring is correctly closed: the
conductors might be cleanly terminated at the correct way and the ring
might be physically intact — but without the verification reading no
attestation can be made. `continuity_verified: false` reflects the
**absent test record** (it is set to false because there is no evidence
that the ring is verified, not because there is evidence that it is
broken).

### Procedural-omission vs install-defect FAIL

C02 may be physically a perfectly-closed ring; the violation is
procedural — the verification reading is missing. `continuity_verified:
false` means **"design cannot attest verification has been performed"**,
not "verification was performed and failed". The two states are
operationally equivalent at design freeze (engineer-of-record may not
energise until the reading is on record) but semantically distinct.

This is a **different failure mode from C01**:

| Aspect          | C01                                                   | C02                                                |
| --------------- | ----------------------------------------------------- | -------------------------------------------------- |
| Failure mode    | Install defect                                        | Procedural omission                                |
| Sub-check       | 1 (`mcb_way_id` consistency)                          | 2 (`continuity_verified: true`)                    |
| Evidence type   | Wrong-way termination + anomalous `r1` reading        | Missing Appendix H test record                     |
| Remediation     | Reterminate `endpoint_b` + re-test                    | Perform Appendix H + file readings                 |
| Ring physically | Two-radials topology (broken)                         | Unknown — likely intact, but unverified            |

A real-world install often has BOTH problems on the same ring; the
example splits them across two rings for pedagogical clarity.

### Remediation

Engineer-of-record performs the Appendix H `r1`/`rn`/`r2` ring continuity
verification at first fix (or as soon as access permits), files the
readings to the Schedule of Test Results, and re-issues
`continuity_verified: true`.

---

## Validator INV emission table (19 INVs)

| INV    | Result    | Severity   | Note                                                                                                                                |
| ------ | --------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| INV-01 | PASS      | high       | Rings on 2.5/1.5 CPC PVC T+E with 32 A RCBO matches Appendix 15 recipe — cable composition is correct; only termination is broken    |
| INV-02 | PASS      | high       | All 3 circuits' breaking_capacity_ka (6.0) ≥ parent_db.pfc_at_busbar_ka (6.0)                                                       |
| INV-03 | PASS      | high       | All 3 circuits Type A 30 mA RCBO per `§411.3.3`                                                                                     |
| INV-04 | PASS      | high       | GB jurisdiction permits ring final circuits per `§433.1` — INV-04 checks topology, not continuity                                   |
| INV-05 | PASS      | high       | Every socket's circuit_id matches its room's circuit coverage                                                                       |
| INV-06 | PASS      | low        | All Type B curve — appropriate for domestic mixed loads                                                                             |
| INV-07 | PASS      | high       | diversified_max_load_a < OCPD rating on all 3 circuits                                                                              |
| INV-08 | PASS      | high       | Zs deferral consistent — but contingent on ring remediation (Zs result is meaningless until C01 retermination + C02 Appendix H)      |
| INV-09 | PASS      | high       | chat_summary 781 chars ≤ 800 cap                                                                                                    |
| INV-10 | PASS      | low        | GB drawing standard BS 1192:2007+A2:2016 applied                                                                                    |
| INV-11 | PASS      | high       | No cable-sizing intent consumed — no-op                                                                                             |
| INV-12 | PASS      | high       | **N/A** — no Part-7 room_types; cascade trigger does not fire                                                                       |
| INV-13 | PASS      | low        | **N/A** — building_diversity absent                                                                                                 |
| INV-14 | **FAIL**  | **high**   | **Both rings: C01 sub-check 1 FAIL (wrong-way endpoint_b) + C02 sub-check 2 FAIL (Appendix H missing)** — the canonical FAIL demo    |
| INV-15 | PASS      | high       | **N/A** — circuit.floor_area_m2 not populated                                                                                       |
| INV-16 | PASS      | high       | Rings 32 A on 2.5/1.5 CPC ≤ ring ceiling; dedicated_radial trivially PASSes — INV-16 checks coordination, not continuity            |
| INV-17 | PASS      | medium     | **N/A** — no fcu_spurs[] populated (deliberately omitted to scope failure surface tightly to INV-14)                                |
| INV-18 | PASS      | high       | **N/A** — no EV charge circuits                                                                                                     |
| INV-19 | PASS      | medium     | **N/A** — both building_diversity + cable-sizing inputs absent                                                                      |

**Active FAILes:** `INV-14` (twice — once per ring, two distinct
sub-check failure modes). The other 18 INVs PASS or are N/A and trivially
PASS — the violations are scoped tightly to the ring continuity surface.
This isolation is important: the eval can assert `INV-14` FAILS twice
while `INV-01`/`INV-02`/`INV-03`/`INV-04`/`INV-05`/`INV-07` still PASS
on the same fixture.

---

## OCPD + cable selection + RCD posture (unchanged from C.8)

The OCPD and cable selection is engineered **correctly** — the violations
are scoped tightly to the ring continuity surface. Both rings use 32 A
Type B RCBO + 2.5 mm² + 1.5 mm² CPC PVC T+E per BS 7671 Appendix 15. The
cooker uses 32 A Type B RCBO + 6 mm² T+E PVC on a dedicated radial. All
breakers Type B (no significant inrush). All RCBOs 6 kA Icu meets the
declared PSCC = 6 kA at the CU busbar per BS 7671 §434.5.1 minimum
boundary.

All three circuits use Type A 30 mA RCBOs per `§411.3.3` additional
protection for socket outlets ≤32 A. The `§411.3.3` citation appears
only in RCD-posture context per the verified-citations discipline.

`Zs` verification deferred to `calc.zs_loop_impedance` per WI3:
`tool_call_pending_for_zs_verification: true` on every circuit. But note:
`Zs` verification on C01 is **meaningless until the ring is correctly
closed** — the current two-radials-sharing-conductors topology would
yield `Zs` readings that do not represent the eventual design-intended
ring loop. Remediation order:

1. C01 retermination + Appendix H re-test.
2. C02 Appendix H performed + readings filed.
3. **Then** `Zs` deferred to `calc.zs_loop_impedance` per the standard
   pattern.

---

## Honest disclosures (4-place engineering judgment surface)

This example carries four specific honest disclosures making the
FAIL-by-design judgment explicit at the schema-validated level:

1. **FAIL-by-design discipline.** This example is **DELIBERATELY**
   engineered to fire `INV-14` FAIL HIGH on both rings.
   `compliance_summary.compliant: false` is the by-design outcome. The
   IR is structurally valid against the IR schema (`ring_endpoints`
   present on both rings with all required fields populated); the
   broken engineering surfaces in the prose evidence + `invariants[]`
   block, not in the schema shape. Recorded in
   `compliance_summary.assumptions[1]` and in the third entry of
   `non_compliance_flags[]` (the `severity: "info"` pedagogy entry).

2. **IR schema severity enum mapping.** The IR schema's
   `compliance_summary.non_compliance_flags` severity enum is
   `{critical, warning, info}` — `"high"` is not a valid value at that
   layer. The spec calls for HIGH severity on the two `INV-14` entries
   — this maps to `"critical"` (the strongest available schema enum)
   here because broken ring continuity is a real safety-critical
   fault-loop hazard. The `invariants[]` block uses the
   `{critical, high, medium, low}` enum directly and `INV-14` carries
   `severity: "high"` there — the canonical HIGH severity emission.
   Recorded in `compliance_summary.assumptions[2]`.

3. **C01 engineering specifics — wrong-way termination.** `endpoint_b`
   was misterminated at `CU-MAIN-WAY-2` instead of the design-intended
   `CU-MAIN-WAY-1`. The structural `mcb_way_id` field carries the
   design-intended way (`CU-MAIN-WAY-1`) only — the schema does not have
   a per-endpoint `mcb_way_id` field. The wrong-way-termination at
   install is recorded in the `ring_endpoints._citation` prose, in the
   circuit `designation`, and in the `INV-14` evidence. Recorded in
   `compliance_summary.assumptions[3]`.

4. **C02 engineering specifics — missing Appendix H verification.** Both
   legs are documented as landing at the intended `CU-MAIN-WAY-2`
   (sub-check 1 would have passed). The violation is sub-check 2 —
   `continuity_verified: false` because the engineer-of-record never
   performed the IET OSG Appendix H ring continuity verification at
   first fix. This is a **different** `INV-14` failure mode from C01
   (procedural-omission FAIL vs install-defect FAIL); the pair
   demonstrates that `INV-14` catches both sub-checks independently per
   ring. Recorded in `compliance_summary.assumptions[4]`.

### Verified-citation discipline

Only the following standards are cited in the IR:

- `BS 7671:2018+A2:2022 §433.1` (general overcurrent protection
  principles — the only sub-clause of §433 transcribed in the verified
  file).
- `BS 7671:2018+A2:2022 §526` top-level (sub-clause beyond top-level is
  NOT transcribed in the verified file; cite only the top-level).
- `BS 7671:2018+A2:2022 §411.3.3` cited ONLY in RCD-posture context.
- `BS 7671:2018+A2:2022 §411.4.5` (TN disconnection time).
- `BS 7671:2018+A2:2022 §434.5.1` (breaking capacity minimum).
- `BS 7671:2018+A2:2022 Appendix 15` (final circuit composition).
- `IET On-Site Guide §8.4.4` (ring final circuit footprint guidance).
- `IET On-Site Guide Appendix H` (ring continuity verification).
- `IET On-Site Guide Appendix A` (diversity factors).
- `BS 1363` (13 A sockets).
- `BS 4177` (cooker control unit).
- `BS EN 60898-1` (MCB curves).
- `BS 1192:2007+A2:2016` (drawing standard).
- `Part M of the Building Regulations 2010 (England)` (socket mounting
  height).

**Banned tokens — do NOT cite anywhere in skill output:** the
sub-clauses beyond top-level `§526` and beyond top-level `§433` (sub-clauses
not transcribed in verified file), `OZEV` (do NOT cite — operational
policy, not a BS standard), `3rd Edition` of any IET CoP (do NOT cite —
superseded), `Reg 559` (do NOT cite — not the ring continuity regulation,
and this is banned regardless of context).

---

## Pair-with-PASS-example (Sprint D4 Phase C.8)

This FAIL example is the SECOND half of a PASS / FAIL pair. The
companion PASS example (`uk-3bed-with-ring-continuity`) ships in the same
Phase C batch with:

- Same 3-bed dwelling geometry (same rooms, same supply, same parent CU).
- Both rings correctly engineered: matching `mcb_way_id` on both legs
  per ring + `continuity_verified: true` on both rings.
- One 13 A FCU spur on the GF ring (1800 W extractor hood) demonstrating
  `INV-17` PASS as the secondary engineering surface.
- `INV-14 PASS` on both rings.
- `compliance_summary.compliant: true`.

The eval harness (the `INV-14` ring continuity eval, e.g.
`eval-10-ring-continuity.yaml` or equivalent) consumes both fixtures and
asserts:

- `INV-14 PASS` on the C.8 fixture (both rings).
- `INV-14 FAIL` on the C.9 fixture (both rings, with distinct sub-check
  failure modes per ring).

The split failure modes (C.9 C01 = sub-check 1 FAIL, C.9 C02 = sub-check
2 FAIL) exercise both `INV-14` sub-checks independently. Future Phase
D/E examples may exercise `INV-14` in cross-product with other rules
(e.g. `INV-17` PASS + `INV-14` FAIL on the same ring) but the C.8/C.9
pair is the canonical baseline.
