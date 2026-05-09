---
title: "refactor: System engineer role alignment for methane OGI submission"
type: refactor
status: implemented
date: 2026-05-08
---

# refactor: System engineer role alignment for methane OGI submission

**Origin note:** Merges the prior `refactor-system-engineer-role-alignment-plan` (gpt-5-5 originated) and `feat-low-level-platforms-supplement-plan` (claude-opus-4-7 originated) into one plan. The supplement plan is superseded; its U1/U2 are absorbed as U6/U7 below.

**Completion note:** Implemented in the submission package. The report now includes integration interfaces, embedded runtime posture, Appendix E low-level platforms, Appendix F verification, and Appendix G diagnostics/field support; `bonus/data/low-level-talking-points.md` provides the interview cheat sheet.

## Summary

Improve the methane OGI technical-assignment package so it reads as a system-engineering deliverable, not only an EO/IR trade study. The work spans two layers:

1. **Main report framing** — explicit integration, verification, embedded-runtime, diagnostics, and deployment-support content that makes the JD competencies visible without bloating the report or weakening the assignment-specific technical answer.
2. **Low-level platforms supplement** — a focused Appendix E (~1.5 pages) covering the embedded/firmware concerns the JD names (sensor bus, real-time scheduling, driver-level NUC, DMA/buffers, firmware boot/watchdog, power management, gimbal MCU, bring-up tooling), plus a separate interview cheat sheet for live Q&A.

The cooled-MWIR vs uncooled-LWIR core argument is preserved throughout.

---

## Problem Frame

The current submission already covers detector physics, payload architecture, spectral design, detection algorithms, and modeled performance. The target role, however, emphasizes full system design, HW/SW integration, testing, deployment, maintenance, low-level platforms, and cross-functional communication.

The deliverable has two visible gaps against that role:

- **Upper-layer systems framing.** Verification discipline, integration interfaces, diagnostics, and operational deployment thinking are mostly implicit and need explicit content.
- **Lower-layer platforms credibility.** The body stops at "Jetson Orin Nano-class processor" and "30-60 Hz pipeline budget." Without driver/firmware/RTOS coverage, an interviewer probing low-level questions ("how does the bolometer connect to the processor?", "what's your real-time scheduling story?") will surface a credibility gap. The author is newer to EO/IR domain and may also be less practiced on driver/firmware specifics; both halves need a defensible artifact.

Both layers should be addressed without bloating the report or diluting the assignment-specific technical answer.

---

## Role-Alignment Rubric

Use the user-provided System Engineer job description as the evaluation rubric:

| JD competency | Submission evidence to strengthen |
|---------------|-----------------------------------|
| Complex HW/SW system design | Integrated payload boundary, subsystem responsibilities, interface table |
| System integration and testing | Verification-and-validation matrix, bench/field/flight test methods, pass-criteria provenance |
| Maintenance, support, debugging | Diagnostics, telemetry, fault modes, calibration/NUC handling, field logs |
| Low-level platforms | Bounded embedded-runtime callout in body; deeper bus/scheduling/driver/DMA/MCU specifics in Appendix E and the cheat sheet |
| Component selection and architecture | Preserve cooled MWIR vs uncooled LWIR trade-off and surface when new integration constraints would weaken it |
| Cross-functional communication | Tables and operational framing that a payload engineer, embedded engineer, and program stakeholder can all read |
| Programming-language credibility | Truthful C++/C# fluency section in the cheat sheet; do not claim the report demonstrates either language |

---

## Requirements

