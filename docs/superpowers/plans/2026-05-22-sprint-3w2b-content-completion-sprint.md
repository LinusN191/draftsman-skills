# Sprint 3-W2b — Content Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 14 db-layout content failures + all Sprint 3-W2a code-review followups so the 3-pass golden CI gate hits **AGGREGATE 143/143 exit 0** (full green).

**Architecture:** 6 tasks across 5 phases. Phase A reconciles the IR schema with reality (oneOf `board_kind` discriminator + add `board_kind` to all 20 examples). Phase B authors 10 missing rationale blocks via Opus subagents, bundled by jurisdiction (KE → UK → INT) for citation-form consistency and precedent inheritance. Phase C bundles Bucket B cleanup (silent-regression fixes + Task 4 minor lint + CLAUDE.md doc polish). Phase D ships.

**Tech Stack:** JSON Schema Draft-07 (db-layout-ir.schema.json), JSON (example output.json files), Python 3 (scripts/validate-examples.py), Markdown (CLAUDE.md). Subagent dispatch via the Agent tool: Sonnet for mechanical, Opus for judgment-heavy authoring.

**Pattern parents (verified at commit `9a67044`):**
- `shared/schemas/core/eval.schema.json` (Sprint 3-W2a Task 1) — same oneOf+discriminator pattern this sprint uses for the board.
- `electrical/db-layout/examples/uk-domestic-consumer-unit/output.json` — main_switchboard rationale reference: 9 sections (Board Classification → Compliance), chat_summary 366 chars.
- `electrical/db-layout/examples/intl-dbcomms-data/output.json` — specialty_board rationale reference: 6 sections (Board Identification, Incoming Supply, Circuit Breakdown, Selectivity Analysis, Compliance Assessment, Schedule Notes), chat_summary 422 chars.
- `electrical/db-layout/schemas/db-layout-ir.schema.json` — current `board.required: ["db_id", "designation", "location", "ways_total"]`; `ways_total` is the contention point.
- `electrical/db-layout/prompts/generator.md` + `electrical/db-layout/prompts/reviewer.md` — section list authority + quality bar.
- `shared/schemas/core/rationale.schema.json` — canonical rationale envelope (chat_summary 40-500, sections[*].summary maxLength 800).
- `scripts/validate-examples.py` (Sprint 3-W2a Task 4) — extend in place; M2/M3/M4/M7 surgical edits at known line refs.

**Final state acceptance:**
- Pass 1 (examples): **53/53** (40/53 baseline + 4 from Phase A + 10 from Phase B + 0 net from Phase C/D = 53/53). Wait: baseline is 39/53. 39 + 14 cleared = 53. Correct.
- Pass 2 (evals): 81/81 (unchanged)
- Pass 3 (inputs.json): 9/9 (unchanged)
- AGGREGATE: 143/143 exit 0

**Model selection (per `[[feedback-no-haiku-sonnet-opus-only]]`):**
- Sonnet: Task 1 (mechanical schema + 20 board_kind additions), Task 5 (mechanical Bucket B edits).
- Opus: Tasks 2/3/4 (judgment-heavy rationale authoring), Task 6 (ship-readiness).

---

## File Structure

**Files modified (≈30 total):**
- `electrical/db-layout/schemas/db-layout-ir.schema.json` — restructure board with `board_kind` discriminator + oneOf branch.
- `electrical/db-layout/examples/*/output.json` (20 files) — add `board_kind` to each board object; 10 of those also get a `rationale` block added.
- `electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml` — 1 `!= null` placeholder triage
- `electrical/arc-flash/evals/eval-03-coefficient-fallback-trap.yaml` — method_fallback_trail description tighten
- `electrical/arc-flash/evals/eval-04-missing-fault-data.yaml` — 2 `!= null` placeholder triage
- `electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml` — 1 free-text-flag fix + 1 `!= null` placeholder
- `electrical/arc-flash/evals/eval-06-rationale-block.yaml` — 2 `!= null` placeholder triage
- `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml` — 1 free-text-flag fix + 2 `!= null` placeholder
- `electrical/arc-flash/evals/eval-09-shock-approach-out-of-range.yaml` — numeric→string coercion comment
- `electrical/arc-flash-labelling/evals/eval-06-rationale-block.yaml` — 1 `!= null` placeholder triage
- `electrical/arc-flash-labelling/evals/eval-07-svg-template-population.yaml` — 2 `!= null` placeholder triage
- `electrical/arc-flash-labelling/evals/eval-08a-qr-code-emitted.yaml` — add 1 cross-cutting `all_equal` check
- `scripts/validate-examples.py` — M2 (line 108 add counter), M3 (line 173 remove unused var), M4 (lines 283/288/293 drop f-prefix), M7 (lines 163-165 remove dead filter)
- `CLAUDE.md` — 5 doc polish edits

**Files created:**
- `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2b-shipped.md` (Task 6).

---

## Task 1: Schema reconciliation (Phase A) — Sonnet

