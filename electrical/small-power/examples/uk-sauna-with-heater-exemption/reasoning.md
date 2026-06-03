# UK Domestic Sauna Room — Heater Documented §411 Exception + Standard §411.3.3 Control Panel (small-power D4 depth exercise)

## Why this example exists

Sprint D4 Phase C.4 binding condition: exercise the
`no_rcd_with_documented_§411_exception` value on the `rcd_posture` enum
and the companion `rcd_exception_citation` field on a realistic UK
domestic sauna installation, AND demonstrate that the §411 exception is
NARROW — equipment-specific equipment-side carve-outs do NOT propagate
to sibling circuits in the same Part-7 room.

The canonical engineering point of the example: two distinct
`rcd_posture` values coexist in the same Part-7 §703 sauna room.

- C01 (sauna heater) takes `no_rcd_with_documented_§411_exception` with
  `rcd_exception_citation` populated.
- C02 (sauna control panel) takes `type_a_30ma_per_§411_3_3` — the
  standard sibling-circuit posture per `§411.3.3`.

The §411 exception is NOT a room-wide exemption; it is the
appliance-specific carve-out the verified standards file records:

> "30 mA RCD on all sauna circuits except the heater (Reg 703.411.3.3)"

This is the C.4 brief's `rcd_exception_citation` content — the heater is
the canonical example because `BS EN 60335-2-53` (Particular requirements
for sauna heating appliances) certifies the equipment-side fault-current
characteristics that make 30 mA RCD discrimination impractical without
nuisance trips.

## Scenario at a glance

- UK domestic sauna room (prefabricated 2.4 × 2.0 × 2.4 m timber cabin)
  on a typical TN-C-S domestic supply (`Ze = 0.35 Ω`, `PSCC = 6 kA`).
- Hard-wired 6 kW single-phase `BS EN 60335-2-53` sauna heater.
- Two dedicated radial circuits:
  - **C01 sauna heater radial** — 32 A Type C MCB on heat-rated
    silicone-insulated `4 mm² + 4 mm² CPC` cable (schema-pinned to `EPR`
    as the closest enum approximation; engineer-of-record substitutes
    silicone manufacturer part number at procurement). No RCD per the
    documented `§411` exception.
  - **C02 sauna control panel radial** — 6 A RCBO Type B + Type A 30 mA
    on standard `1.5 mm² T+E PVC` cable. Control panel mounted on the
    EXTERNAL face of the changing-room wall per the verified `§703` key
    requirement that all control gear must sit OUTSIDE the sauna.
- Zero 230 V sockets inside the sauna cabin per the verified `§703`
  key requirements (the heater supply is the only cable permitted
  through the sauna walls).

## Room layout

| Room        | room_type | Dimensions          | special_location | Notes                                               |
| ----------- | --------- | ------------------- | ---------------- | --------------------------------------------------- |
| sauna_cabin | `sauna`   | 2.4 × 2.0 × 2.4 m   | `null`           | Prefab timber cabin; 0 sockets; heater hard-wired   |

The `sauna_cabin.room_type = "sauna"` literal is the Part-7 enum trigger
for the schema's `allOf` clause. The `special_location` field is set to
`null` because the schema's `special_location` enum carries only
`{bathroom_zone_*, outdoor, wet_area}` — no `sauna_zone_*` literals. The
§703 zoning is carried entirely by the cascade payload (`zones[]` array).

## Circuit topology

| Circuit | Designation                                | Topology         | OCPD                | Cable                                       | rcd_posture                                       |
| ------- | ------------------------------------------ | ---------------- | ------------------- | ------------------------------------------- | ------------------------------------------------- |
| C01     | Sauna heater (BS EN 60335-2-53 hard-wired) | `dedicated_radial` | 32 A Type C MCB     | 4 mm² + 4 mm² CPC silicone (EPR pin)        | `no_rcd_with_documented_§411_exception`           |
| C02     | Sauna control panel (door-switch interlock) | `dedicated_radial` | 6 A RCBO Type B    | 1.5 mm² T+E PVC                            | `type_a_30ma_per_§411_3_3`                        |

Both circuits are `dedicated_radial`. Neither is a ring final circuit
(no `ring_endpoints` block), neither carries `fcu_spurs[]`, neither
populates `ev_charge_metadata`.

## `rcd_exception_citation` content — the canonical C.4 demonstration

The C01 `rcd_exception_citation` field carries three distinct components
that together compose the full §411 documented-exception safety case:

