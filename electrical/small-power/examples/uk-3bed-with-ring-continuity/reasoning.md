# uk-3bed-with-ring-continuity — reasoning walkthrough

**Example purpose.** Sprint D4 Phase C.8 canonical PASS demonstration of the
new `INV-14` (ring final circuit continuity) rule that ships in small-power
`v2.0.0`. The schema's `allOf` clause REQUIRES `ring_endpoints` to be
populated whenever `circuits[].topology == "ring"`; `INV-14` then verifies
that `endpoint_a_xy` and `endpoint_b_xy` land at the SAME `mcb_way_id` AND
that `continuity_verified: true`. This example exercises that rule on TWO
independent rings (GF + 1F) both correctly engineered.

This is the **PASS counterpart** to
`uk-3bed-with-ring-continuity-VIOLATION` (C.9) which fires `INV-14 FAIL
HIGH` on a ring landing at two different MCB ways. The pair exercises
`INV-14` both directions — PASS here, FAIL there — and gives the eval
harness (`eval-10-ring-continuity.yaml`) two real fixtures to assert
against.

A secondary engineering surface is exercised in passing: one 13 A FCU spur
on the GF ring (kitchen under-cabinet extractor hood, 1800 W downstream)
demonstrates `INV-17` (AMD 2 FCU spur modelling) PASS with 40 % headroom
below the 2990 W FCU ceiling. The combined `INV-14 + INV-17` PASS
demonstration matches the plan's Phase C.8 task description.

---

## Generator Step 14 walkthrough (engineering chain)

### Step 14.a — Site brief intake

Engineer brief: UK 3-bed 2-storey dwelling, ~95 m² total, TN-C-S supply
from the DNO at the consumer cut-out with declared `Ze = 0.35 Ω` and
`PSCC = 6 kA`. Consumer unit `CU-MAIN` is a 12-way Amendment-3 board with
6 kA Icu busbar. Eight habitable rooms: kitchen, utility, dining, lounge,
landing, three bedrooms. No bathroom shaver supply and no outdoor socket
on this design — the dwelling intentionally avoids Part-7 special-location
rooms so the example focuses cleanly on the ring continuity engineering
without entangling the special-locations cascade machinery.

### Step 14.b — Topology selection per jurisdiction

GB jurisdiction so ring final circuits are permitted per
`BS 7671:2018+A2:2022 §433.1`. Two rings selected:

- **C01 — Ground-floor ring** covering kitchen + utility + dining +
  lounge (approximately 52 m²).
- **C02 — First-floor ring** covering 3 bedrooms + landing
  (approximately 36 m²).

Both rings are inside the IET On-Site Guide §8.4.4 100 m² recommended
footprint for a 32 A ring final circuit. The cooker is on a dedicated
radial (C03) because the 7 kW hob+oven nameplate exceeds the FCU 13 A
ceiling AND exceeds the diversified contribution a ring can reasonably
absorb.

### Step 14.c — Ring continuity engineering (the heart of this example)

For each ring the engineer-of-record must terminate both legs of every
conductor (phase + neutral + CPC) at the SAME terminal on the SAME MCB
way. A ring landing at two different MCB ways is structurally TWO RADIALS
sharing conductors — the Zs / cable thermal protection assumptions for
ring topology no longer apply.

**C01 ring termination.** Both legs land at `CU-MAIN-WAY-1`:

- `ring_endpoints.endpoint_a_xy = {x_mm: 200, y_mm: 200}` — the leg
  exiting the CU on the upstream side.
- `ring_endpoints.endpoint_b_xy = {x_mm: 8500, y_mm: 200}` — the leg
  returning to the CU after the perimeter loop.
- `ring_endpoints.mcb_way_id = "CU-MAIN-WAY-1"` — both legs.
- `ring_endpoints.continuity_verified = true` — engineer-of-record
  records end-to-end resistance per IET On-Site Guide Appendix H ring
  continuity verification procedure at first fix.

**C02 ring termination.** Both legs land at `CU-MAIN-WAY-2`:

- `ring_endpoints.endpoint_a_xy = {x_mm: 200, y_mm: 200}` — leg exiting
  the CU.
- `ring_endpoints.endpoint_b_xy = {x_mm: 7200, y_mm: 200}` — leg
  returning to the CU.
- `ring_endpoints.mcb_way_id = "CU-MAIN-WAY-2"` — both legs.
- `ring_endpoints.continuity_verified = true`.

**Continuity verification procedure (IET OSG Appendix H).** The
engineer-of-record performs three end-to-end resistance readings with a
low-resistance ohmmeter:

1. `r1` (phase loop): from line terminal at the MCB to the same terminal
   after traversing the ring. Should be approximately `2 × (length / Iz
   per metre)` for 2.5 mm² phase.
