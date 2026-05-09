# Cited facts — methane OGI EO payload

**Status:** working draft built from public literature, 2026-05-08; fact-check pass updated 2026-05-09. Every quantitative claim in the report should trace to an entry here. If a number is missing or listed as a hardening/procurement check, do not cite it as final vendor performance without confirming.

**Conventions:** wavelengths in µm, wavenumbers in cm⁻¹. Band intensities are integrated over the band at 296 K and one atmosphere unless noted. NETD is at f/1.0, 300 K scene unless noted.

---

## 1. Methane absorption — band positions and integrated intensities

Methane (CH₄) is a tetrahedral symmetric-top molecule. Of its four fundamental vibrations, only **ν₃** (asymmetric C-H stretch) and **ν₄** (asymmetric C-H bend) are infrared-active and operationally useful for thermal-IR optical gas imaging.

| Band | Center (cm⁻¹) | Center (µm) | Working passband (µm) | Integrated-intensity scale (cm⁻² atm⁻¹, 296 K) |
|---|---|---|---|---|
| ν₃ asymmetric stretch (MWIR) | ≈ 3019 | **3.31** | 3.20-3.40 | **few-hundred** |
| ν₄ asymmetric bend (LWIR) | ≈ 1306 | **7.66** | 7.40-8.00 | **low-hundreds** |

**Sources for band intensities:**
- HITRAN2020 line list — Gordon et al., *The HITRAN2020 molecular spectroscopic database*, JQSRT 277, 107949 (2022). DOI: 10.1016/j.jqsrt.2021.107949.
- Methane line parameters in HITRAN: Brown et al., *Methane line parameters in the HITRAN2012 database*, JQSRT 130, 201-219 (2013). DOI: 10.1016/j.jqsrt.2013.06.020.
- Heicklen, *Integrated infrared intensities of methane*, JQSRT 37(2), 107-110 (1987). DOI: 10.1016/0022-4073(87)90013-6 — primary reference for the original ν₃ and ν₄ integrated intensities.

**Working band-intensity ratio (ν₃ / ν₄):** few× rather than 10×. This is a literature-scale / engineering-model input, NOT a final passband-weighted measurement; exact values depend on filter shape, pressure broadening, temperature, and atmospheric path and should be recomputed from HITRAN / PNNL spectra before detailed radiometric design.

**Important correction to widely-quoted "10×" claim:** the popular shorthand that methane's 3.3 µm band is "10× stronger" than its 7.6 µm band is more representative of comparing strongest individual lines than integrating over an OGI filter passband. The report's trade-off section should frame the ratio as a few× engineering assumption, not a precisely computed passband result.

**Reference spectra source for the companion simulation:** PNNL Northwest Infrared (NWIR) gas-phase library — quantitative IR spectra at 0.1 cm⁻¹ resolution, N₂-broadened to 1 atm.
- Sharpe et al., *Gas-phase databases for quantitative infrared spectroscopy*, Applied Spectroscopy 58(12), 1452-1461 (2004). DOI: 10.1366/0003702042641281.
- Brauer et al., *The Northwest Infrared (NWIR) gas-phase spectral database of industrial and environmental chemicals: Recent updates*, Proc. SPIE 9106, 910604 (2014). DOI: 10.1117/12.2053591.
- HITRAN portal: https://hitran.org. PNNL portal: https://nwir.pnl.gov.

---

## 2. Atmospheric transmittance and the water-vapor problem

Both filter passbands sit inside atmospheric transmission windows but with different water-vapor profiles.

**3.2-3.4 µm (MWIR):** mostly clean window, with weak H₂O lines and a CO₂ shoulder at the long-wave edge. Atmospheric transmittance over a 100 m horizontal path at sea level, standard atmosphere ≈ **0.85-0.95**. Solar contribution at 3.3 µm is non-trivial in daytime (this is also why MWIR is sun-sensitive — see §7).