**Why Sonnet:** Mechanical schema restructure + 20 deterministic example edits. No engineering judgment required.

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-ir.schema.json` — board section + root-level oneOf
- Modify: `electrical/db-layout/examples/*/output.json` (20 files) — add `board.board_kind`

### Step 1: Read current schema board section

- [ ] Read `electrical/db-layout/schemas/db-layout-ir.schema.json` in full. Confirm:
  - Top-level `required` array includes `board, incoming_supply, main_switch, spare_ways, circuits, ...` (12 fields total).
  - `board.required` is `["db_id", "designation", "location", "ways_total"]`.
  - `board.properties` includes `db_id, designation, location, enclosure_form_iec61439, enclosure_form_nec_type, ip_rating, ways_total, ways_used, ways_spare`.
  - No `additionalProperties: false` on board (so we can ADD specialty-board keys without rejection).
  - No existing oneOf on board.

### Step 2: Restructure board section

- [ ] Replace the `board` definition in `properties:` with the new shape:

```json
"board": {
  "type": "object",
  "required": ["db_id", "designation", "location", "board_kind"],
  "properties": {
    "db_id":                    { "type": "string", "pattern": "^[A-Z][A-Z0-9-]{1,15}$" },
    "designation":              { "type": "string" },
    "location":                 { "type": "string" },
    "board_kind":               { "enum": ["main_switchboard", "specialty_board"] },
    "enclosure_form_iec61439":  { "enum": ["1", "2a", "2b", "3a", "3b", "4a", "4b"] },
    "enclosure_form_nec_type":  { "enum": ["NEMA_1", "NEMA_3R", "NEMA_4", "NEMA_4X", "NEMA_12"] },
    "ip_rating":                { "type": "string", "pattern": "^IP[0-9X]{2,3}$" },
    "ways_total":               { "type": "integer", "minimum": 1, "maximum": 200 },
    "ways_used":                { "type": "integer", "minimum": 0 },
    "ways_spare":               { "type": "integer", "minimum": 0 },
    "enclosure_rating":         { "type": "string" },
    "manufacturer_class":       { "type": "string" },
    "scope":                    { "type": "string" },
    "role":                     { "type": "string" }
  },
  "oneOf": [
    {
      "properties": { "board_kind": { "const": "main_switchboard" } },
      "required": ["ways_total", "ways_used", "ways_spare"]
    },
    {
      "properties": { "board_kind": { "const": "specialty_board" } },
      "required": ["enclosure_rating", "manufacturer_class", "scope", "role"]
    }
  ]
}
```

Notes:
- `board_kind` is now required at root of `board` (the discriminator).
- `ways_total/used/spare` move OUT of `board.required` and INTO the `main_switchboard` oneOf branch.
- `enclosure_rating/manufacturer_class/scope/role` are added to `board.properties` AND required by the `specialty_board` oneOf branch.
- Keep `additionalProperties` unset on board (preserves backward compatibility with `enclosure_form_*` + `ip_rating` keys).

### Step 3: Verify the schema is well-formed Draft-07

- [ ] Run:
```bash
python3 -c "import json, jsonschema; s = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema OK')"
```
Expected: `Schema OK`.

### Step 4: Author a positive + negative schema test

- [ ] Run this inline verification script (don't commit it — just confirm the oneOf behaves as expected):

```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))

# Positive 1: minimal valid main_switchboard board
positive_main = {
    "drawing_type": "db_layout_schedule_and_schematic",
    "version": "1.0",
    "meta": {"project_id": "TEST", "skill_version": "1.0.0", "produced_at": "2026-05-22T00:00:00Z"},
    "jurisdiction": "GB",
    "board": {
        "db_id": "DB-TEST",
        "designation": "Test main",
        "location": "test",
        "board_kind": "main_switchboard",
        "ways_total": 12, "ways_used": 6, "ways_spare": 6
    },
    "incoming_supply": {"voltage_v": 230, "phase_arrangement": "single_phase", "supply_rating_a": 100, "fed_from": "MAIN", "supply_class": "non_essential", "declared_pfc_ka": 6.0},
    "main_switch": {"type": "isolator", "rating_a": 100, "breaking_capacity_ka": 10},
    "spare_ways": [],
    "circuits": [],
    "selectivity_results": [],
    "compliance_summary": {},
    "rationale": {"chat_summary": "Test rationale for positive case verification.", "sections": [{"title": "Board Classification", "summary": "Main switchboard test."}]}
}
try:
    # We expect this to maybe fail due to other required fields — focus on board oneOf
    jsonschema.validate(positive_main, schema)
    print("Positive main OK")
except jsonschema.ValidationError as e:
    # If error path mentions 'board', the discriminator is broken
    if 'board' in str(e.absolute_path):
        print(f"FAIL: board branch broken: {e.message}")
    else:
        print(f"OK (board passes, other field failed): {e.message[:120]}")

# Positive 2: minimal valid specialty_board
positive_specialty = dict(positive_main)
positive_specialty["board"] = {
    "db_id": "DB-TEST",
    "designation": "Test specialty",
    "location": "test",
    "board_kind": "specialty_board",
    "enclosure_rating": "IP4X",
    "manufacturer_class": "IEC 61439-3 Distribution Board",
    "scope": "single-board",
    "role": "test_panel"
}
try:
    jsonschema.validate(positive_specialty, schema)
    print("Positive specialty OK")
except jsonschema.ValidationError as e:
    if 'board' in str(e.absolute_path):
        print(f"FAIL: specialty branch broken: {e.message}")
    else:
        print(f"OK (board passes, other field failed): {e.message[:120]}")

# Negative: cross-shape (main_switchboard with specialty fields)
negative = dict(positive_main)
negative["board"] = {
    "db_id": "DB-TEST",
    "designation": "Cross-shape",
    "location": "test",
    "board_kind": "main_switchboard",
    "enclosure_rating": "IP4X",
    "manufacturer_class": "IEC 61439-3",
    "scope": "single-board",
    "role": "test"
    # missing ways_total/used/spare → must fail
}
try:
    jsonschema.validate(negative, schema)
    print("FAIL: negative cross-shape unexpectedly passed")
except jsonschema.ValidationError as e:
    if 'board' in str(e.absolute_path) or 'ways_total' in e.message:
        print(f"Negative correctly rejected: {e.message[:120]}")
    else:
        print(f"Negative rejected for wrong reason: {e.message[:120]}")
EOF
```
Expected output:
- `Positive main OK` (or "OK (board passes, other field failed)" if the test object has unrelated holes)
- `Positive specialty OK` (or similar)
- `Negative correctly rejected: ...ways_total...` confirming the cross-shape fails on the main_switchboard branch's required.

If the negative case PASSES, the oneOf is broken — halt and re-author Step 2 before continuing.

### Step 5: Add `board_kind` to all 20 example output.json files

- [ ] Run this script to bulk-add the discriminator:

```bash
python3 << 'EOF'
import json, glob, sys
main_files = []
specialty_files = []
for f in sorted(glob.glob('electrical/db-layout/examples/*/output.json')):
    d = json.load(open(f))
    board = d.get('board', {})
    if 'ways_total' in board:
        board['board_kind'] = 'main_switchboard'
        main_files.append(f)
    elif 'enclosure_rating' in board:
        board['board_kind'] = 'specialty_board'
        specialty_files.append(f)
    else:
        print(f"SKIP {f} — neither ways_total nor enclosure_rating"); continue
    # Write back preserving 2-space indent + UTF-8
    with open(f, 'w') as out: json.dump(d, out, indent=2, ensure_ascii=False); out.write('\n')
print(f"main_switchboard: {len(main_files)} files")
for f in main_files: print(f"  {f}")
print(f"specialty_board: {len(specialty_files)} files")
for f in specialty_files: print(f"  {f}")
EOF
```

Expected: 6 main_switchboard + 14 specialty_board = 20 total. Lists must match the spec §2 ground truth.

### Step 6: Run the harness to confirm Phase A progress

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Subtotal|AGGREGATE|FAIL.*db-layout"
```

Expected:
- Pass 1 Subtotal: 43/53 (was 39/53 baseline; +4 from the 4 outlier-with-rationale files that now satisfy the specialty_board oneOf branch).
- 10 remaining FAIL lines, ALL `db-layout` skill, ALL on missing `rationale` property.

If Pass 1 is not 43/53, something is off — investigate before committing.

### Step 7: Commit

