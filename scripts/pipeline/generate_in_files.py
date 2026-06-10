#!/usr/bin/env python3
"""
Unified .in file generator for GPR simulations.

Consolidates functionality of:
- generate_dataset.py (batch generation)
- generate_angular_rocks_400MHz.py (angular rocks specialist)
- generate_single_in_file.py (single file creation)

Supports two modes:
1. Batch: Generate N samples per fouling class
2. Single: Generate one .in file with optional PNG visualization

Rendering is delegated to scripts/visualization/unified_visualizer.py.
All .in files contain embedded CONFIG_* and SOURCE_* headers for replication.

Usage Examples:

    # Batch: 50 files per class, 1.5 GHz (default)
    python scripts/pipeline/generate_in_files.py output/ --mode batch --labels CL MC MF -n 50

    # Batch: 400 MHz angular rocks, 1000 per class
    python scripts/pipeline/generate_in_files.py output/ --mode batch --labels CL MC MF F HF \\
        -n 1000 --freq 400e6 --angular --packing-algo shang_chu

    # Single: Custom PVC, 1.5 GHz, with PNG
    python scripts/pipeline/generate_in_files.py test.in --mode single --pvc 25 --render

    # Single: 400 MHz, angular triangular rocks with Shang-Chu packing
    python scripts/pipeline/generate_in_files.py out.in --mode single --freq 400e6 --pvc 50 \\
        --angular --sides 3 --packing-algo shang_chu --render

    # Render existing .in file as PNG (unified visualizer, auto-detects 2D/3D)
    python scripts/visualization/unified_visualizer.py output.in --geometry -o output.png --dpi 200
"""

import sys
import argparse
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig, create_per_label_config
from src.dataset_generator import DatasetGenerator
from src.fouling import list_all_classes, get_pvc_range
from src.work_order import WorkOrder, WorkOrderSystem
from src.file_writer import GPRMaxFileWriter
from src.scene_model import parse_toml
from src.exporter import JSONExporter


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

    # For single file, use simple sample ID
    sample_id = 1

    # Track parameter sources for SOURCE_* headers
    param_sources = {}

    # If specific PVC/moisture given, use exact values (no sampling)
    if pvc is not None and moisture is not None:
        params = {
            'pvc': pvc,
            'moisture': moisture,
            'pvc_bottom': pvc,
            'pvc_top': pvc,
            'FI_bottom': pvc,
            'FI_top': pvc,
        }
        param_sources['pvc'] = 'CLI_OVERRIDE'
        param_sources['moisture'] = 'CLI_OVERRIDE'
        work_order = WorkOrder.from_sampled_params(sample_id, params)
        wos = WorkOrderSystem(work_order)
    else:
        # Sample parameters
        gen.sampler = gen.sampler  # Use default sampler from config
        params = gen.sampler.sample()
        param_sources['pvc'] = 'SAMPLED'
        param_sources['moisture'] = 'SAMPLED'
        work_order = WorkOrder.from_sampled_params(sample_id, params)
        wos = WorkOrderSystem(work_order)

    # Track seed source
    if seed is not None:
        param_sources['base_seed'] = 'CLI_OVERRIDE'
    else:
        param_sources['base_seed'] = 'DEFAULT'

    # Run production line
    pipeline = gen.pipeline
    checkpoint = pipeline.run(wos)

    # Validate
    validation_errors = checkpoint.validate_all()
    if validation_errors:
        print(f"[!] Validation warnings: {len(validation_errors)} issue(s)")
        for err in validation_errors[:3]:
            print(f"  - {err}")
    else:
        print(f"[OK] Geometry validation passed")

    # Write .in file with config embedded
    from src.file_writer import GPRMaxFileWriter

    written_path = GPRMaxFileWriter.save_scene_checkpoint(
        checkpoint,
        output_path=str(output_path),
        scenario_type="Sim",
        config=config,  # Embed config for replication
        param_sources=param_sources,  # Track parameter sources
    )

    print(f"[OK] Wrote .in file: {written_path}")

    # Optionally render PNG using the unified visualizer (auto-detects 2D/3D)
    if render:
        try:
            import subprocess
            png_path = output_path.with_suffix('.png')
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/visualization/unified_visualizer.py",
                    str(written_path),
                    "-o", str(png_path),
                    "--geometry",
                    "--no-show",
                    "--dpi", "150",
                ],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )
            if result.returncode == 0:
                print(f"[OK] Rendered visualization: {png_path}")
            else:
                print(f"[WARN] Rendering failed: {result.stderr}")
        except Exception as e:
            print(f"[WARN] Could not render PNG: {e}")

    print(f"\n{'='*70}\n")
    return Path(written_path)


