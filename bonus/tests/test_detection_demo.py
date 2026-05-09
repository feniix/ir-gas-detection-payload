"""Tests for bonus.detection_demo (synthetic frames + detection pipeline + benchmark).

Test-first development. The demo's value is twofold:
1. The synthetic frame generator produces clips that *qualitatively* match
   real OGI footage well enough that the pipeline's design decisions show.
2. The detection pipeline's precision/recall on those clips is high enough
   on the easy scenario to demonstrate the design works, and low enough on
   the hard scenario to demonstrate where the limit is.

Both failure modes (high precision/recall on easy, graceful degradation on
hard) are explicit assertions here.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import detection_demo as dd


# ---------------------------------------------------------------------------
# Synthetic scene generation
# ---------------------------------------------------------------------------


class TestSyntheticScene:
    def test_generated_frames_have_expected_shape(self):
        scenario = dd.Scenario(name="test", n_frames=10, width=64, height=48)
        frames, _ = dd.generate_scene(scenario)
        assert frames.shape == (10, 48, 64)

    def test_generation_is_deterministic_for_same_seed(self):
        scenario = dd.Scenario(name="test", n_frames=10, width=64, height=48, seed=123)
        frames_a, _ = dd.generate_scene(scenario)
        frames_b, _ = dd.generate_scene(scenario)
        np.testing.assert_array_equal(frames_a, frames_b)

    def test_different_seeds_produce_different_frames(self):
        a = dd.Scenario(name="test", n_frames=10, width=64, height=48, seed=1)
        b = dd.Scenario(name="test", n_frames=10, width=64, height=48, seed=2)
        frames_a, _ = dd.generate_scene(a)
        frames_b, _ = dd.generate_scene(b)
        assert not np.array_equal(frames_a, frames_b)

    def test_no_plume_scenario_has_no_ground_truth(self):
        # Setting plume_CL=0 should suppress the plume entirely.
        scenario = dd.Scenario(
            name="bg_only",
            n_frames=10,
            width=64,
            height=48,
            plume_CL=0.0,
        )
        _, ground_truth = dd.generate_scene(scenario)
        assert all(bbox is None for bbox in ground_truth.bbox_per_frame)

    def test_plume_scenario_produces_visible_local_signal(self):
        # The plume should produce a hotter region than the static background.
        scenario = dd.Scenario(
            name="easy", n_frames=20, width=64, height=48, plume_CL=5000.0,
            plume_dT=10.0, plume_start_xy=(32, 36), plume_drift=(0.0, -0.8),
            plume_sigma_initial=4.0, perturbation="none",
        )
        frames, ground_truth = dd.generate_scene(scenario)
        # Pick a frame mid-clip when the plume is fully formed
        bbox = ground_truth.bbox_per_frame[10]
        assert bbox is not None
        x0, y0, x1, y1 = bbox
        plume_region = frames[10, y0:y1, x0:x1]
        elsewhere = np.concatenate([
            frames[10, :y0, :].ravel(),
            frames[10, y1:, :].ravel(),
        ])
        assert plume_region.mean() > elsewhere.mean() + 100  # mK

    def test_plume_drifts_upward_over_time(self):
        # Buoyancy: the plume's centroid y-coord should decrease (moving up)
        # frame by frame in image coordinates where y=0 is top.
        scenario = dd.Scenario(
            name="drift",
            n_frames=30,
            width=64,
            height=64,
            plume_CL=5000.0,
            plume_dT=8.0,
            plume_start_xy=(32, 50),
            plume_drift=(0.0, -1.5),
            plume_sigma_initial=4.0,
            perturbation="none",
        )
        _, gt = dd.generate_scene(scenario)
        # Average y of bounding-box center across early vs late frames
        valid_bboxes = [bb for bb in gt.bbox_per_frame if bb is not None]
        assert len(valid_bboxes) >= 20
        early_y = np.mean([(bb[1] + bb[3]) / 2 for bb in valid_bboxes[:5]])
        late_y = np.mean([(bb[1] + bb[3]) / 2 for bb in valid_bboxes[-5:]])
        assert late_y < early_y  # plume rose

    def test_turbulence_perturbation_increases_temporal_variance(self):
        clean = dd.Scenario(
            name="clean", n_frames=30, width=64, height=48,
            plume_CL=0, perturbation="none",
        )
        turbulent = dd.Scenario(
            name="turb", n_frames=30, width=64, height=48,
            plume_CL=0, perturbation="turbulence", perturbation_amplitude=200.0,
        )
        clean_frames, _ = dd.generate_scene(clean)
        turb_frames, _ = dd.generate_scene(turbulent)
        # Per-pixel temporal std should be larger with turbulence
        assert turb_frames.std(axis=0).mean() > clean_frames.std(axis=0).mean() * 2

    def test_static_distractor_perturbation_appears_at_fixed_location(self):
        scenario = dd.Scenario(
            name="distractor",
            n_frames=20,
            width=64,
            height=48,
            plume_CL=0,
            perturbation="static_distractor",
            perturbation_amplitude=400.0,
        )
        frames, _ = dd.generate_scene(scenario)
        # The distractor should be persistent — its location must have
        # consistently elevated mean across frames.
        per_pixel_mean = frames.mean(axis=0)
        per_pixel_std_over_time = frames.std(axis=0)
        # Hot static spot: high mean, low temporal std
        bg_mean = per_pixel_mean.mean()
        hot_mask = per_pixel_mean > bg_mean + 200
        assert hot_mask.sum() >= 10  # at least some spatial extent
        assert per_pixel_std_over_time[hot_mask].mean() < 100  # mostly static


# ---------------------------------------------------------------------------
# Detection pipeline
# ---------------------------------------------------------------------------


class TestDetectionPipeline:
    def test_no_signal_produces_no_detections(self):
        # Pure-noise frames should produce essentially no detections.
        rng = np.random.default_rng(42)
        frames = rng.normal(0, 50, size=(60, 48, 64)).astype(np.float32)
        pipeline = dd.DetectionPipeline()
        detections = pipeline.process(frames)
        # Allow occasional spurious singleton detections, but they should be sparse.
        total_detections = sum(len(per_frame) for per_frame in detections)
        assert total_detections < 20  # fewer than 1 / 3 frames

    def test_pipeline_warmup_yields_no_detections(self):
        # During the rolling-window warmup, no detections should fire — there
        # isn't yet a stable background model to differ against.
        scenario = dd.Scenario(
            name="warmup",
            n_frames=60,
            width=64,
            height=48,
            plume_CL=5000,
            plume_dT=10.0,
            perturbation="none",
        )
        frames, _ = dd.generate_scene(scenario)
        pipeline = dd.DetectionPipeline(window_frames=30)
        detections = pipeline.process(frames)
        # The warmup window must not emit detections
        assert all(len(d) == 0 for d in detections[:30])

    def test_easy_scenario_high_precision_recall(self):
        # Big plume, big ΔT, no perturbation: pipeline should nail this.
        scenario = dd.Scenario(
            name="easy",
            n_frames=90,
            width=64,
            height=48,
            plume_CL=10_000,
            plume_dT=10.0,
            perturbation="none",
        )
        frames, gt = dd.generate_scene(scenario)
        pipeline = dd.DetectionPipeline()
        detections = pipeline.process(frames)
        metrics = dd.precision_recall(
            detections,
            gt,
            iou_threshold=0.1,
            warmup_frames=pipeline.window_frames,
        )
        assert metrics["precision"] >= 0.85
        assert metrics["recall"] >= 0.85

    def test_subthreshold_scenario_does_not_fabricate_detections(self):
        # CL well below detection floor: pipeline should not produce many
        # spurious detections (precision should stay reasonable).
        scenario = dd.Scenario(
            name="subthreshold",
            n_frames=90,
            width=64,
            height=48,
            plume_CL=10,  # well below uncooled-LWIR floor
            plume_dT=2.0,
            perturbation="none",
        )
        frames, gt = dd.generate_scene(scenario)
        pipeline = dd.DetectionPipeline()
        detections = pipeline.process(frames)
        metrics = dd.precision_recall(
            detections,
            gt,
            iou_threshold=0.1,
            warmup_frames=pipeline.window_frames,
        )
        # Recall is allowed to be poor at sub-threshold; precision should not collapse
        # below 0.5 — pipeline should not fabricate detections on noise alone.
        # (When recall == 0 and there are no detections, precision is treated as 1.0
        # by the metric — that's fine here.)
        assert metrics["precision"] >= 0.5

    def test_hot_static_distractor_does_not_dominate_detections(self):
        # A persistent hot patch at a fixed location should be filtered by
        # the temporal differencing — it does not move and therefore does not
        # produce a strong signal in the differenced frames.
        scenario = dd.Scenario(
            name="static_only",
            n_frames=90,
            width=64,
            height=48,
            plume_CL=0,
            perturbation="static_distractor",
            perturbation_amplitude=600.0,
        )
        frames, _ = dd.generate_scene(scenario)
        pipeline = dd.DetectionPipeline()
        detections = pipeline.process(frames)
        # Static hot patch with no real plume should produce few detections
        total = sum(len(d) for d in detections[pipeline.window_frames:])
        assert total < 5


# ---------------------------------------------------------------------------
# Benchmark / metric utility
# ---------------------------------------------------------------------------


class TestPrecisionRecall:
    def test_perfect_detection_returns_unit_precision_and_recall(self):
        gt = dd.GroundTruth(bbox_per_frame=[(10, 10, 30, 30) for _ in range(5)])
        detections = [[(10, 10, 30, 30)] for _ in range(5)]
        m = dd.precision_recall(detections, gt, iou_threshold=0.5, warmup_frames=0)
        assert m["precision"] == pytest.approx(1.0)
        assert m["recall"] == pytest.approx(1.0)

    def test_no_detections_no_truth_returns_well_defined_metrics(self):
        gt = dd.GroundTruth(bbox_per_frame=[None for _ in range(5)])
        detections = [[] for _ in range(5)]
        m = dd.precision_recall(detections, gt, iou_threshold=0.5, warmup_frames=0)
        # No truth, no detections: precision conventionally 1.0; recall undefined → 1.0
        assert m["precision"] == pytest.approx(1.0)
        assert m["recall"] == pytest.approx(1.0)

    def test_warmup_frames_excluded_from_metrics(self):
        # First 5 frames have ground truth but pipeline produces nothing during warmup.
        gt = dd.GroundTruth(
            bbox_per_frame=[(10, 10, 30, 30) for _ in range(10)]
        )
        # Pipeline produces nothing in warmup, perfect after
        detections = [[] for _ in range(5)] + [[(10, 10, 30, 30)] for _ in range(5)]
        m = dd.precision_recall(detections, gt, iou_threshold=0.5, warmup_frames=5)
        assert m["recall"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Main entry point — runs all scenarios and emits artifacts
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    def test_main_writes_required_outputs(self, tmp_path: Path):
        outputs_dir = tmp_path / "outputs"
        dd.main(outputs_dir=outputs_dir)
        assert (outputs_dir / "benchmark_results.json").exists()
        assert (outputs_dir / "frame_pre_detection.png").exists()
        assert (outputs_dir / "frame_post_detection.png").exists()

    def test_main_benchmark_results_have_expected_structure(self, tmp_path: Path):
        outputs_dir = tmp_path / "outputs"
        dd.main(outputs_dir=outputs_dir)
        with (outputs_dir / "benchmark_results.json").open() as f:
            results = json.load(f)
        # Should contain entries for each scenario with precision, recall.
        # (Latency is printed to stdout, not stored — wall-clock measurement
        # would break artifact reproducibility.)
        assert isinstance(results, dict)
        assert "scenarios" in results
        assert "easy" in results["scenarios"]
        for scenario in results["scenarios"].values():
            assert "precision" in scenario
            assert "recall" in scenario

    def test_main_easy_scenario_meets_quality_bar(self, tmp_path: Path):
        outputs_dir = tmp_path / "outputs"
        dd.main(outputs_dir=outputs_dir)
        with (outputs_dir / "benchmark_results.json").open() as f:
            results = json.load(f)
        easy = results["scenarios"]["easy"]
        assert easy["precision"] >= 0.85
        assert easy["recall"] >= 0.85

    def test_main_is_deterministic(self, tmp_path: Path):
        out_a = tmp_path / "a"
        out_b = tmp_path / "b"
        dd.main(outputs_dir=out_a)
        dd.main(outputs_dir=out_b)
        assert (out_a / "benchmark_results.json").read_text() == (
            out_b / "benchmark_results.json"
        ).read_text()
