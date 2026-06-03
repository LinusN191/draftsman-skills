# UK NHS Operating Theatre — Medical IT Isolation Sockets with §710 Cascade (small-power Part-7 exercise)

## Why this example exists

Sprint D4 Phase C.2 binding condition: extend small-power's special-locations
cascade proof beyond §701 bathrooms and §702 pools into §710 Group 2 medical
locations, AND close the producer↔consumer integrity loop with the cascade
fixture that special-locations sprint C.2 authored AS IF a small-power Group 2
medical consumer existed at the time.

The fixture lives at
`electrical/special-locations/examples/cascade-small-power-uk-medical-group-2-isolation/intent-out.json`.
At producer-side C.2 it was authored without a downstream consumer; this
small-power C.2 example now creates that consumer, byte-identical to the source
payload — closing the loop.

The example fires INV-12 against the §710 cascade payload and exercises:

- the `patient_1` anchor-driven 1-zone derivation
  (`zone_patient_1_envelope_g2`, 12-sided polygon approximation of the 1.5 m
  radius patient cylinder),
- the `medical_it_system` electrical constraint (5 kVA isolating transformer,
  IMD per BS EN 61557-8 with ≤8 s alarm, HTM 06-01 NHS precedence, safety
  service category 1),
- the `supplementary_equipotential_bonding` constraint (≤0.2 Ω measured at the
  bonding terminal, conductor ≥4 mm²), and
- the **no-RCD posture** mandated by §710 (top-level) on Medical IT system
  circuits — the IT topology + IMD provide first-fault tolerance, an RCD would
  defeat continuity-of-supply on a first earth fault.

`room_type = "medical_group_2_theatre"` is selected as the exact-match Part-7
enum literal so the schema's `allOf` clause for
`consumed_intents.special_locations_zoning` presence fires structurally and the
validator's INV-12 fires semantically.

## Room context — UK NHS operating theatre (Group 2)

A 6.0 m × 5.0 m × 3.0 m operating theatre containing:

- a single patient position centred at room-local (3000, 2500),
- a 1.5 m-radius patient envelope encoded as a 12-sided regular polygon
  approximation (height 0–2500 mm),
- supplementary equipotential bonding terminal ≤0.2 Ω (measured 0.15 Ω),
- six BS EN 60884-1 isolation-monitored 230 V sockets mounted on the theatre
  walls at 1000 mm AFFL — 3 on the north wall (C01), 2 on the west wall (C02),
  1 on the east wall (C03), all fed from the DB-MED-IT-1 5 kVA isolating
  transformer, and
- no general-purpose 230 V sockets (the prohibited `socket_230v_non_medical`
  literal is not present).

The operating-table life-support sockets (Category 1 no-break, UPS-backed per
HTM 06-01) are engineer-of-record scope and intentionally **NOT** modelled in
this small-power IR — the UPS/IPS coordination belongs to a dedicated UPS/IPS
skill.

## Cascade prerequisite — what special-locations told us

`consumed_intents.special_locations_zoning.payload` carries the full upstream
contract, byte-identical to the producer-side fixture source:

- **1 zone** derived from the `patient_1` anchor:
  - `zone_patient_1_envelope_g2` — Group 2 patient envelope, 12-sided polygon
    approximation of the 1.5 m-radius cylinder, height 0–2500 mm, IPx4 minimum,
    230 V permitted, `rcd_required_ma = null` (NO RCD — Medical IT system
    mandated instead per §710), `prohibited_fixture_types =
    [socket_230v_non_medical, switch_230v_non_medical, tnc_circuit]`.
- **2 electrical constraints**:
  1. `medical_it_system`: isolating transformer 5 kVA, IMD per BS EN 61557-8
     with 8 s alarm response, safety service category 1, supplementary bonding
     ≤0.2 Ω, hospital_precedence = HTM 06-01, equipment_standard =
     BS EN 60601 series.
  2. `supplementary_equipotential_bonding`: ≤0.2 Ω measured, bonding extends to
     operating table frame, anaesthesia machine ground, scrub sink, surgical
     pendant arm, patient monitor chassis. Conductor CSA ≥4 mm².