- [ ] Run:
```bash
git add electrical/db-layout/schemas/db-layout-ir.schema.json electrical/db-layout/examples/
git commit -m "feat(sprint-3w2b): Phase A — db-layout-ir.schema.json board.board_kind discriminator (oneOf main_switchboard vs specialty_board); add board_kind to all 20 examples (6 main + 14 specialty); Pass 1 goes 39→43/53"
```

---

## Task 2: KE rationale bundle (Phase B, Africa-first) — Opus

**Why Opus:** Engineering content authoring with jurisdiction-specific citation form. Judgment required for clause selection, diversity factors, RCD posture choices.

**Files:**
- Modify: `electrical/db-layout/examples/ke-nairobi-gh-db/output.json`
- Modify: `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/output.json`

### Step 1: Inspect both input.json + output.json (non-rationale fields)

- [ ] Run:
```bash
python3 -c "
import json
for ex in ['ke-nairobi-gh-db', 'ke-nairobi-industrial-100A-tpn']:
    inp = json.load(open(f'electrical/db-layout/examples/{ex}/input.json'))
    out = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    print(f'=== {ex} ===')
    print('input top keys:', sorted(inp.keys()))
    print('output board:', out.get('board'))
    print('output incoming_supply:', out.get('incoming_supply'))
    print('output circuit count:', len(out.get('circuits', [])))
    print('output has rationale?', 'rationale' in out)
    print()
"
```

Confirm both files have all top-level required fields populated except `rationale`.

### Step 2: Author rationale for `ke-nairobi-gh-db`

Both KE files are `specialty_board` per Task 1 output. Use the **6-section specialty template** (matching the precedent in `intl-dbcomms-data`, etc.):

1. **Board Identification** — db_id, designation, role, IEC 61439-3 class, jurisdiction note (KE)
2. **Incoming Supply** — voltage, phase_arrangement, fed_from, supply_class, Ze (if applicable)
3. **Circuit Breakdown** — what loads are served + diversity factor reasoning
4. **Selectivity Analysis** — cascade verification + any TOOL-CALL-PENDING flags
5. **Compliance Assessment** — KS 1700:2018 § X (route to BS 7671 via §313) for protection; relevant IEC 61439-3 clauses for enclosure
6. **Schedule Notes** — anything noteworthy (KE-specific: utility connection conventions, local DNO practice)

- [ ] Read `electrical/db-layout/examples/intl-dbcomms-data/output.json` to see how the 6 sections are populated in the existing precedent. Match the prose density (each section summary 280-490 chars, 1-3 decisions per section).

- [ ] Read `electrical/db-layout/prompts/generator.md` and `electrical/db-layout/prompts/reviewer.md` for the section-content rules + quality bar the rationale must satisfy.

- [ ] Write the rationale block, following the canonical envelope:

```json
"rationale": {
  "chat_summary": "<40-500 char paragraph summarizing the board's purpose, key design decisions, and any flags/assumptions. Invite refinement.>",
  "sections": [
    {
      "title": "Board Identification",
      "summary": "<280-490 char paragraph identifying the board: db_id, designation, role, enclosure class, jurisdiction>",
      "decisions": [
        {
          "label": "<one-line human-readable label>",
          "summary": "<one-sentence reasoning>",
          "rule": "<the deterministic rule invoked, e.g. 'KS 1700:2018 § 313 routes board enclosure form to BS EN 61439-3'>",
          "code_clause": "<specific clause ref, e.g. 'KS 1700:2018 § 313 (route to BS 7671 via §313)'>",
          "inputs": { "<key>": "<value driving this decision>" }
        }
      ]
    },
    {
      "title": "Incoming Supply",
      "summary": "...",
      "decisions": [ ... ]
    },
    {
      "title": "Circuit Breakdown",
      "summary": "...",
      "decisions": [ ... ]
    },
    {
      "title": "Selectivity Analysis",
      "summary": "...",
      "decisions": [ ... ]
    },
    {
      "title": "Compliance Assessment",
      "summary": "...",
      "decisions": [ ... ]
    },
    {
      "title": "Schedule Notes",
      "summary": "...",
      "decisions": [ ... ]
    }
  ]
}
```

Citation form rules:
- For protection requirements (RCD, EFLI, Zs, OCPD coordination): `KS 1700:2018 § X (route to BS 7671 via §313)` — both refs.
- For enclosure form / construction: `IEC 61439-3:2012 § X` (KS 1700 routes here too).
- For special locations (if relevant): `KS 1700:2018 Part 7-XXX` mirroring BS 7671 Part 7-XXX numbering.
- NEVER invent a clause number. If a decision can't be cited, leave `code_clause` out of that decision (it's optional in the schema).

### Step 3: Author rationale for `ke-nairobi-industrial-100A-tpn`

Same 6-section template. Industrial context (likely a 100A TPN motor/HVAC sub-DB) — `Circuit Breakdown` section should mention motor diversity per `IET OSG Appendix A` (or the KS 1700 equivalent if it exists).

### Step 4: Validate both files against the IR schema

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
for ex in ['ke-nairobi-gh-db', 'ke-nairobi-industrial-100A-tpn']:
    d = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    try:
        jsonschema.validate(d, schema)
        print(f'PASS {ex}')
    except jsonschema.ValidationError as e:
        print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: both PASS.

### Step 5: Validate rationale shape against shared schema

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema, copy
schema = json.load(open('shared/schemas/core/rationale.schema.json'))
# strip $refs (rationale.schema.json may reference itself)
def strip(n):
    if isinstance(n, dict):
        if '$ref' in n: return {'type': 'object'}
        return {k: strip(v) for k, v in n.items()}
    if isinstance(n, list): return [strip(v) for v in n]
    return n
schema_test = strip(schema)
for ex in ['ke-nairobi-gh-db', 'ke-nairobi-industrial-100A-tpn']:
    d = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    rationale = d['rationale']
    try:
        jsonschema.validate(rationale, schema_test)
        chat_len = len(rationale['chat_summary'])
        sec_count = len(rationale['sections'])
        print(f'PASS {ex} (chat={chat_len} chars, {sec_count} sections)')
    except jsonschema.ValidationError as e:
        print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: both PASS, chat between 40-500 chars, sections between 6 and 9.

