# Frequency sweep 100–2000 MHz (step 100) — three-layer trackbed

**Goal:** find at what antenna frequency the formation/subgrade interface
becomes resolvable as a *separate* event from the ballast/formation interface
in the A-scan, on the same geometry as Run 3 in `../README.md` (ballast 0.45m
eps=4.0 in air / formation 0.10m eps=10.0 / subgrade 0.20m eps=8.0).

**Method:** `run_freq_sweep.py` generates + runs one `.in`/`.out` per 100 MHz
step (dx omitted → auto-derived per frequency, dx shrinks from 5mm @100-800MHz
down to 1.5mm @2000MHz; everything else identical to Run 3, no rocks/PML
config changed). `analyze_sweep.py` Hilbert-envelopes each trace, gates out
the direct/surface pulse (t<5ns), **locally** renormalizes within the 5–15ns
coda window (not by the global trace max — see below), and counts peaks.

## Result

| Freq range | Peaks resolved (n) | What's happening |
|---|---|---|
| 100–800 MHz | 1 | Direct-wave pulse is wider than the ~2.1 ns gap between the two interface reflections → they merge into a single coda bump (thin-bed effect, matches the 420 MHz finding in `../README.md` Run 3) |
| 900 MHz | 2 | Separation starts |
| 1000–2000 MHz | 3–5 | Stably resolves both predicted reflections: a peak near **6.2–6.5 ns** (ballast/formation, predicted 6.3 ns) and a separate, weaker peak near **8.0–8.6 ns** (formation/subgrade, predicted 8.4 ns). Extra peaks (~5.5–5.9, ~7.4 ns) are wavelet ringing/sidelobes, not new interfaces. |

**Gotcha:** a first pass using a single threshold normalized by each trace's
*global* max (i.e. the huge direct-wave amplitude) found only 1 peak at every
frequency, even at 2000 MHz. The formation/subgrade reflection coefficient
(R ≈ 0.056, eps 10→8) is ~4x weaker in amplitude than the ballast/formation
one (R ≈ 0.225, eps 4→10) — so it falls under a global threshold and looks
"unresolved" even when it's actually present and time-separated. Re-detecting
peaks with **local** renormalization (within the gated coda window only)
revealed it. Lesson: weak-reflector resolution failures can be an amplitude
problem, not (only) a timing/bandwidth problem — check both before concluding
"not resolvable."

**Answer to "¿se resuelven las 3 interfaces?":** yes, from ~1000–1200 MHz
upward, the three interfaces (surface, ballast/formation, formation/subgrade)
are all distinguishable in time — but the deepest one is intrinsically weak
and needs gain/local normalization to see, not raw amplitude. At 420 MHz
(railway GPR's typical frequency) they are NOT separable; this is a
fundamental thin-bed/bandwidth limit, not a modeling bug.

## Files
- `run_freq_sweep.py` — sweep driver (TOML template + generate + gprMax per step)
- `three_layer_NNNNmhz.{toml,in,out}` × 20 (100–2000 MHz)
- `analyze_sweep.py` — naive Hilbert envelope + peak detection + comparison plots
- `freq_sweep_envelope_comparison.png` — stacked Hilbert-envelope plot, all 20 frequencies
- `freq_sweep_raw_comparison.png` — same stack but the raw oscillating Ez signal
  (no envelope) — shows the sign flip at the ballast/formation reflection
  (R=-0.225, eps 4→10) directly
- `analyze_sweep_vivanco.py` / `freq_sweep_vivanco_envelope_comparison.png` —
  same sweep run through the REAL production pipeline
  (`src/signal_processing.py vivanco_preprocess`, Rojas-Vivanco 2025 7-step
  chain) instead of a naive Hilbert envelope. See finding below.
- `sweep_log.txt` — run log (timings, all 20 OK, 6–21s each)

## Addendum — same sweep through the real `vivanco_preprocess()` pipeline

The "1000+ MHz resolves all 3 interfaces" finding above used an ad-hoc 15 ns
analysis window. Re-ran every `.out` through the actual production
preprocessing (`vivanco_preprocess()`, defaults: 150–800 MHz bandpass,
time-zero = direct-peak − 3 ns, **7 ns window**) — unscaled per simulated
frequency, i.e. exactly as it runs on real Puerto-Limache/French data.

**Result: the formation/subgrade reflection (predicted ~8.4 ns) is outside
the 7 ns window at every single frequency from 300–2000 MHz** — for those,
`time_zero_idx` lands at/near sample 0 (direct peak is <3 ns from trace
start), so the window only covers ~0–7 ns, and even the *stronger*
ballast/formation reflection (~6.3 ns) sits right at the trailing edge with
no margin. For antennas ≥1000 MHz, the fixed 150–800 MHz bandpass also
removes most of the trace's actual spectral content (centered well above
800 MHz), so those envelopes are largely flat residual-filter artifacts, not
real subsurface information.

**Implication:** this isn't just a synthetic-modeling curiosity — the
production feature-extraction window, as currently configured, structurally
cannot see anything at subgrade depth on this 3-layer geometry, regardless of
antenna frequency. If subgrade-level information ever matters for fouling
classification, either the window needs to extend well past 7 ns, or the
target's relevant physics has to live within the first ~6 ns (i.e. within the
ballast layer itself) for this pipeline to capture it at all.

### Follow-up: widening window_ns to 15 doesn't fix it either

Re-ran `analyze_sweep_vivanco.py --window-ns 15` (the script now takes
`--window-ns`, default 7.0). The formation/subgrade RTT now falls
geometrically inside the window at every frequency (see
`freq_sweep_vivanco_envelope_comparison_15ns.png`) — but locally-renormalized
peak detection (same method as `analyze_sweep.py`) in the 5–15 ns range still
finds only **one** peak for the in-band frequencies (400/600/800 MHz: single
peak at 6.6–7.7 ns, close to the ballast/formation prediction) and **zero**
peaks for out-of-band frequencies (1300/1600/2000 MHz: envelope is flat —
nothing survives the 150–800 MHz bandpass at all).

**Conclusion: it's not just the 7 ns window.** The fixed 150–800 MHz bandpass
filter — tuned to one specific real antenna's bandwidth — smooths away the
weak formation/subgrade reflection (R≈0.056) regardless of window length, and
for any simulated antenna whose actual spectral content sits outside
150–800 MHz, the filter discards essentially the whole trace. Both pipeline
constants (window AND bandpass) are antenna-specific, not general-purpose;
neither should be assumed to transfer to a different antenna/geometry without
re-tuning.

### Cropped traces: just the window the analysis actually uses

`crop_to_vivanco_window.py` saves, per frequency, only the segment
`vivanco_preprocess()` keeps (`[time_zero_idx, time_zero_idx + 7ns]`,
production default) as `three_layer_NNNNmhz_vivanco_crop.csv`
(`t_ns_local, processed, envelope` — `processed` is the raw oscillating
signal post dewow/bandpass/BGR, not the envelope). Confirmed the direct wave
sits inside this window at every frequency (0.6–3.0 ns in, depending on how
much the backward shift got clamped — see prior Q&A in this conversation),
consistent with the production pipeline's H-grid features intentionally
including the direct wave. Comparison plot:
`freq_sweep_vivanco_crop_comparison.png`.
