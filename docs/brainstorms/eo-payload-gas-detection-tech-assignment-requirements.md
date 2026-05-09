---
date: 2026-05-08
topic: eo-payload-gas-detection-tech-assignment
---

# EO Payload for Methane Gas Detection — Tech Assignment Report

## Summary

A 12-14 page interview deliverable defending an **uncooled LWIR + LWIR-band narrowband filter (7.7-8.0 µm passband; centroid resolved per optical-section analysis) EO payload on a small UAV** for methane OGI visualization-grade detection at 50-150 m (200 m marginal under favorable ΔT), with cooled MWIR named explicitly as the conditional alternative. Written as a practical product memo (vendor-agnostic, deployment-focused, regulatory-aware) with a Python bonus: a contrast-vs-column-density simulation and a focused detection-pipeline demo on synthetic frames.

---

## Problem Frame

The author is preparing a technical-assignment submission for an interview at an oil & gas / methane-monitoring company. The assignment asks for a complete EO payload design for remote gas detection at 50-200 m with day/night outdoor operation, on a small UAV or fixed ground station, and demands a defended trade-off between cooled MWIR and uncooled LWIR. The author is newer to EO/IR — strong on engineering thinking, less practiced with NETD math, Beer-Lambert reasoning, and the OGI domain conventions. The risk is producing a generic systems report that does not demonstrate domain fluency: missing the methane absorption-band reasoning, naming a recommendation that reads as the textbook answer rather than the deployable answer, and treating the trade-off section as a list rather than as the spine of the report. The cost is failing to convert in a domain where the evaluator is likely a senior EO/payload engineer who will probe for depth.

---

## Actors

- A1. **Author**: writes the report; needs the document to land defensible engineering decisions in language they can defend live in interview.
- A2. **Evaluator**: senior EO / payload engineer at a methane-monitoring company; reads for depth of EO understanding, system thinking, trade-off clarity, practical realism, and clear engineering communication.

---

## Requirements

**Framing & narrative arc**

- R1. The report opens with an explicit recommendation: uncooled LWIR + LWIR-band narrowband filter (7.7-8.0 µm passband as the working assumption; specific centroid is resolved in §6 from filter-weighted absorption-vs-water-vapor analysis) on a small UAV for visualization-grade methane detection across 50-200 m. The executive summary names a working envelope of effective utility (e.g., 50-150 m nominal, 200 m marginal under ≥ 5 K ΔT) rather than implying flat performance across the range. The recommendation appears in the executive summary on page 1, not buried in a conclusion.
- R2. The report is written as a practical product memo: operational framing in intro/conclusion (mission, regulatory environment, deployable reality), rigorous engineering in the body sections (physics, trade-off, performance math, algorithm).
- R3. Superseded by final precedent strategy: hardware is still proposed by spec class rather than as a vendor SKU, but named products are allowed as clearly caveated public precedents (e.g., FLIR GF77/GF77a and MFE Detect LW) where they support architecture/platform claims.
- R4. The cooled-vs-uncooled trade-off section is placed *before* the payload architecture section, so the architecture flows as a consequence of the technology choice rather than feeling pre-decided.
- R5. The report has a single, named target reader: a senior EO/payload engineer at a methane-monitoring operation. Tone calibrates to that audience — no over-teaching of fundamentals, no unexplained jargon.

**Detection physics content**

- R6. The physics section establishes Beer-Lambert (τ = exp(-α·CL)) and the contrast-formation mechanism with both signs: gas hotter than background → emissive contrast; gas cooler than background → absorptive contrast; gas equal to background → zero contrast. The thermal-differential requirement is named explicitly as a real operational constraint of OGI (typically ≥ 2-3 K).
- R7. The physics section identifies methane's two usable absorption bands — the ν₃ asymmetric C-H stretch near 3.3 µm (MWIR, strongest) and the ν₄ bending mode near 7.6-7.9 µm (LWIR, weaker) — and grounds the band choice for the chosen filter in a *filter-weighted integrated-absorption* comparison computed from public spectral data (HITRAN or PNNL), not in an asserted ratio. Later fact-checking superseded the initial ~10× brainstorm shorthand: the final report uses a few× engineering ratio and names line-by-line passband integration as radiometric-design follow-up.
- R8. The physics section explains via Wien's law that 300 K backgrounds peak near 9.7 µm, motivating uncooled bolometers in LWIR (photon-rich) and cooled photon detectors in MWIR (photon-poor at room-temperature scenes).
- R9. The physics section presents the minimum-detectable-column-density relation CL_min ∝ NETD / [α(λ) · ΔT] explicitly, naming the three knobs (sensor noise, absorption strength, thermal differential) the rest of the report will trade against each other.