### Step 6: Run the harness

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Subtotal|FAIL.*db-layout"
```
Expected: Pass 1 Subtotal: 45/53 (+2 from Task 2). Remaining 8 db-layout failures are the UK + INT files still without rationale.

### Step 7: Commit

- [ ] Run:
```bash
git add electrical/db-layout/examples/ke-nairobi-gh-db/output.json electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/output.json
git commit -m "feat(sprint-3w2b): Phase B-1 KE bundle — author rationale for ke-nairobi-gh-db + ke-nairobi-industrial-100A-tpn (6-section specialty_board template; KS 1700:2018 § X (route to BS 7671 via §313) citation form; IEC 61439-3 for enclosure class); Pass 1 goes 43→45/53"
```

---

## Task 3: UK rationale bundle (Phase B) — Opus

**Why Opus:** Same engineering content authoring as Task 2, jurisdiction-shifted to GB. Sees the KE precedent from Task 2.

**Files:**
- Modify: `electrical/db-layout/examples/uk-commercial-msb-3storey/output.json`
- Modify: `electrical/db-layout/examples/uk-commercial-sdb-gf/output.json`
- Modify: `electrical/db-layout/examples/uk-commercial-sdb-l1/output.json`
- Modify: `electrical/db-layout/examples/uk-commercial-sdb-l2/output.json`

### Step 1: Read the KE bundle output (precedent)

- [ ] Read both KE rationale blocks from Task 2 commit. Use them as prose-density and section-shape precedent.

### Step 2: Inspect all 4 UK file inputs + non-rationale outputs

- [ ] Run:
```bash
python3 -c "
import json
for ex in ['uk-commercial-msb-3storey', 'uk-commercial-sdb-gf', 'uk-commercial-sdb-l1', 'uk-commercial-sdb-l2']:
    out = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    print(f'=== {ex} ===')
    print('  board:', out['board'])
    print('  incoming_supply.fed_from:', out['incoming_supply'].get('fed_from'))
    print('  supply_class:', out['incoming_supply'].get('supply_class'))
    print('  circuits:', len(out.get('circuits', [])))
    print()
"
```

Note that `uk-commercial-msb-3storey` is likely the parent MSB feeding the 3 sdb (sub-DB) files (`sdb-gf`, `sdb-l1`, `sdb-l2` correspond to ground/level-1/level-2 floors). The 4 rationales must be MUTUALLY CONSISTENT — the MSB's downstream board IDs must match the SDBs' `fed_from` values.

### Step 3: Author rationale for `uk-commercial-msb-3storey`

This may be a `specialty_board` (verify from Task 1's board_kind annotation). Use the appropriate template:
- specialty_board → 6 sections (Board Identification, Incoming Supply, Circuit Breakdown, Selectivity Analysis, Compliance Assessment, Schedule Notes)
- main_switchboard → 9 sections (Board Classification, Incoming Supply, Busbar Sizing, Way Assignment, OCPD Selection, RCD Strategy, Cable Selection, Selectivity Verification, Compliance)

Citation form for UK:
- Protection / Zs / EFLI / RCD: `BS 7671:2018+A2:2022 § X.X.X` (use exact regulation number)
- Enclosure / construction: `BS EN 61439-3:2012 § X` (UK identical to IEC; cite BS EN preferentially)
- OCPDs: `BS EN 60898-1:2019` (MCBs) / `BS EN 61009-1:2012` (RCBOs) / `BS EN 60947-2` (MCCBs)
- Cables: `BS 7671 Appendix 4` (current ratings) / `Appendix 12` (voltage drop)

### Step 4: Author rationale for `uk-commercial-sdb-gf`, `sdb-l1`, `sdb-l2`

Each sub-DB rationale should:
- Mention `fed_from` pointing at the MSB id (consistency check — must match the MSB's downstream emit if it shipped one)
- Show selectivity reasoning against the MSB's OCPDs (cascade rationale)
- Cite the same UK regs as the MSB plus floor-specific specials (e.g. `BS 7671 Part 7-701` if there's a bathroom; `BS 7671 § 422` if there's a fire shutter)

### Step 5: Validate all 4 against the IR schema + rationale schema

- [ ] Run (adapt Task 2 Step 4 + 5 for UK files):
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
files = ['uk-commercial-msb-3storey', 'uk-commercial-sdb-gf', 'uk-commercial-sdb-l1', 'uk-commercial-sdb-l2']
for ex in files:
    d = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    try: jsonschema.validate(d, schema); print(f'PASS {ex}')
    except jsonschema.ValidationError as e: print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: 4/4 PASS.

### Step 6: Run the harness

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Subtotal|FAIL.*db-layout"
```
Expected: Pass 1 Subtotal: 49/53 (+4 from Task 3). Remaining 4 db-layout failures are the INT files.

### Step 7: Commit

- [ ] Run:
```bash
git add electrical/db-layout/examples/uk-commercial-msb-3storey/output.json electrical/db-layout/examples/uk-commercial-sdb-gf/output.json electrical/db-layout/examples/uk-commercial-sdb-l1/output.json electrical/db-layout/examples/uk-commercial-sdb-l2/output.json
git commit -m "feat(sprint-3w2b): Phase B-2 UK bundle — author rationale for uk-commercial-msb-3storey + 3 sdb floor sub-DBs (cross-board consistent fed_from + selectivity cascade); BS 7671:2018+A2:2022 + BS EN 61439-3:2012 + BS EN 60898/61009 citation form; Pass 1 goes 45→49/53"
```

---

## Task 4: INT rationale bundle (Phase B) — Opus

**Why Opus:** Engineering content authoring across 4 different specialty board types (fire alarm, lighting, mechanical, power). Each board has unique specialty refs.

**Files:**
- Modify: `electrical/db-layout/examples/intl-dbfa1-fire-alarm/output.json`
- Modify: `electrical/db-layout/examples/intl-dbl1-lighting/output.json`
- Modify: `electrical/db-layout/examples/intl-dbm1-mechanical/output.json`
- Modify: `electrical/db-layout/examples/intl-dbp1-power/output.json`

### Step 1: Read KE + UK bundles (precedents)

- [ ] Re-read the 2 KE + 4 UK rationales committed in Tasks 2 + 3. Use them as prose-density and section-shape precedent.

### Step 2: Inspect all 4 INT file inputs + non-rationale outputs

- [ ] Run:
```bash
python3 -c "
import json
for ex in ['intl-dbfa1-fire-alarm', 'intl-dbl1-lighting', 'intl-dbm1-mechanical', 'intl-dbp1-power']:
    out = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    print(f'=== {ex} ===')
    print('  board:', out['board'])
    print('  circuits:', len(out.get('circuits', [])))
    print()
"
```

All 4 are `specialty_board` per Task 1 → use the 6-section template.

### Step 3: Author rationale for `intl-dbfa1-fire-alarm`

Fire-alarm DB is a Category 1 life-safety panel. Special citations:
- `IEC 60364-5-56:2018 § 560` — safety services
- `IEC 60839-7-2` or `BS 5839-1:2017` (UK fire-alarm standard often cited internationally)
- `IEC 61439-3:2012` for enclosure class
- The fire-alarm DB itself is typically NON-RCD protected (RCD would defeat fire alarm continuity) — Compliance Assessment section MUST cover this rationale explicitly

### Step 4: Author rationale for `intl-dbl1-lighting`

