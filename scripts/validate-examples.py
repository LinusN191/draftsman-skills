#!/usr/bin/env python3
"""Golden-example schema validation harness — 7-pass + 5 lint sub-passes (Sprint F.5 final state).

Pass 1 — Example outputs: validate every examples/*/output.json against the
         parent skill's IR schema.
Pass 2 — Eval files: validate every evals/eval-*.yaml against
         shared/schemas/core/eval.schema.json.
Pass 3 — Inputs files: validate each skill's inputs.json against
         shared/schemas/core/inputs.schema.json.
Pass 4 — Intent emissions: validate every examples/*/intent-out.json against
         the producing skill's intent schema (added Sprint D round-3).
Pass 5 — Manifests: validate each skill's skill.manifest.json against
         shared/schemas/core/skill-manifest.schema.json (added Sprint F.5).
Pass 6 — Room-types entries across 3 catalogues (room-types-schema.json):
         + OmniClass T13 (shared/standards/spaces/room-types/*.json) — Sprint X
         + Uniclass 2015 SL (shared/standards/spaces/room-types-uniclass-sl/*.json) — Sprint Z
         + OmniClass T11 (shared/standards/spaces/building-types-t11/*.json) — Sprint Z
Pass 7 — ASHRAE source files (parse + structure) [added Sprint X.E.1]
Pass 8 — ISO 16739 IFC subset (parse + structure) [added Sprint X.E.1]

Lint sub-passes (Sprint F.5 additions):

  Lint 1 — Manifest field-name typos: flag unknown manifest top-level fields
            with Levenshtein-nearest suggestion. Underscore-prefixed fields
            (e.g. _v2_breaking_change_note) are permitted documentation fields.
            INFORMATIONAL — not gate-failing.

  Lint 2 — grounded_source two-tier validation: enumerate every grounded_source
            binding in inputs.json items[]. Tier 1 (canonical 14 room.*/project.*
            bindings) = silent PASS. Tier 2 (project.<custom>) = INFORMATIONAL.
            Invalid bindings (not canonical and not matching project.<custom>) = FAIL.

  Lint 3 — Dropped-item orphans in examples: scan examples/*/input.json files
            for top-level fields that were dropped from inputs.json (stale
            references). INFORMATIONAL — not gate-failing.

  Lint 4 — Cascade byte-equality SHA-256: for every example with
            consumed_intents.<X>.source_path, hash the producer's intent-out.json
            payload and the consumer's inlined payload; SHA-256 mismatch = FAIL
            (cascade contract drift).

  Lint 5 — Canonical room.type membership across all 3 catalogues
            [added Sprint X.E.1; extended Sprint Z.E.1].

Pass 1 recursively strips $ref nodes before validation — focuses on inline
schema-shape bugs rather than external-ref resolution (rationale, intent, etc.).
Passes 2 and 3 do NOT strip $refs because those schemas use internal $ref nodes
(#/definitions/Check, #/definitions/InputItem) that are load-bearing.

Returns exit 0 on full pass + zero gate-failing lint findings; exit 1 on any failure.
"""
import hashlib
import json
import re
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


