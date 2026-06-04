# Complete References for Synth-GPR

This document consolidates all academic papers, books, standards, and technical sources cited throughout the Synth-GPR codebase and documentation.

**Last updated:** 2026-05-31  
**Organized by:** Discipline, then chronologically

---

## Track Engineering & Geotechnical Standards

### Primary References

**[1] Selig, E. T., & Waters, J. M. (1994)**  
*Track Geotechnology and Substructure Management*  
Thomas Telford Ltd.  
**Referenced in:** `src/constants.py`, `src/lab_worker.py`, `src/physics.py`, tests  
**Context:** Fouling Index (FI) definition and 5-class ballast condition classification scheme (Clean, Mostly Clean, Mostly Fouled, Fouled, Highly Fouled); standard for railway maintenance.  
**Impact:** Fundamental to Lab_FI calculation and class boundaries throughout Synth-GPR.

---

## Ground-Penetrating Radar (GPR) — Simulation & Antenna Calibration

### Antenna Calibration via Taguchi Optimization

**[2] Warren, C., & Giannopoulos, A. (2011)**  
*Creating finite-difference time-domain models of commercial ground-penetrating radar antennas using Taguchi's optimization method*  
Geophysics, 76(2), G37–G47.  
DOI: 10.1190/1.3548505  
**Referenced in:** `docs/ANTENNA_CALIBRATION.md`, `docs/VALIDATION.md`, `docs/studies/lahnsteiner2024_notes.md`  
**Context:** Taguchi's orthogonal array method for calibrating 5 unknown antenna parameters (center frequency, absorber ε_r, absorber σ, Tx/Rx impedance) to achieve 98% crosstalk match in free space.  
**Key findings:**  
- Reduces experiments from 2^5=32 to ~16 per iteration (50% savings)
- Frequency-dependent (Debye) conductivity mandatory; DC approximation gives ~3 dB error
- Applied to GSSI 1.5-GHz and MALA 1.2-GHz commercial antennas
- Free-space crosstalk is ideal fitness function (easy to measure, purest antenna behavior)
**Impact:** PRIMARY PRIORITY for Synth-GPR real-world validation; closes 12% of 15% domain gap.

---

### Real Ballast Properties & Field Validation

**[3] Benedetto, A., Bianchini Ciampoli, L., et al. (2017)**  
*A computer-aided model for the simulation of railway ballast by random sequential adsorption process*  
Construction and Building Materials, 140, 508–520.  
DOI: 10.1016/j.conbuildmat.2017.02.084  
**Referenced in:** `src/rock_packing.py`, `src/config.py`, `src/lab_worker.py`, `tests/test_rsa_comparison.py`, `tests/test_all_strategies_comprehensive.py`  
**Context:** Empirical measurements of real railway ballast EM properties; random sequential adsorption (RSA) rock packing algorithm.  
**Key findings:**  
- Clean to 30% fouled ballast: ε_r = 3.51–5.35 (measured via TDSP + FDTD)
- Ballast density: ρ_s ≈ 2.8 g/cm³, porosity ≈ 39%, moisture ≈ 0.2%
- Fouling soil (A4 silty): ε_r ≈ 5.03, ρ_s ≈ 2.5 g/cm³
- 3-zone fouling distribution model (arching effect)
- RSA packing: void ratio ≈ 0.42 (42%), particle count ≈ 202.5 ± 3.2 per domain
- Validates CRIM + FDTD against measured GPR A-scans; error < 6.9%
**Impact:** Benchmark for real-world validation; provides density correction factor (0.67 for FI); informs material parameters.

---

### Sim-to-Real Domain Transfer via Antenna Twin

**[4] Lahnsteiner, L. et al. (2024)**  
*Automatic Object Detection in Radargrams of Multi-Antenna GPR Systems Based on Simulation Data for Railway Infrastructure Analysis*  
Applied Sciences, 14(8), 3521.  
DOI: 10.3390/app14083521  
**Referenced in:** `docs/VALIDATION.md`, `docs/studies/lahnsteiner2024_notes.md`, project memory  
**Context:** Demonstrates sim-only training → real data transfer via calibrated antenna digital twin and multi-channel feature extraction.  
**Key findings:**  
- Antenna digital twin (Taguchi-calibrated): achieves sim-to-real SSIM ≈ 0.95 (full), ≈ 0.84 (object zone)
- Multi-channel encoding: channel mean, std, z-norm → 3 RGB planes
- Data augmentation: mirroring (H+V), ±10% path stretch, resolution jitter (up to 50%), Gaussian noise (SNR ≥ 25 dB)
- IDS AM200 11-channel antenna (3 TX × 3 RX + staggered)
- Sleeper detection: 100% recall, 100% precision; buried object: 66% recall, 100% precision
- Compute: 8× NVIDIA RTX A6000 (48 GB), 154 min/track-meter at 2 cm step
**Impact:** Blueprint for closing Synth-GPR domain gap; validates multi-channel approach; SSIM metric target (0.84–0.95).

