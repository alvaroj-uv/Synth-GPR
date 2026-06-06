"""
Demo: Circle Packing & Compaction Ideas from GPR-repo

Showcases new utilities adapted from GPR-repo/RSA/Circles:
1. Grading curves (PSD sampling) - from gen_sieve_curve.py
2. Discretized gravity compaction - from circle_Compaction.py
3. CompactionBasedPacking strategy - hybrid RSA + gravity settling

Run this script to visualize different packing approaches and compaction effects.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rock_model import Rock, PackingBounds
from src.grading_curve_utils import (
    pick_rand_grading_curve,
    convert_sieve_curve_to_fractions,
    en13450_bounds,
    fuller_ideal_curve,
    uniform_distribution,
    print_grading_curve,
    SieveBounds
)
from src.circle_compaction_utils import (
    apply_compaction_pattern,
    calculate_void_ratio,
    discretize_domain
)
from src.rock_packing import (
    RSAPacking,
    CompactionBasedPacking,
    GradingCurve,
    PackingBounds as PackBounds
)


def demo_grading_curves():
    """Demonstrate different grading curve approaches."""
    print("\n" + "="*70)
    print("DEMO 1: Grading Curves (PSD Sampling)")
    print("="*70)

    # Example 1: EN 13450 railway ballast specification
    print("\n--- EN 13450 Railway Ballast (31.5/63 fraction) ---")
    bounds = en13450_bounds()
    print(f"Specification bounds: {len(bounds)} sieve sizes")

    # Generate 3 random gradings within the specification
    for i in range(3):
        curve = pick_rand_grading_curve(bounds, alpha=2.0, beta=2.0)
        print(print_grading_curve(curve, label=f"Random Grading #{i+1}"))

        # Convert to fractions for RSA
        fractions = convert_sieve_curve_to_fractions(curve)
        print(f"  -> {len(fractions)} sieve fractions for RSA")
        print(f"     Total retained: {fractions[:, 2].sum():.1f}%\n")

    # Example 2: Fuller ideal curve
    print("\n--- Fuller-Thompson Ideal Curve (max packing density) ---")
    d_max = 0.063  # 63mm max diameter
    fuller = fuller_ideal_curve(d_max, n=0.5, n_points=10)
    print(print_grading_curve(fuller, label="Fuller (n=0.5)"))

    # Example 3: Uniform distribution (baseline)
    print("\n--- Uniform Distribution (baseline) ---")
    uniform = uniform_distribution(0.0224, 0.080, n_points=2)
    print(print_grading_curve(uniform, label="Uniform"))


def demo_rsa_packing():
    """Demonstrate RSA packing with grading curves."""
    print("\n" + "="*70)
    print("DEMO 2: RSA Packing with Grading Curves")
    print("="*70)

    # Setup
    bounds = PackBounds(x_min=0.0, x_max=1.0, y_min=0.0, y_max=0.5)
    r_min, r_max = 0.0112, 0.040  # 22.4 - 80mm diameter

    # Use EN 13450 grading
    from src.rock_packing import GradingCurve
    gc_en13450 = GradingCurve.en13450()

    # RSA packing
    rsa = RSAPacking(void_ratio=0.42)
    rocks = rsa.generate_rocks(
        bounds,
        r_min, r_max,
        target_fill_ratio=None,  # Ignored, uses void_ratio
        max_attempts=10000,
        grading_curve=gc_en13450
    )

    print(f"\nGenerated {len(rocks)} rocks via RSA")
    void = calculate_void_ratio(rocks, bounds)
    print(f"Void ratio: {void:.3f}")

    # Visualize
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(f"RSA Packing (EN 13450) - {len(rocks)} rocks, void={void:.3f}")
    ax.set_xlim(bounds.x_min - 0.05, bounds.x_max + 0.05)
    ax.set_ylim(bounds.y_min - 0.05, bounds.y_max + 0.05)
    ax.set_aspect('equal')

    # Draw bounds
    rect = patches.Rectangle(
        (bounds.x_min, bounds.y_min), bounds.width, bounds.height,
        linewidth=2, edgecolor='red', facecolor='none', linestyle='--'
    )
    ax.add_patch(rect)

    # Draw rocks
    for rock in rocks:
        circle = patches.Circle(
            (rock.x, rock.y), rock.radius,
            edgecolor='black', facecolor='slategray', alpha=0.7
        )
        ax.add_patch(circle)

    plt.tight_layout()
    plt.savefig('rsa_packing.png', dpi=100)
    print("  -> Saved: rsa_packing.png")
    plt.close()

    return rocks, bounds


def demo_compaction(rocks, bounds):
    """Demonstrate gravity-based compaction."""
    print("\n" + "="*70)
    print("DEMO 3: Gravity-Based Compaction")
    print("="*70)

    print(f"\nBefore compaction: {len(rocks)} rocks, void={calculate_void_ratio(rocks, bounds):.3f}")

    # Apply vertical compaction
    rocks_compact = apply_compaction_pattern(
        rocks,
        bounds,
        layer_thickness=0.05,
        pattern=[('vertical', 2)]
    )

    void_after = calculate_void_ratio(rocks_compact, bounds)
    print(f"After compaction:  {len(rocks_compact)} rocks, void={void_after:.3f}")
    print(f"Void reduction: {(calculate_void_ratio(rocks, bounds) - void_after)*100:.1f}%")

    # Visualize before/after
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    for ax, rock_list, title in [
        (ax1, rocks, f"Before Compaction (void={calculate_void_ratio(rocks, bounds):.3f})"),
        (ax2, rocks_compact, f"After Compaction (void={void_after:.3f})")
    ]:
        ax.set_title(title)
        ax.set_xlim(bounds.x_min - 0.05, bounds.x_max + 0.05)
        ax.set_ylim(bounds.y_min - 0.05, bounds.y_max + 0.05)
        ax.set_aspect('equal')

        rect = patches.Rectangle(
            (bounds.x_min, bounds.y_min), bounds.width, bounds.height,
            linewidth=2, edgecolor='red', facecolor='none', linestyle='--'
        )
        ax.add_patch(rect)

        for rock in rock_list:
            circle = patches.Circle(
                (rock.x, rock.y), rock.radius,
                edgecolor='black', facecolor='slategray', alpha=0.7
            )
            ax.add_patch(circle)

    plt.tight_layout()
    plt.savefig('compaction_before_after.png', dpi=100)
    print("  -> Saved: compaction_before_after.png")
    plt.close()


def demo_compaction_based_packing():
    """Demonstrate the new CompactionBasedPacking strategy."""
    print("\n" + "="*70)
    print("DEMO 4: CompactionBasedPacking Strategy (RSA + Gravity)")
    print("="*70)

    bounds = PackBounds(x_min=0.0, x_max=1.0, y_min=0.0, y_max=0.5)
    r_min, r_max = 0.0112, 0.040

    # Use new CompactionBasedPacking
    packer = CompactionBasedPacking(
        base_strategy=RSAPacking(void_ratio=0.42),
        layer_thickness=0.05,
        compaction_pattern=[('vertical', 2), ('horizontal', 1)]
    )

    rocks = packer.generate_rocks(
        bounds, r_min, r_max,
        target_fill_ratio=None,
        max_attempts=10000,
        grading_curve=GradingCurve.en13450()
    )

    void = calculate_void_ratio(rocks, bounds)
    print(f"\nFinal result: {len(rocks)} rocks, void={void:.3f}")

    # Visualize
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(f"CompactionBasedPacking - {len(rocks)} rocks, void={void:.3f}")
    ax.set_xlim(bounds.x_min - 0.05, bounds.x_max + 0.05)
    ax.set_ylim(bounds.y_min - 0.05, bounds.y_max + 0.05)
    ax.set_aspect('equal')

    rect = patches.Rectangle(
        (bounds.x_min, bounds.y_min), bounds.width, bounds.height,
        linewidth=2, edgecolor='red', facecolor='none', linestyle='--'
    )
    ax.add_patch(rect)

    for rock in rocks:
        circle = patches.Circle(
            (rock.x, rock.y), rock.radius,
            edgecolor='black', facecolor='slategray', alpha=0.7
        )
        ax.add_patch(circle)

    plt.tight_layout()
    plt.savefig('compaction_based_packing.png', dpi=100)
    print("  -> Saved: compaction_based_packing.png")
    plt.close()


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("Circle Packing & Compaction Ideas from GPR-repo")
    print("Adapted for Synth-GPR-1")
    print("="*70)

    # Demo 1: Grading curves
    demo_grading_curves()

    # Demo 2: RSA packing
    rocks, bounds = demo_rsa_packing()

    # Demo 3: Compaction
    demo_compaction(rocks, bounds)

    # Demo 4: CompactionBasedPacking
    demo_compaction_based_packing()

    print("\n" + "="*70)
    print("All demos complete! Check PNG files for visualizations.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
