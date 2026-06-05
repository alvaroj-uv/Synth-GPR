"""
Pymunk-based ballast packing using realistic physics simulation.

Integrates PINN4GPR's BallastSimulation (RSA + gravity compaction) into Synth-GPR's
pluggable rock packing architecture.

Physics engine: pymunk (2D rigid-body dynamics)
Algorithm: Random Sequential Adsorption (RSA) + gravity compaction
Output: Realistic, settled ballast configurations matching real railway conditions
"""

import pymunk
import numpy as np
import time
from typing import List, Optional

from .rock_model import Rock, PackingBounds
from .rock_packing import RockPackingStrategy, GradingCurve
from .constants import PHC  # single source of truth for material densities


class BallastSimulation:
    """
    Class responsible to create and run a 2D physics simulation for generating
    realistic ballast positions and radii.

    Uses Random Sequential Adsorption (RSA) followed by gravity compaction
    to produce physically realistic ballast stone configurations.

    Parameters
    ----------
    domain_size : tuple[float, float]
        (x, y) size of the simulation in meters.
    radii_distribution : np.ndarray, default: None
        radii distribution to use in the RSA algorithm.
        Shape (n_sieves, 3): [[r_max, r_min, mass_frac], ...]
        If None, the default clean ballast distribution is used.
    buffer_y : float, default: 0
        Extra vertical headroom above the domain for rocks to settle into.
    verbose : bool
        Print debug info. Default: False
    """

    def __init__(
        self,
        domain_size: tuple[float, float],
        radii_distribution: Optional[np.ndarray] = None,
        buffer_y: float = 0,
        verbose: bool = False,
    ):
        self.domain_size = domain_size
        self.input_radii_distribution = radii_distribution
        self.buffer_y = buffer_y
        self.verbose = verbose

    @classmethod
    def get_clean_ballast_radii_distrib(cls) -> np.ndarray:
        """Returns the radii distribution for clean ballast without fouling."""
        ballast_radii_distrib = np.array([
            [0.063, 0.050, 0.15],
            [0.050, 0.040, 0.45],
            [0.040, 0.0315, 0.33],
            [0.0315, 0.0224, 0.05],
            [0.0224, 0.00476, 0.02],
        ])
        ballast_radii_distrib[:, 0:2] = ballast_radii_distrib[:, 0:2] / 2
        return ballast_radii_distrib

    @classmethod
    def get_fouled_ballast_radii_distrib(cls) -> np.ndarray:
        """Returns the radii distribution for very fouled ballast."""
        ballast_radii_distrib = np.array([
            [0.063, 0.050, 0.10],
            [0.050, 0.040, 0.30],
            [0.040, 0.0315, 0.25],
            [0.0315, 0.0224, 0.15],
            [0.0224, 0.00476, 0.20],
        ])
        ballast_radii_distrib[:, 0:2] = ballast_radii_distrib[:, 0:2] / 2
        return ballast_radii_distrib

    def _get_standard_sieve_bounds(self) -> np.ndarray:
        """Returns the standard sieve curve (Gleisschotter 32/50)."""
        sieve_63 = np.array([0.063, 1, 1])
        sieve_50 = np.array([0.050, 0.7, 0.99])
        sieve_40 = np.array([0.040, 0.3, 0.65])
        sieve_31 = np.array([0.0315, 0.03, 0.25])
        sieve_22 = np.array([0.0224, 0.01, 0.03])
        sieve_low_limit = np.array([0.018, 0, 0])
        sieve_bounds = np.vstack(
            [sieve_63, sieve_50, sieve_40, sieve_31, sieve_22, sieve_low_limit]
        )
        return sieve_bounds

    def sample_radii_distribution(
        self, sieve_diameter_bounds: np.ndarray, random_generator: np.random.Generator
    ) -> np.ndarray:
        """Samples a random radii distribution from sieve bounds."""
        grad_curve = sieve_diameter_bounds[:, [0, 1]]
        grad_curve[:, 1] = (
            random_generator.beta(2, 2) * (
                sieve_diameter_bounds[:, 2] - sieve_diameter_bounds[:, 1]
            )
            + sieve_diameter_bounds[:, 1]
        )

        grad_curve_conv = np.zeros([grad_curve.shape[0] - 1, 3])
        for i in range(grad_curve.shape[0] - 1):
            grad_curve_conv[i] = np.array([
                grad_curve[i, 0] / 2,
                grad_curve[i + 1, 0] / 2,
                grad_curve[i, 1] - grad_curve[i + 1, 1],
            ])

        return grad_curve_conv

    def random_sequential_adsorption(
        self,
        space: pymunk.Space,
        required_void: float,
        mult_factor: float,
        random_seed: Optional[int] = None,
    ) -> pymunk.Space:
        """
        Use RSA algorithm to randomly place ballast stones.

        Parameters
        ----------
        space : pymunk.Space
            Space in which to place circles
        required_void : float
            Fraction of void to fill (0.44 typical)
        mult_factor : float
            Scaling factor for pymunk numerical stability
        random_seed : int, optional
            Seed for RNG

        Returns
        -------
        pymunk.Space
            Space with circles added
        """
        size = self.domain_size[0], self.domain_size[1] + self.buffer_y
        random_generator = np.random.default_rng(random_seed)
        cur_void = 1
        req_void_cur = 1
        timeout_start = time.time()

        radii_distribution = self.input_radii_distribution
        if radii_distribution is None:
            radii_distribution = self.sample_radii_distribution(
                self._get_standard_sieve_bounds(), random_generator
            )

        for grain in radii_distribution:
            req_void_cur -= grain[2] * (1 - required_void)
            while req_void_cur < cur_void:
                radius = random_generator.uniform(grain[1], grain[0]) * mult_factor
                x_pos = random_generator.uniform(
                    radius, size[0] * mult_factor - radius
                )
                y_pos = random_generator.uniform(
                    radius, size[1] * mult_factor - radius
                )
                body = pymunk.Body()
                body.position = x_pos, y_pos
                circle = pymunk.Circle(body, radius)
                circle.density = PHC.BALLAST_DENSITY_PYMUNK  # from constants.py

                intersect = space.shape_query(circle)
                if len(intersect) == 0:
                    space.add(body, circle)
                    cur_void = cur_void - circle.area / (size[0] * size[1] * mult_factor ** 2)

        elapsed_time = round(time.time() - timeout_start, 2)
        if self.verbose:
            print(f"RSA Algorithm elapsed: {elapsed_time}s")
            print(f"N bodies before compaction: {len(space.bodies)}")

        return space

    def _run(
        self,
        space: pymunk.Space,
        running_time: float,
        time_step: float,
        display: bool,
        mult_factor: float,
    ) -> pymunk.Space:
        """Internal simulation runner."""
        if display:
            import pygame

            import pymunk.pygame_util

            pymunk.pygame_util.positive_y_is_up = True
            pygame.init()
            surface = pygame.display.set_mode(
                (int(self.domain_size[0] * mult_factor), int(self.domain_size[1] * mult_factor))
            )
            draw_options = pymunk.pygame_util.DrawOptions(surface)

        current_time = 0.0
        while current_time < running_time:
            current_time += time_step
            space.step(time_step)
            if display:
                surface.fill((0, 0, 0))
                space.debug_draw(draw_options)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        display = False

        if display:
            input("Simulation ended! Waiting for user input to continue.")
            pygame.display.quit()

        return space

    def run(
        self,
        running_time: float = 2,
        time_step: float = PHC.GRAVITY_SETTLE_TIME_STEP,  # from constants.py
        display: bool = False,
        random_seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Run the full ballast simulation (RSA + gravity compaction).

        Parameters
        ----------
        running_time : float
            Simulated time to run (seconds)
        time_step : float
            Time step for physics integration
        display : bool
            Show pygame visualization
        random_seed : int, optional
            Seed for RNG

        Returns
        -------
        np.ndarray of shape [n_rocks, 3]
            Rock positions and radii: [[x, y, radius], ...]
        """
        space = pymunk.Space()
        space.gravity = 0, -981

        mult_factor = 500

        wall_min_x = -0.03 * mult_factor
        wall_min_y = 0
        wall_max_x = (self.domain_size[0] + 0.03) * mult_factor
        wall_max_y = (self.domain_size[1] + self.buffer_y) * mult_factor

        floor = pymunk.Poly(
            space.static_body,
            [(wall_min_x, wall_min_y), (wall_max_x, wall_min_y), (wall_max_x, wall_min_y - 1), (wall_min_x, wall_min_y - 1)],
        )
        space.add(floor)

        left_wall = pymunk.Poly(
            space.static_body,
            [(wall_min_x, wall_min_y), (wall_min_x - 1, wall_min_y), (wall_min_x - 1, wall_max_y), (wall_min_x, wall_max_y)],
        )
        right_wall = pymunk.Poly(
            space.static_body,
            [(wall_max_x, wall_min_y), (wall_max_x + 1, wall_min_y), (wall_max_x + 1, wall_max_y), (wall_max_x, wall_max_y)],
        )
        space.add(left_wall)
        space.add(right_wall)

        required_void = 0.44
        space = self.random_sequential_adsorption(space, required_void, mult_factor, random_seed)
        space = self._run(space, running_time, time_step, display, mult_factor)

        ballast_stones = []
        for body in space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                shapes = body.shapes
                if body.position[1] / mult_factor < self.domain_size[1]:
                    for circle in shapes:
                        ballast_stones.append((body.position[0], body.position[1], circle.radius))

        res = np.array(ballast_stones) / mult_factor
        return res


class PymunkBallastPacking(RockPackingStrategy):
    """
    Rock packing using pymunk physics simulation (RSA + gravity compaction).

    Produces physically realistic ballast configurations by:
    1. Randomly placing rocks (RSA algorithm)
    2. Simulating gravity to compact and settle them
    3. Filtering results to fit the target layer bounds

    This integrates PINN4GPR's BallastSimulation into Synth-GPR's packing architecture.
    """

    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.85,
        max_attempts: int = 5000,
        min_gap: float = 0.0,
        grading_curve: Optional[GradingCurve] = None,
    ) -> List[Rock]:
        """
        Generate rocks using pymunk physics simulation.

        Parameters
        ----------
        bounds : PackingBounds
            Bounding box for rock placement
        radius_min : float
            Minimum rock radius (meters)
        radius_max : float
            Maximum rock radius (meters)
        target_fill_ratio : float
            Target void fill ratio (0.85 = 85% fill)
        max_attempts : int
            Max iterations (not used by pymunk, kept for interface)
        min_gap : float
            Minimum gap between rocks (not used, kept for interface)
        grading_curve : GradingCurve, optional
            Sieve grading curve. If None, uses clean ballast distribution.

        Returns
        -------
        List[Rock]
            List of Rock objects within bounds
        """
        domain_width = bounds.width
        domain_height = bounds.height

        if grading_curve is not None:
            radii_distribution = self._grading_curve_to_pinn4gpr_format(grading_curve)
        else:
            radii_distribution = BallastSimulation.get_clean_ballast_radii_distrib()

        simulation = BallastSimulation(
            domain_size=(domain_width, domain_height),
            radii_distribution=radii_distribution,
            buffer_y=0.4,
            verbose=False,
        )

        rocks_array = simulation.run(
            running_time=2.0,
            time_step=0.002,
            display=False,
            random_seed=None,  # Will use numpy's default RNG
        )

        rocks = []
        for x, y, radius in rocks_array:
            translated_x = bounds.x_min + x
            translated_y = bounds.y_min + y

            if (bounds.x_min <= translated_x <= bounds.x_max and
                bounds.y_min <= translated_y <= bounds.y_max and
                radius >= radius_min and radius <= radius_max):
                rocks.append(self._create_rock(translated_x, translated_y, radius))

        return rocks

    @staticmethod
    def _grading_curve_to_pinn4gpr_format(grading_curve: GradingCurve) -> np.ndarray:
        """
        Convert Synth-GPR GradingCurve to PINN4GPR's radii_distribution format.

        Parameters
        ----------
        grading_curve : GradingCurve
            Grading curve with _sizes (radii) and _cdf

        Returns
        -------
        np.ndarray
            Array of shape (n-1, 3): [[r_max, r_min, mass_frac], ...]
        """
        sizes = grading_curve._sizes
        cdf = grading_curve._cdf

        distribution = []
        for i in range(len(sizes) - 1):
            r_max = sizes[i + 1]
            r_min = sizes[i]
            mass_frac = cdf[i + 1] - cdf[i]

            distribution.append([r_max, r_min, mass_frac])

        return np.array(distribution)
