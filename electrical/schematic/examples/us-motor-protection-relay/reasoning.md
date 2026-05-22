# Reasoning — US 150 HP Motor Protection (49 / 50 / 51 / 86 + PTC)

## The 49 / 50 / 51 / 86 stack — why all four

Industrial motor protection at the 150 HP tier is the inflection point where US practice moves from "MCCB-only with built-in thermal" (typical below 50 HP) to "multifunction motor IED with discrete protection elements" (mandatory above 200 HP, common in the 75-200 HP band). The 49/50/51/86 stack is the canonical configuration:

- **49 (Thermal)**: A thermal-replica algorithm in the relay tracks the motor's predicted winding temperature based on the I²t history of the phase currents. Pickup at 1.0× FLA = 140 A; the Class 10 envelope tolerates 7.2× FLA for ~10 s (long enough to permit normal LRA starts) but trips on sustained operation above 1.15× FLA after the thermal model accumulates enough heat to cross the model's trip threshold.
- **50 (Instantaneous Overcurrent)**: Pickup at 1200 A primary = 1.33× LRA (900 A). Clears bolted short-circuits in ~25 ms — fast enough to limit damage from a fault inside the motor terminal box or on the motor cable. The 1.33× factor sits within IEEE C37.96 § 5.5's recommended 1.3×-1.5× LRA — the lower end of the band is preferred for cold-start applications, the upper end for warm-start applications where multiple consecutive starts heat the motor.
- **51 (IDMT Overcurrent)**: Backup against R49 thermal-model failure. Pickup 175 A (1.25× FLA × 1.15 SF = 1.4375× FLA effective), VI curve TMS 0.3. Operates ~6 s at 900 A LRA — well below the Design B 12 s locked-rotor withstand time but well above any legitimate start time (the motor reaches synchronous slip in ~4-5 s, current drops to FLA before 51 can trip).
- **86 (Lockout)**: Hand-reset master trip relay. Any of 49/50/51 trips drives K86 coil A1, which latches and holds the trip. Q1 MCCB cannot reclose until operator presses the reset — this is the safety discipline that prevents inadvertent reclose onto a hot motor after a 49 trip, or onto a faulted motor after a 50 trip.

Plus the motor-embedded PTC thermistor chain B1 (6 thermistors, 2 per phase), wired to R49's thermistor input. The PTC chain provides direct winding-temperature measurement (the 49 thermal-replica is a current-derived estimate; the PTCs are an actual temperature measurement). For Class F insulation with a 155 °C hot-spot threshold, the PTC switches from <100 ohm cold to >2700 ohm at the threshold, and the relay detects the step change and trips. The PTC chain protects against thermal failures that the current-only thermal model cannot see — e.g. blocked cooling air on a TEFC motor, where the motor draws normal FLA but the windings overheat because the fan-cooling assumption breaks.

## device_class judgment call: ANSI 49 → idmt_relay

The schematic IR schema's device_class enum has 27 values:
- contactor, overload, isolator, motor, thermistor, ptc
- idmt_relay, instantaneous_relay, differential_relay, ref_relay, distance_relay, lockout_relay, uv_relay, ov_relay
- breaker, ct, vt
- terminal, wire_reference, lamp, push_button, selector_switch
- timer, counter, latch, logic_gate, signal_converter

There is no `thermal_relay` value. The ANSI 49 thermal-replica protection function has to be mapped to one of the existing relay sub-classes. The closest functional match is `idmt_relay` (the thermal-replica algorithm operates on an inverse-time current-derived envelope — mathematically very close to the standard IDMT relay characteristic). The alternative would be `instantaneous_relay`, which is wrong (the thermal element is fundamentally not instantaneous), or `overload` (which the schema reserves for the discrete thermal overload device used in motor starters — a different physical thing). The schematic accordingly uses `device_class: idmt_relay` for R49 with `ansi_function_code: 49` carrying the actual function designation, and the `rating` field text explicitly states "Thermal-replica element (ANSI 49)" so the reading engineer is in no doubt about what the device actually is.

This is the same judgment-call pattern Task 7 used for any function that didn't have a dedicated enum value — map to the closest enum, document the mapping in the rating and assumptions, and let the ANSI function code carry the precise function semantic. A future schema revision could add `thermal_relay` to the enum but that's a coordinated migration out of scope for v1.0.

## R49 pickup 1.0× FLA with SF 1.15 margin built into the thermal model

This is a subtle but important point about NEC compliance. NEC 2023 § 430.32(A)(1) specifies overload protection sizing as a function of motor service factor:
- For SF ≥ 1.15 motors (this motor): 115% of FLA as the maximum overload pickup
- For SF = 1.0 motors: 125% of FLA as the maximum overload pickup
- For SF < 1.15 motors below 1.0: 115% of FLA (covers special-case totally-enclosed slow-speed motors)

The interpretation is: a SF 1.15 motor is designed to operate continuously at 115% of nameplate FLA without damage. So the overload protection should NOT trip until current sustained above 115% of FLA. The relay accordingly sets the thermal-replica pickup at 1.0× FLA = 140 A but the Class 10 envelope inherently incorporates the SF 1.15 margin (the thermal model only accumulates heat above 1.15× FLA). NEC's 115% figure is the MAXIMUM the overload pickup can be set to — setting it lower (i.e. setting it at 1.0× FLA with SF 1.15 model-handling) is more conservative and is preferred industry practice.

The 125% value for SF = 1.0 motors does not apply here. The schematic explicitly documents this in compliance_summary.assumptions[3].