2. `r2` (CPC loop): same for the 1.5 mm² CPC. Should scale by phase /
   CPC csa ratio (2.5 / 1.5 = 1.67×).
3. `rn` (neutral loop): same for the 2.5 mm² neutral. Should be
   approximately `r1`.

The expected reading triplet (`r1 ≈ rn`, `r2 ≈ 1.67 × r1`) confirms ring
continuity. Any single reading high indicates a broken or
poorly-terminated conductor and the ring fails INV-14 at the
commissioning stage. Setting `continuity_verified: true` at design time
attests that the engineer-of-record has the procedure scheduled into the
install programme.

### Step 14.d — FCU spur engineering on C01 (INV-17 PASS)

The GF ring carries ONE 13 A fused connection unit (FCU) spur. AMD 2 of
the IET On-Site Guide introduced explicit modelling for FCU spurs on
ring final circuits; the rule (`TOP-12`) requires every entry in
`fcu_spurs[]` to satisfy:

- `fcu_rating_a ∈ {3, 5, 13}` (standard FCU cartridge fuse ratings).
- `downstream_loads_w ≤ fcu_rating_a × 230 V` (the FCU is the OCPD for
  the downstream fixed appliance).

This example's single FCU spur:

- `location_xy = {x_mm: 4500, y_mm: 200}` — kitchen worktop wall,
  approximately mid-ring.
- `fcu_rating_a = 13` (standard for kitchen fixed appliances).
- `downstream_loads_w = 1800` (typical kitchen under-cabinet extractor
  hood: 1.8 kW extraction motor + lighting + control electronics).

Validation: `1800 ≤ 13 × 230 = 2990` → PASS with `1190 W` (40 %)
headroom.

### Step 14.e — OCPD + cable selection

Both rings use 32 A Type B RCBO + 2.5 mm² + 1.5 mm² CPC PVC T+E per
BS 7671 Appendix 15 standard ring final circuit recipe. The cooker uses
32 A Type B RCBO + 6 mm² T+E PVC sized for the 25 A diversified load
(IET OSG Appendix A cooker diversity formula: `10 + 30% × (32-10) + 5 =
21.6 A → rounded to 25 A`).

All breakers Type B — domestic loads have no significant inrush. All
RCBOs 6 kA Icu meet the declared PSCC = 6 kA at the CU busbar per
BS 7671 §434.5.1 minimum boundary.

### Step 14.f — RCD posture

All three circuits use Type A 30 mA RCBOs per `§411.3.3` additional
protection for socket outlets ≤32 A in domestic premises. No Type B
requirement because there are no DC-injecting loads (no EV chargers, no
PV inverters) on this dwelling. The cited regulation `§411.3.3` is the
RCD-posture regulation — the only context in which it may be cited per
the verified-citations discipline of the small-power skill.

### Step 14.g — Zs deferral

Zs verification deferred to `calc.zs_loop_impedance` per WI3:
`tool_call_pending_for_zs_verification = true` on every circuit and
`TOOL-CALL-PENDING:calc.zs_loop_impedance` set in `flags[]`. At
install-side commissioning the engineer reads the actual Zs per `§612`
and compares against the `§411.4.5` disconnection-time table (32 A
Type B, 0.4 s domestic = 1.37 Ω at U0 = 230 V).

---

## Validator INV emission table (19 INVs)

| INV    | Result | Severity | Note                                                                                       |
| ------ | ------ | -------- | ------------------------------------------------------------------------------------------ |
| INV-01 | PASS   | high     | Rings on 2.5/1.5 CPC PVC T+E with 32 A RCBO matches Appendix 15 recipe                     |
| INV-02 | PASS   | high     | All 3 circuits' breaking_capacity_ka (6.0) ≥ parent_db.pfc_at_busbar_ka (6.0)              |
| INV-03 | PASS   | high     | All 3 circuits Type A 30 mA RCBO per `§411.3.3`                                            |
| INV-04 | PASS   | high     | GB jurisdiction permits ring final circuits per `§433.1`                                   |
| INV-05 | PASS   | high     | Every socket's circuit_id matches its room's circuit coverage                              |
| INV-06 | PASS   | low      | All Type B curve — appropriate for domestic mixed loads                                    |
| INV-07 | PASS   | high     | diversified_max_load_a < OCPD rating on all 3 circuits                                     |
| INV-08 | PASS   | high     | Zs deferral consistent across all 3 circuits + flag                                        |
| INV-09 | PASS   | high     | chat_summary 729 chars ≤ 800 cap                                                           |
| INV-10 | PASS   | low      | GB drawing standard BS 1192:2007+A2:2016 applied                                           |
| INV-11 | PASS   | high     | No cable-sizing intent consumed — no-op                                                    |
| INV-12 | PASS   | high     | **N/A** — no Part-7 room_types; cascade trigger does not fire                              |
| INV-13 | PASS   | low      | **N/A** — building_diversity absent (small dwelling, not office/healthcare/industrial)     |
| INV-14 | **PASS** | **high** | **Both rings: mcb_way_id consistency + continuity_verified=true** — the canonical demo    |
| INV-15 | PASS   | high     | **N/A** — circuit.floor_area_m2 not populated                                              |
| INV-16 | PASS   | high     | Rings 32 A on 2.5/1.5 CPC ≤ ring ceiling; dedicated_radial trivially PASSes                |
| INV-17 | **PASS** | **medium** | **C01 fcu_spurs[0]: 1800 W ≤ 2990 W ceiling (40% headroom)** — secondary demo            |
| INV-18 | PASS   | high     | **N/A** — no EV charge circuits                                                            |
| INV-19 | PASS   | medium   | **N/A** — both building_diversity + cable-sizing inputs absent                             |