- `compliant = true`, `non_compliance_flags = []`.

The cascade source path is:
`electrical/special-locations/examples/cascade-small-power-uk-medical-group-2-isolation/intent-out.json`.

**Integrity-loop closure.** Unlike the pool-hall C.1 example (which reuses a
lighting-layout-anchored cascade via the anchor-driven engineering-equivalence
argument), this consumer reuses a cascade authored specifically FOR a
small-power Group 2 medical consumer. Producer-side sprint C.2 authored the
fixture AS IF this consumer existed; consumer-side sprint C.2 (this example)
creates that consumer. The payload is byte-identical — no
engineering-equivalent reuse argument is needed.

## §710 top-level-only citation pattern

`§710` is cited **at top-level only** per the D4 sprint spec verified-citations
list. The verified file lists `§710` (top-level) and **no §710 sub-clauses**.
The cross-reference `§701.415.2` is cited only for supplementary bonding (a
deliberate §701-cross-reference path used by the cascade's
`_clause_citation` field on the supplementary bonding constraint).

The cascade source's own `_derivation_note` on the medical_it_system constraint
makes this explicit:

> Medical IT system required for the Group 2 patient envelope per §710 (no
> Part 7 sub-clauses valid; §710 top-level only).

That discipline is preserved verbatim through the consumed_intents payload and
honoured throughout the small-power IR's compliance_summary +
rationale + invariants. The IMD-alarm 8 s threshold is cited from
**BS EN 61557-8**, not from a §710 sub-clause. HTM 06-01 is cited as the
governing NHS technical memorandum (not as a BS 7671 sub-clause). The
sub-clauses banned by D4 spec §3.2 (§710.413.1.5, §710.314, §710.411.3.3, etc.)
are nowhere in the file.

## Socket placement decisions

