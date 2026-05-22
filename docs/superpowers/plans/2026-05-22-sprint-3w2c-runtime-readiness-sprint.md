# Sprint 3-W2c — Runtime Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 13 engineering-refinement deferred items from Sprint 3-W2b reviews AND verify the skills repo is runtime-ready via 4 cross-cutting audits (prompts, intent contracts, manifests, inputs.json taxonomy) — so the upcoming runtime end-to-end test is not blocked by stale artifacts.

**Architecture:** 4 tasks across 3 phases. Phase A applies the 13 engineering refinements via mechanical per-occurrence rules (Sonnet). Phase B runs the 4 audits and applies non-cascading fixes inline — Task 2 prompts audit needs content judgment (Opus); Task 3 schema/JSON audits are mechanical (Sonnet). Phase C ships (Opus).

**Tech Stack:** JSON (example output.json + skill.manifest.json + intent.schema.json), Markdown (prompts + audit reports + CLAUDE.md + memory), JSON Schema Draft-07 (per-skill intent schemas).

**Pattern parents (verified at commit `b665568`):**
- Sprint 3-W2b just shipped at `915522b` with harness FULL GREEN 143/143 — must not regress
- Sprint 3-W2a Task 5 — mechanical-edits-per-occurrence-rules pattern for Task 1
- Sprint 3-W2a Task 5 + 3-W2b Task 5 — Opus-on-judgment pattern for Task 2
- `electrical/<skill>/schemas/<intent>-intent.schema.json` — per-skill intent schemas (NO shared/schemas/intents/ directory exists; that was a spec assumption corrected during planning)
- 9 shipped skill manifests + 27 prompt files (3 per skill × 9 skills) confirmed

**Producer/consumer graph (ground-truthed from actual manifests at HEAD):**

| Producer skill | Intent emitted | Consumers (shipped skills) |
|---|---|---|
| fault-level | `fault-level` | arc-flash, cable-sizing, db-layout, sld (4) |
| db-layout | `db-layout-rollup` | arc-flash, cable-sizing, fault-level (3) |
| db-layout | `db-layout` | earthing, sld (2) |
| lighting-layout | `lighting-layout` | db-layout, earthing (2) |
| arc-flash | `arc-flash` | arc-flash-labelling (1) |
| small-power | `small-power` | earthing (1) |
| cable-sizing | `cable-sizing` | small-power (1) |
| earthing | `earthing` | sld (1) |
| arc-flash-labelling | `labels` | (none — terminal) |
| sld | `sld` | (none — terminal) |

**15 producer→consumer pairs total.** Audit A2 must check each.

**Manifest inconsistency surfaced during planning (in scope for A3):**
- 3 skills use `produces_intent_schemas` (plural array): arc-flash, arc-flash-labelling, db-layout
- 6 skills use `produces_intent_schema` (singular): cable-sizing, earthing, fault-level, lighting-layout, sld, small-power
- Some use `inputs` (path string), others use `inputs_path` (path string). Audit A3 should propose canonical names + recommend fixes (or defer with explicit rationale).

**Final state acceptance:**
- Harness still 143/143 FULL GREEN
- All 13 refinements applied
- 4 audit reports: per-target PASS or "N issues fixed" or "DEFERRED with reason"
- `sprint-3w2c-shipped.md` memory + `MEMORY.md` index updated
- Pushed cleanly to origin/main

**Model selection per [[feedback-no-haiku-sonnet-opus-only]]:**
- Sonnet: Task 1 (mechanical refinements), Task 3 (mechanical schema/JSON audits)
- Opus: Task 2 (prompts audit needs content judgment), Task 4 (ship)

---

## File Structure

**Files modified (~25):**
- ~10 db-layout example `output.json` files (Task 1 refinements)
- Up to ~27 prompt files (Task 2 — most likely PASS without edits)
- Up to ~10 per-skill intent schemas (Task 3 A2 — surgical fixes only if non-cascading)
- 9 `skill.manifest.json` files (Task 3 A3 — likely minimal edits for naming inconsistencies)
- Up to 5 `inputs.json` files (Task 3 A4 — fixes for depends_on graph issues)
- 0-1 `CLAUDE.md` (Task 4 — only if audit surfaced new conventions)

**Files created (3):**
- `docs/sprint-3w2c-prompts-audit.md` (Task 2)
- `docs/sprint-3w2c-contracts-audit.md` (Task 3)
- `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2c-shipped.md` (Task 4)

---

## Task 1: Engineering refinements (Phase A) — Sonnet

**Why Sonnet:** 13 surgical edits with explicit per-occurrence rules. No engineering judgment beyond the locked policies (D4 numeric, D5 voltage-drop frame).

**Files modified:**
- `electrical/db-layout/examples/ke-nairobi-gh-db/output.json` (KE-1, KE-3, KE-4, KE-5)
- `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/output.json` (KE-2)
- `electrical/db-layout/examples/uk-commercial-msb-3storey/output.json` (UK-1, UK-3)
- `electrical/db-layout/examples/uk-commercial-sdb-gf/output.json` (UK-1, UK-2, UK-3, UK-4)
- `electrical/db-layout/examples/uk-commercial-sdb-l1/output.json` (UK-1, UK-2, UK-3, UK-4)
- `electrical/db-layout/examples/uk-commercial-sdb-l2/output.json` (UK-1, UK-2, UK-3, UK-4)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/output.json` (INT-2, INT-3)
- `electrical/db-layout/examples/intl-dbl1-lighting/output.json` (INT-3)
- `electrical/db-layout/examples/intl-dbm1-mechanical/output.json` (INT-3)
- `electrical/db-layout/examples/intl-dbp1-power/output.json` (INT-1, INT-3, INT-4)

### Step 1: Read current state — confirm targets exist before editing

- [ ] Survey current state:
```bash
python3 << 'EOF'
import json
files = [
  ('ke-nairobi-gh-db', ['declared_pfc_ka', 'voltage_class for C03']),
  ('ke-nairobi-industrial-100A-tpn', ['Appendix 1 citation']),
  ('uk-commercial-msb-3storey', ['§ 311 citations', 'voltage-drop refs']),
  ('uk-commercial-sdb-gf', ['§ 311', 'BS EN 61009-1', 'voltage-drop', 'switch-disconnector']),
  ('uk-commercial-sdb-l1', ['§ 311', 'BS EN 61009-1', 'voltage-drop', 'switch-disconnector']),
  ('uk-commercial-sdb-l2', ['§ 311', 'BS EN 61009-1', 'voltage-drop', 'switch-disconnector']),
  ('intl-dbfa1-fire-alarm', ['§ 560.7']),
  ('intl-dbp1-power', ['IEC 60364-7-701 in assumptions', 'P10 3.7%']),
]
for ex, _ in files:
    p = f'electrical/db-layout/examples/{ex}/output.json'
    d = json.load(open(p))
    print(f'{ex}: top-level keys present: {sorted(d.keys())[:5]}...')