1. **`§703.411.3.3` heater-exclusion language** (install-side, verified
   standards file). The C.4-permitted §703 sub-clause that the verified
   standards file at
   `shared/standards/electrical/BS7671/part7-special-locations.json`
   records verbatim under the §703 `key_requirements` block: `"30 mA RCD
   on all sauna circuits except the heater (Reg 703.411.3.3)"`.
2. **`§411` top-level documented-exception path** (install-side). The
   `§411` Section provides the general-rule framework that the §703
   sub-clause carves out from.
3. **`BS EN 60335-2-53`** (equipment-side appliance standard). The
   Particular requirements for sauna heating appliances. The appliance
   type-test certifies the equipment-side safety integrity required for
   the §411 documented-exception path — without the appliance-side
   certification, the install-side exception is not available.

`HD 60364-7-703` (CENELEC harmonisation reference for §703) is cited in
`drawing_notes` as the harmonisation pointer; the BS 7671 install side
is the operative regulation in GB jurisdiction.

The validator prompt's INV-06 sub-rule 3 wording demands "explicit
BS 7671 §411 / IEC 60364-4-41 §411 reference"; the citation above
satisfies the BS 7671 §411 reference cleanly.

## Why the heater takes the §411 exception (equipment-side rationale)

BS EN 60335-2-53 sauna heating appliances use **low-resistance heating
elements** that exhibit cold-start fault-current characteristics:

- At cold start, the element's resistance is below its steady-state
  resistance (positive temperature coefficient of resistance).
- The initial inrush current can be several times the steady-state
  26.1 A design current.
- Earth-fault currents during this transient can exceed a 30 mA RCD's
  nuisance-trip threshold (RCD tripping bands are typically 50–100% of
  rated sensitivity per BS EN 61008-1).
- A 30 mA RCD installed upstream of the heater would therefore trip on
  every cold-start cycle — incompatible with the heater's intended
  operating profile.

The §411 documented-exception path is the regulated answer: with the
appliance-side BS EN 60335-2-53 type-test certifying the equipment's
safety integrity AND the install-side §703.411.3.3 heater-exclusion
language permitting the carve-out, the design is permitted to omit the
upstream 30 mA RCD provided the §411.4.5 disconnection-time table is
satisfied entirely by the OCPD characteristic at the prospective fault
current (no RCD additional-protection backstop).

The 32 A Type C MCB on a 6 m run of 4 mm² + 4 mm² CPC with declared
`Ze = 0.35 Ω` is **provisionally** within the §411.4.5 0.4 s
domestic-final disconnection envelope; the formal verification is
deferred to `calc.zs_loop_impedance` per WI3 (`tool_call_pending_for_zs_verification = true` on C01).

## Why the control panel keeps the standard §411.3.3 posture

C02 is a **low-current control circuit** (0.5 A diversified at 0.05 kW
design load). The control panel houses:

- a timer/thermostat with door-switch interlock,
- the relay or contactor that switches the heater supply,
- low-voltage SELV signalling for the door switch (out of scope for the
  small-power IR which captures only the 230 V control panel supply).

Critically, C02's load envelope is **well below the heater's
fault-current characteristic** and does NOT exhibit the heater's
nuisance-trip behaviour. The standard §411.3.3 30 mA Type A RCD posture
applies cleanly — there is no equipment-side rationale to invoke the
§411 exception.

This is the **two-posture coexistence** point: the §411 exception is
specifically for the equipment that cannot tolerate 30 mA RCD
discrimination; sibling circuits in the same Part-7 room — even circuits
serving the same physical room — still take the standard §411.3.3 path.

## §703 key requirements respected in the design

The verified standards file's §703 `key_requirements` block lists five
discrete requirements. The example respects all five:

| Requirement | Compliance in this design |
| ----------- | ------------------------- |
| Cables must be rated for sauna temperatures (typically 170°C in zone 1) — silicone insulated or equivalent | C01 cable spec'd as silicone-insulated; schema-pinned to EPR as closest enum approximation; designation text + assumptions + drawing_notes carry the silicone discipline forward |
| Light fittings: IPx4 minimum, T-rated for ambient up to 125°C | Out of scope (no luminaires in this small-power IR; lighting-layout owns this) |
| 30 mA RCD on all sauna circuits except the heater (Reg 703.411.3.3) | C01 (heater) takes the §411 exception; C02 (control panel) takes 30 mA Type A per §411.3.3 — both circuits respect the verified language |
| All control gear OUTSIDE the sauna | C02's control panel mounted on the EXTERNAL face of the changing-room wall; C01's MCB lives in CU-MAIN (outside the cabin); door-switch interlock is the only sensor inside |
| Only the sauna heater supply may pass through the sauna walls | C01 enters via heat-rated silicone cable terminating directly at the heater appliance terminals; C02 terminates at the external control panel (does NOT enter the cabin) |

