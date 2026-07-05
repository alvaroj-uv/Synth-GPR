# Experiment 2026-06-29 — Layer model from EFE B-scan picks (PK 20 000 m)

## Goal

Close the real→synthetic loop: translate horizon picks from the real EFE
Puerto Limache GPR B-scan directly into a gprMax layered model, then run
FDTD to produce a synthetic A-scan for comparison with the real trace at the
same position.

## Methodology

1. Loaded the stitched real B-scan (`D:/Codigo/Data/efe_full_agc.h5`, AGC-corrected).
2. Picked three horizons visually at PK ≈ 20 000 m:
   - **Ballast surface**: ~5.5 ns two-way travel time
   - **Ballast base**: ~12.0 ns
   - **Subgrade**: ~19.5 ns
3. Converted intervals to layer thicknesses via `picks_to_layer_toml()`
   (Sussmann 2000: `d = c × t_oneway / sqrt(ε)`):
   - Ballast: (12.0 − 5.5) ns, ε = 5.1 → **0.431 m**
   - Subgrade: (19.5 − 12.0) ns, ε = 12.0 → **0.325 m**
4. Wrote TOML → `generate_gprmax_scenes.py` → `.in` file.

## EM properties used

| Layer | ε | σ (S/m) | Source |
|---|---|---|---|
| Ballast | 5.1 | 0.001 | Validated pipeline (r=0.913 with real DZT) |
| Subgrade | 12.0 | 0.05 | Literature (fouled/moist subgrade) |

## Expected results

- Synthetic A-scan should show surface reflection at ~5.5 ns and
  ballast-base reflection at ~12 ns, matching the real trace envelope shape.
- Any mismatch in reflection timing or amplitude characterises the
  residual sim→real domain gap at this location.

## Known caveats

- Hardware trigger delay (~3 ns) not subtracted from the surface time —
  the 5.5 ns value includes this offset, so true antenna standoff is
  likely 0.05 m (5 cm on-rail), not 0.75 m.
- Domain width (0.5 m) is below the FDTD-guideline minimum of 2.14 m at
  420 MHz; boundary reflections may appear after ~12 ns.
- Homogeneous layers: no rocks, no heterogeneous fouling.

## Results

The simulation completed in 18 s (7 068 time-steps, 420 MHz, 2 m × ~1.1 m domain).

**`syn_vs_real_pk20000m.png`** — synthetic vs real A-scan comparison:
- Real trace (EFE AGC HDF5, PK 20 000 m, idx 194 125) shows clear multi-interface
  reflections at +6 ns (ballast base) and +13 ns (subgrade) after the direct wave.
- Synthetic trace: essentially one dominant direct-wave pulse then **no visible coda**.
  The homogeneous `free_space` ballast matrix + RIP rocks produces no detectable
  ballast-base or subgrade reflections at the Rx.

**Interpretation:** The matrix permittivity mismatch (ε_ballast=5.1 vs ε_matrix=1) creates
an overwhelming surface reflection that drains energy before it reaches the interfaces.
Setting `matrix = "free_space"` is physically incorrect for the void-fill — use a
soil/fouling matrix (ε=2–4) as the inter-rock filler in future models.

Direct-wave alignment: synthetic peak at 3.21 ns, real peak at 5.97 ns
(difference = 2.76 ns, consistent with 0.05 m standoff × ε_air = ~0.33 ns —
the remainder is hardware trigger delay).

## Inversion — envelope vs Wasserstein, and the d–ε degeneracy (overnight, 4704 gprMax runs)

Folder `inversion/`. Flat 3-layer forward proxy (deterministic, no rocks),
inverting against ONE raw trace at PK 20 000 m (`D:/Codigo/Data/efe_full.h5`,
**raw not AGC** — AGC destroys coda coherence). Objective lives in
`src/signal_processing.py`: `coda_envelope_correlation` (phase-blind) vs
`coda_wasserstein_distance` (optimal transport, keeps timing — Lu et al. 2024).

**4-D sweep** `invert_pk20000m_w2_grid.py`: ε_b(21) × d_ballast(14) ×
ε_s(4) × ε_f(4) = 4704 FDTD runs, 8.84 h, 0 failures.

**Findings** (`degeneracy_ridge_maps.png`, `objective_landscapes.png`):
- The **d–ε degeneracy** is a diagonal valley along `d·√ε = const` (= ballast-base
  two-way time). A single trace constrains the *product*, not d and ε separately.