**Cooled vs uncooled trade-off**

- R10. The trade-off section compares both technologies across at minimum: NETD, absorption coefficient at the operating filter wavelength, spatial resolution / pixel pitch, temporal response (combining time-constant and frame rate), SWaP, cost (order-of-magnitude), MTBF / cooler reliability, cool-down time / instant-on, solar-contamination susceptibility (with an explicit distinction between band-integrated solar radiance vs specular-glint pixel saturation, and which one a narrowband filter actually mitigates), and vibration tolerance (with an explicit distinction between cryocooler bearing wear vs bolometer thermal-smear under high-frequency vibration, and which dominates at small-UAV vibration spectra).
- R11. The comparison includes a quantitative table populated with engineering-estimate ranges (not vendor specs), with a short footnote stating the assumptions and citing public literature (HITRAN, PNNL, peer-reviewed OGI papers) for absorption coefficients.
- R12. The trade-off section concludes with the recommendation framed as an engineering judgment, not a textbook answer: pure physics points to cooled MWIR for sensitivity, but mission constraints flip the choice to uncooled LWIR for visualization-grade detection. The decisive arguments are the unambiguous ones — SWaP (10× lower mass/power without a cryocooler), cost (~5-10× lower), instant-on (no cool-down), and cryocooler MTBF risk on a vibrating UAV. Solar-contamination resistance and vibration tolerance are presented as supporting bullets only when stated at the resolution R10 demands; if the author cannot defend the distinctions live, those two bullets are dropped from the recommendation rather than asserted in soft form.
- R13. The trade-off section explicitly enumerates the conditions under which cooled MWIR would be the correct choice instead: fixed-platform installation where SWaP is unconstrained; regulatory-grade low-emission-rate detection / quantification; very thin / low-emission-rate plumes near the detection floor; cold-background scenes where ΔT is marginal; or deployments where the methane-band SNR margin must be maximized.
- R13b. The trade-off section cites public precedent for uncooled LWIR with LWIR-band narrowband filtering as a methane-OGI architecture and UAV integration path, while explicitly stating that no public 50-200 m ppm·m performance curve was located. Later fact-checking resolved this as: architecture/platform validated by FLIR GF77/GF77a and MFE Detect LW, range envelope modeled and requiring field validation.

**Payload architecture**

- R14. The architecture section presents a labeled block diagram showing: methane-band-qualified uncooled LWIR core (640×512, 12 µm pitch, NETD ≤ 40 mK as design target), optical assembly with narrowband filter, companion visible-light camera (low-light / NIR-capable for night ops) for fusion overlay, IMU + GPS, embedded processor (Jetson Orin Nano-class — Cortex-A78AE CPU plus GPU / Tensor compute; exact TOPS and encode support depend on module variant — sized to support the algorithm pipeline at 30-60 Hz after benchmark), encrypted comms link, battery / power management, and 2-axis gimbal.
- R15. The architecture section includes a SWaP budget table totaling payload mass and power, sized to a small UAV (target sub-2 kg payload class, ~30 min nominal mission-endurance target). Each subsystem line carries an engineering-estimate value with a stated assumption; volume is left to detailed mechanical packaging rather than asserted.
- R16. Stabilization is sized for the platform: a lightweight 2-axis gimbal is the minimum viable hover-and-pan baseline, IMU-aided electronic image stabilization (EIS) mitigates residual jitter, and the algorithm pipeline handles remaining residual through frame registration. A 3-axis/higher-bandwidth gimbal remains the fallback if selected-airframe vibration or roll/pan dynamics exceed test limits.
- R17. The visible-light fusion subsystem is justified as part of the payload: the operator alarm overlays detected plumes on the visible image so the leak's physical location is interpretable in context, not just a thermal blob. **Night-operation handling is named explicitly:** when ambient illumination is insufficient, the operator overlay degrades gracefully to thermal-only, and ego-motion compensation falls back from visible-feature registration to thermal-frame self-registration with the IMU as prior. A low-light / NIR-sensitive visible sensor (or a low-power NIR scene illuminator at short range) is named as the recommended hardware path for sustained nighttime utility; the alternative is to declare nighttime operation as overlay-degraded but detection-capable.
- R18. Communications and power are dimensioned: link bandwidth for compressed thermal + visible streaming + alarm metadata, battery capacity for the stated endurance, and a notional latency budget for operator alerting.