- R1. Keep the original assignment answer intact: methane plume detection at 50-200 m, day/night operation, cooled MWIR vs uncooled LWIR trade-off, payload architecture, optical/spectral design, detection algorithm, and performance estimates.
- R2. Add explicit system-engineering framing across hardware, software, optics, power, compute, comms, calibration, and operator workflow.
- R3. Add a verification-and-validation plan that maps mission requirements to test methods and pass criteria, with each pass criterion tagged by source category.
- R4. Add integration-interface details for thermal, visible, IMU/GPS, embedded processor, power, and ground-control links.
- R5. Add maintainability, diagnostics, and field-support content that demonstrates deployed-system thinking.
- R6. Add a compact embedded-runtime callout in the main body without overclaiming firmware or driver implementation depth; the deeper layer lives in Appendix E (R7) and is cross-referenced rather than duplicated.
- R7. Add **Appendix E** (~1.5 pages) covering the eight low-level topics below, each as a paragraph or short subsection led by a one-line decision or working assumption:
  - Sensor-to-processor interface (MIPI CSI-2 vs USB3 Vision vs GigE Vision; preferred conditional path, fallback path, rationale)
  - Real-time scheduling story (Linux PREEMPT_RT vs RTOS vs bare-metal partition; chosen approach with rationale; end-to-end latency budget covering acquisition buffering, transfer, CPU scheduling, GPU/NPU work, thermal throttling, late-frame policy, and watchdog/fallback behavior)
  - Driver-level NUC integration (V4L2-style or vendor-SDK control model; trigger/sequencing semantics; how the application coordinates with driver-level shutter actuation without assuming a proprietary API)
  - Buffer management and DMA (zero-copy from sensor → CUDA / NPU; pinned memory for rolling temporal background; ring-buffer sizing)
  - Firmware boot / watchdog / recovery (boot sequence, watchdog timer policy, post-fault behavior — payload should fail safe, not bring down the airframe)
  - Power management (sleep states, thermal throttling, instant-on enabling sequence, payload-power-isolation rationale already in §5.6)
  - Gimbal MCU partition (separate MCU running PID loops, comms with main processor over CAN or UART, fault isolation)
  - Bring-up / debug tooling (JTAG, oscilloscope, logic analyzer, vendor SDKs)
- R8. Add a one- or two-sentence cross-reference at the end of §5.6 pointing readers to Appendix E without creating a new §5.7 anchor.
- R9. Produce `bonus/data/low-level-talking-points.md` — a separate ~1-2 page interview cheat sheet structured as ~10-15 Q&A entries grouped under **Embedded / firmware**, **Driver / OS**, and **Languages and process**, plus a "Things to be honest about" section (≥3 items) and a "Pivot moves" section (≥2 bridges). Voice is terse/scannable, distinct from Appendix E's prose.
- R10. All numeric claims in Appendix E and the cheat sheet are either added to `bonus/data/facts.md` with source/assumption notes, or phrased qualitatively. No fabricated specs. Each externally grounded claim is tagged **confirmed**, **assumed**, or **illustrative**.
- R11. The cheat sheet includes a truthful C++/C# language-fluency section: prior experience the author can honestly cite, likely payload components by language, and limits not to overclaim.
- R12. Preserve page-count discipline by keeping the report near ~12-14 body pages plus ~1-3 appendix pages. If Appendix E or new body sections push past, first compress lower-value appendix prose or move benchmark/debug detail to `bonus/data/` before cutting required R2/R7 coverage.
- R13. Keep the bonus code and source-of-truth data consistent with any wording changes in the report, especially `bonus/data/facts.md`, `bonus/data/precedent-search.md`, `bonus/README.md`, and demo/simulation assumptions.
- R14. Start with a baseline gap audit against the role-alignment rubric before adding sections, so the refactor targets actual gaps instead of duplicating existing strengths.

---

## Scope Boundaries

- Do not change the core recommendation unless the existing technical basis is contradicted during editing; do require a pre-edit checkpoint that re-reads the recommendation and modeled assumptions before adding role-alignment material.
- Do not add real hardware procurement, CAD, PCB, firmware, or driver work. Appendix E and the cheat sheet describe approach and reasoning, not implementations.
- Do not expand the synthetic demo into a production detection system.
- Do not add new Python code in `bonus/`. The simulation and demo are unchanged.
- Do not add vendor-specific commitments beyond the Jetson Orin Nano class already named in §5. References to specific FPGAs, MCUs, or driver frameworks (V4L2-style controls, FreeRTOS, PREEMPT_RT) are working assumptions or examples that must be tagged confirmed/assumed/illustrative before appearing in Appendix E or the cheat sheet.
- Do not re-architect §5. Appendix E is the *layer below* §5, not a revision.
- Do not introduce new unverified performance numbers; new pass criteria must either reuse existing report assumptions or be labeled as proposed verification targets.
- Do not require an additional ce-doc-review pass after this plan is tightened. Lightweight scope, single-author, time-bounded for interview prep.

---

## Context & Research

### Relevant code and patterns

