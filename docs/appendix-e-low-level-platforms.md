# Appendix E — Low-Level Platforms Supplement

*Supporting material for `methane-ogi-payload-report.md`. The body's §5 names the embedded processor as "Jetson Orin Nano-class" and §7.6 frames the pipeline as a bounded runtime. This appendix documents the next layer down — sensor bus, real-time scheduling, driver-level NUC, DMA paths, firmware boot and watchdog, power management, gimbal MCU partition, and bring-up tooling — at the depth a system engineer needs to defend the architecture without committing to a specific carrier-board lane mapping.*

Each subsection leads with a one-line decision or working assumption, followed by 2-4 sentences of rationale. Factual claims about external behavior carry a tag:

- **(confirmed)** — verifiable against the named vendor's product brief or a public standard.
- **(assumed)** — working assumption that holds for the named class of hardware but is not yet pinned to a specific model.
- **(illustrative)** — example of what the integration would look like; not committed to.

## E.1 — Sensor-to-processor interface

**Working assumption: MIPI CSI-2 preferred when the selected uncooled-LWIR core and Jetson carrier board both support it; USB3 Vision is the fallback path; GigE Vision is the long-cable / multi-camera fallback.**

MIPI CSI-2 gives the lowest acquisition latency and lowest CPU overhead when the selected thermal core and carrier board expose compatible lanes; CSI support is confirmed for Jetson-class carriers, while end-to-end zero-copy DMA depends on the driver/media stack (assumed until demonstrated). The risk is that not every uncooled LWIR core ships with a MIPI CSI-2 output — many ship with USB3 Vision or GigE Vision interfaces — and the carrier board's CSI lane mapping has to match the core's lane count. USB3 Vision adds protocol-stack latency and CPU load but works on common Jetson carrier configurations (assumed). GigE Vision is preferred when cable lengths exceed USB3 limits or when fanning out to multiple cameras (illustrative). The interface choice is therefore conditional until the specific thermal core and carrier-board lane mapping are confirmed; the report's §5.7 interface-rate constraint (30-60 Hz at 14-bit per pixel for 640×512) fits comfortably within any of the three.

## E.2 — Real-time scheduling

**Working assumption: Linux user-space with PREEMPT_RT for the main image pipeline; gimbal control on a separate MCU.**

The §7 pipeline runs at 30-60 Hz with a per-frame budget of 16-33 ms. PREEMPT_RT is the right starting point for reducing Linux scheduling latency, but worst-case jitter on Jetson-class hardware is a measured property that depends on kernel version, power mode, CPU isolation, IRQ affinity, and carrier-board tuning (assumed, not pre-certified). A bare-metal RTOS would give tighter determinism but at the cost of losing the Linux user-space ecosystem the detection algorithm depends on (OpenCV, CUDA, NumPy). The gimbal PID loop has a fundamentally different deadline (sub-millisecond) and a different fault-isolation requirement: a crashed image pipeline must not cause the gimbal to lurch. That decoupling is why E.7 puts the gimbal on its own MCU rather than co-hosting it with the detection worker.

The end-to-end V3 latency budget (Appendix F) decomposes qualitatively into acquisition buffering, transfer over the chosen sensor bus, CPU scheduling under PREEMPT_RT, GPU / Tensor compute (the largest single cost, in line with the §8.4 ~20 ms target figure), encoding if performed on-module, and thermal-throttle headroom reserved for sustained-load conditions. The late-frame policy adds 0-1 frame of slip before the §7.6 deterministic fallback kicks in. Radio/video latency is platform-dependent and may be tens of milliseconds for low-latency links or 100-200+ ms for enterprise payload video. The 200 ms operator-budget envelope (V3) applies first to detection + metadata alarm and only to full video overlay after the integration benchmark is passed.

## E.3 — Driver-level NUC integration

**Working assumption: V4L2-style control plane where the core exposes one; vendor SDK where the V4L2 model is incomplete.**

The §6.3 NUC schedule is driven by filter-temperature drift, not fixed cadence. The application schedules NUC triggers and coordinates pipeline masking (the §7.3 flush-and-suppress window) around driver-level shutter actuation. V4L2 standard controls cover common camera settings such as exposure and gain where a kernel-mainline driver exposes them; thermal-camera NUC / shutter triggering is typically a vendor-specific control, private V4L2 extension, or SDK call (assumed until the selected core is known). The application layer treats NUC as an opaque "fire and wait" operation; nothing in §7's algorithm depends on reading proprietary calibration state back from the driver.