The design ships zero `socket_230v_non_medical` outlets (the prohibited literal
named by the cascade's zone polygon). The theatre carries exactly six
`BS_EN_60884_1_isolation_monitored_socket_230V` sockets — the explicit
medical-isolation-socket literal that the cascade authors deliberately left
**out** of the prohibition list to permit this exact installation pattern.

1. `theatre-S01`: north wall, C01.
2. `theatre-S02`: north wall, C01.
3. `theatre-S03`: north wall, C01.
4. `theatre-S04`: west wall, C02.
5. `theatre-S05`: west wall, C02.
6. `theatre-S06`: east wall, C03.

All at 1000 mm AFFL — convenient height for surgical equipment plug-in
(above worktop / instrument trolley level, below shoulder height). All within
the 1.5 m patient envelope polygon (deliberately — that is exactly where
surgical equipment is plugged in).

Type literal `BS_EN_60884_1_isolation_monitored_socket_230V` is distinct from
`socket_230v_non_medical`. Even strict literal-match against the
`prohibited_fixture_types` list passes in favour of the design.

## Circuit topology + RCD posture

Three dedicated_radial circuits — one per wall:

- **C01 — North wall (3 sockets).** 16 A Type B MCB + 2.5 mm² + 2.5 mm² CPC
  PVC T+E, 14 m run. Diversified load 6.5 A. `rcd_type = none`. No RCD per
  §710 (top-level).
- **C02 — West wall (2 sockets).** 16 A Type B MCB + 2.5 mm² + 2.5 mm² CPC PVC
  T+E, 11 m run. Diversified load 6.5 A. `rcd_type = none`.
- **C03 — East wall (1 socket).** 16 A Type B MCB + 2.5 mm² + 2.5 mm² CPC PVC
  T+E, 9 m run. Diversified load 4.3 A. `rcd_type = none`. Reserved capacity
  for ancillary surgical equipment.

**Why no RCD?** §710 (top-level) prohibits RCDs on Medical IT system circuits.
The IT topology + IMD (per BS EN 61557-8 with ≤8 s alarm response) provide the
first-fault tolerance. An RCD would defeat continuity-of-supply on the first
earth fault, which is precisely what the Medical IT system is designed to
allow — fault detection without supply interruption, so the surgical team can
finish the procedure while maintenance investigates. The IMD alarm signal
terminates at the theatre control panel AND the nurse-station annunciator,
giving staff an audible + visual warning that a first earth fault has occurred.

**Why three radials instead of one ring?** Operating-theatre design philosophy
prioritises socket-availability redundancy. Splitting by wall isolates a
faulted wall's sockets without disabling sockets on adjacent walls — critical
in an OR where partial socket availability is preferred over total loss of
socket supply. The 6-socket diversified load (≈17.3 A combined) sits
comfortably within the 3 × 16 A radial capacity (48 A).

**CPC sized equal to phase (2.5 mm² CPC on 2.5 mm² phase).** Larger CPC
supports the supplementary equipotential bonding network's parallel-path
equipotentialisation per §710 + §701.415.2 (cross-ref). The bonding terminal at
≤0.2 Ω ties operating table frame, anaesthesia machine, scrub sink, surgical
pendant, and patient monitor chassis through the CPC network.

## supply_origin schema enum constraint

`supply_origin.system_type = "TN-C-S"` records the **upstream building supply
origin** per the schema enum (which does not enumerate IT as a building-supply
value — IT is a downstream local-arrangement property). The Medical IT system
is the LOCAL arrangement downstream of the DB-MED-IT-1 isolating transformer,
derived from the TN-C-S upstream supply via the 5 kVA isolating transformer.
The IT-system topology is captured via:

- `consumed_intents.special_locations_zoning.payload.electrical_constraints[0]`
  (constraint_type = medical_it_system),
- `compliance_summary.non_compliance_flags[0]` (info-severity cascaded
  constraint summary), and
- each circuit's
  `rcd_posture = no_rcd_required_in_medical_it_system_per_§710_top_level`.

The Zs-interpretation note in `compliance_summary.non_compliance_flags[3]`
records that IT-system Zs interpretation differs from TN — first-fault
impedance is reported by the IMD rather than tripping an OCPD; §710 top-level
defers continuity-on-first-fault to the IT topology, so the canonical TN-style
Zs check applies only to the OCPD breaking-capacity coordination
(not to disconnection time).

## INV-12 cascade evidence (4 sub-checks walked)

The validator's INV-12 evidence string (≤800 chars per IR schema cap):

> Cascade source: electrical/special-locations/examples/cascade-small-power-uk-medical-group-2-isolation/intent-out.json (producer-side fixture — integrity-loop closure).
> Sub-check 1 PASS (consumed_intents.special_locations_zoning present).
> Sub-check 2 PASS (payload.compliant=true, 1 zone zone_patient_1_envelope_g2, 2 constraints medical_it_system + supplementary_equipotential_bonding, 0 flags).
> Sub-check 3 PASS — walked sockets: all 6 theatre sockets are BS_EN_60884_1_isolation_monitored_socket_230V (distinct from prohibited socket_230v_non_medical literal); the cascade authors deliberately specified the non-medical sub-literal to permit medical-isolation sockets in the Group 2 envelope.
> Sub-check 4 PASS — payload.non_compliance_flags=[]; nothing to cascade.
> BS 7671:2018+A2:2022 §710 + BS EN 61557-8 + HTM 06-01.

Walking each sub-check explicitly:

1. **Sub-check 1 — cascade present.**
   `consumed_intents.special_locations_zoning.payload` is populated with
   `intent_version = 1.0.0`, source_path pointing at the producer-side fixture,
   and the full payload byte-identical to the source. The schema's `allOf`
   clause for `room_type = medical_group_2_theatre` is satisfied.
2. **Sub-check 2 — upstream compliant.** `payload.compliant == true`. The
   single zone is well-formed (12-sided polygon, centred at the patient
   anchor). Both electrical constraints are well-formed — medical_it_system
   has all required fields populated (5 kVA, IMD true, 8 s alarm, Cat 1,
   bonding ≤0.2 Ω, HTM 06-01 precedence, BS EN 60601 equipment standard);
   supplementary_equipotential_bonding has 5 metallic parts listed and a
   4 mm² conductor CSA floor.
3. **Sub-check 3 — socket/zone cross-walk.** All 6 theatre sockets sit within
   the patient envelope polygon (that's the design intent — surgical equipment
   is plugged in inside the envelope). Each socket's type literal is
   `BS_EN_60884_1_isolation_monitored_socket_230V`, distinct from the cascade's
   prohibited `socket_230v_non_medical` literal. The cascade authors
   deliberately specified the `_non_medical` sub-literal to permit
   medical-isolation sockets in the envelope — pattern-match against the
   prohibition list passes in favour of the design.
4. **Sub-check 4 — flag cascading.** `payload.non_compliance_flags[]` is
   empty. Nothing to cascade. The `compliance_summary.non_compliance_flags[]`
   entries present in this IR are all `severity: info` design /
   engineering-judgment notes (cascaded constraint summaries + HTM 06-01
   precedence note + Zs-deferral note) — not cascaded failures, so no
   `_cascaded_from` attribution is required.

All four sub-checks resolve PASS. INV-12's IR record carries
`{id: "INV-12", passes: true, severity: "high", evidence: "…"}`.

## INV-13 through INV-19 walk-through

- **INV-13 (building_diversity self-consistency, LOW/N-A)** —
  `building_diversity` is intentionally absent. The validator's INV-13 wording
  explicitly resolves to "N/A and trivially PASS when absent (input not
  supplied)". This example's engineering scope is the §710 cascade + IT-system
  no-RCD posture + supplementary bonding + integrity-loop closure;
  building-wide demand calculation is out of scope (covered by Phase A/B
  examples).
