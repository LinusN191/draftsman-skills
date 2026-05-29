# photometric-analysis v1.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `electrical/photometric-analysis/` from v0.1.0 stub to v1.0.0 production — DIALux-grade point-grid + uniformity U₀ + UGR computation wrapping `calc.lumen_grid_solver`. Build the new `shared/photometric/ies/` library with 8 synthetic reference IES files. Wire the lighting-layout cascade contract (manifest + schema + INV-11 rewrite + 7 example retrofits).

**Architecture:** Four phases (A foundations → B prompts → C examples → D cascade integration + ship) with 13 implementer tasks total. Calc-primitive skill: emits IR with calc inputs filled + outputs marked `tool_call_pending: false` after runtime `calc.lumen_grid_solver` invocation. Reuses cable-sizing's `consumes_intents[]` manifest shape; reuses D3 photometric ontology (UF tables) as fallback in validator only (Full v1.0 requires real IES at production). Wave 1 first deliverable of the lighting skill family roadmap.

**Tech Stack:** JSON Schema Draft-07 (IR + intent schemas), Markdown (generator/validator/reviewer prompts), YAML (rules + evals), Python 3.11 (LM-63 IES file generator + validate-examples.py + functional_audit.py), ANSI/IES LM-63-2002 (IES file format).

**Spec:** `docs/superpowers/specs/2026-05-30-photometric-analysis-design.md` (commit `e5c6556`).

**Version bumps:**
- photometric-analysis: `[0.1.0]` (stub) → `[1.0.0]` (production)
- lighting-layout: `[1.4.0]` → `[1.5.0]` (additive — consumes_intents + INV-11 rewrite + 7 example retrofits)

**Gates target:** validate-examples 236/236 → ~257/257 (+21 estimated per spec §12); functional_audit 1 finding unchanged (disclosed motor-superposition oracle FP on `fault-level/us-industrial-with-motors/MCC-1`).

**Pre-flight notes (verified by spec author):**
- Existing stub at `electrical/photometric-analysis/` has only README.md + skill.manifest.json + empty `docs/`, `evals/`, `examples/`, `prompts/`. Need to populate everything else.
- Cable-sizing's `consumes_intents[]` shape uses `{skill_id, intent_name, version_constraint}` — we extend this to add a new optional `trigger` field for conditional cascades (per spec §10.1).
- Lighting-layout v1.4.0 currently has empty `consumes_intents: []`. Phase D adds the photometric_grid cascade entry.
- No `.ies` files exist in the repo yet. Phase A.1 ships a synthetic-IES generator + 8 reference files (open-source friendly; avoids manufacturer-license concerns; deterministic + reproducible).
- The shared `calc.lumen_grid_solver` calc contract exists at `shared/calculations/lighting/lumen-grid-solver.json` but is currently a 5-line stub (implementation_note only). This sprint expands its I/O schema based on B.1's generator step — but does NOT implement the runtime executor (lives in runtime project per `[[runtime-project-boundary]]`).

---

## File Structure

### Modified

- `electrical/photometric-analysis/skill.manifest.json` — stub fields → production fields (standards, inputs, outputs, produces_intents, consumes_intents)
- `electrical/photometric-analysis/README.md` — stub body → real skill body
- `shared/calculations/lighting/lumen-grid-solver.json` — expand I/O contract (inputs + outputs schema) based on B.1 generator spec
- `electrical/lighting-layout/skill.manifest.json` — D.1: bump 1.4.0 → 1.5.0; populate `consumes_intents[]` with photometric_grid cascade entry
- `shared/schemas/electrical/lighting-layout-ir.schema.json` — D.1: add `consumed_intents` top-level block + extend `allOf` `else` branch to require `consumed_intents.photometric_grid` when `mode == 'full_drawing'`
- `electrical/lighting-layout/prompts/validator.md` — D.1: replace D3 INV-11 placeholder with the 4-sub-check cascade rule
- `electrical/lighting-layout/CHANGELOG.md` — D.3: add [1.5.0] entry (INV-11 cascade activation + 7 example retrofits)
- 7 × `electrical/lighting-layout/examples/<example>/input.json` — D.2: add `photometric_ies_paths[]` field per example
- 7 × `electrical/lighting-layout/examples/<example>/output.json` — D.2: add `consumed_intents.photometric_grid` block + rewrite INV-11 evidence
- 7 × `electrical/lighting-layout/examples/<example>/intent-out.json` — D.2: add `consumed_intents.photometric_grid` block

### Created

#### `shared/photometric/` (NEW shared resource — A.1)
- `shared/photometric/README.md` — provenance + verification_status policy + per-file inventory + substitution policy
- `shared/photometric/ies-provenance.json` — machine-readable per-file provenance (8 entries)
- `shared/photometric/ies/LED_PANEL_600.ies` — 6000 lm 4000K opal-diffuser variant
- `shared/photometric/ies/LED_PANEL_600-4500lm.ies` — 4500 lm variant
- `shared/photometric/ies/LED_PANEL_600-3500lm.ies` — 3500 lm variant
- `shared/photometric/ies/LED_DOWNLIGHT.ies` — 1000 lm 100mm narrow-beam
- `shared/photometric/ies/HIGHBAY.ies` — 22000 lm industrial narrow-beam
- `shared/photometric/ies/LINEAR_LED.ies` — 5000 lm 1200×100 batten (reference; not used in current examples but in inventory for future)
- `shared/photometric/ies/EMERGENCY.ies` — 300 lm emergency 300×100
- `shared/photometric/ies/HALOGEN_DOWNLIGHT.ies` — 750 lm 50W halogen GU10 (legacy demo)
- `shared/schemas/core/photometric-provenance.schema.json` — validates ies-provenance.json shape
- `scripts/generate_reference_ies.py` — deterministic LM-63 generator from `{beam_angle, lumens, mounting_type}` analytical model

#### `electrical/photometric-analysis/` (skill build — Phases A–C)
- `electrical/photometric-analysis/inputs.json` — 5 items (A.4)
- `electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json` — full IR schema (A.3)
- `electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json` — intent payload schema (A.3)
- `electrical/photometric-analysis/prompts/generator.md` — ~600 lines (B.1)
- `electrical/photometric-analysis/prompts/validator.md` — ~350 lines, 9 INVs (B.2)
- `electrical/photometric-analysis/prompts/reviewer.md` — ~200 lines, 5 D-checks (B.3)
- `electrical/photometric-analysis/rules/grid-spacing-rules.yaml` — BS EN 12464-1 §6.2 formula + per-task tolerance (A.4)
- `electrical/photometric-analysis/rules/ugr-rules.yaml` — CIE 117 observer geometry + per-room UGR limits per BS EN 12464-1 Table 5.3 (A.4)
- `electrical/photometric-analysis/rules/ies-provenance-rules.yaml` — `_source` provenance string requirements + verification_status enum (A.4)
- `electrical/photometric-analysis/CHANGELOG.md` — initial v1.0.0 entry (A.2)
- `electrical/photometric-analysis/examples/uk-open-plan-office-10x8-dali-photometric/{input,output,intent-out}.json + reasoning.md` (C.1)
- `electrical/photometric-analysis/examples/uk-office-uniformity-fail-perimeter-cold-spots/{input,output,intent-out}.json + reasoning.md` (C.1)
- `electrical/photometric-analysis/examples/uk-drawing-office-strict-ugr/{input,output,intent-out}.json + reasoning.md` (C.1)
- 7 × `electrical/photometric-analysis/examples/cascade-<lighting-layout-name>/{input,output,intent-out}.json + reasoning.md` (C.2)
- `electrical/photometric-analysis/evals/eval-01-grid-spacing-formula.yaml` through `eval-05-...yaml` (C.3 — minimum 5 per CLAUDE.md)
- `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/photometric-analysis-shipped.md` — sprint shipped memory (D.3)

---

## Phase A — Foundations (4 tasks, sequential)

Shared IES library + skill scaffolding + schemas + inputs/rules must land before B prompts can cite them.

---

## Task A.1: Shared IES library + synthetic LM-63 generator (Opus)

**Why Opus:** Engineering judgment on photometric realism (analytical model selection per luminaire archetype) + LM-63 format correctness + provenance disclosure language.

**Files:**
- Create: `scripts/generate_reference_ies.py` — deterministic generator
- Create: `shared/photometric/ies/<8 files>.ies`
- Create: `shared/photometric/ies-provenance.json`
- Create: `shared/photometric/README.md`
- Create: `shared/schemas/core/photometric-provenance.schema.json`

**Standards reference:** ANSI/IES LM-63-2002 (file format) + CIBSE LG7 §6.2 (typical luminaire intensity distributions per archetype).

- [ ] **Step 1: Create the metaschema for ies-provenance.json**

Write `shared/schemas/core/photometric-provenance.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/photometric-provenance.schema.json",
  "title": "Photometric IES Provenance",
  "description": "Machine-readable provenance for shared/photometric/ies/ reference files. Validates ies-provenance.json shape.",
  "type": "object",
  "required": ["_note", "files"],
  "additionalProperties": false,
  "properties": {
    "$schema": {"type": "string"},
    "_note": {
      "type": "string",
      "minLength": 60,
      "description": "Library-level honest disclosure of verification_status policy."
    },
    "files": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "filename", "luminaire_type", "lumens", "wattage_w", "cct_k",
          "verification_status", "_source", "_retrieved", "_lm63_version"
        ],
        "additionalProperties": false,
        "properties": {
          "filename": {"type": "string", "pattern": "^[A-Z][A-Z0-9_-]*\\.ies$"},
          "luminaire_type": {"type": "string", "minLength": 3},
          "lumens": {"type": "integer", "minimum": 100, "maximum": 200000},
          "wattage_w": {"type": "number", "exclusiveMinimum": 0},
          "cct_k": {"type": "integer", "minimum": 2000, "maximum": 8000},
          "beam_angle_deg": {"type": "integer", "minimum": 5, "maximum": 180},
          "verification_status": {
            "enum": ["engineer_typical_C2", "manufacturer_supplied_project_specific", "synthetic_reference_C3"]
          },
          "_source": {
            "type": "string",
            "minLength": 40,
            "description": "Provenance string: archetype name + intended use + verification caveats + substitution policy."
          },
          "_retrieved": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
          "_lm63_version": {"enum": ["LM-63-1995", "LM-63-2002", "LM-63-2019"]}
        }
      }
    }
  }
}
```

