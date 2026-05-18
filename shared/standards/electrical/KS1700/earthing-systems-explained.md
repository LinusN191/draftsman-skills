# Earthing Systems Under KS 1700:2018

> **Verification note:** This file is authored as a draft-from-bs7671-derivative.
> KS 1700:2018 §411.4 adopts the BS 7671 / IEC 60364 system definitions
> substantially via KS Annex E. Promote `verification_status` once verified
> clause-by-clause against the published KS 1700:2018 PDF.

The earthing system is the most consequential choice in any Kenyan
electrical design. It dictates the protection strategy, the cable sizes,
and the verification regime. KPLC supply characteristics in Kenya differ
materially from UK DNO defaults — recognising the actual supply type at
the intake is the first design step.

---

## Kenya supply context

KPLC (Kenya Power and Lighting Company) is the primary distribution
network operator. The supply type encountered at any given site depends
on the area, the era of the network build-out, and whether the supply is
on-grid or off-grid:

- **TN-C-S (PME)** is the modern KPLC default for urban domestic and
  commercial supplies (Nairobi, Mombasa metro, Nakuru, Kisumu, Eldoret).
  Declared Ze typically 0.20–0.35 Ω.
- **TN-S** is found on legacy industrial supplies, particularly older
  Industrial Area Nairobi feeders, some Athi River industrial estates,
  and dedicated transformer supplies. Declared Ze typically 0.65–1.0 Ω.
- **TT** is the default for off-grid and rural supplies — overhead LV
  spurs in rural Kenya, solar-PV island installations, and any site
  where KPLC does not provide an earth at the intake.
- **IT** is rare in Kenya outside specialist installations (hospital
  operating theatres, some marine/oil-and-gas facilities).

KPLC declares the earthing arrangement on the Letter of Information
issued at supply connection. The Ze and PFC are recorded against the
KPLC Wayleave reference (e.g. `KPLC-NRB-IND-2143`).

---

## The five systems (KS §411.4)

KS 1700 follows IEC 60364 and recognises five earthing arrangements
identified by two-letter codes:

- **First letter** — relationship between supply and earth:
  - `T` (Terra) — directly earthed point at the supply
  - `I` (Isolated) — supply isolated from earth, or earthed via high impedance
- **Second letter** — relationship between exposed-conductive-parts and earth:
  - `T` (Terra) — direct connection to a local earth electrode
  - `N` (Neutral) — connection to the neutral of the supply

When the second letter is `N`, additional letters describe the N and PE arrangement:

- `S` (Separate) — separate N and PE conductors
- `C` (Combined) — N and PE combined in a single PEN conductor

---

## TN-S

```
KPLC TRANSFORMER              CONSUMER PREMISES
     ║                              ║
     L ──────────────────────────→ L
     N ──────────────────────────→ N
     E ──────────────────────────→ PE
     │
     ▼ earth electrode at substation
```

Separate N and PE all the way from the supply transformer. The earth
conductor is typically the metallic sheath of the supply cable.

- Common on legacy KPLC industrial supplies (Industrial Area Nairobi, Athi River, Mombasa industrial zones).
- Typical Ze: 0.65–1.0 Ω.
- Earth integrity depends on the supply cable sheath — important when the supply cable is many decades old.

---

## TN-C-S (PME)

```
KPLC TRANSFORMER         CUTOUT       CONSUMER
     ║                     │              ║
     L ──────────────────→│─────────────→ L
     N─────                │              N
          ╲                │              ║
           PEN ───────────→│──┬──────────→ PE
                           │   ╲
                           │    bonded to MET, water, structural steel
     │
     ▼ earth electrode at substation
```

Combined PEN conductor from transformer to the cutout, split into N and
PE inside the consumer's premises. Modern KPLC default for urban
domestic + commercial supplies.

- Typical Ze: 0.20–0.35 Ω — low, gives high fault current and fast disconnection.
- KS §544 main bonding sized similarly to BS Table 54.8 (KS Annex E adopts verbatim).
- Open-PEN fault hazard applies identically to BS PME — bond all extraneous-conductive-parts at the intake.
- EV charging in Kenya is comparatively rare but growing; KS routes EV requirements via Annex E §VIII to IEC 60364-7-722. Open-PEN detection or TT-island is the same mitigation as under BS.

---

## TT