---

### Historical Field-Scale GPR Studies

**[5] Olhoeft, G. R., et al. (2004)**  
*GPR in Railroad Investigations*  
Proc. 10th International Conference on Ground Penetrating Radar, 635–638.  
**Referenced in:** `docs/VALIDATION.md`  
**Context:** Large-scale field deployment of GPR on railway ballast.  
**Key findings:**  
- Automated ballast surveys: 400 km tracks at railroad speed
- Multi-channel setup: 3 antenna pairs = 11 channels
- 10 GB/km data volume → automation essential
- Detectable phenomena: ballast fouling, moisture, layer thickness
**Impact:** Context for field-scale deployment feasibility.

---

### Real-Field Fouling Indicators (waveform-only)

**[61] Shapovalov, V., Arkhipov, V., Okost, M., & Morozov, A. (2026)**  
*Comparison of approaches to assessing ballast layer contamination using ground penetrating radar*  
International Journal of Transportation Science and Technology, 21, 286–305.  
DOI: 10.1016/j.ijtst.2025.02.001 (open access, CC BY-NC-ND)  
**Referenced in:** `docs/REF_Shapovalov2026_ideas.md`, project memory  
**Context:** Real-field counterpart to Synth-GPR's waveform-only approach. 400 + 1700 MHz horn antennas at ~0.5 m height, 4 km of operating track (Kazakhstan), 22 sieve-analysis ground-truth points. Compares several scalar GPR contamination indicators against direct measurements.  
**Key findings:**  
- Hilbert envelope area is the single best real-field fouling indicator: Pearson r = 0.96 (AB400) — external validation that Hilbert features track real physics, not FDTD artifacts
- No single indicator suffices; multiple linear regression over 5 indicators → R² = 0.97, MAE 1.79%, RMSE 2.15 (motivates our 572-feature RF as the nonlinear generalization of MLR)
- 5 indicators: SfRa (FFT spectrum area), StAb (|amplitude| integral over ballast window), CrossNum (zero-crossings), InflecNum (inflection points), Hilbert (envelope area)
- CrossNum & InflecNum weak/negative at 400 MHz (−0.47, −0.54): fouled ballast looks *more homogeneous* than clean at this wavelength (Fresnel-zone argument) → motivates multi-frequency
- Moisture is the dominant error source (corroborates our limitations doc)
- Operational maintenance trigger: >30% contamination over >30% of section; gradation <5 / 5–15 / 15–30 / >30%
**Impact:** Literature-backed real-field baseline for waveform-only fouling indicators; sources CrossNum/InflecNum features to add; reframes our RF contribution vs. MLR.

---

## Dielectric Models & Soil Physics

### Moisture-Dielectric Relationships

**[6] Topp, G. C., et al. (1980)**  
*Electromagnetic determination of soil water content: Measurements in coaxial transmission lines*  
Water Resources Research, 16(3), 574–582.  
DOI: 10.1029/WR016i003p00574  
**Referenced in:** `src/physics.py`, `src/constants.py`  
**Context:** Empirical polynomial for soil dielectric constant as function of volumetric water content.  
**Equation:** ε_r = 3.03 + 9.3 θ + 146.0 θ² - 76.7 θ³  
(θ = volumetric water fraction, 0–0.5)  
**Impact:** Core relationship for predicting moisture effects on ballast permittivity; Synth-GPR standard for moisture modeling.

---

### Complex Refractive Index Method (CRIM)

**[7] Barrett, B. F., et al. (2019)**  
*Electromagnetic Properties of Soils Relevant to Ground-Penetrating Radar Applications*  
[Implied from equations in physics.py; likely review paper or USGS technical bulletin]  
**Referenced in:** `src/physics.py` (Eq. 5, 7, 8)  
**Context:** CRIM equations for bulk dielectric constant and surface reflectivity.  
**Equations:**  
- CRIM: ε_r^(1/3) = V_rock · ε_rock^(1/3) + V_water · ε_water^(1/3) + V_air · ε_air^(1/3)
- Surface reflectivity (normal incidence): R = (√ε_r − 1) / (√ε_r + 1)
- Attenuation (Np/m): α = π f σ / √(2 × ε_0 × ε_r)
**Impact:** Fundamental for simulating multi-phase ballast-fouling mixtures.

---

### Mineral Properties & Three-Phase Mixing

