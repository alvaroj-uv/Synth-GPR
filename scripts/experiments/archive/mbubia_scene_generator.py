#!/usr/bin/env python3
"""
Mbubia-Style Scene Generator

Generate synthetic GPR scenes matching Mbubia et al. 2026 methodology.
Fully parameterized - supports different fouling levels, frequencies, and configurations.

Reference: Mbubia et al. (2026) - GPR and AI for railway ballast assessment
"""

import argparse
from pathlib import Path
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import GeneratorConfig
from src.production_line import ProductionLine
from src.work_order import WorkOrder, WorkOrderSystem
from src.domain import SceneParameters
from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.scene import parse_in_file
from scripts.visualization.mbubia_visualizer import visualize_monostatic_scene


@dataclass
class MbubiaConfig:
    """Mbubia et al. 2026 study parameters"""

    # Frequency (Table 5: Central source frequency)
    frequency: float = 1.4e9  # 1.4 GHz (NOT 400 MHz!)

    # Domain dimensions
    # Mbubia study: 4.0 m width, 0.80 m height (structures only)
    # Synth-GPR needs: 1.65 m height (antenna clearance + air buffer)
    domain_x: float = 4.0  # 4.0 m width (Mbubia)
    domain_y: float = 1.7  # 1.7 m height (infrastructure requirement, air buffer included)

    # Antenna (Table 5)
    antenna_mode: str = "monostatic"  # Real railway standard (Mbubia)
    antenna_height: float = 0.3  # 0.3 m above surface

    # Signal acquisition (Table 5)
    signal_time: float = 20e-9  # 20 ns

    # Layer parameters (Table 2: First layer thickness 0.13–0.79 m)
    ballast_thickness: float = 0.35  # Typical middle value
    ballast_grain_size: float = 0.050  # 36-60mm, use ~50mm

    # Fouling level (Table 3: Rb-f %)
    rbf_class: str = "fouled"  # "clean", "fouled", "highly_fouled"

    # PVC equivalent to Rb-f
    pvc_map = {
        "clean": 2.0,              # Rb-f < 2%
        "fouled": 15.0,            # Rb-f 2-18% (midpoint ~10%)
        "highly_fouled": 55.0,     # Rb-f >= 55%
    }


def validate_config(config: MbubiaConfig) -> None:
    """Validate Mbubia parameters"""
    errors = []

    if config.frequency != 1.4e9:
        print(f"⚠️  Frequency is {config.frequency/1e9:.1f}GHz, Mbubia uses 1.4GHz")

    if config.antenna_mode != "monostatic":
        errors.append(f"Antenna mode must be 'monostatic' (Mbubia standard), got '{config.antenna_mode}'")

    if config.rbf_class not in config.pvc_map:
        errors.append(f"Fouling class must be one of {list(config.pvc_map.keys())}, got '{config.rbf_class}'")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        sys.exit(1)


def generate_mbubia_scene(
    output_dir: Path,
    mbubia_cfg: MbubiaConfig,
    scene_id: str = "mbubia",
    verbose: bool = True,
) -> tuple:
    """
    Generate a Mbubia-style scene

    Args:
        output_dir: Directory to save outputs
        mbubia_cfg: Mbubia configuration
        scene_id: Scene identifier
        verbose: Print detailed progress

    Returns:
        (generator_config, scene, parsed_scene) tuple
    """

    if verbose:
        print("=" * 80)
        print(f"GENERATING MBUBIA-STYLE SCENE: {scene_id}")
        print("=" * 80)

    validate_config(mbubia_cfg)

    # 1. Create generator config with monostatic
    if verbose:
        print(f"\n1. Creating Mbubia config...")
        print(f"   Frequency: {mbubia_cfg.frequency/1e9:.1f} GHz (Mbubia standard)")
        print(f"   Antenna mode: {mbubia_cfg.antenna_mode} (Mbubia standard)")
        print(f"   Domain: {mbubia_cfg.domain_x:.1f}m × {mbubia_cfg.domain_y:.2f}m")
        print(f"     (Width from Mbubia, height adjusted for antenna clearance)")
        print(f"   Fouling class: {mbubia_cfg.rbf_class} (Rb-f → PVC ≈ {mbubia_cfg.pvc_map[mbubia_cfg.rbf_class]:.1f}%)")

    gen_config = GeneratorConfig(
        antenna_mode=mbubia_cfg.antenna_mode,
        domain_x=mbubia_cfg.domain_x,
        domain_y=mbubia_cfg.domain_y,
    )

    # 2. Create scene parameters
    pvc = mbubia_cfg.pvc_map[mbubia_cfg.rbf_class]
    scene_params = SceneParameters(
        pvc=pvc,
        moisture=0.05,  # Typical
        ballast_thickness=mbubia_cfg.ballast_thickness,
    )

    if verbose:
        print(f"\n2. Creating scene with PVC={pvc:.1f}%...")

    # 3. Run pipeline
    work_order = WorkOrderSystem(WorkOrder(
        id=scene_id,
        typed_params=scene_params
    ))
    pipeline = ProductionLine(gen_config)
    scene = pipeline.run(work_order)

    if verbose:
        print(f"   ✓ Scene generated")
        print(f"     • Antenna mode: {scene.config.antenna_mode}")
        print(f"     • TX @ X = {gen_config.tx_x:.3f}m")
        print(f"     • RX @ X = {gen_config.tx_x:.3f}m (co-located)")

    # 4. Parse for visualization (if .in file exists)
    parsed_scene = None
    in_file = output_dir / f"{scene_id}.in"
    if in_file.exists():
        try:
            from src.file_writer import GPRMaxFileWriter
            writer = GPRMaxFileWriter()
            writer.write_to_file(scene, str(in_file))
            parsed_scene = parse_in_file(in_file)
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Could not parse .in file: {e}")

    return gen_config, scene, parsed_scene