- `methane-ogi-payload-report.md` §5 (Architecture) — current architecture body, ends at processor-class level. Appendix E hooks below it via the §5.6 cross-reference.
- `methane-ogi-payload-report.md` §7 (Detection Algorithm) — pipeline runs on the processor named in §5; Appendix E describes how that pipeline maps onto OS scheduling and DMA.
- `bonus/data/facts.md` — cited-numbers source-of-truth. Any new numeric claim added to the report, Appendix E, or the cheat sheet should be entered here with a source/assumption note or rewritten qualitatively. Likely candidates: interface bandwidth/lane count, USB/GigE latency, scheduling jitter, ring-buffer depth, watchdog timing, power sequencing.
- `bonus/data/precedent-search.md` — existing pattern for `bonus/data/` Markdown supplements; the new cheat sheet follows the same shape.

### External references

- Jetson Orin Nano product brief — confirm interface support (MIPI CSI lanes, USB3 ports, NPU class).
- V4L2 documentation — confirm what is standard camera-control behavior versus thermal-camera-vendor-specific NUC behavior.
- Linux PREEMPT_RT documentation — confirm whether scheduling-latency claims should be numeric or qualitative.

These references are load-bearing for any factual claims that survive into Appendix E or the cheat sheet.

---

## Key Technical Decisions

- **Prioritize verification content first.** The biggest upper-layer role-fit gap is making integration and test discipline visible.
- **Use compact tables over long prose.** Tables communicate systems thinking efficiently and protect the report from page-count creep.
- **Two artifacts for the low-level layer, not one.** Appendix E is the formal report extension (prose, vendor-agnostic, defensible to a reader). The cheat sheet is interview preparation (Q&A bullets, terse, role-specific). Combining them would either bloat the report or dilute the cheat sheet.
- **Appendix E placement: after Appendix D.** Keeps the appendix sequence A → B → C → D → E in order of relevance to the body (sim, algorithm, figures, references, low-level extension).
- **Cheat-sheet location:** `bonus/data/low-level-talking-points.md`, alongside `facts.md` and `precedent-search.md` — supporting research material the author uses, not part of the formal deliverable but tracked for reproducibility.
- **Sensor interface working assumption:** MIPI CSI-2 preferred when the selected core and carrier board support it, with USB3 Vision / GigE Vision / vendor SDK module as fallback. Frame conditionally until the specific thermal core and carrier-board lane mapping are confirmed.
- **Real-time scheduling working assumption:** Linux user-space with PREEMPT_RT, not bare-metal RTOS, for the main image pipeline. Justified by an end-to-end latency budget. Gimbal control remains on a separate MCU because its PID loop and fault-isolation needs differ from image-processing deadlines.
- **Driver-level NUC:** V4L2-style control plane where available, vendor SDK where necessary. Application schedules NUC/shutter triggers and coordinates pipeline masking around those events; no claim of standard readback of proprietary per-pixel correction state unless verified.
- **Power-management isolation:** payload power separate from airframe power. Already stated in §5.6 — Appendix E elaborates the *why* (preserves airframe propulsion if payload faults, simplifies certification).
- **Frame embedded body content as architecture/runtime design.** In the main body, mention bounded pipelines, timestamps, watchdogs, telemetry, and fallback modes; avoid implying custom firmware unless explicitly scoped. Defer driver/firmware specifics to Appendix E.
- **Cheat sheet format:** ~10-15 Q&A pairs, easy to scan during a live interview without flipping pages.
- **Start with a gap audit, not additive drafting.** Score the existing report against the role-alignment rubric and decide whether each competency needs a new section, tighter existing language, an appendix move, or no change.
- **Keep bonus material secondary.** Bonus simulation/code supports the report rather than dominating it.

---

## Open Questions

### Resolved during planning

- *Should the low-level supplement be its own document or a section in the report?* Resolved: Appendix E in the report (formal) plus a separate cheat sheet under `bonus/data/` (informal). Different audiences.
- *Should the cheat sheet include C++/C# code samples?* Resolved: no. The deliverable doesn't demonstrate either language; pretending otherwise is a credibility risk. The cheat sheet flags language fluency as "discuss separately" rather than papering over.
- *Should the alignment refactor and the low-level supplement be one plan or two?* Resolved: one. Plan 1 U5 already deferred driver/firmware depth to the supplement; merging removes the cross-plan coordination burden.

