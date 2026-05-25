# INT 11 kV HV RESTRICTED Substation — Worked Example

## Scenario

International industrial 11 kV indoor substation, single bus-A configuration, downstream of a 2 MVA oil-immersed transformer. The single arc-flash node analysed:

- `HV-BUS-A`: indoor metal-clad MV switchgear, single bus, 11 kV nominal, 25 kA bolted fault, X/R = 22, t_clear 0.5 s (MV VCB with overcurrent relay at incomer).

This example exists specifically to exercise the **RESTRICTED** branch (incident energy > 40 cal/cm²) — the highest-consequence safety branch of the arc-flash skill, where no commercially available PPE provides adequate protection and live-work is operationally prohibited.

## Method choice — IEEE 1584-2018 2700V model class, HCB

**Why IEEE 1584-2018 (no fallback):** Sprint A.3 transcribed the IEEE 1584-2018 Table 1 coefficients for the 2700V model class (k1-k7 for each electrode configuration), so the primary method applies directly. `method_fallback_trail` records a single entry: `ieee_1584_2018 = applied`.

**Why 2700V model class:** IEEE 1584-2018 §7.3 defines three voltage model classes — 600V, 2700V, 14300V — with valid voltage ranges. 11 kV nominal sits inside the 2700V model class applicability window (600 V to 15 kV).

**Why HCB electrode configuration:** 11 kV indoor metal-clad cubicles typically use **horizontal cylindrical bars** (HCB) for the main bus arrangement — bars run horizontally across the cubicle width, supported on insulators. This is documented in IEEE 1584-2018 §4.1.2 as a discrete electrode configuration with its own coefficient set. The input declares `electrode_config_overrides: [{ electrode_config: "HCB" }]` to override the auto-inference (the auto-inference rule for indoor MV switchgear could default to VCB, which would be wrong for this physical arrangement).

## Arc-current derivation

Per IEEE 1584-2018 §10:

```
I_arc = f(Ibf, V, gap, electrode_config, voltage_class)
```

With the 2700V HCB k1-k7 coefficients applied:
- I_arc ≈ 22.7 kA

The HV regime is characterised by a **small arcing-current reduction** (≈9% below Ibf) — unlike the LV regime, where I_arc can be 30-60% below Ibf for short-circuit currents in the kA range. This matters operationally because the overcurrent relay must see I_arc to clear the fault, and at HV the relay margin is generous (the trip will fire reliably).

## Incident-energy computation

Per IEEE 1584-2018 §11 with:
- I_arc = 22.7 kA
- t_clear = 0.5 s (engineer-declared MV VCB)
- Working distance D = 910 mm (typical MV switchgear, 36 in)
- Gap = 153 mm (IEEE 1584-2018 Table 9 standard MV value)
- Enclosure volume ≈ 762 L (914×914×914 mm cubicle — within §10.5 typical range, no out-of-band adjustment factor needed)

```
IE @ 910 mm ≈ 48.2 cal/cm²
AFB (where IE drops to 1.2 cal/cm²) ≈ 4275 mm
```

The AFB ≥ working distance invariant (INV-06) holds: 4275 mm ≥ 910 mm.

## RESTRICTED branch — the critical safety decision

**IE 48.2 cal/cm² exceeds the 40 cal/cm² threshold.** Per IEEE 1584-2018 §13.1, no commercially available arc-rated PPE provides adequate protection above 40 cal/cm². The reasons are:

1. **ATPV limits.** Practical arc-rated suits cap around 40 cal/cm² ATPV — beyond this rating, the garment-side energy-dissipation mechanism fails (heat penetration to skin → 2nd-degree burn).
2. **Non-thermal injury modes.** Above 40 cal/cm² the arc-flash event develops pressure-wave / molten-metal-ejection injury modes that thermal PPE does not address.
3. **NFPA 70E:2024 Table 130.7(C)(15)(A)(b)** defines PPE categories 1-4, none of which extend above 40 cal/cm². The table simply does not assign a category above this limit.

**IR encoding (contract-correct):**

| Field | Value | Why |
|-------|-------|-----|
| `arc_flash.ppe_category` | `null` | Per validator.md INV-07: IE > 40 → null (do not silently emit Cat 4) |
| `arc_flash.ppe_category_source` | `"computed_from_E"` | The decision is derived from IE — not engineer-override, not table-lookup |
| `compliance_summary.non_compliance_flags[]` | includes `INCIDENT_ENERGY_GT_40_RESTRICTED` | Required per INV-07 + schema enum |
| Flag `severity` | `"error"` | Live-work prohibition is a blocker, not a warning |
| `compliance_summary.compliant` | `false` | Equipment cannot operate under PPE selection alone |
| `flags[]` | includes `RESTRICTED_LIVE_WORK_PROHIBITED` | Top-level project flag for downstream skills |

