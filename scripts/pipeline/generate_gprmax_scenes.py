#!/usr/bin/env python3
"""
TOML-driven .in file generator for GPR simulations.

The TOML config is the SOLE source of truth — there are NO scene-config CLI
flags. The only command-line inputs are the config path and an optional output
override (``-o``). This guarantees one unambiguous configuration per run.

A single config selects what to generate via ``[job].mode`` (or auto-detection
from the sections present):

    mode = "batch"   -> per-class dataset (N samples/class)  ([sim] + [batch])
    mode = "single"  -> one sampled .in file                 ([sim] + [single])
    mode = "layers"  -> one arbitrary N-layer scene
                        ([sim]/[source]/[scenario]/[[layer]]/[[command]])

Auto-detection (when [job].mode is absent): [[layer]] -> layers,
[batch] -> batch, [single] -> single. This keeps legacy scene TOMLs working.

TWO DISTINCT .in FORMATS — by design, not a bug:
  * batch + single share the CANONICAL DATASET FORMAT (DatasetGenerator +
    GPRMaxFileWriter): FDTD-guideline-sized domain, the fixed mbubia stack, and
    the full FI_class / Lab_* / Lab_PSD / CONFIG_* training metadata header.
    This is the format the v2/v3 corpora and the training/feature pipelines
    expect — use batch/single for any data that will be modelled.
  * layers is a SEPARATE lightweight scene-PROTOTYPING tool
    (layer_scene_builder): arbitrary layer stacks, a small derived domain, and a
    minimal header WITHOUT training labels. Handy for one-off geometry/physics
    experiments; NOT a drop-in source of dataset .in files.

Rendering uses src.visualization.render.render_geometry_png directly (in-process).
All .in files contain embedded CONFIG_* and SOURCE_* headers for replication.

Usage:

    # N-layer scene
    python scripts/pipeline/generate_in_files.py examples/scenes/three_layer_circlify.toml -o out.in

    # Per-class dataset
    python scripts/pipeline/generate_in_files.py configs/v3_dataset.toml -o gpr_synth_dataset_v3/

    # One sampled file
    python scripts/pipeline/generate_in_files.py configs/single_400mhz.toml -o test.in
"""

import sys
import argparse
from pathlib import Path
import time
import logging

# Configure logging for data access operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig, create_per_label_config
from src.dataset_generator import DatasetGenerator
from src.fouling import get_pvc_range
from src.data_access import PNGWriter


def apply_seed(seed: int | None):
    """Apply seed to both random and numpy for reproducibility."""
    if seed is not None:
        import random
        random.seed(seed)
        try:
            import numpy as np
            np.random.seed(seed)
        except ImportError:
            pass


def generate_batch(
    output_dir: Path,
    labels: list[str],
    n_per_label: int,
    freq_hz: float,
    angular: bool,
    sides: int,
    packing_algo: str,
    psd_type: str,
    num_rx: int,
    rx_spacing: float,
    moisture_max: float,
    start_id: int,
    seed: int | None,
) -> int:
    """Generate batch dataset with N samples per fouling class."""

    print(f"\n{'='*70}")
    print("BATCH MODE: Generate Dataset per Fouling Class")
    print(f"{'='*70}")
    print(f"Output Directory: {output_dir}")
    print(f"Labels: {labels}")
    print(f"Samples/Label: {n_per_label}")
    print(f"Frequency: {freq_hz/1e6:.0f} MHz")
    print(f"Angular Rocks: {angular} ({sides} sides)")
    print(f"Packing Algorithm: {packing_algo}")
    print(f"PSD Type: {psd_type}")
    print(f"Moisture Max: {moisture_max}")
    print(f"{'='*70}\n")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create base config using physically perfect (frequency-aware)
    base_config = GeneratorConfig.create_physically_perfect(
        center_freq_hz=freq_hz,
        num_receivers=num_rx,
        receiver_spacing=rx_spacing,
        rock_packing_algorithm=packing_algo,
        rock_psd_type=psd_type,
        angular_rocks=angular,
        rock_sides=sides,
        moisture_max=moisture_max,
        base_seed=seed if seed is not None else start_id,
    )

    current_id = start_id
    total_generated = 0
    start_time = time.time()

    for label in labels:
        label_upper = label.upper()
        try:
            pmin, pmax = get_pvc_range(label_upper)
        except ValueError as e:
            print(f"[WARN] {e}, skipping")
            continue

        print(f">> Generating {label_upper} (PVC {pmin:.0f}-{pmax:.0f}%) ...")

        # Create label-specific config with PVC range
        cfg = create_per_label_config(base_config, label_upper)

        gen = DatasetGenerator(cfg)
        files = gen.generate_samples(
            output_dir=output_dir,
            n_samples=n_per_label,
            start_id=current_id,
        )

        count = len(files)
        print(f"  [OK] Generated {count} samples. IDs: {current_id} -> {current_id + count - 1}")

        current_id += count
        total_generated += count

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"Completed in {elapsed:.2f}s")
    print(f"Total Samples Generated: {total_generated}")
    print(f"{'='*70}\n")

    return total_generated