### Deferred to implementation

- *Exact FPS/MIPI lane count for the chosen Jetson Orin Nano configuration.* Confirm carrier-board lane mapping, sensor bit depth, and frame rate at write-time before making a numeric claim. If not confirmed, state the interface choice qualitatively.
- *Whether to mention specific vendor SDKs (FLIR Atlas, Workswell SDK).* Body and Appendix E stay vendor-agnostic; the cheat sheet may name SDKs as "examples of what the integration would look like."
- *How much C++/C# prep to put in the cheat sheet.* Working assumption: include a truthful language-fluency section that names prior experience if available, maps C++ to gimbal MCU firmware / performance-critical camera pipeline pieces, maps C# only where relevant to tooling or operator UI, and lists what the author should not claim.

---

## Implementation Units

### U1. Audit role-fit gaps and add system-engineering framing

**Goal:** Identify the highest-value role-fit gaps in the current report, then make the executive summary and introduction explicitly describe the payload as an integrated HW/SW system.

**Requirements:** R1, R2, R14

**Dependencies:** None

**Files:**
- Modify: `methane-ogi-payload-report.md`

**Approach:**
- Audit the existing report against the role-alignment rubric and record the action for each competency: add new content, tighten existing wording, move detail to appendix, or leave unchanged.
- Re-read the current recommendation and modeled assumptions before editing; record whether new integration, verification, or deployment constraints weaken the recommendation.
- Add a short "system-engineering view" paragraph near the executive summary or mission section only where the audit shows the current report does not already make the system boundary clear.
- Name the coupled subsystems: detector, optics, filter, mechanical mount/stabilization, embedded processor, power, comms, operator overlay, calibration, verification.
- Adjust the conclusion to emphasize prototype build, bench validation, UAV integration, flight test, and iterative hardening.

**Test scenarios:** Test expectation: none — narrative/report edit.

**Verification:**
- The audit explicitly maps each JD competency to an add/tighten/move/no-change decision.
- A reviewer can identify the system boundary and major HW/SW subsystems from the first two report sections.
- The conclusion reads like a deployable system recommendation, not only a sensor-selection opinion.
- Any new integration or deployment constraint that weakens the original recommendation is surfaced rather than hidden.

---

### U2. Add a System Integration and Verification Plan

**Goal:** Demonstrate verification discipline by mapping requirements to test methods and pass criteria.

**Requirements:** R1, R3

**Dependencies:** U1

**Files:**
- Modify: `methane-ogi-payload-report.md`

**Approach:**
- Add a compact section or appendix titled `System Integration and Verification Plan`.
- Include a traceability table with requirement, verification method, pass criteria, and pass-criteria source category.
- Source categories: assignment requirement, existing modeled assumption, engineering budget, or proposed verification target.
- Visually separate proposed verification targets from validated requirements so the evaluator can distinguish defensible constraints from prototype-test goals.
- Cover at minimum: range detection, day/night operation, latency, payload mass, power draw, false-positive rejection, vibration tolerance, calibration stability, operator alerting.
- Keep pass criteria consistent with existing assumptions (e.g., frame-to-overlay latency under the stated budget, payload below the existing mass budget, steady power below the existing power budget).

**Test scenarios:** Test expectation: none — narrative/report edit.

**Verification:**
- Each major assignment requirement has at least one verification method.
- Every pass criterion carries one of the source categories above.
- Verification language distinguishes modeled estimates, bench tests, controlled-release tests, flight tests, and proposed targets.

---

### U3. Add integration-interface architecture detail

**Goal:** Show how the hardware, software, and platform components connect and what constraints each interface carries.

**Requirements:** R2, R4

**Dependencies:** U1

**Files:**
- Modify: `methane-ogi-payload-report.md`
- Optional modify: `figures/block-diagram.png` if the existing diagram needs interface labels

**Approach:**
- Add an `Integration Interfaces` table near the payload architecture section.
- Include thermal camera to processor, visible camera to processor, IMU/GPS to processor, processor to ground-control station, payload power regulation, and optional storage/logging.
- For each interface, list data type, expected rate or timing constraint, and system-level risk.
- If the current block diagram is too generic, add interface labels rather than redrawing the whole figure.

**Test scenarios:** Test expectation: none — narrative/diagram edit.

