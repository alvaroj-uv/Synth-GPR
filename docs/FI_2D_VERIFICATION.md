# Verifying Virtual-Sieve FI from 2D Triangle Geometry Against Lab FI Thresholds

**Problem:** Rocks are gprMax `#triangle` primitives (2D triangles, infinite z-extent), and the LabWorker's virtual sieve compares **2× circumradius** against sieve apertures (`lab_worker.py`, `diameter = 2 * radius`). Selig & Waters FI thresholds (C<1, MC 1–10, MF 10–20, F 20–40, HF≥40) are defined for **mass-based 3D sieve tests**. Two biases stack:

1. **Shape bias:** real sieving classifies particles by their *intermediate dimension* (≈ minimum Feret diameter), not their longest. A triangle's circumdiameter exceeds its minimum width, so the current sieve **overestimates particle size → underestimates % passing → biases FI low** (samples labeled cleaner than they are).
2. **Dimensionality bias:** a 2D area-based gradation is statistically biased relative to a 3D mass-based one (stereology), so class boundaries may not transfer directly.

## Route 0 — Exact shape fix: sieve by minimum Feret diameter

Image-analysis ↔ sieve correlation studies consistently find that **square-aperture sieves classify particles by their width, best estimated by the minimum Feret diameter** (x_Fe,min / x_c,min). For a triangle this is exact and cheap: min Feret = smallest altitude, computable directly from the three vertices. Replacing `2*radius` (circumdiameter) with the smallest altitude in `LabWorker._sieve` removes the shape bias analytically — no calibration needed.

- Sieve–image analysis correlation (min Feret as sieve-equivalent size): https://www.microtrac.com/files/81623/white-paper-correlation-between-sieve-analysis-and-image-analysis-made-easy.pdf
- Particle width = intermediate dimension on square meshes: https://www.sympatec.com/en/particle-measurement/glossary/fundamentals-of-particle-characterisation/particle-shape
- Direct sieve-size estimation from 2D images: https://orbi.uliege.be/bitstream/2268/12635/1/PARTEC2004%20P516.pdf
- 2D vs 3D particle descriptor correlation (simulated dataset): https://www.sciencedirect.com/science/article/pii/S1674200124002086

## Four further literature-backed verification routes

### 1. Stereological unfolding (Wicksell / Saltykov)
2D sections systematically under-sample true particle size (a plane rarely cuts a particle at its max diameter). The Wicksell corpuscle problem gives the exact relation between observed 2D circle radii and the underlying 3D sphere size distribution; the Scheil-Schwartz-Saltykov method inverts it on a histogram.

**Application:** Treat each triangle's equivalent-area circle radius as a 2D section size, unfold to an equivalent 3D PSD, recompute P4 + P200 → FI_3D, and compare against FI_2D. Classic Saltykov assumes spheres; for angular particles use the convex-body generalization (below) or absorb the shape factor into the empirical mapping. If FI_2D → FI_3D is monotonic (it should be), derive **corrected class thresholds** in FI_2D space.

- Wicksell equation / MDE solution: https://www.ias-iss.org/ojs/IAS/article/view/2133
- Saltykov implementation (open source): https://github.com/DorianDepriester/automatic-Saltykov
- 2D→3D PSD recovery review: https://onlinelibrary.wiley.com/doi/full/10.1111/maps.12812
- Stereology for non-spherical convex bodies: https://arxiv.org/pdf/2305.02856

### 2. Area-based → mass-based gradation conversion
Kim et al. (KSCE J. Civil Eng., 2017) measured fresh and fouled ballast by 2D image analysis and compared area-, number-, and volume-based gradation curves to lab sieve analysis: **area-based gradations match sieve analysis closest** for crushed stone, and ellipse shape assumptions outperform circles. Hossain et al. provide a mass model (weight/particle ratio) converting image PSD to mass PSD directly comparable to mechanical sieving.

**Application:** Compute the generator's gradation both ways (area-weighted from circle areas vs mass-weighted assuming unit-depth cylinders) and quantify the FI offset between them.

- Area/volume gradation vs sieve (Kim et al.): https://link.springer.com/article/10.1007/s12205-016-1765-x
- Mass model from 2D images: https://www.sciencedirect.com/science/article/pii/S2095268617302392

### 3. DEM virtual sieving (validated against lab sieves)
Zhou et al. (2017) and the ASCE IJG study (2019) built DEM virtual sieve models with X-ray CT particle shapes and validated against lab sieve tests. Key finding: **most particles pass smaller apertures than their equivalent-volume spheres** — independent confirmation that angular particles sieve by their narrow dimension, supporting the min-Feret fix in Route 0.

- DEM sieve with image-based aggregates: https://www.researchgate.net/publication/315372461
- ASCE validated virtual sieving: https://ascelibrary.org/doi/10.1061/(ASCE)GM.1943-5622.0001376

### 4. Empirical calibration precedent (image FI ↔ lab FI)
Machine-vision studies established **linear regressions between image-derived degradation measures and lab-sieve FI** (Percent Degraded Segments ↔ FI), proving that a 2D-derived index can be calibrated to lab FI rather than assumed equal. Anbazhagan et al. likewise show FI threshold equations are routinely **modified to suit specific gradations** — adapting thresholds to the synthetic domain has precedent.

- Machine-vision FI correlation: https://www.researchgate.net/publication/326750158
- RGB-based FI prediction: https://www.sciencedirect.com/science/article/abs/pii/S0263224124006985
- Modified FI for gradation requirements (Anbazhagan): https://www.researchgate.net/publication/237152572

## Recommended protocol for Synth-GPR

1. **Ground-truth advantage:** the generator knows every cylinder radius and the exact fines volume — no sampling bias. Compute mass-based PSD analytically (unit-depth cylinders: mass ∝ πr²ρ) alongside the current virtual sieve.
2. **Unfold:** apply Saltykov to the radius distribution → equivalent 3D PSD → FI_3D.
3. **Map:** regress FI_2D vs FI_3D across the existing 30k dataset; if offset is systematic, publish corrected thresholds for class labels (route 4 precedent).
4. **Report:** in the presentation, caveat that FI is "2D-equivalent FI, stereologically mapped to Selig & Waters thresholds" — defensible per routes 1–2.
5. **Sanity check:** spot-validate with a 3D DEM virtual sieve (route 3) on a few extruded scenes if reviewers demand it.