- [ ] **Step 2: Write the synthetic IES generator script**

Create `scripts/generate_reference_ies.py`. This is a deterministic, dependency-free Python script (no numpy/scipy — stdlib only) that emits ANSI/IES LM-63-2002 ASCII files from `{luminaire_type, lumens, wattage_w, cct_k, mounting_type, distribution_model, beam_angle_deg}`. It uses three analytical models matched to luminaire archetypes:

- **`lambertian_panel`** — for LED_PANEL_600, LED_PANEL_600-4500lm, LED_PANEL_600-3500lm, EMERGENCY. Intensity I(θ) = I₀ × cos(θ) for θ ∈ [0°, 90°], zero for θ > 90°. Diffuse downward distribution per CIBSE LG7 §6.2 typical opal-diffuser panel.
- **`gaussian_narrow`** — for LED_DOWNLIGHT, HIGHBAY, HALOGEN_DOWNLIGHT. Intensity I(θ) = I₀ × exp(-θ²/(2σ²)) where σ = beam_angle_deg / 2.355 (FWHM convention). Tighter beam matches reflector luminaires.
- **`lambertian_batten`** — for LINEAR_LED. Intensity I(θ, φ) = I₀ × cos(θ) × (1 + 0.3 × cos(2φ)) for θ ∈ [0°, 90°]. Asymmetric to model along-axis vs across-axis emission.

LM-63 file structure (per ANSI/IES LM-63-2002 §4):

```
IESNA:LM-63-2002
[TEST] <test-id>
[TESTLAB] DraftsMan synthetic reference
[ISSUEDATE] 2026-05-30
[MANUFAC] DraftsMan synthetic — engineer-typical reference
[LUMCAT] <luminaire_type>
[LUMINAIRE] <luminaire_type> — synthetic photometric distribution per scripts/generate_reference_ies.py
[LAMPCAT] LED <cct_k>K
[LAMP] LED <lumens>lm <wattage_w>W
[OTHER] Synthetic distribution; engineer-of-record MUST substitute project IES before final design freeze
TILT=NONE
1 <lumens> 1.0 <n_v_angles> <n_h_angles> 1 2 -<width_m> -<width_m> 0
1.0 <wattage_w> 1.0
<vertical_angles_space_separated>
<horizontal_angles_space_separated>
<candela_values_row_major>
```

Where:
- `n_v_angles = 19` (0, 5, 10, ..., 90 degrees for panels; 0, 5, ..., 90 for downlights — half-hemisphere)
- `n_h_angles = 1` (axisymmetric panels + downlights + highbay + emergency) OR `13` (linear batten, 0..180 in 15° steps)
- `width_m` = luminaire physical width in meters from {LED_PANEL_600: 0.6, LED_DOWNLIGHT: 0.1, HIGHBAY: 0.3, LINEAR_LED: 1.2, EMERGENCY: 0.3, HALOGEN_DOWNLIGHT: 0.1}
- Candela values normalised so total flux integrates to `lumens` (numerical integration over hemisphere).

Write the script with this exact structure (~280 lines):

```python
#!/usr/bin/env python3
"""
Deterministic LM-63-2002 IES file generator for shared/photometric/ies/ library.

Produces synthetic photometric distributions per CIBSE LG7 §6.2 archetypes:
- lambertian_panel: opal-diffuser LED panels (LED_PANEL_600, EMERGENCY)
- gaussian_narrow:  reflector luminaires (LED_DOWNLIGHT, HIGHBAY, HALOGEN_DOWNLIGHT)
- lambertian_batten: linear LED battens (LINEAR_LED)

All output flagged verification_status: synthetic_reference_C3 — for skill examples only.
Engineer-of-record MUST substitute project-specific manufacturer IES before final design freeze.

Usage:
    python3 scripts/generate_reference_ies.py
    # Generates 8 .ies files in shared/photometric/ies/ + provenance entries
"""

import json
import math
import os
from datetime import date
from pathlib import Path

# 8 reference luminaires per spec §8.1 + provenance per spec §8.2
LUMINAIRES = [
    {
        "filename": "LED_PANEL_600.ies",
        "luminaire_type": "LED_PANEL_600",
        "lumens": 6000, "wattage_w": 48, "cct_k": 4000,
        "beam_angle_deg": 110, "width_m": 0.6,
        "distribution_model": "lambertian_panel",
        "_source": "Synthetic 600x600mm recessed LED panel, opal diffuser, 4000K. Distribution: Lambertian cos(theta) per CIBSE LG7 §6.2 typical opal panel. Engineer-of-record MUST substitute project IES before final design freeze."
    },
    {
        "filename": "LED_PANEL_600-4500lm.ies",
        "luminaire_type": "LED_PANEL_600",
        "lumens": 4500, "wattage_w": 36, "cct_k": 4000,
        "beam_angle_deg": 110, "width_m": 0.6,
        "distribution_model": "lambertian_panel",
        "_source": "Synthetic 600x600mm recessed LED panel, opal diffuser, 4000K, 4500lm variant. Distribution: Lambertian per CIBSE LG7 §6.2. Engineer must substitute project IES."
    },
    {
        "filename": "LED_PANEL_600-3500lm.ies",
        "luminaire_type": "LED_PANEL_600",
        "lumens": 3500, "wattage_w": 28, "cct_k": 4000,
        "beam_angle_deg": 110, "width_m": 0.6,
        "distribution_model": "lambertian_panel",
        "_source": "Synthetic 600x600mm recessed LED panel, opal diffuser, 4000K, 3500lm variant (under-spec demo). Engineer must substitute project IES."
    },
    {
        "filename": "LED_DOWNLIGHT.ies",
        "luminaire_type": "LED_DOWNLIGHT",
        "lumens": 1000, "wattage_w": 12, "cct_k": 3000,
        "beam_angle_deg": 60, "width_m": 0.1,
        "distribution_model": "gaussian_narrow",
        "_source": "Synthetic 100mm narrow-beam recessed LED downlight, 3000K, prismatic lens. Distribution: Gaussian sigma=FWHM/2.355 per CIBSE LG7 §6.2 typical reflector luminaire. Engineer must substitute project IES."
    },
    {
        "filename": "HIGHBAY.ies",
        "luminaire_type": "HIGHBAY",
        "lumens": 22000, "wattage_w": 150, "cct_k": 5000,
        "beam_angle_deg": 90, "width_m": 0.3,
        "distribution_model": "gaussian_narrow",
        "_source": "Synthetic industrial highbay LED, 5000K, narrow-beam reflector for 8m+ mounting. Distribution: Gaussian per CIBSE LG7 §6.2 typical industrial highbay. Engineer must substitute project IES."
    },
    {
        "filename": "LINEAR_LED.ies",
        "luminaire_type": "LINEAR_LED",
        "lumens": 5000, "wattage_w": 40, "cct_k": 4000,
        "beam_angle_deg": 120, "width_m": 1.2,
        "distribution_model": "lambertian_batten",
        "_source": "Synthetic 1200x100mm linear LED batten, 4000K. Distribution: asymmetric Lambertian with along-axis weighting per CIBSE LG7 §6.2 typical batten. Engineer must substitute project IES."
    },
    {
        "filename": "EMERGENCY.ies",
        "luminaire_type": "EMERGENCY",
        "lumens": 300, "wattage_w": 5, "cct_k": 4000,
        "beam_angle_deg": 120, "width_m": 0.3,
        "distribution_model": "lambertian_panel",
        "_source": "Synthetic 300x100mm emergency luminaire (self-contained 3h duration, anti-panic), 4000K. Distribution: Lambertian. Per BS 5266-1:2016 §5.3 anti-panic minimum 0.5 lux floor. Engineer must verify against actual emergency luminaire IES."
    },
    {
        "filename": "HALOGEN_DOWNLIGHT.ies",
        "luminaire_type": "HALOGEN_DOWNLIGHT",
        "lumens": 750, "wattage_w": 50, "cct_k": 2800,
        "beam_angle_deg": 36, "width_m": 0.1,
        "distribution_model": "gaussian_narrow",
        "_source": "Synthetic 50W GU10 halogen downlight, 2800K, 36-degree beam (legacy retrofit demo for uk-part-l-fail-incandescent). 15 lm/W efficacy, fails Approved Doc L 2021 §6 Table 6.2 95 lm/W minimum. Engineer must substitute project IES."
    }
]

V_ANGLES = list(range(0, 91, 5))  # 19 vertical angles 0..90 in 5° steps


def lambertian_panel_intensity(I0, theta_deg):
    """Diffuse downward: I(θ) = I₀ × cos(θ) for θ ∈ [0, 90°]; else 0."""
    if theta_deg > 90:
        return 0.0
    return I0 * math.cos(math.radians(theta_deg))


def gaussian_narrow_intensity(I0, theta_deg, fwhm_deg):
    """Reflector beam: I(θ) = I₀ × exp(-θ²/(2σ²)) where σ = FWHM/2.355."""
    if theta_deg > 90:
        return 0.0
    sigma = fwhm_deg / 2.355
    return I0 * math.exp(-(theta_deg ** 2) / (2 * sigma ** 2))


def lambertian_batten_intensity(I0, theta_deg, phi_deg):
    """Asymmetric: I(θ, φ) = I₀ × cos(θ) × (1 + 0.3 × cos(2φ))."""
    if theta_deg > 90:
        return 0.0
    return (
        I0
        * math.cos(math.radians(theta_deg))
        * (1 + 0.3 * math.cos(math.radians(2 * phi_deg)))
    )


def normalise_to_total_lumens(intensities_2d, v_angles_deg, h_angles_deg, target_lumens):
    """Numerically integrate hemisphere → scale so total flux = target_lumens."""
    total = 0.0
    n_h = len(h_angles_deg)
    for i, theta in enumerate(v_angles_deg):
        if i == 0 or i == len(v_angles_deg) - 1:
            d_theta = math.radians(2.5)
        else:
            d_theta = math.radians(5.0)
        sin_theta = math.sin(math.radians(theta))
        for j, _phi in enumerate(h_angles_deg):
            d_phi = math.radians(360.0 / max(1, n_h))
            total += intensities_2d[i][j] * sin_theta * d_theta * d_phi
    if total == 0:
        raise ValueError(f"Total flux integration produced zero (check distribution model)")
    scale = target_lumens / total
    return [[v * scale for v in row] for row in intensities_2d]


def emit_ies_lm63(spec):
    """Build LM-63-2002 ASCII content for one luminaire spec."""
    lumens = spec["lumens"]
    wattage = spec["wattage_w"]
    cct = spec["cct_k"]
    beam = spec["beam_angle_deg"]
    width = spec["width_m"]
    model = spec["distribution_model"]

    if model == "lambertian_batten":
        h_angles = list(range(0, 181, 15))  # 13 horizontal angles 0..180 every 15°
    else:
        h_angles = [0]  # axisymmetric

    # Initial unscaled intensities (I0=1.0 placeholder; we normalise after)
    intensities = []
    for theta in V_ANGLES:
        row = []
        for phi in h_angles:
            if model == "lambertian_panel":
                row.append(lambertian_panel_intensity(1.0, theta))
            elif model == "gaussian_narrow":
                row.append(gaussian_narrow_intensity(1.0, theta, beam))
            elif model == "lambertian_batten":
                row.append(lambertian_batten_intensity(1.0, theta, phi))
            else:
                raise ValueError(f"Unknown distribution_model: {model}")
        intensities.append(row)

    # Normalise so integral = lumens
    intensities = normalise_to_total_lumens(intensities, V_ANGLES, h_angles, lumens)

    today = date.today().isoformat()

    lines = []
    lines.append("IESNA:LM-63-2002")
    lines.append(f"[TEST] DraftsMan-{spec['filename'].replace('.ies', '')}")
    lines.append("[TESTLAB] DraftsMan synthetic reference")
    lines.append(f"[ISSUEDATE] {today}")
    lines.append("[MANUFAC] DraftsMan synthetic — engineer-typical reference")
    lines.append(f"[LUMCAT] {spec['luminaire_type']}")
    lines.append(
        f"[LUMINAIRE] {spec['luminaire_type']} — synthetic photometric distribution "
        f"per scripts/generate_reference_ies.py ({model})"
    )
    lines.append(f"[LAMPCAT] LED {cct}K")
    lines.append(f"[LAMP] LED {lumens}lm {wattage}W")
    lines.append(
        "[OTHER] verification_status=synthetic_reference_C3. Engineer-of-record MUST "
        "substitute project IES before final design freeze."
    )
    lines.append("TILT=NONE")
    # Line 10: 1 <lumens> 1.0 <n_v> <n_h> 1 2 -<w> -<w> 0
    lines.append(
        f"1 {lumens} 1.0 {len(V_ANGLES)} {len(h_angles)} 1 2 "
        f"{-width:.2f} {-width:.2f} 0"
    )
    # Line 11: <ballast_factor> <input_watts> <future>
    lines.append(f"1.0 {wattage} 1.0")
    # Vertical angles
    lines.append(" ".join(f"{a}" for a in V_ANGLES))
    # Horizontal angles
    lines.append(" ".join(f"{a}" for a in h_angles))
    # Candela values, row-major (one row per vertical angle, all horizontal angles per row)
    for row in intensities:
        lines.append(" ".join(f"{v:.2f}" for v in row))

    return "\n".join(lines) + "\n"


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ies_dir = repo_root / "shared" / "photometric" / "ies"
    ies_dir.mkdir(parents=True, exist_ok=True)

    provenance = {
        "$schema": "../../schemas/core/photometric-provenance.schema.json",
        "_note": (
            "Reference IES files for photometric-analysis skill examples + cascade retrofit "
            "of existing lighting-layout examples. ALL files flagged verification_status="
            "synthetic_reference_C3 — generated by scripts/generate_reference_ies.py from "
            "CIBSE LG7 §6.2 archetypes (Lambertian / Gaussian). NOT project-deliverable; "
            "engineer-of-record MUST substitute project-specific manufacturer IES files "
            "before final design freeze."
        ),
        "files": []
    }

    today = date.today().isoformat()

    for spec in LUMINAIRES:
        ies_path = ies_dir / spec["filename"]
        ies_path.write_text(emit_ies_lm63(spec))
        provenance["files"].append({
            "filename": spec["filename"],
            "luminaire_type": spec["luminaire_type"],
            "lumens": spec["lumens"],
            "wattage_w": spec["wattage_w"],
            "cct_k": spec["cct_k"],
            "beam_angle_deg": spec["beam_angle_deg"],
            "verification_status": "synthetic_reference_C3",
            "_source": spec["_source"],
            "_retrieved": today,
            "_lm63_version": "LM-63-2002"
        })
        print(f"Wrote {ies_path.relative_to(repo_root)} ({len(ies_path.read_text())} chars)")

    provenance_path = repo_root / "shared" / "photometric" / "ies-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Wrote {provenance_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the generator + commit the IES files + provenance**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
mkdir -p shared/photometric/ies
python3 scripts/generate_reference_ies.py
```

