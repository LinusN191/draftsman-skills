# KS 1700:2018 — Compliance Checklist

Engineer-facing checklist for KS 1700 compliance in Kenya installations. Adopts BS 7671 §6 inspection framework substantially via KS Annex E with KS-specific additions noted.

## §411 — Automatic Disconnection of Supply (ADS)

- [ ] Earthing system type identified (TN-S / TN-C-S / TT)
- [ ] Ze declared by KPLC OR measured at intake position
- [ ] Each circuit's Zs ≤ Zs_max per Table 41.2 / 41.3 (KS Annex E adopts BS Tables verbatim)
- [ ] Required disconnection time achieved per Table 41.1 (0.4s for final circuits ≤32A @ 230V; 0.2s @ 400V; 5s for distribution circuits)
- [ ] **§411.3.3 (KS-specific):** 30mA RCD additional protection installed on **all** socket circuits ≤32A regardless of Zs compliance

## §415 — Supplementary equipotential bonding

- [ ] Supplementary bonding installed in all locations specified by §415 (bathrooms, kitchens with metallic plumbing, swimming pool zones, agricultural)
- [ ] Bonding conductor CSA ≥ 4 mm² Cu

## §544 — Main bonding

- [ ] Main earthing conductor sized per §544.1.1: ≥ half the largest service conductor; ≥ 10 mm² Cu for protected route; ≥ 16 mm² Cu for unprotected route between intake and MET
- [ ] All extraneous-conductive-parts bonded: water service entry, gas service entry, structural steel, lift rails (where present)
- [ ] Bonding conductor CSA ≥ 10 mm² Cu for service entries (PME systems require this minimum)

## §722 — EV charging (KS-routed to IEC 60364-7-722)

- [ ] KS 1700 has no native §722. KS Annex E §VIII directs to IEC 60364-7-722:2018 for EV charging requirements.
- [ ] For EV installations in Kenya, apply IEC 60364-7-722 with KS 1700 §411 / §544 / §415 baseline.

## §521 — Installation methods

- [ ] Method selected appropriate for environment (Reference Method per Table 4A)
- [ ] Bunching / grouping factors applied per Tables 4B1-4C1 (KS adopts BS verbatim)
- [ ] Ambient temperature correction applied per KS Annex G climate zone (NOT BS 7671's 30°C baseline)

## §522 — IP ratings

- [ ] IP rating selected appropriate for environment
- [ ] **Kenya-specific:** Outdoor installations in coastal zones use IP65 minimum due to humidity

## §6 — Inspection and testing

- [ ] Initial inspection conducted before energisation
- [ ] Continuity tests, insulation resistance tests, polarity tests, earth fault loop impedance tests, RCD tests recorded
- [ ] Inspection certificate signed by EPRA-registered electrical contractor
- [ ] Periodic inspection scheduled per EPRA regime: ≤5 years commercial/industrial, ≤10 years domestic

## Equipment

- [ ] All consumer-side equipment carries KEBS certification mark
- [ ] Cables comply with KS specifications (cross-references KS ISO 11801 etc.)
- [ ] Protective devices (MCB / MCCB / RCBO / RCD) carry BS EN 60898 or IEC 60898 markings (both accepted by KS 1700 §531)

## Documentation

- [ ] Installation drawings + certificates kept on site
- [ ] KPLC Wayleave reference recorded for the connection
- [ ] Ze measurement record signed by KPLC technician

## See also

- BS7671/compliance-checklist.md — for adopted-verbatim BS clauses
- `ks-unique-deviations.json` — full enumeration of KS-specific deviations
- `annex-E-bs7671-adoption-table.json` — clause-by-clause BS↔KS adoption type