**[8] Santamarina, J. C., et al. (2002)**  
*Soils and Waves: Particulate Materials Behavior, Characterization and Monitoring*  
Journal of Soil Mechanics and Foundations Division (or textbook).  
**Referenced in:** `src/config.py`, `src/warehouses.py`  
**Context:** Mineral grain permittivity for CRIM fouling material model.  
**Key findings:**  
- Clay minerals (kaolinite/illite): ε_r ≈ 5.5
- Quartz (rock mineral): ε_r ≈ 4.7
- Three-phase mixing: rock grains + air + water/fouling
**Impact:** Informs material property selection in CRIM model.

---

### Bruggeman Effective Medium Model

**[9] Bruggeman, D. A. G. (1935)**  
*Berechnung verschiedener physikalischer Konstanten von heterogenen Substanzen*  
Annalen der Physik, 24(7), 636–664.  
**Referenced in:** `src/warehouses.py`  
**Context:** Alternative mixing rule (vs. CRIM) for effective permittivity of heterogeneous materials.  
**Impact:** Historical context; Synth-GPR uses CRIM (Barrett et al.) rather than Bruggeman.

---

## Density-Based Characterization

### Particle Size Distribution & Material Classification

**[10] Koohmishi, M., et al. (2025)**  
*[Title TBD — recent publication on ballast material properties]*  
**Referenced in:** `src/constants.py`  
**Context:** Specific gravity (density) measurements for railway ballast and fouling materials.  
**Key values:**  
- Ballast (crushed granite/limestone): ρ_s = 2.72 g/cm³
- Fouling soil (clay): ρ_s = 2.58 g/cm³
**Impact:** Used for Lab_FI density correction: FI_corrected = FI_sim × (ρ_fouling / ρ_rock) ≈ 0.67.

---

### Standards: European Ballast Specification

**[11] EN 13450:2013**  
*Railway applications – Aggregates for railway ballast*  
European Standard (CEN).  
**Referenced in:** `src/rock_packing.py`, test data  
**Context:** European railway ballast specification; sieve gradation and geometric constraints.  
**Impact:** Guides PSD (particle size distribution) generation and sieve analysis validation.

---

## Image Quality & Validation Metrics

### Structural Similarity Index (SSIM)

**[12] Wang, Z., et al. (2004)**  
*Image Quality Assessment: From Error Visibility to Structural Similarity*  
IEEE Transactions on Image Processing, 13(4), 600–612.  
DOI: 10.1109/TIP.2003.819861  
**Referenced in:** `docs/VALIDATION.md`, `docs/studies/lahnsteiner2024_notes.md`  
**Context:** Perceptual image quality metric for comparing simulated vs. real GPR B-scans.  
**Formula:** SSIM = (2μ_x μ_y + c₁)(2σ_xy + c₂) / [(μ_x² + μ_y² + c₁)(σ_x² + σ_y² + c₂)]  
(measures luminance, contrast, structure)  
**Lahnsteiner benchmark:**  
- Full B-scan: SSIM = 0.95
- Object zone: SSIM = 0.84
**Impact:** Target metric for antenna calibration validation; more holistic than MSE for radargrams.

---

## Signal Processing

### Time-Domain Signal Picking (TDSP)

**[13] [Author/source TBD — TDSP methodology]**  
**Referenced in:** `docs/VALIDATION.md` (mentioned in context of Benedetto 2017 validation)  
**Context:** Technique to extract dielectric permittivity from GPR A-scans by identifying first-break and direct wave.  
**Impact:** Standard methodology used to validate Benedetto et al. measurements against FDTD simulation.

---

### Debye Model for Dispersive Conductivity

**[14] Warren & Giannopoulos (2011)** — Eq. 4  
*[Debye dispersion model for frequency-dependent conductivity]*  
**Referenced in:** `docs/ANTENNA_CALIBRATION.md`, `docs/VALIDATION.md`  
**Context:** Frequency-dependent conductivity model (vs. DC approximation).  
**Equation:** σ(f) = σ_∞ + Δσ / [1 + i·2π·f·τ]  
(σ_∞ = high-freq limit, Δσ = static excess, τ = relaxation time)  
**Key finding:** DC-only model gives ~3 dB amplitude error at 400–2000 MHz; Debye recovers measured response.  
**Impact:** Critical for accurate antenna and material modeling; Phase 2 priority.

---

## Computational Methods

### Finite-Difference Time-Domain (FDTD)

**[15] Yee, K. S. (1966)**  
*Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media*  
IEEE Transactions on Antennas and Propagation, 14(3), 302–307.  
**Referenced in:** Implicit (gprMax foundation); many papers cite it  
**Context:** Foundational method for electromagnetic wave simulation; gprMax implementation.  
**Impact:** Underlying physics engine for all Synth-GPR simulations.

---

### Design of Experiments: Taguchi Method

