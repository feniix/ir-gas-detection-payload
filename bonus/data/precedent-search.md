# Precedent search — uncooled LWIR + LWIR-band methane OGI

**Date:** 2026-05-08
**Outcome:** Architecture precedent found. Public 50-200 m range-performance data was not found, so the final report should frame the architecture as commercially validated and the range envelope as modeled.

---

## Question

Does at least one credible public deployment of *uncooled LWIR + LWIR-band narrowband-filter methane OGI* exist, and does public evidence establish the 50-200 m range envelope?

This question gates origin requirement R13b. The search found strong architecture/platform precedent, but not a public ppm·m detection curve at 50-200 m. The final report should therefore avoid claiming field validation of the exact range envelope.

---

## Searches conducted

| Query | Source | Notable hits |
|---|---|---|
| "uncooled LWIR methane optical gas imaging" | Exa web search | FLIR GF77 datasheet (FLIR support); MFE Detect LW (LWIR OGI for DJI drones) |
| "FLIR GF77 LWIR methane detection" | Exa | FLIR GF77 LR/HR family — uncooled, 7-8.5 µm, methane filter |
| "UAV drone uncooled longwave methane survey" | Exa | MFE Detect LW (DJI M300/M350 payload; M400 listed on some public pages); supplementary trade reports |
| "Appendix K OGI methane camera certification" | Exa | EPA 40 CFR Part 60 Appendix K — applies to both cooled and uncooled cameras meeting the 19 g/hr at 2 m benchmark |

---

## Precedents found

### 1. FLIR GF77 / GF77a (production since ~2019, Teledyne FLIR)

- Spectral range: **7-8.5 µm** (LR variant, methane-filtered)
- Detector: uncooled microbolometer (public GF77/GF77a methane-filtered pages checked here list 320×240 IR resolution and 25 µm detector pitch)
- Operating model: handheld / fixed-camera ground-based; not natively UAV-mounted but demonstrates the methane-filtered uncooled-LWIR architecture
- Public performance spec: methane NECL <100 ppm·m at ΔT = 10 °C and distance = 1 m for the 7-8.5 µm LR configuration
- Compliance: public pages checked here do **not** visibly document EPA Appendix K compliance for GF77/GF77a; do not cite GF77 as an Appendix K compliance precedent without a separate certification document
- Source: https://support.flir.com/DsDownload/Assets/85204-0102-en-US.html (FLIR GF77 LR datasheet, accessed 2026-05-09) and https://www.flir.com/products/gf77a/

This is the foundational uncooled LWIR methane OGI camera. Existence of the GF77 line proves that:
1. Uncooled microbolometer + LWIR-band narrowband filter is a viable methane-visualization architecture.
2. The 7-8.5 µm passband is industry-validated for methane OGI.
3. The "uncooled cannot do methane OGI" objection is dated.

### 2. MFE Detect LW (UAV payload, in production)

- Platform: payload for **DJI Matrice M300, M350** drones, with **M400** compatibility stated on some public pages
- Detector: uncooled LWIR microbolometer
- Filter: methane-specific narrowband
- Compliance: EPA OOOOa, OOOOb, OOOOc, Appendix K **per vendor docs**; no independent public certification / field-curve packet located in this search
- Application: aerial methane survey for upstream/midstream/downstream oil & gas, landfills, processing units, storage tanks, well pads
- Source: https://mfe-is.com/en_ca/product/mfe-detect-lw/

**This is the single strongest precedent** for the recommendation — a deployed, vendor-stated regulator-compliant, UAV-integrated uncooled LWIR methane OGI system. It validates the architecture and platform integration path, while leaving the exact 50-200 m performance curve and independent compliance evidence to be modeled, requested from the vendor, or field-tested.

### 3. Other uncooled OGI references (lighter)

- Workswell WIRIS family (general uncooled LWIR thermography on UAVs — not gas-filtered, but demonstrates UAV+uncooled+long-mission-duration integration is mature).
- MultiSensor Scientific HEAT (multispectral SWIR/LWIR; relevant adjacent technology, not pure uncooled-LWIR).
- Various oil & gas service-company offerings using GF77-class hardware in vehicle-mounted or fixed configurations (e.g., third-party mods to the GF77 for permanent monitoring).

---

## Caveat — what the precedents do NOT prove

- They prove the *architecture* is deployable, not that it achieves the same sensitivity as cooled MWIR. The report should still cite the empirical sensitivity gap (Ravikumar findings — see facts.md §5.2) and explain that uncooled LWIR is best positioned for *survey* (find leaks worth fixing) rather than *quantification* (regulatory-grade emission rate measurement).
- MFE Detect LW's exact ppm·m floor at 50-200 m altitude is not in the public datasheet at this time of search. Vendor literature gives operational claims rather than published detection-curve data. The companion simulation produces our own modeled floor; the precedent supports the architecture choice but does not provide a calibration anchor.

---

## Interviewing-company platform-tribe check

**Status:** open. The plan included this as a coupled task with the precedent search but it is independent — the user identifies the company at submission time. Working assumption for plan continuation: company is UAV-tolerant or UAV-centric (consistent with the GF77 / MFE Detect LW landscape). If the company turns out to be fixed-station-centric (Bridger Photonics-style aircraft-borne, Project Canary-style fixed sensors, Kairos-style aircraft), the recommendation flips per the plan's hard gate.

This is a 30-minute LinkedIn / company-page check the author runs immediately before drafting §1-§2. Not in scope for this research session.

---

## Conclusion

**Recommendation in origin R12 / R13b stands as architecture-validated, with range performance modeled.** The trade-off section can cite MFE Detect LW (UAV) and FLIR GF77 (handheld/ground) as deployed precedents that establish:

1. Uncooled LWIR + narrowband filter at 7-8.5 µm is a working architecture for methane OGI.
2. UAV integration of uncooled LWIR methane OGI is in commercial deployment.
3. MFE carries vendor-stated Appendix K / OOOO compliance claims for an uncooled-LWIR UAV payload, while Appendix K remains a 2 m viewing-distance benchmark rather than validation of the report's 50-200 m envelope.

The final report should present the architecture as deployable and commercially precedented, but the 50-200 m performance claim as a modeled engineering estimate requiring field validation.
