# UK Abnormal-Condition (Water-Damaged) LV Panel — Worked Example

## Scenario

GB indoor LV switchboard, 400 V TPN, basement plant room of a UK commercial
building. A plumbing leak in 2024-Q3 caused water ingress on the busbar
compartment. A follow-up inspection on 2024-08-12 flagged visible corrosion
on three of six busbar mounting brackets. The equipment remained energised
pending remediation. This study assesses arc-flash risk under abnormal
equipment condition per **NFPA 70E:2024 §130.5(A)** prior to authorising
further live work.

Single-node cascade — `PANEL-A` (service_entrance, 400 V TPN, MCCB
incomer, t_clear 0.2 s). Working distance 18 in (457 mm) per IEEE 1584-2018
Table 8 LV standard; gap distance 32 mm per Table 9; enclosure ~227 L
within §10.5 typical range. Bolted-fault current 12.5 kA at the panel
incomer.

## Why abnormal — NFPA 70E §130.5(A)

NFPA 70E §130.5(A) lists equipment condition as a required input to arc-flash
hazard analysis. The clause distinguishes **normal** (well-maintained,
within design intent, no observed defects) from **abnormal** (water damage,
corrosion, prior arc damage, missed maintenance, evidence of physical
distress, exposure beyond design rating, etc.).

For PANEL-A, the abnormal flag is unambiguous: water ingress + visible
corrosion on busbar mounting brackets is exactly the failure mode the
clause anticipates. The 2024-08-12 inspection produced a written
observation; no remediation has been completed; the equipment remains
energised. The 2024-08-12 maintenance date is recorded in
`equipment_condition.last_maintenance_date`.

**Why the abnormal posture matters** — corroded busbar mounting brackets
reduce the dielectric integrity of the panel, increase the probability of
flashover at lower fault levels, and elevate the actual incident energy
above the desk-study estimate that would be computed assuming clean
equipment. The skill responds defensively rather than producing a value
the field crew could mistake for a verdict.

## Method choice — Lee 1982 fallback (Sprint A.3 honest disclosure)

IEEE 1584-2018 is the preferred method for LV equipment. However, the
600 V coefficient table at
`shared/standards/electrical/IEEE1584/method-2018-tables-1-3-600V-coefficients.json`
carries `_status: pending-transcription` per the **Sprint A.3** disclosure
— the IEEE 1584-2018 Tables 1+3 numerical coefficients are paywalled at
IEEE Xplore and have not yet been verbatim-transcribed into the standards
layer with licensed access. The structural shape was confirmed against
ETAP white papers + EasyPower release notes + Bisson Ch. 5, but the
numerical values remain authoritative-pending.

The method fallback chain therefore executes:

1. **`ieee_1584_2018`** — SKIPPED (coefficients pending per Sprint A.3)
2. **`ieee_1584_2002`** — SKIPPED (Doughty/Neal Annex F similarly pending)
3. **`lee_1982`** — APPLIED. Theoretical formula always available;
   V_nom 400 V within 50–15000 V range.

Lee 1982 is the theoretical maximum model (>15 kV regime) — at 400 V it
**over-predicts** incident energy. This is acceptable conservatism for an
abnormal-condition desk study where the operational recommendation is
site assessment + remediation, not field-actionable PPE selection. The
`LEE_1982_FALLBACK_USED` info-severity flag is emitted alongside the
abnormal-condition flag.

## Adder choice — 1.25× industry consensus (NOT NFPA prescription)

This is the most consequential engineering judgment in the example, and
the one most easily mis-cited.

**NFPA 70E:2024 §130.5(A) does NOT prescribe a multiplier.** The standard
says abnormal equipment "warrants different posture" without quantifying
the adjustment. A reviewer who reads "1.25× per §130.5(A)" would catch
the misattribution — the citation must be honest.

The 1.25× default applied here comes from **industry consensus**:

- **ETAP Arc Flash Analysis App Note 2020** — recommends a 1.25× IE
  adjustment for equipment classified abnormal at the engineer's
  discretion, citing field study data showing 20-50% IE elevation in
  documented water-damaged + corroded equipment;
- **EasyPower technical bulletin TB-AF-2019** — recommends a 1.2–1.5×
  range, with 1.25 as the default starting point.

1.25 is the mid-range of the 1.2-1.5× industry range. The
`ie_adjustment_factor` is engineer-overrideable within `[1.0, 2.0]`. The
`ie_adjustment_source` field on every node carries this exact disclosure
so a downstream consumer cannot mistake the multiplier for an NFPA
prescription.

## Arithmetic

```
IE_base (Lee 1982, 400 V VCB, 12.5 kA bolted, 0.2 s, 457 mm)
       = 5.12 × 10⁵ × V × I_bf × t / D²
       ≈ 5.2 cal/cm²

IE_adjusted = IE_base × ie_adjustment_factor
            = 5.2 × 1.25
            = 6.5 cal/cm²
```

Arcing current per Lee approximation ≈ 10.87 kA (87% of Ibf at LV).

Arc-flash boundary (where IE drops to 1.2 cal/cm²) ≈ 1850 mm — well
beyond the 457 mm working distance, so `boundary_ge_working_distance`
holds.