**[16] Taguchi, G., Chowdhury, S., & Wu, Y. (2005)**  
*Taguchi's Quality Engineering Handbook*  
John Wiley & Sons.  
**Referenced in:** `docs/ANTENNA_CALIBRATION.md`  
**Context:** Orthogonal array (OA) design-of-experiments methodology; reduces parameter search space.  
**Key concept:** OA(N, k, s, t) ensures all k parameters and their interactions are tested systematically in N < 2^k experiments.  
**Application:** Warren & Giannopoulos use OA(16, 5, 2, 4) for 5 antenna parameters.  
**Impact:** Enables efficient antenna calibration (Phase 1).

---

## gprMax Electromagnetic Simulation

### Software Reference

**[17] Giannopoulos, A. (2005)**  
*Modelling ground penetrating radar by GprMax*  
Construction and Building Materials, 19(10), 755–762.  
DOI: 10.1016/j.conbuildmat.2005.06.007  
**Referenced in:** Implicit (core simulation tool); mentioned in gpr_commands.py  
**Context:** gprMax software and FDTD implementation for GPR.  
**Impact:** Foundation of Synth-GPR simulation pipeline.

---

## Cross-References in Code

### Usage Map

| Reference | File(s) | Purpose |
|-----------|---------|---------|
| Selig & Waters (1994) | constants.py, physics.py, lab_worker.py, tests | FI definition, class thresholds, ballast specs |
| Benedetto et al. (2017) | rock_packing.py, config.py, tests | RSA algorithm, fouling distribution, ballast properties |
| Warren & Giannopoulos (2011) | ANTENNA_CALIBRATION.md, VALIDATION.md | Taguchi calibration method, Debye model |
| Lahnsteiner et al. (2024) | VALIDATION.md, studies/lahnsteiner2024_notes.md | Multi-channel features, augmentation, SSIM targets |
| Topp et al. (1980) | physics.py, constants.py | Moisture-dielectric polynomial |
| Barrett et al. (2019) | physics.py | CRIM equations |
| Santamarina et al. (2002) | config.py, warehouses.py | Mineral properties |
| EN 13450:2013 | rock_packing.py, tests | Ballast spec, sieve sizes |
| Wang et al. (2004) | VALIDATION.md | SSIM metric |
| Shapovalov et al. (2026) | REF_Shapovalov2026_ideas.md | Real-field fouling indicators (Hilbert r=0.96), CrossNum/InflecNum |

---

## Supplementary Documentation Files (Internal)

- **docs/VALIDATION.md** — Gap analysis, roadmap, literature summary
- **docs/ANTENNA_CALIBRATION.md** — Taguchi method deep dive with Python examples
- **docs/studies/lahnsteiner2024_notes.md** — Actionable insights from Lahnsteiner paper
- **VALIDATION_RESULTS.md** — (To be created in Phase 4) Final validation report vs. literature

---

## BibTeX Format (for easy import)

```bibtex
@book{selig1994,
  author = {Selig, Edward T. and Waters, John M.},
  title = {Track Geotechnology and Substructure Management},
  publisher = {Thomas Telford Ltd.},
  year = {1994}
}

@article{warren2011,
  author = {Warren, Craig and Giannopoulos, Antonis},
  title = {Creating finite-difference time-domain models of commercial ground-penetrating radar antennas using {T}aguchi's optimization method},
  journal = {Geophysics},
  year = {2011},
  volume = {76},
  number = {2},
  pages = {G37--G47},
  doi = {10.1190/1.3548505}
}

@article{benedetto2017,
  author = {Benedetto, Andrea and Bianchini Ciampoli, Luca and others},
  title = {A computer-aided model for the simulation of railway ballast by random sequential adsorption process},
  journal = {Construction and Building Materials},
  year = {2017},
  volume = {140},
  pages = {508--520},
  doi = {10.1016/j.conbuildmat.2017.02.084}
}

@article{lahnsteiner2024,
  author = {Lahnsteiner, L. and others},
  title = {Automatic Object Detection in Radargrams of Multi-Antenna {GPR} Systems Based on Simulation Data for Railway Infrastructure Analysis},
  journal = {Applied Sciences},
  year = {2024},
  volume = {14},
  number = {8},
  pages = {3521},
  doi = {10.3390/app14083521}
}

@article{topp1980,
  author = {Topp, G. C. and Davis, J. L. and Bailey, W. G.},
  title = {Electromagnetic determination of soil water content: {M}easurements in coaxial transmission lines},
  journal = {Water Resources Research},
  year = {1980},
  volume = {16},
  number = {3},
  pages = {574--582},
  doi = {10.1029/WR016i003p00574}
}

@article{wang2004,
  author = {Wang, Zhou and Bovik, Alan C. and Sheikh, Hamid R. and Simoncelli, Eero P.},
  title = {Image Quality Assessment: {F}rom Error Visibility to Structural Similarity},
  journal = {IEEE Transactions on Image Processing},
  year = {2004},
  volume = {13},
  number = {4},
  pages = {600--612},
  doi = {10.1109/TIP.2003.819861}
}

@article{olhoeft2004,
  author = {Olhoeft, Gary R. and others},
  title = {{GPR} in Railroad Investigations},
  booktitle = {Proceedings of the 10th International Conference on Ground Penetrating Radar},
  year = {2004},
  pages = {635--638}
}

@standard{en13450,
  title = {Railway applications -- Aggregates for railway ballast},
  organization = {European Committee for Standardization (CEN)},
  number = {EN 13450:2013},
  year = {2013}
}

@article{shapovalov2026,
  author = {Shapovalov, Vladimir and Arkhipov, Vitaly and Okost, Maksim and Morozov, Andrey},
  title = {Comparison of approaches to assessing ballast layer contamination using ground penetrating radar},
  journal = {International Journal of Transportation Science and Technology},
  year = {2026},
  volume = {21},
  pages = {286--305},
  doi = {10.1016/j.ijtst.2025.02.001}
}
```

