# Fault-Level Skill — Known Limitations (v1.0.0)

## v1.0.0 scope

- **Output:** project-scoped fault-level IR (one IR per project, not per board)
- **Intent emitted:** fault-level intent (downstream-facing subset)
- **Systems supported:** AC fault analysis per IEC 60909-0:2016 (LV + HV)
- **Jurisdictions:** GB, EU, INT, US
- **Calculation:** deferred to `calc.iec60909_cascade` runtime tool (per WI3)

## What is OUT of scope

### DC fault analysis
PV strings, battery storage, EV DCFC fault current — separate skill `dc-fault-level` (post-v1.0).

### Arc-flash incident energy
IEEE 1584 / NFPA 70E arc-flash hazard calculation — separate skill `arc-flash` (post-v1.0).

### Time-graded protection coordination
IDMT relays, definite-time, distance protection — separate skill `protection-coordination` (post-Tier 1).

### Lightning-induced transients
BS EN 62305 / NFPA 780 surge analysis — separate scope.

### HV transformer differential protection
Outside building services scope.

### Sub-cycle dynamics
DC offset envelope, asymmetry decay below 1 cycle — requires EMT (electromagnetic transient) simulation, beyond IEC 60909 scope.

## What may produce false positives in evals

- **D2 (Cascade topology accuracy):** Engineer-declared cascade trees can have legitimate non-standard structures (loop systems, transfer schemes, parallel feeders). Reviewer should accept these when documented.
- **D5 (Peak factor κ):** Tool-computed κ might differ slightly from inline approximation due to floating-point precision; 2% tolerance applied.
- **INV-04 (Monotonicity):** Motor back-feed nodes legitimately add to downstream Ifault — flagged as expected, not as error.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute Ik\"max + Ik\"min + ipk + X/R at every cascade node | tool_call_pending (until DraftsMan runtime project ships) |

When the runtime tool exists, IRs currently with `cascade[*].tool_call_pending: true` will be re-emitted with computed values.