## Cable selection — schema-pinned to EPR (closest approximation to silicone)

The C01 cable enters sauna_zone_1 where the §703 ambient routinely sits
at 170°C. Silicone-insulated heat-rated cable is the engineering
choice. The small-power IR schema's `insulation` enum is
`{PVC_70, XLPE_90, EPR}`:

- `PVC_70` — 70°C continuous; would fail at 170°C.
- `XLPE_90` — 90°C continuous; would also fail at 170°C.
- `EPR` (ethylene propylene rubber, elastomeric, heat-resistant to ~150°C)
  — closest approximation to the silicone install but not a direct match.

The IR carries the silicone discipline in three orthogonal places to
guard against the enum-pinning approximation losing engineering content:

1. `cable.csa_mm2_or_awg` designation text records the silicone
   discipline verbatim (`"4mm² + 4mm² CPC silicone-insulated (heat-rated
   for §703 Zone 1 ambient up to 170°C)"`).
2. `compliance_summary.assumptions[]` records the schema-pinned
   approximation with engineer-of-record substitution at procurement.
3. `drawing_notes[]` repeats the silicone discipline for the runtime to
   render on the as-drawn legend.

Engineer-of-record substitutes the manufacturer's silicone cable part
number (typical UK products: Pyrosil, Silofex, Olflex SiHF) at
procurement; the IR carries the heat-rated discipline forward.

## Cascade prerequisite (special-locations payload) — DEFERRED-POINTER state

`room_type = "sauna"` is the Part-7 enum trigger for the schema's
`allOf` clause requiring `consumed_intents.special_locations_zoning`.
INV-12 then fires the 4 sub-check sequence.

The cascade source path
`electrical/special-locations/examples/cascade-small-power-uk-sauna-heater-exemption/intent-out.json`
points to a producer-side fixture that **does NOT yet exist at C.4-ship**.

D.1 of the Phase D dispatch builds
`cascade-small-power-uk-sauna-heater-exemption/` (4 files) AFTER C.4
ships. At C.4-ship the consumer's
`consumed_intents.special_locations_zoning.payload` is **INLINED with
the payload that D.1 will emit byte-identical**:

- 3 zones (`zone_heater_1_z1` around the heater anchor,
  `zone_heater_1_z2` covering the sauna body polygon,
  `zone_heater_1_z3` above 1500 mm for accessory mounting) per the
  verified §703 zone-table convention.
- 1 `electrical_constraint` of type `rcd_blanket_by_room` with
  `sauna_heater_excluded = true` reflecting the verified §703.411.3.3
  heater-exclusion language.
- `compliant: true`, `zone_count: 3`, `constraint_count: 1`, all
  violation counts 0, `non_compliance_flags: []`.
- `anchor_source_summary.all_extracted: true`,
  `extraction_source_lowest: "architectural_drawing_extraction"`.

At D.1-ship the `source_path` will resolve to a real producer file but
the **payload bytes remain unchanged**. This mirrors the C.3 EV pattern.

The producer-side fixture is functionally identical to the existing
`electrical/special-locations/examples/uk-sauna-with-3-zone-derivation/`
fixture but explicitly tagged as a small-power-consumer cascade source
— the file-tree naming makes the producer-side intent of "this is the
small-power-consumer source" auditable.

## INV-12 cascade walk (4 sub-checks)

| Sub-check | Pass | Notes |
| --------- | ---- | ----- |
| 1 — `consumed_intents.special_locations_zoning` present | PASS | Payload inlined byte-identical to what D.1 will emit. |
| 2 — Payload counts reconcile | PASS | `compliant = true`, `zone_count = 3`, `constraint_count = 1`, all violations 0. |
| 3 — Socket-by-zone gating + zone containment | PASS | Sauna cabin `sockets[] = []`; no sockets to walk against zone polygons. The heater is hard-wired (not a socket) and the control panel sits OUTSIDE the room polygon. Vacuous zone-containment satisfaction. |
| 4 — Flag cascade | PASS | `payload.non_compliance_flags = []`; nothing to cascade. |

