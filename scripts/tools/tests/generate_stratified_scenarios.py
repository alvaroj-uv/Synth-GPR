"""
Generate all representative stratified fouling scenarios and render PNG blueprints.

Five physically distinct cases:
  1. Clean            — both halves clean (baseline)
  2. Subgrade MC      — light migration from subgrade (bottom MC, top C)
  3. Subgrade Uprising — heavy bottom fouling, clean top (Bianchini Ciampoli Config 3)
  4. Uniform Fouled   — both halves heavily fouled
  5. Surface Infiltration — top fouled, bottom clean (reversed gradient)

Usage:
    python scripts/tools/tests/generate_stratified_scenarios.py
"""
import sys, dataclasses
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import matplotlib
matplotlib.use("Agg")

from src.config import GeneratorConfig
from src.physics import convert_pvc_to_fi, classify_fouling_index
from src.work_order import WorkOrder, WorkOrderSystem
from src.production_line import ProductionLine
from src.file_writer import GPRMaxFileWriter
from src.visualization.scene import parse_in_file, render_geometry_figure

OUT_DIR = Path("d:/Codigo/Synth-Data/StratifiedScenarios")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_CFG = dataclasses.replace(
    GeneratorConfig(granular_mode=True),
    stratified_fouling=True,
    pvc_min=0.0,
    pvc_max=100.0,
    base_seed=9000,
)

# (label, description, pvc_bottom %, pvc_top %, seed)
SCENARIOS = [
    ("s1_clean",          "Clean / Clean",              0.0,  0.0,  9001),
    ("s2_subgrade_mc",    "Subgrade MC / Clean",        20.0, 3.0,  9002),
    ("s3_subgrade_uprising","Subgrade F / Clean",       65.0, 0.0,  9003),
    ("s4_uniform_fouled", "Uniform F / F",              65.0, 60.0, 9004),
    ("s5_surface_infilt", "Surface MF / Clean bottom",  5.0,  55.0, 9005),
]


def fi_label(pvc_b: float, pvc_t: float) -> str:
    fi_b = convert_pvc_to_fi(pvc_b)
    fi_t = convert_pvc_to_fi(pvc_t)
    fi_mean = (fi_b + fi_t) / 2.0
    return (f"bot PVC={pvc_b:.0f}% (FI={fi_b:.1f}%)  "
            f"top PVC={pvc_t:.0f}% (FI={fi_t:.1f}%)  "
            f"-> mean FI={fi_mean:.1f}% [{classify_fouling_index(fi_mean)}]")


def build_params(pvc_b: float, pvc_t: float, seed: int) -> dict:
    import random
    random.seed(seed)
    fi_b = convert_pvc_to_fi(pvc_b)
    fi_t = convert_pvc_to_fi(pvc_t)
    fi   = (fi_b + fi_t) / 2.0
    return {
        "ballast_thickness": 0.45,
        "moisture": 0.05,
        "antenna_offset": 0.0,
        "pvc":        (pvc_b + pvc_t) / 2.0,
        "pvc_bottom": pvc_b,
        "pvc_top":    pvc_t,
        "FI":         fi,
        "FI_bottom":  fi_b,
        "FI_top":     fi_t,
        "FI_class":   classify_fouling_index(fi),
    }


def generate_one(scenario_id: str, desc: str, pvc_b: float, pvc_t: float, seed: int):
    import random
    random.seed(seed)

    params   = build_params(pvc_b, pvc_t, seed)
    wo       = WorkOrder.from_sampled_params(0, params)
    wos      = WorkOrderSystem(wo)
    pipeline = ProductionLine(BASE_CFG)
    checkpoint = pipeline.run(wos)

    in_path  = OUT_DIR / f"{scenario_id}.in"
    png_path = OUT_DIR / f"{scenario_id}.png"

    GPRMaxFileWriter.save_scene_checkpoint(checkpoint, output_path=str(in_path), scenario_type="Sim")

    scene = parse_in_file(in_path)
    title = f"{desc}\n{fi_label(pvc_b, pvc_t)}"
    fig, _ = render_geometry_figure(scene, title=title, dpi=150)
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)

    print(f"  [OK] {scenario_id}.in + .png — {fi_label(pvc_b, pvc_t)}")
    return str(in_path), str(png_path)


if __name__ == "__main__":
    print("=" * 65)
    print("Generating stratified fouling scenarios")
    print(f"Output: {OUT_DIR}")
    print("=" * 65)

    for scenario_id, desc, pvc_b, pvc_t, seed in SCENARIOS:
        print(f"\n[{scenario_id}] {desc}")
        generate_one(scenario_id, desc, pvc_b, pvc_t, seed)

    print("\n" + "=" * 65)
    print(f"Done. Files in: {OUT_DIR}")
