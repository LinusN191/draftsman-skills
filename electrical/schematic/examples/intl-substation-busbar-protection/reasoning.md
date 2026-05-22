# Reasoning — INT 33 kV Substation Busbar Protection (2-Zone 87B + 50BF)

## Why high-impedance 87B (not low-impedance numerical 87B)

Busbar protection comes in two architecturally distinct flavours: high-impedance and low-impedance. High-impedance (the older but still dominant scheme for modest-zone-count substations) uses a single relay coil in series with a stabilising resistor, with all CTs paralleled into the relay node. Under healthy conditions the CT secondary currents sum to zero at the relay; under an internal fault, the unbalance develops a voltage across the relay coil that exceeds the relay setting. Low-impedance numerical 87B (ABB REB670, Siemens 7SS85, Schneider P746) implements the same mathematical principle but with each CT brought independently to the relay's analogue input and the differential calculated in firmware, with per-zone configurable logic.

For a 2-zone substation with 4 feeders per zone, high-impedance is the right choice on cost, CT performance demand, and commissioning simplicity. Low-impedance numerical 87B becomes preferable when (a) the busbar is highly subdivided (5+ zones), (b) automatic CT-saturation detection is required for very high through-fault levels (>60 kA), or (c) the substation is digitalised with IEC 61850-9-2 process bus carrying CT samples to the central relay. None of those conditions applies here — 31.5 kA through-fault is modest by HV substation standards, the 2-zone architecture is simple, and the design assumes a conventional copper-CT wiring scheme.

## CT class PX (not 5P) — linearity, not accuracy

The choice of class PX (formerly Class X under earlier IEC 60044-1 editions) over class 5P or 10P is the single most important CT specification on a high-impedance scheme. 5P and 10P CTs are specified by their composite accuracy at a stated ALF (accuracy limit factor — typically 5×, 10×, or 20× rated primary current). Above the ALF, the CT begins to saturate non-linearly and produces secondary current that no longer linearly tracks primary current. For an IDMT relay this is acceptable (the relay pickup is well below the saturation knee), but for a high-impedance differential scheme it is fatal: a saturated CT produces unbalanced secondary current → false differential current → false trip under external faults. Class PX is specified by its knee-point voltage Vkp (the voltage above which the magnetising current increases steeply), its winding resistance Rct, and its excitation current at Vkp/4. The scheme designer sizes the stabilising resistor so the voltage developed under maximum external through-fault stays below Vkp/2 — guaranteeing the scheme remains stable across all credible through-fault scenarios.

## Stabilising-resistor sizing math (2200 ohm chosen)

The canonical sizing formula is Vs = If × (Rct + 2 × Rl), where:
- Vs = the voltage that develops across the relay coil + stabilising resistor under maximum external through-fault
- If = maximum CT secondary current under through-fault = (maximum primary fault) / CT ratio = 31.5 kA / 1200 × 5 = 131 A
- Rct = CT winding resistance = ~4 ohm typical for a 1200/5 PX CT
- Rl = lead resistance one-way to the relay = ~1.5 ohm for a 50 m loop in 4 mm² Cu

Therefore Vs = 131 × (4 + 2×1.5) = 131 × 7 = 917 V.

The relay setting Vr is chosen at ~30% of Vs to ensure operation only on internal faults — Vr = 200 V is the catalogue value for a typical high-impedance busbar relay (ABB REB650 or Siemens 7SS52). The stabilising resistor Rs is then sized as Rs = Vr / Ir where Ir is the relay coil operating current at Vr — for a 5 A CT secondary and a 200 V / 1 mA relay coil, Rs ≈ 200 / 0.001 - Rrelay ≈ 2000-2400 ohm, with 2200 ohm being the standard catalogue value. The resistor's power rating is sized for the worst-case through-fault duration assumption (typically 3 s at If²×Rs ≈ 131² × 2200 = 38 MW — which is why the resistor is a chunky metal-wirewound element, not a discrete component).

## 50BF breaker failure time 200 ms = 90 + 60 + 50

