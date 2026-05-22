# Reasoning — INT HVAC VFD Soft-Start Control

## Why VFD (and not DOL or star-delta) for a 22 kW CHW pump

Three reasons all point to VFD on an HVAC chilled-water pump.

First, hydraulic. A CHW pump on DOL or star-delta presents the chilled-water loop with a torque step that pressurises pipework and valves over ~100 ms. The resulting water-hammer shock cycles flexible couplings, expansion bellows, gauge tappings, and butterfly valves; on a 22 kW pump it is the single biggest cause of pipework fatigue failure within the first three years of service. A VFD ramping over 3 s flattens the torque rise enough that the loop pressurises smoothly and the pump curve enters its operating point without water-hammer.

Second, energy. A CHW pump rarely runs at design flow. Variable-flow systems (now the default per ASHRAE 90.1 and the equivalent EN 14511 efficiency frameworks) require the pump to track BMS-commanded reduced flow at part-load. With a VFD, the pump frequency drops with cubic relationship to flow demand — at 50% flow the pump draws ~12.5% of rated power. DOL or star-delta has no part-load capability; throttling valves are inefficient and produce noise.

Third, motor reliability. The 7×FLA inrush on DOL stresses the motor windings and the cage rotor; over many start cycles this contributes to insulation breakdown and bar/end-ring fatigue. The VFD soft-start ramp limits motor current to FLA throughout the acceleration profile.

## VFD as `signal_converter` device_class

The v1.0 schematic IR enum (27 device_class values) was authored before VFDs were considered as a distinct schematic primitive. There is no `vfd`, `inverter`, or `drive` class. The closest fits in the existing enum are:

- `signal_converter` — captures the analogue + digital I/O block (4-20 mA BMS speed-ref in, 24 VDC digital outputs for RAMPING / AT-SPEED / FAULT). This is the choice made in this example.
- `logic_gate` — too narrow; only captures the discrete-logic aspect.
- `contactor` with `rating` — captures the power-switching aspect but loses the I/O block.

The `signal_converter` choice is explicitly disclosed in `labels[]` (a sequence_note on VFD1) and in `compliance_summary.assumptions[]`. A future v1.1 IR enum revision should add a dedicated `vfd` or `power_drive` class — this is a known v1.0 limitation. The under-cite is preferable to inventing an enum value the schema would reject.

## Soft-start ramp 3 s

3 s is the workhorse value for an HVAC CHW pump. Shorter ramps (1-2 s) re-introduce water-hammer; longer ramps (5-10 s) stall the pump on start-up torque demand because the pump curve at low frequency does not yet generate the differential pressure needed to lift the impeller out of static seal-stiction. 3 s is also the common manufacturer-default value on Danfoss FC202, ABB ACH580, and Schneider ATV600 HVAC drives — the engineers shipping these products converged on this figure over millions of installed units.

## Line contactor K1 (AC-1, not AC-3)

This is the most common mis-specification on VFD line-side wiring. K1 *never* switches under motor load — motor torque is built and released by the VFD output stage (a 3-phase IGBT bridge), not by the upstream line contactor. K1 only isolates the VFD line side; when K1 is opened, the VFD has already crow-barred its output (or run down through DC-bus discharge), so K1 sees only the line-side magnetising-current step. AC-1 utilisation category covers exactly this duty (steady-state distribution currents); selecting AC-3 would over-spec the contactor mechanical life rating for no benefit.

## Cascade verification

Both `db-layout-rollup` and `fault-level` intents are consumed. The cascade verifies cleanly:

- db-layout-rollup → 63 A DB-MECH outgoing circuit → Q1 + K1 sized at 63 A AC-1
- fault-level → 8.2 kA prospective at DB-MECH outgoing → VFD declared SCCR 50 kA (6× headroom) + K1 short-time withstand exceeds 8.2 kA

The conductor csa step (16 mm² line / 10 mm² motor cable) reflects that line-side current is ~10% higher rms than VFD-output current due to harmonic content (5th, 7th, 11th, 13th harmonics from the 6-pulse rectifier). The earthing intent is absent — TT or TN-C-S is engineer-declared. The VFD enclosure PE bond and screened motor cable termination should be re-verified when earthing intent is added in a future project revision.