EOF
```
Expected: all 8 files exist + readable.

### Step 2: Apply KE refinements (5 items) to ke-nairobi-gh-db + ke-nairobi-industrial-100A-tpn

**KE-1 — PFC 9.8 → 1.0 kA at GH-DB + add inputs**

`ke-nairobi-gh-db/output.json`: find `incoming_supply.declared_pfc_ka` and change `3.0` → `1.0`. Then locate the Incoming Supply rationale section's PFC-related decision. Add the explicit assumption inputs to that decision's `inputs` object:

```json
"inputs": {
  ...existing keys...,
  "submain_csa_mm2": 10,
  "submain_length_m": 60,
  "submain_material": "Cu_SWA",
  "loop_z_estimate_ohm": 0.24,
  "ipsc_at_source_ka": 9.8
}
```

Then update the decision's `summary` text to mention "Conservative 1.0 kA at GH-DB after 60m of 10mm² Cu SWA submain attenuation (loop Z ≈ 0.24 Ω)" instead of the old 3.0 kA claim. Cross-reference: the new figure preserves Icn headroom of >5x against the 6 kA MCB Icn.

**KE-2 — KS 1700 Appendix 1 → § 311 + IET OSG App A**

`ke-nairobi-industrial-100A-tpn/output.json`: find any `code_clause` matching `KS 1700:2018 Appendix 1` and replace with `KS 1700:2018 § 311 (route to BS 7671 § 311.1) + IET OSG App A`. Use:

```bash
python3 -c "
import json, re
p = 'electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/output.json'
s = open(p).read()
print('Before:', re.findall(r'KS 1700:2018 Appendix 1[^\"]*', s))
"
```

Then apply via Edit tool. If multiple occurrences exist, use replace_all.

**KE-3 — KS § 432 (MCB curve) → BS EN 60898-1:2019 only**

`ke-nairobi-gh-db/output.json`: find any `code_clause` containing `BS 7671 § 432` or `KS 1700:2018 § 432` for MCB curve-related decisions. Replace with `BS EN 60898-1:2019` only.

Verify with grep first:
```bash
grep -n '§ 432\|§432' electrical/db-layout/examples/ke-nairobi-gh-db/output.json
```

**KE-4 — C03 voltage_class `comms_data` → `LV_power`**

`ke-nairobi-gh-db/output.json`: find the circuit with `id: "C03"` (CCTV power). Change `voltage_class: "comms_data"` → `voltage_class: "LV_power"`.

Also update any rationale prose that references C03 as "comms_data" — change to "LV_power supplying CCTV PSU" or similar.

Find both with:
```bash
grep -n 'comms_data\|C03' electrical/db-layout/examples/ke-nairobi-gh-db/output.json
```

**KE-5 — C01 floodlight RCD → also cite § 714**

`ke-nairobi-gh-db/output.json`: find the C01 (external floodlight) RCD decision. The current `code_clause` cites `KS 1700:2018 § 411.3.3 (route to BS 7671 via §313)` (or similar). Update to ALSO cite `BS 7671:2018+A2:2022 § 714` (outdoor lighting installations). Update the decision's `summary` to explicitly note the no-RCD justification under § 714 (Class II luminaires or not within touch reach — adapt to what the prose currently says about the floodlight class).

Combined cite form: `KS 1700:2018 § 411.3.3 + § 714 (route to BS 7671 § 411.3.3 + § 714)`

### Step 3: Validate KE files after refinements

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
for ex in ['ke-nairobi-gh-db', 'ke-nairobi-industrial-100A-tpn']:
    d = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    try: jsonschema.validate(d, schema); print(f'PASS {ex}')
    except jsonschema.ValidationError as e: print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: both PASS.

### Step 4: Apply UK refinements (4 items) to all 4 UK files

**UK-1 — Voltage-drop reference frame: 400V line-line canonical**

For each of the 4 UK files (`uk-commercial-msb-3storey` + 3 SDBs), find every voltage-drop percentage claim in rationale prose AND in selectivity_results code_clause AND in compliance_summary.assumptions. Standardise on **400V line-line** as the reference frame.

If the current text says "≈ 1.4% at 100A" (230V phase reference), recompute against 400V line-line OR change the wording to explicitly state the reference frame:

- Option a (preferred): recompute against 400V line-line. For 35mm² SWA Cu at 1.10 mV/A/m line-line: VD(45m, 100A) = 1.10 × 100 × 45 / 1000 = 4.95V on 400V = 1.24%.
- Option b (acceptable if recompute is complex): keep the existing number but state "≈ 2.0–2.5% of 230V phase reference / 1.2–1.5% line-line" with both frames explicit.

Apply Option a where straightforward, Option b otherwise.

```bash
# Find current voltage-drop references
grep -nE "(volta?ge[- ]drop|VD|%) " electrical/db-layout/examples/uk-commercial-{msb-3storey,sdb-gf,sdb-l1,sdb-l2}/output.json
```

**UK-2 — switch-disconnector breaking_capacity_ka semantic clarifier (3 SDB files)**

For each of the 3 SDB files (`sdb-gf`, `sdb-l1`, `sdb-l2`): the `main_switch.type` is `switch-disconnector` with a `breaking_capacity_ka` field. The IR field name is misleading because switch-disconnectors carry Icw (short-time withstand), not Icu (breaking capacity).

Don't rename the IR field (out of scope). Instead, in the Incoming Supply or Schedule Notes section, add a one-decision clarifier:

```json
{
  "label": "main_switch.breaking_capacity_ka carries Icw not Icu",
  "summary": "BS EN 60947-3 switch-disconnectors do not break fault current; the breaking_capacity_ka IR field carries the device's short-time withstand (Icw) rating. Equipment manufacturer's catalogue confirms 10 kA Icw / 1 s.",
  "rule": "BS EN 60947-3 switch-disconnector IR field semantics",
  "code_clause": "BS EN 60947-3:2020 (switch-disconnector device class)",
  "inputs": {
    "main_switch_type": "switch-disconnector",
    "icw_rating_ka_at_1s": 10
  }
}
```

Insert as a new decision in the Schedule Notes section (or Incoming Supply, whichever fits the existing structure of each file).

**UK-3 — § 311 → § 311.1 across 4 UK files**

For each of the 4 UK files: find every `code_clause` containing `BS 7671:2018+A2:2022 § 311` (without sub-clause suffix). Change `§ 311` → `§ 311.1`.

```bash
# Find occurrences
grep -nE "§ 311[^.]" electrical/db-layout/examples/uk-commercial-{msb-3storey,sdb-gf,sdb-l1,sdb-l2}/output.json
```

Be careful NOT to change occurrences that already have a sub-clause (e.g. § 311.1 already, § 311.2). The regex `§ 311[^.]` finds bare § 311 not followed by a dot.

**UK-4 — BS EN 61009-1:2012 → BS EN 61009-1:2012+A12:2014 (3 SDB files)**

For each of the 3 SDB files: find every `code_clause` containing `BS EN 61009-1:2012` (the bare 2012 edition). Append `+A12:2014`. Final form: `BS EN 61009-1:2012+A12:2014`.

```bash
grep -n 'BS EN 61009-1:2012[^+]' electrical/db-layout/examples/uk-commercial-{sdb-gf,sdb-l1,sdb-l2}/output.json
```

### Step 5: Validate UK files

- [ ] Run validation across all 4 UK files (mirror Step 3 pattern). Expected: 4/4 PASS.

### Step 6: Apply INT refinements (4 items)

**INT-1 — DB-P1 pre-existing IEC 60364-7-701 kitchen assumption text update**

`intl-dbp1-power/output.json`: find the `compliance_summary.assumptions` array. Locate the entry referencing `IEC 60364-7-701 series (water proximity)` for the kitchen socket. Update the assumption text to:

`"Commercial kitchen socket P07 requires 30mA Type A RCD per universal IEC 60364-4-41 § 411.3.3 socket-circuit policy. IEC 60364-7-701 (bathrooms and shower locations) does NOT apply — commercial kitchens are not Part 7-701 special locations."`

The new rationale prose (added in 3-W2b Task 4) already corrects this in the rationale block — Task 5 of 3-W2b explicitly noted the pre-existing assumption was out of scope. Now we close it.

**INT-2 — DB-FA1 § 560.7 sub-clause precision**

`intl-dbfa1-fire-alarm/output.json`: find every `code_clause` containing `IEC 60364-5-56 § 560.7` (without sub-clause suffix). Tighten to `§ 560.7.1` (safety service independence) or `§ 560.7.2` (protection coordination) per context:

- Decisions about "no upstream RCD on the FA feeder" → `§ 560.7.1`
- Decisions about "ADS by overcurrent protection only — NO RCD justified" → `§ 560.7.2`

If sub-clause precision can't be confirmed for a particular decision, leave as `§ 560.7` and add `(sub-clause precision pending verification)` parenthetical in the decision's `summary`.

**INT-3 — DRY decision text variation across DB-FA1/L1/M1/P1**

The "Engineer-declared per manufacturer cascade table" decision currently appears IDENTICALLY across 4 INT files. Vary the wording per file with the file-specific cascade ratio:

- DB-FA1 (63A:10A): change summary to include `"6.3:1 same-curve Type C cascade ratio; FA panel + sounder loops fed from F04 incomer"`
- DB-L1 (250A:20A): change summary to include `"12.5:1 MCCB-to-MCB cross-curve cascade ratio; lighting circuits fed from F01"`
- DB-M1 (250A:32A): change summary to include `"7.8:1 MCCB-to-MCB cross-curve cascade ratio; motor circuits fed from F03 with local starter overload protection"`
- DB-P1 (400A:32A): change summary to include `"12.5:1 MCCB-to-MCB cross-curve cascade ratio; ring + radial circuits fed from F02"`

Keep the rule + code_clause unchanged across all 4. Only the `summary` field varies.

**INT-4 — DB-P1 P10 voltage drop 3.7% → 6% + add inputs**

`intl-dbp1-power/output.json`: find the P10 circuit's voltage-drop decision in Circuit Breakdown section. The current claim is "≈3.7% at full load". Revise to a more conservative "≈6% at full load (centre-loaded ring assumption)" and add explicit inputs:

```json
"inputs": {
  ...existing keys...,
  "ring_length_m": 100,
  "assumed_load_distribution": "centre-loaded",
  "iec_mv_per_a_per_m_2p5mm2_cu": 18,
  "computed_vd_percent_at_400v_line_line": 6.3
}
```

Keep the tool_call_pending flag on the cable-sizing-skill handoff. Update the summary text to explicitly state the centre-loaded assumption is the basis for the conservative figure.

### Step 7: Validate INT files

- [ ] Run validation across 4 INT files. Expected: 4/4 PASS.

### Step 8: Run full harness — FULL GREEN must hold

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -6
```
Expected: Pass 1 = 53/53, Pass 2 = 81/81, Pass 3 = 9/9, AGGREGATE = 143/143 exit 0.

