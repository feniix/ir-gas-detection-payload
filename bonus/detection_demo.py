"""Synthetic frames + detection pipeline demo for methane OGI.

Implements the narrowed bonus scope from the plan (U4 + U5):

- A synthetic thermal-frame generator producing buoyant Gaussian-blob plumes
  against a static-with-perturbation background. Intensities are calibrated to
  apparent-ΔT (mK) using the same Beer-Lambert relation as `contrast_simulation`.
- A representative subset of the detection pipeline: rolling-median temporal
  background, frame differencing, spatial smoothing, adaptive thresholding,
  and connected-components blob extraction. (Full 12-stage pipeline is in the
  report's appendix; this demo runs the load-bearing core.)
- A precision/recall benchmark across three scenarios (easy / medium / hard).
- Before/after still PNGs saved for embedding in the report's appendix.

The benchmark numbers are explicitly framed (per origin R36) as a controlled-
conditions sanity check on synthetic data — NOT a field-performance claim.

Run:
    uv run python detection_demo.py

Tests:
    uv run pytest tests/test_detection_demo.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from contrast_simulation import ALPHA_LWIR, apparent_dT


# ---------------------------------------------------------------------------
# Scenario specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Scenario:
    """Synthetic-clip configuration."""

    name: str
    n_frames: int = 60
    width: int = 320
    height: int = 256
    fps: int = 30  # nominal — only for latency reporting

    # Plume parameters (apparent-ΔT mK at peak; plume itself is a Gaussian)
    plume_CL: float = 1000.0  # ppm·m at peak
    plume_dT: float = 5.0  # K, scene thermal differential
    plume_alpha: float = ALPHA_LWIR  # absorption coefficient at filter
    plume_start_xy: tuple[int, int] = (160, 200)  # (x, y) in image coords
    plume_drift: tuple[float, float] = (0.0, -1.5)  # (dx, dy) px / frame
    plume_sigma_initial: float = 8.0  # px
    plume_sigma_growth: float = 0.05  # px / frame (buoyant spreading)
    plume_appears_at_frame: int = 0  # plume invisible before this

    # Background and perturbation
    bg_offset_mK: float = 0.0  # constant baseline in mK (ΔT relative to ambient)
    bg_gradient_amplitude: float = 100.0  # mK across the frame
    sensor_noise_mK: float = 40.0  # NETD-equivalent per-pixel noise (uncooled)
    perturbation: Literal["none", "turbulence", "static_distractor"] = "none"
    perturbation_amplitude: float = 0.0  # mK

    # Reproducibility
    seed: int = 42


@dataclass
class GroundTruth:
    """Per-frame ground-truth bounding boxes (None = plume invisible)."""

    bbox_per_frame: list[tuple[int, int, int, int] | None] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Synthetic scene generation
# ---------------------------------------------------------------------------


def _gaussian_blob(
    height: int, width: int, cx: float, cy: float, sigma: float, amplitude: float
) -> np.ndarray:
    """Render a 2D Gaussian into an array of shape (height, width)."""
    y, x = np.mgrid[0:height, 0:width]
    return amplitude * np.exp(
        -((x - cx) ** 2 + (y - cy) ** 2) / (2.0 * sigma**2)
    )


def _bbox_from_centroid(
    cx: float, cy: float, sigma: float, height: int, width: int
) -> tuple[int, int, int, int] | None:
    """Bounding box at ~2σ around (cx, cy), clipped to the frame."""
    half = max(1, int(round(2.0 * sigma)))
    x0 = max(0, int(round(cx - half)))
    y0 = max(0, int(round(cy - half)))
    x1 = min(width, int(round(cx + half)))
    y1 = min(height, int(round(cy + half)))
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, y0, x1, y1)


def generate_scene(scenario: Scenario) -> tuple[np.ndarray, GroundTruth]:
    """Produce a (T, H, W) array of apparent-ΔT (mK) and ground-truth bboxes."""
    rng = np.random.default_rng(scenario.seed)
    H, W = scenario.height, scenario.width
    T = scenario.n_frames

    # --- Static background: smooth gradient + offset
    yy = np.linspace(-1.0, 1.0, H)
    xx = np.linspace(-1.0, 1.0, W)
    grad = scenario.bg_gradient_amplitude * (yy[:, None] * 0.6 + xx[None, :] * 0.4)
    background = scenario.bg_offset_mK + grad

    # --- Static distractor (pre-computed once, added every frame)
    distractor = np.zeros_like(background)
    if scenario.perturbation == "static_distractor":
        # Hot patch in upper-right of frame
        distractor = _gaussian_blob(
            H, W, cx=W * 0.75, cy=H * 0.30, sigma=6.0,
            amplitude=scenario.perturbation_amplitude,
        )

    # --- Per-frame turbulence: low-pass-filtered noise that varies over time
    if scenario.perturbation == "turbulence":
        # Generate a "turbulence cube" of low-pass noise. Sigma chosen so the
        # spatial structure is coarse (matches real plume background fluctuation),
        # and the time axis varies gradually.
        raw = rng.standard_normal(size=(T, H, W)).astype(np.float32)
        turb_cube = np.empty_like(raw)
        for t in range(T):
            turb_cube[t] = ndimage.gaussian_filter(raw[t], sigma=3.0)
        # Normalize and scale
        turb_cube = (turb_cube - turb_cube.mean()) / (turb_cube.std() + 1e-9)
        turb_cube *= scenario.perturbation_amplitude
    else:
        turb_cube = None

    frames = np.empty((T, H, W), dtype=np.float32)
    bboxes: list[tuple[int, int, int, int] | None] = []

    # Use the same Beer-Lambert linearization as contrast_simulation.apparent_dT
    # so the demo and the simulation are mathematically locked together.
    plume_amplitude_mK = (
        apparent_dT(scenario.plume_alpha, scenario.plume_CL, scenario.plume_dT)
        * 1000.0
    )

    for t in range(T):
        frame = background.copy() + distractor

        # Per-pixel sensor noise
        frame += rng.normal(0.0, scenario.sensor_noise_mK, size=(H, W))

        # Turbulence
        if turb_cube is not None:
            frame += turb_cube[t]

        # Plume
        bbox: tuple[int, int, int, int] | None = None
        if scenario.plume_CL > 0 and t >= scenario.plume_appears_at_frame:
            t_active = t - scenario.plume_appears_at_frame
            cx = scenario.plume_start_xy[0] + scenario.plume_drift[0] * t_active
            cy = scenario.plume_start_xy[1] + scenario.plume_drift[1] * t_active
            sigma = (
                scenario.plume_sigma_initial
                + scenario.plume_sigma_growth * t_active
            )
            blob = _gaussian_blob(H, W, cx, cy, sigma, plume_amplitude_mK)
            frame += blob
            bbox = _bbox_from_centroid(cx, cy, sigma, H, W)

        frames[t] = frame
        bboxes.append(bbox)

    return frames, GroundTruth(bbox_per_frame=bboxes)


# ---------------------------------------------------------------------------
# Detection pipeline
# ---------------------------------------------------------------------------


@dataclass
class DetectionPipeline:
    """Temporal-differencing + spatial-smoothing + adaptive-threshold + CC.

    Threshold is median + k · MAD · 1.4826 (the robust 1-sigma estimator),
    which keeps the plume's own contribution from biasing the spread
    estimate the way median + k · std does.
    """

    window_frames: int = 30
    threshold_k: float = 4.5  # multiplier on robust 1-sigma estimate
    min_blob_pixels: int = 12
    max_blob_pixels: int = 5000
    smoothing_sigma: float = 1.5

    def process(
        self, frames: np.ndarray
    ) -> list[list[tuple[int, int, int, int]]]:
        """Process a (T, H, W) frame stack into per-frame bbox lists."""
        T = frames.shape[0]
        detections: list[list[tuple[int, int, int, int]]] = []

        for t in range(T):
            if t < self.window_frames:
                detections.append([])
                continue

            window = frames[t - self.window_frames : t]
            background_est = np.median(window, axis=0)
            diff = frames[t] - background_est

            # Smooth diff to reduce per-pixel noise
            smoothed = ndimage.gaussian_filter(diff, sigma=self.smoothing_sigma)

            # Robust adaptive threshold using MAD (Gaussian consistency factor 1.4826)
            med = float(np.median(smoothed))
            mad = float(np.median(np.abs(smoothed - med)))
            sigma_est = 1.4826 * mad
            thresh = med + self.threshold_k * sigma_est
            mask = smoothed > thresh

            labeled, num = ndimage.label(mask)
            per_frame: list[tuple[int, int, int, int]] = []
            for label_id in range(1, num + 1):
                blob_mask = labeled == label_id
                size = int(blob_mask.sum())
                if size < self.min_blob_pixels or size > self.max_blob_pixels:
                    continue
                ys, xs = np.where(blob_mask)
                bbox = (
                    int(xs.min()),
                    int(ys.min()),
                    int(xs.max()) + 1,
                    int(ys.max()) + 1,
                )
                per_frame.append(bbox)
            detections.append(per_frame)

        return detections


# ---------------------------------------------------------------------------
# Precision / recall metric
# ---------------------------------------------------------------------------


def _iou(
    box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]
) -> float:
    ax0, ay0, ax1, ay1 = box_a
    bx0, by0, bx1, by1 = box_b
    inter_x0 = max(ax0, bx0)
    inter_y0 = max(ay0, by0)
    inter_x1 = min(ax1, bx1)
    inter_y1 = min(ay1, by1)
    if inter_x1 <= inter_x0 or inter_y1 <= inter_y0:
        return 0.0
    inter = (inter_x1 - inter_x0) * (inter_y1 - inter_y0)
    area_a = (ax1 - ax0) * (ay1 - ay0)
    area_b = (bx1 - bx0) * (by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _centroid_in_bbox(
    detection: tuple[int, int, int, int], gt_bbox: tuple[int, int, int, int]
) -> bool:
    """True if the detection's centroid is inside the ground-truth bbox."""
    dx0, dy0, dx1, dy1 = detection
    cx = (dx0 + dx1) / 2.0
    cy = (dy0 + dy1) / 2.0
    gx0, gy0, gx1, gy1 = gt_bbox
    return gx0 <= cx < gx1 and gy0 <= cy < gy1


