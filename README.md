# Methane OGI EO Payload Technical Assignment

Submission package for the EO Payload for Gas Detection assignment, framed as a system-engineering deliverable rather than a sensor-only trade study.

## Primary deliverable

- **`methane-ogi-payload-report.md`** — technical report (10-15 pages target). §1-§4 mission, physics, and the cooled-MWIR vs uncooled-LWIR trade-off; §5-§7 architecture, optics, detection algorithm; §8 modeled performance; §9 conclusion. Appendices A-D inline (simulation methodology, 12-stage algorithm, figure index, references).

## Supporting documents (separate files to keep the main report at envelope)

- `docs/technical-assignment.md` — transcribed original assignment prompt.
- `docs/appendix-e-low-level-platforms.md` — sensor bus, RT scheduling, drivers, DMA, MCU partition, bring-up tooling.
- `docs/appendix-f-verification.md` — V&V matrix V1-V14 (CL_min, day/night, latency, mass/power, vibration, calibration, registration, NUC recovery, fleet MTBF).
- `docs/appendix-g-diagnostics.md` — telemetry, fault modes / fallbacks, field-support workflow.
- `figures/` — renderer-safe PNG block diagrams / sketches.
- `bonus/` — runnable simulation, detection-algorithm demo, support data.

## Recommended reading order

1. `docs/technical-assignment.md` for the assignment scope.
2. `methane-ogi-payload-report.md` for the technical response.
3. `docs/appendix-e-low-level-platforms.md` / `docs/appendix-f-verification.md` / `docs/appendix-g-diagnostics.md` for the system-engineering layer.
4. `bonus/README.md` to run the simulation, demo, and test suites; `bonus/data/low-level-talking-points.md` is the interview cheat sheet that pairs with Appendix E.

## Run the bonus code

```sh
cd bonus
uv sync
uv run python contrast_simulation.py
uv run python detection_demo.py
uv run pytest tests/
```

Expected test status: `47 passed`.

## Generated / included artifacts

- `bonus/outputs/plot_apparent_dT_vs_CL.png`
- `bonus/outputs/plot_CL_min_vs_dT.png`
- `bonus/outputs/frame_pre_detection.png`
- `bonus/outputs/frame_post_detection.png`
- `bonus/outputs/benchmark_results.json`
- `figures/block-diagram.png`
- `figures/optical-path.png`
- `figures/fov-gsd-geometry.png`
- `figures/detection-pipeline.png`

## Rendering the report

```sh
pandoc methane-ogi-payload-report.md -o report.pdf --pdf-engine=weasyprint
```

For the compact 10-15 page layout matching the assignment's page envelope, render with the project's CSS (Letter, 0.7"/0.85" margins, 10.5pt body):

```sh
pandoc methane-ogi-payload-report.md -o report.pdf --pdf-engine=weasyprint --css=docs/compact.css
```
