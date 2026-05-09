---
title: Low-level platforms — interview talking points
status: prep artifact (not part of the formal deliverable)
---

# Low-level platforms — interview talking points

A scannable Q&A cheat sheet for live discussion of the low-level / embedded / firmware layer covered formally in **Appendix E** of `methane-ogi-payload-report.md`. Voice is terse, designed to be readable in the room. Every answer aligns with Appendix E's working assumptions; if the interviewer takes the discussion deeper than this sheet covers, fall back to the **Pivot moves** at the bottom rather than improvising.

## Embedded / firmware

**Q: How does the bolometer connect to the processor?**
MIPI CSI-2 preferred when the core and Jetson carrier both support it (lowest latency, DMA-mapped). USB3 Vision is the fallback; GigE Vision for long-cable or multi-camera setups. Interface is conditional until carrier-board lane mapping is confirmed — see Appendix E.1.

**Q: What's your real-time scheduling story?**
Linux user-space with PREEMPT_RT for the image pipeline at 30-60 Hz; gimbal control on a separate MCU at sub-millisecond cadence. PREEMPT_RT is the starting point, but jitter is measured after carrier/kernel tuning (power mode, IRQ affinity, CPU isolation) before I claim it meets 16-33 ms frame deadlines.

**Q: What happens if a frame is late?**
Deterministic, documented fallback. Per-frame compute is gated by a 28 ms soft deadline; on sustained overrun the pipeline drops 60 Hz → 30 Hz, then drops cross-modal feature refinement and falls back to IMU-only registration. Operator sees the mode change in telemetry — no surprises.

**Q: How is the gimbal partitioned?**
Dedicated Cortex-M-class MCU running PID at sub-millisecond cadence, communicating with the main processor over CAN or UART. Fault-isolated: a crashed detection worker leaves the gimbal MCU on its last target with last-known IMU state — no free-fall on pipeline restart.

**Q: What does the firmware boot sequence look like, and how do you handle a crashed payload?**
Signed boot from the selected module/carrier storage path — Orin Nano dev-class hardware is typically microSD or NVMe, not on-module eMMC. Hardware watchdog kicked by the §7.6 worker heartbeat; payload power isolated from airframe propulsion. A payload reset is contained — the flight controller is unaffected.

## Driver / OS

**Q: How do you do NUC at the driver level?**
V4L2-style controls where the core exposes them; vendor SDK where V4L2 is incomplete. The application layer treats NUC as opaque "fire and wait" — schedule the trigger, mask the §7.3 flush-and-suppress window in the algorithm. No proprietary calibration-state readback assumed.

**Q: What's your DMA / buffer-management story?**
Zero-copy or low-copy from the sensor buffer to GPU / accelerator memory where the selected driver exposes compatible media buffers; pinned host memory for the §7.3 rolling-temporal background; bounded ring-buffer depth (~45 frames at 60 Hz with margin). Producer-side drops increment the dropped-frame counter — buffers do not grow under drift.

**Q: How do you handle thermal throttling?**
Standard Linux `cpufreq` model. The §7.6 deterministic fallback observes throttle state via `/sys/class/thermal` and steps frame rate down *before* the kernel forces it. Pipeline visibility into thermal state is a runtime invariant, not an afterthought.

**Q: What's the bring-up tool stack?**
JTAG for boot debug; oscilloscope on sensor clock and power rails for electrical integrity; logic analyzer for bus protocol debug (CSI-2 packet timing, USB3 Vision triggers); vendor SDK demo apps for camera-control validation. All exercised on a development carrier board before airframe integration.

## Languages and process

**Q: What language is this written in?**
Body algorithm and the runnable demo are Python (NumPy/SciPy). A production payload would likely split: **C++** for performance-critical pipeline stages and gimbal MCU firmware, **Python** for prototyping / testing / ground-station tools, and **C#** only if the operator UI lands on a Windows ground-control framework. Language choice follows the deadline — Python where interpreter overhead is tolerable, C++ where it is not.

**Q: What's your prior experience with C++ / C# specifically?**
*Fill in honestly with named past projects, embedded contexts, or codebases. Map prior C++ experience to gimbal MCU firmware or pipeline stages where it is most relevant; map prior C# experience to tooling, operator UI, or Windows-side ground-station work if applicable. If C# experience is thin, say so directly — "I read C# fluently but my production work has been in C++ and Python" is a defensible answer; "I'm a C# expert" without backing is not.*

**Q: How would you split work between the system engineer and a firmware engineer?**
System engineer owns architecture, V&V plan, integration interfaces, runtime posture (the body of the report, plus Appendix F verification and Appendix G diagnostics). Firmware engineer owns driver bring-up, MCU firmware, board-level signal integrity, and the parts of Appendix E flagged as "needs vendor SDK" or "depends on carrier board." This split keeps the system engineer accountable for the *whole* deliverable while letting the firmware specialist do the deep board-level work.

## Things to be honest about

Items the author should NOT bluff. Better to say "I haven't worked with that specifically; my reasoning would be …" than to fabricate.

1. **Specific FPGA toolchains** (Vivado, Quartus). The deliverable does not depend on FPGA work; if the conversation pulls toward FPGA bring-up, route it back to the V&V plan and the supplier's responsibility for board-level signal integrity.
2. **Vendor-proprietary protocols** for specific thermal cores (FLIR legacy serial, Workswell SDK, Lepton I²C register maps). The cheat sheet's V4L2 / vendor-SDK posture is correct at the architecture level; specific vendor protocols are a build-time integration cost, not a design-decision blocker.
3. **Depth of prior C++ / C# experience.** Name what is true, not what sounds impressive. The role wants credible architectural fluency in the implementation languages, not front-line authoring of every commit.
4. **Specific PREEMPT_RT jitter numbers on this carrier.** PREEMPT_RT behavior is well-documented in general; the exact jitter on a specific Jetson Orin Nano carrier depends on board tuning and is a measurement, not a citation.
5. **Cooled-MWIR cryocooler MTBF on a specific airframe.** The body cites class-level MTBF ranges (linear Stirling ~20-30 kh, rotary ~10-15 kh); a specific airframe vibration spectrum could push that lower, which is a field-measurement question, not a literature one.

## Pivot moves

When the interviewer takes the conversation toward something this cheat sheet does not cover, route back to documented content rather than improvising.

1. **"That specific question is outside my direct experience — let me reason about it from the architecture."** Walk back through §5 (architecture) → §7 (algorithm) → Appendix F (V&V) → Appendix E (low-level). The deliverable's structure *is* the reasoning framework; using it explicitly is more defensible than guessing.
2. **"I'd want to see real measurements before committing to a number — here's what I'd test."** Map the question to the closest V9-V14 proposed verification target in Appendix F. Naming test conditions and pass criteria is a stronger move than improvising a specific number.
3. **"That trade-off is mission-conditional — here are the conditions under which the answer flips."** §4.4 enumerates conditions where cooled MWIR is the right choice instead. The same posture works for low-level decisions: name the working assumption, name what would flip it.
4. **"The body covers posture; the appendix covers specifics."** If the question pulls below the body's level of abstraction, point at Appendix E. If it pulls below Appendix E, name the test that would resolve it.