The §703 sauna case is the canonical example of a **Part-7 room with
zero sockets** — the design respects the verified §703 key requirement
that the heater supply is the only cable permitted through the sauna
walls. The zone-containment sub-check is vacuous because there is
nothing to walk; the cascade still fires (room_type trigger) and the
INV-12 sequence still satisfies cleanly.

## INV-06 sub-rule 3 walk

INV-06 sub-rule 3 hard-fails when `rcd_posture =
"no_rcd_with_documented_§411_exception"` and `rcd_exception_citation`
is empty or missing. The validator prompt's exact message:

> INV-06 (hard fail): circuit \<C_ID\> rcd_posture=no_rcd_with_documented_§411_exception but rcd_exception_citation is empty or missing. Populate with an explicit BS 7671 §411 / IEC 60364-4-41 §411 reference.

C01 carries the documented-exception posture; the
`rcd_exception_citation` field is populated with the explicit BS 7671
§411 + §703.411.3.3 + BS EN 60335-2-53 reference. INV-06 PASSes
HIGH severity.

C02 carries `rcd_posture = "type_a_30ma_per_§411_3_3"` — sub-rule 1
default; no justification field required.

Neither circuit uses sub-rule 2 (Type B). INV-06 PASSes cleanly on both
circuits.

## INV evaluation — full 19-INV sweep

| INV | Status | One-line evidence |
| --- | ------ | ----------------- |
| INV-01 | PASS (vacuous) | Both circuits dedicated_radial; ring composition rule does not apply. |
| INV-02 | PASS | breaking_capacity_ka = 6.0 = parent_db.pfc_at_busbar_ka on both circuits. |
| INV-03 | PASS | C02 carries §411.3.3 Type A 30 mA; C01 takes the documented-exception path with citation populated. |
| INV-04 | PASS | Sauna cabin sockets[]=[]; no socket-in-zone contradiction possible. |
| INV-05 | PASS | Both circuits rooms_covered=[sauna_cabin]; no orphan rooms; no orphan sockets. |
| INV-06 | PASS | Sub-rule 3 focus invariant: rcd_exception_citation populated on C01; C02 uses sub-rule 1 default. |
| INV-07 | PASS | C01 diversified 26.1 A < 32 A OCPD; C02 0.5 A < 6 A OCPD. |
| INV-08 | PASS | Both carry tool_call_pending_for_zs_verification=true; flags[] carries the TOOL-CALL-PENDING string. |
| INV-09 | PASS | Single room sauna_cabin appears in both circuits' rooms_covered[]. |
| INV-10 | PASS (low) | BS 1192:2007+A2:2016 matches GB jurisdiction; A3 sheet engineer-justified override documented in assumptions. |
| INV-11 | PASS (no-op) | No cable-sizing intent consumed; v1.1 conditional rule no-op. |
| INV-12 | PASS | All 4 sub-checks satisfied (DEFERRED-POINTER cascade; payload inlined). |
| INV-13 | PASS (N/A) | building_diversity intentionally absent. |
| INV-14 | PASS (N/A) | No ring topology circuits. |
| INV-15 | PASS (N/A) | circuit.floor_area_m2 not populated. |
| INV-16 | PASS | Both dedicated_radial; OCPD sized by connected load per §433.1.1; validator INV-16 trivially PASSES. |
| INV-17 | PASS (N/A) | No fcu_spurs[] populated. |
| INV-18 | PASS (N/A) | No ev_charge_metadata; no load_type=ev_charge_*. |
| INV-19 | PASS (N/A) | building_diversity + cable_sizing both absent. |

INV-06 sub-rule 3 + INV-12 are the focus invariants. The N/A
trivially-PASS treatment on INV-13/14/15/17/18/19 follows the validator
prompt's explicit `N/A and trivially PASS` wording for each.

## Honest disclosures

### Verified-citation discipline

Only the C.4 brief's verified-citations list is cited:

- `BS 7671:2018+A2:2022 §703` (top-level — saunas — verified)
- `BS 7671:2018+A2:2022 §703.411.3.3` (the single permitted §703
  sub-clause, mirroring the C.3 §722.531.3.101 precedent — verified
  verbatim in the standards file)
- `BS 7671:2018+A2:2022 §411` and `§411.3.3` (RCD additional
  protection / documented exception path)
- `BS 7671:2018+A2:2022 §411.4.5` (disconnection-time table) — referenced
  for C01's §411 documented-exception safety case