Lighting DB. Special citations:
- `IEC 60364-4-41:2017 § 411.3` for ADS
- `IEC 60364-5-559:2014` for luminaires + accessories specifically
- For emergency lighting circuits within: `IEC 60598-2-22:2014` + `IEC 60364-5-56:2018`
- `IEC 61439-3:2012` for enclosure class

### Step 5: Author rationale for `intl-dbm1-mechanical`

Mechanical (HVAC / motor) DB. Special citations:
- `IEC 60364-5-55:2011` for low-voltage motor circuits
- `IEC 60947-4-1` for contactors + motor starters
- `IEC 60364-4-43:2017` for overload protection
- `IEC 61439-3:2012` for enclosure class
- Diversity factors: cite `IEC 60364-7-718` if office building, or general IEC 60364-1 Appendix C

### Step 6: Author rationale for `intl-dbp1-power`

General power (socket-outlet + small power) DB. Special citations:
- `IEC 60364-4-41:2017` for ADS / disconnection times
- `IEC 60364-7-701:2006` if any bathroom circuit (Part 7-701)
- `IEC 60364-7-704:2017` if any construction-site circuit
- `IEC 61439-3:2012` for enclosure class

### Step 7: Validate all 4 against IR + rationale schemas

- [ ] Run (adapt Task 2 Step 4 + 5 for INT files):
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
for ex in ['intl-dbfa1-fire-alarm', 'intl-dbl1-lighting', 'intl-dbm1-mechanical', 'intl-dbp1-power']:
    d = json.load(open(f'electrical/db-layout/examples/{ex}/output.json'))
    try: jsonschema.validate(d, schema); print(f'PASS {ex}')
    except jsonschema.ValidationError as e: print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: 4/4 PASS.

### Step 8: Run the harness

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Subtotal|FAIL"
```
Expected: Pass 1 Subtotal: **53/53** (FULL GREEN). Pass 2 + Pass 3 still 81/81 + 9/9. AGGREGATE 143/143 exit 0.

If aggregate exit ≠ 0 here, halt — something regressed.

### Step 9: Commit

- [ ] Run:
```bash
git add electrical/db-layout/examples/intl-dbfa1-fire-alarm/output.json electrical/db-layout/examples/intl-dbl1-lighting/output.json electrical/db-layout/examples/intl-dbm1-mechanical/output.json electrical/db-layout/examples/intl-dbp1-power/output.json
git commit -m "feat(sprint-3w2b): Phase B-3 INT bundle — author rationale for 4 specialty boards (fire-alarm + lighting + mechanical + power); IEC 60364-X-XX + IEC 61439-3 + specialty refs (BS 5839 / IEC 60839 fire; IEC 60598-2-22 + 60364-5-559 lighting; IEC 60364-5-55 mechanical; IEC 60364-7-7XX power); Pass 1 reaches 53/53 FULL GREEN"
```

---

## Task 5: Bucket B cleanup (Phase C) — Sonnet

**Why Sonnet:** ~14 mechanical edits across arc-flash evals + harness Python + CLAUDE.md. Per-occurrence triage rules are explicit; no engineering judgment.

**Files:**
- Modify: 8 arc-flash + arc-flash-labelling eval YAMLs (silent-regression fixes + minors)
- Modify: `scripts/validate-examples.py` (M2/M3/M4/M7)
- Modify: `CLAUDE.md` (5 doc polish items)

### Sub-step group C-1: Silent-regression fixes (Task 3 Important from 3-W2a code review)

#### Step 1: Fix arc-flash/eval-05 free-text flag substring (line 37)

- [ ] Read `electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml` around line 37. The current assertion is:

```yaml
  - assertion: 'ir.flags contains "specialised teams"'
    description: <whatever>
```

`ir.flags` is a token array; `"specialised teams"` is recommendation prose that never appears as a token. Replace with EITHER (a) the closest token-array semantics if a related token exists in the prompt's flag taxonomy, OR (b) downgrade to `severity: info` with explicit placeholder wording.

Inspect the surrounding context (description + neighbouring assertions). Decision rule:
- If the description mentions a forward-looking field that doesn't exist (e.g. "flag_messages[] field"): downgrade to `severity: info`, add `description: "ALWAYS-PASS placeholder pending flag_messages[] field — see [[sprint-3w2a-shipped]] deferred queue"`, keep the assertion as `ir.flags != null`.
- Otherwise: replace with the closest known token. The neighbour at line 33 is `ir.flags contains "INCIDENT_ENERGY_GT_40_RESTRICTED"` — already covers the meaningful claim. DELETE the free-text line.

Apply the chosen fix. Commit message will document the choice per-occurrence.

#### Step 2: Fix arc-flash/eval-08 free-text flag substring (line 37)

- [ ] Same triage on `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml` line 37 (`"Refine via protection coordination"`). Neighbour at line 33 is `ir.flags contains "CONSERVATIVE_T_CLEAR_DEFAULT_USED"` — already meaningful. DELETE the free-text line (same decision as Step 1, no forward intent).

#### Step 3: Triage 11 `!= null` placeholder occurrences

For each occurrence below, read the surrounding description + context, then apply per-occurrence rule:
- **If description has forward intent** (mentions a missing field or future runtime support): downgrade to `severity: info`, tighten description to explicitly say "ALWAYS-PASS placeholder pending X".
- **If no forward intent** AND the field is required by the IR schema (so the check is fully redundant): DELETE the assertion.
- **If no forward intent** AND the field is optional in the schema: downgrade to `severity: info`, description "Placeholder check — schema already validates presence when emitted".

Occurrences:
- [ ] `electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml:134` — `ir.flags != null`
- [ ] `electrical/arc-flash/evals/eval-04-missing-fault-data.yaml:60` — `ir.nodes[?(@.node_id=="DB-X1")].shock_approach_source != null`
- [ ] `electrical/arc-flash/evals/eval-04-missing-fault-data.yaml:64` — `ir.nodes[?(@.node_id=="DB-X1")].label_recommended != null`
- [ ] `electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml:43` — `ir.nodes[?(@.node_id=="MSB-RESTRICTED")].shock_approach_source != null`
- [ ] `electrical/arc-flash/evals/eval-06-rationale-block.yaml:18` — `ir.rationale.chat_summary != null`
- [ ] `electrical/arc-flash/evals/eval-06-rationale-block.yaml:62` — `ir.rationale.sections[*].decisions != null`
- [ ] `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml:43` — `ir.nodes[?(@.node_id=="DB-NO-OCPD-INFO")].incident_energy_cal_per_cm2 != null`
- [ ] `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml:48` — `ir.nodes[?(@.node_id=="DB-NO-OCPD-INFO")].ppe_category != null`
- [ ] `electrical/arc-flash-labelling/evals/eval-06-rationale-block.yaml:56` — `ir.rationale.sections[*].decisions != null`
- [ ] `electrical/arc-flash-labelling/evals/eval-07-svg-template-population.yaml:40` — `ir.labels[*].svg_content != null`
- [ ] `electrical/arc-flash-labelling/evals/eval-07-svg-template-population.yaml:53` — `ir.labels[*].format_applied != null`

Note: schema-presence checks (`rationale.chat_summary != null`, `labels[*].svg_content != null`, etc.) where the field is REQUIRED in the IR schema → DELETE (fully redundant). For OPTIONAL fields → downgrade with placeholder wording.

#### Step 4: Verify Bucket B-1 outcome

- [ ] Run:
```bash
grep -rn 'ir.flags contains "specialised teams"\|Refine via protection coordination' electrical/arc-flash/evals/
```
Expected: empty output.

- [ ] Run:
```bash
grep -rn "!= null" electrical/arc-flash/evals/ electrical/arc-flash-labelling/evals/ | wc -l
```
Expected: significantly fewer than 11 (deleted occurrences) OR same count but with `severity: info` consistently (downgraded occurrences).

### Sub-step group C-2: Task 3 minors

#### Step 5: arc-flash/eval-09 numeric→string coercion comment

- [ ] Read `electrical/arc-flash/evals/eval-09-shock-approach-out-of-range.yaml` around line 36 (`matches "^(790|840)$"`). Add a YAML comment ABOVE the assertion line:

```yaml
    # NOTE: regex match relies on runtime coercing numeric values to string; canonical grammar lacks an `in [N1, N2]` numeric-set operator.
  - assertion: 'ir.nodes[?(@.node_id=="MV-36KV")].shock_approach_restricted_mm matches "^(790|840)$"'
