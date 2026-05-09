# Appendix G — Calibration, Diagnostics, and Field Support

*Supporting material for `methane-ogi-payload-report.md`. A deployed payload accumulates calibration drift and hits operational fault modes; this appendix names the telemetry the system exposes, the fault modes it handles, and the field-support workflow.*

**Telemetry signals** (operator sees green / amber / red status, not raw values):

| Signal | Working range | Action threshold |
|---|---|---|
| Filter / FPA temperature | 15-35 °C ambient drift | Auto-NUC at filter Δ ≥ 1 °C; warn at FPA > 50 °C |
| NUC event log | Vendor- and warm-up-dependent; initial planning range ~5-30 s | Alarm on runaway cadence after vendor stability limits are characterized |
| Dropped-frame counter | Illustrative target < 0.1% | Warn / degrade thresholds tuned from flight tests and operator tolerance |
| Processor load | Per-frame ≤ 25 ms at 30 Hz | Warn > 28 ms; fall back 60 Hz → 30 Hz |
| Cross-modal sync residual | Stretch target ≤ 1 thermal pixel RMS | Warn > 2-3 px RMS for > 2 s until field data tightens threshold |
| Radio link quality | Platform-specific RSSI / FER / packet-loss metrics | Metadata-only fallback when video QoS threatens alarm delivery |
| GPS / RTK fix | RTK fixed/float status + correction age + estimated accuracy/covariance | Fall back with time-limited dead reckoning and uncertainty-tagged position |
| Payload power draw | Steady ≤ 12 W; ≤ 18 W transient | Warn > 14 W sustained |

**Fault modes** with graceful degradation — none brick the payload:

| Fault | Detection | Fallback |
|---|---|---|
| Visible camera unavailable | SNR below threshold ≥ 1 s | Thermal-only registration with IMU prior (§5.5); overlay drops visible background |
| IMU / GPS dropout | Watchdog timeout or fix-quality drop ≥ 2 s | Last-known position + dead reckoning; mark "estimated"; thermal self-registration |
| Processor overload | Per-frame > 28 ms for ≥ 5 frames | 60 Hz → 30 Hz; drop cross-modal refinement; IMU-only registration |
| Filter / FPA thermal drift | FPA outside 15-35 °C or filter Δ > 5 °C | Increase NUC cadence; suspend alarms if NUC > 1 / 2 s (radiometry untrusted) |
| Radio link degradation | RSSI / FER thresholds for ≥ 2 s | Drop video; retain alarm metadata + telemetry; on-board log if metadata also fails |

The on-board detection pipeline keeps running through every fault; degraded modes degrade the operator's *visibility into* the payload, not the payload's ability to detect.

**Field-support workflow**: a pre-flight bring-up script verifies FPA + filter temperature, NUC, GPS / RTK, radio link, and runs a synthetic-frame self-test (single green / amber / red status); in-flight, amber is advisory and red triggers an audible alert with recommended action ("RTL — link degraded", "Pause survey — thermal drift outside envelope"); post-flight, telemetry + detection-track + fault-event logs are pulled via wired interface for after-action review; calibration cadence is factory radiometric on receipt, field cross-modal extrinsic re-cal after sensor-head impact, automatic routine NUC, depot major recal.
