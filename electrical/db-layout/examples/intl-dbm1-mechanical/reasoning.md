# Reasoning — INT DB-M1 (Mechanical/HVAC Sub-DB)

## Site context

Mechanical sub-DB serving HVAC plant on the generic IEC commercial 3-storey office building. DB-M1 sits in the rooftop plantroom adjacent to the air-handling units, chilled-water plant, and kitchen extract. Fed from MSB-MAIN F03 (250A MCCB Type D, 45m feeder).

The mechanical DB is the second-largest of the four sub-DBs downstream of MSB-MAIN — typical of a Grade-A office where the HVAC plant carries comparable load to the lighting DB but with very different inrush + protection characteristics.

## Board sizing — 250A TPN intake

Connected mechanical load:
- 2× AHU supply fans @ 11 kW = 22 kW
- 2× AHU extract fans @ 7.5 kW = 15 kW
- Chilled water pump @ 5.5 kW
- Kitchen extract fan @ 4 kW
- FCU control panel + condensate pump = 3.5 kW
- **Total connected ≈ 50 kW**

Diversified demand: HVAC plant runs ≥95% of design load during peak cooling — no significant diversity available. After-diversity demand ≈ 48 kW. Design current = 48,000 / (√3 × 400 × 0.85) ≈ 81A.

Adding a 30% growth/inrush headroom: ~105A. The 250A intake provides comfortable headroom and matches the upstream MSB-MAIN F03 MCCB rating directly. Generous spare-way provision for VRF expansion or additional FCU banks.

IP54 enclosure rating selected for the plantroom environment — dust, moisture, oil mist exposure exceeds the IP4X indoor-office spec.

## Motor circuit protection strategy

M01-M06 are 3-phase motor circuits. The DB-M1 MCB provides **short-circuit protection only** — overload protection is delegated to the local motor starter/VSD downstream:

| Circuit | Motor | Local protection | DB-M1 MCB |
|---------|-------|------------------|-----------|
| M01 | AHU-1 supply 11kW | DOL starter with Class 10A thermal overload (IEC 60947-4-1) | 32A Type D MCB (SC only) |
| M02 | AHU-1 extract 7.5kW | DOL starter + thermal overload | 25A Type D MCB |
| M03 | AHU-2 supply 11kW | DOL or VSD with electronic overload | 32A Type D MCB |
| M04 | AHU-2 extract 7.5kW | DOL or VSD | 25A Type D MCB |
| M05 | CHW pump 5.5kW | DOL with thermal overload | 20A Type C MCB |
| M06 | Kitchen extract 4kW | DOL with thermal overload | 16A Type C MCB |

The motor starter / VSD at each motor location handles:
- Thermal overload protection (Class 10A or 20)
- Lock-out / tag-out isolation
- Phase failure detection
- Soft-start or VSD speed control where specified

The DB-M1 MCB protects the cable run from the DB to the starter against short-circuit and acts as the upstream isolation point.

## MCB curve selection

- **Type D (Ia = 20×In)** on M01-M04 — full-voltage DOL starting of AHU fans produces ≈6-8× FLC inrush for ≈100ms. Type D Ia band (10-20×In) accommodates this without nuisance trip. Type C would risk tripping on hot restart.
- **Type C (Ia = 10×In)** on M05 (CHW pump) and M06 (kitchen extract) — smaller motors with gentler inrush profile suit Type C; tighter earth-fault loop protection than Type D.
- **Type B (Ia = 5×In)** on M07 (FCU control panel feed) — non-motor circuit serving a control panel transformer + 24V auxiliary supply. Standard light-load Type B.
- **Type C (Ia = 10×In)** on M08 (single-phase condensate pump) — small motor with brief inrush; Type C suits.

## RCD strategy — selective application

| Circuit | RCD? | Justification |
|---------|------|---------------|
| M01-M06 (3-ph fixed motors) | **No** | IEC 60364-4-41 Clause 411.3.3 socket-RCD policy does NOT apply to fixed-equipment 3-phase motor circuits with local lock-out isolation. RCDs on motor circuits are also prone to nuisance tripping from VSD common-mode leakage currents. |
| M07 (FCU control feed) | **30mA Type A** | Control panel supply is socket-equivalent (operator-accessible isolator + future modification potential). Type A handles BMS controller SMPS leakage. |
| M08 (condensate pump) | **30mA Type A** | Single-phase, ceiling-void mounting accessible for maintenance access — socket-equivalent. |

For M03/M04 (potential future VSD), an additional consideration: VSD common-mode leakage on the DC bus can exceed 30mA in steady state. If a VSD is procured, the upstream MCB should remain RCD-free OR an industrial 300mA Type B RCD with delay can be specified (IEC 60364-7-722 EV charging-style approach). This is flagged in the assumptions block for future verification.

## Cable selection — 5-core SY PVC Cu

All motor circuits (M01-M06) use 5-core SY (steel-wire shielded) PVC Cu cable. SY screening:
- Provides EMC containment (important for VSD-fed motors to limit conducted emissions per IEC 61800-3)
- Acts as a CPC (5th core dedicated earth + screening braid for double earthing)
- Mechanically robust for plantroom routing

Cable sizes selected per IEC 60364-5-52 Annex B Reference Method C (clipped direct on cable tray or in conduit):
- 11 kW motor (FLC ≈ 21A): 6mm² → tabulated ampacity ≈ 36A → comfortable
- 7.5 kW motor (FLC ≈ 14.5A): 4mm² → tabulated ≈ 27A → comfortable
- 5.5 kW motor (FLC ≈ 10.5A): 2.5mm² → tabulated ≈ 20A → adequate
- 4 kW motor (FLC ≈ 8A): 2.5mm² → comfortable
- 1.5 kW single-ph (FLC ≈ 6.5A): 1.5mm² → 14A → adequate

## Selectivity verification

Upstream MSB-MAIN F03 = 250A MCCB Type D. Downstream MCBs at DB-M1 are ≤32A Type C/D:
- Current ratio: 250/32 = 7.8:1 — above the 2.5:1 selectivity minimum
- Curve coordination: Type D upstream with Type D downstream needs particular care because Ia bands overlap. Manufacturer cascade table must be consulted; for typical ABB/Schneider/Hager ranges, the 250A MCCB has long-time + short-time delay (LSI trip unit) that gives time-current selectivity against the instantaneous-only MCBs downstream
- Manufacturer cascade table required for confirmation at 25 kA fault level (engineer-declared; verification deferred to fault-level skill)

Verdict: pass with the caveat that Type D-to-Type D pairing requires cascade-table confirmation.

## Breaking capacity

Declared PFC at DB-M1 ≈ 14 kA. 10 kA Icn MCBs with cascade backup from upstream 250A MCCB Icu ≥ 25 kA per IEC 60364-5-53 Clause 536.4. Engineer must verify cascade pairing on the procured manufacturer's published cascade table.

## Phase balancing

3-phase motors (M01-M06) inherently balance across L1/L2/L3. Single-phase loads:
- M07 (BMS control) on L1: 2 kW
- M08 (condensate pump) on L2: 1.5 kW

L3 has no single-phase contribution. Net imbalance: ≤2 kW over a 50 kW total = 4% — well within Clause 314 guidance.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade, Phase B of SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify feeder + 8 motor-circuit cables against IEC 60364-5-52
- (Future) `electrical/fault-level/` — cascade fault current and Zs at each motor terminus
- (Future) `electrical/load-schedule/` — mechanical equipment schedule integration with HVAC consultant

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F03 feeder)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — lighting sub-DB)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire alarm panel)
