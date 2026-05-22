# Schematic Skill v1.0 Design

**Date:** 2026-05-22
**Predecessor:** Sprint 3-W2c (Runtime Readiness) — shipped at `5ee65d8` with harness FULL GREEN 143/143; skills repo declared runtime-ready
**Status:** Brainstorm complete; spec for review.

---

## §1 — Locked Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Scope | Control + protection schematics in single v1.0 (8 examples = 4 control + 4 protection across KE/UK/INT/US) |
| D2 | Consumer pattern | Hybrid: consumes db-layout-rollup + fault-level + earthing intents when available; leaf-mode fallback via engineer-provided context when intents absent |
| D3 | Producer | `produces_intent: "schematic"` — terminal in shipped skills (future tender-report / om-manual may consume) |
| D4 | IR architecture | Per-schematic IR (one schematic = one IR document) — mirrors db-layout's "one board = one IR" and sld's "one system = one IR" |
| D5 | Symbol library | ~40 BS EN 60617 symbols covering motor starter + protection + auxiliary — frozen list at sprint start; deeper coverage deferred to v1.1 |
| D6 | Citation form lessons from 3-W2c | Single-frame voltage references; if dual-frame needed, pair % with absolute volts (no two %s); standard publication years omitted unless cross-verified |

---

## §2 — Scope

### 8 examples (4 control + 4 protection across 4 jurisdictions)

**Control schematics (4):**
1. `ke-nairobi-workshop-motor-starter` — 11 kW DOL grinder, KE industrial workshop
   - Standards: BS EN 60617 + KS 1700:2018 § 552 (motor circuits, route to BS 7671 § 552 via §313)
   - Demonstrates: leaf-mode (no upstream intents available); single-motor starter logic
2. `uk-commercial-genset-changeover` — 250 kVA standby diesel + ATS to MSB, UK office
   - Standards: BS 7671:2018+A2:2022 § 560 safety services + BS 7671 § 537 (transfer switches) + BS EN 61082
   - Demonstrates: hybrid mode (consumes db-layout-rollup for MSB context); changeover sequence
3. `intl-hvac-vfd-control` — 22 kW pump set with VFD + soft-start, IEC commercial
   - Standards: IEC 60364-5-55 (motor circuits) + IEC 60947-4-2 (semiconductor motor controllers) + IEC 60617
   - Demonstrates: hybrid mode (consumes db-layout-rollup + fault-level); VFD control logic
4. `us-industrial-star-delta` — 15 HP star-delta starter, NEC industrial
   - Standards: NEC 2023 Article 430 (motor circuits) + IEEE Std 315 (symbols for diagrams used in the US)
   - Demonstrates: hybrid mode (consumes db-layout-rollup); star-delta sequence with timer logic

**Protection schematics (4):**
5. `ke-industrial-transformer-protection` — 11 kV / 415 V step-down with IDMT overcurrent + restricted earth fault, KE industrial step-down
   - Standards: KS 1700:2018 + IEC 60255 (protection relays) + IEC 61850 (protection signalling)
   - Demonstrates: hybrid mode (consumes fault-level + earthing); IDMT 51 + REF 87N coordination
6. `uk-commercial-11kv-differential` — 11 kV intake transformer differential (87T), UK commercial intake
   - Standards: BS 7671:2018+A2:2022 § 314 + IEC 60255 + ENA G59/G99 grid code reference
   - Demonstrates: hybrid mode (consumes fault-level + db-layout-rollup); 87T differential + 50/51 backup
7. `intl-substation-busbar-protection` — HV substation busbar protection (87B + 50BF breaker failure), IEC HV substation
   - Standards: IEC 60255 + IEC 61850-9-2 (process bus) + IEC 60044 (instrument transformers)
   - Demonstrates: leaf-mode (HV substation has no shipped-skill upstream); 87B + 50BF tripping logic
8. `us-motor-protection-relay` — 600V industrial motor with 49 thermal + 50/51 overcurrent + 86 lockout, NEC industrial
   - Standards: NEC 2023 Article 430 + IEEE C37.96 (motor protection) + IEEE Std 315
   - Demonstrates: hybrid mode (consumes db-layout-rollup + fault-level); ANSI 49+50+51+86 coordination

