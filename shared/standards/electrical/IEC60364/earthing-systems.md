# IEC 60364 Earthing Systems Explained

Reference for TN-S, TN-C, TN-C-S, TT, and IT earthing systems — when to use each,
how to identify the system on site, and key design implications.

---

## System coding

The two-letter code describes the earthing arrangement at two positions:

**First letter — supply earth:**
- **T** (*Terra*) — the supply transformer neutral is directly connected to earth
- **I** (*Isolé/Isolated*) — the supply is isolated from earth, or connected through a high impedance

**Second letter — consumer earth:**
- **T** (*Terra*) — the consumer has a separate, independent earth electrode
- **N** (*Neutral*) — the consumer earth is derived from the supply neutral conductor

**Optional third letter — N conductor arrangement in TN:**
- **S** (*Separate*) — neutral (N) and protective earth (PE) are separate conductors throughout
- **C** (*Combined*) — neutral and PE functions combined in a single PEN conductor
- **C-S** — combined upstream, separate downstream (split at consumer's main earthing terminal)

---

## TN-S — Separate N and PE throughout

```
TRANSFORMER             DISTRIBUTION            CONSUMER
                         NETWORK                INSTALLATION
    L ────────────────────────────────────────── Load
    N ──────────────────────────────────────────
    │                    │                       │
    ═══ (earth)         N │  PE │               MET
                          └────┘                 │
                     Separate N and PE          Load exposed
                     conductors                 metal parts
```

**Supply earth:** Transformer neutral earthed at transformer.
**Consumer earth:** Separate PE conductor from transformer earth, running alongside the supply cables. Never electrically connected to neutral within the consumer's installation.

**Characteristics:**
- No current flows in PE under normal conditions — PE is a fault-only conductor
- Cleanest earth reference — ideal for sensitive equipment, VFDs, instrumentation
- Earth fault current returns via PE (low impedance) — fast disconnection by overcurrent devices
- Fault loop impedance is low (L → fault → PE → transformer) — MCBs can trip within 0.4s

**Where used:**
- Industrial installations with sensitive instruments, drives, or data
- Medical facilities (Group 2 operations often use IT, but other areas TN-S)
- Data centres
- New commercial buildings where the utility provides a TN-S supply
- Some parts of continental Europe (Germany, Netherlands as TNS)

**Design implication:** Specify 4-core or 5-core SWA cables with separate N and PE cores. Do NOT share N and PE at any point downstream of the split.

---

## TN-C — Combined PEN conductor

```
TRANSFORMER             DISTRIBUTION
                         NETWORK
    L ─────────────────────────────── Load
    PEN ──────────────────────────────
    │                    │
    ═══ (earth)         PEN conductor
                        (carries both N current
                        and earth function)
```

**Supply earth:** Transformer neutral earthed at transformer.
**Consumer earth:** A single PEN conductor carries both neutral current AND protective earth function throughout.

**Restriction: NOT PERMITTED in consumer installations (IEC 60364-5-54 Clause 543.4.1). Only in fixed distribution networks.**

**Why it is dangerous:**
If the PEN conductor breaks (corroded joint, mechanical damage), the exposed metalwork of all equipment connected to PEN becomes live at phase voltage. This has caused fatalities.

**Where found:**
- Older utility distribution networks (Europe, Africa)
- Historical internal wiring of industrial buildings (pre-1980s)
- Never in new consumer installations

---

## TN-C-S — Combined upstream, separate downstream (PME)

```
TRANSFORMER         UTILITY NETWORK           CONSUMER'S INSTALLATION
    L ──────────────────────────────── L ────────────── Load
    PEN ─────────────────────────────  │
    │               (PEN underground)  │ MET (split point)
    ═══ (earth)                        ├── N (neutral to loads)
                                       └── PE (earth to all metalwork)
                                                │
                                           Exposed conductive
                                           parts of equipment
```

**Supply:** PEN conductor in utility network (DNO's cables).
**Split:** At the consumer's Main Earthing Terminal (MET), the PEN is split: N continues as the neutral conductor, and PE is derived as a separate earth conductor.
**Within installation:** All wiring uses separate N and PE — same as TN-S within the building.

**This is the dominant earthing system in:**
- United Kingdom (where it is called PME — Protective Multiple Earthing)
- Nigeria, Kenya, Ghana, South Africa (urban areas)
- Much of Asia and the Middle East
- Most of continental Europe at low voltage

**Advantages:**
- DNO provides earth via the neutral — no separate earth electrode cable needed
- Low fault loop impedance — fast disconnection
- Cost-effective

**PME hazard:**
If the PEN conductor (supply neutral) upstream breaks, the consumer's MET rises to phase voltage. All bonded metalwork (gas pipes, water pipes, structural steel) becomes live. This is the PME hazard.

**Mitigation:**
- Multiple earthing points on the PEN along the distribution route reduce the chance of the whole neutral breaking and limit voltage rise
- Supplementary earth electrode at the consumer is recommended to limit voltage rise
- Not suitable for TN-C-S in areas with long overhead lines, high soil resistivity, or poor maintenance

**Where TN-C-S is NOT appropriate:**
- Rural areas with long overhead distribution lines (broken neutral risk is higher)
- Locations where water surfaces or significant water exposure exists — marinas, outdoor pools (broken neutral + water = extreme hazard)
- For these locations, TT with RCDs is safer

---

## TT — Separate independent earth electrode

```
TRANSFORMER         UTILITY NETWORK           CONSUMER'S INSTALLATION
    L ──────────────────────────────── L ──────────────── Load
    N ──────────────────────────────── N
    │                                          │
    ═══ (supply earth                     ═══ Consumer's
         at transformer)                       earth electrode
                                           (completely separate)
```

**Supply earth:** Transformer neutral earthed at transformer (utility).
**Consumer earth:** Completely independent earth electrode at the consumer's site — no electrical connection to the supply neutral.

**Key characteristic:** Earth fault current must flow through: supply transformer neutral earth → soil → consumer's earth electrode. The total impedance is the sum of two earth electrode resistances — typically 20–1000Ω. This is too high for overcurrent devices to trip reliably within 0.4s.

**Therefore: RCDs are MANDATORY for ALL circuits in TT systems.**

For 30mA RCD: Zs_max = U0 / IΔn = 230 / 0.030 = 7667Ω — always satisfied regardless of electrode resistance.

**Advantages:**
- No PME hazard — consumer earth is independent of supply neutral
- Safer where overhead supply lines are used (broken neutral doesn't affect consumer earth)
- Preferred for rural, coastal, and agricultural installations
- Required at marinas, caravan parks, and construction sites

**Design implications:**
- EVERY circuit requires a 30mA RCD (or 300mA RCD for distribution with 30mA downstream)
- Earth electrode must be designed and tested — target Ra ≤ 200Ω (50Ω preferred)
- Select RCDs carefully — Type A for all circuits with electronic loads

**Common in:**
- Rural Africa (where overhead poles distribute power)
- Nigeria rural areas outside city limits
- Kenya, Tanzania, Uganda rural supplies
- Old European installations in countries that never migrated to TN-C-S
- France (the dominant TT country — NF C 15-100 requires TT for residential)

---

## IT — Isolated supply (Impedance-earthed)

```
TRANSFORMER         DISTRIBUTION
    L ──────────────────────────── Load A     Load B
    N          │                   ══════      ══════
               Z                    │          │
               │                   PE          PE
              ═══                    │          │
          (High-impedance              └────────┘
           or unearthed)                   │
                                          MET
                                           │
                                          ═══
```

**Supply:** Neutral is isolated from earth (or earthed through high impedance Z, typically 1000Ω or more).

**First fault:** Earth fault current is limited to the current through the supply impedance — typically < 1A. The installation continues operating. An insulation monitoring device (IMD) gives an alarm.

**Second fault (before first fault is repaired):** Two faults create a fault loop independent of earth — treated like a TN fault. Disconnection is required. This drives the critical importance of locating and repairing the first fault promptly.

**Where used:**
- **Medical locations Group 2** (IEC 60364-7-710) — operating theatres, intensive care. A first fault cannot cause disconnection mid-surgery. IMD gives alarm; surgeon knows to finish the procedure while fault is found.
- Semiconductor fabrication (cannot afford sudden power interruption)
- Offshore platforms (limited earth reference available)
- Arc furnace circuits (functional isolation for process control)

**IMD requirement:** Every IT system must have an Insulation Monitoring Device that continuously measures the insulation resistance between live conductors and earth, and alarms when it falls below a threshold (typically 50kΩ for medical).

---

## Selecting the earthing system

| Factor | TN-S | TN-C-S | TT | IT |
|--------|------|--------|----|----|
| Supply provided by DNO | Usually TN-C-S or TN-S — DNO determines, not designer | | | |
| Urban area with underground cables | ✓ Best | ✓ Common | ✓ OK | — |
| Rural area with overhead lines | Avoid | Avoid (PME hazard) | ✓ Best | — |
| Sensitive electronics / instrumentation | ✓ Best | ✓ Good | ✓ Good | — |
| Medical Group 2 | — | — | — | ✓ Required |
| Marina / caravan park | — | Avoid | ✓ Required | — |
| Agriculture | Possible | Avoid | ✓ Preferred | — |
| Data centre | ✓ Best | ✓ Good | ✓ OK | — |
| Must maintain supply on first fault | — | — | — | ✓ Required |

---

## Identifying the earthing system on site

**At the main distribution board:**

1. **Is there a separate green-yellow PE conductor coming in from the street supply?**
   - Yes → Could be TN-S
   - No → Could be TN-C-S or TT

2. **Is the N and PE bar connected together or separate?**
   - Connected at MET only → TN-C-S (split here)
   - Completely separate throughout → TN-S
   - N and PE completely separate, with only a local earth rod → TT

3. **Is there an earth electrode (rod, tape) connected?**
   - Yes + supply earth also present → TN-C-S with supplement, or TT
   - Only earth electrode, no supply earth → TT

4. **Ask the DNO or utility:** They know what earthing arrangement their network provides. For projects in Nigeria, Kenya, South Africa: check with the DISCO/utility which system is provided at the point of supply.

---

## Key regulatory reference

- **IEC 60364-1** — System classification and coding
- **IEC 60364-4-41** — Protection requirements for each system type
- **IEC 60364-5-54** — Earthing arrangements, electrode sizing, bonding
- **IEC 60364-7-701** (bathrooms), **7-705** (agricultural), **7-708** (marinas), **7-710** (medical) — system-specific requirements
