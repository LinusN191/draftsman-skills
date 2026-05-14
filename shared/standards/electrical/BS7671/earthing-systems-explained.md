# Earthing Systems Under BS 7671

The earthing system is the most consequential choice in any electrical
design. It dictates the protection strategy, the cable sizes, and the
verification regime. Get this wrong and nothing else works.

---

## The five systems

BS 7671 follows IEC 60364 and recognises five earthing arrangements,
identified by two-letter codes:

- **First letter** — relationship between the supply and earth:
  - `T` (Terra) — directly earthed point at the supply
  - `I` (Isolated) — supply isolated from earth, or earthed via high impedance
- **Second letter** — relationship between exposed-conductive-parts and earth:
  - `T` (Terra) — direct connection to a local earth electrode
  - `N` (Neutral) — connection to the neutral of the supply

When the second letter is `N`, additional letters describe how N and PE are arranged:

- `S` (Separate) — separate N and PE conductors
- `C` (Combined) — N and PE combined in a single PEN conductor

---

## TN-S

```
DNO TRANSFORMER             CONSUMER PREMISES
     ║                            ║
     L ──────────────────────────→ L
     N ──────────────────────────→ N
     E ──────────────────────────→ PE
     │
     ▼ earth electrode at substation
```

**Separate N and PE all the way from the supply transformer.**

- Earth conductor is usually the metallic sheath of the supply cable, or a separate dedicated earth.
- Common in older UK installations and where supply is from an underground LV network with armoured cable.
- Typical Ze: 0.5–0.8 Ω.

**Pros**
- Clear separation prevents neutral currents from flowing through earth.
- Good fault performance.
- No PME-specific restrictions on bonding.

**Cons**
- Less common in modern UK supplies (DNOs prefer TN-C-S for cost).
- Earth integrity depends on the supply cable sheath — degraded sheath = degraded earth.

---

## TN-C-S (PME)

```
DNO TRANSFORMER             CUTOUT       CONSUMER
     ║                        │              ║
     L ──────────────────────→│─────────────→ L
     N─────                   │              N
          ╲                   │              ║
           PEN ──────────────→│──┬──────────→ PE
                              │   ╲
                              │    bonded to MET, water, gas, structure
     │
     ▼ earth electrode at substation
```

**Combined PEN conductor from transformer to the cutout. Split into N and PE inside the consumer's premises.**

- Standard UK suburban supply (Protective Multiple Earthing — multiple earth electrodes along the PEN network).
- Earth provided by the supply cable's combined PEN conductor.
- Typical Ze: 0.20–0.35 Ω. Very low — gives high fault current, fast disconnection.

**Pros**
- Lowest Ze of any common UK system → fastest disconnection.
- DNO favours it (cheapest supply infrastructure).

**Cons — significant**
- PEN conductor carries neutral current. Loss of PEN (open neutral) causes the exposed-conductive-parts to rise to dangerous voltage.
- Bonding requirements are stricter (Reg 544 main equipotential bonding to all incoming services — water, gas, structural metal, oil — sized per Table 54.8).
- **Not permitted for EV charging or caravans/boats** without specific risk mitigation (Reg 722, Reg 708, Reg 709). DNO open-PEN fault would energise the vehicle chassis.
- Sub-bonding requirements in bathrooms (Reg 701.415.2).

**PME-specific requirements**
- Main protective bonding conductor (10mm² typical for domestic, 16mm² where supply > 100A).
- All extraneous-conductive-parts entering the equipotential zone must be bonded.
- For EV charging: install dedicated earth electrode (TT island) OR use open-PEN detection device per Reg 722.411.4.1.

---

## TT

```
DNO TRANSFORMER             CONSUMER PREMISES
     ║                            ║
     L ──────────────────────────→ L
     N ──────────────────────────→ N
     │                            │
     ▼ earth at substation        ▼ INDEPENDENT earth electrode (rod)
                                  │
                                  PE bus → exposed-conductive-parts
```

**Independent earth electrode at the consumer. No connection between supply earth and consumer earth.**

- Used where the DNO does not provide an earth — rural overhead supplies, farms, some industrial sites, marinas.
- Earth is the consumer's own rod (or rods) into the ground.
- Typical Ze: 20–200 Ω. **Much higher** than TN systems.

**Pros**
- Open-PEN fault on supply network cannot energise consumer's parts.
- Required where DNO will not provide an earth.

**Cons**
- High Ze means fault current is too low for overcurrent devices to provide ADS.
- **RCD protection is mandatory** for fault disconnection — Reg 411.5 requires 50V touch voltage limit, achieved by 30mA or higher RCD coverage.
- Earth electrode resistance varies with soil moisture — wet vs dry seasons.
- Regular testing of earth electrode resistance required.