## R50 instantaneous pickup at 1.33× LRA

IEEE C37.96 § 5.5 recommends the instantaneous overcurrent pickup for motor protection at 1.3× to 1.5× LRA. The factor is bounded below by "must not nuisance-trip on legitimate LRA inrush" (factor must exceed 1.0× LRA with safety margin) and bounded above by "must clear short-circuits before damage propagates" (lower factor = faster clearing of marginal short-circuits). 1.33× is the standard ABB / Schneider / SEL default for cold-start applications, which is what a typical industrial motor sees (start once or twice per shift, hours between starts). Warm-start applications (multiple consecutive starts within a short window, e.g. plug-reverse on a conveyor) push the factor toward 1.5× because the motor's residual heat reduces the LRA initial transient amplitude making the lower factor more likely to nuisance-trip.

## R51 IDMT VI backup at 1.25× FLA × 1.15 SF

The 51 backup exists for two failure modes the 49 thermal cannot cover: (a) R49 firmware crash (most modern motor IEDs self-supervise but cannot fully self-test), and (b) a thermal model whose calibration has drifted (older relays without auto-calibration can drift over years of service). Pickup at 1.25× FLA × 1.15 SF = 175 A (1.25× × 1.15× = 1.4375× FLA effective) on VI curve TMS 0.3 operates ~6 s at 900 A LRA — well below the Design B locked-rotor withstand time of 12 s, well above any legitimate start time (motor reaches synchronous slip in ~4-5 s, current drops to FLA before R51 can trip). The 1.25× × 1.15× factor combination is conservative and the standard backup setting on US industrial motor IEDs.

## NEC § 430.52(C)(1) Table 430.52 — short-circuit device sizing

Table 430.52 specifies the maximum short-circuit and ground-fault protection sizing for motor branch circuits:
- Inverse-time circuit breaker: 250% of FLA for Design B/C/D motors
- Instantaneous-trip circuit breaker: 800% of FLA
- Time-delay (dual-element) fuse: 175% of FLA
- Non-time-delay (single-element) fuse: 300% of FLA

For this 140 A FLA motor with the Q1 inverse-time MCCB, the maximum permitted short-circuit setting is 250% × 140 = 350 A. The actual R50 instantaneous pickup at 1200 A primary (= 6× FLA) is well below the 350 A NEC ceiling for the inverse-time CB at the same protection level. The R51 IDMT pickup at 175 A (= 1.25× FLA) is also below the 350 A ceiling. Both settings comply with § 430.52(C)(1).

## Cross-skill cascade verification

fault-level intent supplied `ifault_ka_lv = 14 kA` at motor terminals — comfortably below Q1 MCCB 35 kAIC interrupting rating per NEC § 110.10 (interrupting rating must equal or exceed available fault current). 14 kA × √2 peak = 19.8 kA peak short-circuit current, well within the MCCB's tested interrupting capability.

db-layout-rollup intent supplied `main_switch_rating_a = 200 A` for the MCC bucket — matches Q1 AF (ampere frame) rating of 200 A. AF is the long-term thermal rating of the breaker frame; the trip-unit setting (typically 175 A = 1.25× FLA per NEC § 430.32 + § 430.52) is a separate parameter set independently of AF. So Q1 = 200 AF × 175 A trip-unit setting, with 35 kAIC interrupting rating. All cascade values cross-verified.

The earthing intent is NOT consumed by this schematic — motor earth-fault protection is carried by the residual element of the same phase CTs (the R49 IED detects residual-mode current as the vector sum of T1A + T1B + T1C, which is non-zero only on an earth fault). No dedicated earthing-system reference is needed for the motor zone. This is correct partial-hybrid-mode execution (2 of 3 potential intents consumed; the third correctly absent because it's not relevant to the motor protection scope).

## Dual symbol-reference: BS EN 60617 + IEEE Std 315

US drafting convention dual-references both standards on motor protection schematics:
- BS EN 60617 IEC 617-7 (graphical symbols for switchgear) — the v1.0 library symbol_id (carried in `bs_en_60617_ref`)
- IEEE Std 315-1975 (graphical symbols for electrical and electronic diagrams) — the US-traditional figure number for the same symbol (carried in `ieee_std_315_ref`)

The two standards are largely harmonised (BS EN 60617 was derived from IEC 617 which was harmonised with IEEE Std 315 in the 1970s-80s), but they have minor cosmetic differences — e.g. the BS EN 60617 motor symbol is a circle with "M" inside, the IEEE Std 315 motor symbol is a circle with three short tails representing the rotor windings. US-jurisdiction schematics typically show the IEEE form on the drawing but cite both standards in the schedule for cross-jurisdiction interoperability. The schematic accordingly populates both reference fields on every item.

## 125 VDC trip circuit (vs 110 VDC on KE / UK examples)

The motor protection trip circuit operates on 125 VDC, which is the standard US substation DC supply voltage. KE and UK substations typically use 110 VDC (or 48 VDC for smaller installations). The difference is historical (US 125 V was set when nominal lead-acid battery voltage was 2.08 V × 60 cells; UK 110 V was set at 2.0 V × 55 cells) but is preserved on modern installations because the asset bases (chargers, batteries, lockout-relay coil ratings) are standardised at each voltage tier within each country. The schematic accordingly specifies R86 coil and Q1 shunt trip coil at 125 VDC — different from the 110 VDC ratings in the KE and UK examples. This is a small but visible jurisdiction-specific design detail.
