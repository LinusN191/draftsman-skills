# Reasoning — INT Rural Cottage Earthing Schematic (genuine TT)

> **Sprint C.1 / M2 author note (2026-05-25):** This example is the *genuine* TT
> case that completes the Sprint A.1 cause-fix. The previously misnamed
> `intl-rural-tt/` folder actually contained TN-C-S data and was renamed to
> `intl-rural-tncs/` in Sprint A.1. The TT branch — the **safest** earthing
> branch by intent (RCD on every circuit) — had thorough prompt logic but
> was never exercised by an example. Sprint C.1 / M2 closes that gap by
> authoring this off-grid cottage example at the freed slot.

## Step 1 — Discovery check
No upstream `db-layout` intent — this is a single-board cottage authored
standalone. `meta.consumed_intents` is intentionally empty. Engineer
provides the four-circuit list directly in `input.json` under
`engineering_brief.circuits_summary[]`.

## Step 2 — Standards files to load
Jurisdiction is INT. Loading:
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json`
  (clauses 411.5 / 411.5.3 / 415.1.1 / 531.3.3 — TT system + RCD)
- `shared/standards/electrical/IEC60364/part5-54-earthing.json`
  (clauses 542.3 / 542.4.1 / 543 / Table 54.2)
- `shared/standards/electrical/IEC60364/earthing-systems.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

Also referenced (periodic inspection):
- `IEC 60364-6:2016` §61.3.6 (Ra re-measurement cadence)

BS 7671 and NFPA 70 NOT loaded (not GB, not US). KS 1700 NOT loaded (not KE) —
INV-10 cross-contamination check confirms zero `KS 1700` strings.

