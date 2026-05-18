# Protective Device Types Under KS 1700:2018

> **Verification note:** This file is authored as a draft-from-bs7671-derivative.
> KS 1700:2018 §531 adopts the BS 7671 / IEC 60364 protective-device
> framework substantially via KS Annex E, with the Kenyan addition that
> **both BS EN 60898 and IEC 60898 marked devices are accepted**.
> Promote `verification_status` once verified clause-by-clause against
> the published KS 1700:2018 PDF.

A guide to the device families used in Kenyan low-voltage installations,
with selection guidance for typical applications.

---

## Kenya supply context

Three context factors shape protective device selection in Kenya:

1. **Dual-marking acceptance.** KS §531 explicitly accepts both BS EN
   60898 marked devices (common from UK / European suppliers) and IEC
   60898 marked devices (common from Asian / South African suppliers).
   Engineers can specify either family — both are compliant.
2. **KEBS certification mark required.** Any MCB / RCBO / RCD sold or
   installed in Kenya must carry the KEBS certification mark in
   addition to the BS EN or IEC marking. Without the KEBS mark, the
   device cannot legally be sold and will fail EPRA inspection.
3. **Universal socket-RCD (KS §411.3.3 deviation).** Unlike pre-AMD2 BS,
   KS 1700 mandates 30mA RCD additional protection on **all** socket
   circuits ≤ 32A regardless of Zs compliance. As a result, most modern
   Kenyan domestic boards are full-RCBO — RCBOs are widely stocked at
   Kenyan electrical wholesalers (East African Cables, Mabati Rolling
   Mills consumer-unit business, importers in Industrial Area Nairobi).
4. **Trip curve types identical to BS.** Type B/C/D MCB curves are
   identical — see `KS1700/appendix3-device-curves.json` (adopts BS
   Appendix 3 verbatim).

---

## MCB — Miniature Circuit Breaker (KS §531 — BS EN 60898 or IEC 60898)

**Construction:** Thermal-magnetic — thermal for overload, magnetic for short-circuit.

**Ratings**
- In: 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125 A
- Breaking capacity (Icn): 3 kA, 4.5 kA, 6 kA, 10 kA, 15 kA, 25 kA
- Categories by instantaneous trip:
  - **Type B**: 3–5× In (resistive loads, general lighting, sockets)
  - **Type C**: 5–10× In (motor loads, fluorescent banks, LED with inrush, distribution circuits)
  - **Type D**: 10–20× In (transformers, lift drives, X-ray, large discharge lighting)

**When to use**
- Final circuits not requiring RCD additional protection
- Lighting circuits (Type B for LED, Type C for older fluorescent banks)

**When NOT to use**
- Socket outlet circuits ≤ 32A — KS §411.3.3 mandates RCD protection, so use RCBO.
- Fault levels above the device's Icn — use MCCB or HRC fuse.

---

## RCBO — Residual Current Breaker with Overcurrent (KS §531 — BS EN 61009 or IEC 61009)

**Construction:** Combined MCB + RCD in one module. Provides overload, short-circuit, and earth-leakage protection.

**Ratings**
- In: same as MCB (6 to 125 A)
- IΔn: 10 mA, 30 mA, 100 mA, 300 mA
- Types: AC, A, F, B (see RCD type table below)

**When to use** — preferred device for Kenyan final circuits because of KS §411.3.3
- **All** socket outlet circuits ≤ 32A — mandatory under KS §411.3.3
- Bathroom + kitchen circuits
- Outdoor and external power circuits (essential in coastal humidity)
- EV charging circuits (Type A or Type B per IEC 60364-7-722 routed via KS Annex E §VIII)

**Why RCBOs dominate the Kenyan domestic board**

KS §411.3.3's universal socket-RCD requirement means most modern Kenyan
domestic + commercial boards are full-RCBO arrays. A typical 8-way
Nairobi suburban board uses 6–8 RCBOs and 1–2 MCBs.

---

## RCD — Residual Current Device (KS §531 — BS EN 61008 or IEC 61008)

**Construction:** Earth-leakage detection only. Always installed in series with an MCB or fuse for overcurrent.

**Ratings**
- IΔn: 10, 30, 100, 300, 500 mA, 1 A
- Types: AC, A, F, B
- S-type: time-delayed (40–130 ms delay) for selectivity with downstream RCDs

**When to use in Kenya**
- Backup protection upstream of RCBOs (S-type for selectivity)
- Construction sites: 30mA on socket outlets, 500mA at origin (KS §704 adopts BS framework)
- Off-grid TT installations: 30mA RCD primary fault-disconnection device (KS §411.5.2)

---

## RCD types

| Type | Detects | Use case in Kenya |
|---|---|---|
| **AC** | Sinusoidal AC only | **Not recommended.** Will fail to detect DC residual current. |
| **A** | AC + pulsating DC | Standard for modern Kenyan installations. Required for electronic loads. |
| **F** | AC + pulsating DC + 1 kHz | Single-phase inverter loads (washing machines, single-phase heat pumps, single-phase solar inverters common in off-grid PV). |
| **B** | AC + DC + smooth DC + HF | Three-phase inverters, three-phase solar PV (Marsabit / Turkana commercial farms), EV charging without built-in DC detection. |

