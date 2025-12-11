"""
Example: Using Domain Value Objects

Demonstrates how domain value objects improve code readability and safety
compared to using primitive types.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain import (
    PercentageVoidContamination,
    Point2D,
    Point3D,
    Length,
)



def example_pvc_usage():
    """Example: Percentage Void Contamination in practice."""
    print("=" * 60)
    print("Example 1: Percentage Void Contamination")
    print("=" * 60)
    
    # Before: Just a number (what does 25.0 mean?)
    # pvc_old = 25.0
    
    # After: Domain concept is explicit
    pvc = PercentageVoidContamination(value=25.0)
    
    print(f"PVC Value: {pvc}")  # 25.0%
    print(f"Classification: {pvc.classification()}")  # Fouled
    print(f"Is clean? {pvc.is_clean()}")  # False
    print(f"Is fouled? {pvc.is_fouled()}")  # True
    
    # Convert to Fouling Index
    porosity = 0.4  # 40% voids in clean ballast
    fi = pvc.to_fouling_index(porosity)
    print(f"Fouling Index (FI): {fi}%")  # 10%
    
    # Validation happens automatically
    try:
        invalid_pvc = PercentageVoidContamination(value=150.0)
    except ValueError as e:
        print(f"\n✓ Validation works: {e}")
    
    print()


def example_coordinates():
    """Example: Type-safe coordinates."""
    print("=" * 60)
    print("Example 2: Type-Safe Coordinates")
    print("=" * 60)
    
    # Before: Ambiguous floats
    # tx_x, tx_y, tx_z = 0.25, 1.35, 0.0025
    
    # After: Explicit 3D point
    tx_position = Point3D(x=0.25, y=1.35, z=0.0025)
    rx_position = Point3D(x=0.30, y=1.35, z=0.0025)
    
    print(f"TX Position: {tx_position}")
    print(f"RX Position: {rx_position}")
    
    # Calculate antenna separation (2D distance, Z is extrusion)
    separation = tx_position.distance_2d(rx_position)
    print(f"Antenna separation: {separation * 100:.1f} cm")
    
    # Project to 2D for visualization
    tx_2d = tx_position.to_2d()
    print(f"TX in 2D: {tx_2d}")
    
    print()


def example_lengths_with_units():
    """Example: Length with explicit units."""
    print("=" * 60)
    print("Example 3: Lengths with Units")
    print("=" * 60)
    
    # Before: Is this cm or m? Who knows!
    # ballast_thickness = 40
    
    # After: Unit is explicit
    ballast_thickness = Length(value=40, unit='cm')
    clearance = Length(value=5, unit='cm')
    
    print(f"Ballast thickness: {ballast_thickness}")  # 40cm
    print(f"Clearance: {clearance}")  # 5cm
    
    # Automatic unit conversion
    print(f"  In meters: {ballast_thickness.to_meters():.2f}m")  # 0.40m
    print(f"  In mm: {ballast_thickness.to_millimeters():.0f}mm")  # 400mm
    
    # Unit-safe arithmetic
    total_height = ballast_thickness + clearance
    print(f"\nTotal height: {total_height} = {total_height.to_centimeters():.0f}cm")
    
    # Unit-safe comparison
    min_thickness = Length(value=300, unit='mm')
    if ballast_thickness > min_thickness:
        print(f"✓ Ballast meets minimum thickness ({min_thickness})")
    
    print()


def example_real_world_scenario():
    """Example: Realistic scenario using multiple value objects."""
    print("=" * 60)
    print("Example 4: Real-World Scenario")
    print("=" * 60)
    
    # Define a fouled ballast scene
    pvc = PercentageVoidContamination(value=35.0)
    ballast_thickness = Length(value=40, unit='cm')
    antenna_height = Length(value=5, unit='cm')
    
    # Antenna position (above ballast)
    antenna = Point3D(
        x=0.25,  # Center of 0.5m domain
        y=ballast_thickness.to_meters() + antenna_height.to_meters(),
        z=0.0025  # Center of 5mm depth
    )
    
    print(f"Scene Configuration:")
    print(f"  PVC: {pvc} ({pvc.classification()})")
    print(f"  Ballast thickness: {ballast_thickness}")
    print(f"  Antenna position: {antenna}")
    print(f"  Antenna height above ballast: {antenna_height}")
    
    # Domain logic becomes clearer
    if pvc.is_fouled():
        print(f"\n⚠ WARNING: Ballast is {pvc.classification().lower()}")
        print(f"  Recommended action: Track maintenance required")
    
    # Type safety prevents errors
    try:
        # This would be a type error (can't add PVC + Length)
        # wrong = pvc + ballast_thickness  # ❌ Type checker catches this!
        pass
    except:
        pass
    
    print()


if __name__ == "__main__":
    example_pvc_usage()
    example_coordinates()
    example_lengths_with_units()
    example_real_world_scenario()
    
    print("=" * 60)
    print("Summary: Benefits of Value Objects")
    print("=" * 60)
    print(" ✓ Type safety (prevents mixing PVC and Length)")
    print(" ✓ Unit clarity (cm vs m explicit)")
    print(" ✓ Validation (PVC must be 0-100%)")
    print(" ✓ Domain logic (classification() method)")
    print(" ✓ Immutability (can't accidentally modify)")
    print(" ✓ Readability (code reads like domain language)")
