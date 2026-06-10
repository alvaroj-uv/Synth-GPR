# Li et al. 2025 — Reference & Action Items

**Paper:** Li B., Guo L., Peng Z., Wang S., Liu G., Li Y. (2025). *FDTD analysis of
ballast fouling status using PFC with discrete random medium model.* Journal of Applied
Geophysics 233, 105605. DOI: 10.1016/j.jappgeo.2024.105605. Zotero key `8QYKYBQD`.

**Why it matters to Synth-GPR:** This is the **most mechanically-faithful synthetic
ballast-fouling study in our library** and a direct precedent for our pipeline. It
builds clean ballast from *laser-scanned real grains* (PFC2D discrete-element gravity
stacking), fouls it with a *discrete random medium*, simulates in gprMax, and shows the
clean/fouled difference is fully recoverable **from the waveform alone** (Hilbert energy
+ S-transform), with **no metadata**. That is exactly our core hypothesis. It is the
companion to [[li_2]] (same group, 2023, RIP+collision-detection, 3 fouling levels).

---

## Their pipeline (vs. ours)

| Stage | Li 2025 | Synth-GPR equivalent |
|---|---|---|
| Clean geometry | Laser-scan grains → random-angle 2D projection → PFC2D `clump` fit → gravity stacking; 15–63 mm, 80% porosity, 5 gradations | our packing modes (Shang-Chu / `mbubia_ballast`), angular rocks |
| Import to gprMax | binarize (PyCharm) → HDF5 → `geometry_objects_read` | same HDF5 / `geometry_objects_read` route |
| Fouling | **Discrete Random Medium (DRM)** (Appendix C: elliptical-Gaussian spectrum + random phase + IFFT) fills voids with sub-15 mm particles | our void-fill / fines approach |
| Solver | gprMax FDTD, RTX 3060 | gprMax FDTD |

**Sim parameters (reusable as a 2.0 GHz baseline):**
- `dx_dy_dz = 0.001, 0.001, 0.01`
- 2.0 GHz Ricker, **simple dipole TX/RX pair 0.02 m apart, air-coupled at 0.2 m standoff**
- 60 A-scans, 0.02 m step; model 1.3 m wide × 1.6 m tall (air/ballast/sand/subgrade), PML outer layer.
- **ε:** Air 1, Ballast **4**, Sand 8, Subgrade 13 (σ = 1, 0.01, 0.001, 0.01 S/m).
  ⚠ Note: [[li_2]] (same group) uses **ballast ε = 6** — both within Clark 2001's dry-clean
  range 3–26.9, but document which we adopt and why.

---

## Key findings relevant to us (all waveform-only)

- **Heavy fouling → S-transform energy concentrated in 1.0–3.0 GHz** (sim); **1.0–4.0 GHz**
  (field). Maps to our **frequency** + **STFT** feature blocks.
- **Faster high-frequency attenuation with depth when fouled.** Sim: fouled decays ~8 ns
  vs clean ~12 ns. Field: fouled high-freq gone by ~6 ns; clean persists to ~14 ns. Maps
  to our **time-domain decay / STFT-over-time** features.
- **Fouled → denser, stronger Hilbert (envelope) energy.** Maps to our **Hilbert**
  features. (Consistent with the field r = 0.96 in [[REF_Shapovalov2026_ideas]].)
- **DRM void-filling reproduces the fouled signature** — confirms fragmentation (fines in
  voids), not bulk-ε change, is enough to drive the waveform difference. Energy gain shows
  up especially in the **4–8 ns** range.
- **Field validation:** GSSI SIR-30 + 4200S 2.0 GHz air-coupled, 50 km line, 18 km cleaned
  (clean) vs uncleaned (fouled). Sim ↔ field consistent.

## The gap our RF fills
They discriminate **binary** clean-vs-heavily-fouled by **visually reading** S-transform
and Hilbert-energy maps — **no extracted feature vector, no trained classifier, no fouling
gradient.** Our 572-feature RF turns their qualitative time-frequency observations into an
automated, quantitative, multi-class predictor. Clean framing for our contribution.

---

## ACTION ITEMS

1. **[med] Reuse their 2.0 GHz air-coupled geometry** (dipole pair 0.02 m, 0.2 m standoff,
   `dz = 0.01`) as a second simulation baseline alongside our ground-coupled setup — lets us
   compare coda features against an air-coupled precedent and against [[REF_Shapovalov2026_ideas]].
2. **[med] Reconcile the ballast ε choice.** Li 2025 = 4, Li 2023 = 6, Shapovalov field is
   moisture-dependent. Add a one-line justification to our materials doc and note the range.
3. **[low] Cite as physical basis for the Hilbert/STFT/frequency feature blocks** in
   OBJECTIVES_AND_HYPOTHESIS — "fouling concentrates energy in 1–3 GHz and accelerates
   depth attenuation" is the mechanism our features encode.
4. **[low] Borrow the DRM void-fill idea** as an alternative fines model to compare against
   our current fouling representation (sensitivity check, not a replacement).

## Limitations they state (and our contrast)
- **2D only**, per-particle **homogeneous isotropic** ε — same simplification Harajchi &
  Slob ([[Harajchi]]) warn under-captures scattering/attenuation. Our heterogeneous-rock
  approach is a step beyond this.
- Fouling = **fragmentation only** — no mud/silt/moisture (the dominant real-field error
  source per [[REF_Shapovalov2026_ideas]]).

## Cross-refs
- [[li_2]] — same group, 2023, RIP+CD, **3 fouling levels** + energy-integration curve (multi-class precedent)
- [[Harajchi]] — heterogeneous vs homogenized ballast (why per-particle homogeneous ε is a limitation)
- [[REF_Shapovalov2026_ideas]] — real-field counterpart; Hilbert r = 0.96
- [[FDTD Medium Dimension Selection]] — domain-sizing guidelines for this kind of model
- `OBJECTIVES_AND_HYPOTHESIS.md`, `REFERENCES.md` (add full citation)