If aggregate ≠ 143/143, halt and investigate.

### Step 9: Cross-reference grep — ensure no stale strings remain

- [ ] Run targeted greps to verify replacements are complete:

```bash
echo "=== KE-1 stale: 3.0 kA at GH-DB ==="
grep -n '"declared_pfc_ka": 3.0' electrical/db-layout/examples/ke-nairobi-gh-db/output.json || echo "  clean"

echo "=== KE-2 stale: Appendix 1 ==="
grep -n 'Appendix 1' electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/output.json || echo "  clean"

echo "=== KE-3 stale: § 432 in gh-db ==="
grep -nE '§ ?432' electrical/db-layout/examples/ke-nairobi-gh-db/output.json || echo "  clean"

echo "=== KE-4 stale: comms_data in gh-db ==="
grep -n 'comms_data' electrical/db-layout/examples/ke-nairobi-gh-db/output.json || echo "  clean"

echo "=== UK-3 stale: bare § 311 (no sub-clause) ==="
grep -nE '§ 311[^.]' electrical/db-layout/examples/uk-commercial-*/output.json || echo "  clean"

echo "=== UK-4 stale: BS EN 61009-1:2012 (no +A12) ==="
grep -nE 'BS EN 61009-1:2012[^+]' electrical/db-layout/examples/uk-commercial-*/output.json || echo "  clean"

echo "=== INT-2 stale: bare § 560.7 (no sub-clause) ==="
grep -nE '§ 560\.7[^.]' electrical/db-layout/examples/intl-dbfa1-fire-alarm/output.json || echo "  clean (or only sub-clause-precision-pending entries remain)"

echo "=== INT-3 DRY check: identical 'Engineer-declared' summary text across 4 INT files ==="
grep -h 'Engineer-declared per manufacturer cascade table' electrical/db-layout/examples/intl-{dbfa1-fire-alarm,dbl1-lighting,dbm1-mechanical,dbp1-power}/output.json | sort -u | wc -l
```

