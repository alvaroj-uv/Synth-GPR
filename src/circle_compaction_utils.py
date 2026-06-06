"""
Circle compaction utilities inspired by jagua-rs and GPR-repo/RSA/Circles.

Provides discretized gravity-based settling and realistic void-filling
for rock packings. Adapted from circle_Compaction.py (GPR-repo).

Key Ideas:
- Discretize 2D domain into slices (vertical or horizontal)
- Compact each slice by moving circles downward until they touch lower circles
- Iterate horizontal/vertical sequences for realistic settling
"""

import math
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
from .rock_model import Rock, PackingBounds


@dataclass
class CompactionConfig:
    """Configuration for discretized compaction."""
    layer_thickness: float = 0.01  # Thickness of discretization slice (m)
    horizontal: bool = False  # Direction of compaction (vertical if False)
    max_iterations: int = 1  # Number of vertical/horizontal passes


def discretize_domain(
    rocks: List[Rock],
    bounds: PackingBounds,
    layer_thickness: float,
    horizontal: bool = False
) -> Tuple[np.ndarray, int]:
    """
    Discretize 2D domain into slices and assign rocks to slices.

    Adapted from circle_Compaction.py discretization_domain().

    Args:
        rocks: List of Rock objects to discretize.
        bounds: Bounding box (x_min, x_max, y_min, y_max).
        layer_thickness: Thickness of each discretization slice.
        horizontal: If True, slice horizontally (along x); else vertically (along y).

    Returns:
        (discret_domains, num_domains):
            discret_domains: 2D array where [i, j] holds rock info or zeros
            num_domains: Number of slices created
    """
    rocks_np = np.array([[r.x, r.y, r.radius] for r in rocks])

    if not horizontal:
        # Vertical slicing (by y-coordinate)
        num_domains = math.floor(bounds.height / layer_thickness)
        if num_domains < 1:
            num_domains = 1

        max_per_slice = math.ceil(len(rocks) / num_domains) + 1
        discret_domains = np.zeros([num_domains, max_per_slice, 3])

        # Assign rocks to their vertical slice
        for domain_idx in range(num_domains):
            y_min = bounds.y_min + domain_idx * layer_thickness
            y_max = y_min + layer_thickness

            rocks_in_slice = rocks_np[
                (rocks_np[:, 1] >= y_min) & (rocks_np[:, 1] < y_max)
            ]

            for rock_idx, rock in enumerate(rocks_in_slice):
                if rock_idx < max_per_slice:
                    discret_domains[domain_idx, rock_idx, :] = rock
    else:
        # Horizontal slicing (by x-coordinate)
        num_domains = math.floor(bounds.width / layer_thickness)
        if num_domains < 1:
            num_domains = 1

        max_per_slice = math.ceil(len(rocks) / num_domains) + 1
        discret_domains = np.zeros([num_domains, max_per_slice, 3])

        # Swap to work with x as primary coordinate
        rocks_swap = rocks_np.copy()
        rocks_swap[:, [0, 1]] = rocks_np[:, [1, 0]]

        # Assign rocks to their horizontal slice
        for domain_idx in range(num_domains):
            x_min = bounds.x_min + domain_idx * layer_thickness
            x_max = x_min + layer_thickness

            rocks_in_slice = rocks_swap[
                (rocks_swap[:, 1] >= x_min) & (rocks_swap[:, 1] < x_max)
            ]

            for rock_idx, rock in enumerate(rocks_in_slice):
                if rock_idx < max_per_slice:
                    discret_domains[domain_idx, rock_idx, :] = rock

    return discret_domains, num_domains


