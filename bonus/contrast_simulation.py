"""Contrast-vs-CL simulation for methane OGI trade-off (cooled MWIR vs uncooled LWIR).

Produces two plots that ground the report's §4 Trade-off and §8 Performance
Estimation sections:

(a) Apparent ΔT seen by the camera vs methane column density CL, for both
    3.3 µm MWIR and 7.7-8.0 µm LWIR narrowband filters at scene ΔT of
    3 K, 5 K, and 10 K. Horizontal effective-NETD lines are overlaid for
    cooled MWIR (~25 mK) and uncooled LWIR with warm-filter penalty (~50 mK).

(b) Minimum detectable column density CL_min vs scene ΔT for both
    technologies, showing the regimes where each wins on raw sensitivity.

Constants come from facts.md (cited numbers source-of-truth) under bonus/data/.
The simulation uses simplified Beer-Lambert with engineering-calibrated,
band-integrated absorption coefficients — NOT line-by-line radiative transfer.
Atmospheric transmittance is not modeled in this script; the report folds
τ_atm into effective NETD in the worked altitude table.

Run:
    uv run python contrast_simulation.py

Tests:
    uv run pytest tests/test_contrast_simulation.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless rendering — no display needed for plot generation
import matplotlib.pyplot as plt
import numpy as np
from scipy import constants


# ---------------------------------------------------------------------------
# Working calibration constants (from facts.md)
# ---------------------------------------------------------------------------

#: Filter-weighted methane absorption coefficient over a 3.2-3.4 µm narrowband
#: passband, in units of (ppm·m)⁻¹. Engineering calibration chosen so that
#: with NETD = 25 mK and scene ΔT = 5 K, CL_min lands near the
#: literature-reported ~200 ppm·m floor for cooled MWIR OGI.
ALPHA_MWIR: float = 2.5e-5

#: Filter-weighted methane absorption coefficient over a 7.7-8.0 µm narrowband
#: passband, in units of (ppm·m)⁻¹. Calibrated so that the operational
#: cooled-MWIR / uncooled-LWIR CL_min ratio at typical ΔT lands at ~5×, not the
#: ~16-25× implied by naive peak-line band-strength ratios. The MWIR/LWIR
#: absorption ratio is treated as a few× engineering assumption pending
#: line-by-line passband integration; folding NETD asymmetry in operational
#: space gives the ~5× total gap.
ALPHA_LWIR: float = 1.0e-5

#: Cooled MWIR working NETD (K). Range 15-25 mK in modern detectors; we use the
#: upper edge as a conservative working value.
NETD_COOLED: float = 25e-3

#: Uncooled LWIR bare-sensor NETD (K). Modern 12 µm pitch VOx microbolometers
#: deliver < 40 mK at f/1.0, 25-60 Hz, 300 K (Raytron OHLE3123 datasheet).
NETD_UNCOOLED_BARE: float = 40e-3

#: Uncooled LWIR effective NETD with warm-filter penalty (K). The narrowband
#: filter at 7.7-8.0 µm sits warm in the optical train and adds shot noise
#: from its own self-emission that NUC cannot fully remove. The penalty
#: bumps effective NETD from 40 mK to ~50 mK as a working assumption.
NETD_UNCOOLED_PENALIZED: float = 50e-3

#: Background scene temperature (K). Roughly 15 °C — typical North-American
#: surface temperature for methane LDAR survey conditions.
T_BG_DEFAULT: float = 288.0


# ---------------------------------------------------------------------------
# Beer-Lambert and contrast formation
# ---------------------------------------------------------------------------


def transmittance(alpha: float, column_density: float) -> float:
    """Beer-Lambert transmittance through a methane column.

    Args:
        alpha: filter-weighted absorption coefficient, (ppm·m)⁻¹.
        column_density: methane column density, ppm·m.

    Returns:
        τ = exp(-α · CL), in [0, 1].
    """
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative, got {alpha}")
    if column_density < 0:
        raise ValueError(f"column_density must be non-negative, got {column_density}")
    return math.exp(-alpha * column_density)


def apparent_dT(alpha: float, column_density: float, scene_dT: float) -> float:
    """Apparent ΔT seen by a thermal camera through a methane plume.

    In the linearized small-ΔT regime where the Planck dB/dT factor cancels
    between numerator and denominator (NEDL = NETD · dB/dT, ΔL = (1-τ) · ΔT
    · dB/dT), apparent_dT reduces to (1 - τ(λ)) · scene_dT.

    Args:
        alpha: filter-weighted absorption coefficient, (ppm·m)⁻¹.
        column_density: methane column density, ppm·m.
        scene_dT: thermal differential between gas and background, K.
            Positive when gas is warmer than background (emissive contrast),
            negative when gas is cooler (absorptive contrast).

    Returns:
        Apparent ΔT, K. Same sign as scene_dT.
    """
    return (1.0 - transmittance(alpha, column_density)) * scene_dT


def CL_min(alpha: float, scene_dT: float, netd: float) -> float:
    """Minimum detectable column density.

    Solves apparent_dT(CL_min) = NETD for CL_min, returning the column density
    at which the camera's apparent contrast matches its noise floor.

    Args:
        alpha: filter-weighted absorption coefficient, (ppm·m)⁻¹.
        scene_dT: thermal differential between gas and background, K.
            Magnitude is what matters; sign is dropped.
        netd: noise-equivalent temperature difference (effective NETD, K).

    Returns:
        CL_min in ppm·m. Returns math.inf if scene |ΔT| ≤ NETD (cannot
        detect — gas would have to fully absorb to be visible, which the
        linearized model treats as unreachable).
    """
    abs_dT = abs(scene_dT)
    if abs_dT <= netd:
        return math.inf
    # apparent_dT(CL_min) = NETD
    # (1 - exp(-α·CL_min)) · |ΔT| = NETD
    # exp(-α·CL_min) = 1 - NETD/|ΔT|
    # CL_min = -ln(1 - NETD/|ΔT|) / α
    return -math.log(1.0 - netd / abs_dT) / alpha


# ---------------------------------------------------------------------------
# Planck radiance — for radiometric sanity checks
# ---------------------------------------------------------------------------


def planck_radiance(wavelength_um: float, temperature_K: float) -> float:
    """Spectral radiance from a blackbody, W / (m² · sr · µm).

    Args:
        wavelength_um: wavelength, µm.
        temperature_K: blackbody temperature, K.

    Returns:
        Spectral radiance B(λ, T) at the given wavelength and temperature.
    """
    h = constants.h  # Planck constant
    c = constants.c  # speed of light
    k = constants.k  # Boltzmann constant
    wavelength_m = wavelength_um * 1e-6
    # Standard Planck spectral radiance (per unit wavelength):
    # B = 2hc² / λ⁵ · 1 / (exp(hc/λkT) - 1)
    exponent = h * c / (wavelength_m * k * temperature_K)
    radiance_per_m = (
        2.0 * h * c**2 / wavelength_m**5 / (math.expm1(exponent))
    )
    # Convert from "per meter" wavelength to "per micrometer"
    return radiance_per_m * 1e-6


# ---------------------------------------------------------------------------
# Plot generation
# ---------------------------------------------------------------------------


def _plot_apparent_dT_vs_CL(outputs_dir: Path) -> Path:
    """Plot (a): apparent ΔT vs column density for both bands at multiple ΔT."""
    cl_grid = np.logspace(1, 5, 400)  # 10 to 100,000 ppm·m
    scene_dT_values = [3.0, 5.0, 10.0]
    band_styles = {
        "MWIR (3.3 µm), cooled": (ALPHA_MWIR, "tab:red", "-"),
        "LWIR (7.7-8.0 µm), uncooled": (ALPHA_LWIR, "tab:blue", "--"),
    }

    fig, ax = plt.subplots(figsize=(8.0, 5.5), dpi=120)
    for label, (alpha, color, linestyle) in band_styles.items():
        for scene_dT in scene_dT_values:
            apparent = np.array(
                [apparent_dT(alpha, cl, scene_dT) for cl in cl_grid]
            ) * 1000.0  # convert K -> mK for plot readability
            ax.loglog(
                cl_grid,
                apparent,
                color=color,
                linestyle=linestyle,
                alpha=0.5 + 0.15 * scene_dT_values.index(scene_dT),
                label=f"{label}, ΔT={scene_dT:.0f} K",
            )

    # NETD reference lines
    ax.axhline(
        NETD_COOLED * 1000,
        color="tab:red",
        linestyle=":",
        alpha=0.7,
        label=f"NETD cooled MWIR ({NETD_COOLED * 1000:.0f} mK)",
    )
    ax.axhline(
        NETD_UNCOOLED_PENALIZED * 1000,
        color="tab:blue",
        linestyle=":",
        alpha=0.7,
        label=(
            f"NETD uncooled LWIR + warm filter "
            f"({NETD_UNCOOLED_PENALIZED * 1000:.0f} mK)"
        ),
    )

    ax.set_xlabel("Methane column density CL (ppm·m)")
    ax.set_ylabel("Apparent ΔT seen by camera (mK)")
    ax.set_title(
        "Apparent ΔT vs column density — cooled MWIR (3.3 µm) vs uncooled LWIR (7.6-8.0 µm)"
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower right", ncol=2)
    fig.tight_layout()

    output = outputs_dir / "plot_apparent_dT_vs_CL.png"
    fig.savefig(output, bbox_inches="tight", dpi=120)
    plt.close(fig)
    return output


def _plot_CL_min_vs_dT(outputs_dir: Path) -> Path:
    """Plot (b): CL_min vs scene ΔT for both technologies."""
    dT_grid = np.linspace(0.5, 15.0, 200)

    cl_min_cooled = np.array([CL_min(ALPHA_MWIR, dT, NETD_COOLED) for dT in dT_grid])
    cl_min_uncooled_bare = np.array(
        [CL_min(ALPHA_LWIR, dT, NETD_UNCOOLED_BARE) for dT in dT_grid]
    )
    cl_min_uncooled_pen = np.array(
        [CL_min(ALPHA_LWIR, dT, NETD_UNCOOLED_PENALIZED) for dT in dT_grid]
    )

    fig, ax = plt.subplots(figsize=(8.0, 5.5), dpi=120)
    ax.semilogy(
        dT_grid,
        cl_min_cooled,
        color="tab:red",
        linewidth=2.0,
        label="Cooled MWIR (3.3 µm), NETD = 25 mK",
    )
    ax.semilogy(
        dT_grid,
        cl_min_uncooled_bare,
        color="tab:blue",
        linewidth=1.5,
        linestyle="--",
        alpha=0.7,
        label="Uncooled LWIR (bare sensor), NETD = 40 mK",
    )
    ax.semilogy(
        dT_grid,
        cl_min_uncooled_pen,
        color="tab:blue",
        linewidth=2.0,
        label="Uncooled LWIR + warm filter, NETD = 50 mK",
    )

    # Annotate the operational ratio at ΔT = 5 K
    cooled_at_5 = CL_min(ALPHA_MWIR, 5.0, NETD_COOLED)
    uncooled_at_5 = CL_min(ALPHA_LWIR, 5.0, NETD_UNCOOLED_PENALIZED)
    ratio = uncooled_at_5 / cooled_at_5
    ax.annotate(
        f"At ΔT = 5 K: uncooled / cooled ≈ {ratio:.1f}×",
        xy=(5.0, uncooled_at_5),
        xytext=(7.5, 4_000),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="0.4", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="0.6"),
    )
    ax.axvline(5.0, color="0.7", linestyle=":", linewidth=0.8, alpha=0.6)

    ax.set_xlabel("Scene thermal differential ΔT (K)")
    ax.set_ylabel("Minimum detectable column density CL_min (ppm·m)")
    ax.set_title(
        "Operational sensitivity floor — CL_min vs scene ΔT (Beer-Lambert, "
        "filter-weighted α)"
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_xlim(0, 15)
    ax.set_ylim(50, 5e4)
    fig.tight_layout()

    output = outputs_dir / "plot_CL_min_vs_dT.png"
    fig.savefig(output, bbox_inches="tight", dpi=120)
    plt.close(fig)
    return output


def main(outputs_dir: Path | None = None) -> None:
    """Entry point — generate both plots into outputs_dir.

    Args:
        outputs_dir: directory to write PNGs to. Defaults to ./outputs/
            relative to this file. Created if it doesn't exist.
    """
    if outputs_dir is None:
        outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Determinism: fix matplotlib's hash randomness via fixed RC params
    matplotlib.rcParams["svg.hashsalt"] = "methane-ogi-2026-05-08"

    plot_a = _plot_apparent_dT_vs_CL(outputs_dir)
    plot_b = _plot_CL_min_vs_dT(outputs_dir)

    print(f"Wrote {plot_a}")
    print(f"Wrote {plot_b}")


if __name__ == "__main__":
    main()
