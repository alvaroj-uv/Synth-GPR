# Li et al. 2023 — Reference & Action Items

**Paper:** Li B., Peng Z., Wang S., Guo L. (2023). *Identification of Ballast Fouling
Status and Mechanized Cleaning Efficiency Using FDTD Method.* Remote Sensing 15, 3437.
DOI: 10.3390/rs15133437 (open access, CC BY). Zotero key `6FM8FKIF`.

**Why it matters to Synth-GPR:** This is the **multi-class, energy-curve precursor** to
[[Li]] (same group, 2025). Two things make it more directly useful than the 2025 paper
for our RF: (1) it models **three fouling levels** (clean / moderately fouled / highly
fouled), not just binary — closer to our multi-class FI target; and (2) it adds an
**energy-integration curve** (cumulative trace energy) as a third waveform-only
discriminator, which is a concrete feature we should confirm we have. Everything is
recovered **from the waveform alone**, no metadata.

---

## Their pipeline (vs. ours)

| Stage | Li 2023 | Synth-GPR equivalent |
|---|---|---|
| Clean geometry | **Random Irregular Polygon (RIP)**: circle split into `k` sides, radius perturbed by Δr; placed by **matrix-based collision detection (CD)**, `min(ΔD) ≥ 0` | our angular-rock packing modes |
| Gradation | sieve % from field samples → 3 fouling levels (Table 1) | our FI / gradation control |
| Solver | gprMax FDTD, RTX 3060 | gprMax FDTD |

**Sim parameters:**
- `dx_dy_dz = 0.001, 0.001, 0.01`; model 5.0 m × 2.5 m (fouling), 15 m × 2.5 m (cleaning).
- 2.0 GHz built-in **dipole**, 0.05 m from rail, **0.3 m height**, 0.05 m step.
- 80 A-scans (0.5–4.5 m) for fouling; 260 A-scans (1–14 m) for cleaning model.
- **ε (measured):** Air 1, Ballast **6**, Sand 12, Subgrade 15 (σ = 1, 0.01, 0.001, 0.01).
  Appendix A documents a buried-steel-plate two-way-time method to measure ε, and cites
  Clark 2001 dry-clean range **3–26.9**. ⚠ Li 2025 uses ballast ε = 4 — reconcile.

---

## Their 3 waveform-only discriminators (map to our features)

| Discriminator | What it measures | Our 572-feature equivalent |
|---|---|---|
| **Hilbert transform energy** | envelope (instantaneous amplitude) energy; denser/stronger with fouling | `area_hilbert` / Hilbert block — but confirm window |
| **S-transform time-frequency** | energy 1.0–3.0 GHz (sim) / 1.0–6.0 GHz (field); decay rate ↑ with fouling | STFT + frequency blocks |
| **Energy-integration curve** | cumulative trace energy, smoothed+normalized 0–1; fouled ≈ 0.8, clean ≈ 0 | **CHECK — do we have a cumulative trace-energy feature?** |

**Multi-class result (the useful part):** high-frequency energy persists to ~12 ns
(clean), decays by ~6 ns (moderate), starts significant decay ~5 ns (highly fouled). A
**monotonic, ordinal** waveform signature across 3 classes — directly supportive of our
multi-class separability hypothesis.

**Cleaning-efficiency model:** 15 m strip, fouled ends + clean centre; integrated-energy
curve cleanly separates (~0.8 vs ~0). Field: 25–42.5 km cleaned section drops to ~0, rest
~0.8. A nice "operational decision" frame (cf. Shapovalov's >30% trigger).

---

## The gap our RF fills
Same as [[Li]]: discrimination is **visual reading** of energy maps + a hand-built
integration curve — no feature vector, no trained classifier. Our RF generalizes their 3
hand-crafted indicators (Hilbert / S-transform / integration curve) into 572 features with
a learned multi-class decision boundary. Their Table 3 also positions their method vs.
**RSA (circles)** and **DEM (few 3D polygons)** — useful related-work framing.

---

## ACTION ITEMS

1. **[high] Confirm we have an "energy-integration curve" feature** — cumulative |amplitude|
   (or envelope energy) along the trace, smoothed/normalized. If missing, it is cheap,
   literature-backed (Li 2023 + Shapovalov's StAb), and currently the most distinctive
   indicator we may be lacking. Pairs with action #1 in [[REF_Shapovalov2026_ideas]].
2. **[high] Use their 3-level gradation (Table 1) as a multi-class sanity reference.**
   Their clean/moderate/highly split shows a monotonic coda-decay trend — compare against
   our FI-class coda-energy plots (`plot_coda_energy_vs_fi.py`).
3. **[med] Reconcile ballast ε** (this paper = 6; [[Li]] = 4) and cite the Appendix-A
   steel-plate measurement method + Clark 2001 range in our materials doc.
4. **[low] Adopt their data-processing chain** as a documented reference: background-mean
   removal → AGC → sleeper-interference truncation → max-normalization (Appendix B).

## Limitations they state (and our contrast)
- **2D**, per-particle **homogeneous isotropic** ε — same caveat as [[Li]] and the
  heterogeneity argument in [[Harajchi]].
- No moisture / rainfall (dominant real-field error per [[REF_Shapovalov2026_ideas]]).

## Cross-refs
- [[Li]] — same group, 2025, PFC2D+DRM, binary but more realistic geometry
- [[Harajchi]] — heterogeneous vs homogenized ballast
- [[REF_Shapovalov2026_ideas]] — real-field counterpart; StAb / Hilbert indicators
- `scripts/visualization/plot_coda_energy_vs_fi.py`, `OBJECTIVES_AND_HYPOTHESIS.md`, `REFERENCES.md`