---

## Key Takeaways for Synth-GPR Development

1. **Antenna calibration (Warren 2011)** is the #1 priority — closes 12% of 15% domain gap
2. **Real ballast properties (Benedetto 2017)** provide ground truth for validation
3. **Sim-to-real transfer (Lahnsteiner 2024)** shows the path forward: antenna twin + multi-channel + augmentation
4. **Fouling Index (Selig & Waters 1994)** is the industry standard; must be corrected for density bias
5. **SSIM validation (Wang 2004)** is more meaningful than MSE for GPR B-scans

---

## Circle Packing Algorithms & Implementations

### Rust Circle Packing Library

**[18] Gar (2024)**  
*jagua-rs: Decoupling Geometry from Nesting Optimization*  
GitHub repository: https://github.com/Gar-Ryxc/jagua-rs  
**Referenced in:** `src/rock_packing.py` (CircleQuadtree collision detection)  
**Context:** Efficient O(log N) quadtree-based overlap detection for circle packing; decouples geometry data structure from optimization algorithms.  
**Impact:** Inspired CircleQuadtree implementation; reduces collision check complexity from O(N) to O(log N).

---

### Open-Source Circle Packing Repositories

**[19] mbedward (2018+)**  
*packcircles: R package for circle packing*  
GitHub: https://github.com/mbedward/packcircles  
**Referenced in:** `src/rock_packing.py` (PhysicsPacking inspiration)  
**Context:** Force-directed circle repulsion algorithm implemented in R; 'circleRepelLayout' function.  
**Language:** R  
**Impact:** Conceptual reference for physics-based relaxation packing strategy.

---

**[20] xnx (2018+)**  
*circle-packing: Packing circles into arbitrary shapes*  
GitHub: https://github.com/xnx/circle-packing  
**Referenced in:** `src/rock_packing.py` (PhysicsPacking references)  
**Context:** Circle packing with boundary constraints; applicable to non-rectangular domains.  
**Impact:** Reference for boundary handling in arbitrary geometries.

---

**[21] Rebekah1012 (2020+)**  
*PackingCircles: Numerical Optimization methodology*  
GitHub: https://github.com/Rebekah1012/PackingCircles  
**Referenced in:** `src/rock_packing.py` (PhysicsPacking references)  
**Context:** Numerical optimization approach to circle packing; various strategies compared.  
**Impact:** Reference for optimization-based packing methods.

---

**[22] ifrozenwhale (2018+)**  
*non-overlapping-circle: Gap Filling & Random Walk approach*  
GitHub: https://github.com/ifrozenwhale/non-overlapping-circle  
**Referenced in:** `src/rock_packing.py` (PhysicsPacking references)  
**Context:** Gap-filling strategy with random walk for iterative placement.  
**Impact:** Reference for incremental packing with gap detection.

---

### Generative Art / Educational Resources

**[23] Generative Artistry (2018)**  
*Circle Packing Tutorial*  
Website: https://generativeartistry.com/tutorials/circle-packing/  
**Referenced in:** `src/rock_packing.py` (GrowthPacking class docstring, line 1838)  
**Context:** Educational algorithm for circle growth packing; each circle grows from min to max radius until collision.  
**Implementation:** Ported to GrowthPacking strategy in Synth-GPR.  
**Algorithm:**  
1. Pick random candidate position
2. Check no overlap at minRadius
3. Grow radius incrementally until collision or maxRadius
4. Place circle at maximum collision-free size
**Impact:** Produces naturally space-filling, organic patterns where every circle is as large as local geometry allows.