Expected output (8 file writes + 1 provenance write):

```
Wrote shared/photometric/ies/LED_PANEL_600.ies (~1100 chars)
Wrote shared/photometric/ies/LED_PANEL_600-4500lm.ies (~1100 chars)
... (8 entries total)
Wrote shared/photometric/ies-provenance.json
```

- [ ] **Step 4: Validate provenance file against new metaschema**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/photometric-provenance.schema.json'))
prov   = json.load(open('shared/photometric/ies-provenance.json'))
jsonschema.validate(instance=prov, schema=schema)
print(f'Provenance valid: {len(prov[\"files\"])} entries')"
```

Expected: `Provenance valid: 8 entries`.

Note: per spec §6.1 / §8.3, `synthetic_reference_C3` is a NEW verification_status value (extends the D2.3 `engineer_typical_C2` set). The metaschema enum in Step 1 includes all 3 values: `engineer_typical_C2`, `manufacturer_supplied_project_specific`, `synthetic_reference_C3`. C3 distinguishes "generated from analytical archetype" from C2 ("transcribed from industry-typical published reference").

- [ ] **Step 5: Write shared/photometric/README.md**

```markdown
# Shared photometric reference library

## Purpose
Reference IES files for `electrical/photometric-analysis/` skill examples + cascade retrofit
of `electrical/lighting-layout/` examples. NOT project-deliverable; engineer-of-record MUST
substitute project-specific manufacturer IES files before final design freeze.

## Verification status policy
ALL files at `ies/` flagged `verification_status: synthetic_reference_C3` per the D2.3 +
photometric-analysis spec §6.1 + §8.3 honest-disclosure pattern. Distributions generated by
`scripts/generate_reference_ies.py` from CIBSE LG7 §6.2 typical archetypes (Lambertian /
Gaussian analytical models). No file is a manufacturer-specific photometric measurement.

`verification_status` enum values:
- `synthetic_reference_C3` — generated by scripts/generate_reference_ies.py from analytical
  archetype (current library)
- `engineer_typical_C2` — transcribed from industry-typical published reference (CIBSE LG7
  illustration tables, manufacturer datasheet aggregate)
- `manufacturer_supplied_project_specific` — actual manufacturer LM-63 measurement for the
  exact project luminaire (engineer-of-record substitutes for final design freeze)

## When to substitute
- After luminaire selection in tender stage
- Before any submission for building control / Part L sign-off
- Before any project-specific UGR / U₀ claim in a tender response

## File format
ANSI/IES LM-63-2002 ASCII format. Each file 800-1500 chars. Validated by
`calc.lumen_grid_solver` LM-63 parser at runtime.

## Inventory (8 files, all synthetic_reference_C3)

| filename | luminaire_type | lumens | wattage | CCT | beam | model |
|---|---|---|---|---|---|---|
| LED_PANEL_600.ies          | LED_PANEL_600     | 6000  | 48 W  | 4000K | 110° | lambertian_panel |
| LED_PANEL_600-4500lm.ies   | LED_PANEL_600     | 4500  | 36 W  | 4000K | 110° | lambertian_panel |
| LED_PANEL_600-3500lm.ies   | LED_PANEL_600     | 3500  | 28 W  | 4000K | 110° | lambertian_panel |
| LED_DOWNLIGHT.ies          | LED_DOWNLIGHT     | 1000  | 12 W  | 3000K |  60° | gaussian_narrow |
| HIGHBAY.ies                | HIGHBAY           | 22000 | 150 W | 5000K |  90° | gaussian_narrow |
| LINEAR_LED.ies             | LINEAR_LED        | 5000  | 40 W  | 4000K | 120° | lambertian_batten |
| EMERGENCY.ies              | EMERGENCY         | 300   | 5 W   | 4000K | 120° | lambertian_panel |
| HALOGEN_DOWNLIGHT.ies      | HALOGEN_DOWNLIGHT | 750   | 50 W  | 2800K |  36° | gaussian_narrow |

## Regenerating

```bash
python3 scripts/generate_reference_ies.py
```

Deterministic + dependency-free (Python stdlib only). Re-run to regenerate identical bytes
after format-only edits (e.g. metaschema bumps).

## Adding new reference files
1. Add a new entry to `LUMINAIRES` in `scripts/generate_reference_ies.py`
2. Re-run the script
3. Verify `ies-provenance.json` shape via the metaschema
4. Update the inventory table above
5. INV-8 in photometric-analysis validator continues to pass (provenance _source ≥40 chars
   + verification_status enum match)
```

- [ ] **Step 6: Run golden CI gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 236/236 pass (0 failures)` (unchanged — IES files + provenance not yet wired to any example; first example consumption lands in C.1).

