# Appendix F — System Integration and Verification Plan

*Supporting material for `methane-ogi-payload-report.md`. The recommendation in §4 is conditional on the system meeting §2.3 performance targets, the §5.2 SWaP budget, and §6 / §8 modeled physics. Each pass criterion below is tagged by source: **A** assignment requirement, **M** modeled estimate from §3-§8, **B** engineering budget declared in §5, **P** proposed verification target this plan introduces.*

| ID | Requirement / target | Pass criterion | Source | Verification method |
|---|---|---|---|---|
| V1 | CL_min at the design point | Within ±20% of §8.1 model at 50 / 100 / 200 m, ΔT = 5 K | M | Controlled-release |
| V2 | Day/night operation | Pipeline produces alarm overlay in daylight (visible-fused) and night (thermal-only fallback per §5.5); auto-transitions on visible-stream SNR drop | A | Bench + tethered hover at dawn / dusk |
| V3 | Alarm latency | 95th percentile event-to-overlay ≤ 200 ms; ≤ 250 ms during NUC-suppression windows | B | Bench, hardware-timestamped frames |
| V4 | Payload mass | ≤ 2.0 kg integrated, with mounting hardware | B | Bench at integration |
| V5 | Payload power | ≤ 12 W steady at 25 °C; ≤ 18 W transient | B | Bench measurement |
| V6 | Frame rate | Sustains 30 Hz; adaptive 60 Hz → 30 Hz; never below 15 Hz | B | Bench, induced load |
| V7 | Operator overlay content | Timestamp + GPS + persistence + confidence on every alarm | A | Bench + flight |
| V8 | MTBF, component-level | ≥ 5 000 h via MIL-HDBK-217F or Telcordia stack-up | M | Modeled at design review |
| V9 | False-positive rate | ≤ 1 alarm / 10 min over 30 min controlled survey across 5 curated FP sources, zero release | P | Controlled-scene flight, manual ground truth |
| V10 | Vibration tolerance | Detection metrics within 10% of static-bench under a tailored Method 514-style vibration profile derived from the selected airframe spectrum | P | Airframe vibration survey + shaker-table bench |
| V11 | Calibration stability | Filter center-λ / passband shift stays inside methane-band budget across f/# cone, field angle, and -10 to +40 °C; eff-NETD within §6.3 ±10 mK envelope | P | Optical bench + thermal-chamber + ambient-extreme controlled-release |
| V12 | Cross-modal registration | Stretch: ≤ 1 thermal-pixel RMS at 50 m; acceptable prototype range: ≤ 1-3 px with confidence metadata, tightened after flight data | P | Bench + tethered hover |
| V13 | NUC-event recovery | Detection re-converges within one rolling-window length (1-2 s) post-NUC; no false alarms in suppression window | P | Bench, scripted NUC events |
| V14 | Fleet MTBF | ≥ 5 000 flight hours demonstrated after 12-month deployment | P | Fleet (operational data) |

V1-V8 derive from existing assumptions; V9-V14 are bars the prototype must clear during hardening. A failing V1 does not invalidate §4 — it re-opens the assumption stack (α, NETD, τ_atm, plume geometry) and tightens the model before re-flight.