- **INV-14 (ring continuity, HIGH/N-A)** — no circuit has `topology = ring`.
  All 3 circuits are dedicated_radial. The ring-endpoints continuity rule
  (TOP-09) evaluates only on ring topology circuits; with zero rings in this
  IR, no ring continuity check applies.
- **INV-15 (per-circuit floor-area cross-check, HIGH/N-A)** —
  `circuit.floor_area_m2` is not populated on any circuit (the v2.0 field is
  optional). INV-15 only evaluates when both `floor_area_m2` AND
  `rooms_covered[]` are populated; absent the former, no Σ-tolerance
  reconciliation is computed.
- **INV-16 (OCPD-topology coordination, HIGH)** — all 3 circuits are
  dedicated_radial 16 A on 2.5 mm² + 2.5 mm² CPC PVC T+E. Validator INV-16
  wording explicitly says `topology = dedicated_radial → MCB sized by
  connected load per §433.1.1 (cable-sizing's domain; INV-16 trivially PASSES
  on dedicated_radial)`. Connected-load coordination: 6.5 A (C01) / 6.5 A
  (C02) / 4.3 A (C03) diversified << 16 A MCB << 2.5 mm² Iz reference
  rating.
- **INV-17 (FCU spur modelling, MEDIUM/N-A)** — no circuit has `fcu_spurs[]`
  populated. BS EN 60884-1 medical isolation sockets are direct-circuit-fed
  (medical-grade installation practice avoids FCUs on Medical IT circuits
  because the FCU fuse would interrupt the continuity-on-first-fault property
  of the IT system).
- **INV-18 (EV RCD type, HIGH/N-A)** — no circuit has `load_type` matching
  `ev_charge_*`. All 3 circuits are general medical-isolation socket radials.
  INV-18 only evaluates on EV-charge circuits where `ev_charge_metadata` and
  `rcd_type ↔ charging_unit_dc_detection_a` are present.
- **INV-19 (cable-sizing + building_diversity cascade, MEDIUM/N-A)** —
  neither `building_diversity.per_circuit_demand_inputs[]` nor
  `consumed_intents.cable_sizing.payload.circuits[]` is present. The
  reconciliation rule (post_per_load_diversity_a ≈ design_current_a ±5 %)
  has nothing to reconcile.

All 19 INVs emit; INV-12 + INV-16 PASS as genuine PASSes; INV-13/14/15/17/18/19
PASS as N/A-vacuous; INV-01 through INV-11 PASS as genuine PASSes against the
baseline small-power rules (INV-01 trivially PASSes on the absence of ring
topology). Zero FAILs.

