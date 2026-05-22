# Reasoning — UK Commercial Genset Changeover (ATS)

## Why ATS (and not parallel synchronisation or static transfer)

This is a standby genset, not a peaking or co-generation set. The mains and genset are never electrically in parallel — they switch alternately under a "break-before-make" automatic transfer scheme. Parallel synchronisation would require G99 protection relays, voltage-vector match, slip-frequency gating, and an export protection regime; that is appropriate for CHP and grid-export sites but disproportionate for a building life-safety / business-continuity standby. Static transfer (thyristor-based, sub-cycle changeover) is used for UPS sub-systems, not for whole-building mains/genset duty at 400 A — the thyristor cost and gate-driver complexity are excessive for a 10 s genset start window. The break-before-make ATS with mechanical interlock is the canonical arrangement for the BS 7671:2018+A2:2022 § 560 (safety services) duty class.

## Why 4-pole switching (and not 3-pole)

The 4-pole choice hinges on the genset alternator's neutral-earth bond. The 250 kVA diesel genset has its own star-point bond at the alternator — a "separately-derived" source in the BS 7671 sense. The mains supply is TN-S with the N-E bond at the substation. With 3-pole switching, the genset N would remain electrically tied to the mains N through the unswitched neutral conductor; under retransfer, current could flow on the neutral via two parallel paths (mains N + genset star-point bond), violating BS 7671:2018+A2:2022 § 551.4.3.2.1 which specifically requires switching of the neutral when sources are independently earthed. 4-pole switching breaks the neutral cleanly during transfer/retransfer and guarantees only one neutral-earth reference is active at any moment.

## The three timer choices (KT1 / KT2 / KT3)

- **KT1 0.5 s on-delay (mains-fail confirm)** — the genset start cycle is expensive (cranking battery + starter motor wear + fuel + warm-up cycle). 0.5 s rejects 99% of momentary mains dips (motor-start dips elsewhere on the network, lightning-induced transients, network reconfigurations) that recover within half a second. A bare K3 trip on first-cycle undervoltage would nuisance-start the genset multiple times per week in a typical urban supply environment.

- **KT2 10 s on-delay (genset warm-up)** — matched directly to the genset manufacturer's declared start-time-to-stable of 10 s. The genset needs to be cranked, fire, build voltage, and reach declared frequency tolerance before the contactor closes. Closing K2 earlier risks dropping the genset voltage under inrush load before excitation has fully built; 10 s is the manufacturer's "ready-for-load" threshold for a 250 kVA Stage V diesel.

- **KT3 60 s off-delay (retransfer hysteresis)** — the mains-restore window. Real mains restoration is usually preceded by 3-5 attempted reclosures by the DNO automatic reclose scheme, each of which can fail. 60 s confirms the mains has been stable and present for a meaningful confirm window before swinging the load back, avoiding flicker-trip on a partially-restored mains. This is the figure most often specified in BSRIA TG12 and CIBSE Guide F for standby genset retransfer.

## Hybrid-mode intent consumption

The schematic consumes one intent (db-layout-rollup → MSB main switch rating 400 A) — this drives the K1/K2 contactor selection and Q1/Q2 breaker sizing. Two further intents (fault-level, earthing) are not yet available in the project, so the 16 kA prospective fault current at the ATS incoming and the TN-S earthing system + genset star-point bond strategy are engineer-declared in inputs.json. The `compliance_summary.assumptions[]` block explicitly documents both partial-intent absences per generator prompt Step 11. The `Cross-Skill Cascade Verification` section in the rationale shows the self-consistency check: 400 A MSB main switch ↔ 400 A K1/K2 contactors ↔ 400 A 50 kA Q1/Q2 ACBs ↔ 240 mm² Cu busbar — when fault-level is added later, the Q1/Q2 Icu margin (50 kA Icu / 16 kA declared = 3.1× headroom) should be re-verified against the cascade-computed value.