def generate_layers(args) -> int:
    """Generate one arbitrary N-layer .in file.

    The TOML config ([sim]/[source]/[[layer]]/[[command]]) is the source of truth;
    CLI flags (--freq/--domain-x/--dx/--rx-spacing/--seed) override [sim] when given.
    """
    from src.layer_spec import parse_layers, parse_config_file, SceneConfig
    from src.layer_scene_builder import SceneParams, write_scene

    output_path = Path(args.output)
    if not args.layers and not args.layers_file:
        print("[FAIL] layers mode requires --layers \"...\" or --layers-file FILE.toml")
        return 1

    if args.layers_file:
        config = parse_config_file(args.layers_file)
        embed_toml = config.toml_text
    else:
        config = SceneConfig(layers=parse_layers(args.layers))
        embed_toml = ""  # builder generates an effective TOML to embed

    sim, src = config.sim, config.source

    def pick(cli_val, cli_default, key, builtin):
        """Precedence: explicit CLI flag > [sim] table > built-in default."""
        if cli_val is not None and cli_val != cli_default:
            return cli_val, "CLI_OVERRIDE"
        if key in sim:
            return sim[key], "TOML"
        return builtin, "DEFAULT"

    ps: dict[str, str] = {}
    freq, ps["center_freq_hz"] = pick(args.freq, 1.5e9, "freq_hz", 400e6)
    domain_x, ps["domain_x"] = pick(args.domain_x, None, "domain_x", 1.0)
    dx, ps["dx"] = pick(args.dx, None, "dx", None)
    rx_spacing, ps["rx_spacing"] = pick(args.rx_spacing, 0.05, "rx_spacing", 0.0)
    seed, _ = pick(args.seed, None, "seed", None)
    ps["antenna_clearance"] = "TOML" if "antenna_clearance" in sim else "DEFAULT"
    ps["air_buffer"] = "TOML" if "air_buffer" in sim else "DEFAULT"

    params = SceneParams(
        freq_hz=float(freq),
        domain_x=float(domain_x),
        dx=float(dx) if dx is not None else None,
        antenna_clearance=float(sim.get("antenna_clearance", 0.5)),
        air_buffer=float(sim.get("air_buffer", 0.1)),
        rx_spacing=float(rx_spacing),
        title=str(sim.get("title", f"N-layer ({len(config.layers)} layers) {float(freq)/1e6:.0f} MHz")),
        time_window=float(sim["time_window"]) if "time_window" in sim else None,
        seed=int(seed) if seed is not None else None,
        source_waveform=str(src.get("waveform", "ricker")),
        source_amplitude=float(src.get("amplitude", 1.0)),
        source_polarization=str(src.get("polarization", "z")),
    )

    print(f"\n{'='*70}\nN-LAYER MODE: Generate One .in File\n{'='*70}")
    print(f"Output File: {output_path}")
    print(f"Source: {'TOML ' + str(args.layers_file) if args.layers_file else 'inline --layers'}")
    print(f"Frequency: {params.freq_hz/1e6:.0f} MHz   Domain X: {params.domain_x} m   "
          f"Source waveform: {params.source_waveform}")
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

    if args.render:
        try:
            import subprocess
            png_path = output_path.with_suffix(".png")
            result = subprocess.run(
                [sys.executable, "scripts/visualization/unified_visualizer.py",
                 str(written), "-o", str(png_path), "--geometry", "--no-show", "--dpi", "150"],
                capture_output=True, text=True,
                cwd=str(Path(__file__).resolve().parent.parent.parent),
            )
            if result.returncode == 0:
                print(f"[OK] Rendered visualization: {png_path}")
            else:
                print(f"[WARN] Rendering failed: {result.stderr}")
        except Exception as e:
            print(f"[WARN] Could not render PNG: {e}")

    print(f"\n{'='*70}\n")
    return 0