def visualize_mbubia_scene(
    parsed_scene,
    config: MbubiaConfig,
    output_dir: Path,
    scene_id: str,
) -> None:
    """Generate publication-quality visualizations"""

    if parsed_scene is None:
        return

    print(f"\n3. Generating visualizations...")

    # Publication PNG (300 DPI)
    png_path = output_dir / f"{scene_id}_mbubia_300dpi.png"
    try:
        in_path = output_dir / f"{scene_id}.in"
        if in_path.exists():
            visualize_monostatic_scene(in_path, png_path, fouling_label=config.rbf_class)
            print(f"   PNG: {png_path.name} ({png_path.stat().st_size / 1024:.1f} KB)")
    except Exception as e:
        print(f"   PNG generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mbubia-style GPR scenes (parameterized)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate clean ballast scene
  python mbubia_scene_generator.py --fouling clean --output results/mbubia

  # Generate highly fouled scene with custom domain
  python mbubia_scene_generator.py --fouling highly_fouled --domain 3.0 --output results/

  # Generate fouled ballast (default)
  python mbubia_scene_generator.py

Note: Frequency is always 1.4 GHz and antenna_mode is always monostatic (Mbubia standard)
        """)

    parser.add_argument(
        "--fouling",
        choices=["clean", "fouled", "highly_fouled"],
        default="fouled",
        help="Fouling class (default: fouled)"
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=1.4e9,
        help="Central frequency in Hz (default: 1.4e9 = 1.4 GHz)"
    )
    parser.add_argument(
        "--domain",
        type=float,
        default=4.0,
        help="Domain width in meters (default: 4.0 m)"
    )
    parser.add_argument(
        "--ballast-thickness",
        type=float,
        default=0.35,
        help="Ballast thickness in meters (default: 0.35 m)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mbubia"),
        help="Output directory (default: results/mbubia)"
    )
    parser.add_argument(
        "--scene-id",
        default="mbubia_scene",
        help="Scene identifier (default: mbubia_scene)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Verbose output (default: true)"
    )

    args = parser.parse_args()

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Create Mbubia config
    mbubia_cfg = MbubiaConfig(
        frequency=args.frequency,
        domain_x=args.domain,
        rbf_class=args.fouling,
        ballast_thickness=args.ballast_thickness,
    )

    # Generate scene
    gen_config, scene, parsed_scene = generate_mbubia_scene(
        args.output,
        mbubia_cfg,
        scene_id=args.scene_id,
        verbose=args.verbose
    )

    # Visualize
    if parsed_scene:
        visualize_mbubia_scene(parsed_scene, mbubia_cfg, args.output, args.scene_id)

    print("\n" + "=" * 80)
    print(f"✅ MBUBIA SCENE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files in: {args.output.absolute()}")
    print(f"Scene configuration:")
    print(f"  • Fouling: {args.fouling}")
    print(f"  • Frequency: {args.frequency/1e9:.1f} GHz")
    print(f"  • Antenna mode: monostatic (Mbubia standard)")
    print(f"  • Domain: {args.domain:.1f}m × {mbubia_cfg.domain_y:.2f}m")
    print(f"\nReference: Mbubia et al. (2026)")
    print(f"DOI: 10.1016/j.treng.2025.100415")


if __name__ == "__main__":
    main()