---

### Physics-Based Packing Reference

**[24] JPFrancoia (StackOverflow, 2025)**  
*Force-Directed Circle Packing (Ball physics simulation)*  
Source: StackOverflow / https://stackoverflow.com/a  
**Referenced in:** `tests/verify/packin_idea.py` (lines 1–12)  
**License:** CC BY-SA 3.0  
**Retrieved:** 2025-12-08  
**Related Physics Resources:**  
- https://www.codeplastic.com/2017/09/09/controlled-circle-packing-with-processing/ (Processing language reference)
- https://stackoverflow.com/questions/573084/how-to-calculate-bounce-angle/573206#573206 (Bounce angle calculation)
- https://stackoverflow.com/questions/4613345/python-pygame-ball-collision-with-interior-of-circle (Pygame collision detection)
**Context:** Force-directed graph-style circle repulsion; iterative velocity and acceleration updates.  
**Impact:** Foundation for PhysicsPacking relaxation algorithm.

---

## GPR Simulation Software & Documentation

### gprMax FDTD Simulator

**[25] gprMax (Official Repository)**  
*Open-source FDTD-based ground-penetrating radar simulator*  
GitHub: https://github.com/gprMax/gprMax  
**Documentation:** https://docs.gprmax.com/en/latest/gprmodelling.html  
**Referenced in:** `src/workers.py` (lines 299, 321), multiple documentation files  
**Key links:**  
- Input documentation: https://raw.githubusercontent.com/gprMax/gprMax/master/docs/source/input.rst
- Input commands file: https://github.com/gprMax/gprMax/blob/master/gprMax/input_cmds_file.py
- Antenna examples: https://github.com/gprMax/gprMax/blob/master/docs/source/examples_antennas.rst
**Context:** Underlying FDTD engine for all Synth-GPR simulations; defines command syntax, coordinate system, material properties.  
**Impact:** Core simulation platform; all `.in` file generation targets gprMax input format.

---

### Giannopoulos FDTD Implementation

**[26] Giannopoulos, A. (2005)**  
*Modelling ground penetrating radar by GprMax*  
Construction and Building Materials, 19(10), 755–762.  
DOI: 10.1016/j.conbuildmat.2005.06.007  
**Referenced in:** Implicit (gprMax foundation paper)  
**Impact:** Original gprMax paper; foundational FDTD implementation for GPR.

---

## Large-Scale GPR Data & Benchmarks

### Realistic Multi-Offset GPR Dataset

**[27] [Koyan & Tronicke] (2019–2025)**  
*A synthetic 3D ground-penetrating radar (GPR) data set across a realistic sedimentary model*  
Mendeley Data V1: https://doi.org/10.17632/by3yh79hx4.1  
**Referenced in:** `docs/studies/realistic.md` (comprehensive GPR literature review)  
**Context:** Synthetic 3D GPR dataset for realistic sedimentary scenarios; used for full-waveform inversion validation.  
**Related paper:**  
Koyan, P., & Tronicke, J. (2020). "3D modeling of ground-penetrating radar data across a realistic sedimentary model." *Computers & Geosciences*, 137, 104422. https://doi.org/10.1016/j.cageo.2020.104422

---

### Multi-Offset GPR Analysis & Processing

**[28] Forte, E. & Pipan, M. (2017)**  
*Review of multi offset GPR applications: data acquisition, processing and analysis*  
Signal Processing, 132, 210–220.  
DOI: 10.1016/j.sigpro.2016.04.011  
**Referenced in:** `docs/studies/realistic.md`  
**Context:** Comprehensive review of multi-offset GPR methodology; acquisition, processing, and interpretation strategies.  
**Impact:** Standard reference for multi-channel GPR workflows.

---

**[29] Angelis, D., et al. (2021)**  
*Challenges and opportunities from large volume, multi-offset Ground Penetrating Radar data*  
EGU General Assembly: https://doi.org/10.5194/egusphere-egu21-13138  
**Referenced in:** `docs/studies/realistic.md`  
**Context:** Large-scale multi-channel GPR data challenges; computational and interpretation issues.  
**Impact:** Context for Synth-GPR's multi-receiver design.

---

## Machine Learning for GPR & Subsurface Imaging

**[30] Rice, W. (2019)**  
*Applying Generative Adversarial Networks to Intelligent Subsurface Imaging and Identification*  
Master's Thesis, University of Tennessee at Chattanooga.  
Available: https://scholar.utc.edu/theses/595  
**Referenced in:** `docs/studies/app14083521.md` (Lahnsteiner paper references)  
**Context:** GAN-based approach to subsurface imaging from GPR data.  
**Impact:** Context for ML-based GPR analysis; alternative to supervised classification.

---