```bash
python3 functional_audit.py 2>&1 | tail -3
```

Expected: `TOTAL FINDINGS: 1` (disclosed motor-superposition oracle FP).

- [ ] **Step 7: Commit A.1**

```bash
git add scripts/generate_reference_ies.py \
        shared/photometric/ \
        shared/schemas/core/photometric-provenance.schema.json
git commit -m "$(cat <<'EOF'
feat(shared/photometric): A.1 shared IES library + LM-63 generator + provenance metaschema

First task of photometric-analysis v1.0 sprint (Wave 1). Establishes
the shared/photometric/ resource consumed by photometric-analysis skill
examples + cascade retrofit of 7 existing lighting-layout examples.

NEW scripts/generate_reference_ies.py (~280 lines):
- Deterministic stdlib-only Python script (no numpy)
- 3 analytical distribution models per CIBSE LG7 §6.2 archetype:
  - lambertian_panel: I(θ) = I₀×cos(θ) for opal panels
  - gaussian_narrow: I(θ) = I₀×exp(-θ²/(2σ²)) for reflector beams
  - lambertian_batten: I(θ,φ) = I₀×cos(θ)×(1+0.3×cos(2φ)) for linear
- Numerical hemisphere integration → normalises total flux = lumens
- Emits ANSI/IES LM-63-2002 ASCII format

NEW shared/photometric/ies/ (8 files, ~80 KB total):
- LED_PANEL_600 + 4500lm + 3500lm variants (3 panels)
- LED_DOWNLIGHT, HIGHBAY, LINEAR_LED, EMERGENCY, HALOGEN_DOWNLIGHT (5)

NEW shared/photometric/ies-provenance.json:
- Machine-readable per-file provenance (8 entries)
- All flagged verification_status: synthetic_reference_C3 (new value
  extending D2.3 engineer_typical_C2 set; documented in README)

NEW shared/photometric/README.md:
- verification_status policy + substitution timing
- Per-file inventory table
- Regeneration instructions

NEW shared/schemas/core/photometric-provenance.schema.json:
- Validates ies-provenance.json shape
- Enforces verification_status enum (3 values: C2, C3, project_specific)
- Enforces _source ≥40 chars (provenance honest-disclosure threshold)

Honest disclosure: all 8 files synthetic_reference_C3 — generated by
analytical archetype, NOT manufacturer-measured. Engineer-of-record
substitutes project-specific IES before final design freeze. README
documents the substitution policy explicitly.

Gates: validate-examples 236/236 unchanged (IES files not yet consumed;
first wire-up lands in C.1 examples). functional_audit 1 finding
unchanged (disclosed FP).

Next: A.2 skill scaffolding (stub manifest → production).
EOF
)"
```

---

## Task A.2: Skill scaffolding — manifest + README + CHANGELOG (Sonnet)

**Why Sonnet:** Mechanical scaffolding. Manifest fields + README sections + CHANGELOG entry are structural, no engineering judgment beyond schema conformance.

**Files:**
- Modify: `electrical/photometric-analysis/skill.manifest.json` — stub → production
- Modify: `electrical/photometric-analysis/README.md` — stub body → real skill body
- Create: `electrical/photometric-analysis/CHANGELOG.md`

**Pattern parent:** `electrical/cable-sizing/skill.manifest.json` (calc-primitive shape with `consumes_intents[]`).

- [ ] **Step 1: Read current stub manifest**

```bash
cat electrical/photometric-analysis/skill.manifest.json
```

Note the 9 stub fields: `skill`, `version`, `status`, `discipline`, `description`, `standards` (empty), `inputs` (empty), `outputs` (empty), `compatible_runtimes`.

- [ ] **Step 2: Rewrite manifest with production fields**

Overwrite `electrical/photometric-analysis/skill.manifest.json` with:

```json
{
  "skill": "photometric-analysis",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "lighting",
  "chat_type": "calculation",
  "description": "DIALux-grade photometric point-grid + uniformity U₀ + UGR computation per BS EN 12464-1:2021 §4.4/§6.2/§6.6 + CIE 117. Calc-primitive skill wrapping calc.lumen_grid_solver runtime tool. Consumes lighting-layout intent + per-luminaire IES files (LM-63-2002); produces photometric_grid intent consumed by lighting-layout INV-11 + emergency-lighting + daylight (Wave 3/4). Full v1.0 — IES required, no ontology UF fallback at production.",
  "status": "production",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "outputs": [
    "photometric-analysis-ir"
  ],
  "output_schema": "electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json",
  "produces_intents": [
    {
      "name": "photometric-grid",
      "version": "1.0.0",
      "schema_path": "electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json"
    }
  ],
  "produces_intent_schema": "electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json",
  "consumes_intents": [
    {
      "skill_id": "lighting-layout",
      "intent_name": "lighting-layout",
      "version_constraint": "^1.0"
    }
  ],
  "standards": [
    "BS EN 12464-1:2021 §4.4 (uniformity)",
    "BS EN 12464-1:2021 §6.2 (grid spacing formula)",
    "BS EN 12464-1:2021 §6.6 (UGR limits)",
    "BS EN 12464-1:2021 Table 5.3 (task minima per room_type)",
    "ANSI/IES LM-63-2002 (IES file format)",
    "CIE 117 (UGR formula + observer geometry)",
    "CIBSE LG7 §6 (UF/MF reference)"
  ],
  "calculations": [
    "shared/calculations/lighting/lumen-grid-solver.json"
  ],
  "rules": [
    "electrical/photometric-analysis/rules/grid-spacing-rules.yaml",
    "electrical/photometric-analysis/rules/ugr-rules.yaml",
    "electrical/photometric-analysis/rules/ies-provenance-rules.yaml"
  ],
  "examples": [
    "electrical/photometric-analysis/examples/uk-open-plan-office-10x8-dali-photometric/",
    "electrical/photometric-analysis/examples/uk-office-uniformity-fail-perimeter-cold-spots/",
    "electrical/photometric-analysis/examples/uk-drawing-office-strict-ugr/",
    "electrical/photometric-analysis/examples/cascade-office-open-plan/",
    "electrical/photometric-analysis/examples/cascade-reception-lobby/",
    "electrical/photometric-analysis/examples/cascade-warehouse-highbay/",
    "electrical/photometric-analysis/examples/cascade-uk-undersized-lighting-vs-target/",
    "electrical/photometric-analysis/examples/cascade-uk-multi-entrance-classroom/",
    "electrical/photometric-analysis/examples/cascade-uk-part-l-fail-incandescent/",
    "electrical/photometric-analysis/examples/cascade-uk-open-plan-office-10x8-dali/"
  ],
  "compatible_runtimes": [
    "DraftsMan >= 1.0",
    "Claude Code",
    "OpenClaw"
  ]
}
```

- [ ] **Step 3: Rewrite README.md with production body**

Overwrite `electrical/photometric-analysis/README.md` with:

```markdown
# photometric-analysis — DraftsMan MEP Engineering Skill

**Status:** production (v1.0.0)
**Discipline:** electrical / lighting
**Standards:** BS EN 12464-1:2021 §4.4 + §6.2 + §6.6 + Table 5.3; ANSI/IES LM-63-2002; CIE 117; CIBSE LG7 §6
**Output:** JSON IR + photometric-grid intent payload

## What this skill does

DIALux-grade photometric point-grid calculation. Computes per-point illuminance on the BS EN
12464-1 task plane, scalar uniformity U₀ = E_min / E_avg, and UGR (Unified Glare Rating per
CIE 117) for default + engineer-supplied observer positions. Wraps the runtime
`calc.lumen_grid_solver` tool — skill emits IR with calc inputs filled + outputs marked
`tool_call_pending: false` after runtime invocation.

Closes the BS EN 12464-1 §4.4 + §6.6 verification gap that lumen-method alone cannot fill:
- Lumen method gives average illuminance; cannot detect cold corners
- Photometric grid gives min/max/avg + U₀ — catches uniformity failures
- UGR per CIE 117 catches glare a wattage-based check misses

## Cascade contract

Consumed upstream by `electrical/lighting-layout/` INV-11 when `mode == 'full_drawing'`.
Lighting-layout cannot ship a full_drawing layout without successful photometric-analysis
verification of its proposed luminaire layout.

Reused by `electrical/emergency-lighting/` (Wave 3) and `electrical/daylight/` (Wave 4) —
the calc primitive `calc.lumen_grid_solver` is shared.

## Inputs (per `inputs.json`)
- `lighting_layout_intent_path` (required) — upstream lighting-layout intent-out.json
- `photometric_ies_paths[]` (required) — IES file path per luminaire_type (LM-63-2002)
- `ugr_view_positions_override[]` (optional) — engineer-supplied observer positions beyond
  the 4 CIE 117 defaults
- `task_area_override` (optional) — partial-room task areas
- `reflectance_override` (optional) — verified surface reflectances

## Outputs
- IR: 9-block structure with per-point illuminance_grid + ugr_results + provenance
- Intent: flat `photometric_grid.*` payload with scalar summary fields

## Validator (9 INVs)
HIGH: INV-1 min lux ≥ 0.7×target; INV-2 U₀ ≥ target; INV-3 UGR ≤ limit; INV-4 IES per
luminaire_type required; INV-5 grid formula adherence ±50 mm; INV-6 grid shape consistency;
INV-9 calc actually ran.
MEDIUM: INV-7 ≥4 CIE 117 default observers; INV-8 _source provenance ≥40 chars +
verification_status enum match.

## Reviewer (5 D-checks)
D-1 headroom reasonable; D-2 IES file age + plausibility; D-3 UGR-vs-task-type fit;
D-4 reflectance plausibility; D-5 task-area coverage envelope.

## Examples
10 total: 3 standalone (happy path, U₀ FAIL demo, UGR FAIL demo) + 7 cascade retrofits
(one per existing lighting-layout example).

## Honest disclosures
- Shared IES library at `shared/photometric/ies/` flagged
  `verification_status: synthetic_reference_C3` — distributions generated by analytical
  archetype per CIBSE LG7 §6.2; NOT manufacturer-measured. Engineer-of-record substitutes
  project-specific IES before final design freeze.
- `calc.lumen_grid_solver` executor lives in runtime project per `[[runtime-project-boundary]]`.
  Skill ships contract + IR; runtime ships pixels + numbers.

## Why this skill exists
Created 2026-05-25 as a depth-extension stub during the post-remediation within-skill-scope
audit. Built to v1.0.0 production in 2026-05-30 sprint as Wave 1 first deliverable of the
lighting skill family roadmap.

See `docs/superpowers/specs/2026-05-30-photometric-analysis-design.md` for the locked
architecture decisions + cluster context.
```