### IR shape (top-level)

```json
{
  "drawing_type": "schematic",
  "version": "1.0",
  "meta": { "project_id": "...", "skill_version": "schematic/1.0.0", "produced_at": "..." },
  "jurisdiction": "GB | EU | INT | US | KE",
  "schematic_type": "control_motor_starter | control_changeover | control_sequence | protection_overcurrent | protection_differential | protection_motor | protection_busbar",
  "sheet": {
    "sheet_id": "...",
    "title": "...",
    "page_of": "1/1"
  },
  "items": [
    { "item_id": "...", "device_class": "contactor | overload | breaker | relay | timer | terminal | lamp | push_button | selector_switch | ...", "bs_en_60617_ref": "...", "rating": "...", "ansi_function_code": "49 | 50 | 51 | 86 | 87T | 87B | ..." }
  ],
  "connections": [
    { "wire_id": "...", "from_item": "...", "from_terminal": "...", "to_item": "...", "to_terminal": "...", "conductor_csa_mm2": "...", "voltage_class": "control_LV | aux_DC | aux_AC", "function": "..." }
  ],
  "labels": [ { "anchor_item": "...", "text": "...", "kind": "device_tag | sequence_note | terminal_number | wire_number" } ],
  "protection_settings": [
    { "ansi_code": "...", "device_id": "...", "set_value": "...", "set_unit": "...", "time_curve": "...", "ct_ratio": "...", "tool_call_pending": "true | false" }
  ],
  "sequence_of_operation": "...",
  "consumed_intents": [ { "intent_type": "db-layout-rollup | fault-level | earthing", "present": true, "fabricated_nodes": [...] } ],
  "compliance_summary": { "compliant": true, "non_compliance_flags": [], "assumptions": [...] },
  "drawn_as_symbols": [...],
  "flags": [...],
  "rationale": { "chat_summary": "...", "sections": [...] }
}
```

`oneOf` branching:
- `schematic_type: control_*` → requires `sequence_of_operation` (non-empty) + `items[]` contains at least one contactor/timer/push_button; `protection_settings[]` may be empty
- `schematic_type: protection_*` → requires `protection_settings[]` (non-empty) + each setting carries ANSI function code; `sequence_of_operation` may be omitted

### Standards + citation form per jurisdiction

| Jurisdiction | Primary standards | Citation form |
|---|---|---|
| GB | BS 7671:2018+A2:2022, BS EN 60617, BS EN 61082, IEC 60255, IEC 61850 (via BS EN) | `BS 7671:2018+A2:2022 § X.X.X`; `BS EN 60617 IEC 617-X` |
| KE | KS 1700:2018, KS adoption of BS EN 60617, IEC 60255 | `KS 1700:2018 § X (route to BS 7671 via §313)`; `IEC 60617` |
| INT | IEC 60364-X-XX, IEC 60617, IEC 60255, IEC 61850 | `IEC 60364-X-XX § X.X.X`; `IEC 60617` |
| US | NEC 2023, NFPA 70, IEEE Std 315, IEEE C37.x | `NEC 2023 Article X` or `NFPA 70 § Y`; `IEEE Std 315` |

Lesson from 3-W2c: omit standard publication years unless cross-verified. Don't fabricate.

### Out of scope (deferred to v1.1 or later)

- BS EN 60617 symbols beyond the v1.0 ~40 (full ~200-symbol library expansion)
- Sequence-of-operation TEXT generation (extended prose narrative companion)
- Ladder-logic / PLC ST code emission (IEC 61131-3 territory)
- HV substation protection beyond busbar (e.g. line distance, distance backup, autoreclose)
- US protection schematics beyond motor + transformer (e.g. generator protection 27/59/81)
- Engineering-content overhauls if Task 4/5/6 prompts end up needing a deeper rewrite mid-sprint

---

## §3 — Phases & Tasks

### Phase A — Infrastructure (Tasks 1-3)

