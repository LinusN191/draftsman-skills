# Reasoning — INT TT Vineyard Cottage

## Step 1 — Discovery
Single consumed intent: db-layout. lighting-layout and small-power not provided — generator must work from db-layout outgoing_circuits alone. This is acceptable for rural/simple installations.

## Step 2 — Standards files loaded
Jurisdiction is INT. Loading:
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json`
- `shared/standards/electrical/IEC60364/part5-54-earthing.json`
- `shared/standards/electrical/IEC60364/earthing-systems.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

BS 7671 and NFPA 70 NOT loaded.

## Step 3 — Earthing system
TT declared. Ontology lookup → TT requires ≥1 electrode at the installation; RCD blanket-required.
IR emits `earthing_system: { system_type: "TT", code_clause: "IEC 60364-4-41 clause 411.5" }`.

## Step 4 — MET location
Service intake cupboard, NW corner. `supply_bond_type: "consumer_electrode_only"` (TT — no supply earth bond). Main earthing conductor 10 mm² Cu.

## Step 5 — Electrode arrangement
Engineer has declared two rods in parallel, 1500mm each. Target Ra 100Ω.
- IEC 60364-4-41 411.5.3: disconnection time satisfied if Ra·IΔn ≤ 50V → with 30mA RCBO, Ra_max = 1667Ω; engineer target 100Ω gives huge headroom.
- `electrodes[0].tool_call_pending: true` — calc.electrode_resistance not yet implemented; engineer-input Ra accepted.

## Step 6 — Main bonding
LPG fuel pipe (external) declared as extraneous-conductive-part → 1 bond at 10mm² Cu per IEC 60364-5-54 Clause 544.

## Step 7 — Supplementary bonding
None declared.

## Step 8 — CPC sizing (IEC 60364-5-54 Table 54.2)
Table method per IEC 60364-5-54 Clause 543.1.1:

| Circuit | L csa | CPC csa | Method |
|---|---|---|---|
| C01 lighting | 1.5 | 1.5 | iec60364_table_54.2 |
| C02 sockets | 2.5 | 2.5 | iec60364_table_54.2 |
| C03 pump | 4.0 | 4.0 | iec60364_table_54.2 |

## Step 9 — Zs verification
TT system Zs = Ze + R1 + R2. For TT, the disconnection time check uses Ra·IΔn ≤ 50V rule (411.5.3). All circuits pass with RCD.

## Step 10 — RCD
All three circuits have 30mA RCBO. IEC 60364-4-41 411.5.3 satisfied for every circuit.

## Step 11 — Compliance
No flags — design is fully compliant. Compliance assumption captured: soil resistivity 100 Ω·m (loam typical).

## Step 12 — Rationale block emitted.
