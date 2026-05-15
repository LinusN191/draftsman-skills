# IEC 61439 — Worked Examples

Four worked examples illustrating how designers apply IEC 61439. Each example walks the schedule entry → verification chain → handover documentation.

---

## Example 1 — Form 3b PSC-Assembly verification chain

**Project:** 8-storey commercial office. Main LV switchboard fed from a 1250 kVA, 11 kV / 415 V transformer.

### Step 1 — Designer specifies

| Field | Value | Source |
|---|---|---|
| Assembly designation | MSB-01 per IEC 61439-2:2020 | designer |
| Form | 3b | designer choice (single-circuit maintenance with rest live) |
| Ue | 400 V (3φ + N + PE) | DNO supply |
| Ui | 1000 V | per Part 1 |
| Uimp | 6 kV (overvoltage category IV) | designer (MSB is OVC IV) |
| In | 2500 A | designer's load schedule |
| Icw / time | 50 kA / 1 s | calculated from transformer Z = 6 %, Sn = 1250 kVA: Isc = 1250 × 1000 / (√3 × 415 × 0.06) = 29 kA. Designer rounds up to standard 50 kA / 1 s. |
| Ipk | 105 kA peak | from Icw via n-factor at PF 0.25 → n = 2.1 → Ipk = 2.1 × 50 = 105 kA |
| fn | 50 Hz | UK |
| IP / IK | IP2X (front) / IP30 (enclosure) / IK08 | indoor plant room |
| IAC | AB FL 50 kA / 0.5 s | designer (occupied building, front + lateral access) |
| RDF | 0.85 | designer's diversity assessment |

### Step 2 — OEM verification path

OEM (Schneider, Prisma iPM) presents:
- Type-test certificate for the Prisma iPM Form 3b at 50 kA / 1 s, 2500 A.
- IAC test certificate at 50 kA / 0.5 s.
- Annex E temperature-rise calculation showing the specific outgoer mix passes at RDF 0.85.
- Annex D bounding comparison showing this build (2500 A, 50 kA, RDF 0.85, IAC AB FL) falls within the verified envelope.

### Step 3 — AM build

Licensed UK panel-builder constructs the assembly using Prisma iPM verified design. Provides routine-verification test records (insulation, polarity, functional) at handover.

### Step 4 — Handover documentation pack

- OEM verification declaration (signed by Schneider)
- Annex E calculation report (Schneider)
- Annex D bounding comparison (Schneider)
- Type-test certificate summary (Schneider)
- IAC test certificate (Schneider)
- As-built single line, GA, terminal schedule (AM)
- Routine test records (AM)
- BSRIA BG 29 O&M (AM, building O&M consultant)

---

## Example 2 — IAC accessibility for an MCC

**Project:** Industrial MCC for a sewage treatment plant. Maintenance personnel are skilled. The MCC sits in a dedicated electrical room.

### Designer's IAC decision

| Question | Answer | Implication |
|---|---|---|
| Is the room accessible to the public? | No | Class A acceptable (skilled persons only) |
| What direction can the OEM access? | Front only (back is against a wall) | Accessibility type F |
| What is the prospective fault current? | 36 kA | Icw test current = 36 kA |
| What is the upstream protection clearing time? | ACB with short-time delay 0.3 s | IAC test duration ≥ 0.3 s, round to 0.5 s |

**Result:** Specify IAC AF 36 kA / 0.5 s.

### What this means in practice

The OEM verifies that during a 36 kA fault for up to 0.5 s, with the door closed:
- No flame or hot gas escapes through the door
- No ignition occurs at the front of the MCC
- The door does not detach
- Earthing remains continuous

If the room were occupied by ordinary persons during operation (a public-accessible substation room), Class B would be required. If access were possible from sides or rear, accessibility would be FL, FR, or FLR.

---

## Example 3 — Busbar derating for a 4000 A board at 45 °C ambient

**Project:** Data centre MSB rated 4000 A at standard 35 °C 24-h average ambient. Installation in a plant room where ambient runs at 45 °C 24-h average.

### Step 1 — Ambient correction factor

From `temperature-rise.json` ambient correction formula with max rise 55 K for busbars:
```
Kt = sqrt((55 + 35 − 45) / 55)
   = sqrt(45 / 55)
   = sqrt(0.818)
   = 0.905
```

### Step 2 — Derated In

Derated In = 4000 × 0.905 = **3620 A** at 45 °C ambient.

### Step 3 — Designer's options

Option A: Accept derating. Specify In = 4000 A on the assembly but apply a 3620 A operational limit in the BMS. Cheap; constrains future load growth.

Option B: Specify In = 4400 A at 45 °C ambient. OEM upsizes the busbar to compensate. Higher cost; preserves headroom.

Option C: Improve ambient (ventilation / cooling) so 35 °C 24-h average is achieved. Capex on HVAC; preserves the standard rating.

### Step 4 — Verification documentation

Whichever option is chosen, the OEM provides an Annex E calculation showing the busbar's temperature rise at the design ambient remains ≤ 55 K above ambient (90 °C absolute peak). If Option B is chosen, the OEM may need a reference-design certificate covering 4400 A or a fresh test.

---

## Example 4 — Icw coordination with upstream MCCB

**Project:** Sub-DB on the 8th floor of the office building from Example 1. Fed from the main switchboard at the building base via 50 m of 3-phase busduct.

### Step 1 — Fault current at sub-DB

From PSCC calculation chain (per IEC 60364-4-43): the fault current at the 8th-floor sub-DB drops to **18 kA prospective** due to busduct impedance.

### Step 2 — Designer's selectivity strategy

Upstream MCCB at the MSB end of the busduct is set with short-time delay (STD) 0.2 s and a magnetic instantaneous threshold at 30 kA (above the 18 kA prospective at the sub-DB).

Sub-DB MCCB at the 8th floor must clear faults at 18 kA without waiting for the upstream STD.

### Step 3 — Sub-DB Icw specification

Designer specifies sub-DB Icw = 18 kA / 0.2 s (matching the upstream STD time). This guarantees the sub-DB withstands 18 kA for the duration that selectivity requires.

If the sub-DB used a fuse-protected feeder instead, Icc would apply: the designer would specify Icc 18 kA conditional on the upstream BS88 cut-out, and the OEM's verification would document the fuse's let-through.

### Step 4 — Common error to avoid

A naive specification of "Icw = 18 kA / 1 s" would force the OEM to verify the sub-DB at 18 kA for a full second. This is more expensive than necessary (because the upstream STD is only 0.2 s) and may push the assembly into a larger frame size. Specify Icw matched to the actual selectivity delay.

---

## Cross-references across these examples

| Topic | Used in Example | Layer file |
|---|---|---|
| Form 3b | Example 1 | `form-separations.json` (FORM_3B), `part2-psc-assemblies.json` (PSC_ASSEMBLY_FORM_3B) |
| IAC classification | Example 2 | `internal-arc-classification.json` |
| Busbar derating | Example 3 | `busbar-derating.json`, `temperature-rise.json` |
| Icw coordination | Example 4 | `short-circuit-withstand.json` |
| n-factor for Ipk | Example 1 | `short-circuit-withstand.json` (rated_characteristics.Ipk.n_factor_table) |
| RDF | Example 1 | `temperature-rise.json` (rated_diversity_factor_RDF) |
| Annex E verification | Examples 1 & 3 | `verification-methods.json` (CALC method), `temperature-rise.json` |
| Annex D bounding | Example 1 | `verification-methods.json` (REFERENCE method) |