**Verification:**
- The architecture section states what data flows between components and where timing, sync, or power constraints matter.
- No interface claim depends on unavailable vendor-specific hardware details.

---

### U4. Add diagnostics, calibration, and field-support content

**Goal:** Demonstrate maintenance/support and troubleshooting awareness for deployed payloads.

**Requirements:** R5

**Dependencies:** U2, U3

**Files:**
- Modify: `methane-ogi-payload-report.md`

**Approach:**
- Add a short subsection such as `Calibration, Diagnostics, and Field Support`.
- Cover shutter/NUC events, filter-temperature monitoring, dropped-frame counters, detector temperature, processor load, IMU sync, radio link quality, detection logs.
- Add fault-mode examples and fallback behavior: visible camera unavailable, IMU/GPS dropout, processor overload, filter thermal drift, radio degradation.
- Keep this operational and concise; do not invent detailed firmware behavior.

**Test scenarios:** Test expectation: none — narrative/report edit.

**Verification:**
- The report includes at least five concrete telemetry or health signals.
- The report includes at least three realistic fault modes with corresponding fallback or operator response.

---

### U5. Add embedded runtime callout in the main body

**Goal:** Make embedded-platform competence visible inside the body without over-scoping; defer driver/firmware specifics to Appendix E.

**Requirements:** R6

**Dependencies:** U3, U4; coordinates with U6 (Appendix E)

**Files:**
- Modify: `methane-ogi-payload-report.md`

**Approach:**
- Add one compact paragraph or callout in the detection-algorithm or architecture section.
- Describe a bounded frame-processing runtime: timestamped acquisition, ring buffer, synchronized thermal/visible/IMU packets, detection worker, telemetry output, watchdog.
- Mention bounded memory, frame deadlines, dropped-frame handling, and deterministic fallback to a lower frame rate if compute load rises.
- Do not duplicate Appendix E's MIPI/USB/GigE, PREEMPT_RT, V4L2, DMA, or MCU specifics. Summarize the runtime posture and cross-reference Appendix E.

**Test scenarios:** Test expectation: none — narrative/report edit.

**Verification:**
- The body shows awareness of embedded runtime constraints: timing, buffering, memory, watchdog/fault recovery, telemetry.
- The wording does not claim custom firmware, kernel drivers, or hard real-time guarantees unless explicitly qualified.
- Body-level embedded content does not duplicate Appendix E specifics.

---

### U6. Write Appendix E — low-level platforms supplement

**Goal:** Add Appendix E (~1.5 pages) covering all eight low-level topics in R7, plus a §5.6 cross-reference pointing readers there.

**Requirements:** R7, R8, R10, R12

