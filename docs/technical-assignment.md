# Technical Assignment — EO Payload for Gas Detection (Cooled vs Uncooled)

Transcribed from the original assignment prompt.

---

## Objective

Design an electro-optical payload for remote gas detection using thermal imaging technologies, comparing cooled MWIR systems and uncooled LWIR systems.

This task evaluates your ability to:

- Design a complete EO payload (not just a sensor)
- Understand IR physics and gas absorption
- Perform trade-offs between cooled and uncooled technologies
- Define a realistic, deployable system

## Scenario

You are designing an EO payload to be mounted on:

- A small UAV, or
- A fixed ground-based monitoring station

The system must:

- Detect gas plumes (e.g., methane, CH₄) at 50-200 meters
- Provide visual indication + detection alert
- Operate in day/night outdoor environments

## Technical Scope

### 1. Detection Concept — Thermal-Based Gas Imaging

Explain the physical principle behind gas detection using thermal imaging:

- Spectral absorption/emission of gases in IR
- Passive imaging vs active approaches

You should explicitly relate your concept to explaining how this law translates into:

- Contrast formation of thermal images
- Detectability of gas plumes

### 2. Payload Architecture

Define a complete EO payload, including:

- Thermal camera (cooled or uncooled)
- Optics (lens, filters)
- Stabilization (if UAV-mounted)
- Processing unit
- Power system
- Communication interface

### 3. Cooled vs Uncooled Trade-off Analysis

This is a core part of the task.

Compare:

- Cooled thermal camera (MWIR)
- Uncooled thermal camera (LWIR)

Analyze differences in:

- Sensitivity (NETD)
- Spectral suitability for gas detection
- Spatial resolution vs noise
- Response time
- Size, weight, and power (SWaP)
- Cost and maintenance
- Operational constraints

Conclude:

- Which technology you would choose for this mission
- Under what conditions the other technology would be preferable

### 4. Optical Design and Spectral Considerations

Discuss:

- Relevant absorption bands
- Filter selection (narrowband vs broadband)
- Lens material (e.g., germanium, silicon)

Explain how spectral alignment impacts:

- Detection sensitivity
- False alarms

### 5. Detection Algorithm

Describe your processing pipeline:

- Image acquisition
- Background estimation
- Gas plume enhancement
- Detection logic

Discuss:

- False positives (hot objects, reflection)
- Noise sources (sensor, environment)

### 6. Performance Estimation

Provide engineering-level estimates for:

- Minimum detectable concentration
- Detection range vs conditions
- Frame rate requirements

You may include simplified assumptions.

## Deliverables

1. Technical report (10-15 pages)
2. Block diagram and sketches
3. Optional bonus:
   - Simple simulation (e.g., contrast vs concentration)
   - Example detection algorithm (pseudo-code or Python)

## Evaluation Focus

- Depth of EO understanding
- System thinking
- Trade-off clarity
- Practical realism
- Clear engineering communication

## Time Expectation

Two weeks.