## Operational consequence — live-work PROHIBITED

This is the durable engineering takeaway of the RESTRICTED branch: **PPE cannot make this work safe.** The only acceptable paths forward are:

1. **De-energise before approach** — switch HV-BUS-A dead, verify zero potential, then perform any required work as electrically-safe-work-condition.
2. **Remote racking with interlocked door operator** — circuit-breaker insertion / withdrawal performed from outside the arc-flash boundary, with the cubicle door interlocked closed during racking. Approach the equipment only after the breaker is racked out and confirmed open.

Operators must NOT attempt to "Cat 4 PPE up and proceed" — that path does not exist within the IEEE 1584-2018 + NFPA 70E framework above 40 cal/cm².

## Shock-approach boundaries — distinct from arc-flash

Shock-approach distances apply **independently** of arc-flash and are still enforceable in the RESTRICTED branch (they protect against electrical-contact injury, not thermal energy). Per NFPA 70E:2024 Table 130.4(C)(a) row "751 V to 15 kV":

| Boundary | Distance |
|----------|----------|
| limited_approach_movable | 3050 mm |
| limited_approach_fixed | 1530 mm |
| restricted_approach | 660 mm |

These distances continue to bound the de-energise / lock-out / tag-out procedure even when arc-flash work itself is prohibited.

## Label policy — RESTRICTED format required

The downstream `arc-flash-labelling` skill consumes the emitted intent and must:

1. Select `format_applied = "restricted_format"` (not bs_5499 / iso_7010 / ansi_z535_4).
2. Use `signal_word = "RESTRICTED"`.
3. Replace the PPE-category line with explicit text: "NO PPE ADEQUATE — DE-ENERGISE OR REMOTE-RACK ONLY".
4. Cite IEEE 1584-2018 §13.1 + NFPA 70E:2024 Table 130.7(C)(15)(A)(b) in the regulatory footer.

The label is the field-level enforcement mechanism for the operational decision — it must communicate "do not approach live" to anyone who reads it.

## Why this is a good test case

This example validates:

1. **RESTRICTED branch fires correctly** — IE > 40 → ppe_category=null + INCIDENT_ENERGY_GT_40_RESTRICTED flag (INV-07 PASS).
2. **MV / HV equipment modelling** — 2700V model class + HCB electrode configuration + MV-row shock-approach distances.
3. **IEEE 1584-2018 primary method works without fallback** — Sprint A.3 coefficients in place; single-entry method_fallback_trail (validates INV-05 with no Lee 1982 escape hatch).
4. **`compliant: false`** — the IR contract correctly distinguishes "calculation succeeded but operating regime is unsafe" from "calculation failed".
5. **Operational consequence documented in `assumptions[]`** — de-energise / remote-rack rationale is visible to downstream tools and to the engineer reviewing the IR.

## What downstream skills must do

- **`arc-flash-labelling`**: emit RESTRICTED-format label (see companion example `uk-bs5499-final-with-provenance` for the non-RESTRICTED counterpart; a follow-up could exercise the RESTRICTED label path explicitly).
- **`schematic`** / **`db-layout`**: render a visible RESTRICTED marker on the equipment one-line + DB schedule, not just a PPE-cat callout.
- **Method statements / O&M skills**: insert the de-energise procedure as the mandatory pre-approach step.

## Citations (compact)

- IEEE 1584-2018 §4.1.2 — HCB electrode configuration
- IEEE 1584-2018 §7.3 — 2700V model class voltage range (600 V to 15 kV)
- IEEE 1584-2018 §10 — arc-current formula
- IEEE 1584-2018 §11 — incident-energy + AFB formulae
- IEEE 1584-2018 §13.1 — PPE inadequate above 40 cal/cm²; live-work prohibition
- NFPA 70E:2024 §130.5(H) — labelling requirement
- NFPA 70E:2024 Table 130.4(C)(a) — shock-approach distances (AC), 751V to 15 kV row
- NFPA 70E:2024 Table 130.7(C)(15)(A)(b) — PPE categories 1-4 (no category above 40 cal/cm²)
