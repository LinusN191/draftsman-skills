# Engineering Philosophy — Cable Sizing

This skill encodes a senior-engineer mental model for cable selection rather than just
running calc tables. The model:

## 1. Walk the ladder, name the binding constraint

Cable sizing isn't optimisation — it's compliance. Start with the smallest standard csa
that meets `In`, then climb the standard ladder until ALL constraints pass:
- Iz ≥ In (ampacity vs OCPD rating)
- cumulative Vd ≤ jurisdictional limit
- CPC adiabatic equation
- (for motors) starting Vd ≤ 10%

The "binding constraint" — the check that forced the last upsize — is the most useful
single number on a cable schedule. It tells the next engineer why this circuit is
10 mm² instead of 4 mm² without re-running the calc.

## 2. Cumulative voltage drop, not per-segment

BS 7671 App 12 / IEC 60364-5-52 §G / NEC 215.2 all apply Vd limits cumulatively from
source to circuit endpoint. A 4% feeder + 4% branch = 8% at the load, which violates
every standard. The cascade tree makes this trivial: each node's `vd_cumulative_pct`
is the sum of its segment Vd plus the parent chain.

## 3. Defer math to deterministic tools

Cable ampacity table lookups (PVC vs XLPE column, derating factor stacking) and
voltage-drop math (`mV/A/m × Ib × L`) are LLM-unreliable. We push them to `calc.*`
tools per the WI3 deferral pattern. Until the runtime ships, every affected node
carries `tool_call_pending: true` + best-effort engineer estimates as placeholders.

## 4. Engineering judgement stays at the prompt layer

What lives in the prompt (walk-up algorithm, when to engage parallels, motor-starting
warning policy, harmonic-derating triggers) is judgement. What lives in calc tools
(Iz lookup, Vd math, CPC adiabatic) is mechanical. Split deliberately.

## 5. Cross-skill contracts before downstream consumers exist

We emit a slim `cable-sizing` intent designed to satisfy the (future) consumed-intent
shape declarations of `cable-schedule`, `riser`, and `cable-containment`. The schema is
the union superset. When those skills get built, they conform to this contract — not
the other way round.

## 6. Hard-rules over soft-guidance

Some things the generator MUST never do (invent fault current, off-ladder csa, missing
binding-constraint token). These live in `hard_rules:` in the generator prompt, not as
suggestions. The validator enforces them mechanically.