- **W₂ tightens the degeneracy ~70×** (9 near-optimal cells vs envelope-r's 618)
  and places the ballast base at the physical ~6.5–7 ns (≈ real 6.3 ns), where
  envelope-r is biased early (~5 ns) because it discards phase.
- **W₂ still leaves a ridge** — its optimum railed ε_b to the grid bound (7.0);
  ε_s, ε_f also weakly constrained (pinned to bounds).

**Reading ε_b** (`epsb_ridge_readout.png`): at the picked thickness d ≈ 0.43 m
the W₂ inversion reads **ε_b ≈ 5.8–6.9** (softplus 5.8 [4.7–7.0]; envelope 6.9,
boundary-railed) — the *fouled* range, consistent with this HF specimen
(validated pipeline: clean 5.1 / fouled 9.5). Envelope-r reads 3.1 (clean —
inconsistent with HF; phase-blind bias).

**Honest caveat — the B-scan does NOT independently break the degeneracy.** The
B-scan ballast-base pick (6.5 ns TWT → d·√ε ≈ 0.975) and the W₂ inversion
(d·√ε ≈ 0.98) constrain the *same* quantity. Splitting d from ε needs an
external depth (core/trench — unavailable) or an assumed ε. What the waveform
*does* deliver: a 70×-tighter TWT constraint than envelope-r, and it rules out
clean ballast (ε≈3) — corroborating the HF class from the waveform alone.

## v3 — formation layer (deep reflector)

A/B from v2: **identical geometry**, only the bottom layer ε changed 12→20
(saturated formation / wet clay below the dry subgrade). This turns the
y=0.3 m boundary into a real interface (R≈−0.13).

**Result** (`syn_vs_real_v3_formation.png`, background-subtracted, first-break
aligned, 22 ns window): the synthetic now shows **three reflectors** —
surface, ballast base (~8.3 ns), and a **new formation event (~15.6 ns)** where
v2 was silent. The synthetic coda now spans the full 0–16 ns range like the
real trace instead of dying after the ballast base.

| Fix applied | Outcome |
|---|---|
| subgrade_pad ε 12→20 (formation) | deep reflection appears at ~15.6 ns ✓ |
| display window → 22 ns | deep event now visible (was clipped at 12.5) ✓ |
| first-break picking (both traces) | consistent convention, removes peak-vs-break bias ✓ |

**Honest caveats (for the inversion, not yet fixed):**
- Real near-surface coda (0–3 ns) is richer than synthetic — likely ballast
  heterogeneity / multiples, not a single interface.
- Deep-event timing is in the right *zone* but not pinned to the real coda;
  exact alignment is an inversion problem (retrieve thickness/ε), not a
  forward-model tweak.
- 4.15 ns feature is small — likely ballast-internal / rock scatter, or the
  surface residual; not a primary interface.

Code: `compare_synthetic_vs_real_bgsub()` in `unified_visualizer.py`
(background subtraction + consistent first-break picking).

## Files

| File | Description |
|---|---|
| `efe_pk20000m.toml` | Layer config (source of truth) |
| `from_picks_pk20000m.in` | gprMax input file (auto-generated) |
| `from_picks_pk20000m.png` | Geometry cross-section (auto-rendered) |
| `from_picks_pk20000m.out` | gprMax output (simulation complete) |
| `syn_vs_real_pk20000m.png` | Synthetic vs real A-scan comparison |
| `run_gprmax.bat` | Conda activation + gprMax runner |
| `run_log.txt` | gprMax run log |

## How to regenerate

```bash
conda activate gprMax
python -m gprMax experiments/2026-06-29/from_picks_pk20000m.in
```

To reproduce the comparison plot:
```python
from scripts.visualization.unified_visualizer import compare_synthetic_vs_real
compare_synthetic_vs_real(
    out_path='experiments/2026-06-29/from_picks_pk20000m.out',
    h5_path='D:/Codigo/Data/efe_full_agc.h5',
    out_png='experiments/2026-06-29/syn_vs_real_pk20000m.png',
    pk_m=20000.0, max_time_ns=25.0,
    layer_times_ns=[5.5, 12.0, 19.5],
    layer_labels=['surface', 'ballast base', 'subgrade'],
)
```
