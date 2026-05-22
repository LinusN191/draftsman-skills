#!/usr/bin/env python3
"""Golden-example schema validation harness — 3-pass.

Pass 1 — Example outputs: validate every examples/*/output.json against the
         parent skill's IR schema.
Pass 2 — Eval files: validate every evals/eval-*.yaml against
         shared/schemas/core/eval.schema.json.
Pass 3 — Inputs files: validate each skill's inputs.json against
         shared/schemas/core/inputs.schema.json.

Pass 1 recursively strips $ref nodes before validation — focuses on inline
schema-shape bugs rather than external-ref resolution (rationale, intent, etc.).
Passes 2 and 3 do NOT strip $refs because those schemas use internal $ref nodes
(#/definitions/Check, #/definitions/InputItem) that are load-bearing.

Returns exit 0 on full pass across all three passes, exit 1 on any failure.
"""
import json
import sys
import os
import glob
import copy
from collections import defaultdict

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Install: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def strip_refs(node):
    """Recursively replace any {$ref: ...} with {type: object}."""
    if isinstance(node, dict):
        if "$ref" in node:
            return {"type": "object"}
        return {k: strip_refs(v) for k, v in node.items()}
    if isinstance(node, list):
        return [strip_refs(v) for v in node]
    return node


def discover_skill_dirs() -> list:
    """Return sorted unique skill directory paths (e.g. 'electrical/lighting-layout')."""
    skill_glob_patterns = [
        "electrical/*/schemas/*-ir.schema.json",
        "mechanical/*/schemas/*-ir.schema.json",
        "plumbing/*/schemas/*-ir.schema.json",
        "fire-protection/*/schemas/*-ir.schema.json",
    ]
    schemas_found = []
    for pat in skill_glob_patterns:
        schemas_found.extend(glob.glob(pat))
    return sorted(set(os.path.dirname(os.path.dirname(p)) for p in schemas_found))


def validate_examples_pass(skill_dirs: list) -> tuple:
    """Validate every examples/*/output.json against the parent skill IR schema.

    Returns (total_examples, total_failures, report_lines).
    """
    results = defaultdict(list)
    total_examples = 0
    total_failures = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        schema_glob = glob.glob(f"{skill_dir}/schemas/*-ir.schema.json")
        if not schema_glob:
            continue
        schema_path = schema_glob[0]

        try:
            with open(schema_path) as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            results[skill_name].append(("SCHEMA-JSON-PARSE", schema_path, str(e)[:200]))
            total_failures += 1
            continue

        # Resolve a single level of $ref at the schema root if the local schema is just
        # a pointer to shared/schemas/electrical/<skill>-ir.schema.json
        if "$ref" in schema and len(schema.keys()) <= 5:
            ref = schema["$ref"]
            resolved_path = os.path.normpath(os.path.join(os.path.dirname(schema_path), ref))
            if os.path.exists(resolved_path):
                try:
                    with open(resolved_path) as f:
                        schema = json.load(f)
                except json.JSONDecodeError as e:
                    results[skill_name].append(("REF-SCHEMA-PARSE", resolved_path, str(e)[:200]))
                    total_failures += 1
                    continue

        # Strip all $refs from the schema we'll test against
        schema_test = strip_refs(schema)

        # Verify the schema itself is well-formed Draft-07
        try:
            jsonschema.Draft7Validator.check_schema(schema_test)
        except Exception as e:
            results[skill_name].append(("META-SCHEMA-INVALID", schema_path, str(e)[:200]))
            total_failures += 1

        examples = sorted(glob.glob(f"{skill_dir}/examples/*/output.json"))
        for ex_path in examples:
            total_examples += 1
            ex_name = os.path.basename(os.path.dirname(ex_path))
            try:
                with open(ex_path) as f:
                    out = json.load(f)
            except json.JSONDecodeError as e:
                results[skill_name].append(("JSON-PARSE", ex_name, str(e)[:200]))
                total_failures += 1
                continue
            try:
                jsonschema.validate(out, schema_test)
                results[skill_name].append(("PASS", ex_name, ""))
            except jsonschema.ValidationError as e:
                total_failures += 1
                path = ".".join(str(p) for p in list(e.absolute_path)[:6])
                results[skill_name].append(("FAIL", ex_name, f"{path}: {e.message[:160]}"))

    lines = []
    for skill in sorted(results.keys()):
        entries = results[skill]
        failures = [e for e in entries if e[0] != "PASS"]
        passes = [e for e in entries if e[0] == "PASS"]
        status = "PASS" if not failures else f"FAIL ({len(failures)} failures, {len(passes)} pass)"
        lines.append(f"\n## {skill}: {status}")
        for kind, name, msg in entries:
            if kind == "PASS":
                lines.append(f"  PASS {name}")
            else:
                lines.append(f"  FAIL [{kind}] {name}")
                if msg:
                    lines.append(f"       -> {msg}")

    return total_examples, total_failures, lines