**7.4-8.0 µm (LWIR):** the LWIR window's *short-wavelength edge*, which is more contested by water-vapor absorption than the central 9-12 µm region. The H₂O continuum (Roberts-Selby and successors) plus discrete H₂O lines reduce transmittance noticeably. Atmospheric transmittance over 100 m at standard atmosphere ≈ **0.80-0.90**; humid (tropical) atmosphere can drop this to **0.65-0.80**. At 200 m and humid conditions, expect another ~10-15 % reduction.

**Sources:**
- Roberts, Selby, Biberman, *Infrared continuum absorption by atmospheric water vapor in the 8-12 µm window*, Applied Optics 15(9), 2085-2090 (1976). DOI: 10.1364/AO.15.002085 — classic reference for H₂O continuum.
- Modtran-style atmospheric profiles (US Standard Atmosphere 1976; Mid-Latitude Summer; Tropical) — typical short-path transmittance values from any standard atmospheric optics text (Hudson 1969, Wolfe & Zissis 1989, or current USAF Geophysics Laboratory documentation).
- HITRAN2020 (above) for line-by-line if needed.

**Operational implication:** the report may use τ_atm ≈ 0.85 at 100 m as an illustrative standard-atmosphere working baseline, with dry/humid sensitivity bounds, but these are design-envelope assumptions requiring MODTRAN / HITRAN line-by-line validation for the selected passband, altitude, humidity, and site conditions.

---

## 2.5 Optical-material notes for §6.2

- **Germanium:** common LWIR lens material with broad IR transmission and high refractive index; AR coating is required because the index is high. Baseline choice for this payload because it gives comfortable margin across the 7.7-8.0 µm methane band and adjacent LWIR optical train.
- **Silicon:** not absolutely ruled out at 7.7-8.0 µm. High-resistivity / float-zone silicon can transmit near this edge band, but it has less broad-LWIR margin than Ge and grade/coating selection matters. Treat as secondary procurement trade, not baseline.
- **ZnSe:** broadband and non-hygroscopic, but mechanically softer / less rugged and requires careful coating/handling. Do not call it hygroscopic; do not claim it is necessarily more expensive than Ge in current supply conditions.

**Sources:** Crystran Germanium / Silicon / Zinc Selenide material pages; Edmund Optics ZnSe optics notes; optical-material handbooks.

---

## 3. Detector NETD ranges (current generation, 2024-2026)

### 3.1 Cooled MWIR photon detectors (3-5 µm)

| Detector type | Operating temperature | NETD (typical) | Pixel pitch | Resolution range |
|---|---|---|---|---|
| InSb (legacy industry standard) | 77 K | **15-25 mK** | 15 µm | 320×256 to 1280×1024 |
| HgCdTe (MCT, mercury-cadmium-telluride) | 77-110 K | **10-20 mK** | 12-15 µm | 640×512 to 2048×2048 |
| Type-II Strained Layer Superlattice (T2SL, modern HOT) | 110-150 K | **20-30 mK** | 10 µm | up to 1280×1024 |

**Key reference (modern T2SL HOT detector):** IRnova *Njord MW* — 1280×1024, 10 µm pitch, T2SL, 150 K HOT operation, 60 Hz. Demonstrates the modern direction for SWaP-reduced cooled MWIR.
- Source: https://www.irnova.se/t2sl-njord-mw (accessed 2026-05-08).

**Reliability/lifetime references:**
- Griot et al., *Cryogenic solutions for IR detectors — a guideline for selection*, Opto-Electronics Review 31, e144566 (2023). DOI: 10.24425/opelre.2023.144566 — Thales / IRnova authors. Discusses Stirling rotary vs linear coolers and the RMs1 cooler family.

### 3.2 Uncooled LWIR microbolometers (8-14 µm; methane-band use requires verified 7.7-8.0 µm transmission)

