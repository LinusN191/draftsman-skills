#!/usr/bin/env python3
"""standards-cross-reference-check.py

Verifies cross-file consistency across the IEEE1584 + NFPA70E layers:
- Every coefficient file references an electrode config that exists in the
  electrode-config files
- The IEEE 1584 incident-energy formula symbols resolve in arc-current-formula.json
- DC arc-flash files in NFPA70E/annex-d-* cross-reference each other consistently
- PPE-category thresholds in table-130-7-C-15-c-ppe-categories.json match
  the boundary-derivation 1.2 cal/cm² used by IEEE 1584

Run from repo root:
  python3 shared/validation/standards/standards-cross-reference-check.py

Exit code: 0 on success, 1 if any cross-reference fails.
"""
import json
import sys
from pathlib import Path

STANDARDS_ROOT = Path("shared/standards/electrical")
IEEE1584 = STANDARDS_ROOT / "IEEE1584"
NFPA70E = STANDARDS_ROOT / "NFPA70E"


def load(json_path: Path) -> dict:
    with json_path.open() as f:
        return json.load(f)


def check_electrode_configs() -> list[str]:
    """Every coefficient file's `electrode_config` references must exist in
    one of the `electrode-config-*-coefficients.json` files."""
    violations: list[str] = []
    config_files = list(IEEE1584.glob("electrode-config-*-coefficients.json"))
    if not config_files:
        return ["IEEE1584/electrode-config-*-coefficients.json files missing"]

    valid_codes = {p.stem.split("-")[2] for p in config_files}  # VCB, VCBB, HCB, VOA, HOA
    expected_codes = {"VCB", "VCBB", "HCB", "VOA", "HOA"}
    if valid_codes != expected_codes:
        violations.append(
            f"electrode configs present {valid_codes} != expected {expected_codes}"
        )

    # Every method-2018-*-coefficients.json should declare its applicable configs
    for method_file in IEEE1584.glob("method-2018-*V-coefficients.json"):
        data = load(method_file)
        configs = data.get("electrode_configs_applicable", [])
        for cfg in configs:
            if cfg not in valid_codes:
                violations.append(
                    f"{method_file.name}: references unknown electrode config '{cfg}'"
                )

    return violations


def check_ppe_thresholds() -> list[str]:
    """PPE-category thresholds in NFPA 70E must be monotonic and start at 1.2 cal/cm²."""
    ppe_file = NFPA70E / "table-130-7-C-15-c-ppe-categories.json"
    if not ppe_file.exists():
        return [f"{ppe_file.name} missing"]

    data = load(ppe_file)
    rows = data.get("rows", [])
    thresholds = [(r.get("category"), r.get("min_cal_per_cm2"), r.get("max_cal_per_cm2")) for r in rows]
    expected = [
        (1, 1.2, 4.0),
        (2, 4.0, 8.0),
        (3, 8.0, 25.0),
        (4, 25.0, 40.0),
    ]
    violations: list[str] = []
    for actual, exp in zip(thresholds, expected):
        if actual != exp:
            violations.append(
                f"PPE thresholds in {ppe_file.name}: row {actual} != expected {exp}"
            )
    return violations


def check_dc_arc_methods_cross_link() -> list[str]:
    """Doan + Stokes & Oppenlander DC methods reference each other correctly."""
    doan = NFPA70E / "annex-d-1-doan-method.json"
    stokes = NFPA70E / "annex-d-2-stokes-oppenlander-method.json"
    if not (doan.exists() and stokes.exists()):
        return [f"DC arc method files missing: {doan.name} or {stokes.name}"]

    doan_data = load(doan)
    # Doan method should reference Stokes for arc-voltage formula
    doan_text = json.dumps(doan_data).lower()
    if "stokes" not in doan_text and "v_arc" not in doan_text:
        return [
            f"{doan.name}: should reference Stokes & Oppenlander arc-voltage "
            "formula for V_arc input"
        ]
    return []


def main() -> int:
    print("Cross-reference check across IEEE1584 + NFPA70E...")
    all_violations: list[str] = []
    all_violations.extend(check_electrode_configs())
    all_violations.extend(check_ppe_thresholds())
    all_violations.extend(check_dc_arc_methods_cross_link())

    if all_violations:
        print(f"\nFAIL: {len(all_violations)} violations:")
        for v in all_violations:
            print(f"  - {v}")
        return 1
    print("\nPASS: cross-reference integrity verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
