#!/usr/bin/env python3
"""Generate 5000 angular-rocks 400 MHz GPR .in files, 1000 per fouling class."""

import argparse
import sys
from pathlib import Path

# Add repository root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import GeneratorConfig
from src.dataset_generator import DatasetGenerator

FOULING_LABELS = ['CL', 'MC', 'MF', 'F', 'HF']

DEFAULT_OUTPUT_DIR = Path('output') / 'angular_rocks_400MHz_5class'
DEFAULT_SAMPLES_PER_LABEL = 1000
DEFAULT_START_ID = 0
DEFAULT_CENTER_FREQ = 4e8


def build_base_config(center_freq: float, base_seed: int | None = None) -> GeneratorConfig:
    """Create the base generator configuration for angular rocks at 400 MHz."""
    cfg = GeneratorConfig.create_physically_perfect(
        center_freq_hz=center_freq,
        granular_mode=True,
        angular_rocks=True,
        base_seed=base_seed,
        min_ballast_thickness=0.25,
        max_ballast_thickness=0.45,
        moisture_min=0.0,
        moisture_max=0.20,
    )
    return cfg


def generate_angular_rocks_dataset(
    output_dir: Path,
    labels: list[str],
    samples_per_label: int,
    start_id: int,
    center_freq: float,
    base_seed: int | None = None,
) -> int:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config = build_base_config(center_freq=center_freq, base_seed=base_seed)
    generator = DatasetGenerator(config)

    current_id = start_id
    total_files = 0

    print(f"Generating angular rocks dataset to: {output_dir}")
    print(f"Center frequency: {center_freq / 1e6:.0f} MHz")
    print(f"Labels: {labels}")
    print(f"Samples per label: {samples_per_label}")
    print(f"Start ID: {start_id}")

    for label in labels:
        label_upper = label.upper()
        print(f"\n--- Generating {label_upper} ({samples_per_label} samples) ---")

        if label_upper not in ('CL', 'MC', 'MF', 'F', 'HF'):
            print(f"Skipping unknown label: {label_upper}")
            continue

        pmin, pmax = {
            'CL': (0.0, 5.0),
            'MC': (5.0, 20.0),
            'MF': (20.0, 40.0),
            'F':  (40.0, 60.0),
            'HF': (60.0, 100.0),
        }[label_upper]

        cfg = GeneratorConfig(
            **{**config.__dict__, 'pvc_min': pmin, 'pvc_max': pmax, 'base_seed': base_seed or current_id}
        )
        label_generator = DatasetGenerator(cfg)

        files, metadata = label_generator.generate_samples(
            output_dir=output_dir,
            n_samples=samples_per_label,
            start_id=current_id,
        )

        count = len(files)
        total_files += count
        current_id += count
        print(f"Generated {count} files for {label_upper}. Next start ID: {current_id}")

    print(f"\nFinished generating {total_files} samples.")
    return total_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate 5000 angular-rocks 400 MHz GPR .in files, 1000 per fouling class.'
    )
    parser.add_argument(
        '-o', '--output', default=str(DEFAULT_OUTPUT_DIR),
        help='Output directory for generated .in files.'
    )
    parser.add_argument(
        '-n', '--num', type=int, default=DEFAULT_SAMPLES_PER_LABEL,
        help='Number of samples per fouling label.'
    )
    parser.add_argument(
        '--start-id', type=int, default=DEFAULT_START_ID,
        help='Starting sample ID for file numbering.'
    )
    parser.add_argument(
        '--center-freq', type=float, default=DEFAULT_CENTER_FREQ,
        help='Center frequency in Hz (default: 4e8).'
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help='Base RNG seed for repeatability.'
    )
    parser.add_argument(
        '--labels', nargs='+', default=FOULING_LABELS,
        help='Fouling labels to generate (default: CL MC MF F HF).'
    )
    args = parser.parse_args()

    generate_angular_rocks_dataset(
        output_dir=Path(args.output),
        labels=args.labels,
        samples_per_label=args.num,
        start_id=args.start_id,
        center_freq=args.center_freq,
        base_seed=args.seed,
    )