**Optical & spectral design**

- R19. The optical section justifies a narrowband filter centered in the 7.4-8.0 µm range, explaining the trade-off vs broadband: narrowband rejects out-of-band background (improves spectral specificity and reduces solar / hot-object false alarms) at the cost of total photon flux. Bandwidth chosen to encompass the methane ν₄ Q-branch while avoiding the worst water-vapor lines.
- R20. The optical section justifies Germanium as the baseline lens material (broad LWIR transparency, good machinability, AR-coatable for narrowband transmission) while treating silicon and ZnSe as secondary options, not impossible choices: silicon can transmit around 7.7-8.0 µm with the right grade but has less broad-LWIR margin; ZnSe is broadband and non-hygroscopic but softer / less rugged and not needed when the visible camera is separate.
- R21. The optical section addresses filter placement honestly: with no dewar (uncooled detector), the methane filter is warm somewhere in the front-end optical train rather than cryogenic. Self-emission is **not** a uniform offset — it carries a spatial gradient (cosine-fourth illumination falloff plus filter-temperature non-uniformity across the aperture) and adds shot noise that two-point NUC partially handles but cannot fully remove. The design accepts an effective-NETD penalty (stated as an order-of-magnitude estimate vs. the bare-sensor NETD in the performance budget), and operationally mitigates with: (a) filter thermal stabilization (passive thermal mass + heatsinking, or active control on extended missions), (b) NUC scheduled to filter-temperature drift rather than fixed cadence, and (c) a full f/#-cone angle-of-incidence budget so passband shift is modeled, not hand-waved. This is called out as a deliberate design decision with quantified consequences, not asserted as solved.
- R22. The optical section presents a worked FOV / IFOV / GSD calculation for representative geometry — e.g., a 640×512 array at 12 µm pitch with a focal length sized for ~14° HFOV at 100 m altitude — giving a numeric ground sample distance that anchors detection-range claims.
- R23. f-number is justified as a trade: f/1.0-f/1.4 maximizes photon collection given the narrowband filter and thermal SNR floor, but f/1.4-f/2.0 remains in the design space if thin-film passband shift over the full cone becomes the dominant risk.

**Detection algorithm**

- R24. The algorithm section presents the pipeline at the *logical-group level* in the body — six groups: (1) Acquisition + NUC, (2) Motion compensation, (3) Background estimation + frame differencing, (4) Spatial detection (filter + adaptive threshold + connected-components), (5) Temporal validation + false-positive rejection, (6) Fusion overlay + operator alarm. The full stage-level expansion (12 stages, with parameters and pseudocode) lives in the appendix; the body explains intent and key design decisions, not stage-by-stage implementation.
- R25. The background-estimation approach is named and justified: a temporal model exploits the asymmetry that real plumes are dynamic and shape-shifting while most of the scene is static. The window length (~1-2 s) is justified against typical plume timescales. **NUC-event reconciliation is specified explicitly:** a shutter NUC event flushes the temporal background model, and the alarm pipeline suppresses detection for one window-length (~1-2 s) after each event to allow the model to re-converge; alternatively, NUC is scheduled only during ferry / transit phases. The chosen rule (flush-and-suppress) is called out so an implementer does not have to invent it.
- R26. Motion compensation is addressed explicitly: UAV ego-motion is estimated from the IMU and refined by feature-based registration on the visible-light camera. **The visible/thermal camera pair is rigid co-boresighted with factory-calibrated intrinsic + extrinsic parameters, using ≤1 px RMS at 50 m as a stretch target and ≤1-3 px as an acceptable prototype range until flight data proves tighter alignment;** runtime cross-modal homography re-estimation is supported but not relied on as the primary mechanism. Residual jitter is absorbed by a tolerance band in the differencing stage. At night, when visible features are insufficient, the pipeline falls back to thermal-frame self-registration with IMU prior (per R17).
- R27. False-positive sources are named individually with mitigations framed as heuristics requiring field tuning: hot static objects (temporal differencing plus stationarity), specular solar reflections (reduced by LWIR/narrowband filtering and checked with visible correlation where possible), water-vapor / steam plumes (high-risk single-band false-positive class requiring operator follow-up or multi-band v2), windborne vegetation (persistence/morphology/scene masks/motion model, not centroid stationarity alone), and NUC residue / fixed-pattern noise (shutter NUC plus temporal differencing).
- R28. The algorithm section names the operator alarm logic: detection threshold is a tuned function of blob persistence + intensity + spatial coherence, and alarms surface the visible-light frame with the thermal plume overlaid.