def precision_recall(
    detections: list[list[tuple[int, int, int, int]]],
    ground_truth: GroundTruth,
    iou_threshold: float = 0.3,
    warmup_frames: int = 0,
    match_strategy: Literal["iou", "centroid_in_bbox"] = "iou",
) -> dict[str, float]:
    """Compute precision and recall over a clip's detections.

    Two matching strategies:

    - ``iou``: a detection matches if its IoU with the GT bbox >= threshold.
      Suitable for tightly-bounded objects where bbox-to-bbox match makes
      sense (vehicles, faces, sharp-edged targets).
    - ``centroid_in_bbox``: a detection matches if its centroid falls inside
      the GT bbox. Better for OGI plume detection, where the detected blob
      is the *core* of the plume (where signal exceeds threshold) and the GT
      bbox is the full plume extent (~2σ). The pipeline has correctly
      *localized* the plume even when the detected core is smaller than GT.

    Frames before ``warmup_frames`` are excluded.
    """
    tp = 0
    fp = 0
    fn = 0
    for t, (per_frame, gt_bbox) in enumerate(
        zip(detections, ground_truth.bbox_per_frame)
    ):
        if t < warmup_frames:
            continue
        if gt_bbox is None:
            fp += len(per_frame)
            continue
        if not per_frame:
            fn += 1
            continue
        if match_strategy == "iou":
            best_match = max(_iou(d, gt_bbox) for d in per_frame)
            matched = best_match >= iou_threshold
        else:  # centroid_in_bbox
            matched = any(_centroid_in_bbox(d, gt_bbox) for d in per_frame)
        if matched:
            tp += 1
            fp += len(per_frame) - 1
        else:
            fn += 1
            fp += len(per_frame)

    precision = 1.0 if (tp + fp) == 0 else tp / (tp + fp)
    recall = 1.0 if (tp + fn) == 0 else tp / (tp + fn)
    return {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn}