def generate_single(
    output_path: Path,
    freq_hz: float,
    pvc: float | None,
    moisture: float | None,
    angular: bool,
    sides: int,
    packing_algo: str,
    psd_type: str,
    num_rx: int,
    rx_spacing: float,
    render: bool,
    seed: int | None = None,
    domain_x: float | None = None,
    dx: float | None = None,
    randomize_rock_materials: bool = False,
) -> Path:
    """Generate a single .in file with optional PNG visualization."""

    print(f"\n{'='*70}")
    print("SINGLE MODE: Generate One .in File")
    print(f"{'='*70}")
    print(f"Output File: {output_path}")
    print(f"Frequency: {freq_hz/1e6:.0f} MHz")
    print(f"PVC: {pvc if pvc is not None else 'sampled'}")
    print(f"Moisture: {moisture if moisture is not None else 'sampled'}")
    print(f"Angular Rocks: {angular} ({sides} sides)")
    print(f"Packing Algorithm: {packing_algo}")
    print(f"Render PNG: {render}")
    print(f"Seed: {seed if seed is not None else 'random'}")
    print(f"{'='*70}\n")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create config with frequency scaling
    extra = {}
    if domain_x is not None:
        extra['domain_x'] = domain_x
    if dx is not None:
        extra['dx'] = dx
    config = GeneratorConfig.create_physically_perfect(
        center_freq_hz=freq_hz,
        num_receivers=num_rx,
        receiver_spacing=rx_spacing,
        rock_packing_algorithm=packing_algo,
        rock_psd_type=psd_type,
        angular_rocks=angular,
        rock_sides=sides,
        pvc_min=pvc if pvc is not None else 0.0,
        pvc_max=pvc if pvc is not None else 100.0,
        moisture_min=moisture if moisture is not None else 0.0,
        moisture_max=moisture if moisture is not None else 0.3,
        base_seed=seed,
        randomize_rock_materials=randomize_rock_materials,
        **extra,
    )

    # Apply seed if provided (for exact geometry reproducibility)
    apply_seed(seed)

    gen = DatasetGenerator(config)

    # Provenance for SOURCE_* headers (pinned vs sampled vs default)
    override = pvc is not None and moisture is not None
    param_sources = {
        'pvc': 'CLI_OVERRIDE' if override else 'SAMPLED',
        'moisture': 'CLI_OVERRIDE' if override else 'SAMPLED',
        'base_seed': 'CLI_OVERRIDE' if seed is not None else 'DEFAULT',
    }

    # Production-line orchestration lives in DatasetGenerator, not the CLI.
    written_path = gen.generate_one(
        output_path, pvc=pvc, moisture=moisture, param_sources=param_sources,
    )

    print(f"[OK] Wrote .in file: {written_path}")

    # Optionally render PNG using data access layer
    if render:
        try:
            png_writer = PNGWriter()
            png_path = png_writer.write(output_path.with_suffix('.png'), written_path, dpi=150)
            print(f"[OK] Rendered visualization: {png_path}")
        except Exception as e:
            print(f"[WARN] Could not render PNG: {e}")

    print(f"\n{'='*70}\n")
    return Path(written_path)