| Detector technology | Pixel pitch | NETD (typical, f/1.0, 300 K, ≤60 Hz) |
|---|---|---|
| Vanadium oxide (VOx) microbolometer, modern | 12 µm | **< 40 mK** |
| Vanadium oxide (VOx) microbolometer, modern | 17 µm | **< 50 mK** |
| Amorphous silicon (a-Si) microbolometer | 12-17 µm | **40-60 mK** |

**Key reference (current-gen uncooled detector):** Raytron *OHLE3123* — 384×288, 12 µm pitch VOx, NETD < 40 mK at f/1.0 25 Hz 300 K, spectral range 8-14 µm. Representative of modern wafer-level-packaged uncooled cores, but not by itself proof that a packaged thermography core transmits the 7.7-8.0 µm methane passband.
- Source: https://www.raytron-microelectronics.com/uncooled-lwir-modules/ohle3123-uncooled-infrared-focal-plane-detector (accessed 2026-05-08).

**Methane-band window caution:** the payload must select an extended-response / methane-band-qualified uncooled core and window stack with measured transmission at 7.7-8.0 µm. FLIR GF77/GF77a and MFE Detect LW prove that methane-band uncooled LWIR architectures exist, but a generic 8-14 µm thermography core is not sufficient evidence for this passband.

**Working assumptions for the report:**
- Cooled MWIR NETD: **25 mK** (working value), range 15-25 mK
- Uncooled LWIR NETD bare-sensor: **40 mK** (working value), range 35-50 mK
- Uncooled LWIR effective NETD with warm-filter penalty: **50 mK** working value used by the report and simulation; **50-65 mK** remains the sensitivity range to validate in prototype radiometric testing.

---

## 4. Cryocooler reliability and SWaP

### 4.1 MTBF (mean time between failures)

- **Linear Stirling tactical coolers:** typical MTBF **~20,000-30,000 hours** at room ambient (some modern units claim 30k-40k); rotary Stirling **legacy class ~10,000-15,000 hours**, with modern industry rotaries (e.g., Thales **RMs1**, **RM2**) reporting **≥30,000-50,000 hours** MTTF per recent SPIE / Opto-Electronics Review literature (Cauquil et al. 2017 SPIE 10626; Griot et al. 2023 Opto-Electron Rev 31; Durupt 2024 SPIE 13046). Both classes degrade with elevated ambient and vibration loading.
- **Source:** Griot et al. (above) discusses tactical Stirling cooler reliability targets and the rotary-vs-linear trade. Specific MTBF figures are typically in vendor datasheets — Thales Cryogenics, AIM, Lockheed Martin, Sumitomo all publish similar ranges.

### 4.2 Cool-down time

- Tactical Stirling coolers: **3-6 minutes** to operating temperature for representative camera engines (faster for HOT-T2SL ~150 K, slower for full 77 K InSb / larger engines).
- Uncooled bolometers: **instant-on** (<1 s warmup to imaging; longer thermal stabilization is for radiometric accuracy, not basic imaging).

### 4.3 Mass and power

- Tactical cooled MWIR camera-engine class (sensor + dewar + Stirling cooler + drive electronics, no optics): **~0.4-1.0 kg, 6-15 W steady-state, ~25-30 W during cool-down**. Larger (>2 kg, >25 W) for high-resolution / extended-mission systems.
- Uncooled LWIR camera-engine class: **~30-100 g, <1 W (typical 0.5-1 W), instant-on**.
- This is the SWaP gap the trade-off section leans on. Roughly **10× mass and 5-10× power** in favor of uncooled.

---

## 5. Methane context and OGI sensitivity literature — empirical reality vs vendor specs

### 5.0 Climate / emissions context used in §2.1