## Honest disclosures (4-place)

The D.4 special-locations cascade pattern requires the cascade-source REUSE +
integrity-loop closure to be disclosed in four places — this example places
the disclosure as follows:

1. **`input.json._cascade_disclosure`** — explicit human-readable narrative
   naming the producer-side fixture and the integrity-loop closure argument.
2. **`output.json.compliance_summary.assumptions[6]`** — engineering
   assumption recording the integrity-loop closure relationship + the
   byte-identical payload reuse (no engineering-equivalent argument needed,
   unlike pool-hall C.1).
3. **`output.json.rationale.sections[6]` (Honest disclosures section)** —
   narrative summary in the chat-visible rationale exposing the cascade
   reuse, the §710 sub-clause coverage discipline (top-level only +
   §701.415.2 cross-ref + BS EN 61557-8 / HTM 06-01 for non-§710 facts), and
   the operating-table-life-support out-of-scope note.
4. **`reasoning.md` (this file) "Cascade prerequisite — Integrity-loop
   closure", "§710 top-level-only citation pattern", and "Honest disclosures
   (4-place)" sections** — long-form engineering walkthrough making the
   reuse, the citation discipline, and the UPS/IPS skill boundary explicit.

Additional disclosures captured in `compliance_summary.assumptions[]`:

- **supply_origin enum constraint** (assumption #0) — the schema's
  `supply_origin.system_type` enum does not enumerate `IT` as a
  building-supply value; the IT topology is a local arrangement downstream
  of the isolating transformer, captured via the cascade constraint +
  compliance_summary.non_compliance_flags[0] + circuit `rcd_posture`.
- **Patient envelope geometry** (assumption #1) — 1.5 m-radius cylinder
  around the patient_1 anchor encoded as a 12-sided regular polygon
  approximation per the cascade's source `_derivation_note`.
- **BS EN 60884-1 socket selection** (assumption #2) — built-in isolation
  monitoring and interlock per §710 Medical IT system requirements; the
  type literal is distinct from the cascade's prohibited
  `socket_230v_non_medical` literal.
- **5 kVA isolating transformer** (assumption #3) — within the
  3.15–8 kVA plausibility band per the cascade's D-4 reviewer judgment (no
  flag raised); covers the 6-socket × 16 A diversified profile with
  comfortable headroom.
- **Supplementary bonding ≤0.2 Ω** (assumption #4) — measured 0.15 Ω at the
  bonding terminal; bonding scheme documented on the earthing-and-bonding
  drawing (out of scope for this IR).
- **Operating-table life-support sockets** (assumption #5) — engineer-of-record
  scope, Cat-1 no-break UPS-backed per HTM 06-01; belongs to the UPS/IPS
  skill, NOT small-power.
- **Cascade source integrity-loop closure** (assumption #6) — byte-identical
  payload reuse from the producer-side fixture; closes the producer↔consumer
  loop.
- **v2.0 retrofit context** (assumption #7) — NEW v2.0.0 example, no v1.x
  retrofit; all 3 circuits are dedicated_radial so no ring_endpoints fields
  are required (the v2.0 ring_endpoints allOf clause is satisfied vacuously).
- **INV-13/19 N-A scope discipline** (assumption #8) — making the intentional
  absence of `building_diversity` explicit.
- **INVs 14/15/17/18 N-A scope discipline** (assumption #9) — making the
  intentional absences of ring topology, floor_area_m2, fcu_spurs[], and
  ev_charge_metadata explicit.

## Standards cited

Only the verified citations per the small-power v2.0.0 D4 sprint spec §2.3
verified table:

- **BS 7671:2018+A2:2022 §710 (top-level)** — Special Installations or
  Locations: medical locations. No §710 sub-clauses are transcribed per the
  spec verified-citations discipline.
- **BS 7671:2018+A2:2022 §701.415.2** — supplementary equipotential bonding
  (the §701 cross-reference path used by the cascade's
  supplementary_equipotential_bonding constraint).
- **BS 7671:2018+A2:2022 §411.4.5** — earth fault loop impedance limits (Zs
  deferred to calc.zs_loop_impedance per WI3; cross-referenced only for the
  TN-style canonical interpretation, not for the IT-system first-fault
  scenario which §710 top-level defers to the IT topology).
- **BS 7671:2018+A2:2022 §433.1.1** — overcurrent protection coordination
  with cable current-carrying capacity (used by INV-16).
- **BS 7671:2018+A2:2022 §434.5.1** — breaking capacity of OCPDs ≥
  prospective fault current (used by INV-02).
- **BS EN 61557-8** — Insulation Monitoring Devices for IT systems — defines
  the IMD performance requirements including the 8 s alarm response
  threshold.
- **BS EN 60884-1** — plugs and socket-outlets for household and similar
  purposes — selected for the medical-isolation socket type with built-in
  isolation monitoring interlock.
- **BS EN 60601 series** — medical electrical equipment (device-side
  standard for equipment that plugs into the sockets).
- **BS EN 60898-1** — circuit breakers for overcurrent protection of
  household installations (curve B selection for surgical equipment loads
  with no significant inrush).
- **HTM 06-01** — NHS Health Technical Memorandum for electrical services
  supply and distribution — governs NHS safety-service categorisation
  (Category 1 no-break for life-support; this example deliberately stays out
  of Cat-1 scope and addresses only the Medical IT system general sockets).
- **BS 1192:2007+A2:2016** — drawing-management conventions (sheet size A2,
  scale 1:50).
- **IET On-Site Guide Appendix A** — diversity factors for general-purpose
  sockets (surgical-equipment-plug-in profile).

## Validator outcome

All 19 INVs emit; all PASS:

| INV    | Severity | Result |
|--------|----------|--------|
| INV-01 | high     | PASS (no ring topology — trivially PASS) |
| INV-02 | high     | PASS (breaking capacity 10 kA ≥ PFC 6 kA on all 3 circuits) |
| INV-03 | high     | PASS (rcd_posture documents §710 no-RCD displacement of §411.3.3 default) |
| INV-04 | high     | PASS (Part-7 socket placement — medical-isolation type literal distinct from prohibited non-medical literal) |
| INV-05 | high     | PASS (circuit topology + socket→circuit_id refs) |
| INV-06 | low      | PASS (Type B on all 3 — no motor / no inrush) |
| INV-07 | high     | PASS (diversified load < breaker rating on every circuit) |
| INV-08 | high     | PASS (Zs deferred to calc tool per WI3) |
| INV-09 | high     | PASS (theatre_1 appears in all 3 rooms_covered; all 6 sockets in theatre_1) |
| INV-10 | low      | PASS (BS 1192 drafting standard matches GB jurisdiction) |
| INV-11 | high     | PASS (no cable-sizing intent consumed — no-op) |
| INV-12 | high     | PASS (4-sub-check §710 cascade walk above — integrity-loop closure) |
| INV-13 | low      | PASS (N/A — building_diversity absent) |
| INV-14 | high     | PASS (N/A — no ring topology) |
| INV-15 | high     | PASS (N/A — circuit.floor_area_m2 not populated) |
| INV-16 | high     | PASS (3 × dedicated_radial 16 A on 2.5 mm² — trivial PASS) |
| INV-17 | medium   | PASS (N/A — no fcu_spurs[]) |
| INV-18 | high     | PASS (N/A — no EV-charge circuit) |
| INV-19 | medium   | PASS (N/A — no building_diversity AND no cable-sizing intent) |

The IR validates against
`electrical/small-power/schemas/small-power-ir.schema.json` including the
`allOf` Part-7 trigger clause (room_type = medical_group_2_theatre forces
`consumed_intents.special_locations_zoning` presence) AND the v2.0
ring-endpoints allOf clause (vacuously satisfied because no circuit has
topology = ring). The downstream-facing intent extraction in
`intent-out.json` validates against `small-power-intent.schema.json` and
carries the cascade payload through `consumed_intents.special_locations_zoning`
for any further consumer.
