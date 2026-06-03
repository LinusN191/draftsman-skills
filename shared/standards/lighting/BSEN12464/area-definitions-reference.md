# Area Definitions — BS EN 12464-1:2021 §4.2.2 + Table 6

Reference companion to `area-definitions.json`. Source: BS EN 12464-1:2021 §4.2.2.1, §4.2.2.2, §4.2.2.3, Table 6.

Engineers must verify against the current edition of the standard.

## §4.2.2.1 Task area

The partial area within the workplace in which the visual task is carried out.

- Illuminate to **Em given for the relevant task type in Table 5**.
- Uniformity U₀ ≥ 0.60 across the task area.

## §4.2.2.2 Immediate surrounding area

A band of **at least 500 mm width** around the task area within the visual field.

| Em(task) | Em(surrounding) |
|---|---|
| ≥ 750 lx | ≥ 500 lx |
| 500 lx | 300 lx |
| 300 lx | 200 lx |
| 200 lx | 150 lx |
| 100–150 lx | 100 lx |
| < 100 lx | Em(task) |

- Uniformity U₀ ≥ 0.40 across the immediate surrounding area.
- The ratio Em(surrounding)/Em(task) shall **not exceed 0.5 minimum** and **may not exceed 0.3 minimum** for visual comfort (Table 6 simplification: ratio in [0.3, 0.5]).

## §4.2.2.3 Background area

A band of **at least 3000 mm width** adjacent to the immediate surrounding area, within the limits of the space.

- **Em(background) ≥ max(Em(task) / 3, 50 lx)** — derived from Table 6 + absolute floor.
- Uniformity U₀ ≥ 0.10 across the background area.

## Table 6 ratio rules (consolidated)

The skill applies these as INV-14 (surrounding ratio) and INV-15 (background floor):

- **Surrounding:** `Em_target_lux` for `purpose=surrounding` zone must satisfy `0.3 × Em_task ≤ Em_target_lux ≤ 0.5 × Em_task`
- **Background:** `Em_target_lux` for `purpose=background` zone must satisfy `Em_target_lux ≥ max(Em_task / 3, 50)`
- **Uniformity:** U₀ thresholds 0.60 / 0.40 / 0.10 applied by INV-19 when per-zone achievement is graded