**Task 1 — Skill skeleton + manifest** (Sonnet, mechanical)
- Promote `electrical/schematic/` from v0.1.0 stub to v1.0.0 scaffold
- Author `skill.manifest.json` (status: stable, version 1.0.0, produces_intent: schematic, consumes_intents: [db-layout-rollup, fault-level, earthing], inputs_path: inputs.json, full standards list, compatible_runtimes)
- Author full `README.md` (replaces stub)
- Author `CHANGELOG.md` initial v1.0.0 entry
- Create empty subdirs (schemas/, rules/, constraints/, validation/)

**Task 2 — IR + intent schemas** (Opus, judgment)
- Author `schemas/schematic-ir.schema.json` with strict additionalProperties: false + 7-value schematic_type enum + oneOf branching for control vs protection (per §2)
- Author `schemas/schematic-intent.schema.json` for terminal intent emission
- Run positive + negative tests for each oneOf branch BEFORE downstream tasks consume the schema

**Task 3 — Symbol library + ontology** (Sonnet, mechanical JSON authoring)
- Author ~40 BS EN 60617 symbols under `shared/symbols/electrical/schematic/`:
  - Motor starter (10): contactor (1NO/1NC/3-pole/4-pole variants), overload, isolator, motor (3-phase/single-phase), thermistor, PTC
  - Protection (12): IDMT 51, instantaneous 50, differential 87, restricted EF 87N, distance 21, lockout 86, undervoltage 27, overvoltage 59, breaker 52, current transformer, voltage transformer, ANSI table reference
  - Auxiliary (10): terminal block (rail / strip), wire reference, lamp (red/green/amber/blue/white), push-button (NO/NC/emergency-stop), selector switch (2-pos/3-pos)
  - Control logic (8): timer (on-delay / off-delay), counter, latch, AND/OR/NOT gate, signal converter
- Per-symbol JSON: `{id, label, bs_en_60617_ref, ieee_std_315_ref (where applicable), sketch_ascii, drawn_as}`
- Author `ontology/schematic-types.json` (taxonomy of 7 schematic_type enum values + descriptions)

### Phase B — Prompts (Tasks 4-6, Opus)

**Task 4 — generator.md** (Opus)
- 12-step generation flow:
  1. Validate consumed intents (db-layout-rollup + fault-level + earthing)
  2. Identify schematic_type from inputs + intent presence
  3. Resolve symbol library references (BS EN 60617)
  4. Place items[]: enumerate devices for the chosen schematic_type
  5. Wire connections[]: control vs auxiliary vs power circuit
  6. Assign protection_settings[] (for protection_*) or sequence_of_operation (for control_*)
  7. Label devices: tag + terminal numbers + sequence notes
  8. Flag tool_call_pending where calc.x.y not yet executed (e.g. CT ratio computation deferred)
  9. Emit rationale: 6-9 sections + chat_summary 40-500
  10. Per-jurisdiction citation form table
  11. Hybrid-mode handling: leaf fallback when intents absent
  12. Validate against schematic-ir.schema.json
- Reference the post-3W2c db-layout/generator.md for canonical structure

**Task 5 — validator.md** (Opus)
- ~10 INV invariants:
  - INV-1: schema_valid against schematic-ir.schema.json
  - INV-2: schematic_type ↔ items consistency (control_* requires contactor/timer; protection_* requires protection relay)
  - INV-3: connection topology valid (no orphan items; no dangling wires)
  - INV-4: protection_settings present when schematic_type=protection_*; sequence_of_operation present when schematic_type=control_*
  - INV-5: symbols all resolve to shared/symbols/electrical/schematic/
  - INV-6: consumed_intents shape valid (matches db-layout-rollup / fault-level / earthing schemas)
  - INV-7: citation form correct per jurisdiction (KE: dual-routing; UK: BS; INT: IEC; US: NEC/IEEE)
  - INV-8: no banned annotations (`switch-fuse` → must be `main_switch_fused`; `§ 311` → must be `§ 311.1`)
  - INV-9: rationale block complete (40 ≤ chat_summary ≤ 500; 6 ≤ sections ≤ 9)
  - INV-10: cross-skill cascade consistency (consumed intent IDs resolve to producer skill outputs)