def extract_parameters(source_path: Path) -> dict:
    """Extract generation parameters from an existing .in file.

    Returns dict with keys: pvc, moisture, seed, freq, angular, sides,
                           packing_algo, psd_type, num_rx, rx_spacing
    """
    from src.file_reader import extract_config_from_in_file

    try:
        config_dict = extract_config_from_in_file(str(source_path))

        # Map CONFIG_ keys to command-line parameter names
        params = {
            'pvc': float(config_dict.get('pvc_sampled')) if 'pvc_sampled' in config_dict else None,
            'moisture': float(config_dict.get('moisture_sampled')) if 'moisture_sampled' in config_dict else None,
            'seed': int(config_dict.get('actual_seed')) if 'actual_seed' in config_dict else int(config_dict.get('base_seed')) if 'base_seed' in config_dict else None,
            'freq': float(config_dict.get('center_freq_hz', 1.5e9)),
            'angular': config_dict.get('angular_rocks', False),
            'sides': int(config_dict.get('rock_sides', 6)),
            'packing_algo': config_dict.get('rock_packing_algorithm', 'circlify'),
            'psd_type': config_dict.get('packing_psd_type', 'uniform'),
            'num_rx': int(config_dict.get('num_receivers', 1)),
            'rx_spacing': float(config_dict.get('receiver_spacing', 0.05)),
        }

        return params
    except Exception as e:
        print(f"[FAIL] Failed to extract parameters from {source_path}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Unified .in file generator for GPR simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Batch: 50 files per class, 1.5 GHz
  %(prog)s output/ --mode batch --labels CL MC MF -n 50

  # Batch: 400 MHz angular rocks
  %(prog)s output/ --mode batch --labels CL MC MF F HF -n 1000 \\
    --freq 400e6 --angular --packing-algo circlify

  # Single: Custom PVC with seed (reproducible)
  %(prog)s test.in --mode single --pvc 25 --moisture 0.10 --seed 42

  # Single: 400 MHz, octagonal rocks
  %(prog)s out.in --mode single --freq 400e6 --pvc 50 --angular --sides 8 --render

  # Reproduce from existing file parameters
  %(prog)s copy.in --mode single --params-from original.in

  # Extract and override one parameter
  %(prog)s modified.in --mode single --params-from original.in --pvc 35
        """,
    )

    # Mode selection
    parser.add_argument(
        "--mode",
        choices=["batch", "single"],
        default="batch",
        help="Generation mode: batch (per-class dataset) or single (one file). "
             "An N-layer scene is auto-selected when --layers / --layers-file is given.",
    )

    # Positional argument (interpreted based on mode)
    parser.add_argument(
        "output",
        help="Output directory (batch mode) or file path (single mode)",
    )

    # Batch-specific
    parser.add_argument(
        "--labels",
        nargs="+",
        default=["CL", "MC", "MF", "F"],
        help=f"Fouling classes. Valid: {', '.join(list_all_classes())}",
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=50,
        help="Samples per label (batch mode) or ignored (single mode)",
    )
    parser.add_argument(
        "--start-id",
        type=int,
        default=1000,
        help="Starting ID for filenames (batch mode)",
    )
    parser.add_argument(
        "--moisture-max",
        type=float,
        default=0.15,
        help="Maximum volumetric moisture content (batch mode)",
    )

    # Single-specific
    parser.add_argument(
        "--pvc",
        type=float,
        default=None,
        help="PVC percentage (single mode). If None, sampled randomly",
    )
    parser.add_argument(
        "--moisture",
        type=float,
        default=None,
        help="Moisture fraction (single mode). If None, sampled randomly",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Generate PNG visualization (single mode)",
    )

    # Parameter extraction (for reproducibility)
    parser.add_argument(
        "--params-from",
        type=str,
        default=None,
        help="Extract generation parameters from existing .in file and use them (single mode only)",
    )

    # N-layer mode
    parser.add_argument(
        "--layers",
        type=str,
        default=None,
        help='Inline N-layer spec (bottom->top), e.g. '
             '"subgrade:0.20, formation:0.10, ballast:0.25:packed". '
             'Presence selects the N-layer creator.',
    )
    parser.add_argument(
        "--layers-file",
        type=str,
        default=None,
        help="TOML scene config ([sim]/[source]/[[layer]]/[[command]]). "
             "Presence selects the N-layer creator; overrides --layers.",
    )

    # Common options
    parser.add_argument(
        "--freq",
        type=float,
        default=1.5e9,
        help="Center frequency in Hz (default: 1.5e9 = 1.5 GHz)",
    )
    parser.add_argument(
        "--domain-x",
        type=float,
        default=None,
        help="Override domain width in metres (mbubia default: 4.0m)",
    )
    parser.add_argument(
        "--dx",
        type=float,
        default=None,
        help="Override grid resolution in metres (mbubia default: 4mm; use 2mm for finer detail)",
    )
    parser.add_argument(
        "--angular",
        action="store_true",
        help="Use polygonal rocks instead of cylinders",
    )
    parser.add_argument(
        "--sides",
        type=int,
        default=6,
        help="Polygon sides for angular rocks (default: 6 = hexagon)",
    )
    parser.add_argument(
        "--packing-algo",
        type=str,
        default="circlify",
        help="Rock packing algorithm (circlify, front_chain, rsa, shang_chu, etc.)",
    )
    parser.add_argument(
        "--psd",
        type=str,
        default="uniform",
        help="Particle size distribution (uniform, en13450, fuller)",
    )
    parser.add_argument(
        "--num-rx",
        type=int,
        default=1,
        help="Number of receivers (default: 1 = single offset)",
    )
    parser.add_argument(
        "--rx-spacing",
        type=float,
        default=0.05,
        help="RX spacing in meters (default: 0.05 = 5cm)",
    )
    parser.add_argument(
        "--randomize-rocks",
        action="store_true",
        help="Assign a random material to each rock (useful to visualize individual rocks and voxelization loss)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (batch mode)",
    )

    args = parser.parse_args()

    # An N-layer scene is auto-detected from --layers / --layers-file — no mode needed.
    if args.layers or args.layers_file:
        return generate_layers(args)

    if args.mode == "batch":
        output_dir = Path(args.output)
        count = generate_batch(
            output_dir=output_dir,
            labels=args.labels,
            n_per_label=args.num,
            freq_hz=args.freq,
            angular=args.angular,
            sides=args.sides,
            packing_algo=args.packing_algo,
            psd_type=args.psd,
            num_rx=args.num_rx,
            rx_spacing=args.rx_spacing,
            moisture_max=args.moisture_max,
            start_id=args.start_id,
            seed=args.seed,
        )
        return 0

    elif args.mode == "single":
        output_path = Path(args.output)

        # Extract parameters from existing file if --params-from is provided
        if args.params_from:
            print(f"\n{'='*70}")
            print("EXTRACTING PARAMETERS FROM EXISTING FILE")
            print(f"{'='*70}")
            print(f"Source File: {args.params_from}\n")

            params = extract_parameters(Path(args.params_from))
            if params is None:
                return 1

            print("Extracted parameters:")
            for k, v in params.items():
                if v is not None:
                    print(f"  {k}: {v}")
            print()

            # Use extracted parameters (can be overridden by explicit command-line args)
            freq_hz = args.freq if args.freq != 1.5e9 else params.get('freq', 1.5e9)
            pvc = args.pvc if args.pvc is not None else params.get('pvc')
            moisture = args.moisture if args.moisture is not None else params.get('moisture')
            angular = args.angular if args.angular else params.get('angular', False)
            sides = args.sides if args.sides != 6 else params.get('sides', 6)
            packing_algo = args.packing_algo if args.packing_algo != 'circlify' else params.get('packing_algo', 'circlify')
            psd_type = args.psd if args.psd != 'uniform' else params.get('psd_type', 'uniform')
            num_rx = args.num_rx if args.num_rx != 1 else params.get('num_rx', 1)
            rx_spacing = args.rx_spacing if args.rx_spacing != 0.05 else params.get('rx_spacing', 0.05)
            seed = args.seed if args.seed is not None else params.get('seed')
        else:
            freq_hz = args.freq
            pvc = args.pvc
            moisture = args.moisture
            angular = args.angular
            sides = args.sides
            packing_algo = args.packing_algo
            psd_type = args.psd
            num_rx = args.num_rx
            rx_spacing = args.rx_spacing
            seed = args.seed

        generate_single(
            output_path=output_path,
            freq_hz=freq_hz,
            pvc=pvc,
            moisture=moisture,
            angular=angular,
            sides=sides,
            packing_algo=packing_algo,
            psd_type=psd_type,
            num_rx=num_rx,
            domain_x=args.domain_x,
            dx=args.dx,
            rx_spacing=rx_spacing,
            render=args.render,
            seed=seed,
            randomize_rock_materials=args.randomize_rocks,
        )
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
