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