- [ ] **Step 4: Create CHANGELOG.md**

Write `electrical/photometric-analysis/CHANGELOG.md`:

```markdown
# Changelog

## [1.0.0] - 2026-05-30 — Initial production release (Wave 1 first deliverable)

### Added
- **Skill scaffolding promoted from v0.1.0 stub.** Production manifest with full standards
  stack (BS EN 12464-1:2021 §4.4/§6.2/§6.6/Table 5.3; ANSI/IES LM-63-2002; CIE 117; CIBSE LG7),
  produces_intents (photometric-grid v1.0.0), consumes_intents (lighting-layout v1.x).
- **Inputs taxonomy** (`inputs.json`): 5 items — lighting_layout_intent_path,
  photometric_ies_paths[], ugr_view_positions_override[], task_area_override,
  reflectance_override.
- **Schemas**: photometric-analysis-ir.schema.json (full IR with per-point illuminance_grid +
  ugr_results + provenance); photometric-grid-intent.schema.json (flat downstream payload).
- **Rules YAML** (3 files): grid-spacing-rules.yaml (BS EN 12464-1 §6.2 adaptive formula);
  ugr-rules.yaml (CIE 117 observer geometry + per-room UGR limits); ies-provenance-rules.yaml
  (provenance _source + verification_status policy).
- **Prompts**: generator.md (~600 lines, 13 numbered steps); validator.md (~350 lines,
  9 INVs); reviewer.md (~200 lines, 5 D-checks).
- **Examples** (10 total): 3 standalone (uk-open-plan-office-10x8-dali-photometric,
  uk-office-uniformity-fail-perimeter-cold-spots, uk-drawing-office-strict-ugr) + 7 cascade
  retrofits (one per existing lighting-layout example).
- **Evals** (≥5 YAML): grid-spacing-formula, ugr-default-observers, ies-required,
  uniformity-failure-detection, provenance-disclosure.

### Cascade integration with lighting-layout
- lighting-layout v1.4.0 → v1.5.0 (additive): manifest gains consumes_intents entry for
  photometric-grid with trigger "mode == 'full_drawing'"; IR schema gains consumed_intents
  block; validator INV-11 rewritten from D3 placeholder to 4-sub-check cascade rule; 7
  existing examples retrofitted with photometric_ies_paths inputs + consumed_intents
  outputs + INV-11 evidence.

### New shared resources
- `shared/photometric/ies/` — 8 reference IES files (LM-63-2002 ASCII, ~80 KB total),
  generated by `scripts/generate_reference_ies.py` from CIBSE LG7 §6.2 archetypes
  (Lambertian / Gaussian).
- `shared/photometric/ies-provenance.json` — machine-readable per-file provenance.
- `shared/photometric/README.md` — verification_status policy + substitution timing.
- `shared/schemas/core/photometric-provenance.schema.json` — validates ies-provenance.json.

### Honest disclosures
- All shared IES files flagged `verification_status: synthetic_reference_C3` (new value
  extending the D2.3 engineer_typical_C2 set). Engineer-of-record MUST substitute
  project-specific manufacturer IES files before final design freeze.
- `calc.lumen_grid_solver` runtime executor not in this repo per
  `[[runtime-project-boundary]]`. Skill emits IR + cascade contract only.

### Gates
- validate-examples.py: 236 → ~257 (+21 across the sprint).
- functional_audit.py: 1 finding unchanged (disclosed motor-superposition oracle FP on
  fault-level/us-industrial-with-motors/MCC-1).
```

- [ ] **Step 5: Validate manifest parses + run gates**

```bash
python3 -c "
import json
m = json.load(open('electrical/photometric-analysis/skill.manifest.json'))
assert m['version'] == '1.0.0'
assert m['status'] == 'production'
assert len(m['standards']) == 7
assert len(m['examples']) == 10
print(f'Manifest OK: v{m[\"version\"]} {m[\"status\"]} with {len(m[\"examples\"])} examples')"

python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -3
```

Expected:
- `Manifest OK: v1.0.0 production with 10 examples`
- `AGGREGATE: 236/236 pass (0 failures)` (unchanged)
- `TOTAL FINDINGS: 1` (unchanged)

- [ ] **Step 6: Commit A.2**

```bash
git add electrical/photometric-analysis/skill.manifest.json \
        electrical/photometric-analysis/README.md \
        electrical/photometric-analysis/CHANGELOG.md
git commit -m "$(cat <<'EOF'
feat(photometric-analysis): A.2 skill scaffolding — stub manifest → production v1.0.0

Second task of photometric-analysis v1.0 sprint. Promotes the
electrical/photometric-analysis/ stub (created 2026-05-25, v0.1.0)
to production v1.0.0 with full manifest + README + CHANGELOG.

Manifest fields populated:
- Standards stack (7 entries — BS EN 12464-1 §4.4/§6.2/§6.6/Table 5.3
  + LM-63-2002 + CIE 117 + CIBSE LG7 §6)
- produces_intents: photometric-grid v1.0.0
- consumes_intents: lighting-layout v1.x (^1.0)
- calculations: shared/calculations/lighting/lumen-grid-solver.json
- rules: 3 files (grid-spacing + ugr + ies-provenance)
- examples: 10 (3 standalone + 7 cascade retrofits) — register placeholders
  before C.1/C.2 populate; validate-examples ignores missing dirs

README rewritten with production body:
- Cascade contract documented (lighting-layout INV-11 + Wave 3/4 reuse)
- 5-input taxonomy + 9-INV validator + 5-D-check reviewer summary
- Honest disclosure section (synthetic_reference_C3 IES library +
  runtime-project-boundary deferral of calc executor)
- Pointer to design spec for locked architecture decisions

CHANGELOG.md created with v1.0.0 entry covering the full sprint scope
(scaffolding + schemas + prompts + examples + evals + cascade
integration + new shared resources + honest disclosures + gates).

Gates: validate-examples 236/236 unchanged (no example wired yet);
functional_audit 1 finding unchanged (disclosed FP).

Next: A.3 schemas (photometric-analysis-ir + photometric-grid-intent).
EOF
)"
```

---

## Task A.3: Schemas — IR + intent payload (Sonnet)

**Why Sonnet:** Mechanical JSON Schema work; spec §5.1 + §5.2 give the exact field list. No engineering judgment beyond schema-correctness + cross-skill consistency.

**Files:**
- Create: `electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json`
- Create: `electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json`

- [ ] **Step 1: Read sibling schemas for shape reference**

```bash
head -50 electrical/cable-sizing/schemas/cable-sizing-ir.schema.json
head -30 electrical/cable-sizing/schemas/cable-sizing-intent.schema.json
```

Note the `$schema` + `$id` + `title` + `description` + `type` + `required` + `properties` + `additionalProperties` discipline. The IR schema mirrors this shape.

- [ ] **Step 2: Write photometric-analysis-ir.schema.json**