def validate_intents_pass(skill_dirs: list) -> tuple:
    """Pass 4 — Intent emissions: validate every examples/*/intent-out.json against
    the producing skill's intent schema (electrical/<skill>/schemas/*-intent.schema.json).

    Added 2026-05-25 (Sprint D round-3) to close the structural-hole Reviewer 1
    flagged: prior gate counted intent-out.json files toward example count via
    Pass 1's output validation but never validated them against the intent
    schema — a downstream consumer of a non-conformant intent would break at
    runtime, invisible to the gate. Same strip_refs convention as Pass 1
    (external $refs to shared/schemas/core/* replaced with {type: object}).

    Returns (total_intents, total_failures, report_lines).
    """
    results = defaultdict(list)
    total_intents = 0
    total_failures = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        intent_schemas = glob.glob(f"{skill_dir}/schemas/*-intent.schema.json")
        if not intent_schemas:
            continue  # skill doesn't produce an intent; skip
        # Pick the canonical schema (usually one per skill; fallback to first)
        schema_path = intent_schemas[0]

        try:
            with open(schema_path) as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            results[skill_name].append(("INTENT-SCHEMA-PARSE", schema_path, str(e)[:200]))
            total_failures += 1
            continue

        # Handle shim-ref pattern (same as Pass 1)
        if "$ref" in schema and len(schema.keys()) <= 5:
            ref = schema["$ref"]
            resolved_path = os.path.normpath(os.path.join(os.path.dirname(schema_path), ref))
            if os.path.exists(resolved_path):
                with open(resolved_path) as f:
                    schema = json.load(f)

        schema_test = strip_refs(schema)

        try:
            jsonschema.Draft7Validator.check_schema(schema_test)
        except Exception as e:
            results[skill_name].append(("INTENT-META-SCHEMA-INVALID", schema_path, str(e)[:200]))
            total_failures += 1
            continue

        intents = sorted(glob.glob(f"{skill_dir}/examples/*/intent-out.json"))
        for ip in intents:
            total_intents += 1
            try:
                with open(ip) as f:
                    instance = json.load(f)
            except json.JSONDecodeError as e:
                results[skill_name].append(("FAIL", ip, f"JSON parse: {str(e)[:200]}"))
                total_failures += 1
                continue
            validator = jsonschema.Draft7Validator(schema_test)
            errs = sorted(validator.iter_errors(instance), key=lambda e: e.absolute_path)
            if errs:
                e = errs[0]
                path = ".".join(str(p) for p in e.absolute_path) or "(root)"
                results[skill_name].append(("FAIL", os.path.basename(os.path.dirname(ip)), f"{path}: {e.message[:200]}"))
                total_failures += 1
            else:
                results[skill_name].append(("PASS", os.path.basename(os.path.dirname(ip)), ""))

    lines = []
    for skill_name in sorted(results):
        items = results[skill_name]
        pass_n = sum(1 for r in items if r[0] == "PASS")
        fail_n = len(items) - pass_n
        status = "PASS" if fail_n == 0 else f"FAIL ({fail_n} failures, {pass_n} pass)"
        lines.append(f"## {skill_name}: {status}")
        for status_code, name, detail in items:
            if status_code == "PASS":
                lines.append(f"  PASS {name}")
            else:
                lines.append(f"  FAIL [{status_code}] {name}")
                if detail:
                    lines.append(f"       -> {detail}")
        lines.append("")

    return total_intents, total_failures, lines