- **Methane GWP:** IPCC AR6 fossil-methane 20-year GWP ≈ **82.5×** CO₂ (non-fossil ≈ 80.8×); 100-year GWP ≈ 29.8× fossil / 27.2× non-fossil. The older "84×" shorthand traces to AR5-with-feedback, not AR6 — avoid it unless explicitly framed as AR5 context.
- **U.S. source ranking:** EPA inventory context identifies agriculture as the largest U.S. methane-emitting sector; petroleum and natural-gas systems are the largest industrial methane source and a major controllable LDAR target. Do not write that oil & gas is the single largest anthropogenic U.S. methane source.
- **Heavy-tailed oil-and-gas emissions:** peer-reviewed aerial and site-level studies show strongly skewed emissions distributions, but the exact superemitter share varies by basin, instrument threshold, and study design. Use qualitative "small fraction / large share" wording unless citing a specific basin and threshold.
- **Regulatory split:** NSPS OOOOa / OOOOb / OOOOc carry LDAR obligations for covered oil-and-gas facilities. 40 CFR Part 98 Subpart W is greenhouse-gas reporting for petroleum and natural-gas systems, not itself a periodic LDAR survey mandate.

**Sources:** EPA Methane Emissions page; EPA Sources of Greenhouse Gas Emissions; IPCC AR6 / GHG Protocol AR6 GWP tables; Sherwin et al. 2024 *Nature* aerial measurements; EPA/eCFR Subpart W.

### 5.1 Regulatory threshold (the floor a deployed system must meet)

**EPA 40 CFR Part 60, Appendix K** — *Determination of Volatile Organic Compound and Greenhouse Gas Leaks Using Optical Gas Imaging*. Quantitative requirement (verbatim from §6.1.2):

> The OGI camera must be capable of detecting (or producing a detectable image of) **methane emissions of 19 grams per hour (g/hr)** ... at a viewing distance of **2.0 meters** and a delta-T of **5.0 °C** in an environment of calm wind conditions around 1 meter per second (m/s) or less.

- Source: 40 CFR Part 60, Appendix K. https://www.ecfr.gov/current/title-40/part-60/appendix-Appendix%20K%20to%20Part%2060
- Effective for compliance with NSPS subparts OOOOa, OOOOb, OOOOc.

**Operational implication for our payload:** at 50-200 m viewing distance (much further than the 2 m benchmark), achieving Appendix K-equivalent sensitivity requires either superior intrinsic camera sensitivity, longer integration, or accepting that the system is for *survey* (find big leaks fast) rather than *compliance verification* at the 19 g/hr floor. The report should be honest about this — survey-grade sensitivity is the achievable target at the stated range.

### 5.2 Empirical detection limits — Stanford / Ravikumar

**Key paper #1: "Good versus Good Enough?"** — Ravikumar et al., 2017/2018.
- Result: **median 50% detection limit ≈ 20 g CH₄/hr at 6 m imaging distance** for FLIR-camera-based OGI (cooled MWIR, GF320-class). One *order of magnitude higher* than vendor-quoted ~1.4 g/hr.
- Detection probability follows a **power-law in imaging distance** — sensitivity degrades strongly with range.
- Operational regime where periodic OGI surveys are effective: median detection limit of ~100 g/hr can be useful in heavy-tailed emissions landscapes, but basin coverage depends on site distribution, wind, distance, and survey protocol. Avoid saying a modeled ppm·m floor "covers most superemitters" without field validation.
- Source: http://eao.stanford.edu/publications/journal-articles/good-versus-good-enough-empirical-tests-methane-leak-detection. DOI: see paper.

**Key paper #2: "Are Optical Gas Imaging Technologies Effective For Methane Leak Detection?"** — Ravikumar, Wang, Brandt.
- Result: **>80% of emissions detectable from 10 m** in simulated well-site conditions (cooled MWIR).
- *Imaging distance is the most important parameter* affecting IR detection effectiveness.
- *Land-based detection against sky or low-emissivity backgrounds has higher detection efficiency than aerial measurements.*
- Source: https://eao.stanford.edu/publications/journal-articles/are-optical-gas-imaging-technologies-effective-methane-leak-detection.

