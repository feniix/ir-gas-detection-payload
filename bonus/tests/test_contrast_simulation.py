"""Tests for bonus.contrast_simulation.

Test-first development. The simulation must produce numbers and plots that
back the report's trade-off section. Behavioral assertions here pin down the
math; the script's main() entry point is tested via plot-file presence and
deterministic re-runs.

Working absorption coefficients (facts.md §6) — not measured here, just used
as the sanity-check inputs the simulation should accept:

- α_MWIR ≈ 2.5e-5 per ppm·m (3.2-3.4 µm passband, filter-weighted)
- α_LWIR ≈ 1.0e-5 per ppm·m (7.7-8.0 µm passband, filter-weighted)

NETD working values (facts.md §3, §6):
- Cooled MWIR: 25 mK
- Uncooled LWIR bare sensor: 40 mK
- Uncooled LWIR with warm-filter penalty: 50 mK

These calibrations land CL_min(cooled, ΔT=5K) ≈ 200 ppm·m and
CL_min(uncooled-with-penalty, ΔT=5K) ≈ 1000 ppm·m — i.e. the operational
gap is ~5-6× under the engineering calibration, not the ~16-25× implied by
peak-line-ratio shorthand. That's the credibility-multiplier story the
simulation should uphold.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

import contrast_simulation as cs


# ---------------------------------------------------------------------------
# Beer-Lambert transmittance
# ---------------------------------------------------------------------------


class TestTransmittance:
    def test_zero_column_density_gives_full_transmittance(self):
        # With no gas in the column, the camera sees the background unattenuated.
        assert cs.transmittance(alpha=2.5e-5, column_density=0.0) == pytest.approx(1.0)

    def test_large_column_density_approaches_zero_transmittance(self):
        # Very thick column → nearly opaque.
        result = cs.transmittance(alpha=2.5e-5, column_density=1e7)
        assert result < 1e-50

    def test_small_column_density_linearizes_to_alpha_CL(self):
        # For α·CL << 1, (1 - τ) ≈ α·CL. This is the regime the report's
        # CL_min approximation lives in. The linearization carries an
        # x²/2 second-order term, so we allow ~1% relative error here.
        alpha = 2.5e-5
        CL = 100.0  # ppm·m, deep in the small-CL regime
        one_minus_tau = 1.0 - cs.transmittance(alpha=alpha, column_density=CL)
        assert one_minus_tau == pytest.approx(alpha * CL, rel=1e-2)

    def test_negative_column_density_raises(self):
        with pytest.raises(ValueError):
            cs.transmittance(alpha=2.5e-5, column_density=-1.0)

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            cs.transmittance(alpha=-1e-5, column_density=100.0)


# ---------------------------------------------------------------------------
# Apparent ΔT — the contrast quantity the camera actually sees
# ---------------------------------------------------------------------------


class TestApparentDT:
    def test_zero_scene_contrast_gives_zero_apparent_dT(self):
        # With T_gas == T_bg, no contrast can form regardless of CL.
        result = cs.apparent_dT(alpha=2.5e-5, column_density=10_000.0, scene_dT=0.0)
        assert result == pytest.approx(0.0)

    def test_zero_column_density_gives_zero_apparent_dT(self):
        # Without any gas, the camera sees only the background — no contrast.
        result = cs.apparent_dT(alpha=2.5e-5, column_density=0.0, scene_dT=5.0)
        assert result == pytest.approx(0.0)

    def test_apparent_dT_is_linear_in_small_CL(self):
        # In the small-CL regime, apparent_dT ≈ α·CL·ΔT.  Same x²/2
        # second-order tolerance budget as the transmittance linearization
        # test above (~1% relative error).
        alpha = 2.5e-5
        CL = 200.0  # ppm·m
        scene_dT = 5.0  # K
        expected = alpha * CL * scene_dT
        actual = cs.apparent_dT(alpha=alpha, column_density=CL, scene_dT=scene_dT)
        assert actual == pytest.approx(expected, rel=1e-2)

    def test_apparent_dT_saturates_at_scene_dT(self):
        # As CL → ∞, every photon at λ_filter gets absorbed and the camera sees
        # gas radiance at T_gas — apparent ΔT → scene ΔT.
        alpha = 2.5e-5
        scene_dT = 5.0  # K
        actual = cs.apparent_dT(alpha=alpha, column_density=1e7, scene_dT=scene_dT)
        assert actual == pytest.approx(scene_dT, rel=1e-3)

    def test_negative_scene_dT_returns_negative_apparent_dT(self):
        # Plume cooler than background → absorptive (negative) contrast.
        result = cs.apparent_dT(alpha=2.5e-5, column_density=200.0, scene_dT=-5.0)
        assert result < 0
        # Symmetry check: |apparent_dT(-ΔT)| == apparent_dT(+ΔT)
        positive = cs.apparent_dT(alpha=2.5e-5, column_density=200.0, scene_dT=5.0)
        assert abs(result) == pytest.approx(positive, rel=1e-9)


# ---------------------------------------------------------------------------
# CL_min — the minimum detectable column density
# ---------------------------------------------------------------------------


class TestCLMin:
    def test_CL_min_at_threshold_produces_apparent_dT_equal_to_NETD(self):
        # By definition, apparent_dT(CL_min) == NETD.
        alpha = 2.5e-5
        scene_dT = 5.0
        netd = 25e-3
        cl_min = cs.CL_min(alpha=alpha, scene_dT=scene_dT, netd=netd)
        recovered = cs.apparent_dT(
            alpha=alpha, column_density=cl_min, scene_dT=scene_dT
        )
        assert recovered == pytest.approx(netd, rel=1e-9)

    def test_CL_min_diverges_when_scene_dT_below_NETD(self):
        # If scene contrast is below the noise floor, no CL can produce a
        # detectable signal — CL_min is infinite.
        cl_min = cs.CL_min(alpha=2.5e-5, scene_dT=10e-3, netd=25e-3)
        assert math.isinf(cl_min)

    def test_CL_min_at_NETD_equal_to_scene_dT_diverges(self):
        # Exact threshold case — gas would have to fully absorb to be detected.
        cl_min = cs.CL_min(alpha=2.5e-5, scene_dT=25e-3, netd=25e-3)
        assert math.isinf(cl_min)

    def test_lower_NETD_gives_lower_CL_min(self):
        # Sanity ordering: a quieter sensor sees thinner plumes.
        kwargs = dict(alpha=2.5e-5, scene_dT=5.0)
        assert cs.CL_min(netd=25e-3, **kwargs) < cs.CL_min(netd=40e-3, **kwargs)

    def test_higher_alpha_gives_lower_CL_min(self):
        # Sanity ordering: stronger absorption gives lower detection floor.
        kwargs = dict(scene_dT=5.0, netd=40e-3)
        assert cs.CL_min(alpha=2.5e-5, **kwargs) < cs.CL_min(alpha=1.0e-5, **kwargs)

    def test_higher_scene_dT_gives_lower_CL_min(self):
        # Sanity ordering: more thermal differential makes thin plumes visible.
        kwargs = dict(alpha=2.5e-5, netd=25e-3)
        assert cs.CL_min(scene_dT=10.0, **kwargs) < cs.CL_min(scene_dT=3.0, **kwargs)

    def test_CL_min_linearized_approximation_holds_in_small_dT_regime(self):
        # When α·CL_min << 1, CL_min ≈ NETD / (α · ΔT).
        alpha = 2.5e-5
        scene_dT = 5.0
        netd = 25e-3
        cl_min = cs.CL_min(alpha=alpha, scene_dT=scene_dT, netd=netd)
        approx = netd / (alpha * scene_dT)
        # Within 1% in this regime
        assert cl_min == pytest.approx(approx, rel=0.01)


# ---------------------------------------------------------------------------
# The credibility multiplier — operational MWIR/LWIR gap
# ---------------------------------------------------------------------------


class TestOperationalGap:
    """The simulation's primary load-bearing claim for the report's §4 trade-off.

    With facts.md §6 calibrations, the operational CL_min gap between cooled
    MWIR and uncooled LWIR (with warm-filter penalty) at typical ΔT should
    land at ~5-6×. The brainstorm's assumed ~16-25× gap was based on the
    peak-line absorption-ratio shorthand.
    """

    def test_mwir_floor_at_5K_dT_lands_near_200_ppm_m(self):
        # Cooled MWIR working calibration: should give the literature-anchored
        # ~100-500 ppm·m floor (Stanford Ravikumar, GF320-class).
        cl_min = cs.CL_min(alpha=cs.ALPHA_MWIR, scene_dT=5.0, netd=cs.NETD_COOLED)
        assert 100.0 < cl_min < 300.0

    def test_lwir_floor_at_5K_dT_with_warm_filter_lands_near_1000_ppm_m(self):
        # Uncooled LWIR with warm-filter NETD penalty: ~1000 ppm·m at 5 K ΔT.
        cl_min = cs.CL_min(
            alpha=cs.ALPHA_LWIR, scene_dT=5.0, netd=cs.NETD_UNCOOLED_PENALIZED
        )
        assert 800.0 < cl_min < 1500.0

    def test_operational_gap_is_between_4x_and_8x(self):
        # The credibility multiplier: real operational gap is ~5×, NOT the
        # ~16-25× the brainstorm assumed from peak-line absorption.
        mwir = cs.CL_min(alpha=cs.ALPHA_MWIR, scene_dT=5.0, netd=cs.NETD_COOLED)
        lwir = cs.CL_min(
            alpha=cs.ALPHA_LWIR, scene_dT=5.0, netd=cs.NETD_UNCOOLED_PENALIZED
        )
        ratio = lwir / mwir
        assert 4.0 < ratio < 8.0

    def test_warm_filter_penalty_raises_uncooled_floor(self):
        # The warm-filter NETD penalty should make uncooled detection
        # quantifiably worse than the bare-sensor case.
        bare = cs.CL_min(
            alpha=cs.ALPHA_LWIR, scene_dT=5.0, netd=cs.NETD_UNCOOLED_BARE
        )
        penalized = cs.CL_min(
            alpha=cs.ALPHA_LWIR, scene_dT=5.0, netd=cs.NETD_UNCOOLED_PENALIZED
        )
        assert penalized > bare


# ---------------------------------------------------------------------------
# Planck radiance — for the appendix figures
# ---------------------------------------------------------------------------


class TestPlanck:
    def test_planck_at_300K_peak_near_9_7_micron(self):
        # Wien displacement: λ_max · T = 2898 µm·K → at 300 K, λ_max ≈ 9.66 µm.
        wavelengths = np.linspace(2.0, 20.0, 1000)
        radiances = np.array([cs.planck_radiance(w, 300.0) for w in wavelengths])
        peak_wavelength = wavelengths[radiances.argmax()]
        assert 9.4 < peak_wavelength < 10.0

    def test_planck_radiance_at_3p3_micron_300K_smaller_than_at_7p6_micron(self):
        # The Wien-displacement asymmetry is what motivates uncooled-LWIR.
        b_3p3 = cs.planck_radiance(3.3, 300.0)
        b_7p6 = cs.planck_radiance(7.6, 300.0)
        # At room-temperature scenes, the LWIR band has substantially more flux.
        assert b_7p6 > 10 * b_3p3

    def test_planck_radiance_increases_with_temperature(self):
        # Stefan-Boltzmann sanity: hotter blackbody radiates more at every λ.
        assert cs.planck_radiance(7.6, 350.0) > cs.planck_radiance(7.6, 300.0)

    def test_planck_radiance_positive(self):
        assert cs.planck_radiance(7.6, 300.0) > 0


# ---------------------------------------------------------------------------
# Determinism + plot generation (integration test)
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    def test_main_writes_both_required_plots(self, tmp_path: Path):
        # The simulation must produce the two plots the report's §4 and §8 cite.
        outputs_dir = tmp_path / "outputs"
        cs.main(outputs_dir=outputs_dir)
        assert (outputs_dir / "plot_apparent_dT_vs_CL.png").exists()
        assert (outputs_dir / "plot_CL_min_vs_dT.png").exists()

    def test_main_is_deterministic(self, tmp_path: Path):
        # Two runs in the same locked environment produce byte-identical PNGs;
        # cross-platform bitwise identity is not claimed in the docs.
        out_a = tmp_path / "run_a"
        out_b = tmp_path / "run_b"
        cs.main(outputs_dir=out_a)
        cs.main(outputs_dir=out_b)
        bytes_a = (out_a / "plot_apparent_dT_vs_CL.png").read_bytes()
        bytes_b = (out_b / "plot_apparent_dT_vs_CL.png").read_bytes()
        assert bytes_a == bytes_b

        bytes_a = (out_a / "plot_CL_min_vs_dT.png").read_bytes()
        bytes_b = (out_b / "plot_CL_min_vs_dT.png").read_bytes()
        assert bytes_a == bytes_b