```

#### Step 6: arc-flash-labelling/eval-08a cross-cutting all_equal check

- [ ] Read `electrical/arc-flash-labelling/evals/eval-08a-qr-code-emitted.yaml`. Find the per-label MSB-1 check block (lines 20-30). After the per-node assertions, ADD this cross-cutting check:

```yaml
  # Cross-cutting: every label (not just MSB-1) must carry the same node-scoped qr_code_url shape
  - assertion: 'ir.labels[*].label_content_qr_code_url all_equal "https://example.com/af/project-123/MSB-1"'
    description: Every label (across all nodes) must carry qr_code_url = <base_url>/<node_id>; degenerate single-node case still enforces the universal claim
    severity: warning
    # TODO: tighten once eval-08a fixture is extended to multiple nodes
```

#### Step 7: arc-flash/eval-03 method_fallback_trail description tighten

- [ ] Read `electrical/arc-flash/evals/eval-03-coefficient-fallback-trap.yaml` lines 40-44. Each of the 2 substring-on-array assertions has a description noting "object-membership check approximated as substring". Extend each description to also note: "substring may also incidentally match a `method` field with the same value — pairing semantics not enforced; severity: warning". Verify both assertions already have `severity: warning` (Task 3 audit confirmed they do).

### Sub-step group C-3: Task 4 minors (scripts/validate-examples.py)

#### Step 8: M2 — add total_failures counter on META-SCHEMA-INVALID branch

- [ ] Read `scripts/validate-examples.py` around line 105-108. The current block is:

```python
        try:
            jsonschema.Draft7Validator.check_schema(schema_test)
        except Exception as e:
            results[skill_name].append(("META-SCHEMA-INVALID", schema_path, str(e)[:200]))
```

Replace with:

```python
        try:
            jsonschema.Draft7Validator.check_schema(schema_test)
        except Exception as e:
            results[skill_name].append(("META-SCHEMA-INVALID", schema_path, str(e)[:200]))
            total_failures += 1
```

This closes a pre-existing silent-failure bug (a malformed IR schema would be reported but not counted toward exit code).

#### Step 9: M3 — remove unused `label` variable on line 173

- [ ] Read `scripts/validate-examples.py` around line 173. The current line is:

```python
            label = f"{skill_name}/{eval_basename}"
```

DELETE this line. It's not referenced anywhere in the function.

#### Step 10: M4 — drop f-prefix from lines 283/288/293

- [ ] Read `scripts/validate-examples.py` lines 283, 288, 293. Each looks like:

```python
    print(f"=== Pass 1 — Example outputs ===\n")
```

Change to (no `f` prefix — no interpolation):

```python
    print("=== Pass 1 — Example outputs ===\n")
```

Apply the same edit to all 3 lines (283 Pass 1, 288 Pass 2, 293 Pass 3).

#### Step 11: M7 — remove dead `_archive/` filter on lines 163-165

- [ ] Read `scripts/validate-examples.py` around line 163-165:

```python
        eval_files = sorted(glob.glob(f"{evals_dir}/eval-*.yaml"))
        # Exclude anything under _archive/
        eval_files = [p for p in eval_files if "/_archive/" not in p]
```

Since `glob.glob` is non-recursive, the filter is a no-op. DELETE the comment + filter line:

```python
        eval_files = sorted(glob.glob(f"{evals_dir}/eval-*.yaml"))
```

(Note: if future maintenance wants to include `_archive/` evals via recursive glob, the filter should be re-added at that point. For now it's dead code.)

#### Step 12: Verify harness still runs cleanly

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -8
```
Expected: AGGREGATE still 143/143 (or close — depends on whether C-1/C-2 deletions changed eval counts in Pass 2). If Pass 2 dropped below 81, debug.

### Sub-step group C-4: CLAUDE.md polish (5 minor items)

#### Step 13: Read CLAUDE.md

- [ ] Read `CLAUDE.md` in full to understand current state. Then apply 5 edits.

#### Step 14: I-3 scaffold-only electrical folders enumeration

- [ ] Find the line(s) listing the scaffold-only electrical folders (currently uses "etc."). Either:
- (a) Replace with: `all other electrical/<skill>/ folders are scaffolds (no inputs.json + schemas/ yet)`, OR
- (b) Enumerate the full list:

```bash
ls electrical/*/inputs.json 2>/dev/null | sed 's:/inputs.json::' | sed 's:electrical/::' | sort > /tmp/_shipped.txt
ls -d electrical/*/ 2>/dev/null | sed 's:electrical/::' | sed 's:/$::' | sort > /tmp/_all.txt
comm -23 /tmp/_all.txt /tmp/_shipped.txt
```

Option (a) is more maintainable. Use (a).

#### Step 15: M-2 timestamp leakage scan

- [ ] Run:
```bash
grep -nE "(2026|Sprint 3-W[0-9]|across [0-9]+ sprints|6 sprints)" CLAUDE.md
```
For each hit, replace specific dates/sprint-ids with generic language ("recent sprints" / "the established workflow"). The single `sprint-<id>` example in the commit format section is OK — that's a generic placeholder.