## E.4 — Buffer management and DMA

**Working assumption: avoidable copies are eliminated from sensor buffer to GPU / accelerator memory where the driver path supports it; pinned host memory for the rolling temporal background; ring-buffer depth sized for the §7.3 window plus margin.**

Jetson-class CPU/GPU memory sharing and media-buffer APIs make zero-copy or low-copy camera-to-CUDA paths feasible when the selected driver supports the required buffer exports; this is an implementation requirement to verify, not something the product brief alone guarantees. Pinning the rolling-median window in host memory avoids page faults during the temporal-background update. Ring-buffer depth is bounded: at 60 Hz with the §7.3 30-frame window, the queue holds ≤45 frames, comfortably within the Orin-class memory envelope (illustrative — exact byte sizing depends on bit depth and metadata overhead). Buffer-depth growth is forbidden by the §7.6 runtime invariant; producer-side drops increment the Appendix G dropped-frame counter rather than absorbing drift silently.

## E.5 — Firmware boot, watchdog, and recovery

**Working assumption: secure / signed boot from the selected storage path where supported; hardware watchdog with sub-second timeout; failure mode is "payload safed, airframe propulsion uncoupled."**

The compute module boots from the selected module / carrier storage path — for Orin Nano developer-class hardware this is typically microSD or NVMe rather than on-module eMMC — with secure / signed boot enabled where the deployment configuration supports it. A kernel-managed hardware watchdog kicked by the §7.6 worker heartbeat restarts the module if the pipeline stalls. Critically, a payload reboot must not cause an airframe upset — the §5.6 / E.6 power isolation means a reset has no propulsion-side effect, which is a certification simplification, not just a reliability point.

## E.6 — Power management

**Working assumption: payload power isolated from airframe propulsion bus; thermal throttling honored explicitly in the §7 pipeline; instant-on is a property of the uncooled architecture.**

§5.6 specifies a payload reserve module with conditioned airframe-bus feed; the deeper rationale is that propulsion-battery sag during climb-out must not undervolt the payload, and a payload current spike (NUC, radio burst, GPU peak) must not draw current the propulsion controllers expect. Thermal throttling follows the standard Linux `cpufreq` model; the §7.6 deterministic fallback observes throttle state via `/sys/class/thermal` and steps frame rate down before the kernel forces it. Instant-on is the structural advantage cooled MWIR lacks.

## E.7 — Gimbal MCU partition

**Working assumption: 2-axis gimbal driven by a dedicated Cortex-M-class MCU running PID at sub-millisecond cadence, communicating over CAN or UART, fault-isolated from the detection pipeline.**

Linux scheduler jitter is unacceptable for sub-millisecond PID even with PREEMPT_RT, so the gimbal moves to a small MCU running bare-metal or an RTOS task. CAN is the typical airframe-grade choice for noise immunity; UART is acceptable on short runs. A crashed detection worker leaves the gimbal MCU running its current target with last-known IMU state — no free-fall on pipeline restart.

## E.8 — Bring-up and debug tooling

**Working assumption: standard embedded-Linux bring-up stack — JTAG, oscilloscope, logic analyzer, vendor SDK demo apps — exercised on a development carrier board prior to airframe integration.**

JTAG covers boot-debug and low-level firmware init; oscilloscope on sensor clock and power rails confirms electrical integrity; logic analyzer captures bus transactions (CSI-2 packet timing, USB3 Vision triggers); vendor SDK demo apps validate camera-control paths (NUC, gain, exposure) end-to-end before the §7 algorithm sits on top. The plan is to clear all of this on a development carrier board first, then move the validated stack onto the airframe-integrated payload — the Appendix F V&V plan is the gating sequence.

## E.9 — Why this layer is presented as a supplement

The body's §5 architecture is correct at its level of abstraction: detector, optics, gimbal, processor, radio, power, operator overlay. The decisions in this appendix sit one layer below §5 — they are integration-engineering choices, not architecture changes. Readers who care about that layer have one place to look (this appendix) and a parallel cheat sheet in `bonus/data/low-level-talking-points.md` for live discussion. The architecture decision in §5 does not change if any working assumption in this appendix flips.
