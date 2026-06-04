#!/usr/bin/env python3
"""
Generate 3D gprMax input files using GPRMaxFileWriter and SphereCommand.

Phase 1 POC: 1000 samples (200 per class), 1.5 x 0.4 x 0.4 m domain, dx=0.01 m
- Spheres confined to ballast zone (y=0.15-0.40)
- Fouling via #box overlay (overwritten by spheres inside rocks)
- Metadata headers for build_parquet_merged.py compatibility

Output: input_files_3d_poc/s_00000.in ... s_00999.in
"""

import sys
from pathlib import Path
from datetime import datetime

import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.gpr_commands import (
    Header, DomainCommand, DxDyDzCommand, TimeWindowCommand,
    MaterialCommand, BoxCommand, SphereCommand,
    WaveformCommand, HertzianDipoleCommand, RxCommand,
    AbsorbingBCCommand, GeometryViewCommand
)
from src.file_writer import GPRMaxFileWriter
from src.physics import fmt, get_fdtd_recommendations, fi_from_fouling_height
from src.version_utils import get_git_revision_hash
from datetime import date

# Configuration
OUTPUT_DIR = Path("input_files_3d_poc")

# 400 MHz frequency-dependent sizing (IEEE 2025 guidelines)
CENTER_FREQ_HZ = 400e6
FDTD_RECS = get_fdtd_recommendations(CENTER_FREQ_HZ)

# Domain dimensions from FDTD recommendations
DOMAIN_X = FDTD_RECS['domain_x']  # 2.248 m (1.5 * lambda_max)
DX = FDTD_RECS['dx']  # 0.0132 m (lambda_min / 10)

# Vertical domain: subgrade + formation + ballast + antenna clearance + air buffer
SUBGRADE_THICKNESS = 0.20
FORMATION_THICKNESS = 0.10
BALLAST_THICKNESS = 0.25
ANTENNA_CLEARANCE = 0.50  # Space above ballast for antenna
AIR_BUFFER = 0.10

DOMAIN_Y = SUBGRADE_THICKNESS + FORMATION_THICKNESS + BALLAST_THICKNESS + ANTENNA_CLEARANCE + AIR_BUFFER
DOMAIN_Z = 0.4  # Fixed transverse dimension (GPR survey direction perpendicular to X)

BALLAST_Y_MIN = SUBGRADE_THICKNESS + FORMATION_THICKNESS
BALLAST_Y_MAX = BALLAST_Y_MIN + BALLAST_THICKNESS

NUM_SAMPLES = 1000
SAMPLES_PER_CLASS = NUM_SAMPLES // 5

ROCKS_PER_SAMPLE = 150  # Increased from 80 for denser packing
RADIUS_DIST = {'mean': 0.020, 'std': 0.003}

# Fouling heights as offsets from ballast_bottom
# Original 2D values (0.16-0.34) were absolute positions from y=0 in 2D reference
# Here they represent penetration depth into ballast layer
# Interpretation: fouling fills ballast from bottom up to these offsets
FOULING_HEIGHTS = {
    'C': BALLAST_Y_MIN + 0.02,   # Clean: minimal fouling (2cm into ballast)
    'MC': BALLAST_Y_MIN + 0.05,  # Moderately Clean: 5cm
    'MF': BALLAST_Y_MIN + 0.08,  # Moderately Fouled: 8cm
    'F': BALLAST_Y_MIN + 0.15,   # Fouled: 15cm
    'HF': BALLAST_Y_MIN + 0.20,  # Highly Fouled: 20cm (most of ballast)
}

LAB_FI_VALUES = {
    'C': 5.0, 'MC': 15.0, 'MF': 28.0, 'F': 50.0, 'HF': 80.0,
}

