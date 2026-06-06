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
from typing import List, Optional, Tuple, Dict

from .constants import PHC

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

class MbubiaPymunkSceneGenerator:
    """
    Two-layer Mbubia railway ballast scene generator.

    Delegates physics (RSA + gravity compaction) to BallastSimulation per layer,
    then converts settled circle positions to polygon vertex geometry.

    This avoids duplicating simulation logic and ensures correct gravity scaling,
    proper sieve-based grading curves, and consistent void fraction targeting.
    """

    DOMAIN_X = 4.0
    DOMAIN_Y = 1.2
    DOMAIN_Z = 0.05
    ANTENNA_HEIGHT_ABOVE_SURFACE = 0.30
    CENTER_FREQUENCY_GHZ = 1.4
    LAYER_INTERFACE_Y = 0.488

    LAYER_PROPERTIES = {
        'clean_ballast':        {'epsilon_r': 4.10, 'sigma': 0.001, 'density': 2650},
        'fouled_ballast':       {'epsilon_r': 4.23, 'sigma': 0.005, 'density': 2500},
        'highly_fouled_ballast':{'epsilon_r': 4.35, 'sigma': 0.008, 'density': 2400},
        'subgrade_soil':        {'epsilon_r': 5.50, 'sigma': 0.010, 'density': 2200},
    }

    @property
    def ANTENNA_HEIGHT(self):
        return self.DOMAIN_Y + self.ANTENNA_HEIGHT_ABOVE_SURFACE

    def __init__(
        self,
        scene_name: str,
        upper_material: str = "clean_ballast",
        lower_material: str = "fouled_ballast",
        output_dir: Path = Path("output/mbubia_pymunk"),
        verbose: bool = True,
        domain_x: Optional[float] = None,
        domain_y: Optional[float] = None,
        domain_z: Optional[float] = None,
    ):
        self.scene_name = scene_name
        self.upper_material = upper_material
        self.lower_material = lower_material
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        self.rocks: List[dict] = []
        # Allow per-instance domain override (used by MbubiaWorker from pipeline config)
        if domain_x is not None:
            self.DOMAIN_X = domain_x
        if domain_y is not None:
            self.DOMAIN_Y = domain_y
        if domain_z is not None:
            self.DOMAIN_Z = domain_z

    def _validate_configuration(self) -> None:
        errors = []
        if self.ANTENNA_HEIGHT <= self.DOMAIN_Y:
            errors.append(
                f"Antenna height ({self.ANTENNA_HEIGHT}m) must be above domain top ({self.DOMAIN_Y}m). "
                f"= domain_y({self.DOMAIN_Y}m) + height_above_surface({self.ANTENNA_HEIGHT_ABOVE_SURFACE}m)"
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
        else:
            # fouled_ballast, highly_fouled_ballast, subgrade_soil → fouled curve
            return BallastSimulation.get_fouled_ballast_radii_distrib()

    @staticmethod
    def _circles_to_polygon_dicts(
        rocks_array: np.ndarray,
        material: str,
        rng: np.random.Generator,
    ) -> List[dict]:
        """Convert BallastSimulation circle output to polygon vertex dicts."""
        rocks = []
        for x, y, radius in rocks_array:
            n_sides = int(rng.integers(6, 13))
            angles = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
            # 0.35 amplitude gives clearly visible angular shapes at scene scale
            noise = rng.uniform(-0.35, 0.35, n_sides)
            vertices = [
                (x + (radius + radius * noise[i]) * np.cos(angles[i]),
                 y + (radius + radius * noise[i]) * np.sin(angles[i]))
                for i in range(n_sides)
            ]
            rocks.append({'x': float(x), 'y': float(y), 'vertices': vertices,
                          'material': material, 'n_sides': n_sides})
        return rocks

    def generate(
        self,
        running_time: float = 3.0,
        time_step: float = PHC.GRAVITY_SETTLE_TIME_STEP,
        display: bool = False,
    ) -> None:
        """Generate Mbubia scene: physics via BallastSimulation, geometry as polygons."""
        self._validate_configuration()

        if self.verbose:
            print(f"Generating Mbubia scene: {self.scene_name}")
            print(f"Upper layer: {self.upper_material}  Lower layer: {self.lower_material}")

        rng = np.random.default_rng()

        upper_height = self.DOMAIN_Y - self.LAYER_INTERFACE_Y
        lower_height = self.LAYER_INTERFACE_Y

        if self.verbose:
            print(f"Phase 1 (upper): BallastSimulation {self.DOMAIN_X}m x {upper_height:.3f}m ...")
        upper_sim = BallastSimulation(
            domain_size=(self.DOMAIN_X, upper_height),
            radii_distribution=self._get_radii_for(self.upper_material),
            buffer_y=0.2,
            verbose=self.verbose,
        )
        upper_array = upper_sim.run(running_time=running_time, time_step=time_step, display=display)
        upper_array[:, 1] += self.LAYER_INTERFACE_Y  # offset y into upper layer position

        if self.verbose:
            print(f"Phase 2 (lower): BallastSimulation {self.DOMAIN_X}m x {lower_height:.3f}m ...")
        lower_sim = BallastSimulation(
            domain_size=(self.DOMAIN_X, lower_height),
            radii_distribution=self._get_radii_for(self.lower_material),
            buffer_y=0.2,
            verbose=self.verbose,
        )
        lower_array = lower_sim.run(running_time=running_time, time_step=time_step, display=display)

        self.rocks = (
            self._circles_to_polygon_dicts(upper_array, self.upper_material, rng) +
            self._circles_to_polygon_dicts(lower_array, self.lower_material, rng)
        )

        if self.verbose:
            print(f"Final rock count: {len(self.rocks)} ({len(upper_array)} upper + {len(lower_array)} lower)")

    def export_gprmax_in(self) -> Path:
        """Export scene to gprMax .in format."""
        output_file = self.output_dir / f"mbubia_pymunk_{self.scene_name}.in"
        upper_props = self.LAYER_PROPERTIES[self.upper_material]
        lower_props = self.LAYER_PROPERTIES[self.lower_material]

        content = f"""#title: Mbubia Pymunk Scene - {self.scene_name.upper()}
#domain: {self.DOMAIN_X:.3f} {self.DOMAIN_Y:.3f} {self.DOMAIN_Z:.3f}
#dx_dy_dz: 0.002 0.002 0.001
#time_window: 20e-9

# === MBUBIA SCENE WITH PYMUNK ===
# Generated with pymunk physics engine
# Upper layer: {self.upper_material} (er={upper_props['epsilon_r']}, s={upper_props['sigma']})
# Lower layer: {self.lower_material} (er={lower_props['epsilon_r']}, s={lower_props['sigma']})
# Rocks: {len(self.rocks)} polygon shapes (realistic geometry)

# === MATERIALS ===
#material: {upper_props['epsilon_r']} {upper_props['sigma']} 1.0 0.0 {self.upper_material}
#material: {lower_props['epsilon_r']} {lower_props['sigma']} 1.0 0.0 {self.lower_material}
#material: 5.50 0.010 1.0 0.0 subgrade_soil

# === ANTENNA (MONOSTATIC) ===
#hertzian_dipole: z {self.DOMAIN_X/2:.2f} {self.ANTENNA_HEIGHT:.2f} 0 myricker
#rx: {self.DOMAIN_X/2:.2f} {self.ANTENNA_HEIGHT:.2f} 0

# === WAVEFORM ===
#waveform: ricker 1 {self.CENTER_FREQUENCY_GHZ*1e9:.0f} myricker

# === DOMAIN MATERIAL ===
#box: 0 0 0 {self.DOMAIN_X:.3f} {self.DOMAIN_Y:.3f} {self.DOMAIN_Z:.3f} {self.upper_material}

# === LAYER BOUNDARIES ===
#box: 0 0 0 {self.DOMAIN_X:.3f} {self.LAYER_INTERFACE_Y:.3f} {self.DOMAIN_Z:.3f} {self.lower_material}

# === ROCK GEOMETRY (Pymunk-generated polygons) ===
"""

        for rock in self.rocks:
            vertices = rock['vertices']
            verts_str = ' '.join([f"{v[0]:.4f} {v[1]:.4f} 0" for v in vertices])
            content += f"#polygon: {len(vertices)} {verts_str} {rock['material']}\n"

        content += "\n# === SIMULATION ===\n#run_simulation\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        if self.verbose:
            print(f"Exported to {output_file}")

        return output_file

    def export_json(self) -> Path:
        """Export scene data as JSON."""
        output_file = self.output_dir / f"mbubia_pymunk_{self.scene_name}.json"

        data = {
            'scene_name': self.scene_name,
            'upper_material': self.upper_material,
            'lower_material': self.lower_material,
            'layer_interface_y': self.LAYER_INTERFACE_Y,
            'domain': {'x': self.DOMAIN_X, 'y': self.DOMAIN_Y, 'z': self.DOMAIN_Z},
            'antenna_height': float(self.ANTENNA_HEIGHT),
            'antenna_height_above_surface': self.ANTENNA_HEIGHT_ABOVE_SURFACE,
            'frequency_ghz': self.CENTER_FREQUENCY_GHZ,
            'n_rocks': len(self.rocks),
            'rocks': self.rocks,
            'material_properties': self.LAYER_PROPERTIES,
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        if self.verbose:
            print(f"Exported to {output_file}")

        return output_file

    def export_png(self) -> Path:
        """Render scene to PNG via the dedicated Mbubia visualizer."""
        from scripts.visualization.mbubia_visualizer import render_mbubia_pymunk_scene
        in_file = self.output_dir / f"mbubia_pymunk_{self.scene_name}.in"
        out_png = self.output_dir / f"mbubia_pymunk_{self.scene_name}.png"
        return render_mbubia_pymunk_scene(
            in_path=in_file,
            output_png=out_png,
            upper_material=self.upper_material,
            lower_material=self.lower_material,
            layer_interface_y=self.LAYER_INTERFACE_Y,
        )