- `BS 7671:2018+A2:2022 §433.1.1` (OCPD sized by connected load on
  dedicated_radial) — referenced in INV-16 evidence
- `BS 7671:2018+A2:2022 §434.5.1` (breaking-capacity ≥ PFC) — referenced
  in INV-02 evidence
- `BS EN 60335-2-53` (sauna heating appliances — particular requirements
  — equipment-side safety case)
- `HD 60364-7-703` (CENELEC harmonisation reference for §703 — pointer
  only)

The C.4 brief explicitly bans the following — each item is a banned
citation we do NOT cite anywhere in this example:

- banned: `§703.55` — do NOT cite (not the heater-exclusion clause)
- banned: `§703.512` — do NOT cite (sub-clause outside the verified scope)
- banned: `§703.413` — do NOT cite (sub-clause outside the verified scope)
- banned: `§526.2` — do NOT cite (inherited 14-sub-clause ban; not
  transcribed in the verified file)
- banned: `§433.2` — do NOT cite (inherited 14-sub-clause ban; not
  transcribed in the verified file)
- banned: `OZEV` — do NOT cite (operational policy; not a BS standard)
- banned: `3rd Edition` (of the IET CoP for EV charging) — do NOT cite
  (superseded; not the sauna regulation anyway)
- banned: `Reg 559` — do NOT cite (not the sauna regulation)

The single permitted §703 sub-clause is `§703.411.3.3` because the
verified standards file records the heater-exclusion language verbatim
under §703 `key_requirements`. This mirrors the C.3 precedent that
permitted §722.531.3.101 as the single §722 sub-clause for the EV
RCD-type-boundary citation.

### DEFERRED-POINTER cascade source

At C.4-ship the `consumed_intents.special_locations_zoning.source_path`
points to a producer-side fixture
(`electrical/special-locations/examples/cascade-small-power-uk-sauna-heater-exemption/intent-out.json`)
that **does NOT yet exist**. D.1 of the Phase D dispatch authors that
fixture AFTER C.4 ships. The inlined payload here is what D.1 will emit
byte-identical.

### Schema-pinned insulation=EPR (closest approximation to silicone)

The engineering-correct cable for C01 is silicone-insulated heat-rated.
The schema `insulation` enum is `{PVC_70, XLPE_90, EPR}`; silicone is
not enumerated. EPR is the closest heat-resistant elastomeric family
and is the schema-pinned approximation. The IR carries the silicone
discipline in `csa_mm2_or_awg` designation text, in `assumptions[]`,
and in `drawing_notes[]`. Engineer-of-record substitutes the
manufacturer's silicone part number at procurement.

### Two-posture coexistence (canonical engineering point)

The example is **deliberately constructed** to demonstrate that the
§411 exception is NARROW — appliance-specific carve-outs do NOT
propagate to sibling circuits in the same Part-7 room. The
`compliance_summary.non_compliance_flags[0]` info-severity message
captures this engineering point for the runtime to surface in the
design review. Without the deliberate two-circuit construction the
example would not exercise the validator's INV-06 sub-rule 3 + sub-rule
1 paths simultaneously.

### Out-of-scope items

- **Sauna luminaires (T-rated, IPx4)** — out of scope for the
  small-power IR; lighting-layout owns this surface.
- **Door-switch interlock SELV signalling** — out of scope; small-power
  captures only the 230 V control panel supply.
- **Heater appliance thermal cut-out** — out of scope; the
  BS EN 60335-2-53 type-test certifies the appliance-side safety
  integrity which is consumed by the IR as a citation, not as an
  install-side IR construct.
- **HD 60364-7-703 vs BS 7671 §703 divergence detail** — pointed at,
  not transcribed; the BS 7671 install side is the operative regulation
  in GB jurisdiction.

### v2.0 retrofit context

This is a **new** v2.0.0 example — no v1.x retrofit. Both C01 and C02
are `dedicated_radial` topology so `ring_endpoints` does not apply to
either circuit. No `fcu_spurs[]` populated. No `ev_charge_metadata`
populated. `building_diversity` intentionally absent.

### Sprint D3 lighting-layout depth context (cross-skill awareness)

The full sauna small-power IR composes with `lighting-layout` for the
T-rated IPx4 luminaire surface (out of scope here) and with the
sibling `cable-sizing` skill for the §411.4.5 Zs verification that C01's
documented-exception path requires. The `tool_call_pending_for_zs_verification = true` flag on both circuits is the cross-skill handoff
marker.