**Performance estimation**

- R29. The performance section computes a representative CL_min from the relation in R9 **at both the lower and upper ends of the operating envelope (50 m and 200 m)** — plugging in stated values (effective NETD post-temporal-averaging, ΔT = 5 K nominal with 3 K stress case, filter-weighted α from §6, atmospheric transmittance τ_atm at 100 m for standard atmosphere as the baseline, with humid/dry sensitivity bounds) — and arrives at an order-of-magnitude figure in ppm·m for each. The result drives the executive summary's range envelope (effective utility window vs marginal regime). Every assumption is named in line.
- R30. The performance section presents a detection-range curve under varying conditions: ΔT (3, 5, 10 K), atmospheric water-vapor loading (dry / standard / humid), and plume column density. The curve shape — not a single point — is what's argued.
- R31. The performance section dimensions the frame-rate / latency budget: 30-60 Hz nominal frame rate, ~33-16 ms per-frame processing budget on the Jetson Orin Nano-class processor named in R14, and the resulting alarm latency from event to operator notification. Headroom is framed as an integration benchmark on the selected module, especially if video encoding shares the CPU/GPU budget.

**Bonus — simulation**

- R32. A Python simulation produces two plots as an **honest sensitivity analysis** — its purpose is to characterize the (ΔT, CL) regime where each technology wins, not to confirm the recommendation. (a) apparent ΔT seen by the camera vs column density CL, computed for both 3.3 µm and 7.6-7.9 µm narrowband filters at scene ΔT of 3 K, 5 K, 10 K, with horizontal effective-NETD lines for cooled (~25 mK) and uncooled (~40 mK, with the warm-filter penalty from R21 applied) overlaid; (b) CL_min vs scene ΔT for both technologies, showing the regimes where each wins. **If the chart shows cooled MWIR dominating most of the plane (the expected outcome on physics), the report's narrative explicitly owns that result and routes to the SWaP / cost / instant-on / cryocooler-MTBF argument as the deciding factor — converting the chart from a presentation risk into a credibility multiplier.**
- R33. The simulation uses simplified Beer-Lambert with band-integrated absorption coefficients drawn from public databases (HITRAN-derived or PNNL gas-phase IR), cited explicitly. It does not run line-by-line radiative transfer.
- R34. The simulation is reproducible: a single self-contained Python file with stated assumptions in the docstring, deterministic outputs, and saved plot files referenced from the report.

**Bonus — algorithm demo**

- R35. A Python implementation of a representative subset of the detection pipeline (rolling temporal background, frame differencing, adaptive thresholding, and connected-components extraction — logical group 3 and the core of group 4 from R24, not the full 12-stage pipeline) runs on synthetic frames. Synthetic frames are generated from a static thermal background plus a buoyant Gaussian-blob plume model whose intensity is calibrated to a specified CL via the Beer-Lambert relation in the simulation. Perturbation scenarios exercise robustness of the implemented core; temporal persistence and cross-modal false-positive rejection remain described production stages, not implemented demo behavior.
- R36. The demo reports precision/recall on a small benchmark (≤ 3 synthetic clips spanning representative ΔT and CL conditions) **explicitly framed as a controlled-conditions sanity check that the pipeline functions as designed under the assumed plume model — not a field-performance claim.** The appendix names the limitations of synthetic-only validation in line: turbulent plume morphology, non-stationary backgrounds, cross-modal artifacts, and the long tail of real false positives are out of scope for the demo and are explicit future-work items.
- R37. The demo emits before/after still frames (raw thermal | thermal with detection overlay) suitable for inclusion in the report appendix. A full side-by-side video pipeline is out of scope; stills are sufficient for an interview deliverable and reclaim time for the physics, trade-off, and performance sections.

