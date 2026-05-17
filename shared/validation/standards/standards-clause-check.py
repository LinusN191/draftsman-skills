#!/usr/bin/env python3
"""standards-clause-check.py

Verifies every .json file under shared/standards/electrical/<layer>/ carries a
non-empty `clause_ref` field in the expected format:
  <STANDARD_ID> <YEAR>:<SECTION/TABLE>

Run from repo root:
  python3 shared/validation/standards/standards-clause-check.py

Exit code: 0 on success, 1 if any violations found.
"""
import json
import re
import sys
from pathlib import Path

STANDARDS_ROOT = Path("shared/standards/electrical")
CLAUSE_REF_PATTERN = re.compile(
    r"^[A-Z][A-Z0-9-]+\s+\d{4}:\S+",
    re.IGNORECASE,
)

# Layers that follow the clause_ref convention.
# Phase A (2026-05): IEEE1584, NFPA70E
# Retrofit (2026-05): BS7671, IEC60364, IEC60617, IEC60909, IEC61439, NFPA70
LAYERS_REQUIRING_CLAUSE_REF = {
    "BS7671",
    "IEC60364",
    "IEC60617",
    "IEC60909",
    "IEC61439",
    "NFPA70",
    "IEEE1584",
    "NFPA70E",
}


def check_file(json_path: Path) -> list[str]:
    """Return list of violation messages for this file (empty list = pass)."""
    violations = []
    try:
        with json_path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{json_path}: JSON parse error: {e}"]

    if "clause_ref" not in data:
        violations.append(f"{json_path}: missing 'clause_ref' field")
        return violations

    clause_ref = data["clause_ref"]
    if not isinstance(clause_ref, str) or not clause_ref.strip():
        violations.append(f"{json_path}: 'clause_ref' is empty or not a string")
        return violations

    if not CLAUSE_REF_PATTERN.match(clause_ref):
        violations.append(
            f"{json_path}: 'clause_ref' = {clause_ref!r} does not match "
            f"pattern '<STANDARD_ID> <YEAR>:<SECTION>'"
        )

    return violations


def main() -> int:
    all_violations: list[str] = []
    json_files = sorted(STANDARDS_ROOT.glob("*/*.json"))
    # Exclude meta.json files — they have their own schema and don't carry clause_ref.
    json_files = [p for p in json_files if p.name != "meta.json"]
    # Only check layers that follow the clause_ref convention.
    json_files = [p for p in json_files if p.parent.name in LAYERS_REQUIRING_CLAUSE_REF]

    print(f"Checking {len(json_files)} files for clause_ref integrity...")

    for json_path in json_files:
        violations = check_file(json_path)
        all_violations.extend(violations)

    if all_violations:
        print(f"\nFAIL: {len(all_violations)} violations:")
        for v in all_violations:
            print(f"  - {v}")
        return 1

    print(f"\nPASS: all {len(json_files)} files carry valid clause_ref")
    return 0


if __name__ == "__main__":
    sys.exit(main())
