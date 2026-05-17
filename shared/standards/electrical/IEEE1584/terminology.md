# IEEE 1584 — Terminology

Glossary of arc-flash analysis terms used in this standards layer.

## Core quantities

- **Incident energy (E)** — Heat energy per unit area at a specified working distance during an arc-flash event. Units: cal/cm² (calories per square centimetre) or J/cm². Engineers use cal/cm² as the working unit; 1 cal/cm² ≈ 4.184 J/cm². The threshold for second-degree skin burn through bare exposure is **1.2 cal/cm²**.

- **Arc-flash boundary (AFB / D_arc)** — The distance from the arcing source at which incident energy equals 1.2 cal/cm². Inside this boundary, exposed personnel must wear arc-rated PPE. Units: mm or inches.

- **Working distance (D)** — Standardised distance from the worker's torso/face to the electrical equipment's energized parts. IEEE 1584 default: 455 mm (18 in) for LV equipment, 914 mm (36 in) for MV equipment. Engineer may declare otherwise per job.

- **Arcing time (t_arc)** — Duration the arc persists, from initiation to clearing by upstream protective device. Equals the OCPD's clearing time at the arcing current. Units: seconds.

- **Bolted fault current (I_bf or Ibf)** — Three-phase short-circuit current at the fault location, computed per IEC 60909 (consumed via the fault-level intent). Units: A or kA RMS.

- **Arcing current (I_arc or Iarc)** — Actual current flowing through the arc, always **less than** I_bf because the arc itself is a resistance. IEEE 1584 provides empirical formulas to predict Iarc from Vbf, Ibf, and gap distance.

- **Gap distance (G)** — Distance between conductors of different phases at the arc source. Determined by equipment construction; IEEE 1584:2018 Annex C tabulates typical values per equipment type.

## Electrode configurations (IEEE 1584:2018 §5)

- **VCB** — Vertical electrodes inside a Cubic Box (metal enclosure). Most metal-clad MV switchgear; many LV panelboards.
- **VCBB** — VCB With Barrier. Vertical electrodes with an insulating barrier above. LV switchgear with arc-resistant features.
- **HCB** — Horizontal electrodes inside Cubic Box. Drawout breakers, racked switchgear.
- **VOA** — Vertical electrodes in Open Air. Overhead service drops, open-bus systems.
- **HOA** — Horizontal electrodes in Open Air. Substation bus, riser bus.

## Voltage classes (IEEE 1584:2018 §7)

The 2018 method uses three empirical models, each with its own coefficient set:

- **600V model** — applies to 208 V ≤ V_nom ≤ 600 V
- **2700V model** — applies to 601 V ≤ V_nom ≤ 2700 V
- **14300V model** — applies to 2701 V ≤ V_nom ≤ 15 000 V

For nominal voltages between two classes (e.g., 1000V, 4160V), §7.4 logarithmic interpolation applies.

## PPE category (NFPA 70E reference)

Cross-reference to `NFPA70E/table-130-7-C-15-c-ppe-categories.json`:

| Category | Incident energy range |
|---|---|
| 1 | 1.2 – 4 cal/cm² |
| 2 | 4 – 8 cal/cm² |
| 3 | 8 – 25 cal/cm² |
| 4 | 25 – 40 cal/cm² |
| (> 40 cal/cm²) | Restricted — energized work only by specialised teams per facility risk assessment |
