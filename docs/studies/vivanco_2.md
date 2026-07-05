# Rojas-Vivanco et al. 2026 (Sci Rep, in press) — Substructure performance indicators from multi-source data

**Citation:** Rojas-Vivanco J., Breul P., Talon A., Benz M., Villavicencio G., Pinto H., García J.
"Assessment of the condition of railway substructure by developing performance indicators based on
data from multiple sources." *Scientific Reports* (2026). DOI: 10.1038/s41598-026-58962-5.
In-house group (PUCV + Clermont Auvergne + Sol Solution) — companion/successor to the Rojas 2025
thesis (`rojasvivanco.md`), which defines our real-data pipeline.

## What the paper does

Builds **per-layer performance indicators** (ballast, interlayer/subballast, subgrade) from
heterogeneous inspection data — GPR, light dynamic penetrometer (LDCP/Panda) + geoendoscopy,
surface video — using Functional Analysis + FMEA + fault trees, aggregated with expert AHP
(Saaty) weights (5 experts, 72 pairwise comparisons, CR < 0.1) onto a **universal 0–10 scale with
five states** (excellent / good / medium / poor / critical). Evaluated on a 35 km single-track
mixed-traffic line (UIC group 6, 7 000–14 000 t/day) at 1 m resolution, benchmarked by confusion
matrices against the manager's **multidomain diagnosis** (Case 1 = no work, Case 2 = more info,
Case 3 = intervene).

## Where OUR work plugs in (the important part)

The ballast fault tree (Fig. 3a) is fed by parameters we produce or could produce:

| Fault-tree node | Parameter | Our pipeline |
|---|---|---|
| P1 | **Fouling index** — dominant weight for drainage (A1); experts rank it top because FI ↔ permeability | The waveform-only FI classifier IS this input, meter-resolved without trenching |
| P7 / P3 | **Ballast thickness** (also feeds subgrade-protection function) | Layer-stripping / CRIM envelope inversion outputs thickness |
| P6 | **Moisture condition** | The (f, S_w) CRIM two-observable inversion idea would supply S_w — currently no GPR-derived moisture input exists in their scheme |
| P2 | Vegetation (drainage) | video only; explicitly "no studies quantify it" |

FI is normalized to the universal scale via the **Selig & Waters bins**: <1 % excellent,
1–10 good, 10–20 medium, 20–40 poor, >40 critical. This is the operational class system the
indicators consume — i.e., the deployment target for our classifier is **these five Selig
states**, not the 0/10/20/30/40 notebook bins (cf. `feedback_two_fi_definitions`).

## Other findings relevant to us

- **Layer hierarchy:** "the shallower the layer, the greater its impact on decision making" —
  ballast condition dominates interventions; supports our ballast-first focus.
- **Drainage + vertical stability** are the functions most correlated with intervention cases —
  both are FI-driven, reinforcing FI as the highest-value quantity to estimate from GPR.
- **Validation is consistency, not ground truth** (their own Limitations §6): benchmark is the
  multidomain framework, no trenching/post-intervention verification. Same epistemic status as
  our sim→real comparisons — useful precedent for phrasing thesis claims.
- Robustness: ±10 % weight perturbation (Monte Carlo, 10 000 draws) doesn't change classes;
  ±10 % threshold shifts keep 66–89 % classification stability per layer, ~85 % global.
- Future-work section explicitly calls for **machine learning to feed/refine the indicators** —
  the slot our waveform-only RF/XGBoost work occupies.

## Status for our project

**REFERENCE (motivation) + PENDING (two actionables):**
1. Align production classifier output to the five Selig states used by the indicator scale.
2. The CRIM inversion's S_w output would fill P6 (moisture) — a fault-tree input that currently
   has no instrumented source; strengthens the case for the (f, S_w) two-observable inversion.