def validate_room_types_pass() -> tuple:
    """Pass 6 — Room-types schema validation (3 catalogues).

    Validate every entry across all 3 room-type catalogues against
    shared/standards/spaces/room-types-schema.json:
      - OmniClass T13: shared/standards/spaces/room-types/*.json
      - Uniclass 2015 SL: shared/standards/spaces/room-types-uniclass-sl/*.json
      - OmniClass T11: shared/standards/spaces/building-types-t11/*.json

    Returns (total_entries, total_failures, report_lines).
    (Originally Pass 5; renumbered to Pass 6 when Sprint F.5 inserted manifest
    validation as the new Pass 5.)
    """
    results = defaultdict(list)
    total_entries = 0
    total_failures = 0

    schema_path = "shared/standards/spaces/room-types-schema.json"
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        return (0, 0, [f"\n## Pass 6: SKIP — {schema_path} not found"])

    for f_path in sorted(
        glob.glob("shared/standards/spaces/room-types/*.json")
        + glob.glob("shared/standards/spaces/room-types-uniclass-sl/*.json")
        + glob.glob("shared/standards/spaces/building-types-t11/*.json")
    ):
        f_name = os.path.basename(f_path)
        try:
            with open(f_path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results[f_name].append(("JSON-PARSE", f_path, str(e)[:200]))
            total_failures += 1
            continue
        for i, entry in enumerate(d.get("entries", [])):
            total_entries += 1
            try:
                jsonschema.validate(entry, schema)
                # Silent PASS at entry level; per-file PASS reported below
            except jsonschema.ValidationError as e:
                total_failures += 1
                cid = entry.get("canonical_id", f"entry[{i}]")
                results[f_name].append(("FAIL", cid, e.message[:160]))

    lines = ["\n## Pass 6: Room-types schema validation"]
    for f_name in sorted(results.keys()):
        failures = results[f_name]
        if not failures:
            lines.append(f"  PASS {f_name}")
        else:
            for kind, name, msg in failures:
                lines.append(f"  {kind} {f_name}.{name}: {msg}")
    if not results:
        lines.append("  PASS — all room-types entries validate")
    return (total_entries, total_failures, lines)


def validate_ashrae_pass() -> tuple:
    """Pass 7 — ASHRAE source files parse + structure check.

    Validate that shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json and
    shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json parse, have _source +
    _edition + entries fields populated.

    Returns (total_files, total_failures, report_lines).
    (Originally Pass 6; renumbered to Pass 7 when Sprint F.5 inserted manifest
    validation as the new Pass 5.)
    """
    results = []
    total_files = 0
    total_failures = 0

    checks = [
        ("ASHRAE-90-1", "shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json"),
        ("ASHRAE-62-1", "shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json"),
    ]
    for name, path in checks:
        if not os.path.exists(path):
            results.append(("SKIP", name, f"file not found: {path}"))
            continue
        total_files += 1
        try:
            with open(path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results.append(("JSON-PARSE", name, str(e)[:200]))
            total_failures += 1
            continue
        for required in ["_source", "_edition", "entries"]:
            if required not in d:
                results.append(("FAIL", name, f"missing required key: {required}"))
                total_failures += 1
                break
        else:
            results.append(("PASS", name, f"{len(d['entries'])} entries"))

    lines = ["\n## Pass 7: ASHRAE source files"]
    for kind, name, msg in results:
        lines.append(f"  {kind} {name}: {msg}")
    return (total_files, total_failures, lines)


def validate_ifc_pass() -> tuple:
    """Pass 8 — ISO 16739 IFC subset parse check.

    Validate that shared/standards/bim/ISO16739/{space-types,classification,placement}.json
    parse and have _source + _source_url fields.

    Returns (total_files, total_failures, report_lines).
    (Originally Pass 7; renumbered to Pass 8 when Sprint F.5 inserted manifest
    validation as the new Pass 5.)
    """
    results = []
    total_files = 0
    total_failures = 0

    files = [
        "shared/standards/bim/ISO16739/space-types.json",
        "shared/standards/bim/ISO16739/classification.json",
        "shared/standards/bim/ISO16739/placement.json",
    ]
    for path in files:
        name = os.path.basename(path)
        if not os.path.exists(path):
            results.append(("SKIP", name, f"file not found: {path}"))
            continue
        total_files += 1
        try:
            with open(path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results.append(("JSON-PARSE", name, str(e)[:200]))
            total_failures += 1
            continue
        for required in ["_source", "_source_url"]:
            if required not in d:
                results.append(("FAIL", name, f"missing required key: {required}"))
                total_failures += 1
                break
        else:
            results.append(("PASS", name, "valid"))

    lines = ["\n## Pass 8: ISO 16739 IFC subset"]
    for kind, name, msg in results:
        lines.append(f"  {kind} {name}: {msg}")
    return (total_files, total_failures, lines)


def lint_canonical_room_type_membership(skill_dirs: list) -> tuple:
    """Lint sub-pass 5 — Canonical room.type membership check.

    Scan every examples/*/{output,intent-out,input}.json file across all skills for
    room.type values. Check each against the union of canonical_id values across
    shared/standards/spaces/room-types/*.json. Report PASS / FAIL / SUGGEST.

    Returns (total_fail_count, report_lines).
    """
    # Load canonical IDs
    canonical_ids = set()
    aliases_to_canonical = {}
    for f in sorted(
        glob.glob("shared/standards/spaces/room-types/*.json")
        + glob.glob("shared/standards/spaces/room-types-uniclass-sl/*.json")
        + glob.glob("shared/standards/spaces/building-types-t11/*.json")
    ):
        try:
            with open(f) as fh:
                d = json.load(fh)
            for entry in d.get("entries", []):
                canonical_ids.add(entry["canonical_id"])
                for alias in entry.get("common_aliases", []):
                    aliases_to_canonical[alias.lower().strip()] = entry["canonical_id"]
        except (json.JSONDecodeError, KeyError):
            continue

    if not canonical_ids:
        return (0, ["\n## Lint 5: Canonical room.type membership", "  SKIP — no room-types catalogue found"])

    # Scan all skill example files
    total_checked = 0
    total_fail = 0
    total_suggest = 0
    findings = []
    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        for ex_glob in [f"{skill_dir}/examples/*/output.json",
                        f"{skill_dir}/examples/*/intent-out.json",
                        f"{skill_dir}/examples/*/input.json"]:
            for ex_path in sorted(glob.glob(ex_glob)):
                ex_name = os.path.basename(os.path.dirname(ex_path))
                file_kind = os.path.basename(ex_path)
                try:
                    with open(ex_path) as f:
                        d = json.load(f)
                except json.JSONDecodeError:
                    continue
                # Find room.type values only — the NEW canonical field (room.type).
                # The legacy field (room.room_type) predates the Sprint X catalogue and
                # is NOT checked here; Lint 5 fires only when the new room.type key is
                # populated, so existing examples that still carry room_type will SKIP.
                room_type_values = []
                if isinstance(d.get("room"), dict) and "type" in d["room"]:
                    room_type_values.append(("room.type", d["room"]["type"]))
                for rt_path, rt_val in room_type_values:
                    if not isinstance(rt_val, str):
                        continue
                    total_checked += 1
                    if rt_val in canonical_ids:
                        pass  # Silent PASS
                    elif rt_val.lower().strip() in aliases_to_canonical:
                        canonical = aliases_to_canonical[rt_val.lower().strip()]
                        total_suggest += 1
                        findings.append(
                            f"  SUGGEST {skill_name}.{ex_name}.{file_kind} "
                            f"({rt_path}='{rt_val}'): not canonical; matches alias of '{canonical}'"
                        )
                    else:
                        total_fail += 1
                        findings.append(
                            f"  FAIL {skill_name}.{ex_name}.{file_kind} "
                            f"({rt_path}='{rt_val}'): not in canonical catalogue + no alias match"
                        )

    lines = ["\n## Lint 5: Canonical room.type membership"]
    if total_checked == 0:
        lines.append("  SKIP — no room.type values found in example files")
    elif total_fail == 0 and total_suggest == 0:
        lines.append(f"  PASS — {total_checked} room.type values all canonical")
    else:
        lines.append(
            f"  Checked: {total_checked}; PASS: {total_checked - total_fail - total_suggest}; "
            f"SUGGEST: {total_suggest}; FAIL: {total_fail}"
        )
        lines.extend(findings[:20])  # Cap output at 20 findings
        if len(findings) > 20:
            lines.append(f"  ... and {len(findings) - 20} more findings (output truncated)")
    return (total_fail, lines)


# ---------------------------------------------------------------------------
# Pass 5 (Sprint F.5) — Manifest metaschema validation
# ---------------------------------------------------------------------------

def _discover_all_manifest_dirs() -> list:
    """Return sorted manifest paths across all disciplines."""
    patterns = [
        "electrical/*/skill.manifest.json",
        "mechanical/*/skill.manifest.json",
        "plumbing/*/skill.manifest.json",
        "fire-protection/*/skill.manifest.json",
        "coordination/*/skill.manifest.json",
        "documents/*/skill.manifest.json",
        "compliance/*/skill.manifest.json",
        "commissioning/*/skill.manifest.json",
    ]
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(pat))
    return sorted(paths)


def validate_manifests_pass() -> tuple:
    """Pass 5 — Manifest metaschema validation.

    Validate every skill.manifest.json across all disciplines against
    shared/schemas/core/skill-manifest.schema.json (created Sprint F.2).

    Returns (total_manifests, total_failures, report_lines).
    """
    schema_path = "shared/schemas/core/skill-manifest.schema.json"
    try:
        with open(schema_path) as f:
            manifest_schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return (0, 0, [f"\n## Pass 5 (F.5): Manifest validation — SKIP: {e}"])

    manifest_paths = _discover_all_manifest_dirs()
    total_manifests = 0
    total_failures = 0
    results = []

    for manifest_path in manifest_paths:
        skill_label = "/".join(manifest_path.split("/")[:2])
        total_manifests += 1
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            total_failures += 1
            results.append(("JSON-PARSE", skill_label, str(e)[:200]))
            continue
        try:
            jsonschema.validate(manifest, manifest_schema)
            results.append(("PASS", skill_label, ""))
        except jsonschema.ValidationError as e:
            total_failures += 1
            path_str = ".".join(str(p) for p in list(e.absolute_path)[:6]) or "(root)"
            results.append(("FAIL", skill_label, f"{path_str}: {e.message[:160]}"))

    lines = ["\n## Pass 5 (F.5): Manifest metaschema validation"]
    for kind, label, msg in results:
        if kind == "PASS":
            lines.append(f"  PASS {label}")
        else:
            lines.append(f"  FAIL [{kind}] {label}")
            if msg:
                lines.append(f"       -> {msg}")

    return (total_manifests, total_failures, lines)


# ---------------------------------------------------------------------------
# Lint sub-passes 1-4 (Sprint F.5)
# ---------------------------------------------------------------------------

# Canonical manifest top-level field names (from skill-manifest.schema.json properties)
KNOWN_MANIFEST_FIELDS: frozenset = frozenset([
    "skill", "version", "discipline", "subdiscipline", "chat_type",
    "description", "status", "scope", "placement_convention", "licence",
    "last_updated", "changelog", "inputs_path", "inputs", "outputs",
    "output_schema", "produces_intents", "produces_intent_schema",
    "produces_intent_schemas", "consumes_intents", "standards", "ontology",
    "symbols", "calculations", "prompts", "evals", "examples", "validation",
    "rules", "constraints", "templates", "docs", "compatible_runtimes",
    "$schema",
])


def _suggest_field(unknown: str, known: frozenset) -> str:
    """Return the closest known field name if Levenshtein edit-distance ≤ 2."""
    def edit_distance(a: str, b: str) -> int:
        previous = list(range(len(a) + 1))
        for i, cb in enumerate(b):
            current = [i + 1]
            for j, ca in enumerate(a):
                insertions = previous[j + 1] + 1
                deletions = current[j] + 1
                substitutions = previous[j] + (ca != cb)
                current.append(min(insertions, deletions, substitutions))
            previous = current
        return previous[-1]

    candidates = sorted(known, key=lambda k: edit_distance(unknown, k))
    if candidates and edit_distance(unknown, candidates[0]) <= 2:
        return candidates[0]
    return ""


def lint_manifest_fields() -> tuple:
    """Lint 1 — Flag unknown manifest top-level fields with Levenshtein suggestion.

    Underscore-prefixed fields (e.g. _v2_breaking_change_note, _ontology_note)
    are permitted internal documentation fields and are silently skipped.

    Returns (total_unknowns, report_lines). INFORMATIONAL — not gate-failing.
    """
    manifest_paths = _discover_all_manifest_dirs()
    findings = []
    total_unknowns = 0

    for manifest_path in manifest_paths:
        skill_label = "/".join(manifest_path.split("/")[:2])
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            continue
        for k in manifest.keys():
            if k.startswith("_"):
                continue  # permitted internal documentation field
            if k not in KNOWN_MANIFEST_FIELDS:
                total_unknowns += 1
                suggestion = _suggest_field(k, KNOWN_MANIFEST_FIELDS)
                hint = f" (did you mean: '{suggestion}'?)" if suggestion else ""
                findings.append(f"  LINT {skill_label}: unknown field '{k}'{hint}")

    lines = ["\n## Lint 1 (F.5): Manifest field-name typos"]
    if total_unknowns == 0:
        lines.append("  PASS — no unknown fields detected across all manifests")
    else:
        lines.extend(findings)
        lines.append(f"  ({total_unknowns} unknown field(s) — informational only, not gate-failing)")
    return (total_unknowns, lines)


# Tier 1: closed enum for canonical grounded_source bindings
CANONICAL_GROUNDED_SOURCES: frozenset = frozenset([
    "room.type", "room.area_m2", "room.bbox.length", "room.bbox.width",
    "room.centroid.x", "room.centroid.y", "room.mounting_height", "room.polygon",
    "project.building_type", "project.code_basis", "project.jurisdiction",
    "project.units", "project.ceiling_height_mm", "project.project_id",
])

# Tier 2: pattern for project.<custom> bindings
_PROJECT_CUSTOM_RE = re.compile(r"^project\.[a-z_]+$")


def lint_grounded_sources(skill_dirs: list) -> tuple:
    """Lint 2 — grounded_source two-tier validation.

    Tier 1 (canonical 14 bindings) = silent PASS.
    Tier 2 (project.<custom>) = INFORMATIONAL — orchestrator must confirm it
      can provide the binding.
    Invalid bindings (not canonical and not matching project.<custom>) = FAIL.

    Returns (total_failures, report_lines).
    """
    findings = []
    total_custom = 0
    total_failures = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        inputs_path = f"{skill_dir}/inputs.json"
        if not os.path.exists(inputs_path):
            continue
        try:
            with open(inputs_path) as f:
                inputs = json.load(f)
        except json.JSONDecodeError:
            continue

        # Flatten items across all supported inputs.json shapes
        items: list = list(inputs.get("items") or inputs.get("inputs") or [])
        for grp in inputs.get("input_groups", []):
            items.extend(grp.get("items", []))

        for item in items:
            if not isinstance(item, dict):
                continue
            gs = item.get("grounded_source")
            if not gs:
                continue
            if gs in CANONICAL_GROUNDED_SOURCES:
                continue  # silent PASS
            if _PROJECT_CUSTOM_RE.match(gs):
                total_custom += 1
                findings.append(
                    f"  LINT {skill_name}.{item.get('id', '?')}: "
                    f"custom binding '{gs}' (confirm orchestrator can provide)"
                )
            else:
                total_failures += 1
                findings.append(
                    f"  FAIL {skill_name}.{item.get('id', '?')}: "
                    f"invalid grounded_source '{gs}'"
                )

    lines = ["\n## Lint 2 (F.5): grounded_source two-tier validation"]
    if total_custom == 0 and total_failures == 0:
        lines.append("  PASS — all grounded_source bindings are canonical (or none present)")
    else:
        lines.extend(findings)
        if total_custom:
            lines.append(f"  ({total_custom} custom project.* binding(s) — informational only)")
        if total_failures:
            lines.append(f"  ({total_failures} invalid binding(s) — gate-failing)")
    return (total_failures, lines)


def lint_dropped_items_orphaned(skill_dirs: list) -> tuple:
    """Lint 3 — Dropped-item orphans in examples.

    For each skill, compare top-level fields in examples/*/input.json against
    the canonical item IDs in inputs.json. Fields that look like dropped items
    (match a known dropped-field heuristic) but are absent from the current
    inputs.json are flagged as stale references.

    Returns (0, report_lines). INFORMATIONAL — not gate-failing.
    """
    # Heuristic: these bare top-level names were common before the inputs.json
    # schema migration and are the most likely dropped-item orphans.
    LEGACY_TOP_LEVEL_FIELDS = frozenset([
        "room_type", "room_length_mm", "room_width_mm", "jurisdiction",
        "building_type", "project_id", "ceiling_height_mm", "mounting_height_mm",
        "room_area_m2",
    ])

    findings = []
    total_orphans = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        inputs_path = f"{skill_dir}/inputs.json"
        if not os.path.exists(inputs_path):
            continue
        try:
            with open(inputs_path) as f:
                inputs = json.load(f)
        except json.JSONDecodeError:
            continue

        # Build canonical ID set (all shapes)
        canonical_ids: set = set()
        for item in list(inputs.get("items") or inputs.get("inputs") or []):
            if isinstance(item, dict) and "id" in item:
                canonical_ids.add(item["id"])
        for grp in inputs.get("input_groups", []):
            for item in grp.get("items", []):
                if isinstance(item, dict) and "id" in item:
                    canonical_ids.add(item["id"])

        if not canonical_ids:
            continue  # skip skills without canonical items (stubs)

        for example_input in sorted(glob.glob(f"{skill_dir}/examples/*/input.json")):
            example_name = os.path.basename(os.path.dirname(example_input))
            try:
                with open(example_input) as f:
                    ex = json.load(f)
            except json.JSONDecodeError:
                continue

            for k in ex.keys():
                if k.startswith("_"):
                    continue
                if k in LEGACY_TOP_LEVEL_FIELDS and k not in canonical_ids:
                    total_orphans += 1
                    findings.append(
                        f"  LINT {skill_name}.examples.{example_name}: "
                        f"stale field '{k}' (dropped from inputs.json)"
                    )

    lines = ["\n## Lint 3 (F.5): Dropped-item orphans in examples"]
    if total_orphans == 0:
        lines.append("  PASS — no orphaned dropped fields detected")
    else:
        lines.extend(findings)
        lines.append(f"  ({total_orphans} stale field(s) — informational only, not gate-failing)")
    return (0, lines)  # informational; never gate-failing


def lint_cascade_byte_equality(skill_dirs: list) -> tuple:
    """Lint 4 — Cascade byte-equality (SHA-256).

    For every example with consumed_intents.<X>.source_path, hash the
    producer's intent-out.json payload and the consumer's inlined payload
    using json.dumps(sort_keys=True) for deterministic serialisation.
    SHA-256 prefix mismatch = FAIL (cascade contract drift).

    Returns (total_mismatches, report_lines).
    """
    findings = []
    total_checked = 0
    total_mismatches = 0

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        for output_path in sorted(glob.glob(f"{skill_dir}/examples/*/output.json")):
            example_name = os.path.basename(os.path.dirname(output_path))
            try:
                with open(output_path) as f:
                    out = json.load(f)
            except json.JSONDecodeError:
                continue

            consumed = out.get("consumed_intents", {})
            if not isinstance(consumed, dict):
                continue

            for cascade_key, cascade in consumed.items():
                if not isinstance(cascade, dict):
                    continue
                src_path = cascade.get("source_path")
                payload = cascade.get("payload")
                if not src_path or payload is None:
                    continue
                if not os.path.exists(src_path):
                    # Producer fixture absent (DEFERRED-POINTER) — skip
                    continue

                try:
                    with open(src_path) as f:
                        src = json.load(f)
                except json.JSONDecodeError:
                    continue

                # Producer intent-out.json may embed the payload at top level
                # (i.e. the file IS the payload) or under the cascade key.
                # Try cascade_key first; fall back to the whole file.
                src_payload = src.get(cascade_key, src)

                consumer_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
                producer_bytes = json.dumps(src_payload, sort_keys=True, ensure_ascii=False).encode()
                consumer_hash = hashlib.sha256(consumer_bytes).hexdigest()[:16]
                producer_hash = hashlib.sha256(producer_bytes).hexdigest()[:16]
                total_checked += 1

                if consumer_hash != producer_hash:
                    total_mismatches += 1
                    findings.append(
                        f"  FAIL {skill_name}.examples.{example_name}.{cascade_key}: "
                        f"byte-equality mismatch "
                        f"(consumer={consumer_hash} producer={producer_hash})"
                    )

    lines = ["\n## Lint 4 (F.5): Cascade byte-equality (SHA-256)"]
    if total_checked == 0:
        lines.append("  SKIP — no cascade payloads with source_path found")
    elif total_mismatches == 0:
        lines.append(f"  PASS — {total_checked} cascade payload(s) byte-identical to producer fixtures")
    else:
        lines.extend(findings)
        lines.append(f"  ({total_mismatches} mismatch(es) out of {total_checked} checked — gate-failing)")
    return (total_mismatches, lines)


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
    it_tot, it_fail, it_lines = validate_intents_pass(skill_dirs)

    # Pass 5 (F.5) — Manifest metaschema validation
    p5m_total, p5m_failures, p5m_lines = validate_manifests_pass()

    # Pass 6 — Room-types schema (originally Pass 5; renumbered Sprint F.5)
    p6_total, p6_failures, p6_lines = validate_room_types_pass()

    # Pass 7 — ASHRAE source files (originally Pass 6)
    p7_total, p7_failures, p7_lines = validate_ashrae_pass()

    # Pass 8 — ISO 16739 IFC subset (originally Pass 7)
    p8_total, p8_failures, p8_lines = validate_ifc_pass()

    # Lint 1-4 (Sprint F.5 additions)
    l1_unknowns, l1_lines = lint_manifest_fields()
    l2_failures, l2_lines = lint_grounded_sources(skill_dirs)
    l3_orphans, l3_lines = lint_dropped_items_orphaned(skill_dirs)
    l4_mismatches, l4_lines = lint_cascade_byte_equality(skill_dirs)

    # Lint 5 — Canonical room.type membership (Sprint X.E.1 / Z.E.1)
    l5_failures, l5_lines = lint_canonical_room_type_membership(skill_dirs)

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

    print("=== Pass 4 — Intent emissions ===\n")
    for line in it_lines:
        print(line)
    print(f"\nSubtotal: {it_tot - it_fail}/{it_tot} pass ({it_fail} failures)\n")

    print("=== Pass 5 (F.5) — Manifest metaschema validation ===\n")
    for line in p5m_lines:
        print(line)
    print(f"\nSubtotal: {p5m_total - p5m_failures}/{p5m_total} pass ({p5m_failures} failures)\n")

    print("=== Pass 6 — Room-types schema (3 catalogues: T13 + SL + T11) ===\n")
    for line in p6_lines:
        print(line)
    print(f"\nSubtotal: {p6_total - p6_failures}/{p6_total} entries pass ({p6_failures} failures)\n")

    print("=== Pass 7 — ASHRAE source files ===\n")
    for line in p7_lines:
        print(line)
    print(f"\nSubtotal: {p7_total - p7_failures}/{p7_total} files pass ({p7_failures} failures)\n")

    print("=== Pass 8 — ISO 16739 IFC subset ===\n")
    for line in p8_lines:
        print(line)
    print(f"\nSubtotal: {p8_total - p8_failures}/{p8_total} files pass ({p8_failures} failures)\n")

    print("=== Lint 1 (F.5) — Manifest field-name typos ===\n")
    for line in l1_lines:
        print(line)
    print()

    print("=== Lint 2 (F.5) — grounded_source two-tier validation ===\n")
    for line in l2_lines:
        print(line)
    print()

    print("=== Lint 3 (F.5) — Dropped-item orphans in examples ===\n")
    for line in l3_lines:
        print(line)
    print()

    print("=== Lint 4 (F.5) — Cascade byte-equality (SHA-256) ===\n")
    for line in l4_lines:
        print(line)
    print()

    print("=== Lint 5 — Canonical room.type membership ===\n")
    for line in l5_lines:
        print(line)
    print()

    total = (ex_tot + ev_tot + in_tot + it_tot + p5m_total
             + p6_total + p7_total + p8_total)
    total_fail = (ex_fail + ev_fail + in_fail + it_fail + p5m_failures
                  + p6_failures + p7_failures + p8_failures
                  + l2_failures + l4_mismatches + l5_failures)
    print(f"=== AGGREGATE: {total - total_fail}/{total} pass ({total_fail} failures) ===")
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