Create `electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json` with this content:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json",
  "title": "Photometric Analysis IR",
  "description": "Full IR produced by photometric-analysis v1.0.0. Per-point illuminance grid + UGR results + provenance + cascade evidence. Per spec §5.1.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "mode",
    "room",
    "consumed_intents",
    "photometric_inputs",
    "calculation_summary",
    "rationale",
    "invariants"
  ],
  "additionalProperties": false,
  "properties": {
    "drawing_type": {"const": "photometric_analysis"},
    "version": {"type": "string"},
    "mode": {
      "enum": ["full_analysis", "screening_only"],
      "description": "full_analysis = per-point grid + UGR (default; production output). screening_only = scalar target-vs-predicted only (early-design Part L pre-check when IES files pending). Mirrors lighting-layout's mode: full_drawing | calc_only pattern."
    },
    "_note": {"type": "string", "description": "Optional engineer or implementer note — runtime-readable, no semantic effect."},
    "room": {
      "type": "object",
      "required": ["length_mm", "width_mm", "area_m2", "ceiling_height_mm", "room_type"],
      "additionalProperties": false,
      "properties": {
        "length_mm": {"type": "integer", "minimum": 500},
        "width_mm": {"type": "integer", "minimum": 500},
        "area_m2": {"type": "number", "exclusiveMinimum": 0},
        "ceiling_height_mm": {"type": "integer", "minimum": 2000},
        "working_plane_mm": {"type": "integer", "minimum": 0},
        "room_type": {
          "enum": [
            "open_plan_office", "private_office", "meeting_room", "corridor",
            "warehouse", "warehouse_aisle", "classroom", "consulting_room",
            "ward", "kitchen_commercial", "bathroom", "reception_lobby",
            "escape_route", "plantroom", "external",
            "drawing_office", "technical_drawing", "fine_assembly", "precision_work"
          ],
          "description": "15 lighting-layout values + 4 drawing-office-grade types per BS EN 12464-1 Table 5.3 row 5.34 (stricter UGR limit 16)."
        }
      }
    },
    "consumed_intents": {
      "type": "object",
      "required": ["lighting_layout"],
      "additionalProperties": false,
      "properties": {
        "lighting_layout": {
          "type": "object",
          "required": ["intent_version", "source_path"],
          "additionalProperties": false,
          "properties": {
            "intent_version": {"type": "string"},
            "source_path": {"type": "string", "minLength": 1},
            "consumed_summary": {
              "type": "object",
              "description": "Subset of upstream intent fields actually consumed (room dims + luminaire positions + luminaire_type symbol). Aids debugging without re-reading upstream file."
            }
          }
        }
      }
    },
    "photometric_inputs": {
      "type": "object",
      "required": ["ies_files", "grid_metadata", "reflectances"],
      "additionalProperties": false,
      "properties": {
        "ies_files": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["luminaire_type", "path", "_source", "verification_status"],
            "additionalProperties": false,
            "properties": {
              "luminaire_type": {"type": "string", "minLength": 3},
              "path": {"type": "string", "minLength": 1},
              "_source": {"type": "string", "minLength": 40},
              "verification_status": {
                "enum": ["engineer_typical_C2", "manufacturer_supplied_project_specific", "synthetic_reference_C3"]
              },
              "parsed_summary": {
                "type": "object",
                "description": "LM-63 parser summary: total_lumens, max_intensity_cd, beam_angle_deg, ies_test_distance_m. Populated by runtime calc.lumen_grid_solver parser.",
                "additionalProperties": false,
                "properties": {
                  "total_lumens": {"type": "integer"},
                  "max_intensity_cd": {"type": "number"},
                  "beam_angle_deg": {"type": "integer"},
                  "ies_test_distance_m": {"type": "number"}
                }
              }
            }
          }
        },
        "grid_metadata": {
          "type": "object",
          "required": ["task_area_bounds", "grid_spacing_mm", "grid_spacing_formula", "point_count"],
          "additionalProperties": false,
          "properties": {
            "task_area_bounds": {
              "type": "object",
              "required": ["x_min_mm", "y_min_mm", "x_max_mm", "y_max_mm"],
              "additionalProperties": false,
              "properties": {
                "x_min_mm": {"type": "integer"},
                "y_min_mm": {"type": "integer"},
                "x_max_mm": {"type": "integer"},
                "y_max_mm": {"type": "integer"}
              }
            },
            "grid_spacing_mm": {"type": "integer", "minimum": 50, "maximum": 1000},
            "grid_spacing_formula": {"type": "string", "minLength": 20},
            "point_count": {"type": "integer", "minimum": 1}
          }
        },
        "reflectances": {
          "type": "object",
          "required": ["ceiling", "wall", "floor", "_source"],
          "additionalProperties": false,
          "properties": {
            "ceiling": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "wall": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "floor": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "_source": {"type": "string", "minLength": 10}
          }
        }
      }
    },
    "calculation_summary": {
      "type": "object",
      "required": [
        "target_illuminance_lux", "uniformity_u0_target", "ugr_limit",
        "compliant", "tool_call_pending", "_calc_tool"
      ],
      "additionalProperties": false,
      "properties": {
        "target_illuminance_lux": {"type": "integer", "minimum": 1},
        "uniformity_u0_target": {"type": "number", "minimum": 0.1, "maximum": 1.0},
        "ugr_limit": {"type": "integer", "minimum": 10, "maximum": 30},
        "achieved_avg_illuminance_lux": {"type": "number"},
        "achieved_min_illuminance_lux": {"type": "number"},
        "achieved_max_illuminance_lux": {"type": "number"},
        "achieved_uniformity_u0": {"type": "number"},
        "max_ugr_across_view_positions": {"type": "number"},
        "compliant": {"type": "boolean"},
        "non_compliance_flags": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
              "message": {"type": "string"},
              "reference": {"type": "string"},
              "severity": {"enum": ["critical", "warning", "info"]}
            }
          }
        },
        "tool_call_pending": {"type": "boolean"},
        "_calc_tool": {"const": "calc.lumen_grid_solver"},
        "_calc_engine_version": {"type": "string"}
      }
    },
    "illuminance_grid": {
      "type": "array",
      "description": "Flat list of {x_mm, y_mm, illuminance_lux} per spec §5.1 + Q5 brainstorm decision. Required when mode == full_analysis; omitted when mode == screening_only.",
      "items": {
        "type": "object",
        "required": ["x_mm", "y_mm", "illuminance_lux"],
        "additionalProperties": false,
        "properties": {
          "x_mm": {"type": "integer", "minimum": 0},
          "y_mm": {"type": "integer", "minimum": 0},
          "illuminance_lux": {"type": "number", "minimum": 0}
        }
      }
    },
    "ugr_results": {
      "type": "array",
      "description": "Per-observer UGR values. Required when mode == full_analysis. Minimum 4 entries (CIE 117 defaults) plus optional engineer-supplied overrides.",
      "items": {
        "type": "object",
        "required": ["label", "position", "azimuth_deg", "ugr_value", "_source"],
        "additionalProperties": false,
        "properties": {
          "label": {"type": "string", "minLength": 1},
          "position": {
            "type": "object",
            "required": ["x_mm", "y_mm", "height_mm"],
            "additionalProperties": false,
            "properties": {
              "x_mm": {"type": "integer", "minimum": 0},
              "y_mm": {"type": "integer", "minimum": 0},
              "height_mm": {"type": "integer", "minimum": 0, "maximum": 3000}
            }
          },
          "azimuth_deg": {"type": "integer", "minimum": 0, "maximum": 359},
          "ugr_value": {"type": "number"},
          "_source": {"enum": ["cie_117_default", "engineer_supplied"]}
        }
      }
    },
    "rationale": {"$ref": "../../../shared/schemas/core/rationale.schema.json"},
    "invariants": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "passes", "severity", "evidence"],
        "properties": {
          "id": {"type": "string", "pattern": "^INV-[0-9]{2,3}$"},
          "passes": {"type": "boolean"},
          "severity": {"enum": ["critical", "high", "medium", "low"]},
          "evidence": {"type": "string", "minLength": 20, "maxLength": 800}
        }
      }
    }
  },
  "allOf": [
    {
      "description": "mode-conditional required fields per spec §5.1. full_analysis requires illuminance_grid + ugr_results; screening_only does not.",
      "if": {
        "properties": {"mode": {"const": "screening_only"}},
        "required": ["mode"]
      },
      "then": {},
      "else": {
        "required": ["illuminance_grid", "ugr_results"]
      }
    }
  ]
}
```

- [ ] **Step 3: Write photometric-grid-intent.schema.json**

Create `electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json` with this content (flat shape per spec §5.2 + B.4 fix-pass precedent):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json",
  "title": "Photometric Grid Intent Payload",
  "description": "Flat intent payload (no envelope wrap) produced by photometric-analysis v1.0.0. Consumed by lighting-layout INV-11 + emergency-lighting + daylight. Per spec §5.2.",
  "type": "object",
  "required": [
    "intent_version",
    "skill",
    "consumed_lighting_layout_intent",
    "photometric_grid"
  ],
  "additionalProperties": false,
  "properties": {
    "intent_version": {"const": "1.0.0"},
    "skill": {"const": "photometric-analysis"},
    "consumed_lighting_layout_intent": {
      "type": "string",
      "minLength": 1,
      "description": "Path to upstream lighting-layout intent-out.json that this analysis verifies."
    },
    "photometric_grid": {
      "type": "object",
      "required": [
        "achieved_avg_illuminance_lux",
        "achieved_min_illuminance_lux",
        "achieved_uniformity_u0",
        "ugr_max",
        "ugr_target",
        "uniformity_target",
        "target_illuminance_lux",
        "task_area_compliant",
        "grid_point_count",
        "ies_source_summary"
      ],
      "additionalProperties": false,
      "properties": {
        "achieved_avg_illuminance_lux": {"type": "number", "minimum": 0},
        "achieved_min_illuminance_lux": {"type": "number", "minimum": 0},
        "achieved_uniformity_u0": {"type": "number", "minimum": 0, "maximum": 1.0},
        "ugr_max": {"type": "number"},
        "ugr_target": {"type": "integer", "minimum": 10, "maximum": 30},
        "uniformity_target": {"type": "number", "minimum": 0.1, "maximum": 1.0},
        "target_illuminance_lux": {"type": "integer", "minimum": 1},
        "task_area_compliant": {"type": "boolean"},
        "grid_point_count": {"type": "integer", "minimum": 0},
        "non_compliance_flags": {
          "type": "array",
          "description": "Mirror of full-IR non_compliance_flags subset relevant to cascade consumer (INV-11 cascades flags upstream per spec §10.3 sub-check 4).",
          "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
              "message": {"type": "string"},
              "reference": {"type": "string"},
              "severity": {"enum": ["critical", "warning", "info"]}
            }
          }
        },
        "ies_source_summary": {
          "type": "object",
          "required": ["all_verified", "verification_status_lowest"],
          "additionalProperties": false,
          "properties": {
            "all_verified": {
              "type": "boolean",
              "description": "true iff every ies_files[].verification_status == manufacturer_supplied_project_specific"
            },
            "verification_status_lowest": {
              "enum": ["synthetic_reference_C3", "engineer_typical_C2", "manufacturer_supplied_project_specific"],
              "description": "Worst (lowest-confidence) verification_status across all consumed IES files. Used by reviewer D-2 to gate project-stage substitution."
            }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Validate both schemas parse + are self-consistent**

```bash
python3 -c "
import json, jsonschema
ir = json.load(open('electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json'))
intent = json.load(open('electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json'))
jsonschema.Draft7Validator.check_schema(ir)
jsonschema.Draft7Validator.check_schema(intent)
print(f'IR schema: {len(ir[\"properties\"])} top-level properties; {len(ir[\"required\"])} required')
print(f'Intent schema: {len(intent[\"properties\"])} top-level; {len(intent[\"properties\"][\"photometric_grid\"][\"properties\"])} payload fields')"
```

Expected:
- `IR schema: 11 top-level properties; 9 required`
- `Intent schema: 4 top-level; 10 payload fields`

- [ ] **Step 5: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -3
```

Expected: 236/236 unchanged + 1 finding unchanged.

- [ ] **Step 6: Commit A.3**