def pack_spheres_grid_search(target_count, radius_dist, max_retries=100):
    """Grid-accelerated sphere packing in ballast zone only."""
    spheres = []
    grid = {}
    grid_cells = 10
    cell_size_x = DOMAIN_X / grid_cells
    cell_size_y = (BALLAST_Y_MAX - BALLAST_Y_MIN) / grid_cells
    cell_size_z = DOMAIN_Z / grid_cells

    def get_cell_coords(x, y, z):
        ix = int(x / cell_size_x)
        iy = int((y - BALLAST_Y_MIN) / cell_size_y)
        iz = int(z / cell_size_z)
        return (ix, iy, iz)

    def get_nearby_cells(ix, iy, iz, radius):
        r_cells = int(radius / min(cell_size_x, cell_size_y, cell_size_z)) + 1
        cells = []
        for dx in range(-r_cells, r_cells + 1):
            for dy in range(-r_cells, r_cells + 1):
                for dz in range(-r_cells, r_cells + 1):
                    cells.append((ix + dx, iy + dy, iz + dz))
        return cells

    for _ in range(target_count):
        for _ in range(max_retries):
            radius = np.random.normal(radius_dist['mean'], radius_dist['std'])
            radius = np.clip(radius, 0.015, 0.035)

            x = np.random.uniform(radius, DOMAIN_X - radius)
            y = np.random.uniform(BALLAST_Y_MIN + radius, BALLAST_Y_MAX - radius)
            z = np.random.uniform(radius, DOMAIN_Z - radius)

            cell = get_cell_coords(x, y, z)
            nearby = get_nearby_cells(cell[0], cell[1], cell[2], radius)

            overlap = False
            for nearby_cell in nearby:
                if nearby_cell in grid:
                    for (sx, sy, sz, sr) in grid[nearby_cell]:
                        dist = np.sqrt((x - sx)**2 + (y - sy)**2 + (z - sz)**2)
                        if dist < radius + sr:
                            overlap = True
                            break
                if overlap:
                    break

            if not overlap:
                spheres.append((x, y, z, radius))
                if cell not in grid:
                    grid[cell] = []
                grid[cell].append((x, y, z, radius))
                break

    return spheres

def generate_metadata_for_class(class_name, sample_id):
    """Generate realistic metadata for a given fouling class."""
    rng = np.random.RandomState(sample_id)

    lab_fi = LAB_FI_VALUES[class_name]
    pvc = lab_fi * 0.8
    moisture = 15.0 + rng.uniform(-5, 5)
    achieved_density = 1.5 + rng.uniform(-0.1, 0.1)
    porosity = 0.35 + rng.uniform(-0.05, 0.05)

    rock_frac = (100 - pvc) / 100.0
    fouling_frac = pvc / 100.0

    lab_fi_local = lab_fi * 0.95
    lab_fr = 0.5 + rng.uniform(-0.2, 0.2)
    lab_er_bulk_leng = 5.0 + rng.uniform(-0.5, 0.5)
    lab_bulk_eps = 5.0 + rng.uniform(-0.5, 0.5)
    lab_alpha_400mhz = 0.1 + rng.uniform(-0.05, 0.05)
    lab_alpha_2ghz = 0.3 + rng.uniform(-0.1, 0.1)
    lab_surface_r = 0.6 + rng.uniform(-0.1, 0.1)
    lab_ldcp_fh = lab_fi
    # Rojas-Vivanco 2025 quadratic (matches real labeling), not linear FH/1.5.
    lab_ldcp_fi_est = round(fi_from_fouling_height(lab_ldcp_fh), 2)
    lab_ldcp_qs_mean = 0.3 + rng.uniform(-0.1, 0.1)
    lab_clean_ballast_mm = 40.0 + rng.uniform(-5, 5)

    fouling_height = FOULING_HEIGHTS[class_name]
    ballast_top_y = BALLAST_Y_MIN
    ballast_bottom_y = BALLAST_Y_MAX
    mc_y_max = fouling_height
    mc_y_min = BALLAST_Y_MIN
    mc_y_local_max = fouling_height
    ldcp_x = 0.75 + rng.uniform(-0.1, 0.1)

    return {
        'Lab_Class': class_name,
        'Lab_FI': lab_fi,
        'Lab_FI_local': lab_fi_local,
        'Lab_FR': lab_fr,
        'pvc': pvc,
        'moisture': moisture,
        'achieved_density': achieved_density,
        'porosity': porosity,
        'Lab_er_bulk_leng': lab_er_bulk_leng,
        'Lab_bulk_eps': lab_bulk_eps,
        'Lab_alpha_400MHz_npm': lab_alpha_400mhz,
        'Lab_alpha_2GHz_npm': lab_alpha_2ghz,
        'Lab_surface_R': lab_surface_r,
        'Lab_LDCP_FH': lab_ldcp_fh,
        'Lab_LDCP_FI_est': lab_ldcp_fi_est,
        'Lab_LDCP_qs_mean': lab_ldcp_qs_mean,
        'Lab_clean_ballast_mm': lab_clean_ballast_mm,
        'mc_rock_fraction': rock_frac,
        'mc_fouling_fraction': fouling_frac,
        'mc_subgrade_fraction': 0.1,
        'mc_formation_fraction': 0.05,
        'mc_void_fraction': porosity,
        'mc_pvc_measured': pvc,
        'ballast_top_y': ballast_top_y,
        'ballast_bottom_y': ballast_bottom_y,
        'mc_y_max': mc_y_max,
        'mc_y_min': mc_y_min,
        'mc_y_local_max': mc_y_local_max,
        'ldcp_x': ldcp_x,
    }

