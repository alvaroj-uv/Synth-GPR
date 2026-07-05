"""
Pymunk-based simulation utilities for ballast packing and Mbubia scene generation.

Contains:
- BallastSimulation: Physics-based RSA + gravity compaction
- MbubiaPymunkSceneGenerator: Two-layer railway ballast scene generator

Rock packing strategy (PymunkBallastPacking) is in rock_packing.py.

Physics engine: pymunk (2D rigid-body dynamics)
"""

import json
import pymunk
import numpy as np
import time
from pathlib import Path
from typing import List, Optional, Tuple

from .constants import PHC
from .rock_model import Layer, Rock, PackingBounds  # shared domain models
from .rock_packing import RockPackingStrategy
# NOTE: this module is intentionally decoupled from SceneModel/config. Packers
# take geometry (Layer/PackingBounds) + size params and return Rock objects.
# Scene/config adaptation lives in the orchestration layer (granular_worker,
# layer_scene_builder), never here.

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


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




# ─── Mbubia Scene Generator ────────────────────────────────────────────────

class MbubiaPymunkSceneGenerator(RockPackingStrategy):
    """
    Multi-layer pymunk-based scene generator for railway ballast and soil layers.

    Generates rocks in any number of layers via physics-based RSA + gravity compaction.
    Delegates physics to BallastSimulation per layer, then converts circles to polygons.

    Extends RockPackingStrategy so it integrates natively with the packing hierarchy:
    - generate_rocks() fulfils the abstract interface (single-layer, no domain config)
    - generate() is the multi-layer entry point (painter's algorithm, domain config)

    Typical use: Two-layer Mbubia (upper ballast + lower subgrade)
    But supports 1, 2, 3+ layers for other applications.
    """

    # Default domain geometry (Mbubia standard)
    _DEFAULT_DOMAIN_X          = 4.0
    _DEFAULT_DOMAIN_Y          = 1.2
    _DEFAULT_DOMAIN_Z          = 0.05
    _DEFAULT_ANTENNA_CLEARANCE = 0.30
    _DEFAULT_LAYER_INTERFACE_Y = 0.488

    def __init__(
        self,
        scene_name: str,
        upper_material: str = "clean_ballast",
        lower_material: str = "fouled_ballast",
        output_dir: Path = None,
        verbose: bool = True,
        domain_x: Optional[float] = None,
        domain_y: Optional[float] = None,
        domain_z: Optional[float] = None,
        layer_interface_y: Optional[float] = None,
        randomize_rock_materials: bool = False,
        random_material_pool: Optional[List[str]] = None,
        settle_time: float = 2.0,
    ):
        self.scene_name         = scene_name
        self.upper_material     = upper_material
        self.lower_material     = lower_material
        self.output_dir         = Path(output_dir) if output_dir is not None else None
        self.verbose            = verbose
        # Gravity-settle duration (s). Lower -> looser pack (higher porosity):
        # ~0.1 gives phi~0.40, the 2-D-equivalent of field ballast void (Brancadoro);
        # default 2.0 settles dense (phi~0.12). See generate_rocks.
        self.settle_time        = settle_time
        self.randomize_rock_materials = randomize_rock_materials
        # Caller provides the pool so this class stays EM-agnostic
        self.random_material_pool = random_material_pool or [upper_material, lower_material]
        self.rocks: List[Rock] = []

        self.DOMAIN_X          = domain_x          if domain_x          is not None else self._DEFAULT_DOMAIN_X
        self.DOMAIN_Y          = domain_y          if domain_y          is not None else self._DEFAULT_DOMAIN_Y
        self.DOMAIN_Z          = domain_z          if domain_z          is not None else self._DEFAULT_DOMAIN_Z
        self.LAYER_INTERFACE_Y = layer_interface_y if layer_interface_y is not None else self._DEFAULT_LAYER_INTERFACE_Y
        self.ANTENNA_HEIGHT    = self.DOMAIN_Y + self._DEFAULT_ANTENNA_CLEARANCE

    # ── RockPackingStrategy interface ────────────────────────────────────────

    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float = 0.0,
        radius_max: float = float("inf"),
        target_fill_ratio: float = 0.85,
        max_attempts: int = 5000,
        min_gap: float = 0.0,
        grading_curve=None,
        random_seed: Optional[int] = None,
    ) -> List[Rock]:
        """
        RockPackingStrategy interface — single-layer generation within bounds.

        Runs BallastSimulation (pymunk gravity settling) for the given bounds,
        applies polygon conversion via the inherited polygonize() helper, and
        returns List[Rock]. When ``random_seed`` is given, both the gravity
        simulation and the polygon shaping are deterministic.

        For multi-layer painter's algorithm scenes use generate() instead.
        """
        sim = BallastSimulation(
            domain_size=(bounds.width, bounds.height),
            radii_distribution=self._get_radii_for(self.upper_material),
            buffer_y=0.2,
            verbose=self.verbose,
        )
        rng = np.random.default_rng(random_seed)
        circle_array = sim.run(
            running_time=self.settle_time, time_step=PHC.GRAVITY_SETTLE_TIME_STEP,
            display=False, random_seed=random_seed,
        )
        circle_array[:, 0] += bounds.x_min
        circle_array[:, 1] += bounds.y_min

        rocks = [Rock(x=float(x), y=float(y), radius=float(r)) for x, y, r in circle_array]
        self.polygonize(rocks, rng=rng)
        return rocks

    def pack(
        self,
        bounds: PackingBounds,
        radius_min: float = 0.0,
        radius_max: float = float("inf"),
        target_fill_ratio: float = 0.85,
        *,
        seed: Optional[int] = None,
    ) -> List[Rock]:
        """Unified entry point (overrides base): routes ``seed`` into the pymunk
        gravity simulation. generate_rocks already returns polygons, so no extra
        polygonisation step is needed here."""
        return self.generate_rocks(bounds, radius_min, radius_max,
                                   target_fill_ratio, random_seed=seed)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _validate_configuration(self) -> None:
        errors = []
        if self.ANTENNA_HEIGHT <= self.DOMAIN_Y:
            errors.append(
                f"Antenna height ({self.ANTENNA_HEIGHT}m) must be above domain top ({self.DOMAIN_Y}m)."
            )
        if self.LAYER_INTERFACE_Y <= 0 or self.LAYER_INTERFACE_Y >= self.DOMAIN_Y:
            errors.append(
                f"Layer interface ({self.LAYER_INTERFACE_Y}m) must be within domain (0, {self.DOMAIN_Y}m)"
            )
        if self.DOMAIN_X <= 0 or self.DOMAIN_Y <= 0 or self.DOMAIN_Z <= 0:
            errors.append(f"Domain dimensions must be positive: {self.DOMAIN_X} x {self.DOMAIN_Y} x {self.DOMAIN_Z}")
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  * {e}" for e in errors))
        if self.verbose:
            print("[OK] Configuration validated")
            print(f"  Domain: {self.DOMAIN_X}m x {self.DOMAIN_Y}m x {self.DOMAIN_Z}m")
            print(f"  Layer interface: y={self.LAYER_INTERFACE_Y}m")
            print(f"  Antenna: y={self.ANTENNA_HEIGHT}m (above surface)")

    @staticmethod
    def _get_radii_for(material: str) -> np.ndarray:
        """Map material name to BallastSimulation sieve-based grading curve."""
        if material == 'clean_ballast':
            return BallastSimulation.get_clean_ballast_radii_distrib()
        return BallastSimulation.get_fouled_ballast_radii_distrib()

    def _generate_layer(
        self,
        phase: int,
        material: str,
        domain_height: float,
        y_offset: float,
        running_time: float,
        time_step: float,
        display: bool,
        rng: np.random.Generator,
    ) -> List[Rock]:
        """
        Generate rocks for one layer via BallastSimulation + polygonize().

        Runs physics, offsets circles into layer position, converts to
        polygon Rock objects using the inherited polygonize() helper.
        Material and optional randomization are set directly on Rock.material.
        """
        if self.verbose:
            label = 'upper' if phase == 1 else 'lower'
            print(f"Phase {phase} ({label}): BallastSimulation {self.DOMAIN_X}m x {domain_height:.3f}m ...")

        sim = BallastSimulation(
            domain_size=(self.DOMAIN_X, domain_height),
            radii_distribution=self._get_radii_for(material),
            buffer_y=0.2,
            verbose=self.verbose,
        )
        circle_array = sim.run(running_time=running_time, time_step=time_step, display=display)

        if y_offset != 0:
            circle_array[:, 1] += y_offset

        # Build Rock objects — material set per rock (random or layer material)
        rocks = []
        for x, y, radius in circle_array:
            mat = rng.choice(self.random_material_pool) if self.randomize_rock_materials else material
            rocks.append(Rock(x=float(x), y=float(y), radius=float(radius), material=mat))

        # Convert circles to polygon rocks using the shared RockPackingStrategy helper
        self.polygonize(rocks, rng=rng)
        return rocks

    def generate(
        self,
        layers: Optional[List[Layer]] = None,
        running_time: float = 3.0,
        time_step: float = PHC.GRAVITY_SETTLE_TIME_STEP,
        display: bool = False,
    ) -> None:
        """
        Generate overlapping rock layers using painter's algorithm.

        Each layer is generated independently with gravity settling.
        Layers are written to .in file in priority order (painter's algorithm):
        lower priority (drawn first) → higher priority (drawn last, appears on top).

        Args:
            layers: List of Layer objects (name, material, y_min, y_max, priority).
                   If None, uses default two-layer Mbubia setup.
            running_time: Gravity settling duration per layer (seconds)
            time_step: FDTD time step for settling
            display: Display simulation progress

        Example - Two-layer (default Mbubia, no overlap):
            gen.generate()

        Example - Three overlapping layers (painter's algorithm):
            gen.generate(layers=[
                Layer(name="subgrade", material="subgrade_soil", y_min=0.0, y_max=0.8, priority=1),
                Layer(name="fouled", material="fouled_ballast", y_min=0.4, y_max=0.9, priority=2),
                Layer(name="clean", material="clean_ballast", y_min=0.6, y_max=1.2, priority=3),
            ])
            # Result: subgrade drawn first, fouled on top of it, clean on top of fouled
            # Painter's algorithm creates visual mixing where they overlap
        """
        self._validate_configuration()

        # Use default two-layer Mbubia if no layers specified
        if layers is None:
            upper_height = self.DOMAIN_Y - self.LAYER_INTERFACE_Y
            lower_height = self.LAYER_INTERFACE_Y
            layers = [
                Layer(name="lower", material=self.lower_material, y_min=0.0, y_max=self.LAYER_INTERFACE_Y, priority=1),
                Layer(name="upper", material=self.upper_material, y_min=self.LAYER_INTERFACE_Y, y_max=self.DOMAIN_Y, priority=2),
            ]

        if self.verbose:
            print(f"Generating scene: {self.scene_name}")
            print(f"Layers: {', '.join(f'{L.name}({L.material}, priority={L.priority})' for L in sorted(layers, key=lambda L: L.priority))}")
            print(f"(Painter's algorithm: lower priority drawn first)")

        rng = np.random.default_rng()
        layer_rocks = {}

        # Generate rocks for each layer independently (no inter-layer collisions)
        for phase, layer in enumerate(sorted(layers, key=lambda L: L.priority), 1):
            rocks = self._generate_layer(
                phase=phase,
                material=layer.material,
                domain_height=layer.height,
                y_offset=layer.y_min,
                running_time=running_time,
                time_step=time_step,
                display=display,
                rng=rng,
            )
            layer_rocks[layer.name] = rocks

        # Combine rocks in priority order (painter's algorithm)
        # Lower priority rocks drawn first, higher priority rocks drawn last (on top)
        self.rocks = []
        for layer in sorted(layers, key=lambda L: L.priority):
            self.rocks.extend(layer_rocks[layer.name])

        if self.verbose:
            detail = " + ".join(f"{len(layer_rocks[L.name])} {L.name}" for L in sorted(layers, key=lambda L: L.priority))
            print(f"Final rock count: {len(self.rocks)} ({detail})")

