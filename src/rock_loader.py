"""
Load pre-packed rocks from existing .in files instead of generating them.

Allows workers to skip packing algorithm and reuse existing rock configurations.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from .rock_model import Rock


@dataclass
class LoadedRock:
    """Rock loaded from .in file."""
    x: float
    y: float
    z: float
    radius: float
    material: str
    is_triangle: bool = False
    triangle_points: Optional[List[Tuple[float, float, float]]] = None

    def to_rock(self) -> Rock:
        """Convert to Rock object for use in scene."""
        return Rock(
            x=self.x,
            y=self.y,
            z=self.z,
            radius=self.radius,
            material=self.material
        )


class RockLoader:
    """Load rocks from existing .in files."""

    @staticmethod
    def extract_rocks_from_file(in_file: Path) -> Tuple[List[LoadedRock], dict]:
        """
        Extract all rocks from a .in file.

        Args:
            in_file: Path to .in file

        Returns:
            Tuple of (rocks_list, metadata_dict)
        """
        rocks = []
        metadata = {}

        if not in_file.exists():
            raise FileNotFoundError(f"Input file not found: {in_file}")

        with open(in_file, 'r') as f:
            lines = f.readlines()

        # Extract metadata from header
        for line in lines:
            if line.startswith('##') and ':' in line:
                key, value = line.strip('## \n').split(':', 1)
                metadata[key.strip()] = value.strip()

        # Extract rocks
        for line in lines:
            if line.startswith('#cylinder:'):
                # Parse: #cylinder: x1 y1 z1 x2 y2 z2 radius material
                match = re.match(
                    r'#cylinder:\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+'
                    r'([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+(\S+)',
                    line
                )
                if match:
                    # For cylinder, use midpoint
                    y_mid = (float(match.group(2)) + float(match.group(5))) / 2
                    rock = LoadedRock(
                        x=float(match.group(1)),
                        y=y_mid,
                        z=float(match.group(3)),
                        radius=float(match.group(7)),
                        material=match.group(8),
                        is_triangle=False
                    )
                    rocks.append(rock)

            elif line.startswith('#triangle:'):
                # Parse: #triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 radius material
                match = re.match(
                    r'#triangle:\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+'
                    r'([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+'
                    r'([\d.-]+)\s+([\d.-]+)\s+(\S+)',
                    line
                )
                if match:
                    # For triangle, use average y coordinate
                    y_avg = (float(match.group(2)) + float(match.group(5)) + float(match.group(8))) / 3
                    rock = LoadedRock(
                        x=float(match.group(1)),
                        y=y_avg,
                        z=float(match.group(3)),
                        radius=float(match.group(10)),
                        material=match.group(11),
                        is_triangle=True,
                        triangle_points=[
                            (float(match.group(1)), float(match.group(2)), float(match.group(3))),
                            (float(match.group(4)), float(match.group(5)), float(match.group(6))),
                            (float(match.group(7)), float(match.group(8)), float(match.group(9)))
                        ]
                    )
                    rocks.append(rock)

        if not rocks:
            raise ValueError(f"No rocks found in {in_file}")

        return rocks, metadata

    @staticmethod
    def load_rocks_for_ballast_layer(
        in_file: Path,
        ballast_bottom: float,
        ballast_top: float
    ) -> List[LoadedRock]:
        """
        Load rocks from .in file and filter those within ballast layer.

        Args:
            in_file: Path to .in file
            ballast_bottom: Bottom y-coordinate of ballast layer
            ballast_top: Top y-coordinate of ballast layer

        Returns:
            List of rocks within ballast layer
        """
        rocks, _ = RockLoader.extract_rocks_from_file(in_file)

        # Filter rocks in ballast layer
        filtered = [
            rock for rock in rocks
            if ballast_bottom <= rock.y <= ballast_top
        ]

        if not filtered:
            raise ValueError(
                f"No rocks found in ballast layer [{ballast_bottom}, {ballast_top}]. "
                f"Rocks found in y-range: "
                f"[{min(r.y for r in rocks):.4f}, {max(r.y for r in rocks):.4f}]"
            )

        return filtered

    @staticmethod
    def get_rock_statistics(rocks: List[LoadedRock]) -> dict:
        """Get statistics about loaded rocks."""
        if not rocks:
            return {}

        y_coords = [r.y for r in rocks]
        radii = [r.radius for r in rocks]

        return {
            'count': len(rocks),
            'min_y': min(y_coords),
            'max_y': max(y_coords),
            'avg_y': sum(y_coords) / len(y_coords),
            'min_radius': min(radii),
            'max_radius': max(radii),
            'avg_radius': sum(radii) / len(radii),
            'triangles': sum(1 for r in rocks if r.is_triangle),
            'cylinders': sum(1 for r in rocks if not r.is_triangle),
        }