**Dependencies:** U1, U5 (so the body's runtime callout and the appendix are coherent)

**Files:**
- Modify: `methane-ogi-payload-report.md` (add Appendix E after Appendix D; add the §5.6 cross-reference sentence)
- Optional modify: `bonus/data/facts.md` if Appendix E introduces numeric claims not already sourced there

**Approach:**
- Re-read §5 and §7 to anchor the new content; no contradictions with existing architecture.
- Structure Appendix E as 8 short subsections matching R7's topic list, each one paragraph or a short bullet list.
- Lead each subsection with a one-line decision or working assumption, then 2-4 sentences of rationale.
- Tag external claims as **confirmed**, **assumed**, or **illustrative** before using them; add numeric claims to `bonus/data/facts.md` or phrase qualitatively.
- Include the full real-time story: acquisition buffering, transfer, CPU scheduling, GPU/NPU work, thermal throttling, late-frame handling, watchdog/fallback behavior.
- Close with one paragraph: "Why this layer is presented as a supplement, not as part of §5" — explains the layering choice and that bringing it up front would have bloated the body without earning the page count.
- The §5.6 cross-reference is one or two sentences at the end of §5.6, signposting Appendix E without creating a new §5.7 anchor.

**Patterns to follow:** Appendices A-D's voice and length pattern. Appendix B is the closest analog (technical detail, vendor-agnostic, references runnable code).

**Test scenarios:** Test expectation: none — narrative report content. Verification via the checklist below.

**Verification:**
- Appendix E covers all 8 topics from R7, each with a defensible working assumption.
- The §5.6 cross-reference renders inline and does not create a broken §5.7 anchor.
- No claim contradicts §5 or §7. Specifically: processor class matches §5.1, sensor interface remains conditional unless confirmed, real-time budget aligns with §8.3.
- No fabricated vendor specs; each factual external claim is tagged confirmed, assumed, or illustrative.

---

### U7. Write the interview talking-points cheat sheet

**Goal:** Produce `bonus/data/low-level-talking-points.md` (~1-2 pages) as a Q&A cheat sheet covering the questions an EO/embedded interviewer is plausibly going to ask. Terse, scannable, designed for in-the-room reference.

**Requirements:** R9, R10, R11

**Dependencies:** U6 (so the cheat sheet's claims align with Appendix E; no drift)

**Files:**
- Create: `bonus/data/low-level-talking-points.md`

**Approach:**
- Format: ~10-15 Q&A entries grouped under three headings: **Embedded / firmware**, **Driver / OS**, **Languages and process**.
- Each Q&A entry:
  - Question phrased as the interviewer would ask it ("How does the bolometer connect to the processor?", "What's your real-time scheduling story?")
  - Answer in 2-4 sentences, leading with the one-line decision and following with rationale and any caveat.
- Include a truthful language-fluency entry: prior C++/C# experience the author can honestly cite, likely payload components by language, and limits not to overclaim.
- Include a final "Things to be honest about" section: items the author should not bluff (specific FPGA toolchains, vendor-proprietary protocols, depth of prior C++/C# experience). Better to say "I haven't worked with that specifically; my reasoning would be …" than to pretend.
- Include a "Pivot moves" section: bridges that route a question the author can't answer back to the systems-engineering content the deliverable does cover.

**Patterns to follow:** `bonus/data/facts.md` and `bonus/data/precedent-search.md` set the voice pattern for `bonus/data/` supplements: structured, citation-aware where applicable, not bloated.

**Test scenarios:** Test expectation: none — preparation artifact. Verification via the checklist below.

**Verification:**
- 10-15 Q&A entries covering the topics in R7 (some appendix subsections will map to multiple Q&A entries, e.g., "real-time scheduling" might split into "what OS?" and "what happens if a frame is late?").
- Every claim aligns with Appendix E (no drift; if Appendix E says PREEMPT_RT as a working assumption, the cheat sheet doesn't accidentally present RTOS as the chosen architecture).
- Language-fluency section is present, truthful, and distinguishes demonstrated experience from expected implementation-language choices.
- "Things to be honest about" section is present and lists at least 3 items.
- "Pivot moves" section is present and lists at least 2 bridges.
- File is under 2 printed pages (~80-100 lines of Markdown) so it's actually scannable in a live interview, not a wall of text.

---

### U8. Rebalance length and run bonus consistency pass

**Goal:** Preserve submission readability after adding upper-layer system-engineering material *and* Appendix E.

**Requirements:** R12, R13

**Dependencies:** U1-U7

**Files:**
- Modify: `methane-ogi-payload-report.md`
- Modify: `bonus/README.md` if bonus positioning changes
- Modify: `README.md` if package overview should point to the new systems sections
- Optional modify: `bonus/data/facts.md` if numeric or sourced claims change
- Optional modify: `bonus/data/precedent-search.md` if precedent wording changes
- Optional modify: `bonus/contrast_simulation.py` and `bonus/detection_demo.py` only if report wording changes assumptions their docstrings or outputs repeat

**Approach:**
- Review total report length after U1-U7 against the target envelope: ~12-14 body pages plus ~1-3 appendix pages, or the renderer-equivalent word/page count if PDF/Word conversion shifts pagination.
- If Appendix E or new body sections push past the envelope, first compress lower-value Appendix A/B prose or move benchmark/debug detail to `bonus/data/` before cutting required R2/R7 coverage.
- Keep the cooled-MWIR vs uncooled-LWIR core argument intact.
- Run a post-edit consistency pass comparing report assumptions against `bonus/data/facts.md`, `bonus/data/precedent-search.md`, `bonus/README.md`, demo parameters, and simulation assumptions even when no bonus files were intentionally modified.
- Make the top-level README describe the deliverable as a system-engineering package: report (body + Appendix E), diagrams, simulation, detection demo, verification plan, and interview cheat sheet.

**Test scenarios:** Test expectation: none — documentation packaging edit.

**Verification:**
- The report remains within the target envelope or records the specific material moved/compressed to protect it.
- The added system-engineering sections and Appendix E are visible in the table of contents / section headings.
- Bonus code is positioned as supporting evidence, not the main deliverable.
- Changed numeric, precedent, or assumption claims still trace to `bonus/data/facts.md` / `bonus/data/precedent-search.md` or are explicitly labeled as proposed verification targets.

---

## System-Wide Impact

- **Report narrative:** shifts from "best sensor architecture" toward "integrated payload system ready for prototype and verification," with Appendix E giving an evaluator the one place to look for low-level credibility.
- **Figures:** existing figures may need light relabeling, but wholesale replacement is not required.
- **Bonus code:** no functional changes expected unless wording in the report changes assumptions that bonus docs, docstrings, tests, or outputs repeat; U8 still checks for drift even when bonus files are not intentionally edited.
- **Bonus data:** new file `bonus/data/low-level-talking-points.md`; possible additions to `bonus/data/facts.md` for new numeric claims.
- **Submission package:** README highlights systems-engineering artifacts (report body, Appendix E, V&V plan, diagrams, simulation, detection demo, cheat sheet) so an evaluator sees role fit immediately.

---

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Report becomes too long | Use tables, compress appendix prose, and keep embedded/diagnostics content concise; target ~12-14 body pages plus ~1-3 appendix pages |
| Appendix E pushes total page count past envelope | U8 first compresses Appendix A/B detail or moves benchmark/debug detail to `bonus/data/`; Appendix C trimming alone is not assumed to be enough |
| Systems content feels bolted on | Start with a role-fit gap audit; integrate additions into architecture, algorithm, and performance sections rather than adding only a disconnected appendix |
| Pass criteria look invented | Label each criterion by source category: assignment requirement, modeled assumption, engineering budget, or proposed verification target |
| Embedded wording overclaims low-level implementation | Use architecture/runtime language and qualify assumptions; route driver/firmware specifics to Appendix E with confirmed/assumed/illustrative tags |
| Author can't defend a specific vendor / driver claim live | Tag external claims; cheat sheet "Things to be honest about" enumerates items NOT to bluff, with a pivot move for each |
| Numeric low-level claims drift from source-of-truth data | Add new numeric claims to `bonus/data/facts.md` or phrase qualitatively |
| Appendix E and cheat sheet drift apart in detail | U7 explicitly depends on U6 — write Appendix E first, derive the cheat sheet from it; alignment is a verification step |
| Core assignment answer gets diluted | Preserve the cooled MWIR vs uncooled LWIR trade-off as the spine of the report and explicitly check whether new constraints weaken it |
| Source-of-truth data drifts | U8 consistency pass across report wording, `bonus/data/facts.md`, `bonus/data/precedent-search.md`, bonus README, demo/simulation assumptions |
| Interviewer asks about a low-level topic NOT in R7 | Out of scope. Cheat sheet's "Pivot moves" gives the author bridges back to documented content; an unanticipated topic gets a graceful "I haven't worked with that specifically — here's how I'd reason about it" answer rather than a fabricated one |

---

## Documentation / Operational Notes

- After implementation, rerun `cd bonus && uv run pytest tests/` if any bonus files change or if report assumptions that bonus tests/docstrings encode are revised.
- Run a final Markdown rendering check if submitting as PDF or Word.
- Consider one final doc-review pass focused specifically on system-engineering role alignment.

---

## Sources & References

- Existing report: `methane-ogi-payload-report.md`
- Original assignment transcription: `docs/technical-assignment.md`
- Requirements brainstorm: `docs/brainstorms/eo-payload-gas-detection-tech-assignment-requirements.md`
- Existing facts file (alignment reference): `bonus/data/facts.md`
- Existing precedent supplement (voice/format reference): `bonus/data/precedent-search.md`
- User-provided System Engineer job description in the 2026-05-08 planning conversation
- Jetson Orin Nano product brief, V4L2 documentation, Linux PREEMPT_RT documentation (load-bearing for any factual claims that survive into Appendix E or the cheat sheet)

---

*Plan merged on 2026-05-08 from the prior `refactor-system-engineer-role-alignment-plan` (gpt-5-5 originated) and `feat-low-level-platforms-supplement-plan` (claude-opus-4-7 originated). The supplement plan is superseded; its U1/U2 are absorbed as U6/U7 above.*