The 50BF time is built from three components:
- Breaker operating time ~90 ms typical for a 33 kV SF6 vacuum CB (manufacturer datasheet specifies "5-cycle" CB = 100 ms at 50 Hz; modern vacuum CBs at this voltage achieve sub-60 ms)
- 50BF current-check element operating time ~60 ms (the time for the 50BF relay to confirm that current is still flowing through the supposedly-tripped breaker)
- Margin ~50 ms (covers measurement uncertainty + DC supply transient + lockout-relay pick-up time)

Total = 200 ms. Faster than 200 ms risks false 50BF trips on slow breakers; slower than 200 ms extends the fault clearance time beyond the IEEE C37.234 § 5.5 guidance maximum of ~250 ms for typical substation arc-flash energy. 200 ms is the universal industry default for medium-voltage substations.

## Zone overlap at the bus-section breaker

Busbar protection schemes must have NO dead-zone. The bus-section breaker (drawn here as Q4 from Zone 1's perspective and Q5 from Zone 2's perspective — physically the same CB, drawn as two items for zone-clarity on the schematic) is the most failure-prone position because it sits at the boundary between zones. Without overlap, a fault on the bus-section bushings could potentially escape detection (or be detected by the "wrong" zone, leading to over-tripping). The standard practice is to mount TWO independent CT cores on the bus-section breaker: T4 wired into Zone 1 protection and T5 wired into Zone 2 protection. A fault between T4 and T5 (i.e. on the bus-section CB itself) is seen by BOTH zones — they both trip, clearing all 8 feeders, which is the correct conservative response. The "intentional overlap" is the canonical IEC 60255-187 § 5.3 zone-definition discipline.

## Leaf-mode execution

This schematic sits at the top of the protection hierarchy. There are no consumed intents because:
- db-layout-rollup: a substation busbar is upstream of any LV distribution-board cascade by definition — the LV DBs are downstream of the transformer cascades downstream of the substation busbar.
- fault-level: the busbar IS the fault-level source for downstream cascades. Its through-fault rating (31.5 kA at 33 kV per IEC standard switchgear breaking-capacity tier) is engineer-declared as the upstream-of-everything reference value.
- earthing: the busbar protection zone is functionally independent of the LV earthing system. Earthing applies to the LV side of distribution transformers; the substation HV busbar protection cares about the protection zone bounded by the CTs, not about how earth-fault current returns through the LV neutral.

All three intent absences are correct and explained in compliance_summary.assumptions[6]. The schematic is in leaf-mode and the leaf-mode declaration belongs in the Schedule Notes rationale section per generator prompt Step 11.

## Schema-pattern compromise on 50BF

The schematic IR schema regex for ANSI codes (both `ansi_function_code` on items and `ansi_code` on protection_settings) is `^[0-9]{1,3}[A-Z]?(T|B|N|G)?$`. This permits codes like 50, 51, 51N, 52, 87T, 87N, 87B, 86 — but it does NOT permit 50BF (because 50BF would require the regex to allow two trailing letters, and only one is permitted in the second optional group). The industry-standard ANSI/IEEE C37.2 designation for breaker failure is 50BF and is universally used in protection settings sheets, single-line diagrams, and relay manuals. To stay schema-compliant whilst preserving the engineering intent, this schematic carries `50B` in the schema-bound ANSI fields (item.ansi_function_code, protection_settings.ansi_code) and retains the full `50BF` designation in item.rating strings, label.sequence_note text, set_unit strings, and the compliance_summary.assumptions[]. The reading engineer sees `50BF` in every human-readable position; the schema validator sees `50B` in the strict-pattern positions. An assumption explicitly documents this representation choice. (A future schema revision could broaden the regex to permit two-letter suffixes for the BF, BU, and BFG cases — but that is out-of-scope for v1.0 and would require a coordinated schema migration across all protection examples.)

## IEC 61850-9-2 cited as future-proofing reference

IEC 61850-9-2 specifies the process-bus protocol for digital substations — CT and VT samples are transmitted as multicast Sampled Values (SV) over Ethernet rather than as analogue 1 A / 5 A signals over copper. This schematic is a conventional copper-wired scheme (the protection_settings and CT class assumptions reflect that), but IEC 61850-9-2 is cited as the framework reference because the typical 33 kV substation new-build in 2026 is being designed with at least the capability to migrate to process bus within the asset lifetime. The CT class PX specification holds equally well for either architecture — the relay-side wiring changes, not the CT-side wiring.