**Cross-cutting**

- R38. Page budget: original target was 12-14 main-body pages plus short appendices. Final package prioritizes factual caveats and system-engineering appendices over strict brevity; before submission, render to PDF/Word and split appendices into supporting material if the 10-15 page report constraint is exceeded.
- R39. Figures included in the final package: payload block diagram, optical-path schematic, FOV / GSD geometry, detection-pipeline sketch, the two simulation plots from R32, and the trade-off comparison table from R11. Planck-curve and methane-absorption-spectrum sketches were not added; their claims are handled in text and cited facts.
- R40. Citation discipline: every quantitative claim (NETD ranges, absorption coefficients, MTBF figures, ppm·m sensitivities, cost ratios) carries a citation to public literature or is explicitly labeled as an engineering estimate with stated assumptions. No fabricated specs.
- R41. All text sourced from this brainstorm — including pseudo-numerical assumptions — is checkable against the cited references before final submission.

---

## Acceptance Examples

- AE1. **Covers R1, R12, R13.** Given a reader skims only the executive summary and the trade-off conclusion, when they finish those two sections, they can state both (a) the recommended technology and platform, and (b) the specific operational conditions under which the alternative technology would be preferred — without further reading.
- AE2. **Covers R6, R9.** Given a reader new to OGI reads the physics section, when they finish, they can explain in one paragraph why thermal imaging detects gas, what the three knobs of detectability are, and why methane has both an MWIR and an LWIR band.
- AE3. **Covers R20, R21.** Given an evaluator probes "why Germanium and not silicon," the report contains a direct answer: silicon can work near 7.7-8.0 µm with the right grade, but Ge gives broader LWIR margin and is the safer baseline for a methane-band payload. The author does not need to invent an absolute material exclusion on the fly.
- AE4. **Covers R32, R33.** Given an evaluator asks "show me the simulation," the author can run the Python script, produce the two plots within seconds, and read the absorption coefficients off cited public references.
- AE5. **Covers R27.** Given an evaluator probes "what about steam," the report's false-positive section already contains a paragraph naming steam as a real limitation, the spectral and behavioral cues that distinguish it, and the operational guidance that mitigates it.

---

## Success Criteria

- The author can defend every quantitative claim in the report under live questioning, because each is grounded in cited literature or labeled as an engineering estimate with assumptions named in line.
- The trade-off section reads as an engineering judgment that respects both technologies — not as a hatchet job on cooled MWIR or a sales pitch for uncooled LWIR — and an evaluator who disagrees with the recommendation can still see why a competent engineer would choose this way.
- The bonus simulation runs deterministically and produces the two plots in R32; the algorithm demo runs end-to-end on synthetic frames and emits the reported precision/recall numbers.
- The report could be handed to a downstream contributor (or to ce-plan) without further conversation, and they could begin writing prose / building the simulation without inventing product behavior, scope, or success criteria.

---

## Scope Boundaries