def compact_slice(
    domain: np.ndarray,
    rocks_below: np.ndarray
) -> np.ndarray:
    """
    Compact rocks in one slice by moving them downward until they touch.

    Adapted from circle_Compaction.py compaction() logic.
    Moves each rock in the domain downward (increasing y for vertical,
    but we work in domain space) until it touches another rock below.

    Args:
        domain: Array of rocks in current slice (non-zero rows).
        rocks_below: All rocks in current and below slices.

    Returns:
        Compacted domain array.
    """
    compacted = domain.copy()

    # Filter out zero rows
    nonzero_rocks = domain[domain[:, 0] != 0.0]
    nonzero_below = rocks_below[rocks_below[:, 0] != 0.0]

    if len(nonzero_rocks) == 0 or len(nonzero_below) == 0:
        return compacted

    for idx, rock in enumerate(nonzero_rocks):
        x, y, r = rock[0], rock[1], rock[2]

        # Find rocks below that are within horizontal reach
        dx_diff = nonzero_below[:, 0] - x
        reach = r + nonzero_below[:, 2]
        below_mask = (
            (dx_diff >= -reach) &
            (dx_diff <= reach) &
            (nonzero_below[:, 1] < y)  # Only rocks below
        )

        relevant_rocks = nonzero_below[below_mask]

        if len(relevant_rocks) == 0:
            # No rocks below: settle to bottom
            compacted[idx, 1] = r
        else:
            # Find maximum y (shortest distance to rocks below)
            distances = np.sqrt(
                (r + relevant_rocks[:, 2])**2 -
                (x - relevant_rocks[:, 0])**2
            ) + relevant_rocks[:, 1]
            max_y = max(np.amax(distances), r)
            compacted[idx, 1] = max_y

    return compacted


def apply_compaction_pattern(
    rocks: List[Rock],
    bounds: PackingBounds,
    layer_thickness: float = 0.01,
    pattern: List[Tuple[str, int]] = None
) -> List[Rock]:
    """
    Apply a sequence of horizontal/vertical compactions to settle rocks.

    Adapted from circle_Compaction.py run_comp_pattern().

    Args:
        rocks: Initial rock list.
        bounds: Bounding box for compaction.
        layer_thickness: Thickness of discretization slices.
        pattern: List of (direction, count) tuples, e.g., [('vertical', 2), ('horizontal', 1)].
                 If None, defaults to [('vertical', 1), ('horizontal', 1)].

    Returns:
        Compacted rock list.
    """
    if pattern is None:
        pattern = [('vertical', 1), ('horizontal', 1)]

    current_rocks = rocks

    for direction, num_iterations in pattern:
        for _ in range(num_iterations):
            horizontal = (direction == 'horizontal')
            discret_domains, num_domains = discretize_domain(
                current_rocks, bounds, layer_thickness, horizontal
            )

            # Compact each slice
            all_rocks_below = np.zeros([num_domains * discret_domains.shape[1], 3])
            all_rocks_below[:] = discret_domains.reshape(-1, 3)

            for domain_idx in range(num_domains):
                rocks_below_flat = all_rocks_below[:domain_idx * discret_domains.shape[1] + discret_domains.shape[1]]
                discret_domains[domain_idx] = compact_slice(
                    discret_domains[domain_idx],
                    rocks_below_flat
                )

            # Convert back to Rock list
            flattened = discret_domains.reshape(-1, 3)
            nonzero_rocks = flattened[flattened[:, 0] != 0.0]

            # Swap coordinates back if horizontal
            if horizontal:
                nonzero_rocks[:, [0, 1]] = nonzero_rocks[:, [1, 0]]

            current_rocks = [
                Rock(x=r[0], y=r[1], radius=r[2])
                for r in nonzero_rocks
            ]

    return current_rocks


def calculate_void_ratio(rocks: List[Rock], bounds: PackingBounds) -> float:
    """
    Calculate void ratio of rock packing.

    void_ratio = (area_empty / area_total)

    Args:
        rocks: List of Rock objects.
        bounds: Bounding box.

    Returns:
        Void ratio (0 to 1).
    """
    total_area = bounds.area
    rock_area = sum(math.pi * r.radius**2 for r in rocks)
    void = (total_area - rock_area) / total_area
    return max(0.0, min(1.0, void))