```bash
git add electrical/photometric-analysis/schemas/
git commit -m "$(cat <<'EOF'
feat(photometric-analysis): A.3 IR + intent payload schemas

Third task of photometric-analysis v1.0 sprint. Adds the two schemas
this skill emits + the cascade consumers (lighting-layout INV-11 +
emergency-lighting Wave 3 + daylight Wave 4) read.

photometric-analysis-ir.schema.json (full IR — ~280 lines):
- 11 top-level properties; 9 required
- additionalProperties: false enforced at root + every object block
- mode enum {full_analysis, screening_only} with allOf if/then/else
  conditional: full_analysis requires illuminance_grid + ugr_results;
  screening_only omits both (early-design Part L pre-check)
- room.room_type 19-value enum (15 lighting-layout values + 4
  drawing-office-grade per BS EN 12464-1 Table 5.3 row 5.34)
- photometric_inputs.ies_files[]._source minLength 40 + verification_status
  enum {C3 synthetic, C2 engineer_typical, manufacturer_specific}
- photometric_inputs.grid_metadata.grid_spacing_mm [50, 1000] per
  BS EN 12464-1 §6.2 formula bounds
- calculation_summary._calc_tool: "calc.lumen_grid_solver" const
- illuminance_grid: flat list of {x_mm, y_mm, illuminance_lux} per
  Q5 brainstorm decision
- ugr_results: ≥4 default + optional engineer-supplied (label, position,
  azimuth, ugr_value, _source enum)
- invariants[] standard shape (id + passes + severity + evidence)

photometric-grid-intent.schema.json (flat intent payload — ~85 lines):
- FLAT shape (no envelope wrap) per spec §5.2 + B.4 fix-pass precedent
- Required: intent_version (const 1.0.0), skill (const), consumed_lighting_layout_intent
  (path string), photometric_grid (payload object)
- payload.task_area_compliant boolean (the cascade consumer's primary signal)
- payload.non_compliance_flags[] mirrors IR for INV-11 sub-check 4
  (flag cascading)
- payload.ies_source_summary.{all_verified, verification_status_lowest}
  for reviewer D-2 gating

Gates: validate-examples 236/236 unchanged; functional_audit 1 finding
unchanged.

Next: A.4 inputs.json + 3 rules YAML files.
EOF
)"
```

---

## Task A.4: inputs.json + 3 rules YAML files (Sonnet)

**Why Sonnet:** Mechanical structural work; spec §4 gives the exact input items + rules§ inherited from the brainstorm decisions.

**Files:**
- Create: `electrical/photometric-analysis/inputs.json`
- Create: `electrical/photometric-analysis/rules/grid-spacing-rules.yaml`
- Create: `electrical/photometric-analysis/rules/ugr-rules.yaml`
- Create: `electrical/photometric-analysis/rules/ies-provenance-rules.yaml`

- [ ] **Step 1: Write inputs.json**

Create `electrical/photometric-analysis/inputs.json` with the 5 items from spec §4:

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "photometric-analysis",
  "version": "1.0.0",
  "items": [
    {
      "id": "lighting_layout_intent_path",
      "label": "Path to upstream lighting-layout intent-out.json",
      "hint": "Photometric-analysis is a downstream consumer of lighting-layout. In runtime cascade context auto-populated by manifest consumes_intents trigger; in standalone context engineer-supplied.",
      "answer_type": "text",
      "required": true,
      "validator": "non_empty_string",
      "project_fact_candidate": true
    },
    {
      "id": "photometric_ies_paths",
      "label": "IES files per luminaire type (ANSI/IES LM-63-2002 format)",
      "hint": "Required for every distinct luminaire_type.symbol in the upstream lighting-layout intent. Reference library at shared/photometric/ies/ for engineer_typical / synthetic distributions; substitute project-specific manufacturer IES before final design freeze.",
      "answer_type": "struct_list",
      "required": true,
      "item_schema": {
        "type": "object",
        "required": ["luminaire_type", "path", "_source"],
        "properties": {
          "luminaire_type": {"type": "string", "minLength": 3, "description": "Must match a luminaire_type.symbol in the upstream lighting-layout intent"},
          "path": {"type": "string", "minLength": 1, "description": "Filesystem path to LM-63-2002 IES file (typically shared/photometric/ies/<type>.ies for examples; project path for real projects)"},
          "_source": {"type": "string", "minLength": 40, "description": "Provenance: manufacturer + product code + retrieval date + verification_status caveat"}
        }
      },
      "project_fact_candidate": true
    },
    {
      "id": "ugr_view_positions_override",
      "label": "Engineer-supplied UGR observer positions (extends 4 CIE 117 defaults)",
      "hint": "Skill auto-emits 4 default observers per CIE 117 (one per wall facing inward at 1.2m). Use this field to add specific workstations / control rooms / operator chairs / display-facing observers.",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["label", "x_mm", "y_mm", "view_azimuth_deg"],
        "properties": {
          "label": {"type": "string", "minLength": 1, "description": "Unique per position (e.g. 'Operator desk A1', 'Drafting station 14 N')"},
          "x_mm": {"type": "integer", "minimum": 0},
          "y_mm": {"type": "integer", "minimum": 0},
          "height_mm": {"type": "integer", "minimum": 0, "maximum": 3000, "default": 1200, "description": "Per CIE 117 seated observer; 1500 for standing"},
          "view_azimuth_deg": {"type": "integer", "minimum": 0, "maximum": 359}
        }
      },
      "project_fact_candidate": false
    },
    {
      "id": "task_area_override",
      "label": "Task-area rectangle override (default = room interior minus 500mm perimeter border)",
      "hint": "BS EN 12464-1 §4.3 defines task area for U₀/UGR evaluation. Default = room interior minus 500mm border. Override for partial-room task areas (e.g. desk cluster in a large open office).",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["x_min_mm", "y_min_mm", "x_max_mm", "y_max_mm"],
        "properties": {
          "x_min_mm": {"type": "integer", "minimum": 0},
          "y_min_mm": {"type": "integer", "minimum": 0},
          "x_max_mm": {"type": "integer", "minimum": 0},
          "y_max_mm": {"type": "integer", "minimum": 0}
        }
      },
      "project_fact_candidate": false
    },
    {
      "id": "reflectance_override",
      "label": "Surface reflectances (default = room-type-typical from upstream lighting-layout calculation_summary.assumptions)",
      "hint": "Default reflectances ceiling/wall/floor = 0.7/0.5/0.2 for clean office (per upstream lighting-layout). Override for verified surface measurements.",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["ceiling", "wall", "floor"],
        "properties": {
          "ceiling": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "wall": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "floor": {"type": "number", "minimum": 0.0, "maximum": 1.0}
        }
      },
      "project_fact_candidate": false
    }
  ]
}
```

Note: per `shared/schemas/core/inputs.schema.json` constraints (per A.3 D3 finding), `answer_type` enum is `[enum, int, float, boolean, text, enum_list, struct_list]` — no `struct` singleton allowed. Used `struct_list` for the 3 optional struct-shaped fields with implicit 1-element semantics (engineer supplies single override entry).

- [ ] **Step 2: Write grid-spacing-rules.yaml**

Create `electrical/photometric-analysis/rules/grid-spacing-rules.yaml`:

```yaml
id: grid-spacing-rules
description: BS EN 12464-1 §6.2 adaptive grid spacing formula + per-task tolerance
_verification_status: standard_transcribed_C2
_note: "Values transcribed from published BS EN 12464-1:2021 §6.2. Cross-check against published edition before runtime use."

rules:
  - id: grid-spacing-rules#adaptive-formula
    value:
      formula: "p = 0.2 × 5^log₁₀(d/0.2)"
      d_definition: "longer task-area dimension in metres"
      p_clamp_min_mm: 50
      p_clamp_max_mm: 1000
    citation: "BS EN 12464-1:2021 §6.2 (calculation grid for indoor work places)"
    rationale: "Denser grid in smaller task areas, sparser in large open spaces. The standard's intent is per-area-dependent resolution; fixed-spacing alternatives over-sample small task areas + under-sample large ones."

  - id: grid-spacing-rules#tolerance
    value:
      tolerance_mm: 50
      description: "Implementations may round to nearest 50 mm for renderability without violating the standard"
    citation: "BS EN 12464-1:2021 §6.2 + CIBSE LG7 §6.2 implementation practice"
    rationale: "Rendered IR coordinates snap to 50 mm grid (per lighting-layout placement-rules#grid-snap). INV-5 in validator enforces match within ±50 mm of the formula output."

  - id: grid-spacing-rules#default-border
    value:
      task_area_border_mm: 500
      description: "Default task area = room interior minus 500 mm perimeter border (excludes wall-adjacent zone where photometric prediction is dominated by wall reflections)"
    citation: "BS EN 12464-1:2021 §4.3 (task area definition)"
    rationale: "Engineer overrides via inputs.task_area_override for partial-room task areas (desk cluster, control room operator station, etc.)."

  - id: grid-spacing-rules#worked-examples
    value:
      examples:
        - {room_type: open_plan_office, task_dims_m: [10, 8], computed_p_mm: 600, point_count_approx: 238}
        - {room_type: cellular_office, task_dims_m: [4, 3], computed_p_mm: 300, point_count_approx: 154}
        - {room_type: warehouse_aisle, task_dims_m: [30, 2], computed_p_mm: 850, point_count_approx: 108}
        - {room_type: corridor, task_dims_m: [20, 2], computed_p_mm: 700, point_count_approx: 87}
        - {room_type: classroom, task_dims_m: [4, 6], computed_p_mm: 400, point_count_approx: 176}
        - {room_type: drawing_office, task_dims_m: [12, 9], computed_p_mm: 650, point_count_approx: 280}
    citation: "BS EN 12464-1:2021 §6.2 formula evaluated at representative task areas"
    rationale: "Reference values for INV-5 evidence + reasoning.md cross-reference. Implementer + generator-prompt + validator all cite these to confirm formula adherence on the example layouts."
```

- [ ] **Step 3: Write ugr-rules.yaml**

Create `electrical/photometric-analysis/rules/ugr-rules.yaml`:

```yaml
id: ugr-rules
description: CIE 117 UGR observer geometry + per-room UGR limits per BS EN 12464-1 Table 5.3
_verification_status: standard_transcribed_C2
_note: "UGR limits transcribed from BS EN 12464-1:2021 Table 5.3. CIE 117 observer geometry per published standard. Engineer-of-record must verify against published editions before runtime use."

