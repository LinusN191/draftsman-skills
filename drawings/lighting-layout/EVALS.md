# EVALS — lighting-layout skill

Evaluation criteria for testing the lighting-layout skill. Each eval
defines a test input, the expected reasoning steps, and pass/fail criteria
for the output. Use these to verify a skill version before shipping.

---

## Eval 01 — Basic office layout (happy path)

**Input:**
```
Room: 10m × 8m
Ceiling height: 3.0m
Room type: open plan office
Luminaire: 600×600 LED recessed panel
Lumen output: 4500 lm
Wattage: 36W
```

**Expected reasoning shown in chat:**

| Step | Expected | Pass criteria |
|---|---|---|
| Step 2 | 500 lux, UGR ≤ 19, Ra ≥ 80 | Exact values per BS EN 12464-1:2021 Table 5.3 |
| Step 3 | Hm = 2.25m, RI = 1.98 | RI within ±0.05 of 1.98 |
| Step 4 | UF = 0.65–0.70 range | UF flagged as [ASSUMPTION] if no photometric data given |
| Step 5 | MF = 0.80 | MF flagged as [ASSUMPTION] |
| Step 6 | N ≥ 17 (rounded up) | N never rounded down |
| Step 7 | Grid achieves S ≤ SHR_max × Hm | Explicit spacing check shown |
| Step 8 | Positions in mm, snapped to 50mm | All x,y divisible by 50 |
| Step 9 | ≤ 51 luminaires per 10A circuit | Load calculation shown |

**Expected JSON output:**

- `room.room_index` between 1.90 and 2.05
- `calculation_summary.target_illuminance_lux` = 500
- `calculation_summary.achieved_illuminance_lux` ≥ 500
- `calculation_summary.compliant` = true
- `luminaires` array length ≥ 17
- All luminaire IDs unique (L01, L02, ...)
- All circuit loads ≤ 1840W
- At least 1 switch in `switches` array
- `calculation_summary.assumptions` non-empty (UF and MF always assumed)

**Fail conditions:**
- N rounded down (e.g. 16 when lumen method gives 16.3)
- No [ASSUMPTION: ...] tags on UF and MF
- Any luminaire position not snapped to 50mm grid
- Circuit load > 1840W (80% of 2300W)
- Missing drawing_notes array
- JSON missing any required top-level key

---

## Eval 02 — Lux target below standard minimum

**Input:**
```
Room: 8m × 6m
Ceiling height: 2.8m
Room type: open plan office
Client lux target: 300 lux (below BS EN 12464-1:2021 minimum of 500)
Luminaire: LED downlight, 1200 lm, 12W
```

**Expected behaviour:**

The skill must flag the non-compliance before proceeding.

**Pass criteria:**
- Output includes `[NON-COMPLIANCE RISK: ...]` in chat response
- Output includes message referencing BS EN 12464-1:2021 minimum of 500 lux
- Skill continues to produce a layout at 300 lux only if the non-compliance
  is explicitly flagged (does not silently comply with wrong target)
- `calculation_summary.non_compliance_flags` non-empty in JSON

**Fail conditions:**
- Skill produces 300-lux layout without any flag
- Skill refuses to proceed entirely without asking engineer to confirm

---

## Eval 03 — Missing luminaire lumen data

**Input:**
```
Room: 12m × 10m
Ceiling height: 3.5m
Room type: warehouse (low rack)
Luminaire: "LED highbay" (no lumen output stated)
```

**Expected behaviour:**

The skill must stop and ask for lumen output. It must not assume a value
and proceed.

**Pass criteria:**
- Skill asks for luminaire lumen output explicitly
- No JSON output emitted
- Question is specific: asks for "maintained lumen output at design conditions"
  or equivalent — not just "how many lumens"

**Fail conditions:**
- Skill assumes any lumen value and proceeds
- Skill emits JSON without lumen data confirmed

---

## Eval 04 — Circuit load check

**Input:**
```
Room: 20m × 15m
Ceiling height: 4.0m
Room type: open plan office
Luminaire: 600×600 LED panel, 4500 lm, 36W
```

**Expected behaviour:**

With a large room, many luminaires will be required. The skill must
correctly split into multiple circuits.

**Pass criteria:**
- Each circuit load ≤ 1840W (80% of 2300W on 10A MCB)
- If total load requires more than one circuit, `circuits` array has multiple entries
- Each circuit has non-overlapping `luminaire_ids`
- Total luminaire IDs across all circuits equals `luminaires` array length
- No luminaire ID appears in more than one circuit

**Fail conditions:**
- Any circuit with load > 1840W
- Same luminaire ID in two circuits
- Circuit count × max_per_circuit < total luminaires

---

## Eval 05 — Ceiling grid alignment

**Input:**
```
Room: 9m × 6m (9000mm × 6000mm)
Ceiling grid: 600mm module
Ceiling height: 2.8m
Room type: private office
Luminaire: 600×600 LED panel, 3500 lm, 28W
```

**Expected behaviour:**

Luminaire positions must snap to the 600mm grid. In a 9000×6000 room on a
600mm grid, valid x positions are 300, 900, 1500, 2100, 2700, 3300, 3900,
4500, 5100, 5700, 6300, 6900, 7500, 8100, 8700 (centres of 600mm cells).

**Pass criteria:**
- All luminaire x positions are multiples of 300mm (centred on 600mm grid)
- All luminaire y positions are multiples of 300mm
- Drawing note references ceiling grid module assumption

**Fail conditions:**
- Any position not on 600mm grid centres
- No mention of ceiling grid in drawing notes or assumptions

---

## Running evals manually

To run these evals against the skill, paste each input into a DraftsMan
chat session with only the lighting-layout skill active, then check each
output against the pass/fail criteria above.

For automated testing, compare the JSON output against the expected field
values using the test harness in `tests/`.

## Eval pass rate requirement

Before shipping a new skill version: all 5 evals must pass. Evals 01 and 04
are mandatory for any release. Evals 02, 03, and 05 must pass before
marking the version as production-ready.