#### Step 16: M-3/M-4 per-skill folder bullet extension

- [ ] Find the per-skill folder bullet list (~lines 20-29). Add (where applicable):

```markdown
- `calculations/` (where applicable) — skill-specific calc declarations
- `annotations/` (where applicable) — annotation tags (e.g. drawing layer mapping)
- `templates/` (where applicable) — output templates (e.g. SVG label templates)
```

#### Step 17: M-5 deferred-sprint reference

- [ ] Find the line referencing "14 known db-layout content failures (deferred to Sprint 3-W2b)". Change to:

```markdown
- 14 known db-layout content failures (deferred — see [[sprint-3w-shipped]] and [[sprint-3w2a-shipped]] memory).
```

After this sprint ships, the deferred queue moves to `[[sprint-3w2b-shipped]]` and onward to Sprint 3-W2c.

#### Step 18: M-6 oneOf description duplication

- [ ] Find the core schemas section, line about `inputs.schema.json` description. Currently might have both:
- `oneOf [items, inputs, input_groups]`
- `(canonical WI1 items[], legacy inputs[], grouped input_groups[])`

These are duplicates. Tighten to one form:

```markdown
- `inputs.schema.json` — per-skill inputs.json metaschema; accepts canonical WI1 `items[]` (5 skills), legacy `inputs[]` (arc-flash family), or grouped `input_groups[]` (cable-sizing + small-power) at top level via oneOf.
```

#### Step 19: Verify CLAUDE.md is still well-formed

- [ ] Run:
```bash
wc -l CLAUDE.md
grep -nE "^## " CLAUDE.md | wc -l
```
Expected: ~114-120 lines, still 11 H2 headings.

### Final commit for Task 5

#### Step 20: Run full harness one more time

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Subtotal|AGGREGATE"
```
Expected: 53/53 + 81/81 + 9/9 = AGGREGATE 143/143 exit 0.

If Pass 2 dropped (because C-1 deletions removed checks), the count will be lower than 81. That's OK ONLY if the deletions were intentional per the triage rules and the file still validates.

#### Step 21: Commit Task 5

- [ ] Run:
```bash
git add electrical/arc-flash/evals/ electrical/arc-flash-labelling/evals/ scripts/validate-examples.py CLAUDE.md
git commit -m "feat(sprint-3w2b): Phase C — Bucket B cleanup (C-1 silent-regression fixes for 2 free-text-flag assertions + 11 != null placeholder triage; C-2 Task 3 minors: numeric coercion comment + eval-08a cross-cutting check + eval-03 description tighten; C-3 harness M2/M3/M4/M7 lint fixes including META-SCHEMA-INVALID counter bug closure; C-4 CLAUDE.md 5 doc polish items per-occurrence-documented in this commit body)"
```

---

## Task 6: Final validation + push + memory save (Phase D) — Opus

**Why Opus:** Ship-readiness judgment. The harness must show 143/143 exit 0 cleanly. Memory file authoring requires faithful sprint summary + accurate deferred-queue documentation.

### Step 1: Run the harness end-to-end

- [ ] Run:
```bash
python3 scripts/validate-examples.py
```

Expected (FULL OUTPUT not just subtotals):
```
=== Pass 1 — Example outputs ===
[per-skill report — all PASS]
Subtotal: 53/53 pass (0 failures)

=== Pass 2 — Eval files ===
[per-skill report — all PASS]
Subtotal: 81/81 pass (0 failures)

=== Pass 3 — Inputs files ===
[per-skill report — all PASS]
Subtotal: 9/9 pass (0 failures)

=== AGGREGATE: 143/143 pass (0 failures) ===
```
Exit code: 0.

If aggregate ≠ 143/143 or exit ≠ 0, halt — investigate before ship.

### Step 2: Confirm git state

- [ ] Run:
```bash
git log --oneline origin/main..HEAD
git status
```
Expected: 5 task commits ahead of origin/main, clean working tree.

### Step 3: Confirm schema correctness

- [ ] Run:
```bash
python3 -c "
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
jsonschema.Draft7Validator.check_schema(schema)
print('db-layout-ir.schema.json well-formed Draft-07')
"
```
Expected: `db-layout-ir.schema.json well-formed Draft-07`.

### Step 4: Confirm rationale + board_kind across all 20 db-layout examples

- [ ] Run:
```bash
python3 << 'EOF'
import json, glob
ok = 0; fail = 0
for f in sorted(glob.glob('electrical/db-layout/examples/*/output.json')):
    d = json.load(open(f))
    board_kind = d.get('board', {}).get('board_kind')
    has_rat = 'rationale' in d and len(d['rationale'].get('sections', [])) >= 6
    name = f.split('/')[-2]
    if board_kind in ('main_switchboard', 'specialty_board') and has_rat:
        ok += 1
    else:
        fail += 1
        print(f'BAD {name}: board_kind={board_kind!r}, has_rationale_with_sections={has_rat}')
print(f'{ok}/20 db-layout examples have board_kind + 6+ rationale sections')
EOF
```
Expected: 20/20.

### Step 5: Confirm Bucket B closure

- [ ] Run:
```bash
grep -rn 'ir.flags contains "specialised teams"\|Refine via protection coordination' electrical/arc-flash/evals/ || echo "C-1 clean"
grep -nE "^\s*total_failures \+= 1$" scripts/validate-examples.py | head -5
grep -nE 'label = f"' scripts/validate-examples.py || echo "M3 clean"
grep -nE 'print\(f"=== Pass' scripts/validate-examples.py || echo "M4 clean"
grep -nE '/_archive/' scripts/validate-examples.py || echo "M7 clean"
```
Expected: all 5 checks "clean" (no offending patterns remain).

### Step 6: Push to origin/main

- [ ] Run:
```bash
git push origin main
```
Expected: clean push, no hook failures, no remote rejection. Do NOT use --force or --no-verify.

After successful push:
```bash
git log --oneline origin/main..HEAD
```
Expected: empty output.

### Step 7: Save sprint-shipped memory

- [ ] Write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2b-shipped.md` following the shape of `sprint-3w2a-shipped.md`:

Frontmatter:
```yaml
---
name: sprint-3w2b-shipped
description: Sprint 3-W2b Content Completion shipped 2026-05-22 — db-layout schema reconciliation with board_kind discriminator + 10 LLM-authored specialty-board rationale blocks (KE/UK/INT bundles) + Bucket B cleanup (silent-regression fixes + harness M2/M3/M4/M7 lint + CLAUDE.md polish); 53/53 + 81/81 + 9/9 = AGGREGATE 143/143 FULL GREEN
metadata:
  type: project
---
```