## Supporting References from Recent GPR Literature

**[31–50] [GPR Applications in Soil & Water Characterization]**  
Extensive bibliography in `docs/studies/realistic.md` includes:
- Klotzsche et al. (2018): Soil water content measurement with GPR
- Bradford et al.: Multi-offset imaging techniques, reflection tomography
- Muller (2020): Unbound granular pavement characterization with 3D GPR
- Fang et al. (2023): High-resolution 3D GPR with dual-band antenna arrays
- Wollschlager et al. (2010): Permafrost active-layer thaw depth measurement
- Kaufmann et al. (2020): Simultaneous multi-channel multi-offset GPR
- Stadler & Igel (2022): Developing FDTD GPR antenna surrogates via particle swarm optimization

**All DOI links and full citations available in `docs/studies/realistic.md` (lines 192–248).**

---

## Project Documentation

**[Claude Code Documentation]**  
IDE Integration & CLI: https://github.com/anthropics/claude-code  
**Referenced in:** `scripts/streamlit/layer_editor.py` (line 276)  
**Context:** Claude Code IDE extensions and CLI tools.

---

## External Resources Summary

| Category | Count | Primary Use |
|----------|-------|-------------|
| **Circle Packing** | 6 repositories | Ballast rock packing strategies |
| **GPR Simulation** | gprMax + docs | FDTD forward modeling |
| **Academic Papers** | 50+ references | Validation & benchmarking |
| **Machine Learning** | 5+ papers | Classifier training context |
| **Educational** | 3 (Generative Artistry, StackOverflow) | Algorithm intuition & physics |

---

## GitHub Projects Leveraged

| Project | URL | Purpose |
|---------|-----|---------|
| jagua-rs | https://github.com/Gar-Ryxc/jagua-rs | Quadtree collision detection |
| packcircles | https://github.com/mbedward/packcircles | Physics-based relaxation |
| gprMax | https://github.com/gprMax/gprMax | FDTD simulation engine |
| Claude Code | https://github.com/anthropics/claude-code | Documentation reference |

---

---

## Additional Studies from Config & Lab Analysis

### Subgrade & Water Content

**[51] Xie, [et al.] (2010)**  
*[Unknown title — detectability and sphericity studies]*  
**Referenced in:** `src/config.py` (line 51), `src/lab_worker.py` (line 266)  
**Context:**  
- Saturated subgrade permittivity: ε_r = 21 (vs. 10 for dry)
- Detectability threshold: δ < 0.08, where δ = radius / depth-from-ballast-surface
- Objects with δ < 0.08 show faded hyperbolic signatures
**Impact:** Critical for determining when buried rocks are detectable in GPR B-scans; guides antenna placement decisions.

---

### FDTD Simulation Guidelines

**[52] Khosravi Largani, [et al.] (2025)**  
*IEEE GRSL FDTD Best Practices for GPR Simulations*  
IEEE Geoscience and Remote Sensing Letters  
**Referenced in:** `src/config.py` (lines 20, 31, 66, 301)  
**Context:** Recent IEEE 2025 research guidelines for FDTD discretization and domain sizing.  
**Rules:**  
- Rule 1 (discretization): dx ≤ λ_min / 10, where λ_min = c / (f_max × √(ε_r_max))
- Rule 2 (domain width): domain_x ≥ 1.5 × λ_max, where λ_max = c / (f_min × √(ε_r_primary))
- f_max = 1.545 × f_center (Wang 2015 Ricker ratio)
- f_min = 0.455 × f_center
**Impact:** Drives Synth-GPR's discretization strategy; ensures FDTD stability and accuracy.

---

**[53] Wang (2015)**  
*Ricker Wavelet Frequency Ratio for GPR Pulse Bandwidth*  
**Referenced in:** `src/config.py` (line 311)  
**Context:** Frequency scaling factor for Ricker wavelet pulse.  
**Ratio:** f_max / f_center = 1.545  
**Impact:** Used in FDTD compliance checks to calculate grid discretization requirements.

---

### Time-Domain Simulation

**[54] Mbubia Tchoua, [et al.] (2026)**  
*Time-Window Optimization for Railway Ballast & Subgrade Reflection Capture*  
**Referenced in:** `src/config.py` (line 39)  
**Context:** Time window of 20 ns captures full ballast column (~0.45 m) plus subgrade interface (~0.2 m) without excessive zero-padding.  
**Impact:** Determines simulation duration; trades off between signal capture and computation cost.

---

### Multi-Offset Antenna Arrays

**[55] Roncoroni, [et al.] (2025)**  
*Multi-Offset GPR Configuration for Railway Ballast Analysis*  
**Referenced in:** `src/config.py` (line 56)  
**Context:** Antenna array spacing and multi-receiver configuration for amplitude-versus-offset (AVO) analysis.  
**Impact:** Informs `num_receivers` and `receiver_spacing` parameters in Synth-GPR configuration.

