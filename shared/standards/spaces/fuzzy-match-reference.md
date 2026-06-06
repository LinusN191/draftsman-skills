# Room-Type Fuzzy-Match Reference

Reference algorithm + test fixtures for orchestrators implementing fuzzy lookup of
non-canonical `Room.type` strings against the canonical taxonomy at
`shared/standards/spaces/room-types/*.json`.

Per `[[runtime-project-boundary]]`, this skills repo ships the **ALGORITHM SPEC +
TEST FIXTURES**. Orchestrators (DraftsMan runtime / Claude CLI / MCP servers / future
tooling) implement the engine in their own runtime layer.

---

## When fuzzy match is needed

Architectural drawing parsers typically emit room labels in title-case human language —
"Open Plan Office", "Operating Theatre 1", "ICU Bay 3", "Corridor", "WC" — rather
than the canonical snake_case `canonical_id` form expected by `Room.type`
(`space_planning_types.planned_work_space`, `healthcare_spaces.operating_theatre`,
`healthcare_spaces.inpatient_care_spaces.patient_room_intensive_care`,
`circulation_spaces.primary_circulation_spaces.corridor`,
`facility_service_spaces.restroom`).

The orchestrator **MUST** normalize each raw label to a `canonical_id` before passing
it to a skill via `Room.type`.

---

## Algorithm — 4-tier match priority

Process each non-canonical input string `s` through the tiers in order. Return on
first match.

### Tier 1: Exact match (highest priority)

If `s` already equals a `canonical_id` in any `room-types/*.json` file, return it
unchanged.

```python
if s in canonical_ids_set:
    return s
```

### Tier 2: Snake_case normalization match

Normalize `s` to snake_case, strip trailing suffix numbers, then check against
canonical_ids and their segment suffixes.

```python
import re

normalized = s.strip().lower()
normalized = re.sub(r'[-\s]+', '_', normalized)      # spaces/hyphens → underscore
normalized = re.sub(r'[^\w]', '', normalized)         # drop remaining punctuation
normalized = re.sub(r'_\d+$', '', normalized)         # strip suffix number ("theatre_1" → "theatre")

for cid in canonical_ids_set:
    parts = cid.split('.')
    # Try matching last 1, 2, or 3 dot-segments (suffix match)
    for n in range(1, 4):
        suffix = '.'.join(parts[-n:])
        suffix_underscored = '_'.join(parts[-n:])
        if normalized in (suffix, suffix_underscored):
            return cid
```

### Tier 3: Alias match

Check `common_aliases[]` arrays across all room-types entries against the same
normalized form.

```python
for entry in all_room_types_entries:
    for alias in entry.get('common_aliases', []):
        alias_normalized = re.sub(r'[-\s]+', '_', alias.strip().lower())
        alias_normalized = re.sub(r'[^\w]', '', alias_normalized)
        alias_normalized = re.sub(r'_\d+$', '', alias_normalized)
        if alias_normalized == normalized:
            return entry['canonical_id']
```

### Tier 4: Levenshtein distance fallback (≤2 edits)

For strings still unmatched, compute Levenshtein edit distance against all
`canonical_id` values and all alias strings (use the normalized form throughout).
Return the closest candidate if distance ≤ 2. Catches common typos and minor
spelling variations.

```python
def levenshtein(a: str, b: str) -> int:
    """Standard dynamic-programming Levenshtein implementation."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[:]
        dp[0] = i
        for j in range(1, n + 1):
            dp[j] = prev[j - 1] if a[i-1] == b[j-1] else 1 + min(prev[j], dp[j-1], prev[j-1])
    return dp[n]

best_match, best_distance = None, float('inf')
for candidate, cid in candidate_to_canonical.items():   # candidate = normalized alias or cid segment
    d = levenshtein(normalized, candidate)
    if d < best_distance and d <= 2:
        best_distance = d
        best_match = cid
return best_match   # None when no candidate is within 2 edits
```

### Tier 5: Embedding-similarity fallback (optional, runtime-specific)

If the orchestrator has LLM access, compute semantic embedding cosine similarity
between `normalized` and every `canonical_id` + alias string. Return the closest
match only when similarity ≥ 0.85.

**This tier is OPTIONAL.** CLI tools and lightweight orchestrators without LLM access
stop at Tier 4 and fall through to engineer override (see below).

---

## Test fixtures

Orchestrators verify their fuzzy-match implementation against these 10
input/expected-output pairs drawn exclusively from the 13-category taxonomy shipped
in `shared/standards/spaces/room-types/*.json`. No residential entries exist in this
taxonomy (OmniClass Table 13 scope; residential is Table 11).

| # | Input string | Expected `canonical_id` | Match tier | Notes |
|---|---|---|---|---|
| 1 | `circulation_spaces.primary_circulation_spaces.corridor` | `circulation_spaces.primary_circulation_spaces.corridor` | 1 — exact | Already canonical; pass-through |
| 2 | `Corridor` | `circulation_spaces.primary_circulation_spaces.corridor` | 2 — snake_case suffix | `"Corridor"` → `"corridor"` → last segment match |
| 3 | `Operating Theatre 1` | `healthcare_spaces.operating_theatre` | 2 — snake_case + suffix-number strip | `"operating_theatre_1"` → strip `_1` → `"operating_theatre"` → last segment match |
| 4 | `hallway` | `circulation_spaces.primary_circulation_spaces.corridor` | 3 — alias | `"hallway"` is `common_aliases[0]` for `corridor` |
| 5 | `OR` | `healthcare_spaces.operating_theatre` | 3 — alias | `"OR"` (normalized `"or"`) is a `common_aliases` entry for `operating_theatre` |
| 6 | `WC` | `facility_service_spaces.restroom` | 3 — alias | `"WC"` (normalized `"wc"`) is `common_aliases[1]` for `restroom` |
| 7 | `lecture theatre` | `education_and_training_spaces.lecture_and_classroom_spaces.lecture_hall_fixed_seats` | 3 — alias | `"lecture theatre"` (normalized `"lecture_theatre"`) is `common_aliases[0]` |
| 8 | `corridoor` (typo) | `circulation_spaces.primary_circulation_spaces.corridor` | 4 — Levenshtein ≤2 | 2 edits from `"corridor"` (extra `'o'`) |
| 9 | `data centre` | `environmentally_controlled_spaces.data_center` | 3 — alias | `"data centre"` (normalized `"data_centre"`) is `common_aliases[0]` for `data_center` |
| 10 | `unknown space type xyz` | `null` (no match) | — | No tier resolves; fall through to engineer override |

---

## When to fall back to engineer override

When fuzzy match returns `null` (no candidate found within Tier 4 thresholds and Tier
5 either absent or below the 0.85 cosine threshold), the orchestrator **MUST**:

1. Present a searchable dropdown of canonical_ids to the engineer.
2. Allow the engineer to map the unknown label to a canonical_id manually.
3. Or accept `Room.type: "unknown.userdefined"` as a graceful fallback when the
   engineer explicitly acknowledges the room type cannot be resolved.

The sentinel value `unknown.userdefined` is reserved for orchestrator use only — it
does not appear in any `room-types/*.json` file and is never a valid intermediate
value within the fuzzy-match pipeline.

---

## Citation

Algorithm pattern follows standard information-retrieval fuzzy-string-matching
practice. Levenshtein edit distance: Levenshtein, V.I. (1966). "Binary codes capable
of correcting deletions, insertions, and reversals". *Soviet Physics Doklady*, 10(8),
707–710. Embedding-similarity convention follows modern LLM cosine-similarity
practice (no single primary citation; tier is implementation-defined).
