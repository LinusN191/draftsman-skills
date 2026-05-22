# Reasoning — US Industrial Star-Delta (Wye-Delta) Starter

## Why star-delta (and not DOL, soft-start, or VFD) for a 15 HP conveyor

Star-delta sits in a specific niche that has narrowed over the last 30 years but still exists.

DOL on a 15 HP / 460 V motor is electrically viable — the 6×FLA inrush (~126 A) is within the trip headroom of a 30 A NEC Article 430 motor-circuit breaker if it's rated NEMA Class 2 (which has inrush tolerance comparable to IEC Type D). But DOL slams the conveyor with full starting torque — belt-driven systems with rubber belts, gearbox couplings, and load-cell tensioners take a measurable shock load. For a conveyor moving fragile goods (pharmaceuticals, electronics) or with significant length (>20 m), this shock is undesirable.

VFD would handle this beautifully — soft ramp, energy savings at part-load, BMS integration. But for a fixed-speed conveyor that runs at a single speed 24/7, the VFD's part-load capability is wasted. The VFD also adds ~$2-3k of capital cost on a 15 HP system that doesn't otherwise need it. For greenfield specifications in 2026, a VFD is increasingly the default even in this niche — but the question here is a brownfield install where the conveyor is a known fixed-speed application and the existing panel infrastructure already has the contactor wiring layout for star-delta.

Soft-starter is also a viable choice and is in many ways the modern successor to star-delta (no transition timing, smoother ramp, less wiring). It has displaced star-delta in most new specifications. Star-delta remains in industrial standard practice for cost reasons (3 standard contactors + 1 timer cost less than a 15 HP soft-starter) and because there's a deep ecosystem of NEMA-rated star-delta enclosures available off-the-shelf in North America.

The decision here is to ship the canonical star-delta arrangement as the example, with the schedule notes pointing out that closed-transition with a bridging resistor is required for high-inertia loads. The open-transition variant is fine for the conveyor inertia.

## NEMA Size 1 vs IEC AC-3 contactor sizing

The schematic uses NEMA Size 1 for K1/K2/K3. NEMA Size 1 is rated 27 A continuous and 7.5-15 HP at 460 V — exactly fits a 21 A FLA / 15 HP motor. The IEC equivalent (AC-3 utilisation, 30 A rated, suitable for 15 HP at 415 V) is mechanically and electrically similar but the NEMA frame size correlates to a specific physical package and mounting pattern that is the dominant standard in North American industrial panels. The label set on H2/H1 + the IEEE Std 315 ieee_std_315_ref cross-references reflect the US convention of dual-symbol working (BS EN 60617 primary + IEEE Std 315 cross-reference).

## The 7 s transition timer

The KT1 7 s on-delay is the workhorse transition time for a 15 HP motor on an industrial conveyor. Too short (<5 s) and the motor hasn't accelerated fully under reduced wye voltage — the K3 close in delta hits a still-accelerating motor and draws a current spike close to DOL inrush, defeating the purpose of star-delta. Too long (>10 s) and the motor stalls in wye against load torque (the wye voltage is 1/√3 of delta, so torque is 1/3 of DOL torque). 7 s is the value most often pre-set by NEMA Size 1 star-delta packaged starters from major North American vendors (Allen-Bradley, Schneider Square D, Siemens).

## Open-transition vs closed-transition

Open-transition (this example): K2 STAR drops completely before K3 DELTA picks. During the brief 30-50 ms dead-time, the motor sees an open circuit at U2/V2/W2 and coasts. K3 then closes onto the partially-decelerated motor. For a conveyor this is fine — the inertia is low, the deceleration over 50 ms is negligible, the K3 inrush is close to FLA.

Closed-transition: A 4th contactor K4 closes a bridging resistor between K1 line and motor U2/V2/W2 during the transition. K2 drops, the resistor carries the motor briefly, K3 closes, K4 drops. Mechanically more complex (4 contactors + resistor + 2nd transition timer) but the motor never sees open-circuit conditions. Required for high-inertia loads (centrifugal compressors, large fans with flywheels) where the open-transition coast would cause inrush spikes on K3 close.

The Schedule Notes section explicitly flags this distinction for downstream engineers reading the schematic.

## NEC Article 430 citation discipline

The schematic cites NEC 2023 Article 430 at the Article level, not at a specific sub-clause. This is a deliberate under-cite per the generator prompt fallback policy. NEC § 430.83 ("ratings") versus § 430.91 ("disconnecting means") versus § 430.32 ("overload protection") could each plausibly cover specific aspects of this design, but distinguishing which sub-clause precisely covers reduced-voltage starting versus overcurrent versus overload requires careful cross-checking of the NEC text. Better to cite the Article and let downstream review verify the sub-clauses than fabricate a sub-clause that may be wrong. NEC 2023 Article 250 is cited for grounding/bonding (engineer-declared because no earthing intent was consumed).

## Hybrid-mode disclosure

One intent consumed (db-layout-rollup → PNL-A 30 A circuit). Two intents absent (fault-level, earthing). Both partial-intent absences are disclosed in `compliance_summary.assumptions[]` per generator prompt Step 11. The cascade is self-consistent at the contact level: 30 A PNL-A circuit ↔ Q1 30 A disconnect ↔ K1/K2/K3 NEMA Size 1 (27 A continuous, 15 HP) ↔ 21 A motor FLA, with F1 Class 10 overload set at the motor FLA.
