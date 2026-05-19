# Socket Schedule — KE Nairobi 80 m² commercial office unit

Project: `ke-nairobi-office-eg01`
Sheet: A1 @ 1:50 per BS 1192:2007+A2:2016
Total sockets: 15 across 4 circuits

| Circuit | Room | Socket ID | Type | Mount | Height (mm AFFL) | RCD posture | Engineering note |
|---|---|---|---|---|---|---|---|
| C01 | workstation-1 | workstation-1-S01 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk left — workstation power |
| C01 | workstation-1 | workstation-1-S02 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk right — workstation power |
| C01 | workstation-2 | workstation-2-S01 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk left — workstation power |
| C01 | workstation-2 | workstation-2-S02 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk right — workstation power |
| C01 | reception | reception-S01 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Reception desk left — PC + monitor |
| C01 | reception | reception-S02 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Reception desk right — phone + scanner |
| C02 | workstation-3 | workstation-3-S01 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk left — workstation power |
| C02 | workstation-3 | workstation-3-S02 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk right — workstation power |
| C02 | workstation-4 | workstation-4-S01 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk left — workstation power |
| C02 | workstation-4 | workstation-4-S02 | BS 1363 double 13A switched | wall | 300 | Type A 30 mA / 20 A MCB B | Under-desk right — workstation power |
| C03 | kitchenette | kitchenette-S01 | BS 1363 double 13A switched | above_worktop | 1100 | Type A 30 mA / 20 A MCB B | Worktop — kettle / hot water |
| C03 | kitchenette | kitchenette-S02 | BS 1363 double 13A switched | above_worktop | 1100 | Type A 30 mA / 20 A MCB B | Worktop — microwave |
| C03 | kitchenette | kitchenette-S03 | BS 1363 double 13A switched | above_worktop | 1100 | Type A 30 mA / 20 A MCB B | Worktop — flexible (coffee / toaster) |
| C03 | kitchenette | kitchenette-S04 | 13A switched fused connection unit (BS EN 60669-2-1) | wall | 300 | Type A 30 mA / 20 A MCB B | Under-counter fridge — fixed-feed FCU |
| C04 | toilet | toilet-S01 | BS EN 61558-2-5 shaver supply unit | wall | 1400 | Type A 30 mA / 6 A MCB B | Zone 3 only; isolating transformer; no general 13 A sockets in toilet (KS 1700:2018 §701 routes to BS 7671:2018+A2:2022 Part 7-701) |

## Circuit summary

| Circuit | Designation | OCPD | Cable | Topology | Rooms covered | Sockets |
|---|---|---|---|---|---|---|
| C01 | Workstations 1-2 + reception | 20 A MCB B / Type A 30 mA / 9 kA | 2.5 mm² T+E, ~18 m | radial | workstation-1, workstation-2, reception | 6 |
| C02 | Workstations 3-4 | 20 A MCB B / Type A 30 mA / 9 kA | 2.5 mm² T+E, ~14 m | radial | workstation-3, workstation-4 | 4 |
| C03 | Kitchenette + fridge FCU | 20 A MCB B / Type A 30 mA / 9 kA | 2.5 mm² T+E, ~10 m | radial | kitchenette | 4 |
| C04 | Toilet shaver supply (SSU) | 6 A MCB B / Type A 30 mA / 9 kA | 1.5 mm² T+E, ~6 m | dedicated_radial | toilet | 1 |

## Notes

- All workstation/reception sockets BS 1363 double 13 A switched (KE commercial idiom — UK plug standard widely adopted) at 300 mm AFFL for under-desk routing.
- Kitchenette worktop sockets at 1100 mm AFFL (150 mm above 950 mm worktop); under-counter fridge fed via 13 A FCU at 300 mm AFFL.
- Toilet is classified `bathroom_zone_3` per KS 1700:2018 §701 (routes to BS 7671:2018+A2:2022 Part 7-701); only the BS EN 61558-2-5 shaver supply unit is installed (no general 13 A sockets within 3 m of zone 1 per §701.512.3).
- All four circuits are radial — KS 1700:2018 §433 routes to BS 7671:2018+A2:2022 §433.1.5 permitting ring finals, but KE commercial engineering practice favours radial at tenant fit-out scale (selectivity + maintenance access).
- All MCBs are 9 kA Icu to match the declared KPLC PSCC at the parent DB busbar via the KS 1700:2018 §434 → BS 7671:2018+A2:2022 §434.5.1 routing chain.
- RCD protection is board-level Type A 30 mA at DB-OFFICE-01 (covers all 4 final circuits) per KS 1700:2018 §411.3.3 (routes to BS 7671:2018+A2:2022 §411.3.3).
- All circuits carry `tool_call_pending_for_zs_verification: true`; loop-impedance Zs delegated to `calc.zs_loop_impedance` per WI3.
- Cable lengths quoted are *total radial length* and assume Reference Method 100/101 (concealed in stud / ceiling void); final route by `cable-containment` skill.