- A fixed ground-station design is not produced; ground-station operation is named only as one of the conditions favoring cooled MWIR in R13.
- Active sensing approaches (TDLAS, DIAL, backscatter LiDAR) and hyperspectral imaging are mentioned briefly as adjacent technologies for context; no architecture is developed for them.
- Multi-gas detection is out of scope. The report focuses on methane; co-detection of other hydrocarbons is acknowledged as a side-effect of the broad C-H absorption region but not designed for.
- Quantification (converting detection to mass-flow rate or kg-CH₄/hr) is named as the next-tier capability and explicitly excluded; the system is visualization-grade detection only.
- ML / CNN-based detection algorithms are named as a future-work direction and not implemented; the v1 algorithm is classical signal-processing.
- Full HITRAN line-by-line radiative transfer is out of scope; the simulation uses simplified Beer-Lambert with band-integrated coefficients.
- Real-fluid plume CFD modeling is out of scope; the algorithm demo uses a Gaussian-blob plume model with intensity calibrated via Beer-Lambert.
- Detailed BOM, vendor selection, and cost modeling are out of scope; cost discussion is order-of-magnitude only.
- FAA airworthiness, radio-spectrum compliance, cybersecurity, and certification topics are mentioned only when they would change a design decision; they are not developed.
- Calibration and field-maintenance procedures are acknowledged as real operational concerns and named once in the architecture section, but not developed into procedures.

---

## Key Decisions