def validate_evals_pass(skill_dirs: list, eval_schema: dict) -> tuple:
    """Validate every evals/eval-*.yaml against shared/schemas/core/eval.schema.json.

    Skips runner-config.yaml and any path under _archive/.
    Returns (total_evals, total_failures, report_lines).
    """
    results = defaultdict(list)
    total_evals = 0
    total_failures = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        evals_dir = f"{skill_dir}/evals"
        if not os.path.isdir(evals_dir):
            continue

        eval_files = sorted(glob.glob(f"{evals_dir}/eval-*.yaml"))

        if not eval_files:
            continue

        for eval_path in eval_files:
            total_evals += 1
            eval_basename = os.path.basename(eval_path)

            try:
                with open(eval_path) as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                results[skill_name].append(("YAML-PARSE", eval_basename, str(e)[:200]))
                total_failures += 1
                continue

            try:
                jsonschema.validate(data, eval_schema)
                results[skill_name].append(("PASS", eval_basename, ""))
            except jsonschema.ValidationError as e:
                total_failures += 1
                path = ".".join(str(p) for p in list(e.absolute_path)[:6])
                results[skill_name].append(("SCHEMA", eval_basename, f"{path}: {e.message[:160]}"))

    lines = []
    for skill in sorted(results.keys()):
        entries = results[skill]
        failures = [e for e in entries if e[0] != "PASS"]
        passes = [e for e in entries if e[0] == "PASS"]
        status = "PASS" if not failures else f"FAIL ({len(failures)} failures, {len(passes)} pass)"
        lines.append(f"\n## {skill}: {status}")
        for kind, name, msg in entries:
            if kind == "PASS":
                lines.append(f"  PASS {name}")
            else:
                lines.append(f"  FAIL [SCHEMA] {name}")
                if msg:
                    lines.append(f"       -> {msg}")

    return total_evals, total_failures, lines


def validate_inputs_pass(skill_dirs: list, inputs_schema: dict) -> tuple:
    """Validate each skill's inputs.json against shared/schemas/core/inputs.schema.json.

    Returns (total_inputs, total_failures, report_lines).
    """
    results = defaultdict(list)
    total_inputs = 0
    total_failures = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        inputs_path = f"{skill_dir}/inputs.json"

        if not os.path.exists(inputs_path):
            continue

        total_inputs += 1

        try:
            with open(inputs_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            results[skill_name].append(("JSON-PARSE", "inputs.json", str(e)[:200]))
            total_failures += 1
            continue

        try:
            jsonschema.validate(data, inputs_schema)
            results[skill_name].append(("PASS", "inputs.json", ""))
        except jsonschema.ValidationError as e:
            total_failures += 1
            path = ".".join(str(p) for p in list(e.absolute_path)[:6])
            results[skill_name].append(("SCHEMA", "inputs.json", f"{path}: {e.message[:160]}"))

    lines = []
    for skill in sorted(results.keys()):
        entries = results[skill]
        failures = [e for e in entries if e[0] != "PASS"]
        passes = [e for e in entries if e[0] == "PASS"]
        status = "PASS" if not failures else f"FAIL ({len(failures)} failures, {len(passes)} pass)"
        lines.append(f"\n## {skill}: {status}")
        for kind, name, msg in entries:
            if kind == "PASS":
                lines.append(f"  PASS {name}")
            else:
                lines.append(f"  FAIL [SCHEMA] {name}")
                if msg:
                    lines.append(f"       -> {msg}")

    return total_inputs, total_failures, lines


def main(repo_root="."):
    os.chdir(repo_root)
    skill_dirs = discover_skill_dirs()

    try:
        with open("shared/schemas/core/eval.schema.json") as f:
            eval_schema = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Could not load eval.schema.json: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        with open("shared/schemas/core/inputs.schema.json") as f:
            inputs_schema = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Could not load inputs.schema.json: {e}", file=sys.stderr)
        sys.exit(2)

    ex_tot, ex_fail, ex_lines = validate_examples_pass(skill_dirs)
    ev_tot, ev_fail, ev_lines = validate_evals_pass(skill_dirs, eval_schema)
    in_tot, in_fail, in_lines = validate_inputs_pass(skill_dirs, inputs_schema)

    print("=== Pass 1 — Example outputs ===\n")
    for line in ex_lines:
        print(line)
    print(f"\nSubtotal: {ex_tot - ex_fail}/{ex_tot} pass ({ex_fail} failures)\n")

    print("=== Pass 2 — Eval files ===\n")
    for line in ev_lines:
        print(line)
    print(f"\nSubtotal: {ev_tot - ev_fail}/{ev_tot} pass ({ev_fail} failures)\n")

    print("=== Pass 3 — Inputs files ===\n")
    for line in in_lines:
        print(line)
    print(f"\nSubtotal: {in_tot - in_fail}/{in_tot} pass ({in_fail} failures)\n")

    total = ex_tot + ev_tot + in_tot
    total_fail = ex_fail + ev_fail + in_fail
    print(f"=== AGGREGATE: {total - total_fail}/{total} pass ({total_fail} failures) ===")
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
