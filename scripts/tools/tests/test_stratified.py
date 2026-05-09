"""Quick test: generate one stratified fouling sample and render PNG."""
import dataclasses, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator

cfg = dataclasses.replace(
    GeneratorConfig(granular_mode=True),
    stratified_fouling=True,
    pvc_min=0.0,
    pvc_max=80.0,
    base_seed=7777,
)
gen = DatasetGenerator(config=cfg)
files, meta = gen.generate_samples(
    "d:/Codigo/Synth-Data/StratifiedTest",
    n_samples=1,
    start_id=7777,
)
m = meta[0]
print(f"pvc_bottom={m['pvc_bottom']:.1f}%  pvc_top={m['pvc_top']:.1f}%")
fi_b = m.get('FI_bottom')
fi_t = m.get('FI_top')
if fi_b is not None:
    print(f"FI_bottom={fi_b:.2f}  FI_top={fi_t:.2f}")
print(f"FI_class={m['FI_class']}  Lab_FI={m.get('Lab_FI', 'N/A')}")
print("Written:", files)