# ---------------------------------------------------------------------------
# Benchmark scenarios
# ---------------------------------------------------------------------------


SCENARIOS: list[Scenario] = [
    # Easy: well above floor, no perturbation. Demonstrates the pipeline works
    # cleanly under good conditions — high precision and recall.
    Scenario(
        name="easy",
        n_frames=90,
        width=320,
        height=256,
        plume_CL=8000.0,
        plume_dT=10.0,
        plume_start_xy=(160, 200),
        plume_drift=(0.0, -1.0),
        perturbation="none",
        seed=101,
    ),
    # Medium: lower CL and ΔT, with light turbulence. Demonstrates that the
    # pipeline still works under degraded background conditions.
    Scenario(
        name="medium",
        n_frames=90,
        width=320,
        height=256,
        plume_CL=4000.0,
        plume_dT=8.0,
        plume_start_xy=(160, 200),
        plume_drift=(0.2, -1.0),
        perturbation="turbulence",
        perturbation_amplitude=60.0,
        seed=102,
    ),
    # Hard: plume genuinely near or below the detection floor with heavy
    # turbulence. Demonstrates graceful degradation — pipeline misses
    # detections rather than fabricating them. Recall expected to be near 0;
    # precision high (no false positives on noise alone).
    Scenario(
        name="hard",
        n_frames=90,
        width=320,
        height=256,
        plume_CL=1200.0,
        plume_dT=4.0,
        plume_start_xy=(160, 200),
        plume_drift=(0.4, -0.8),
        perturbation="turbulence",
        perturbation_amplitude=120.0,
        seed=103,
    ),
]