Solar-PV-heavy installations in Kenya should default to Type A as a
baseline and step up to Type F or B where the inverter datasheet shows
significant DC fault-current capability.

---

## HRC fuse — High Rupturing Capacity fuse (BS 88-3 or IEC 60269)

**Construction:** Sand-filled silver/copper element. Single-use.

**Ratings**
- In: 6 to 1250 A common range
- Breaking capacity: 80 or 120 kA typical — much higher than MCBs
- Class: gG (general), aM (motor only)

**When to use in Kenya**
- Submain protection where KPLC declared PFC + downstream rise exceeds MCB Icn
- KPLC service heads (KPLC standard practice on industrial supplies)
- Motor protection (gG or aM with overload relay)
- Industrial installations across Industrial Area Nairobi, Athi River, Mombasa industrial zones

**Practical note:** Spare fuses must be kept on site. Replacement after
operation is a maintenance overhead — often the deciding factor against
HRC fuses on sites without dedicated maintenance staff.

---

## MCCB — Moulded Case Circuit Breaker (KS §531 — BS EN 60947-2 or IEC 60947-2)

**Construction:** Industrial circuit breaker in a moulded case. Adjustable thermal-magnetic trip or electronic trip unit.

**Ratings**
- In: 16 to 3200 A
- Breaking capacity: Icu 25 to 100 kA typical; Ics typically 50–75% of Icu
- Trip units: thermal-magnetic (simple) or electronic LSIG (Long-time, Short-time, Instantaneous, Ground fault) for selectivity studies

**When to use in Kenya**
- Main switchboard incomers and outgoing ways (typically ≥ 100 A)
- Sub-distribution board incomers
- Motor protection with electronic trip
- Anywhere adjustable trip settings are needed for selectivity

---

## ACB — Air Circuit Breaker (KS §531 — BS EN 60947-2 or IEC 60947-2)

**Construction:** Open-frame breaker for very high currents.

**Ratings**
- In: 630 to 6300 A
- Icu: 50 to 150 kA

**When to use in Kenya**
- Main incomer of large MSBs (typically > 1000 A) — large commercial towers (Upper Hill, Westlands), large industrial loads, KPLC substations
- Tie breakers between MSB sections
- Generator outgoing breakers (common in Kenya given KPLC supply reliability — virtually every commercial premises has a backup generator with ATS)

---

## AFDD — Arc Fault Detection Device

KS 1700:2018 does **not** mandate AFDDs. BS 7671 AMD 1 (2020) introduced
AFDD recommendations; this has not yet been incorporated into KS 1700.
Engineers may specify AFDDs as informative guidance under KS §1.6
(engineering judgement) for sleeping accommodation, timber-frame
construction, etc.

The next KS 1700 revision is expected to incorporate AFDDs formally.

---

## Device selection decision tree (Kenya practice)

```
Final circuit?
├── YES
│   ├── Socket outlet ≤ 32A?     → RCBO 30mA (MANDATORY per KS §411.3.3)
│   ├── Bathroom / kitchen?      → RCBO 30mA
│   ├── Outdoor circuit?         → RCBO 30mA (Kenya humidity → leakage risk)
│   ├── Other final ≤ 100A?      → MCB if RCD not required, else RCBO
│   └── Final circuit > 100A?    → MCCB
└── NO (distribution circuit)
    ├── Up to ~125A?              → MCCB or MCB if Icn sufficient
    ├── 125 to 1000A?             → MCCB (electronic trip for selectivity)
    └── Above 1000A?              → ACB
```

---

## Common errors in Kenya practice

- MCB used on socket circuit instead of RCBO — non-compliant with KS §411.3.3.
- Device without KEBS certification mark installed — non-compliant; EPRA inspection failure.
- Type AC RCD specified for a load with single-phase inverter content (solar inverter, modern washing machine) — DC residual fault not detected.
- Choosing MCB Icn below site PFC declared by KPLC — device cannot interrupt fault safely. Always check the KPLC Letter of Information PFC before specifying Icn.
- Mixing manufacturers in cascade and claiming selectivity — only manufacturer-tested combinations are guaranteed.
- Specifying ACB where MCCB would suffice — unnecessary cost and space.

---

## See also

- `KS1700/terminology.md` — KEBS + KPLC vocabulary
- `KS1700/compliance-checklist.md` — §411 RCD additional-protection checklist
- `KS1700/pscc-determination.md` — PFC values that drive Icn selection
- `KS1700/appendix3-device-curves.json` — Type B / C / D MCB curves (adopted from BS verbatim)
- `BS7671/protective-device-types.md` — parent BS text adopted by KS Annex E
- `KS1700/ks-unique-deviations.json` — §411.3.3 universal socket-RCD deviation
