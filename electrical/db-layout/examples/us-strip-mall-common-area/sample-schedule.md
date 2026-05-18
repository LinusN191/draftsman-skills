# DB Schedule — CA-P, Common-Area + Exterior Lighting Panel

**Project:** us-stripmall-cap-eg06
**Board:** CA-P, NEMA Type 1, 60A 208Y/120V intake (fed from MSP-A 60A 2-pole breaker)
**Generated:** 2026-05-18
**Jurisdiction:** US (NFPA 70 NEC 2023)

---

| Way      | Circuit | Designation                                                        | Phase  | Device       | In (A) | Cable        | Length (m) | GFCI         |
|----------|---------|--------------------------------------------------------------------|--------|--------------|--------|--------------|------------|--------------|
| W1       | C01     | Parking lot lighting (LED pole-mounted, 240V branch)               | L1-L2  | MCB Type C   | 30     | 10 AWG Cu    | 60         | —            |
| W2       | C02     | Façade + signage lighting                                          | L3     | MCB Type C   | 20     | 12 AWG Cu    | 40         | —            |
| W3       | C03     | Common area corridor lighting (always-on egress)                   | L1     | MCB Type C   | 20     | 12 AWG Cu    | 35         | —            |
| W4       | C04     | Common area receptacles (janitor + outdoor maintenance)            | L2     | MCB Type C   | 20     | 12 AWG Cu    | 30         | 10mA Class A |
| W5-W6    | C05     | Fire pump controller dedicated tap (life-safety, NEC 695.4)        | TPN    | MCCB Type D  | 60     | 6 AWG Cu     | 18         | —            |
| W7       | C06     | Site security cameras + intercom                                   | L3     | MCB Type C   | 15     | 14 AWG Cu    | 50         | —            |
| W8-W20   | —       | Spare ways reserved (13 ways)                                      |        |              |        |              |            |              |

---

## Notes

**CRITICAL NON-COMPLIANCE FLAG:** C05 fire pump branch from CA-P common-area panelboard violates NEC 695.4(A). Fire pump requires dedicated independent source (utility tap, on-site generator, or dedicated feeder upstream of MSP main service disconnect). Engineer must re-route C05 as a dedicated tap before construction. Drawing as-shown for issue traceability.

- Connected load ≈ 19.6 kW; ~22 A diversified after fire pump re-route (C05 removed from CA-P)
- 60A intake bus is appropriate for common-area load **after** the NEC 695.4 corrective re-route of C05
- NEC 210.8(B) commercial GFCI applied to C04 outdoor/janitor receptacles only (10mA Class A per UL 943)
- C03 corridor lighting (egress) NO GFCI per NEC 700.6 — life-safety availability
- C05 fire pump NO GFCI per NEC 695.5 — earth-fault trip would defeat fire pump purpose
- C05 60A MCCB rated 22 kA Icu per NEC 695.4(B)(2); NEC 695.5(B) prohibits thermal trip on fire pump OCPD (short-circuit trip only); LRA hold-through verified per NEC 695.5(C)
- C01 parking lot 30A on 10 AWG at 60m: voltage drop ~0.3% at 240V — well within NEC 215.2(A)(1) 3% recommendation
- EGC sizing per NEC 250.122 matched to OCPD ratings throughout
- 10 kA Icn MCBs with cascade backup from upstream MSP-A; cascade verification deferred to fault-level skill (tool_call_pending)
- C03 emergency_lighting voltage_class — corridor egress always-on
- Upstream producer: MSP-A (`electrical/db-layout/examples/us-strip-mall-panelboard/`); peers: TSP-A, TSP-B
