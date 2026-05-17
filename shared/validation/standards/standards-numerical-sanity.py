#!/usr/bin/env python3
"""standards-numerical-sanity.py

Verifies numerical content across IEEE1584 + NFPA70E standards files:
- Every numeric coefficient is finite (no NaN, null, infinity)
- Every applicable_range is monotonic (min < max)
- Every worked_example's expected_output values are within plausible bounds
  for arc-flash analysis (incident energy 0.01 - 1000 cal/cm²; AFB 0.01 - 100 m)

Run from repo root:
  python3 shared/validation/standards/standards-numerical-sanity.py

Exit code: 0 on success, 1 if any violation.
"""
import json
import math
import sys
from pathlib import Path

STANDARDS_ROOT = Path("shared/standards/electrical")

# Plausible bounds for arc-flash quantities
BOUNDS = {
    "incident_energy_cal_per_cm2": (0.01, 1000.0),
    "afb_mm":                       (1.0, 100_000.0),  # 1mm – 100m
    "arc_flash_boundary_mm":        (1.0, 100_000.0),
    "iarc_a":                       (10.0, 200_000.0),  # 10A – 200kA
    "arcing_current_a":             (10.0, 200_000.0),
    "ibf_a":                        (10.0, 200_000.0),
    "bolted_fault_current_a":       (10.0, 200_000.0),
}


def walk_numerics(obj, path: str = ""):
    """Yield (path, value) for every numeric value in nested dict/list."""
    if isinstance(obj, (int, float)):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_numerics(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_numerics(v, f"{path}[{i}]")


def check_finite(json_path: Path) -> list[str]:
    """Every numeric value is finite."""
    violations: list[str] = []
    try:
        data = json.load(json_path.open())
    except json.JSONDecodeError as e:
        return [f"{json_path}: JSON parse error: {e}"]

    for p, v in walk_numerics(data):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            violations.append(f"{json_path}: non-finite at {p}: {v}")
    return violations


def check_applicable_range(json_path: Path) -> list[str]:
    """applicable_range dicts must have monotonic min/max pairs."""
    violations: list[str] = []
    data = json.load(json_path.open())
    ar = data.get("applicable_range")
    if not isinstance(ar, dict):
        return violations

    # Look for {*_min, *_max} pairs
    for key in ar:
        if key.endswith("_min"):
            base = key[: -len("_min")]
            max_key = f"{base}_max"
            if max_key in ar:
                if ar[key] >= ar[max_key]:
                    violations.append(
                        f"{json_path}: applicable_range {key}={ar[key]} >= {max_key}={ar[max_key]}"
                    )
    return violations


def check_worked_examples(json_path: Path) -> list[str]:
    """Every worked_example expected_output value is within plausible bounds."""
    violations: list[str] = []
    data = json.load(json_path.open())
    examples = data.get("worked_examples", [])
    for i, ex in enumerate(examples):
        if not isinstance(ex, dict):
            continue
        eo = ex.get("expected_output", {})
        for key, value in eo.items():
            if key in BOUNDS and isinstance(value, (int, float)):
                lo, hi = BOUNDS[key]
                if not (lo <= value <= hi):
                    violations.append(
                        f"{json_path}: worked_examples[{i}].expected_output.{key}={value} "
                        f"out of plausible range [{lo}, {hi}]"
                    )
    return violations


def main() -> int:
    json_files = sorted(STANDARDS_ROOT.glob("*/*.json"))
    print(f"Numerical sanity check on {len(json_files)} files...")

    all_violations: list[str] = []
    for f in json_files:
        all_violations.extend(check_finite(f))
        all_violations.extend(check_applicable_range(f))
        all_violations.extend(check_worked_examples(f))

    if all_violations:
        print(f"\nFAIL: {len(all_violations)} violations:")
        for v in all_violations:
            print(f"  - {v}")
        return 1
    print("\nPASS: all numerical content is sane")
    return 0


if __name__ == "__main__":
    sys.exit(main())