def _save_still_frame(
    frame: np.ndarray,
    detections: list[tuple[int, int, int, int]],
    output: Path,
    title: str,
    ground_truth_bbox: tuple[int, int, int, int] | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(6.0, 4.5), dpi=120)
    img = ax.imshow(frame, cmap="inferno", vmin=-200, vmax=600)
    fig.colorbar(img, ax=ax, label="apparent ΔT (mK)")
    if ground_truth_bbox is not None:
        x0, y0, x1, y1 = ground_truth_bbox
        ax.add_patch(
            plt.Rectangle(
                (x0, y0), x1 - x0, y1 - y0,
                linewidth=1.0, edgecolor="cyan", facecolor="none",
                linestyle=":", label="ground truth",
            )
        )
    for x0, y0, x1, y1 in detections:
        ax.add_patch(
            plt.Rectangle(
                (x0, y0), x1 - x0, y1 - y0,
                linewidth=1.5, edgecolor="lime", facecolor="none",
                label="detection",
            )
        )
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    if detections or ground_truth_bbox is not None:
        # Dedupe legend labels
        handles, labels = ax.get_legend_handles_labels()
        seen: dict[str, object] = {}
        for h, l in zip(handles, labels):
            if l not in seen:
                seen[l] = h
        ax.legend(seen.values(), seen.keys(), loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", dpi=120)
    plt.close(fig)


def main(outputs_dir: Path | None = None) -> None:
    """Run all scenarios, write benchmark JSON and before/after stills."""
    if outputs_dir is None:
        outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    matplotlib.rcParams["svg.hashsalt"] = "methane-ogi-2026-05-08"

    results: dict[str, dict[str, float]] = {}
    easy_artifacts: tuple[np.ndarray, GroundTruth, list[list[tuple[int, int, int, int]]]] | None = None
    still_idx = 60  # frame index for the still-frame export (after warmup)

    pipeline = DetectionPipeline()

    for scenario in SCENARIOS:
        frames, gt = generate_scene(scenario)

        t0 = time.perf_counter()
        detections = pipeline.process(frames)
        elapsed = time.perf_counter() - t0
        per_frame_ms = elapsed * 1000.0 / scenario.n_frames

        metrics = precision_recall(
            detections,
            gt,
            warmup_frames=pipeline.window_frames,
            match_strategy="centroid_in_bbox",
        )
        results[scenario.name] = metrics
        # Latency is reported to stdout only — not in the JSON, since wall-clock
        # measurement varies run-to-run and breaks artifact reproducibility.
        print(
            f"[{scenario.name}] mean per-frame latency: {per_frame_ms:.2f} ms "
            f"(measured on host; report cites Jetson-Orin-Nano-class numbers)"
        )

        if scenario.name == "easy":
            easy_artifacts = (frames, gt, detections)

    # Save before/after stills from the easy scenario, where detection fires
    # reliably — illustrates the pipeline working as designed.
    if easy_artifacts is not None:
        frames, gt, detections = easy_artifacts
        _save_still_frame(
            frame=frames[still_idx],
            detections=[],
            output=outputs_dir / "frame_pre_detection.png",
            title=f"Synthetic frame — raw thermal (easy scenario, frame {still_idx})",
            ground_truth_bbox=gt.bbox_per_frame[still_idx],
        )
        _save_still_frame(
            frame=frames[still_idx],
            detections=detections[still_idx],
            output=outputs_dir / "frame_post_detection.png",
            title=f"Synthetic frame — pipeline detection overlaid (easy, frame {still_idx})",
            ground_truth_bbox=gt.bbox_per_frame[still_idx],
        )

    # Write benchmark JSON with stable key order for determinism
    output = {
        "preamble": (
            "Precision/recall reported below is a controlled-conditions sanity "
            "check on synthetic frames generated by the same Beer-Lambert model "
            "the detection pipeline implicitly recovers. These numbers are NOT "
            "a field-performance claim. Real-OGI performance must be validated "
            "on field data — explicit future work per origin requirement R36."
        ),
        "pipeline_config": {
            "window_frames": pipeline.window_frames,
            "threshold_k": pipeline.threshold_k,
            "min_blob_pixels": pipeline.min_blob_pixels,
            "smoothing_sigma": pipeline.smoothing_sigma,
        },
        "scenarios": {name: results[name] for name in ["easy", "medium", "hard"]},
    }
    (outputs_dir / "benchmark_results.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n"
    )
    print(f"Wrote {outputs_dir / 'benchmark_results.json'}")
    print(f"Wrote {outputs_dir / 'frame_pre_detection.png'}")
    print(f"Wrote {outputs_dir / 'frame_post_detection.png'}")


if __name__ == "__main__":
    main()
