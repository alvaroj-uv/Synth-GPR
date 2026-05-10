"""Test GradingCurve PSD sampler against all three distribution types."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))


from src.rock_packing import GradingCurve, CirclifyPacking, PackingBounds

packing = CirclifyPacking()
bounds  = PackingBounds(0, 1.0, 0, 0.5)

for label, kwargs in [
    ("uniform (default)",  {}),
    ("en13450 (ballast norm)", {"grading_curve": GradingCurve.en13450()}),
    ("fuller (max density)",   {"grading_curve": GradingCurve.fuller(d_max=0.08)}),
]:
    rocks  = packing.generate_rocks(bounds, 0.01, 0.04, **kwargs)
    radii  = [r.radius for r in rocks]
    print(f"[{label}]  n={len(rocks):3d}  "
          f"r_min={min(radii):.4f}  r_max={max(radii):.4f}  "
          f"r_mean={sum(radii)/len(radii):.4f}")

# Also verify that the config helper works
from src.config import GeneratorConfig
import dataclasses

for psd in ("uniform", "en13450", "fuller"):
    from src.rock_packing import _grading_curve_from_config
    cfg = dataclasses.replace(GeneratorConfig(), rock_psd_type=psd)
    gc  = _grading_curve_from_config(cfg)
    sample = gc.sample(clamp_min=cfg.rock_radius_min, clamp_max=cfg.rock_radius_max)
    print(f"  config psd_type={psd!r:<10} -> sample radius={sample:.4f} m")