def run_batch_layers(config_path: Path, data: dict, output_dir: Path) -> int:
    """Batch generation over an arbitrary [[layer]] stack.

    Emits N seed-varied realizations of the SAME declared layer stack. Each .in
    carries the dataset-format header (FI_class/Lab_*/CONFIG_*) computed by
    LabWorker on that realization — so the label is MEASURED per realization, not
    a per-class PVC target. (Per-class PVC targeting over arbitrary layers would
    need a fouling-fill knob; the fixed-stack batch path still does that.)
    """
    import dataclasses
    from src.layer_spec import parse_config_file
    from src.layer_scene_builder import write_scene

    config = parse_config_file(config_path)
    params, ps = config.to_scene_params()
    b = data.get("batch", {}) or {}
    n = int(b.get("n_per_label", b.get("num", 50)))
    start_id = int(b.get("start_id", 1000))
    base_seed = params.seed if params.seed is not None else 0

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{'='*70}\nBATCH MODE (arbitrary [[layer]] stack)\n{'='*70}")
    print(f"Config (TOML): {config_path}")
    print(f"Output Directory: {output_dir}")
    print(f"Layers (bottom -> top): {len(config.layers)}   Realizations: {n}   "
          f"Base seed: {base_seed}  (label = measured per realization)")
    print(f"{'='*70}\n")

    written = []
    for k in range(n):
        seed = base_seed + k
        p = dataclasses.replace(params, seed=seed)
        out = output_dir / f"s_{start_id + k}.in"
        write_scene(config.layers, p, out, raw_commands=config.raw_commands,
                    param_sources=ps, scenario=config.lab if config.lab else None)
        written.append(out)
        print(f"  [OK] s_{start_id + k}.in  (seed={seed})")

    print(f"\n{'='*70}\nCompleted: {len(written)} files in {output_dir}\n{'='*70}\n")
    return 0


def generate_layers(config_path: Path, output_path: Path, render: bool = False) -> int:
    """Generate one arbitrary N-layer .in file from a TOML scene config.

    The TOML ([sim]/[source]/[scenario]/[[layer]]/[[command]]) is the SOLE source
    of truth — there are no CLI scene overrides. Everything that shapes the scene
    (frequency, domain, packing algorithm, layers, seed) lives in the file.
    """
    from src.layer_spec import parse_config_file
    from src.layer_scene_builder import write_scene

    config = parse_config_file(config_path)
    params, ps = config.to_scene_params()

    print(f"\n{'='*70}\nN-LAYER MODE: Generate One .in File\n{'='*70}")
    print(f"Config (TOML): {config_path}")
    print(f"Output File: {output_path}")
    print(f"Frequency: {params.freq_hz/1e6:.0f} MHz   Domain X: {params.domain_x} m   "
          f"Source waveform: {params.source_waveform}")
    print(f"Rock packing algorithm: {params.rock_packing_algorithm} [TOML]")
    print(f"Layers (bottom -> top): {len(config.layers)}")
    for i, ly in enumerate(config.layers):
        kind = (f"PACKED rocks(eps={ly.rock_eps}) in matrix '{ly.matrix_name}'"
                if ly.packed else f"flat (eps={ly.eps}, sigma={ly.sigma})")
        print(f"  [{i}] {ly.name:18s} thickness={ly.thickness:.3f} m  {kind}")
    if config.raw_commands:
        print(f"Passthrough commands: {len(config.raw_commands)}")
    print(f"{'='*70}\n")

    written = write_scene(config.layers, params, output_path,
                          raw_commands=config.raw_commands, param_sources=ps,
                          scenario=config.lab if config.lab else None)
    print(f"[OK] Wrote .in file: {written}")

    if render:
        try:
            png_writer = PNGWriter()
            png_path = png_writer.write(output_path.with_suffix(".png"), written, dpi=150)
            print(f"[OK] Rendered visualization: {png_path}")
        except Exception as e:
            print(f"[WARN] Could not render PNG: {e}")

    print(f"\n{'='*70}\n")
    return 0


def _load_toml(path: Path) -> dict:
    """Load a TOML config file into a dict using the data access layer."""
    from src.data_access import TOMLReader
    reader = TOMLReader()
    return reader.read(path)


def _resolve_mode(data: dict) -> str | None:
    """Pick the generation mode from [job].mode, else auto-detect from sections.

    Auto-detection keeps legacy scene TOMLs (which only carry [[layer]]) working
    without a [job] table.
    """
    mode = (data.get("job", {}) or {}).get("mode")
    if mode:
        return str(mode).lower()
    if data.get("layer"):
        return "layers"
    if "batch" in data:
        return "batch"
    if "single" in data:
        return "single"
    return None


def run_batch_from_toml(data: dict, output_dir: Path) -> int:
    """Drive per-class dataset generation entirely from a TOML config."""
    sim = data.get("sim", {}) or {}
    b = data.get("batch", {}) or {}
    generate_batch(
        output_dir=output_dir,
        labels=list(b.get("labels", ["CL", "MC", "MF", "F"])),
        n_per_label=int(b.get("n_per_label", b.get("num", 50))),
        freq_hz=float(sim.get("freq_hz", 1.5e9)),
        angular=bool(sim.get("angular", False)),
        sides=int(sim.get("sides", 6)),
        packing_algo=str(sim.get("rock_packing_algorithm", "circlify")),
        psd_type=str(sim.get("rock_psd_type", sim.get("psd", "uniform"))),
        num_rx=int(sim.get("num_rx", 1)),
        rx_spacing=float(sim.get("rx_spacing", 0.05)),
        moisture_max=float(b.get("moisture_max", 0.15)),
        start_id=int(b.get("start_id", 1000)),
        seed=int(sim["seed"]) if "seed" in sim else None,
    )
    return 0