```
KPLC TRANSFORMER              CONSUMER PREMISES
     ║                              ║
     L ──────────────────────────→ L
     N ──────────────────────────→ N
     │                              │
     ▼ earth at substation          ▼ INDEPENDENT earth electrode (rod)
                                    │
                                    PE bus → exposed-conductive-parts
```

Independent earth electrode at the consumer. The most common system for
off-grid Kenya — rural farms, solar-PV islands, remote sites without
KPLC earth at the intake.

- Typical Ze: 20–200 Ω (much higher than TN).
- **RCD protection is mandatory** for fault disconnection per KS §411.5.2 (RA × IΔn ≤ 50V).
- Earth electrode resistance varies seasonally — Kenyan dry seasons (Jan–Mar, Jul–Sep) raise electrode resistance significantly; design for the dry-season worst case.
- For a 30mA RCD: theoretical max electrode resistance = 1667 Ω; design target ≤ 100 Ω for reliable operation.
- Solar-PV installations in arid northern Kenya (Marsabit, Garissa, Wajir) — use multiple rods + bentonite enhancement to reach the design target during dry season.

---

## TN-C and IT (brief)

- **TN-C** (combined PEN throughout the consumer installation) is **not permitted** for consumer installations under KS 1700, matching BS 7671.
- **IT** systems are uncommon in Kenya. Encountered in hospital operating theatres (Aga Khan, Nairobi Hospital, MP Shah, Kenyatta National Hospital Group 2 areas) and some specialist industrial process control. KS §710 adopts the BS medical-IT framework substantially.

---

## Choosing the system for Kenyan installations

| Building / context | Recommended system | Rationale |
|---|---|---|
| Urban domestic (Nairobi, Mombasa, Kisumu metro) | TN-C-S (PME) | KPLC default. Low Ze. |
| Industrial Area Nairobi (legacy) | TN-S | KPLC legacy supply; declared on Wayleave. |
| Rural overhead LV spur | TT | KPLC typically does not provide earth on rural overhead. |
| Off-grid solar PV (Marsabit, Turkana) | TT | No KPLC connection; consumer-owned earth. |
| Hospital operating theatre (Group 2) | IT (medical IT system) | Continuity of supply during first fault. KS §710. |
| Petrol station forecourt | TT for forecourt | Avoids PME open-neutral risk on forecourt equipment. |
| Construction site | TT, OR TN-S with isolating transformer | KS §704 adopts BS framework. |

---

## Practical design implications

**Cable sizing changes by earthing system:**
- TT: cable sizing rarely limited by Zs (RCD handles disconnection). Sized on current capacity + voltage drop.
- TN-S / TN-C-S: cable sizing must achieve Zs ≤ Zs_max for the protective device per KS Annex E (Tables 41.2 / 41.3 adopted verbatim).

**Bonding changes by system:**
- TN-C-S (PME): heavy main bonding per KS §544. Bond all incoming services (water mains, structural steel, lift rails).
- TN-S: lighter bonding sufficient.
- TT: bonding local to the equipotential zone; earth path is via electrode.

**Verification changes by system:**
- TN: measure Zs at every accessible point and compare to Zs_max per KS §6.
- TT: measure RA (earth electrode resistance) AND verify RCD operation. RA must satisfy RA × IΔn ≤ 50V.
- All systems: insulation resistance per KS §6.3 (mirrors BS Reg 643.3).

---

## Common errors in Kenya practice

- Designing for TN-S Ze values when the supply is actually modern TN-C-S — wastes cable.
- Designing for TN-C-S bonding when supply is actually TT (off-grid solar) — under-bonded but PE path is wrong.
- TT electrode sized only for wet-season measurements — fails in dry season (Jan–Mar, Jul–Sep) when soil resistivity rises 3–5×.
- Off-grid PV installations without an EPRA-registered inspection certificate — illegal to commission for occupied premises.
- Assuming KPLC Ze without the Letter of Information — engineers must request and retain the document.

---

## See also

- `KS1700/terminology.md` — KPLC + EPRA + KEBS vocabulary
- `KS1700/compliance-checklist.md` — §411 ADS checklist
- `KS1700/protective-device-types.md` — MCB/MCCB/RCBO/RCD selection in Kenya
- `KS1700/inspection-and-testing.md` — EPRA inspection regime
- `BS7671/earthing-systems-explained.md` — parent BS text adopted by KS Annex E