- **Platform: small UAV.** UAV is the right platform for the deployable mission this report addresses: rapid leak-survey across dispersed assets (well pads, gathering lines, small facilities) where fixed monitoring infrastructure is uneconomic and where on-demand, finer-spatial-resolution coverage at low altitude is the operationally needed capability. A consequence (not the cause) is that the platform constraint pushes back on the textbook MWIR answer and produces a richer trade-off discussion than a fixed ground station; the report does not surface that consequence as the rationale.
- **Recommendation: uncooled LWIR + LWIR-band narrowband filter, with cooled MWIR as the named conditional alternative.** The decisive factors are SWaP, cost, instant-on, and cryocooler-MTBF risk on a vibrating UAV — all unambiguous wins for uncooled. The recommendation is presented as visualization-grade detection within a stated effective envelope, with explicit acknowledgement (per R13b) that public precedent validates architecture/platform class, not the exact 50-200 m performance curve.
- **Single-band passive imaging only.** No active illumination, no multi-band differencing in v1. Keeps SWaP, cost, and complexity tractable for a small UAV; multi-band approaches are deferred.
- **Trade-off section before architecture.** The architecture is *consequent on* the technology choice, not pre-declared; this ordering also forces the reader through the core engineering argument early.
- **Practical product memo tone.** Calibrated to an oil & gas / methane-monitoring evaluator; vendor-agnostic specs avoid name-dropping while preserving market awareness through anonymous anchors.
- **Filter placement: warm filter in the optical train.** The uncooled core has no dewar, so a cold filter is not an option. Warm-filter self-emission and angle-of-incidence passband shift are handled with stated consequences (effective-NETD penalty, thermal stabilization, drift-aware NUC, full f/#-cone filter modeling) rather than asserted as solved by NUC alone — see R21.
- **Visible-light fusion is part of the payload, not an add-on.** The operator alarm needs context — a thermal blob without a recognizable scene reference is hard to act on. This also gives the algorithm an extra registration channel for ego-motion compensation.
- **Algorithm is classical signal processing in v1.** Temporal differencing with motion compensation and persistence testing is defensible, debuggable, and runnable in a synthetic demo without a labeled OGI dataset; ML is named as future work.
- **Simulation uses simplified Beer-Lambert, not line-by-line.** Sufficient for the contrast-vs-CL story the report needs to tell; LBL would require infrastructure (HITRAN integration, layer atmospheric modeling) that exceeds the deliverable's intent.

---

## Dependencies / Assumptions

- Public absorption-coefficient data for methane in the 3.2-3.4 µm and 7.4-8.0 µm bands is available from HITRAN or PNNL gas-phase IR libraries and can be cited directly. **Assumed; not verified at brainstorm time** — verify before populating the simulation and the trade-off table's α values.
- NETD ranges of 15-25 mK for cooled MWIR and 30-50 mK for modern uncooled LWIR are consistent with current peer-reviewed and trade literature. **Assumed; not verified at brainstorm time** — confirm against current published ranges before citing. **Contingency:** if confirmed values differ materially (e.g., uncooled NETD floor exceeds 60 mK after the warm-filter penalty in R21, or cooled NETD floor exceeds 35 mK), the CL_min calculation in R29 carries explicit sensitivity bounds and the recommendation in R12 is revisited rather than asserted unchanged.
- The initial brainstorm's ~10× absorption-strength asymmetry between methane's 3.3 µm and 7.6 µm bands was a peak-line shorthand and is **superseded** by the final report's few× engineering ratio. The integrated/passband-weighted ratio depends on filter shape and should be computed from cited spectra before detailed radiometric design.
- Frame rates of 30-60 Hz are achievable on modern uncooled LWIR cores within stated SWaP class. Assumed.
- A sub-2 kg payload class with ~30 min mission endurance is the implicit UAV envelope. If the evaluator's company operates in a different class, this assumption must be revisited.
- The simulation is run as honest sensitivity analysis (per R32), not as confirmation of the recommendation. The expected outcome — cooled MWIR dominating raw sensitivity across most of the (ΔT, CL) plane — is the truth the report is built to *own*, not to hide. The recommendation defends on SWaP / cost / instant-on / cryocooler-MTBF risk, and the chart is what makes that defense credible. Only if the simulation surfaces a sensitivity gap so large that uncooled LWIR cannot deliver visualization-grade detection within the stated envelope (e.g., CL_min > 5000 ppm·m even at ΔT = 10 K) is the recommendation itself revisited.

---

## Outstanding Questions

### Resolve Before Planning

- [Affects R7, R12, R13b, R32, R33][Needs research] **Compute the filter-weighted integrated absorption ratio** between methane's 3.3 µm passband (~3.2-3.4 µm) and the chosen LWIR passband (~7.7-8.0 µm) from public spectral data (HITRAN or PNNL). Later work avoided asserting the initial 10× shorthand and used a few× engineering ratio instead; exact passband integration remains a detailed radiometric-design follow-up, not a blocker for the assignment-level model.
- [Affects R5, R13b][User decision] **Identify the interviewing company's actual platform tribe** (UAV vs aircraft vs fixed station vs vehicle vs handheld) before locking the UAV framing. A 30-minute LinkedIn / company-page scan is sufficient. If the company is fixed-station-centric, the recommendation flips: cooled MWIR becomes primary in the executive summary and UAV becomes one of the conditional alternatives.

### Deferred to Planning

- [Affects R15][Technical] Locate at least one public reference (academic paper, regulatory pilot, or operator-reported deployment) demonstrating uncooled LWIR + LWIR-band narrowband filtering for methane OGI at 50-200 m. Required to back R13b before write-time; if none can be found, R13b's reframe-as-exploratory branch fires.
- [Affects R29-R31][Needs research] Specific NETD and α(λ) values used in the worked CL_min are selected from cited references at write-time, not asserted; the brainstorm specifies the *form* of the calculation but defers the populated values. Include atmospheric transmittance τ_atm at 100 m for standard atmosphere as the baseline, with humid/dry sensitivity bounds.
- [Affects R10, R11][Technical] Cost comparison framing — absolute order-of-magnitude figures (e.g., "$5-15k vs $30-80k") or ratio-only ("~5-10× cost differential") — is a planning-time call; either is allowed as long as citations support it.
- [Affects R28][Technical] Exact alarm-decision logic (threshold function, hysteresis, persistence-window length) is a planning-time refinement; the brainstorm specifies the inputs (blob persistence, intensity, spatial coherence) but not the formula.
- [Affects R15][Technical] Specific SWaP envelope (sub-2 kg vs sub-25 kg payload class) best matched to the target operator. Working assumption is sub-2 kg, ~30 min endurance; resolve by reading the interviewing company's operations literature.

---

## Deferred / Open Questions

### From 2026-05-08 review

- **Atmospheric water-vapor handling is inconsistent across the doc — extend the model or drop the axis** — R9, R29, R30, R32-R33 (P2, feasibility + scope-guardian, confidence 75)

  R30 requires a detection-range curve over atmospheric water-vapor loading (dry / standard / humid), but R29's CL_min relation omits τ_atm and R32-R33's simulation does not model atmospheric transmission with humidity. Two coherent fixes exist: (a) extend R9's relation and the simulation to include τ_atm, accepting the additional modeling complexity; or (b) drop water-vapor as an axis from R30, keep ΔT and CL only, and handle humidity as a named assumption + qualitative footnote. (a) is more rigorous and matches R30's promise; (b) is simpler and matches the simulation scope already declared. Both are defensible; the author's call.

  <!-- dedup-key: section="r9 r29 r30 r3233" title="atmospheric watervapor handling is inconsistent across the doc extend the model or drop the axis" evidence="r30 requires a detectionrange curve over atmospheric watervapor loading dry standard humid but r29s clmin relation omits tatm" -->

- **Identify the interviewing company's platform tribe before locking the UAV framing** — R5 / Audience (P2, product-lens, confidence 75)

  The doc names "senior EO engineer at a methane-monitoring company" but doesn't require identifying *which* company / platform tribe (UAV vs aircraft vs fixed station vs vehicle vs handheld) before committing to UAV as the primary frame. If the company is fixed-station-centric, the recommendation flips: cooled MWIR becomes primary in the executive summary and UAV becomes a conditional alternative. This is a 30-minute LinkedIn / company-page check the author does before write-time, not a planning task. Surfaced here as Resolve-Before-Planning in Outstanding Questions; flagged as Open Question because the resolution may force a structural rewrite.

  <!-- dedup-key: section="r5 audience" title="identify the interviewing companys platform tribe before locking the uav framing" evidence="r5 the report has a single named target reader a senior eopayload engineer at a methanemonitoring operation" -->

- **'Practical product memo' tone vs engineering-rigor signals the EO evaluator reads for** — R2 / Tone (P2, product-lens, confidence 75)

  The product-memo identity optimizes for the deployable-narrative dimension at the cost of pure-engineering-rigor signals. For a payload-engineering interview, the evaluator's primary question is "can this person do the EO physics?" — not "can this person write a board memo?" A polished product-memo voice paired with vendor-agnosticism may read as marketing-adjacent to a hardcore EO engineer. Two paths: (a) downshift to "engineering report with operational context" as the primary identity, with product-memo voice reserved for executive summary and conclusion only; or (b) keep the framing but require the body sections (physics + trade-off + performance) to occupy ≥ 60% of the page count. Either resolves the identity-drift risk without a full reframe. Author's call.

  <!-- dedup-key: section="r2 tone" title="practical product memo tone vs engineeringrigor signals the eo evaluator reads for" evidence="r2 the report is written as a practical product memo operational framing in introconclusion mission" -->

- **Vendor-agnostic stance vs market-awareness signal** — R3 (P2, adversarial + product-lens, confidence 75)

  R3 forbids naming specific commercial systems, allowing only "anonymous market anchors." This is defensible on style grounds but creates an asymmetry: a senior EO engineer at a methane-monitoring company will likely use brand names conversationally (FLIR GFx, Workswell, Sierra-Olympia, Telops) and may probe whether the candidate has done the homework. Pure-spec vendor-agnosticism is right for a published whitepaper; for an interview deliverable read by one specific evaluator, naming products in a separate market-survey paragraph (distinct from the recommendation) may convert better. Either keep R3 and prepare market fluency for live discussion only, or relax R3 to allow a single market-context sidebar in the body. Author's call — both have real tradeoffs.

  <!-- dedup-key: section="r3" title="vendoragnostic stance vs marketawareness signal" evidence="r3 hardware is described by spec class not by vendor or product name cooled mwir and uncooled lwir are compared as system" -->

- **Algorithm-demo opportunity cost vs physics-depth investment** — R35-R37 / Bonus algorithm (P2, product-lens, confidence 75)

  Even after R35-R37 has been narrowed (per the same-session review fix), the algorithm demo competes for time against deepening EO content the evaluator actually probes for: filter-weighted absorption ratio, cooled-MWIR conditions in R13, performance-range stress at 200 m. The author is newer to EO/IR; time spent shoring up physics depth likely converts higher than time spent on a Python pipeline. Decision: invest the saved time from the narrowed R35-R37 either in (a) deepening the worked CL_min and the trade-off table's quantitative content, or (b) making the demo more rigorous (real PNNL absorption data, actual atmospheric model). (a) probably converts higher for a payload-engineering role; (b) is the defensible alternative if the author is already confident on physics.

  <!-- dedup-key: section="r35r37 bonus algorithm" title="algorithmdemo opportunity cost vs physicsdepth investment" evidence="the author is newer to eoir strong on engineering thinking less practiced with netd math beerlambert reasoning" -->