def run_single_from_toml(data: dict, output_path: Path) -> int:
    """Drive single-file generation entirely from a TOML config."""
    sim = data.get("sim", {}) or {}
    s = data.get("single", {}) or {}
    generate_single(
        output_path=output_path,
        freq_hz=float(sim.get("freq_hz", 1.5e9)),
        pvc=float(s["pvc"]) if "pvc" in s else None,
        moisture=float(s["moisture"]) if "moisture" in s else None,
        angular=bool(sim.get("angular", False)),
        sides=int(sim.get("sides", 6)),
        packing_algo=str(sim.get("rock_packing_algorithm", "circlify")),
        psd_type=str(sim.get("rock_psd_type", sim.get("psd", "uniform"))),
        num_rx=int(sim.get("num_rx", 1)),
        domain_x=float(sim["domain_x"]) if "domain_x" in sim else None,
        dx=float(sim["dx"]) if "dx" in sim else None,
        rx_spacing=float(sim.get("rx_spacing", 0.05)),
        render=bool(s.get("render", False)),
        seed=int(sim["seed"]) if "seed" in sim else None,
        randomize_rock_materials=bool(s.get("randomize_rocks", False)),
    )
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="TOML-driven .in file generator for GPR simulations. "
                    "The TOML config is the SOLE source of truth — there are no "
                    "scene-config CLI flags.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The config TOML selects what to generate via [job].mode (or auto-detection):

  mode = "batch"   -> per-class dataset from [sim] + [batch]   (CANONICAL FORMAT)
  mode = "single"  -> one sampled .in file from [sim] + [single] (canonical fmt)
  mode = "layers"  -> N-layer scene from [sim]/[source]/[scenario]/[[layer]]
                      (lightweight PROTOTYPING format, no training labels)

batch/single produce the dataset format (FI_class/Lab_*/CONFIG_* header) that the
v2/v3 corpora and training expect. layers is a separate scene-prototyping tool
with a different, minimal header — not a source of dataset .in files.

If [job].mode is omitted: [[layer]] -> layers, [batch] -> batch, [single] -> single.
The output path comes from [job].output, or is overridden by -o/--output.

Examples:

  # N-layer scene (output overridden on the CLI)
  %(prog)s examples/scenes/three_layer_circlify.toml -o out.in

  # Per-class dataset (output dir in the TOML or via -o)
  %(prog)s configs/v3_dataset.toml -o gpr_synth_dataset_v3/

  # One sampled file
  %(prog)s configs/single_400mhz.toml -o test.in
        """,
    )
    parser.add_argument(
        "config",
        help="TOML config file — the sole source of truth for the scene/job.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output path (single/layers) or directory (batch). Overrides "
             "[job].output in the TOML. This is the only non-TOML input.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[FAIL] Config file not found: {config_path}")
        return 1
    if config_path.suffix.lower() != ".toml":
        print(f"[FAIL] Config must be a .toml file, got: {config_path.name}")
        return 1

    data = _load_toml(config_path)

    mode = _resolve_mode(data)
    if mode is None:
        print("[FAIL] Could not determine mode. Add [job] mode = \"batch|single|layers\", "
              "or include [[layer]] / [batch] / [single] in the TOML.")
        return 1

    output = args.output or (data.get("job", {}) or {}).get("output")
    if output is None:
        print("[FAIL] No output path. Set [job].output in the TOML or pass -o/--output.")
        return 1
    output_path = Path(output)

    has_layers = bool(data.get("layer"))
    render = bool((data.get("job", {}) or {}).get("render",
                  (data.get("sim", {}) or {}).get("render", False)))

    if mode == "layers":
        return generate_layers(config_path, output_path, render=render)
    elif mode == "batch":
        # An arbitrary [[layer]] stack routes through the layer builder (per-layer
        # eps/sigma/packing); otherwise the fixed-stack per-class dataset pipeline.
        if has_layers:
            return run_batch_layers(config_path, data, output_path)
        return run_batch_from_toml(data, output_path)
    elif mode == "single":
        if has_layers:
            return generate_layers(config_path, output_path, render=render)
        return run_single_from_toml(data, output_path)
    else:
        print(f"[FAIL] Unknown mode '{mode}' (expected batch|single|layers)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
