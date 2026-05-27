# Advanced GPR Physics and Multi-Offset Survey Guide

This document describes the research-grade enhancements implemented in the Synth-GPR pipeline (Session May 2026), aligning with **IEEE 2025 FDTD guidelines** and the **Roncoroni et al. (2025)** benchmark standards.

## 1. Multi-Offset (MO) Antenna Arrays
Traditional GPR simulations use a single bi-static pair. This pipeline now supports linear receiver arrays for **AVO (Amplitude Versus Offset)** and **Velocity Analysis**.

### Configuration
In `GeneratorConfig`, set:
- `num_receivers`: Number of antennas in the array (e.g., 8).
- `receiver_spacing`: Distance between receivers in meters (e.g., 0.05m).

### Physical Implementation
The `AntennaWorker` dynamically places receivers. It includes **Boundary Validation**: if an array is too long for the domain, it will skip out-of-bounds antennas and log a warning, ensuring the simulation remains stable.

---

## 2. Angular Rock Modeling (Crushed Ballast)
Inspired by `gprMax-Designer` (Siwek, 2024), we have moved beyond "cylindrical" rocks to **Triangulated Angular Aggregates**.

### Features
- **Polygon Triangulation**: Each rock is rendered using `#triangle` commands instead of `#cylinder`.
- **Octagonal/Hexagonal Approximation**: Controlled by `rock_sides`.
- **Stochastic Perturbation**: Vertex radii are slightly randomized to create unique, jagged profiles.
- **Physics**: Sharp edges increase high-frequency scattering and diffraction, mimicking the response of crushed railway ballast.

---

## 3. Dynamic Discretization (IEEE 2025 Compliance)
To prevent numerical dispersion, the grid resolution ($dx, dy, dz$) is no longer static.

- **The λ/10 Rule**: $dx$ is calculated as $\frac{c}{f_{max} \cdot 10 \cdot \sqrt{\epsilon_{max}}}$.
- **Resolution Scaling**: If you change the antenna from 1.5 GHz to 400 MHz, the domain size and $dx$ automatically rescale to maintain physical fidelity while optimizing computation time.

---

## 4. Signal Processing Chain (GPRForce Integration)
Integrated processing routines inspired by the **GPRForce** (Li, 2024) repository.

### Processing Steps
1. **Dewow**: Removes low-frequency inductive bias.
2. **Time-Zero Correction**: Automatically detects the "First Break" and aligns the trace.
3. **SEC Gain (Spherical Exponential Compensation)**:
   - Compensates for geometric spreading ($1/r$) and material attenuation.
   - Formula: $G(t) = t \cdot e^{\alpha t}$.
4. **Bandpass Filtering**: Removes out-of-band noise before feature extraction.

---

## 5. Statistical Feature Extraction (Namdari et al. 2025)
Enhanced features for ML-based soil/ballast classification:
- **Peak Count & Mean Peak Height**: Captures scattering density from angular rocks.
- **FFT Standard Deviation**: Measures frequency-domain variability.
- **Hilbert Envelope Moments**: Advanced statistical distribution of the reflected energy.

---

*Refer to `tools/GPRForce` for the raw algorithm implementations used in these processing steps.*