**TT design rules**
- RA × IΔn ≤ 50 V (touch voltage limit). For 30mA RCD: max electrode resistance = 1667 Ω. For 300mA: 167 Ω.
- Aim for ≤ 100 Ω earth electrode resistance for reliable operation.
- Use a Type S (time-delayed) RCD at the origin for selectivity with downstream RCDs.

---

## TN-C

```
DNO TRANSFORMER             CONSUMER PREMISES
     ║                            ║
     L ──────────────────────────→ L
     PEN ─────────────────────────→ PEN (combined throughout)
     │
     ▼ earth electrode
```

**Combined PEN conductor throughout — including inside the consumer's installation.**

- **Not permitted** for consumer installations in the UK under BS 7671. Listed for completeness.
- Found only in some industrial/utility installations where consumer-controlled busbar systems carry combined neutral-earth.

---

## IT

```
SUPPLY                       LOAD
     L1 ──────────────────────→
     L2 ──────────────────────→
     L3 ──────────────────────→
     N (optional) ────────────→
     │
     × no direct earth, OR
     ▼ earthed via high impedance (insulation monitoring)
```

**Live system isolated from earth, or earthed via a high impedance.**

- Used in healthcare (medical IT system in operating theatres, ICU, BS 7671 Section 710 Group 2), marine, mining, and some industrial process control.
- First earth fault does NOT cause disconnection — system continues to operate.
- Insulation Monitoring Device (IMD) detects the first fault and alarms.
- Designer must locate and repair the first fault BEFORE a second fault occurs.

**Pros**
- Continuity of supply through first fault — critical in surgery, refining processes, marine propulsion.
- Touch voltage during first fault is below 50V.

**Cons**
- Requires sophisticated insulation monitoring.
- More expensive — isolating transformer, IMD, trained operators.
- Second fault becomes a line-to-line fault with full short-circuit current — must be cleared by overcurrent device.

---

## Choosing the system

| Building / use | Recommended system | Rationale |
|----------------|--------------------|-----------|
| Single domestic dwelling (urban) | TN-C-S (PME) | DNO default. Low Ze. Beware EV bonding. |
| Single domestic dwelling (rural overhead) | TT | DNO typically supplies as TT in rural overhead networks. |
| Block of flats | TN-S or TN-C-S | TN-S preferred for landlord supply; TN-C-S common. |
| Commercial office | TN-S or TN-C-S | TN-S if DNO provides; TN-C-S more common in new builds. |
| Petrol filling station | TT for forecourt | Avoids PME open-neutral risk on forecourt equipment. |
| EV charging only | TT island within PME OR open-PEN detection | Reg 722. PME has open-PEN risk on vehicle chassis. |
| Construction site | TN-S with isolating transformer OR TT | Reg 704. Reduced low voltage (RLV 110V) for tools. |
| Hospital — general areas | TN-S | Standard. |
| Hospital — operating theatre (Group 2) | IT (medical IT system) | Reg 710. Continuity of supply during first fault is critical. |
| Marina / boat berth | TT per pontoon | Reg 709. Avoids PME risk on metal hulls. |
| Caravan park | TT per pitch | Reg 708. Same rationale. |
| Petrochemical / hazardous area | TN-S with no PME | Reg 717 plus DSEAR. PME prohibited in hazardous zones. |

---

## Practical design implications

**Cable sizing changes by earthing system:**
- TT: cable sizing is rarely limited by Zs (RCD handles disconnection). Sized on current capacity and voltage drop.
- TN-S / TN-C-S: cable sizing must achieve Zs ≤ Zs_max for the protective device. Long runs may need upsized cables purely for fault loop.

**Bonding changes by system:**
- TN-C-S (PME): heavy main bonding required (Table 54.8). All incoming services bonded.
- TN-S: lighter bonding sufficient (Table 54.7 — main bonding sized per CPC).
- TT: bonding is local to the equipotential zone; earth path is via electrode, not the supply cable.

**Verification changes by system:**
- TN: measure Zs at every accessible point. Compare to Zs_max.
- TT: measure RA (earth electrode resistance) AND verify RCD operation. Compare RA to 50/IΔn.
- All systems: insulation resistance to Reg 643.3.

---

## Common errors

- Designing for TN-S Zs values when the supply is actually TN-C-S — wastes cable.
- Designing for TT bonding when supply is PME — under-bonded, non-compliant.
- Forgetting EV charging open-PEN risk on PME supplies — major safety issue.
- Sizing TT cables on Zs (using overcurrent device tables) when RCDs handle disconnection — over-sized cables.
- Assuming Ze without measurement on TT supplies — the assumed value is often wildly wrong.
- Bonding requirements in special locations (bathrooms, swimming pools) overlooked — frequent inspection finding.