## Step 3 — Earthing system classification (TT mandated by site fact)
**Off-grid cottage.** No utility supply → no utility-side neutral-earth bond
→ no TN-arrangement is possible. The PV/battery inverter provides the
single neutral-earth bond at the consumer side, which by IEC 60364-4-41
§411.5 definition makes the system **TT**: source has one
neutral-to-earth bond, exposed-conductive-parts are connected to a
*separate* (consumer-side) earth electrode, and earth-fault current
returns via the earth path between the consumer electrode and the source
electrode (the inverter's earth reference).

This is the **only valid system class** for off-grid in IEC 60364 — there
is no IT alternative that would make sense for a domestic dwelling (IT is
for medical/industrial isolation use cases).

Cross-check `electrical/earthing/ontology/earthing-system-types.json` →
TT is permitted for INT, electrode required, RCD mandatory on every
final circuit.

IR emits: `earthing_system: { system_type: "TT", code_clause: "IEC 60364-4-41:2017 §411.5 (TT system — disconnection by RCD)" }`.

## Step 4 — MET location and MEC
MET at the cottage meter board, kitchen utility area (the only practical
location — the cottage is single-storey 80 m², and the meter board sits
adjacent to the inverter & consumer unit).

- `supply_bond_type: "consumer_electrode_only"` — the schema's three-value
  taxonomy maps the TT off-grid case to this enum (no DNO PME, no TN-S
  separate PE). The single rod electrode E1 is the system's only protective
  earth source.
- Main earthing conductor: 16 mm² Cu — the IEC 60364-5-54 §542.3.1 minimum
  for a Cu MEC that is mechanically protected and corrosion-resistant. There
  is no heavy line conductor to size against (largest final-circuit line is
  2.5 mm²), so the §542.3.1 minimum governs.

## Step 5 — Electrode design (the critical TT decision)

**Single 3 m × 16 mm copper-clad steel driven rod E1**, in sandy loam at
~800 Ω·m soil resistivity.

**Installer-measured Ra = 200 Ω** at handover (dry-season worst case).
This is the engineer-input design value pending `calc.electrode_resistance`
tool execution (WI3 deferred).

**Sanity check the rod against the disconnection condition:**

Per IEC 60364-4-41 §411.5.3, the TT disconnection condition is:

> Ra × IΔn ≤ 50 V

The **acceptance ceiling** for the chosen RCD (30 mA, IΔn = 0.030 A) is:

> Ra_max = 50 V / 0.030 A = **1666 Ω**

The measured Ra = 200 Ω passes the ceiling with **~8× margin**
(50/6 = 8.33).

**Why one rod is sufficient:** A second rod would reduce Ra (rough rule of
thumb: 2 rods spaced ≥ 1 rod-length apart give ~60% of single-rod Ra,
so ≈ 120 Ω). But the design is already 8× under the threshold; adding a
second rod would not improve compliance, only cost.

**Periodic re-measurement:** IEC 60364-6 §61.3.6 mandates periodic
verification. Ra in sandy loam drifts seasonally (worst case in
prolonged drought). Recommend re-measure every 5 years; if Ra exceeds
1500 Ω at any inspection, add a supplementary rod or chemical electrode.

## Step 6 — Main protective bonding (empty by site fact)

`main_bonding: []` — and this is **deliberate, not an oversight**.

Off-grid cottage has:
- **No incoming metallic water service** (rainwater from roof to tank;
  pipework PEX/PE — no extraneous-conductive-part to bond)
- **No incoming metallic gas service** (bottled LPG — the cylinder
  bracketry is bonded internally to the cylinder valve which is
  isolated from the cottage earth system by design; the LPG installer
  documentation confirms no bond to cottage MET)
- **No structural metalwork** (timber-frame cottage on concrete slab; no
  steel column or rebar mat extends to roof or ground in a way that
  would constitute an extraneous-conductive-part)

If a future borehole-pump installation introduces an incoming metallic
pipe to the cottage, **that pipe MUST be bonded to MET** per IEC 60364-5-54
§544.1. The empty `main_bonding[]` is documented in the assumptions block.

## Step 7 — Supplementary bonding (none)

No bathroom (the cottage has a dry-composting WC in an external
outbuilding — outside the §701 zone). No pool, kitchen-commercial, or
medical Group 2 trigger. `supplementary_bonding: []`.

## Step 8 — CPC sizing per circuit (Table 54.2 regime)

All four final circuits have line CSA ≤ 16 mm² Cu, so IEC 60364-5-54
**Table 54.2** governs: CPC ≥ line CSA. Each circuit takes CPC = line CSA:

| Circuit | Designation         | OCPD     | Line  | CPC   | Length | Method                 |
|---------|---------------------|----------|-------|-------|--------|------------------------|
| F01     | Lighting (whole)    | B6 MCB   | 1.5   | 1.5   | 18 m   | IEC 60364-5-54 Tbl 54.2 |
| F02     | Kitchen sockets     | B16 MCB  | 2.5   | 2.5   | 12 m   | IEC 60364-5-54 Tbl 54.2 |
| F03     | Water heater (ded)  | B16 MCB  | 2.5   | 2.5   | 6 m    | IEC 60364-5-54 Tbl 54.2 |
| F04     | Bedroom sockets     | B16 MCB  | 2.5   | 2.5   | 14 m   | IEC 60364-5-54 Tbl 54.2 |

## Step 9 — Zs verification (RCD-disconnection path, not OCPD)

This is **the TT-specific reasoning**. With Ra = 200 Ω, the earth-fault
current via the OCPD path would be:

> Ia(fault) ≈ U0 / Ze = 230 / 200 = **1.15 A**

This is **two orders of magnitude below** any MCB instantaneous-trip
threshold (B6 needs ≥ 30 A, B16 needs ≥ 80 A). **OCPD alone cannot meet
§411.4 disconnection time** on a high-Ra TT system — this is the
fundamental reason TT mandates RCD.

The **RCD disconnection path** replaces the OCPD path. Per §411.5.3, the
Zs_max via RCD is:

> Zs_max = U0 / IΔn = 230 / 0.030 = **7666.67 Ω**

Computing Zs per circuit using 20 °C Cu data (IEC 60228 / Eland tables;
under-estimate vs 70 °C operating by ~20%, immaterial here):

| Circuit | Ze (Ω) | R1+R2 (Ω)                          | Zs (Ω)  | Zs_max (Ω) | Compliance      |
|---------|--------|------------------------------------|---------|------------|-----------------|
| F01     | 200    | 2 × 12.1 mΩ/m × 18 m = 0.436       | 200.436 | 7666.67    | pass_with_rcd   |
| F02     | 200    | 2 × 7.41 mΩ/m × 12 m = 0.178       | 200.178 | 7666.67    | pass_with_rcd   |
| F03     | 200    | 2 × 7.41 mΩ/m × 6 m  = 0.089       | 200.089 | 7666.67    | pass_with_rcd   |
| F04     | 200    | 2 × 7.41 mΩ/m × 14 m = 0.207       | 200.207 | 7666.67    | pass_with_rcd   |

All four circuits pass Zs by **three orders of magnitude of margin**.
The compliance disposition is `pass_with_rcd` (not `pass`) because the
pass is conditional on the RCD being present — without the RCD, the
OCPD path fails by ~100×.

**Hand-check of the disconnection condition** (the heart of TT):

> Ra · IΔn = 200 × 0.030 = **6.0 V**

`6.0 V ≤ 50 V` per §411.5.3 — passes with margin of 50/6 = **8.33×**.

## Step 10 — RCD requirements (TT mandates RCD on every circuit)

Per IEC 60364-4-41 §411.5:

> "Where, in TT systems, automatic disconnection of supply is provided by
> means of an RCD, the following conditions shall be fulfilled: ..."

§411.5 mandates RCD-based ADS in TT. Every final circuit takes 30 mA.

**Type selection per §531.3.3:**

| Circuit | Load profile                     | DC residual expected? | RCD type |
|---------|----------------------------------|-----------------------|----------|
| F01     | Lighting (LED drivers + filament)| Negligible (≤1 mA)    | AC       |
| F02     | Kitchen sockets                  | Yes (chargers, electronics) | A   |
| F03     | Water heater (resistive)         | None on the heater itself, but installed on socket-outlet spur | A |
| F04     | Bedroom sockets                  | Yes (chargers, electronics) | A   |

Type A on F03 is a precaution per the design choice to feed the water
heater via a socket-outlet spur. If the heater were hard-wired on a
dedicated radial, Type AC would be acceptable per §531.3.3.

## Step 11 — Compliance flags

**Compliant** (`compliant: true`). No non-compliance flags. All four
circuits pass `pass_with_rcd` via the §411.5.3 RCD disconnection path.

Two **TOOL-CALL-PENDING** flags remain (WI3 deferrals, expected, not
defects):
- `calc.electrode_resistance` — Ra=200 Ω is installer-measured; will
  refine when runtime tool ships.
- `calc.zs_loop_impedance` — Zs values are LLM-estimates from 20 °C Cu
  data; deterministic refinement deferred per WI3.

## Step 12 — Rationale emitted

9-section taxonomy + chat_summary, each section with decisions citing IEC
60364 clauses. See `output.json` — `rationale` block populated per
shared/schemas/core/rationale.schema.json.

## Validator INVs populated in `ir.invariants[]`

Per the generator step that consumes `validator.md` INV list, four INVs
were exercised on this example and one cross-contamination check passed:

- **INV-02** (electrode jurisdiction-system match): PASS — INT+TT requires
  ≥1 electrode; `electrodes[]` has one entry (E1).
- **INV-04** (CPC sizing method per jurisdiction): PASS — INT permits
  `iec60364_table_54.2`; all four circuits use it because line ≤ 16 mm² Cu.
- **INV-06** (RCD requirement): PASS — TT system → `rcd_required: true` on
  all 4 final circuits per §411.5. Ra·IΔn = 6.0 V ≤ 50 V satisfies §411.5.3.
  Type AC on lighting F01, Type A on socket circuits per §531.3.3.
- **INV-09** (tool deferral shape): PASS — `tool_call_pending_for_zs: true`
  with `zs_calc_tool_input` payload present and `flags[]` carrying the
  TOOL-CALL-PENDING string.
- **INV-10** (KE/INT citation cross-contamination): PASS — jurisdiction is
  INT; no `code_clause` field contains the string `KS 1700`.

## Why this example exists (Sprint C.1 cause-fix continuation)

The Sprint A.1 fix renamed the misnamed folder but left the TT slot empty.
That meant the safest earthing branch — TT with mandatory RCD per
§411.5 — was never exercised by an example. A model with that gap could
silently regress the TT logic and no example would catch it.

This example exercises:
1. **TT system mandate** by site context (off-grid → no PEN bond is the
   trigger, not jurisdiction).
2. **Electrode-only protective earth** with a single rod and an
   installer-measured Ra accepted via WI3 tool deferral.
3. **High-Ra Zs strategy** — OCPD path fails by 2 orders of magnitude
   (Ia=1.15 A on a B16 MCB); RCD path succeeds by 3 orders of magnitude
   (Zs ≈ 200 Ω vs Zs_max 7667 Ω).
4. **§411.5.3 disconnection-condition hand-check** — Ra·IΔn = 6.0 V ≤ 50 V
   with explicit ~8× margin documented.
5. **§531.3.3 RCD type selection** — Type AC vs Type A by load DC
   residual characteristics, including the design choice to upgrade F03
   to Type A because of the socket-outlet spur installation.
6. **INV-06 PASS** — the critical RCD-requirement invariant now fires on
   a real example for the first time. Prior to this example, INV-06 was
   only exercised against TN-C-S branches (where it asks "is this socket
   ≤32 A in a dwelling?"); the TT branch ("is rcd_required true on every
   circuit?") was untested.

A model regressing any of these would now break this example's schema
validation or eval assertions.
