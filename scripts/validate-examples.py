#!/usr/bin/env python3
"""Golden-example schema validation harness.

For each skill folder that has examples/*/output.json + schemas/*-ir.schema.json,
validate every example output against its skill's IR schema. Reports per-skill
+ per-example pass/fail. Returns exit 0 on full pass, exit 1 on any failure.

Recursively strips $ref nodes to {type: object} before validation — focuses on
inline schema-shape bugs rather than external-ref resolution (rationale, intent,
etc.). Ref resolution is the runtime's job; this harness catches author bugs in
the inline schema definitions.
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


def strip_refs(node):
    """Recursively replace any {$ref: ...} with {type: object}."""
    if isinstance(node, dict):
        if "$ref" in node:
            return {"type": "object"}
        return {k: strip_refs(v) for k, v in node.items()}
    if isinstance(node, list):
        return [strip_refs(v) for v in node]
    return node


def main(repo_root="."):
    os.chdir(repo_root)
    results = defaultdict(list)
    total_examples = 0
    total_failures = 0

    # Discover skill folders by scanning for schemas/*-ir.schema.json under disciplines
    skill_glob_patterns = [
        "electrical/*/schemas/*-ir.schema.json",
        "mechanical/*/schemas/*-ir.schema.json",
        "plumbing/*/schemas/*-ir.schema.json",
        "fire-protection/*/schemas/*-ir.schema.json",
    ]
    schemas_found = []
    for pat in skill_glob_patterns:
        schemas_found.extend(glob.glob(pat))

    skill_dirs = sorted(set(os.path.dirname(os.path.dirname(p)) for p in schemas_found))

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

        # Resolve a single level of $ref at the schema root if the local schema is just a pointer
        # to shared/schemas/electrical/<skill>-ir.schema.json
        if "$ref" in schema and len(schema.keys()) <= 5:
            ref = schema["$ref"]
            # Resolve relative to the schema_path's directory
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

    # Report
    print(f"=== Golden-example schema validation — {len(skill_dirs)} skills, {total_examples} examples ===\n")
    for skill in sorted(results.keys()):
        entries = results[skill]
        failures = [e for e in entries if e[0] != "PASS"]
        passes = [e for e in entries if e[0] == "PASS"]
        status = "PASS" if not failures else f"FAIL ({len(failures)} failures, {len(passes)} pass)"
        print(f"\n## {skill}: {status}")
        for kind, name, msg in entries:
            if kind == "PASS":
                print(f"  PASS {name}")
            else:
                print(f"  FAIL [{kind}] {name}")
                if msg:
                    print(f"       -> {msg}")

    print(f"\n=== TOTAL: {total_examples - total_failures}/{total_examples} pass ({total_failures} failures) ===")
    sys.exit(0 if total_failures == 0 else 1)


if __name__ == "__main__":
    main()