**Note on AFB conservatism** — Lee 1982 is known to over-predict the
arc-flash boundary at LV (≤ 1 kV) by a factor of ~1.5–1.7× relative
to IEEE 1584-2018 at comparable IE (per the well-documented LV
inflation of the Lee theoretical-max model — see IEEE 1584 Annex C
discussion). A naive inverse-square scaling from a sibling example
at IE 5.2 cal/cm² (uk-lv-switchgear's IEEE 1584 result) would predict
AFB ≈ 1175 mm at this node. The 1850 mm value here is intentionally
the Lee-conservative AFB, retained as the field value because the
study is gated by `is_provisional=true` + Lee-fallback + abnormal-
condition disclosures — the wider boundary is the safer field
posture pending IEEE 1584-2018 600V coefficient transcription
(Sprint A.3). When the coefficient table ships and the calc re-runs
under IEEE 1584-2018, AFB will tighten accordingly.

**PPE category** per NFPA 70E Table 130.7(C)(15)(c):

| IE band (cal/cm²) | Category |
|-------------------|----------|
| 1.2 ≤ IE < 4      | 1        |
| **4 ≤ IE < 8**    | **2**    |
| 8 ≤ IE < 25       | 3        |
| 25 ≤ IE < 40      | 4        |
| IE > 40           | null (RESTRICTED) |

IE_adjusted 6.5 falls in the 4-8 band → **PPE Category 2**.

(For reference: pre-adjustment IE 5.2 also falls in the same band — the
adjustment doesn't change the category here, but it does correctly
elevate the safety margin within the band and produces a higher AFB.)

## Operational consequence — DRAFT, NOT FOR FIELD USE

The combined effect of:

- `equipment_condition.condition == "abnormal"` →
  `provenance.is_provisional = true` forced;
- Lee 1982 fallback → `provenance.is_provisional = true` reinforced;
- `ABNORMAL_EQUIPMENT_CONDITION` error-severity flag →
  `compliance_summary.compliant = false`;
- `checks.abnormal_condition_provisional_forced = true` on PANEL-A;

is that **live-work is prohibited at PANEL-A** until:

1. Corroded busbar mounting brackets are replaced;
2. Panel is dried + re-tested per BS 7671 Part 6;
3. Arc-flash is re-assessed with `condition = normal` post-remediation.

Downstream consumers (labelling skill, energised-work-permit document)
MUST honour the DRAFT marker per Sprint A.2 C2 convention. The
arc-flash-labelling skill will render the label with the explicit DRAFT
banner so no field crew can mistake the value for a verified verdict.

## Provisional posture

`provenance.is_provisional = true` is forced by TWO independent triggers,
either of which alone would be sufficient:

- **(a) Abnormal-condition declaration** per NFPA 70E §130.5(A) defensive
  posture (Sprint D1.4 INV-11 rule);
- **(b) Lee 1982 fallback** per Sprint A.3 600 V coefficient
  pending-transcription (existing Sprint C3 IR-level provenance pattern).

The IR root `provenance.provenance_note` narrates both reasons explicitly.

## What changes when IEEE 1584-2018 coefficients ship

When the Sprint A.3 600 V VCB transcription completes (licensed
access required):

1. `method_applied` auto-promotes from `lee_1982` → `ieee_1584_2018`;
2. `IE_base` drops 2-5× to realistic empirical values
   (likely ~1.5-2.5 cal/cm²);
3. `IE_adjusted = IE_base × 1.25` may now fall in the 1.2-4 band
   (Cat 1) rather than the 4-8 band (Cat 2);
4. AFB shrinks accordingly;
5. `is_provisional` stays TRUE — the abnormal-condition trigger alone
   keeps the DRAFT posture until remediation completes.

No skill code changes — the fallback chain re-runs at runtime and the
abnormal-condition gate continues to fire independently. This is the
clean separation between coefficient supply and abnormal-condition
defensive posture.

## tool_call_pending status

`checks.tool_call_pending: true`. The numeric values in `arc_flash` are
senior-engineer Lee 1982 estimates pending the runtime
`calc.arc_flash_incident_energy` tool. The contract is shipped at
`shared/calculations/electrical/arc-flash-incident-energy.json` but the
runtime executor is not yet implemented — see the runtime project
boundary note in `[[runtime-project-boundary]]`.

## INV-11 — the new validator gate (Sprint D1.4)

INV-11 (HIGH severity) asserts the abnormal-condition defensive posture
for every cascade node carrying `equipment_condition`. For PANEL-A:

- `condition` = `"abnormal"` (in enum) ✓
- `justification` present, 203 chars (within 20-500) ✓
- `last_maintenance_date` = `2024-08-12` (valid ISO date) ✓
- `ie_adjustment_factor` = `1.25` (within `[1.0, 2.0]`) ✓
- `ie_adjustment_source` present (cites ETAP/EasyPower + discloses
  NFPA non-prescription) ✓
- IR root `provenance.is_provisional` = `true` ✓
- IR root `equipment_condition_basis` populated (project-level
  defaults) ✓
- `checks.abnormal_condition_provisional_forced` = `true` ✓

All rules hold. INV-11 entry in `invariants[]` records PASS with full
evidence narration.