- Severity policy: critical for schema; warning for content advisories; info for placeholders

**Task 6 — reviewer.md** (Opus)
- 6 D-decisions:
  - D1: engineering correctness (control logic sound / protection settings defensible against device manufacturer typicals)
  - D2: standard refs grounded (no invented clause numbers; no fabricated publication years)
  - D3: symbol library coverage (all referenced symbols exist under shared/symbols/electrical/schematic/)
  - D4: cross-skill cascade consistency (consumed_intents shapes match producers)
  - D5: schematic_type appropriate to use case (e.g. don't classify a motor protection scheme as control_motor_starter)
  - D6: rationale prose quality (engineering reasoning defensible; no LLM filler; each section adds value)

### Phase C — Jurisdictional examples (Tasks 7-8, Opus, bundled by category)

**Task 7 — Control schematics bundle (4 examples)** (Opus)
- Dispatch single Opus subagent with full context for all 4 control examples
- Per-example: input.json + output.json + reasoning.md + sample-schedule.md (if applicable for changeover/sequence)
- Cross-example consistency: each example's `consumed_intents` matches the manifest's declared consumes_intents

**Task 8 — Protection schematics bundle (4 examples)** (Opus)
- Dispatch single Opus subagent with full context for all 4 protection examples
- Per-example: input.json + output.json + reasoning.md + protection-settings-table.md (typical)
- Cross-example consistency: ANSI function codes per IEEE C37.2; CT ratios cited per device manufacturer typicals (e.g. ABB REF615, Siemens 7UM62)
- Engineering content care: protection settings must be defensible (no fabricated CT ratios, no invented stabilising resistor values); flag tool_call_pending where deeper calc needed

### Phase D — Evals + rules + constraints + validation (Tasks 9-11)

**Task 9 — Evals authoring (~10 evals)** (Opus, judgment)
- Per spec §2 acceptance:
  - 1 happy_path per category (2): control DOL + protection IDMT
  - 1 edge_case (1): incomplete intent consumed (leaf-mode fallback)
  - 1 compliance_failure (1): missing protection setting on a protection schematic
  - 1 cross_validation (1): db-layout-rollup intent cascade verified
  - 1 jurisdiction_switch (1): same motor starter across KE → UK → INT → US (citation form variance)
  - 1 rationale_block (1): 6+ sections + chat_summary 40-500
  - 1 skill_specific (1): symbol library resolution
  - 1 validation_trap (1): banned `switch-fuse` (should be `main_switch_fused`) detection
- All evals canonical eval.schema.json shape (Format A with name+skill+input+checks per post-3W2a)

**Task 10 — Rules + constraints + validation + inputs.json** (Sonnet, mechanical YAML/JSON)
- 5 rules YAMLs:
  - motor-protection-coordination.yaml (49 thermal vs motor full-load curve)
  - contactor-rating.yaml (AC-3 utilisation category; motor inrush coordination)
  - overload-class.yaml (class 5 / 10 / 20 / 30 per motor service)
  - differential-stability.yaml (bias slope + stabilising resistor sizing)
  - busbar-protection-zoning.yaml (zone-overlap with breaker failure 50BF)
- 3 constraints + validation YAMLs:
  - schema-cross-references.yaml (every symbol ref resolves; every wire endpoints to known items)
  - protection-coordination.yaml (selectivity cascade; no upstream device tripping before downstream)
  - banned-annotations.yaml (switch-fuse, bare § 311, dual-frame VD %, IEC 60364-7-701 for kitchens, etc. — lessons from 3-W2c)
- inputs.json with items[] taxonomy (~25-30 items):
  - schematic_type selector (enum: 7 values)
  - intent presence flags (db-layout-rollup_present, fault-level_present, earthing_present)
  - leaf-mode fallback context (engineer-provided breaker info, fault current, earthing system type)
  - jurisdiction (GB / EU / INT / US / KE)
  - device declarations (motor rating, transformer kVA, etc.)
  - depends_on graph branches by schematic_type

**Task 11 — Bookkeeping + cross-cutting validation** (Sonnet, mechanical)
- Update `SKILLS_STATUS.md`: 10 shipped (was 9)
- Update `ARCHITECTURE.md` if any new cross-skill pattern surfaced (likely no — schematic mirrors existing patterns)
- Update `CLAUDE.md`: 10 drawings shipped → 2 remaining (cable-containment + riser)
- Run `python3 scripts/validate-examples.py` after each task touching schematic — must maintain 143/143 baseline + add schematic contribution toward 162/162

### Phase E — Final ship (Task 12, Opus)

**Task 12 — Final validation + push + memory save**
- Run 3-pass harness; expect AGGREGATE **162/162 exit 0** (143 baseline + 8 examples + ~10 evals + 1 inputs.json)
- Push origin/main (no `--force` / `--no-verify`)
- Save `schematic-shipped.md` memory file under `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/`
- Update MEMORY.md index entry
- Report: schematic v1.0 shipped; 2 drawings remaining (cable-containment + riser); ready for runtime end-to-end testing

---

## §4 — File Operations Summary

| Phase | Files modified | Files created |
|---|---|---|
| A Task 1 — Skeleton | electrical/schematic/skill.manifest.json (rewrite) | electrical/schematic/README.md (rewrite), CHANGELOG.md |
| A Task 2 — Schemas | 0 | 2 (ir + intent schemas) |
| A Task 3 — Symbols | 0 | ~40 symbol JSONs + 1 ontology JSON |
| B Tasks 4-6 — Prompts | 0 | 3 (generator + validator + reviewer) |
| C Task 7 — Control bundle | 0 | 4 × (input.json + output.json + reasoning.md) + optional sample-schedule.md |
| C Task 8 — Protection bundle | 0 | 4 × (input.json + output.json + reasoning.md) + protection-settings-table.md |
| D Task 9 — Evals | 0 | ~10 eval-*.yaml |
| D Task 10 — Rules + inputs | 0 | 5 rules YAMLs + 3 constraints/validation YAMLs + 1 inputs.json |
| D Task 11 — Bookkeeping | SKILLS_STATUS.md, CLAUDE.md, ARCHITECTURE.md (maybe) | 0 |
| E Task 12 — Ship | MEMORY.md (index) | 1 memory file |
| **Total** | **~3-4 modified** | **~80-90 created** |

Comparable to small-power v1.0 (~64 files). 2-3 dev day budget.

---

## §5 — Risks & Mitigations

- **R1 — Schematic IR shape complexity.** *Mitigation:* Task 2 uses Opus + writes positive + negative tests for each oneOf branch BEFORE downstream tasks consume the schema. Halt if Task 2 exceeds 1 dev-day.
- **R2 — Symbol library scope creep.** *Mitigation:* Task 3 enumerates EXACTLY ~40 symbols at start; freezes list; anything beyond → v1.1.
- **R3 — Cross-skill cascade test failure.** *Mitigation:* Task 12 extends Sprint 3-W2c's A2 audit to verify the 3 new producer→consumer pairs resolve cleanly.
- **R4 — Protection schematic engineering depth.** *Mitigation:* Task 8 spec compliance reviewer checks every protection setting + CT ratio against manufacturer typicals; code quality reviewer checks engineering soundness; defer-with-note if a setting can't be grounded.
- **R5 — Numeric refinement reversal (lesson from 3-W2c Task 1).** *Mitigation:* Task 8 prompt explicitly says "voltage values cite single reference frame; if dual-frame needed, pair % with absolute volts not two %s".
- **R6 — Prompt drift from post-3W2c additions.** *Mitigation:* Tasks 4-6 implementer references db-layout/prompts/generator.md as the post-3W2c canonical precedent.
- **R7 — Inputs.json depends_on graph cycles.** *Mitigation:* Task 10 runs A4-style inputs.json taxonomy audit before commit.
- **R8 — Eval count + harness baseline shift.** *Mitigation:* Task 11 runs harness after EACH task; any drop below 143 baseline halts.
- **R9 — Runtime testing deferred.** *Mitigation:* explicitly accept — schematic shipping doesn't change the runtime-readiness story; new skill follows the same contracts.

---

## §6 — Acceptance Criteria

1. **Harness aggregate:** `python3 scripts/validate-examples.py` exit 0 with AGGREGATE **162/162** (143 baseline + 8 examples + ~10 evals + 1 inputs.json).
2. **Schema correctness:** schematic-ir.schema.json + schematic-intent.schema.json Draft-07 valid; positive + negative tests pass for each oneOf branch.
3. **Examples complete:** 8 examples (4 control + 4 protection across KE/UK/INT/US), each with input.json + output.json + reasoning.md + supplementary md where applicable. All 8 validate against schematic-ir.schema.json.
4. **Cross-skill audit:** 3 new producer→consumer pairs verified clean (db-layout-rollup → schematic; fault-level → schematic; earthing → schematic).
5. **Prompts post-3W2c-aligned:** generator + validator + reviewer reference board_kind discriminator, KE jurisdiction, post-3W2c citation form, main_switch_fused canonical enum where relevant.
6. **Symbol library:** ~40 BS EN 60617 symbols authored under shared/symbols/electrical/schematic/, each with bs_en_60617_ref + sketch_ascii.
7. **Inputs.json valid:** items[]-shape, depends_on graph clean, all required items have example coverage.
8. **Documentation:** schematic-shipped.md memory file + MEMORY.md index + CLAUDE.md build-status (10 shipped, 2 drawings remaining) + SKILLS_STATUS.md.
9. **Git:** committed cleanly to origin/main. 12 task commits + 2 doc commits (spec + plan) = 14 commits.

---

## §7 — Out-of-Scope Handoff (v1.1 or later)

- **BS EN 60617 symbol library expansion** beyond v1.0 ~40 (full ~200-symbol library)
- **Sequence-of-operation TEXT generation** (extended prose narrative companion to control schematics)
- **Ladder-logic / PLC ST code emission** (IEC 61131-3 territory)
- **HV substation protection beyond busbar** (line distance, distance backup, autoreclose)
- **US protection schematics beyond motor + transformer** (generator protection 27/59/81)
- **Engineering content overhauls** if Task 4/5/6 prompts end up needing deeper rewrites mid-sprint
- **Pending lighting-layout content overhaul** (carried from 3-W2c deferred queue)
- **Bucket C — Tier-4 lossy eval conversions** (carried from 3-W2c)

---

## §8 — Model Selection

Per `[[feedback-no-haiku-sonnet-opus-only]]`:
- **Sonnet:** Tasks 1 (skeleton), 3 (symbol library), 10 (rules + constraints + validation + inputs.json), 11 (bookkeeping)
- **Opus:** Tasks 2 (schemas), 4 (generator), 5 (validator), 6 (reviewer), 7 (control bundle), 8 (protection bundle), 9 (evals), 12 (final ship)

Total: 12 tasks. 4 Sonnet + 8 Opus.

---

## §9 — Sprint Workflow

Standard pattern per [[sprint-3w2a-shipped]] / [[sprint-3w2b-shipped]] / [[sprint-3w2c-shipped]]:
1. Spec (this doc) approved by user
2. Plan authored via `superpowers:writing-plans` → `docs/superpowers/plans/2026-05-22-schematic-skill-sprint.md`
3. Execute via `superpowers:subagent-driven-development`, 2-stage review per task, continuous execution
4. Memory save on ship; index updated; remaining drawings: cable-containment + riser

---

## Cross-references

- [[sprint-3w2c-shipped]] — predecessor; runtime-ready skills repo
- [[sprint-3w2b-shipped]] — content completion + FULL GREEN baseline
- [[sprint-3w2a-shipped]] — schema standardisation (canonical eval.schema.json + inputs.schema.json)
- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — model rules
- [[build-strategy-breadth-first]] — schematic is 10th shipped skill; 2 drawings + 4 calculations + 7 documents remain after this
- [[small-power-shipped]] — closest prior pattern (similar 8-section rationale + 4-jurisdiction examples)
- [[cable-sizing-shipped]] — cross-skill consumer pattern reference (multi-intent hybrid consumer)
