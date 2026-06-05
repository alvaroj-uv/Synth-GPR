#!/usr/bin/env python3
"""
Convert checkpoint to .in file format
Uses your standard .in structure
"""

import pickle
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def checkpoint_to_in(checkpoint_path: Path, output_in: Path = None):
    """
    Load checkpoint and convert to .in file format
    """

    if not checkpoint_path.exists():
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        sys.exit(1)

    if output_in is None:
        output_in = checkpoint_path.parent / f"{checkpoint_path.stem}.in"

    output_in.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading checkpoint: {checkpoint_path.name}")
    with open(checkpoint_path, 'rb') as f:
        checkpoint = pickle.load(f)

    print(f"✓ Loaded")

    # Build .in file content from checkpoint
    lines = []

    # Header
    lines.append("## ============================================================")
    lines.append("## Generated gprMax Input File (from Mbubia pipeline)")
    lines.append("## Antenna: Monostatic (TX/RX co-located)")
    lines.append("## Frequency: 1.4 GHz (Mbubia standard)")
    lines.append("## ============================================================")

    # Add metadata from checkpoint
    if hasattr(checkpoint, 'metadata'):
        for key, value in checkpoint.metadata.items():
            lines.append(f"## {key}: {value}")

    lines.append("")

    # Add configuration as comments
    if hasattr(checkpoint, 'config'):
        config = checkpoint.config
        lines.append("## CONFIGURATION")
        lines.append(f"## antenna_mode: {config.antenna_mode}")
        lines.append(f"## domain_x: {config.domain_x}")
        lines.append(f"## domain_y: {config.domain_y}")
        lines.append(f"## tx_x: {config.tx_x}")
        lines.append(f"## rx_x: {config.rx_x}")
        lines.append("")

    # Add gprMax commands from checkpoint (use .render() for proper syntax)
    if hasattr(checkpoint, 'domain_cmd') and checkpoint.domain_cmd:
        lines.append(checkpoint.domain_cmd.render())

    if hasattr(checkpoint, 'dx_dy_dz_cmd') and checkpoint.dx_dy_dz_cmd:
        lines.append(checkpoint.dx_dy_dz_cmd.render())

    if hasattr(checkpoint, 'time_window_cmd') and checkpoint.time_window_cmd:
        lines.append(checkpoint.time_window_cmd.render())

    lines.append("")
    lines.append("## MATERIALS AND GEOMETRY")
    lines.append("")

    if hasattr(checkpoint, 'materials'):
        for mat in checkpoint.materials:
            lines.append(mat.render())

    if hasattr(checkpoint, 'geometry'):
        for geom in checkpoint.geometry:
            lines.append(geom.render())

    lines.append("")
    lines.append("## ANTENNA CONFIGURATION")
    lines.append("")

    if hasattr(checkpoint, 'sources'):
        for src in checkpoint.sources:
            lines.append(src.render())

    if hasattr(checkpoint, 'receivers'):
        for rx in checkpoint.receivers:
            lines.append(rx.render())

    lines.append("")
    lines.append("## SIMULATION")
    lines.append("#run_simulation")
    lines.append("")

    # Write file
    content = '\n'.join(lines)
    with open(output_in, 'w') as f:
        f.write(content)

    size_kb = output_in.stat().st_size / 1024
    print(f"✓ Written: {output_in.name} ({size_kb:.1f} KB)")

    return output_in


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert checkpoint to .in file"
    )

    parser.add_argument(
        "checkpoint",
        type=Path,
        help="Checkpoint file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output .in file"
    )

    args = parser.parse_args()

    checkpoint_to_in(args.checkpoint, args.output)

    print()
    print("="*70)
    print("✅ CONVERSION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
