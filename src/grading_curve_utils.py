"""
Grading curve and sieve distribution utilities.

Adapted from GPR-repo/RSA/Circles/gen_sieve_curve.py with enhancements
for waveform-based feature extraction and realistic particle packing.

Key Ideas:
- Generate random particle size distributions from sieve bounds
- Use beta distribution to sample realistic gradings within specification
- Convert between sieve curves (cumulative %) and particle size fractions
- Support real-world standards (EN 13450 railway ballast)
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class SieveBounds:
    """
    Represents sieve bounds for one particle size fraction.

    Attributes:
        diameter_m: Sieve opening diameter (metres)
        lower_bound: Lower cumulative % bound
        upper_bound: Upper cumulative % bound
    """
    diameter_m: float
    lower_bound: float
    upper_bound: float


def pick_rand_grading_curve(
    sieve_bounds: List[SieveBounds],
    alpha: float = 2.0,
    beta: float = 2.0
) -> np.ndarray:
    """
    Generate random grading curve from sieve bounds using beta distribution.

    Adapted from gen_sieve_curve.py pick_rand_curve().

    Samples a random cumulative % within each sieve's bounds using a beta
    distribution. This produces realistic PSD variations while respecting
    specification envelopes.

    Args:
        sieve_bounds: List of SieveBounds objects in ascending diameter order.
        alpha, beta: Shape parameters for beta distribution (default 2,2 for smooth curves).

    Returns:
        Array of shape (n_sieves, 2) with [diameter (m), cumulative %]
    """
    n_sieves = len(sieve_bounds)
    grad_curve = np.zeros([n_sieves, 2])

    # Keep diameters
    grad_curve[:, 0] = np.array([s.diameter_m for s in sieve_bounds])

    # Sample cumulative % within bounds using beta distribution
    for i, sieve in enumerate(sieve_bounds):
        lower = sieve.lower_bound
        upper = sieve.upper_bound
        # Beta(alpha, beta) on [0,1], then scale to [lower, upper]
        u = np.random.beta(alpha, beta)
        grad_curve[i, 1] = lower + u * (upper - lower)

    # Ensure monotone increasing
    for i in range(1, n_sieves):
        if grad_curve[i, 1] <= grad_curve[i - 1, 1]:
            grad_curve[i, 1] = grad_curve[i - 1, 1] + 0.1

    return grad_curve


def convert_sieve_curve_to_fractions(
    grad_curve: np.ndarray
) -> np.ndarray:
    """
    Convert cumulative sieve curve to particle size fractions.

    Adapted from gen_sieve_curve.py convert_sieve_curve().

    Converts from [diameter, cumulative_%] to [d_max (radius), d_min (radius), pct_retained]
    for use in sequential placement algorithms (RSA).

    Args:
        grad_curve: Array of shape (n_sieves, 2) with [diameter_m, cumulative_%]

    Returns:
        Array of shape (n_sieves-1, 3) with [r_max, r_min, pct_retained]
        where r_max/r_min are in metres (radii, not diameters).
    """
    n_fractions = grad_curve.shape[0] - 1
    fractions = np.zeros([n_fractions, 3])

    for i in range(n_fractions):
        d_max = grad_curve[i, 0]      # Diameter of current sieve
        d_min = grad_curve[i + 1, 0]  # Diameter of next sieve
        pct_between = grad_curve[i, 1] - grad_curve[i + 1, 1]  # Cumulative diff

        # Convert to radius and store
        fractions[i, 0] = d_max / 2.0      # r_max
        fractions[i, 1] = d_min / 2.0      # r_min
        fractions[i, 2] = max(0.0, pct_between)  # pct_retained

    return fractions


def en13450_bounds() -> List[SieveBounds]:
    """
    EN 13450:2013 Type-I railway ballast (31.5/63 fraction) specification bounds.

    Reference: EN 13450:2013, Table 4.
    Sieve sizes: 22.4, 31.5, 40, 50, 63, 80 mm.
    Returns cumulative percentage passing bounds (specification envelope).

    Returns:
        List of SieveBounds objects.
    """
    sieves_mm = [22.4, 31.5, 40.0, 50.0, 63.0, 80.0]
    # Lower and upper bounds from EN 13450 spec
    lower_bounds = [0.0, 5.0, 25.0, 60.0, 92.0, 98.0]
    upper_bounds = [0.0, 12.0, 40.0, 70.0, 98.0, 100.0]

    return [
        SieveBounds(diameter_m=s / 1000.0, lower_bound=l, upper_bound=u)
        for s, l, u in zip(sieves_mm, lower_bounds, upper_bounds)
    ]


def fuller_ideal_curve(
    d_max_m: float,
    n: float = 0.5,
    n_points: int = 20
) -> np.ndarray:
    """
    Fuller-Thompson ideal grading curve (maximizes packing density).

    P(d) = 100 * (d / d_max)^n, where n=0.5 for maximum density.

    Args:
        d_max_m: Maximum particle diameter (metres).
        n: Fuller exponent (default 0.5).
        n_points: Resolution of the CDF table.

    Returns:
        Array of shape (n_points, 2) with [diameter_m, cumulative_%]
    """
    diameters = np.linspace(d_max_m * 0.01, d_max_m, n_points)
    cumulative_pct = 100.0 * (diameters / d_max_m) ** n

    curve = np.zeros([n_points, 2])
    curve[:, 0] = diameters
    curve[:, 1] = cumulative_pct

    return curve


def uniform_distribution(
    d_min_m: float,
    d_max_m: float,
    n_points: int = 2
) -> np.ndarray:
    """
    Uniform (flat) particle size distribution.

    Equivalent to random.uniform sampling; useful as baseline.

    Args:
        d_min_m: Minimum diameter (metres).
        d_max_m: Maximum diameter (metres).
        n_points: Number of sample points (default 2 for linear interpolation).

    Returns:
        Array of shape (n_points, 2) with [diameter_m, cumulative_%]
    """
    diameters = np.linspace(d_min_m, d_max_m, n_points)
    cumulative_pct = 100.0 * (diameters - d_min_m) / (d_max_m - d_min_m)

    curve = np.zeros([n_points, 2])
    curve[:, 0] = diameters
    curve[:, 1] = cumulative_pct

    return curve


def sample_radii_from_fractions(
    fractions: np.ndarray,
    n_samples: int = 100
) -> List[float]:
    """
    Sample particle radii according to retained percentages in fractions.

    Useful for generating representative samples from a given PSD.

    Args:
        fractions: Array of shape (n_fractions, 3) with [r_max, r_min, pct_retained]
        n_samples: Total number of radii to sample.

    Returns:
        List of radii (metres).
    """
    radii = []

    for r_max, r_min, pct_retained in fractions:
        # Number of samples in this fraction
        n_in_fraction = int(np.round(pct_retained / 100.0 * n_samples))

        # Sample uniformly within fraction range
        sampled = np.random.uniform(r_min, r_max, n_in_fraction)
        radii.extend(sampled.tolist())

    return radii


def print_grading_curve(
    grad_curve: np.ndarray,
    label: str = "Grading Curve"
) -> str:
    """
    Pretty-print grading curve for inspection.

    Args:
        grad_curve: Array of shape (n_sieves, 2).
        label: Label for output.

    Returns:
        Formatted string representation.
    """
    lines = [f"\n{label}:", "-" * 50]
    lines.append(f"{'Diameter (mm)':<15} {'Cumulative % Pass':<20}")
    lines.append("-" * 50)

    for d, pct in grad_curve:
        lines.append(f"{d*1000:<15.2f} {pct:<20.2f}")

    lines.append("-" * 50)
    return "\n".join(lines)