Expected: stale-string greps print "clean" (empty grep output). INT-3 DRY check should report > 1 unique line (variation introduced).

### Step 10: Commit Task 1

- [ ] Run:
```bash
git add electrical/db-layout/examples/
git commit -m "feat(sprint-3w2c): Phase A — 13 engineering refinements from 3-W2b reviews; KE (PFC 9.8→1.0 kA at GH-DB with auditable inputs + KS Appendix 1→§ 311 + KS § 432→BS EN 60898-1 + C03 voltage_class LV_power + C01 floodlight § 714); UK (voltage-drop frame standardised on 400V line-line + switch-disconnector Icw clarifier + § 311→§ 311.1 + BS EN 61009-1 +A12:2014); INT (DB-P1 kitchen assumption corrected + § 560.7 sub-clause precision + 4-file decision text DRY varied + P10 6% conservative VD with inputs); harness held at 143/143"
```

## Task 1 Self-Review

- [ ] All 13 refinements applied (count: 5 KE + 4 UK + 4 INT = 13)
- [ ] Step 9 grep confirms zero stale strings remain
- [ ] Harness still 143/143 (Step 8)
- [ ] Numeric refinements (KE-1, INT-4) carry explicit inputs assumptions

---

## Task 2: Prompts audit + fixes (Phase B) — Opus

**Why Opus:** Prompt files are PROSE not schema. Determining "does this prompt drive the LLM toward post-3W2b shapes" requires reading the prose carefully and making judgment calls about adequacy. The 5-row drift check is the framework; per-prompt content judgment is the work.

**Files modified:** up to 27 prompt files across 9 skills (`electrical/<skill>/prompts/{generator,validator,reviewer}.md`).

**Files created:** `docs/sprint-3w2c-prompts-audit.md`.

### Step 1: Inventory prompt files

- [ ] Run:
```bash
find electrical -path "*/prompts/*.md" 2>/dev/null | sort
```
Expected: 27 files (3 per skill × 9 shipped skills). If fewer, identify which skill lacks which file.

### Step 2: Build the audit framework

Create `docs/sprint-3w2c-prompts-audit.md` with this initial structure:

```markdown
# Sprint 3-W2c — Prompts Audit Report

Audit window: post-Sprint 3-W2b schema additions. The harness FULL GREEN does not verify that prompts drive the LLM to emit the post-3W2b shapes. This audit verifies each shipped skill's prompts (generator, validator, reviewer) explicitly cover the new schema surface.

## 5-row drift check

| # | Check | Applies to |
|---|---|---|
| C1 | Mentions `board_kind` discriminator (`main_switchboard` vs `specialty_board` oneOf branch) | db-layout primarily; sld + earthing if they reference board shape |
| C2 | Covers all 5 jurisdiction enum values (`GB / EU / INT / US / KE`) | every skill |
| C3 | Covers `ups_plus_essential` supply_class (alongside existing essential / non_essential / life_safety / ups_backed / genset_backed) | db-layout primarily; consumers if they reference supply_class |
| C4 | Uses canonical `main_switch_fused` enum (NOT informal `switch-fuse`) | db-layout primarily; sld + fault-level if they reference main_switch.type |
| C5 | Citation form aligns with 4-jurisdiction convention | every skill |

Per-check abbreviations: `P` = present + correct; `M` = missing or needs update; `N/A` = not applicable to this skill; `D` = deferred to a future sprint (deeper rewrite needed).

## Per-skill audit

[populate below]

## Summary

[populate at end]
```

### Step 3: Walk each skill's 3 prompts and apply the 5-row check

For each of the 9 skills (arc-flash, arc-flash-labelling, cable-sizing, db-layout, earthing, fault-level, lighting-layout, sld, small-power), read all 3 prompt files (generator, validator, reviewer) and record findings as a markdown table:

```markdown
### {{skill_name}}

| File | C1 board_kind | C2 jurisdiction KE | C3 ups_plus_essential | C4 main_switch_fused | C5 citation form |
|---|---|---|---|---|---|
| generator.md | P/M/N/A | P/M/N/A | P/M/N/A | P/M/N/A | P/M/N/A |
| validator.md | ... | ... | ... | ... | ... |
| reviewer.md | ... | ... | ... | ... | ... |

**Drift items found:** X
**Drift items FIXED in this sprint:** Y
**Drift items DEFERRED:** Z (with reason)
```

Judgment rules:
- C1 (`board_kind`): for db-layout's generator, the prompt MUST tell the LLM to emit `board_kind: "main_switchboard"` or `"specialty_board"` for the produced board. For sld + earthing (consumers of db-layout), the prompt SHOULD acknowledge they may receive either kind. Other skills: N/A.
- C2 (jurisdiction KE): for every skill, the prompt SHOULD list KE alongside GB/EU/INT/US OR explicitly explain the jurisdiction enum. Missing KE → drift.
- C3 (ups_plus_essential): for db-layout's generator + reviewer, the prompt SHOULD acknowledge the supply_class can be `ups_plus_essential` for dual-classified UPS-backed essential boards. Consumers may N/A this.
- C4 (main_switch_fused): for db-layout's generator + validator, the prompt MUST list the canonical enum value `main_switch_fused` (not informal `switch-fuse`). Drift if `switch-fuse` appears as canonical guidance.
- C5 (citation form): for every skill, the prompt's standards section SHOULD provide a per-jurisdiction citation template (e.g. `BS 7671:2018+A2:2022 § X.X.X` for GB; `KS 1700:2018 § X (route to BS 7671 via §313)` for KE).