**The aerial-vs-land caveat is critical for our UAV-at-50-200 m thesis** — the report must own this and explain how UAV altitude is chosen for *coverage* and *access* (dispersed assets, no fixed infrastructure) rather than for raw detection sensitivity. The recommendation is for a survey-grade tool, not a regulatory-quantification-grade tool.

### 5.3 ppm·m sensitivity — practical numbers

- Cooled MWIR OGI (GF320-class) under good conditions: typically cited **~100-500 ppm·m** column density floor.
- FLIR GF77/GF77a-class uncooled LWIR public datasheets list methane **NECL <100 ppm·m** for the LR 7-8.5 µm configuration at **ΔT = 10 °C, distance = 1 m**. That is a close-range product specification, not a UAV-standoff field curve.
- Practical field floors at UAV standoff remain scenario-dependent; column density and mass-flow-rate are different units and conversion depends on plume geometry.

---

## 6. Worked CL_min comparison (the trade-off math)

The contrast detection relation, in apparent-ΔT space:

**CL_min ≈ NETD / (α · ΔT)**

where α is the band-integrated absorption coefficient at the chosen narrowband filter (in units consistent with CL in ppm·m), ΔT is the scene-to-plume thermal differential, and NETD is in K.

### 6.1 Substitute working values

| Quantity | Cooled MWIR @ 3.3 µm | Uncooled LWIR @ 7.6-8.0 µm |
|---|---|---|
| NETD (working) | 25 mK | 40 mK (50 mK with warm-filter penalty) |
| α (engineering-calibrated model value) | 2.5 × 10⁻⁵ per ppm·m | 1.0 × 10⁻⁵ per ppm·m |
| α ratio (MWIR / LWIR) | **≈ 2.5** engineering model value | (reference) |
| Effective CL_min (relative to LWIR's 1.0) | **0.16-0.20** (MWIR is ~5-6× more sensitive in CL_min terms) | 1.0 |

Plug-and-play numerical example, using the literature-anchored 200 ppm·m cooled-MWIR floor at favorable ΔT (Stanford-class):

- **Cooled MWIR @ 5 K ΔT:** CL_min ≈ 200 ppm·m
- **Uncooled LWIR @ 5 K ΔT:** CL_min ≈ 200 · (40/25) · 2.5 = **800 ppm·m** (bare-sensor)
- **Uncooled LWIR @ 5 K ΔT, with warm-filter penalty:** CL_min ≈ 200 · (50/25) · 2.5 = **1000 ppm·m**

These numbers are the order-of-magnitude framing. The companion simulation produces the actual plot at multiple ΔT values; this table is the back-of-envelope check that the simulation should land near. **Important — the gap between cooled and uncooled is ~5-6×, not the 16-25× implied by the brainstorm's "10× absorption" assumption.** This is the credibility-multiplier insight for the trade-off section.

### 6.2 Why the gap is closeable

The 5-6× CL_min gap is not the whole story. At the operational level:
- ΔT = 5 K nominal / 10 K favorable / 3 K stress are modeled cases. Real thermal contrast varies widely and is often the limiting condition; do not present 5-15 K as guaranteed field typical without site data.
- Modern uncooled cores at 12 µm pitch with low-NETD VOx push toward **30-35 mK NETD**.
- Background-modeling + temporal averaging in the algorithm pipeline gives an additional **2-3× effective NETD reduction** for fixed plumes (the plume is dynamic, the background is static — temporal differencing benefits the dynamic signal).
- For *survey* applications (find leaks worth fixing, not regulatory-grade quantification), a 1000 ppm·m floor is operationally plausible for compact high-emission plumes, but exact superemitter capture rates require field validation.

---

## 7. Solar contamination — the honest distinction

The brainstorm doc rightly flagged that "uncooled LWIR has lower solar contamination" is too glib. The honest articulation:

- **Band-integrated solar contribution.** At λ < 3 µm the sun's blackbody peak (5800 K, peak ~0.5 µm) dominates; at 3-5 µm there is still meaningful solar contribution; at 8-14 µm the solar contribution is **2-3 orders of magnitude smaller** because the long-wavelength tail of the solar Planck is far weaker than 300 K background self-emission.
- **Specular-glint pixel saturation.** Direct sunlight reflected off a metal pipe or vehicle windshield can saturate a pixel regardless of band, because it's a localized very-bright source. Narrowband filters help (most solar power is *outside* the methane filter passband) but don't eliminate the issue. This is the issue in MWIR specifically, where a broadband-filter MWIR camera can see strong reflections.
- **What our narrowband 7.7-8.0 µm uncooled filter actually mitigates:** the band-integrated solar issue (small contribution to begin with at LWIR), AND further reduced by the narrowband filter rejecting most of the already-small solar tail. Specular glint is partially mitigated by the narrowband filter rejecting most solar wavelengths but still possible at the filter passband — operational mitigation (sun-shading of optics, field-of-view planning) is required regardless.

**Source for solar-MWIR issue:** Ravikumar et al. discusses imaging backdrop effects; "land-based detection against sky or low-emissivity backgrounds have higher detection efficiency" alludes to this. Detailed solar-contamination treatment in OGI: Strecker et al. (multiple papers on OGI false alarms — to locate at write-time).

---

## 8. Vibration tolerance — the honest distinction

- **Cryocooler bearing wear / vibration sensitivity.** Stirling rotary coolers have moving piston/displacer components on bearings. Externally applied vibration (from a UAV) couples into the cooler and accelerates bearing wear. Linear coolers are somewhat better (flexure-bearing designs are inherently low-friction) but still have moving mass. Bearing wear is the dominant cryocooler failure mode and the reason MTBF degrades on a vibrating platform.
- **Bolometer thermal smear under high-frequency vibration.** Microbolometer thermal time constant is **~5-15 ms** in current literature (Raytron OHLE3123 spec: <15 ms; FLIR microbolometer support page: 7-12 ms; SCD VOx: ~10 ms slow / 5 ms fast pixel; GST212W: <12 ms). Vibration at frequencies near 1/τ_thermal can cause integration smearing. Small-UAV blade-pass and structural modes are airframe-specific and often in the hundreds of Hz; gimbal + EIS can mitigate high-frequency content, but the selected airframe spectrum must be measured before claiming smear is non-limiting.
- **Operational consequence.** On a small UAV in hover or moderate flight, the cryocooler bearing-wear issue is the dominant reliability factor for cooled MWIR; uncooled bolometer thermal smear is *not* dominant. This is the unambiguous part of the "vibration tolerance" advantage.

**Source:** Griot et al. (2023) on cooler reliability; bolometer thermal time constant and frequency response is in any IR detector textbook (Kruse, *Uncooled Thermal Imaging Arrays, Systems, and Applications*, SPIE Press, 2001; or Rogalski, *Infrared Detectors*, 2nd ed., 2011).

---

## 9. Cost (order-of-magnitude framing)

Pure-spec / vendor-agnostic ranges, current-generation, camera-engine pricing only (lens excluded, typical 2025-2026 trade prices):

- **Cooled MWIR camera engine** (640×512 InSb or HgCdTe with Stirling cooler + drive electronics): **$30,000-$80,000+**.
- **Uncooled LWIR camera engine** (640×512 12 µm VOx): **$3,000-$15,000**, with high-volume OEM pricing toward the lower end.
- **Cost ratio:** uncooled ≈ **5-10× cheaper** than cooled, with the gap widening at lower volumes.

These are order-of-magnitude estimates. Specific vendor pricing varies significantly; the report should cite the *ratio* and the *order of magnitude* rather than fabricate specific dollar figures.

---

## 10. Precedent — does uncooled LWIR + LWIR-band methane OGI exist as a deployed system?

**Yes, for architecture/platform precedent.** The precedent-search finding is that uncooled-LWIR methane OGI exists commercially, including UAV integration. Public sources do not provide a full 50-200 m ppm·m performance curve, so the report should treat the range envelope as modeled rather than field-proven.

### 10.1 FLIR GF77 — uncooled LWIR OGI camera (production since ~2019)

- Spectral range: **7-8.5 µm** (LR variant for methane).
- Filter: methane-specific narrowband.
- Detector: uncooled microbolometer; public GF77/GF77a methane-filtered pages checked for this report list 320×240 IR resolution and 25 µm detector pitch for the GF77/GF77a CH₄ configuration.
- Operating model: handheld / fixed-camera; publishes methane NECL <100 ppm·m at ΔT = 10 °C and distance = 1 m. Public pages checked for this report do **not** visibly document Appendix K compliance for GF77/GF77a.
- Source: https://support.flir.com/DsDownload/Assets/85204-0102-en-US.html and https://www.flir.com/products/gf77a/ (accessed 2026-05-09).
- Reference for the broader *uncooled OGI* class: GF77, GF77a, MultiSensor Scientific HEAT (multispectral SWIR/LWIR), and others.

### 10.2 MFE Detect LW — UAV-mounted uncooled LWIR OGI (production)

- Platform: payload for **DJI Matrice M300 / M350** drones, with **M400** compatibility stated on some public product pages.
- Detector: uncooled LWIR microbolometer.
- Filter: methane-specific.
- Compliance: vendor documentation states EPA OOOOa, OOOOb, OOOOc, and Appendix K compliance; no independent public certification / field-curve packet was located in this search.
- Application: aerial methane survey at well pads, pipelines, storage tanks, processing units, landfills.
- Source: https://mfe-is.com/en_ca/product/mfe-detect-lw/ (accessed 2026-05-08).

**This is the strongest single architecture precedent for the recommendation in the report.** The UAV-mounted uncooled LWIR + methane-narrowband-filter architecture is not exploratory, but the exact 50-200 m detection floor remains an engineering estimate unless public range data is obtained. The trade-off section should cite this directly with that caveat.

### 10.3 Other notable precedents (lighter weight)

- Workswell WIRIS Security / WIRIS Pro (uncooled LWIR for general thermography on UAVs; not gas-filtered but demonstrates the platform integration).
- Sierra-Olympia Ventus OGI (cooled MWIR comparator, for the trade-off side).

---

## 11. Operating conditions — what we assume in the simulation and performance section

| Variable | Working value | Sensitivity bounds |
|---|---|---|
| Background temperature T_bg | 288 K (15 °C) | 273-308 K |
| Plume-to-background ΔT | 5 K nominal | 3 K stress / 10 K favorable |
| Atmospheric humidity | Standard atmosphere | Dry / humid bounds per §2 |
| Operating altitude | 50-150 m nominal, 200 m marginal | (per origin executive summary) |
| Frame rate | 30 Hz nominal | 60 Hz available |
| Wind speed | ≤ 1 m/s for design, ≤ 5 m/s sustained operation | Higher → plume disperses faster |

---

## 12. Open verifications / prototype-hardening notes

Items to validate before procurement, detailed design, or field deployment:

1. **Report §6.3** Warm-filter penalty — the report and simulation use **50 mK** effective NETD as a working engineering allowance; detailed radiometric design should validate the **50-65 mK** sensitivity range against f-number, filter temperature, passband angle shift, and passband stability.
2. **Report §4.5 / §8 and facts.md §5.3** field ppm·m sensitivity floors — do not equate close-range GF77 NECL specifications with UAV-standoff field performance. Vendor specifications are product/context specific.
3. **§6** α ratio between filter-weighted MWIR and LWIR passbands — recompute from PNNL spectra before replacing the engineering-calibrated simulation constants with measured passband data. The 2.5× working value is from band-integrated intensities; the *filter-weighted* value with specific passband shapes may differ.
4. **§6** 7.7-8.0 µm hardware implementation — verify the selected detector window and optical stack transmit the methane band; generic 8-14 µm thermography-core specs are insufficient.
5. **§6** thin-film filter angle-of-incidence shift — model the full f/# cone and field angle, not only chief-ray angle; procure / test a low-angle-shift filter or move the filter to a more collimated section if needed.
6. **§9** Cost figures — confirm against trade publications or current procurement data before using them for procurement. The $3k-$15k uncooled / $30k-$80k cooled bracket is order-of-magnitude context, not a primary-source quotation.

These are hardening/procurement checks, not blockers for the submitted assignment package.

---

## 13. Quick-reference citation list (for the report's footnote rendering)

- Gordon, I.E., et al. 2022. "The HITRAN2020 molecular spectroscopic database." *JQSRT* 277, 107949.
- Brown, L.R., et al. 2013. "Methane line parameters in the HITRAN2012 database." *JQSRT* 130, 201-219.
- Heicklen, J. 1987. "Integrated infrared intensities of methane." *JQSRT* 37(2), 107-110.
- Sharpe, S.W., et al. 2004. "Gas-phase databases for quantitative infrared spectroscopy." *Applied Spectroscopy* 58(12), 1452-1461.
- Brauer, C.S., et al. 2014. "The Northwest Infrared (NWIR) gas-phase spectral database of industrial and environmental chemicals: Recent updates." *Proc. SPIE* 9106, 910604.
- Roberts, R.E., Selby, J.E.A., Biberman, L.M. 1976. "Infrared continuum absorption by atmospheric water vapor in the 8-12 µm window." *Applied Optics* 15(9), 2085-2090.
- Griot, R., et al. 2023. "Cryogenic solutions for IR detectors – a guideline for selection." *Opto-Electronics Review* 31, e144566.
- Ravikumar, A.P., Wang, J., Brandt, A.R. "Are Optical Gas Imaging Technologies Effective For Methane Leak Detection?" *Environmental Science & Technology* (Stanford EAO).
- Ravikumar, A.P., Wang, J., McGuire, M., Bell, C.S., Zimmerle, D., Brandt, A.R. "'Good versus Good Enough?' Empirical Tests of Methane Leak Detection Sensitivity of a Commercial Infrared Camera." *Environmental Science & Technology* 52(4), 2368-2374 (2018).
- IPCC AR6 / GHG Protocol AR6 GWP tables for methane 20-year GWP context.
- EPA Methane Emissions and Sources of Greenhouse Gas Emissions pages for U.S. source-ranking context.
- 40 CFR Part 60, Appendix K — *Determination of Volatile Organic Compound and Greenhouse Gas Leaks Using Optical Gas Imaging*. https://www.ecfr.gov/current/title-40/part-60/appendix-Appendix%20K%20to%20Part%2060
- IRnova Njord MW T2SL HD detector. https://www.irnova.se/t2sl-njord-mw
- Raytron OHLE3123 uncooled LWIR detector. https://www.raytron-microelectronics.com/uncooled-lwir-modules/ohle3123-uncooled-infrared-focal-plane-detector
- FLIR GF77 LR datasheet. https://support.flir.com/DsDownload/Assets/85204-0102-en-US.html
- MFE Detect LW. https://mfe-is.com/en_ca/product/mfe-detect-lw/

Specialist secondary references (to consult during drafting if needed):
- Rogalski, A. *Infrared Detectors*, 2nd ed., CRC Press, 2011.
- Kruse, P.W. *Uncooled Thermal Imaging Arrays, Systems, and Applications*, SPIE Press, 2001.
- Hudson, R.D. *Infrared System Engineering*, Wiley, 1969 (classic IR atmospheric optics reference).
- Wolfe, W.L., Zissis, G.J. *The Infrared Handbook*, 2nd ed., 1989.