**Active PASSes:** `INV-14` (twice — once per ring) and `INV-17` (once on
C01). The other 17 INVs are either trivially PASS on standard domestic
shape or N/A and trivially PASS per the validator wording. The example's
engineering scope is INV-14 + INV-17 demonstration; all other
engineering surfaces are out of scope and belong to other Phase A/B/C
examples.

---

## Honest disclosures (4-place engineering judgment surface)

This example carries four specific honest disclosures making the
engineering judgment explicit at the schema-validated level:

1. **Verified-citation discipline.** Only the following standards are
   cited in the IR:

   - `BS 7671:2018+A2:2022 §433.1` (general overcurrent protection
     principles — the only sub-clause of §433 transcribed in the
     verified file).
   - `BS 7671:2018+A2:2022 §526` top-level (sub-clause `§526.2` is NOT
     transcribed in the verified file; cite only the top-level).
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
   - `Part M of the Building Regulations 2010 (England)` (socket
     mounting height).

   **Banned tokens — do NOT cite anywhere in skill output:** `§526.2`
   (sub-clause not transcribed in verified file), `§433.2` (sub-clause
   not transcribed in verified file), `OZEV` (do NOT cite — operational
   policy, not a BS standard), `3rd Edition` of any IET CoP (do NOT
   cite — superseded), `Reg 559` (do NOT cite — not the ring continuity
   regulation, and this is banned regardless of context).

2. **`§411.3.3` cited only in RCD-posture context.** The verified-citations
   discipline restricts `§411.3.3` to the RCD-posture regulation; it is
   not used as a general additional-protection citation elsewhere in
   this IR.

3. **Engineering-judgment xy coordinates on `ring_endpoints`.** The
   `endpoint_a_xy` (200, 200) values represent the CU origin and the
   `endpoint_b_xy` values (8500, 200) and (7200, 200) represent the
   design-anticipated return points on the perimeter. They satisfy the
   IR schema requirement (`mcb_way_id` matching + `continuity_verified =
   true`) without representing as-installed survey coordinates. The
   `compliance_summary.assumptions[3]` records this explicitly.
   Engineer-of-record substitutes project-specific install coordinates
   from the first-fix wiring survey before final design freeze.

4. **Engineering-judgment FCU downstream load.** The 1800 W
   `downstream_loads_w` value on `C01 fcu_spurs[0]` is chosen as a
   realistic worst-case for a kitchen under-cabinet extractor hood;
   `compliance_summary.assumptions[4]` records the source. The
   manufacturer datasheet supplies the actual nameplate value at the
   install side; if it differs by more than ±10 % the FCU rating may
   need to be re-evaluated against the INV-17 ceiling.

---

## Pair-with-VIOLATION-example (Sprint D4 Phase C.9)

This PASS example is authored as the FIRST half of a PASS / FAIL pair.
The companion VIOLATION example
(`uk-3bed-with-ring-continuity-VIOLATION`) ships in the same Phase C
batch with:

- Same 3-bed dwelling geometry (same rooms, same supply, same parent
  CU).
- `C02` ring authored with `endpoint_a_xy.mcb_way_id = "CU-MAIN-WAY-2"`
  but `endpoint_b_xy` landing at `CU-MAIN-WAY-7` (a wrong way — the
  engineer terminated the return conductor at the wrong slot).
- `continuity_verified: false` on `C02` to model the realistic install
  defect.
- `INV-14 FAIL HIGH` on `C02` evidence stating both `mcb_way_ids` + the
  ring continuity broken.
- `compliance_summary.compliant: false` with one non-compliance flag
  citing IET OSG §8.4.4 + remediation hint
  "engineer-of-record reterminates `endpoint_b` at `CU-MAIN-WAY-2` to
  restore ring continuity".

The eval harness (`eval-10-ring-continuity.yaml`) consumes both fixtures
and asserts `INV-14` PASS on this fixture + `INV-14` FAIL on the
VIOLATION fixture.