def build_gprmax_commands(sample_id, spheres, class_name, metadata):
    """Build GPRCommand list for a 3D sample with proper formatting."""
    fouling_height = FOULING_HEIGHTS[class_name]

    commands = []

    # Header separator and metadata
    commands.append(Header("=" * 60))
    commands.append(Header("Generated 3D gprMax Input File"))
    commands.append(Header("Scenario: 3D_POC"))
    commands.append(Header(f"Date: {date.today().isoformat()}"))

    # Git version
    git_hash = get_git_revision_hash()
    if git_hash:
        commands.append(Header(f"Git Version: {git_hash}"))

    commands.append(Header(f"Base Seed: {sample_id}"))

    # Metadata fields (sorted for consistency with 2D)
    for key in sorted(metadata.keys()):
        val = metadata[key]
        val_str = fmt(val) if isinstance(val, float) else str(val)
        commands.append(Header(f"{key}: {val_str}"))

    commands.append(Header(f"source: 3d_poc"))
    commands.append(Header(f"Rocks: {len(spheres)}"))
    commands.append(Header("=" * 60))

    # Domain and grid
    commands.append(Header("Domain Configuration"))
    commands.append(DomainCommand(DOMAIN_X, DOMAIN_Y, DOMAIN_Z))
    commands.append(DxDyDzCommand(DX, DX, DX))

    # Time window: 10 * domain_y / c where c ~= 0.1 m/ns in medium
    time_window = 10 * DOMAIN_Y / 0.1e-9
    commands.append(TimeWindowCommand(time_window))

    # PML sizing: 10% of smallest domain (following 2D pattern with 10 cells at 0.0132m spacing)
    pml_cells = max(10, int(0.1 * DOMAIN_Z / DX))  # At least 10 cells
    commands.append(AbsorbingBCCommand(cells=pml_cells, z_cells=pml_cells))

    # Waveform and antenna
    # Antenna positioned above ballast with IEEE 2025-recommended clearance
    antenna_y = BALLAST_Y_MAX + ANTENNA_CLEARANCE / 2.0  # Middle of antenna clearance zone
    antenna_x = DOMAIN_X / 2.0  # Middle of domain
    antenna_z = DOMAIN_Z / 2.0  # Middle of domain
    rx_x = antenna_x + 0.15  # RX offset 0.15m from TX

    commands.append(Header("Sources and Receivers"))
    commands.append(WaveformCommand('ricker', 1.0, CENTER_FREQ_HZ, 'ricker_src'))
    commands.append(HertzianDipoleCommand('z', antenna_x, antenna_y, antenna_z, 'ricker_src'))
    commands.append(RxCommand(rx_x, antenna_y, antenna_z))

    # Materials
    commands.append(Header("Materials"))
    commands.append(MaterialCommand(eps=10.0, sigma=0.02, mu=1.0, mag_loss=0.0, identifier='subgrade'))
    commands.append(MaterialCommand(eps=10.0, sigma=0.03, mu=1.0, mag_loss=0.0, identifier='formation'))
    commands.append(MaterialCommand(eps=5.0, sigma=0.001, mu=1.0, mag_loss=0.0, identifier='bal_rock'))
    commands.append(MaterialCommand(eps=4.7605, sigma=0.0076842, mu=1.0, mag_loss=0.0, identifier='bal_foul_granular'))

    # Geometry
    commands.append(Header("Geometry"))

    # Layer boxes
    subgrade_top = SUBGRADE_THICKNESS
    formation_top = subgrade_top + FORMATION_THICKNESS

    commands.append(BoxCommand(0.0, 0.0, 0.0, DOMAIN_X, subgrade_top, DOMAIN_Z, 'free_space'))
    commands.append(BoxCommand(0.0, 0.0, 0.0, DOMAIN_X, subgrade_top, DOMAIN_Z, 'subgrade'))
    commands.append(BoxCommand(0.0, subgrade_top, 0.0, DOMAIN_X, formation_top, DOMAIN_Z, 'formation'))

    # Fouling box (placed before spheres, overwritten by spheres)
    if fouling_height > BALLAST_Y_MIN + 0.01:
        commands.append(BoxCommand(0.0, BALLAST_Y_MIN, 0.0, DOMAIN_X, fouling_height, DOMAIN_Z, 'bal_foul_granular'))

    # Spheres (placed after fouling box, overwrite it)
    for x, y, z, r in spheres:
        commands.append(SphereCommand(x, y, z, r, 'bal_rock'))

    # Geometry view (commented out by default)
    commands.append(GeometryViewCommand(
        x1=0.0, y1=0.0, z1=0.0,
        x2=DOMAIN_X, y2=DOMAIN_Y, z2=DOMAIN_Z,
        dx=DX, dy=DX, dz=DX,
        filename=f"s_{sample_id:05d}_geo",
        type_char='n',
        commented=True
    ))

    return commands

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 3D POC: Generating {NUM_SAMPLES} input files")
    print(f"  Frequency: {CENTER_FREQ_HZ/1e6:.0f} MHz (IEEE 2025 compliant)")
    print(f"  Domain: {DOMAIN_X:.3f} x {DOMAIN_Y:.3f} x {DOMAIN_Z:.3f} m")
    print(f"  Ballast zone: y=[{BALLAST_Y_MIN:.3f}, {BALLAST_Y_MAX:.3f}] m")
    print(f"  Grid spacing: {DX:.4f} m ({DX*1000:.2f} mm)")
    print(f"  Antenna clearance: {ANTENNA_CLEARANCE} m above ballast")
    print(f"  Samples per class: {SAMPLES_PER_CLASS}")

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    classes = ['C', 'MC', 'MF', 'F', 'HF']
    np.random.seed(42)

    pbar = tqdm(total=NUM_SAMPLES, desc="Generating inputs")

    for sample_id in range(NUM_SAMPLES):
        # Class assignment (grouped: 0-199=C, 200-399=MC, etc.)
        class_idx = sample_id // SAMPLES_PER_CLASS
        class_name = classes[class_idx]

        # Generate metadata
        metadata = generate_metadata_for_class(class_name, sample_id)

        # Generate sphere packing in ballast zone
        spheres = pack_spheres_grid_search(ROCKS_PER_SAMPLE, RADIUS_DIST)

        # Build GPRCommand list
        commands = build_gprmax_commands(sample_id, spheres, class_name, metadata)

        # Render commands in order (no sorting to preserve header placement)
        lines = []
        for cmd in commands:
            lines.append(cmd.render())
        content = '\n'.join(lines)

        # Write to file
        output_file = OUTPUT_DIR / f"s_{sample_id:05d}.in"
        with open(output_file, 'w') as f:
            f.write(content)

        pbar.update(1)

    pbar.close()

    print(f"\n[OK] Generated {NUM_SAMPLES} input files in {OUTPUT_DIR}")
    print(f"  Class distribution: 200 per class (C, MC, MF, F, HF)")
    print(f"  Fouling heights: C={FOULING_HEIGHTS['C']}m, MC={FOULING_HEIGHTS['MC']}m, MF={FOULING_HEIGHTS['MF']}m, F={FOULING_HEIGHTS['F']}m, HF={FOULING_HEIGHTS['HF']}m")
    print(f"  Rocks per sample: {ROCKS_PER_SAMPLE}")
    print(f"  IEEE 2025 compliant for 400 MHz")
    print(f"  Ready for gprMax 3D FDTD simulation")

if __name__ == "__main__":
    main()