Body covers:
- **✅ SHIPPED 2026-05-22** with commit range
- **What was delivered** (6 task summary)
- **Harness end-state** (FULL GREEN 143/143 — first time since Sprint 3-W started)
- **Known follow-up (Sprint 3-W2c)** — Bucket C Tier-4 lossy items + M1/M5/M6/M8 from Task 4 + remaining minor cleanups
- **Stats** (5 implementation commits + 2 doc commits; ~35 file ops planned, X actually delivered)
- **Cross-references** to `[[sprint-3w-shipped]]`, `[[sprint-3w2a-shipped]]`, `[[runtime-project-boundary]]`, `[[feedback-no-haiku-sonnet-opus-only]]`, `[[build-strategy-breadth-first]]`

### Step 8: Update MEMORY.md index

- [ ] Read `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`. Add a one-line entry after the `[Sprint 3-W2a shipped]` line:

```markdown
- [Sprint 3-W2b shipped](sprint-3w2b-shipped.md) — 2026-05-22: content completion; db-layout board_kind discriminator + 10 specialty-board rationale blocks (KE/UK/INT bundles) + Bucket B cleanup; harness reaches FULL GREEN 143/143
```

### Step 9: Report to user

- [ ] Final summary (≤ 8 lines):
- Push status (success)
- Pass 1 / Pass 2 / Pass 3 counts (must all be 100%)
- AGGREGATE count + exit code
- Memory file path
- Sprint 3-W2c queued (Bucket C Tier-4 lossy + M1/M5/M6/M8 polish)
- Next focal point: back to breadth-first skill build (cable-containment / riser / schematic / 4 calculation skills / 7 document skills)

---

## Risks & Mitigations

- **R1 — JSON Schema Draft-07 oneOf-with-const-discriminator.** Draft-07's oneOf may not behave intuitively when `properties.board_kind.const` is set inside each branch — jsonschema validates ALL branches and requires exactly one to pass. *Mitigation:* Task 1 Step 4 runs explicit positive + negative tests before committing. If the negative case passes, the oneOf is broken and Task 1 must re-author.

- **R2 — Rationale-authoring quality drift (LLM cites wrong clauses).** *Mitigation:* spec compliance reviewer verifies every `code_clause` field against `shared/standards/`; code quality reviewer checks engineering soundness. Any unverifiable citation drops `code_clause` from the decision (it's optional per the rationale schema).

- **R3 — Cross-board consistency in UK bundle.** uk-commercial-msb-3storey is parent to 3 sdb sub-boards; their `fed_from` values must match the MSB's board_id. *Mitigation:* Task 3 Step 4 explicitly authors all 4 files in one subagent dispatch so the subagent has full cross-board context.

- **R4 — Specialty-board section template divergence.** The 4 existing specialty boards (intl-dbcomms-data, intl-dbem-emergency-lighting, intl-dbgenset-changeover, intl-dbups-backed) use 6 sections (Board Identification, Incoming Supply, Circuit Breakdown, Selectivity Analysis, Compliance Assessment, Schedule Notes). Tasks 2/3/4 must MATCH this template — not invent a new one. *Mitigation:* every Phase B task includes "read intl-dbcomms-data as precedent" as Step 1 / 2.

- **R5 — Bucket B silent-regression triage decisions per-occurrence.** 11 `!= null` placeholders + 2 free-text-flag assertions × per-occurrence triage = 13 micro-decisions. Some will be "delete" and some "downgrade to info". *Mitigation:* Task 5 prompt makes the triage rule explicit. Implementer documents each decision in the commit message body so future review can audit.

- **R6 — Pass 2 count regression from Bucket B deletions.** Deleting `!= null` placeholders reduces the eval-file check count, but the FILE still validates (eval.schema.json doesn't enforce a minimum check count — checks[] minItems is 1). *Mitigation:* Task 5 Step 12 + Task 6 Step 1 confirm Pass 2 stays at 81/81. If a file falls to 0 checks (unlikely but possible), the YAML still passes the eval.schema.json oneOf.

- **R7 — Memory write path drift.** The memory directory is `/Users/linus/.claude/projects/.../memory/` outside the repo. *Mitigation:* Task 6 Step 7 uses the absolute path; the memory file is NOT committed to the repo.

- **R8 — Citation form ambiguity for KE specialty boards.** KE's `KS 1700:2018 § 313 (route to BS 7671 via §313)` form is the established convention but specialty-board citations (fire alarm, comms) may need additional jurisdiction-specific refs. *Mitigation:* Task 2 explicitly says "if a citation can't be grounded, leave `code_clause` out of that decision — never invent".

---

## Self-Review

**Spec coverage check:**
- §1 locked decisions (5) ✓ — D1 scope reflected in Task 5 boundary; D2 schema oneOf in Task 1; D3 LLM authoring in Tasks 2/3/4; D4 KE→UK→INT sequencing in Tasks 2/3/4; D5 Bucket B consolidation in Task 5.
- §2 scope (Bucket A + B; C deferred) ✓ — Tasks 1-4 cover Bucket A; Task 5 covers Bucket B; Bucket C deferred per Task 6 memory.
- §3 phases A-E ✓ mapped to Tasks 1, 2, 3, 4, 5, 6.
- §4 file ops ~35 ✓ — actual count: 1 schema + 20 example board_kind + 10 example rationale + ~14 Bucket B = ~45 file edits (slightly higher than spec estimate but in same order).
- §5 risks ✓ mirrored in Risks section.
- §6 acceptance ✓ — 8 acceptance criteria all mapped to Task 6 verification steps.
- §7 out-of-scope (Bucket C + Task 4 M1/M5/M6/M8) ✓ — Task 6 Step 7 memory file documents the deferred queue.
- §8 model selection ✓ — per-task model annotations match.
- §9 sprint workflow ✓ — Task 6 closes the brainstorm→spec→plan→subagent-driven-development→memory loop.

**Placeholder scan:** No TBD/TODO/"implement later" in plan steps. Every code step shows the actual content (assertion strings, schema fragments, command outputs).

**Type consistency:**
- `board_kind` enum values: `["main_switchboard", "specialty_board"]` consistent across Task 1 schema + Tasks 2-4 rationale + Task 6 verification.
- Section template counts: 9 for main_switchboard + 6 for specialty_board — consistent across Tasks 2/3/4.
- Citation forms per jurisdiction: KE `KS 1700:2018 § X (route to BS 7671 via §313)`, UK `BS 7671:2018+A2:2022 § X` + `BS EN 61439-3:2012`, INT `IEC 60364-X-XX:YYYY` + `IEC 61439-3:2012` — consistent across all relevant tasks.
- M2/M3/M4/M7 line refs verified against actual `scripts/validate-examples.py` state at commit `9a67044`.
- 11 `!= null` occurrences with exact file:line refs.