### Step 4: Apply surgical fixes inline

For each drift item that is fixable in < 10 minutes per prompt (e.g. add a missing enum value to a list; add a single missing citation template entry):

- [ ] Make the surgical edit
- [ ] Record in the audit report as `FIXED`
- [ ] If the fix needs > 10 minutes (e.g. rewrite a whole standards section), record as `DEFERRED with reason: <reason>` — surface in Task 4 memory file's known-follow-up section.

### Step 5: Defer deeper rewrites per Risk R1 mitigation

If any single skill has > 5 drift items requiring rewrites, escalate to DEFERRED for that skill's deeper prompt-content overhaul. Document in the audit report.

### Step 6: Verify harness still 143/143 after prompt edits

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143 exit 0. (Prompt edits shouldn't affect harness; verify.)

### Step 7: Author the audit report's summary section

Append to `docs/sprint-3w2c-prompts-audit.md`:

```markdown
## Summary

- Total prompt files audited: 27 (3 per skill × 9 shipped skills)
- Files with zero drift: X
- Files with drift fixed inline: Y
- Files with drift deferred: Z
- Deferred items (escalated to Sprint 3-W2d or post-runtime-test cycle):
  - {{skill}}.{{prompt}}.C{{n}}: {{reason}}
  - ...

**HIGH-RISK drift items**: {{count}} (must be 0 for sprint acceptance)
**Outcome:** {{PASS / N-fixed / DEFERRED-with-reason}}
```

### Step 8: Commit

```bash
git add electrical/ docs/sprint-3w2c-prompts-audit.md
git commit -m "feat(sprint-3w2c): Phase B Task 2 — prompts audit (5-row drift check across 27 prompt files / 9 shipped skills); FIXED {{N}} surgical drift items inline (mostly missing KE jurisdiction + ups_plus_essential supply_class + main_switch_fused canonical enum); DEFERRED {{M}} deeper rewrites to post-runtime-test sprint"
```

## Task 2 Self-Review

- [ ] All 27 prompt files audited (or N/A documented per missing file)
- [ ] 5-row check applied per file
- [ ] Surgical fixes applied inline; deferred items documented with reason
- [ ] HIGH-RISK drift count is 0 (sprint acceptance criterion)
- [ ] Audit report committed

---

## Task 3: Intent contracts + manifests + inputs.json taxonomy (Phase B) — Sonnet

**Why Sonnet:** A2 + A3 + A4 are mechanical schema/JSON diffs with deterministic comparison rules.

**Files modified:** up to ~10 per-skill intent schemas + 9 skill manifests + 5 inputs.json files.

**Files created:** `docs/sprint-3w2c-contracts-audit.md`.

### A2 — Intent contracts audit

### Step 1: Inventory all 10 intent schemas

- [ ] Run:
```bash
find electrical -name "*-intent.schema.json" | sort
```
Expected: 10 files (db-layout has 2: regular + rollup; 8 other skills have 1 each).

### Step 2: Audit each of the 15 producer→consumer pairs

The 15 pairs are documented in the Plan header table. For each pair:

1. Load the producer's intent schema (`electrical/<producer>/schemas/<intent>-intent.schema.json`)
2. The consumer references this same intent name in its `consumes_intents[]` — verify the manifest matches
3. Since there's no separate "consumer-side accepts" schema (the schema is owned by the producer; consumers just consume the produced shape), the audit verifies: does the producer schema use only the canonical enum values + post-3W2b shapes?

For each producer schema:
```bash
python3 -c "
import json, jsonschema
s = json.load(open('electrical/<producer>/schemas/<intent>-intent.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
print(f'{intent}: schema valid as Draft-07')
# Walk enums + check for stale values
"
```

Specifically check for these post-3W2b additions per intent schema:
- `db-layout-intent`: does it have `board_kind` discriminator? Does it accept `ups_plus_essential` supply_class? Does it accept `main_switch_fused` enum?
- `db-layout-rollup-intent`: same checks + does it support KE jurisdiction?
- Other intents: do their jurisdiction fields (if any) accept KE?

### Step 3: Document A2 findings in audit report

Create `docs/sprint-3w2c-contracts-audit.md` with:

```markdown
# Sprint 3-W2c — Contracts Audit Report

## A2 — Intent contracts (15 producer→consumer pairs)

| # | Producer | Intent | Consumers | Schema valid? | Post-3W2b coverage | Outcome |
|---|---|---|---|---|---|---|
| 1 | fault-level | fault-level | arc-flash, cable-sizing, db-layout, sld | Y/N | KE / board_kind / ups_plus_essential / main_switch_fused | PASS / N-fixed / DEFERRED |
| 2 | db-layout | db-layout-rollup | arc-flash, cable-sizing, fault-level | ... | ... | ... |
| 3 | db-layout | db-layout | earthing, sld | ... | ... | ... |
| 4 | lighting-layout | lighting-layout | db-layout, earthing | ... | ... | ... |
| 5 | arc-flash | arc-flash | arc-flash-labelling | ... | ... | ... |
| 6 | small-power | small-power | earthing | ... | ... | ... |
| 7 | cable-sizing | cable-sizing | small-power | ... | ... | ... |
| 8 | earthing | earthing | sld | ... | ... | ... |

(Terminal intents — no consumer — but still verify they're Draft-07 valid:)

| # | Producer | Intent | Schema valid? |
|---|---|---|---|
| T1 | arc-flash-labelling | labels | Y/N |
| T2 | sld | sld | Y/N |
```

### Step 4: Apply non-cascading fixes for A2

For each A2 mismatch where the fix is contained (doesn't break example validation):
- [ ] Add missing enum value (e.g. `KE` to jurisdiction enum)
- [ ] Add missing field for new shape (e.g. `board_kind` accepted in db-layout-intent if missing)

For each cascading mismatch (would break example files validating against the schema):
- [ ] Defer with explicit reason; surface in Task 4 memory file

### A3 — skill.manifest.json audit

### Step 5: Validate the 9 shipped manifests

- [ ] Run:
```bash
python3 << 'EOF'
import json, os
shipped = ['arc-flash', 'arc-flash-labelling', 'cable-sizing', 'db-layout', 'earthing', 'fault-level', 'lighting-layout', 'sld', 'small-power']
findings = []
for s in shipped:
    m = json.load(open(f'electrical/{s}/skill.manifest.json'))
    issues = []
    # Required keys
    if 'version' not in m: issues.append('missing version')
    if 'produces_intent' not in m and 'produces_intent_schema' not in m and 'produces_intent_schemas' not in m:
        issues.append('missing produces_intent')
    # Naming inconsistency
    p_singular = m.get('produces_intent_schema')
    p_plural = m.get('produces_intent_schemas')
    if p_singular and p_plural:
        issues.append('uses BOTH produces_intent_schema (singular) and _schemas (plural)')
    inputs_str = m.get('inputs')
    inputs_path = m.get('inputs_path')
    if inputs_str and inputs_path:
        issues.append('uses BOTH inputs and inputs_path')
    # Reference resolution
    if 'consumes_intents' in m:
        for ci in m['consumes_intents']:
            # find producer
            found = False
            for other in shipped:
                om = json.load(open(f'electrical/{other}/skill.manifest.json'))
                p = om.get('produces_intent')
                if isinstance(p, str) and p == ci: found = True
                if isinstance(p, list) and ci in p: found = True
            if not found:
                issues.append(f'consumes "{ci}" but no shipped producer found')
    findings.append((s, m.get('version', '?'), issues))

for s, v, issues in findings:
    status = 'PASS' if not issues else 'ISSUES'
    print(f'{s} v{v}: {status}')
    for i in issues: print(f'  - {i}')
EOF
```

Document findings in the audit report:

```markdown
## A3 — skill.manifest.json (9 shipped skills)

| # | Skill | Version | Required keys | Naming consistency | Reference resolution | Outcome |
|---|---|---|---|---|---|---|
| 1 | arc-flash | 1.0.0 | OK | uses _schemas (plural) | OK | PASS / N-fixed |
| 2 | arc-flash-labelling | 1.0.0 | ... | uses _schemas (plural) | ... | ... |
| 3 | cable-sizing | 1.0.0 | ... | uses _schema (singular) | ... | ... |
| 4 | db-layout | 1.3.1 | ... | uses _schemas (plural) | ... | ... |
| 5 | earthing | 1.4.0 | ... | uses _schema (singular) | ... | ... |
| 6 | fault-level | 1.1.0 | ... | uses _schema (singular) | ... | ... |
| 7 | lighting-layout | 1.3.0 | ... | uses _schema (singular) | ... | ... |
| 8 | sld | 1.5.0 | ... | uses _schema (singular) | ... | ... |
| 9 | small-power | 1.1.0 | ... | uses _schema (singular) | ... | ... |

### Naming-convention inconsistency proposal

Three skills (arc-flash, arc-flash-labelling, db-layout) use the plural `produces_intent_schemas` because they produce 2+ intents. Six skills use the singular `produces_intent_schema` because they produce exactly 1 intent.

Recommendation: ACCEPT the singular/plural variance as semantically correct (single intent = singular field; multi-intent = plural array). Not a real inconsistency. Document the convention in this audit report + Task 4 CLAUDE.md update if useful.

Similarly: `inputs` vs `inputs_path` — flag as a real inconsistency if both exist in different manifests. Recommendation: standardise on `inputs_path` (more descriptive). Apply IF non-cascading; defer otherwise.
```

### Step 6: Apply manifest fixes if non-cascading

For each A3 issue:
- [ ] If naming inconsistency that's purely cosmetic AND the runtime adapter accepts either form: leave alone, document the convention
- [ ] If broken reference (consumes intent that has no producer): FIX by removing the orphan consumes entry, OR defer with documented reason
- [ ] If missing required key: FIX inline
- [ ] If version misalignment with CHANGELOG.md: FIX inline by bumping or correcting

### A4 — inputs.json taxonomy audit

### Step 7: Audit the 5 items[]-shape inputs.json files

- [ ] Run for each of db-layout, earthing, fault-level, lighting-layout, sld:
```bash
python3 << 'EOF'
import json, glob
for s in ['db-layout', 'earthing', 'fault-level', 'lighting-layout', 'sld']:
    d = json.load(open(f'electrical/{s}/inputs.json'))
    items = d.get('items', [])
    all_ids = {it['id'] for it in items}
    issues = []
    # depends_on graph
    for it in items:
        for dep in it.get('depends_on', []):
            if dep not in all_ids:
                issues.append(f"item '{it['id']}' depends_on '{dep}' (not found)")
    # enum option coverage (vs examples)
    examples = sorted(glob.glob(f'electrical/{s}/examples/*/input.json'))
    for it in items:
        if it.get('answer_type') in ('enum', 'enum_list'):
            opts = set(it.get('options', []))
            seen = set()
            for ex in examples:
                ed = json.load(open(ex))
                val = ed.get(it['id'])
                if isinstance(val, str): seen.add(val)
                elif isinstance(val, list):
                    for v in val: seen.add(v)
            unused = opts - seen
            if unused:
                # not a blocking issue but flagged
                pass  # report optional uncovered
    # required item coverage
    for it in items:
        if it.get('required'):
            covered = False
            for ex in examples:
                ed = json.load(open(ex))
                if ed.get(it['id']) is not None:
                    covered = True; break
            if not covered:
                issues.append(f"required item '{it['id']}' has no example with non-null answer")
    print(f"{s}: items={len(items)}, examples={len(examples)}, issues={len(issues)}")
    for i in issues: print(f"  - {i}")
EOF
```

Document findings in the audit report:

```markdown
## A4 — inputs.json taxonomy (5 items[]-shape skills)

| # | Skill | Item count | depends_on issues | Required-item coverage gaps | Enum coverage notes | Outcome |
|---|---|---|---|---|---|---|
| 1 | db-layout | N | 0 / N | 0 / M required items | enum coverage X% | PASS / N-fixed |
| 2 | earthing | ... | ... | ... | ... | ... |
| 3 | fault-level | ... | ... | ... | ... | ... |
| 4 | lighting-layout | ... | ... | ... | ... | ... |
| 5 | sld | ... | ... | ... | ... | ... |
```

### Step 8: Apply A4 fixes if non-cascading

For each A4 issue:
- [ ] Broken depends_on reference: FIX by removing or correcting the reference
- [ ] Required item with no example coverage: DEFER to a future content sprint (would require authoring new example fields)
- [ ] Unused enum option (warning only): document but don't change

### Step 9: Verify harness still 143/143

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143 exit 0.

### Step 10: Commit Task 3

```bash
git add electrical/ docs/sprint-3w2c-contracts-audit.md
git commit -m "feat(sprint-3w2c): Phase B Task 3 — contracts audit (A2 15 producer→consumer pairs + A3 9 manifests + A4 5 inputs.json taxonomy); FIXED {{N}} surgical mismatches; DEFERRED {{M}} cascading items; documented singular/plural produces_intent_schema convention + inputs vs inputs_path naming variance"
```

## Task 3 Self-Review

- [ ] A2: 15 producer→consumer pairs documented + 2 terminal intents validated
- [ ] A3: 9 manifests checked for required keys + naming consistency + reference resolution
- [ ] A4: 5 items[]-shape inputs.json files checked for depends_on graph + required coverage
- [ ] Surgical fixes applied; cascading mismatches deferred with reason
- [ ] Audit report committed
- [ ] Harness still 143/143

---

## Task 4: Final validation + push + memory save (Phase C) — Opus

**Why Opus:** Ship-readiness judgment + memory file authoring requires faithful sprint summary + accurate deferred-queue documentation.

### Step 1: Run the 3-pass harness

- [ ] Run:
```bash
python3 scripts/validate-examples.py
```

Expected (FULL GREEN held):
```
Subtotal: 53/53 pass (0 failures)
Subtotal: 81/81 pass (0 failures)
Subtotal: 9/9 pass (0 failures)
=== AGGREGATE: 143/143 pass (0 failures) ===
```
Exit code: 0.

If aggregate ≠ 143/143 OR exit ≠ 0, halt — investigate before push.

### Step 2: Confirm git state

```bash
git log --oneline origin/main..HEAD
git status
```
Expected: 5 local commits ahead (spec + plan + 3 task commits), clean working tree.

### Step 3: Walk both audit reports

- [ ] Read `docs/sprint-3w2c-prompts-audit.md` summary section. Verify HIGH-RISK drift count is 0. Note deferred items.
- [ ] Read `docs/sprint-3w2c-contracts-audit.md`. Verify A2 has 0 unresolved HIGH-RISK mismatches. Verify A3 + A4 outcomes.

### Step 4: Verify the 13 engineering refinements grep-clean

- [ ] Run the Step 9 grep block from Task 1 again — every stale-string check should return "clean".

### Step 5: Update CLAUDE.md if audit surfaced material conventions

Only update if Task 2 or Task 3 surfaced a convention worth documenting (e.g. "produces_intent_schema vs schemas plural variance accepted" or "voltage-drop reference frame convention").

Don't expand scope. If nothing new, skip this step.

### Step 6: Push to origin/main

```bash
git push origin main
```

Expected: clean push, no force, hooks pass. Do NOT use `--force` or `--no-verify`.

After successful push:
```bash
git log --oneline origin/main..HEAD
```
Expected: empty (no local-only commits).

### Step 7: Save sprint-shipped memory

- [ ] Write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2c-shipped.md`:

```markdown
---
name: sprint-3w2c-shipped
description: Sprint 3-W2c Runtime Readiness shipped 2026-05-22 — 13 engineering refinements + 4 audits (prompts/intent contracts/manifests/inputs.json taxonomy); harness FULL GREEN 143/143 held; skills repo declared runtime-ready for end-to-end testing
metadata:
  type: project
---

**✅ SHIPPED 2026-05-22 — Sprint 3-W2c: Runtime Readiness** (commits b665568..{{TIP_SHA}}, pushed to origin/main)

Closes the deferred engineering-refinement queue from Sprint 3-W2b code reviews + verifies the skills repo is runtime-ready before end-to-end testing. Harness FULL GREEN 143/143 held; skills repo declared runtime-ready.

## What was delivered

### Engineering refinements (13 items)
- **KE bundle (5):** PFC 9.8→1.0 kA at GH-DB with auditable inputs; KS Appendix 1 → § 311 + IET OSG App A; KS § 432 (MCB curve) → BS EN 60898-1:2019 only; C03 voltage_class comms_data → LV_power; C01 floodlight RCD justification expanded to § 714
- **UK bundle (4):** voltage-drop reference frame standardised on 400V line-line; switch-disconnector Icw clarifier inserted in 3 SDB files; § 311 → § 311.1; BS EN 61009-1:2012 → +A12:2014
- **INT bundle (4):** DB-P1 pre-existing IEC 60364-7-701 kitchen assumption corrected; DB-FA1 § 560.7 → § 560.7.1/§ 560.7.2 sub-clause precision; "Engineer-declared" decision text varied per file with file-specific cascade ratios; DB-P1 P10 voltage drop 3.7% → 6% conservative with explicit centre-loaded ring assumption inputs

### Audit A1 — Prompts ({{N1}} drift items fixed inline, {{D1}} deferred)
- 27 prompt files audited across 9 shipped skills
- 5-row drift check: board_kind discriminator / KE jurisdiction / ups_plus_essential / main_switch_fused / 4-jurisdiction citation form
- HIGH-RISK count after fixes: 0
- See `docs/sprint-3w2c-prompts-audit.md`

### Audit A2 — Intent contracts ({{N2}} mismatches fixed, {{D2}} deferred)
- 15 producer→consumer pairs verified (corrected from spec's initial count of 6 after ground-truth survey)
- 10 per-skill intent schemas validated as Draft-07
- All terminal intents (labels, sld) also validated
- See `docs/sprint-3w2c-contracts-audit.md`

### Audit A3 — Manifests (9 shipped skills)
- All 9 manifests valid + version-consistent
- Documented `produces_intent_schema` (singular) vs `produces_intent_schemas` (plural) convention: accepted as semantically correct (singular = 1 intent; plural = multi-intent)
- {{Other A3 findings}}

### Audit A4 — Inputs.json taxonomy (5 items[]-shape skills)
- depends_on graph clean across db-layout, earthing, fault-level, lighting-layout, sld
- {{A4 findings}}

## Harness end-state
- Pass 1 (examples): 53/53 (FULL GREEN held)
- Pass 2 (evals): 81/81 (held)
- Pass 3 (inputs.json): 9/9 (held)
- AGGREGATE: 143/143 exit 0

## Known follow-up (post-runtime-test sprint — Sprint 3-W2d or named cycle)
- Bucket C Tier-4 lossy eval conversions (require eval-runtime grammar upgrades)
- Harness M1 DRY consolidation
- Harness M5/M6/M8 cosmetic + type-hint widening + strip_refs comment
- Any deferred prompt content overhauls from Task 2
- Any cascading intent contract mismatches deferred from Task 3 A2
- Any inputs.json required-item coverage gaps from Task 3 A4

## Stats
- 3 implementation commits + 2 doc commits (spec + plan)
- ~25 file ops actually delivered
- 2 audit reports authored (prompts + contracts)
- Single session execution

## How to apply
- Skills repo is now runtime-ready: every shipped skill has manifest + prompts + intent schema consistent with post-3W2b shape
- Next step is end-to-end runtime testing — first via Claude directly running a skill, then via the DraftsMan runtime
- Harness FULL GREEN 143/143 is the standing acceptance bar; do not regress

## Cross-references
- [[sprint-3w-shipped]] — schema-fragmentation backlog origin
- [[sprint-3w2a-shipped]] — schema standardisation
- [[sprint-3w2b-shipped]] — content completion; FULL GREEN achieved here
- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — model rules
- [[build-strategy-breadth-first]] — back to breadth-first skill build after runtime testing validates
```

Replace `{{TIP_SHA}}`, `{{N1}}`, `{{D1}}`, `{{N2}}`, `{{D2}}`, `{{Other A3 findings}}`, `{{A4 findings}}` with actual values from the audit reports.

### Step 8: Update MEMORY.md index

- [ ] Read `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`. Add a one-line entry after the `[Sprint 3-W2b shipped]` line:

```markdown
- [Sprint 3-W2c shipped](sprint-3w2c-shipped.md) — 2026-05-22: runtime readiness; 13 engineering refinements + 4 audits (prompts/intent contracts/manifests/inputs.json); harness FULL GREEN 143/143 held; skills repo runtime-ready
```

### Step 9: Report to user

- [ ] Final summary (≤ 8 lines):
- Push status (success + final SHA)
- Harness 3-pass result + AGGREGATE
- Sprint maintained FULL GREEN
- Audit outcomes (prompts FIXED/DEFERRED + contracts FIXED/DEFERRED)
- Memory file path
- Skills repo declared RUNTIME-READY
- Next focal point: end-to-end runtime testing (Claude direct → DraftsMan runtime → injection verification)

## Task 4 Self-Review

- [ ] Harness 143/143 exit 0 confirmed
- [ ] Both audit reports walked + HIGH-RISK count is 0
- [ ] Push succeeded without `--force` / `--no-verify`
- [ ] Memory file written with deferred queue documented
- [ ] MEMORY.md index updated
- [ ] User report includes runtime-readiness declaration

---

## Risks & Mitigations

- **R1 — Prompts audit surfaces large fix queue.** *Mitigation:* if any single skill needs > 30 min of prompt rewriting, defer to follow-up sprint and document in audit report.

- **R2 — Intent contract cascading mismatches.** *Mitigation:* Task 3 categorises every mismatch; non-cascading fixes ship; cascading defers to dedicated sprint.

- **R3 — Numeric refinement reversibility.** *Mitigation:* Task 1 Step 9 grep cross-checks for stale numeric strings; commit body documents per-occurrence decisions.

- **R4 — inputs.json depends_on cycle/orphan.** *Mitigation:* Task 3 Step 8 reports unfixable items; runtime testing phase decides whether to fix in skills repo or runtime adapter.

- **R5 — Audit scope creep.** *Mitigation:* per-audit report has explicit FIXED vs DEFERRED columns; deferred items added to memory follow-up section.

- **R6 — Runtime-readiness necessary but not sufficient.** *Mitigation:* Task 4 commit message acknowledges runtime testing may surface execution-layer issues not visible to this audit.

- **R7 — Bucket C + harness polish truly deferred.** *Mitigation:* memory file explicitly lists both as post-runtime-test follow-ups.

---

## Self-Review

**Spec coverage check:**
- §1 locked decisions D1-D5 ✓ — D1 scope reflected in Task 1+2+3 boundaries; D2 audit coverage in Tasks 2+3; D3 task structure 4 tasks 3 phases ✓; D4 numeric policy applied in KE-1+INT-4; D5 voltage-drop frame applied in UK-1
- §2 scope (13 refinements + 4 audits + out-of-scope) ✓ — Tasks 1-3 cover; Bucket C + harness polish deferred per memory file
- §3 phases A-C ✓ mapped to Tasks 1, 2+3, 4
- §4 file ops ~30-50 ✓ — actual estimate: 10 examples + up to 27 prompts + ~10 intents + 9 manifests + 5 inputs.json = ~60 max, mostly likely 25-35 actual
- §5 risks R1-R7 ✓ mirrored
- §6 acceptance 8 criteria ✓ — all mapped to Task 4 verification steps
- §7 out-of-scope handoff ✓ — Task 4 memory file documents
- §8 model selection ✓ matches
- §9 sprint workflow ✓ — Task 4 closes loop

**Placeholder scan:** No TBD/TODO/"implement later" in plan steps. Every per-occurrence rule is explicit. Memory file template has placeholders ({{TIP_SHA}}, {{N1}}, etc.) clearly marked as fill-in-when-known values.

**Type consistency:**
- Field name `board_kind` consistent (Task 1 INT/KE rationale references + Task 2 C1 check + Task 3 A2 intent schema check)
- Field name `main_switch_fused` consistent (Task 2 C4 + Task 3 A2)
- Field name `ups_plus_essential` consistent (Task 2 C3 + Task 3 A2)
- Producer/consumer graph (15 pairs) consistent between Plan header + Task 3 A2
- Audit report file names: `docs/sprint-3w2c-prompts-audit.md` + `docs/sprint-3w2c-contracts-audit.md` consistent
- Memory file path: `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2c-shipped.md` consistent
