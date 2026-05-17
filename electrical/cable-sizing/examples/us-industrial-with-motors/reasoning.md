# US Industrial Cascade — Worked Example

## Scenario

US 480V industrial 3-node cascade:
- `SERVICE` — 1200A service entrance, copper THWN-2 in cable tray, 35 m
- `SERVICE.F01` — 400A aluminium feeder to MCC, XHHW-2 cable tray, 45 m
- `MCC.M01` — 500 hp DOL chiller motor (NEMA B, LRA multiplier 6.0), 30 m in conduit

## Three different binding constraints across 3 nodes

### SERVICE — `parallel_required`

The standard NEC AWG/kcmil ladder caps at 1000 kcmil with Iz ~615A (THWN-2, cable tray,
75°C terminal cap). Even 1000 kcmil alone can't carry 1200A. Engage `parallel-cables`
rule: 2 × 500 kcmil copper meets minimum csa per NEC 310.10(H)(1), gives Iz ~760A
combined, symmetric.

### SERVICE.F01 — `iz_vs_in` (aluminium)

400A feeder. Aluminium 600 kcmil XHHW-2 in cable tray gives Iz ~420A at 75°C terminal
cap — start csa accepted. binding_constraint = iz_vs_in.

### MCC.M01 — `motor_starting_vd`

500 hp motor at 590A FLA. Cable starts at 500 kcmil (which gives Iz ~430A — fails),
walks up to 600 kcmil (Iz ~475A — fails iz), then 750 kcmil (Iz ~535A — passes iz).
But: motor starting Vd at 500 kcmil = 6.0 × 1.9% = 11.4% (fail), at 600 = 10.5% (fail),
at 750 = 9.6% (pass — within 10% limit, but tight).

binding_constraint = motor_starting_vd. An info-severity flag recommends a soft-starter
to reduce starting Vd to 1.6%.

## Why the motor cumulative Vd hits exactly 5.0% at the limit

The NEC 215.2(A)(1) IN 2 limit for feeder+branch combined is 5%. Walking the cascade:
- SERVICE: 1.6% (35m at 1050A, 2×500 kcmil)
- SERVICE.F01: 1.8% segment → 3.4% cumulative
- MCC.M01: 1.6% segment → 5.0% cumulative

This is the exact NEC limit. If the motor were any further, additional cable upsizing
would be required.

## NEC-specific details (vs IEC)

- AWG/kcmil string identifiers (e.g. `"500"` for 500 kcmil), not numeric mm²
- Terminal-temp cap per NEC 110.14(C): even though THWN-2 is rated 75°C wet/90°C dry,
  Iz is capped by the lowest-rated terminal (75°C here)
- Vd limits per NEC 215.2(A)(1) IN 2: 3% feeder-only, 5% feeder+branch combined
- Parallel rule per NEC 310.10(H)(1): minimum 1/0 AWG per parallel

## Flags emitted

- `TOOL-CALL-PENDING` (runtime calc deferred)
- `MOTOR_STARTING_VD_CLOSE_TO_LIMIT` (info — close to 10%)
- `PARALLEL_CABLES` (informational — downstream cable-containment must accommodate 2 cables in tray)