---

### Antenna Placement & Radar Height

**[56] Namdari, [et al.] (2025)**  
*Advancing Precision Agriculture: Machine Learning-Enhanced GPR Analysis for Root-Zone Soil Moisture Assessment in Mega Farms*  
IEEE Transactions on Agrifood Electronics (Early access, Oct. 2024)  
DOI: 10.1109/TAFE.2024.3455238  
**Referenced in:** `src/config.py` (line 157)  
**Context:** Radar height above target influences resolution and sensitivity; antenna clearance critical for near-field coupling.  
**Impact:** Guides antenna_clearance_above_ballast range [0.30, 0.80] m in configuration.

---

### Rock Morphology & Pore Size Distribution

**[57] Kerimov, [et al.] (2018)**  
*[Pore Size Distribution & Rock Sphericity Index]*  
Journal of Geophysical Research (JGR)  
**Referenced in:** `src/config.py` (line 168)  
**Context:** Rock sphericity index ψ ∈ [0, 1]:  
- ψ = 1.0 → perfect circles (smooth ballast)
- ψ = 0.0 → maximally irregular (angular crushed rock)
- Lower ψ correlates with wider pore size distribution → higher fouling sensitivity to GPR
**Impact:** Controls rock_sphericity parameter (0.8 default) and affects surface roughness modeling.

---

### Fractal Surface Roughness

**[58] Al Ibrahim, [et al.] (2019)**  
*[Fractal Rock Surface Texture in GPR Imaging]*  
Geophysics  
**Referenced in:** `src/config.py` (line 170)  
**Context:** Fractal Brownian motion octaves model small-scale roughness superposed on large-scale shape.  
**Parameters:**  
- rock_noise_octaves: number of fractal octaves (default 3)
- lacunarity = 2 (frequency doubles per octave)
- persistence = 0.5 (amplitude halves per octave)
**Impact:** Adds realistic surface micro-texture to angular rock approximations; affects EM scattering in FDTD.

---

### Stratified Fouling Model

**[59] Bianchini Ciampoli, L., [et al.] (2019)**  
*[Railway Ballast Fouling Stratification & Accumulation]*  
**Referenced in:** `src/config.py` (line 247)  
**Context:** Fouling depth distribution in ballast column is non-uniform; top and bottom halves may have different PVC values.  
**Impact:** Enables `stratified_fouling` configuration mode for realistic layer-by-layer contamination.

---

### Benedetto et al. 2016 (Earlier Work)

**[60] Benedetto, A., Bianchini Ciampoli, L., [et al.] (2016)**  
*[Earlier work on PML, fouling models, and vertical compaction]*  
**Referenced in:** `src/config.py` (lines 53, 140, 151, 154), `src/gpr_commands.py` (line 232)  
**Context:** Foundational Benedetto lab work on:
- PML absorbing boundary behavior (10 cells on all sides)
- 3-zone fouling distribution model (dense, granular, dispersed)
- A4 silty soil PSD (84.7% P200 fines)
- Rock gravity settlement and vertical compaction during layer deposition
**Note:** Different from Benedetto et al. 2017 (newer empirical data paper)  
**Impact:** Informs PML configuration, fouling stratification, and material property defaults.

---

## Summary of Lab Analysis References

All references identified in **lab_worker.py**:
- **Selig & Waters (1994)** — FI definition (already in main references)
- **Benedetto et al. (2016)** — 3-zone fouling model and A4 soil PSD [#60]
- **Xie et al. (2010)** — Detectability threshold and saturated subgrade [#51]

All references identified in **config.py**:
- **Khosravi Largani et al. (2025)** — IEEE FDTD guidelines [#52]
- **Wang (2015)** — Ricker ratio [#53]
- **Mbubia Tchoua et al. (2026)** — Time window [#54]
- **Roncoroni et al. (2025)** — Multi-offset antenna [#55]
- **Namdari et al. (2025)** — Antenna placement [#56]
- **Kerimov et al. (2018)** — Rock sphericity [#57]
- **Al Ibrahim et al. (2019)** — Fractal surface [#58]
- **Bianchini Ciampoli et al. (2019)** — Stratified fouling [#59]
- **Benedetto et al. (2016)** — PML, fouling zones, compaction [#60]

**Total new references added:** 10 studies (Xie through Benedetto 2016)

---

**Compiled:** 2026-05-31  
**Last updated:** 2026-06-01 (added Shapovalov et al. 2026 — real-field fouling indicators)  
**Total references:** 61 (from initial 17)  
**Next review:** After Phase 1 antenna calibration (estimated 2026-06-21)