rules:
  - id: ugr-rules#default-observer-positions
    value:
      count: 4
      placement_rule: "One default observer per wall facing inward toward room centre"
      observer_height_mm: 1200
      observer_offset_from_wall_mm: 1500
      view_azimuth_per_wall:
        N: 180
        S: 0
        E: 270
        W: 90
    citation: "CIE 117 Discomfort glare in interior lighting + BS EN 12464-1:2021 §6.6 (UGR evaluation)"
    rationale: "CIE 117 specifies the standard observer geometry (1.2 m seated; observer-luminaire viewing angles drive G discomfort glare). 4 wall-facing defaults provide minimum-meaningful coverage of a rectangular room; engineer adds workstation-specific positions via inputs.ugr_view_positions_override."

  - id: ugr-rules#per-room-type-limits
    value:
      open_plan_office: 19
      private_office: 19
      meeting_room: 19
      reception_lobby: 22
      classroom: 19
      consulting_room: 19
      ward: 19
      kitchen_commercial: 22
      bathroom: 22
      corridor: 25
      warehouse: 25
      warehouse_aisle: 22
      escape_route: 25
      plantroom: 25
      external: null
      drawing_office: 16
      technical_drawing: 16
      fine_assembly: 16
      precision_work: 16
    citation: "BS EN 12464-1:2021 Table 5.3 (UGR limits per indoor work-place task)"
    rationale: "Stricter UGR limit (16) for visually demanding tasks (drawing, fine assembly, precision work) per Table 5.3 row 5.34. INV-3 + reviewer D-3 enforce. external = null (UGR not defined for outdoor spaces per BS EN 12464-1 scope)."

  - id: ugr-rules#cie-117-formula-summary
    value:
      formula: "UGR = 8 × log₁₀ [ (0.25/Lb) × Σ (L²ω/p²) ]"
      L_definition: "luminance of each glare source (cd/m²) in the field of view"
      omega_definition: "solid angle of glare source seen by observer (sr)"
      p_definition: "Guth position index per CIE 117 Annex A"
      Lb_definition: "average background luminance (cd/m²)"
    citation: "CIE 117 §3 + Annex A (Guth position index tables) + BS EN 12464-1:2021 §6.6"
    rationale: "Reference formula for generator-prompt Step 7 + validator INV-3 evidence. Runtime calc.lumen_grid_solver implements the full formula with IES luminance distribution + numerical Σ; skill emits the formula structure for engineer review."

  - id: ugr-rules#observer-geometry-honest-disclosure
    value:
      simplifications_in_synthetic_ies:
        - "Synthetic IES files (verification_status: synthetic_reference_C3) use analytical Lambertian / Gaussian distributions"
        - "UGR computed from synthetic IES is approximate-but-bounded; manufacturer-specific IES produces project-grade UGR"
        - "Engineer-of-record must substitute project IES + verify UGR against manufacturer-published values before final design freeze"
    citation: "Spec §3 honest-disclosure pattern (D2.3 + A.1 lessons)"
    rationale: "Preserves the no-fabrication discipline. INV-8 + reviewer D-2 enforce on every shipped IR."
```

- [ ] **Step 4: Write ies-provenance-rules.yaml**

Create `electrical/photometric-analysis/rules/ies-provenance-rules.yaml`:

```yaml
id: ies-provenance-rules
description: IES file _source provenance requirements + verification_status policy
_verification_status: skill_policy_C1
_note: "Skill-author policy per spec §6.1 + D2.3 honest-disclosure pattern. C1 = skill-author-declared (no external standard to transcribe)."

rules:
  - id: ies-provenance-rules#source-string-minimum
    value:
      min_length_chars: 40
      required_content:
        - "Manufacturer name OR archetype name (e.g. 'Synthetic 600x600mm recessed LED panel')"
        - "Product code OR distribution model name (e.g. 'lambertian_panel')"
        - "Retrieval / generation date OR _retrieved field cross-reference"
        - "Verification caveat OR substitution policy"
    citation: "Spec §4.2 inputs.json item_schema + §6 validator INV-8 + D2.3 honest-disclosure pattern"
    rationale: "INV-8 enforces the 40-char minimum + provenance honesty. Strings under 40 chars cannot fit all 4 required content elements; threshold catches casual / lazy provenance entries."

  - id: ies-provenance-rules#verification-status-enum
    value:
      enum:
        - synthetic_reference_C3
        - engineer_typical_C2
        - manufacturer_supplied_project_specific
      semantics:
        synthetic_reference_C3: "Generated by scripts/generate_reference_ies.py from analytical archetype (current shared library)"
        engineer_typical_C2: "Transcribed from industry-typical published reference (CIBSE LG7 illustrative tables, manufacturer datasheet aggregate)"
        manufacturer_supplied_project_specific: "Actual manufacturer LM-63 measurement for the exact project luminaire (engineer-of-record substitutes for final design freeze)"
    citation: "Spec §6.1 + §8.3 + D2.3 honest-disclosure extension"
    rationale: "Three-tier ladder per project lifecycle: C3 (skill / library default) → C2 (industry transcription) → project_specific (real manufacturer). Reviewer D-2 escalates warning level per tier when project stage advances past tender."

  - id: ies-provenance-rules#substitution-policy
    value:
      mandatory_substitution_before:
        - "Submission for building control / Part L sign-off"
        - "Any project-specific UGR / U₀ claim in a tender response"
        - "Final design freeze for construction"
      acceptable_uses_of_C3:
        - "Skill examples + cascade retrofit"
        - "Early-design photometric pre-check"
        - "Sensitivity studies + scenario comparisons"
    citation: "Spec §8.3 + shared/photometric/README.md substitution policy"
    rationale: "Preserves user-discipline boundary: synthetic refs are great for design exploration; manufacturer files are required for design accountability. Reviewer D-2 surfaces this distinction per shipped IR."
```

- [ ] **Step 5: Validate inputs.json + YAML files parse**

```bash
python3 -c "
import json, yaml, jsonschema
# inputs.json validates against inputs.schema.json
inputs_schema = json.load(open('shared/schemas/core/inputs.schema.json'))
inputs = json.load(open('electrical/photometric-analysis/inputs.json'))
jsonschema.validate(instance=inputs, schema=inputs_schema)
print(f'inputs.json valid: {len(inputs[\"items\"])} items')

# 3 rules YAML files parse + carry id + rules
for f in ['grid-spacing-rules', 'ugr-rules', 'ies-provenance-rules']:
    d = yaml.safe_load(open(f'electrical/photometric-analysis/rules/{f}.yaml'))
    assert 'id' in d and 'rules' in d
    print(f'{f}.yaml OK: id={d[\"id\"]} rules={len(d[\"rules\"])}')"
```

Expected:
- `inputs.json valid: 5 items`
- `grid-spacing-rules.yaml OK: id=grid-spacing-rules rules=4`
- `ugr-rules.yaml OK: id=ugr-rules rules=4`
- `ies-provenance-rules.yaml OK: id=ies-provenance-rules rules=3`

- [ ] **Step 6: Run golden CI gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -5
python3 functional_audit.py 2>&1 | tail -3
```

Expected: validate-examples increases by +1 (new inputs.json picked up by Pass 3) → **237/237**; functional_audit 1 finding unchanged.

If validate-examples does not increase (Pass 3 may scan a different set), confirm by checking the validator output for the photometric-analysis inputs.json reference — the gate count target adjusts per implementer's measurement.

- [ ] **Step 7: Commit A.4**

```bash
git add electrical/photometric-analysis/inputs.json \
        electrical/photometric-analysis/rules/
git commit -m "$(cat <<'EOF'
feat(photometric-analysis): A.4 inputs.json + 3 rules YAML files

Fourth task of photometric-analysis v1.0 sprint. Completes Phase A
foundations.

inputs.json (5 items per spec §4):
- lighting_layout_intent_path (required text)
- photometric_ies_paths (required struct_list — luminaire_type +
  path + _source provenance ≥40 chars)
- ugr_view_positions_override (optional struct_list — engineer adds
  workstation positions beyond 4 CIE 117 defaults)
- task_area_override (optional struct_list — partial-room task areas)
- reflectance_override (optional struct_list — verified surface
  measurements)

3 rules YAML files (zero-drift SoT pattern per D3.A.2):

grid-spacing-rules.yaml (4 rules):
- adaptive-formula: BS EN 12464-1 §6.2 p = 0.2 × 5^log₁₀(d/0.2),
  clamped [50, 1000] mm
- tolerance: ±50 mm for renderability
- default-border: 500 mm task-area perimeter exclusion
- worked-examples: 6 representative computed p values for INV-5
  evidence cross-reference

ugr-rules.yaml (4 rules):
- default-observer-positions: 4 wall-facing defaults at 1.2 m,
  1500 mm from wall, azimuth per wall (CIE 117 + BS EN 12464-1 §6.6)
- per-room-type-limits: 19-value enum (15 lighting-layout + 4
  drawing-office-grade with stricter limit 16 per Table 5.3 row 5.34)
- cie-117-formula-summary: UGR = 8 log₁₀ [(0.25/Lb) × Σ(L²ω/p²)]
  reference for generator Step 7 + validator INV-3
- observer-geometry-honest-disclosure: synthetic IES UGR is
  approximate-bounded; project IES required for accountability

ies-provenance-rules.yaml (3 rules):
- source-string-minimum: 40 chars + 4 required content elements
  (manufacturer/archetype + product/model + date + caveat)
- verification-status-enum: C3 synthetic / C2 engineer_typical /
  manufacturer_specific 3-tier ladder
- substitution-policy: when C3 acceptable vs when project_specific
  mandatory (building control / Part L / final design freeze)

Gates: validate-examples +1 (Pass 3 picks up new inputs.json) →
expected 237/237; functional_audit 1 finding unchanged.

Phase A complete. Next: B.1 generator prompt (~600 lines).
EOF
)"
```

---
