# Shapovalov et al. 2026 — Reference & Action Items

**Paper:** Shapovalov V., Arkhipov V., Okost M., Morozov A. (2026). *Comparison of
approaches to assessing ballast layer contamination using ground penetrating radar.*
International Journal of Transportation Science and Technology 21, 286–305.
DOI: 10.1016/j.ijtst.2025.02.001 (open access, CC BY-NC-ND).

**Why it matters to Synth-GPR:** It is the **real-field counterpart** to our
synthetic waveform-only work. It uses field GPR (400 MHz + 1700 MHz horn antennas,
~0.5 m above ballast) on 4 km of track in Kazakhstan, with 22 sieve-analysis ground
truth points. It independently validates several of our design choices and gives us
literature-backed baselines.

---

## Key findings relevant to us

- **Hilbert envelope is the single best real-field fouling indicator: Pearson r = 0.96**
  (their Table 3, AB400). This is strong external evidence that our Hilbert-based
  features track *real* fouling physics, not FDTD artifacts.
- **No single indicator suffices; combining them wins.** Best single indicator
  R² = 0.92 (Hilbert); their multiple linear regression over all 5 indicators →
  **R² = 0.97, MAE 1.79%, RMSE 2.15** (Table 4–5). This is the exact argument for our
  572-feature RF: our RF is the nonlinear generalization of their MLR.
- **Resolution/wavelength explains weak features.** CrossNum & InflecNum had weak,
  *negative* correlation (−0.47, −0.54) at 400 MHz: heavily fouled ballast looks *more
  homogeneous* than clean at this wavelength (Fresnel-zone argument). A ready physical
  explanation for why some waveform features fail at 400 MHz, and motivation for
  multi-frequency.
- **Moisture is the dominant error source** — every figure's outlier points are wet
  zones. Corroborates our EXPERIMENT_LIMITATIONS §6.2.
- **Operational decision is coarse:** maintenance triggered at **>30% contamination
  over >30% of section**; proposed gradation `<5% / 5–15% / 15–30% / >30%`. Low-FI
  class confusion matters less than feared (relevant to our weak MF class).

## Their 5 GPR indicators (all computable from our Ez A-scan)

| Indicator | Definition | Field r (AB400) | Do we have it? |
|---|---|---|---|
| SfRa | Area under FFT spectrum | 0.62 | ~yes (`area_fourier`) |
| StAb | Integral of \|amplitude\| over ballast time window | 0.86 | partial — need ballast-window version |
| CrossNum | # zero-crossings in ballast window | −0.47 | **NO — add** |
| InflecNum | # inflection points in ballast window | −0.54 | **NO — add** |
| Hilbert | Area under envelope over ballast window | 0.96 | ~yes (`area_hilbert`) but full-trace, not ballast-window |

Average r for the strong indicators (reflectivity, StAb, Hilbert) ≈ 0.91.

---

## ACTION ITEMS

1. **[high] Add CrossNum + InflecNum to `src/feature_extraction.py`.**
   Cheap, literature-backed, currently missing. Closes the "no comparison to published
   baselines" gap (EXPERIMENT_LIMITATIONS §5.2).

2. **[high] Add a ballast-window StAb** (integral of |amplitude| over the ballast time
   gate), distinct from our existing full-trace stats.

3. **[high] Reconcile the Hilbert window / sign discrepancy.**
   - Theirs: envelope area over **full ballast layer (0–0.4 m)** → r = **+0.96**.
   - Ours: envelope energy over **late coda (6–16 ns)** → r = **−0.698**.
   Both consistent with "fouling attenuates/redistributes energy", but the field result
   suggests the discriminative window may be the **whole-ballast envelope integral**,
   not just the late coda. Re-run `plot_coda_energy_vs_fi.py` with a full-ballast-window
   variant and compare |r|.

4. **[med] Reframe contribution as "ML generalization of MLR".**
   Cite Shapovalov 2026: real-field MLR over 5 indicators hits R²=0.97; our RF over 572
   features is the nonlinear extension. Add to OBJECTIVES_AND_HYPOTHESIS.md.

5. **[med] Use their gradation (`<5/5–15/15–30/>30%`) + >30% maintenance trigger** as
   the operational frame for "is accuracy good enough?" (answers defense Q12).

6. **[low] Temper the antenna-clearance argument.** They got r=0.96 at ~0.5 m height —
   but with a *directional horn* and whole-layer integration, not our Hertzian dipole +
   coda. Note the distinction before over-claiming the clearance effect.

7. **[future] Multi-frequency.** They use 400 + 1700 MHz; CrossNum/InflecNum may become
   effective at higher frequency. Supports a multi-frequency simulation track.

## Cross-refs
- `EXPERIMENT_LIMITATIONS.md` §5.2 (baselines), §6.2 (moisture)
- `OBJECTIVES_AND_HYPOTHESIS.md` (H3 microstructural features; Q3 class separation)
- `scripts/visualization/plot_coda_energy_vs_fi.py` (our r=−0.698 result)
- `REFERENCES.md` (add full citation)
