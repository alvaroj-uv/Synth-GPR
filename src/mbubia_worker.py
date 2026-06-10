"""
MbubiaWorker — two-layer ballast scene worker for the production pipeline.

Replaces the standard Air/Subgrade/Formation/Ballast/GranularMatrix worker
chain with a direct call to MbubiaPymunkSceneGenerator, producing a
physically settled, two-layer ballast cross-section scene.

Recipe trigger: config.rock_packing_algorithm == "mbubia"
"""

from typing import List, Dict, Any

from .worker import Worker, SceneCheckpoint
from .gpr_commands import (
    BoxCommand, MaterialCommand, TriangleCommand,
    HertzianDipoleCommand, RxCommand, WaveformCommand,
)
from .pymunk_packing import MbubiaPymunkSceneGenerator
from .rock_model import Rock
from .constants import MC

# EM material properties — single source of truth is MC (constants.py).
# MbubiaWorker owns the EM setup; pymunk_packing only handles geometry.
LAYER_PROPERTIES = {
    'clean_ballast':         {'epsilon_r': MC.CLEAN_BALLAST_PROPS[0],  'sigma': MC.CLEAN_BALLAST_PROPS[1],  'density': 2650},
    'fouled_ballast':        {'epsilon_r': MC.FOULED_BALLAST_PROPS[0], 'sigma': MC.FOULED_BALLAST_PROPS[1], 'density': 2500},
    'highly_fouled_ballast': {'epsilon_r': MC.HF_BALLAST_PROPS[0],     'sigma': MC.HF_BALLAST_PROPS[1],     'density': 2400},
    'subgrade_soil':         {'epsilon_r': MC.SUBGRADE_SOIL_PROPS[0],  'sigma': MC.SUBGRADE_SOIL_PROPS[1],  'density': 2200},
}


class MbubiaWorker(Worker):
    """
    Generates a two-layer Mbubia ballast scene using pymunk physics.

    Completely replaces the standard layer-by-layer pipeline with a
    single physics-based scene generation step.
    """

    name = "MbubiaWorker"

    # Ballast geometry — Mbubia standard (Mbubia et al. 2026)
    _BALLAST_HEIGHT       = 1.2    # m — total ballast column height
    _LAYER_INTERFACE_Y    = 0.488  # m — nominal sharp upper/lower boundary
    _MIXING_FRACTION      = 0.20   # lower 20% of upper layer mixes with lower material
    # domain_z for BallastSimulation is the polygon export thickness, NOT the
    # 2D FDTD z-cell size. 0.05m gives BallastSimulation a realistic slab depth
    # for internal calculations; the actual sim z-cell comes from scene.config.domain_z.
    _ROCK_EXPORT_DOMAIN_Z = 0.05

    # PVC thresholds for upper/lower material selection
    _PVC_CLEAN_MAX  = 10.0   # < 10%  → clean_ballast / fouled_ballast
    _PVC_FOULED_MAX = 40.0   # 10–40% → fouled_ballast / subgrade_soil
                              # > 40%  → fouled_ballast / highly_fouled_ballast

    @staticmethod
    def _select_materials(pvc: float) -> tuple[str, str]:
        """Return (upper_material, lower_material) based on PVC %."""
        if pvc < MbubiaWorker._PVC_CLEAN_MAX:
            return "clean_ballast", "fouled_ballast"
        elif pvc < MbubiaWorker._PVC_FOULED_MAX:
            return "fouled_ballast", "subgrade_soil"
        else:
            return "fouled_ballast", "highly_fouled_ballast"

    def execute(
        self,
        scene: SceneCheckpoint,
        params: Dict[str, Any],
        materials: Any,
        tools: Any,
    ) -> None:
        # Resolve PVC from work order
        pvc = scene.work_order.get_input('pvc', 0.0) if scene.work_order else params.get('pvc', 0.0)
        upper_material, lower_material = self._select_materials(pvc)

        print(f"[{self.name}] PVC={pvc:.1f}% -> upper={upper_material}, lower={lower_material}")

        # Compute mixing-zone interface: lower 20% of upper layer overlaps lower material
        upper_layer_height = self._BALLAST_HEIGHT - self._LAYER_INTERFACE_Y
        interface_y = self._LAYER_INTERFACE_Y - upper_layer_height * self._MIXING_FRACTION

        gen = MbubiaPymunkSceneGenerator(
            scene_name="pipeline",
            upper_material=upper_material,
            lower_material=lower_material,
            output_dir=None,                         # no file export; checkpoint populated directly
            verbose=True,
            domain_x=scene.config.domain_x,
            domain_y=self._BALLAST_HEIGHT,
            domain_z=self._ROCK_EXPORT_DOMAIN_Z,
            layer_interface_y=interface_y,
            randomize_rock_materials=scene.config.randomize_rock_materials,
            random_material_pool=list(LAYER_PROPERTIES.keys()),
        )
        gen.generate(running_time=2.0)

        print(f"[{self.name}] Generated {len(gen.rocks)} rocks")

        # ── Materials ────────────────────────────────────────────────────────
        for mat_name, props in LAYER_PROPERTIES.items():
            scene.add_material(MaterialCommand(
                eps=props['epsilon_r'],
                sigma=props['sigma'],
                mu=1.0,
                mag_loss=0.0,
                identifier=mat_name,
            ))

        # ── Background layer boxes (painter's algorithm base) ─────────────────
        dz = scene.config.domain_z
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            gen.DOMAIN_X, gen.DOMAIN_Y, dz,
            upper_material,
        ))
        scene.add_geometry(BoxCommand(
            0, 0, 0,
            gen.DOMAIN_X, gen.LAYER_INTERFACE_Y, dz,
            lower_material,
        ))

        # ── Rocks as fan-triangulated TriangleCommands ────────────────────────
        # gprMax does not support #polygon — fan-triangulate each polygon Rock
        # into n triangles sharing the clamped centroid as apex.
        dx, dy = gen.DOMAIN_X, self._BALLAST_HEIGHT
        for rock in gen.rocks:
            # Clamp vertices to domain bounds
            verts = [(max(0.0, min(v[0], dx)), max(0.0, min(v[1], dy))) for v in rock.vertices]
            # Recompute centroid from clamped vertices — not original rock.centroid,
            # which may lie outside the clamped polygon for edge rocks.
            n  = len(verts)
            cx = sum(v[0] for v in verts) / n
            cy = sum(v[1] for v in verts) / n
            for i in range(n):
                v1 = verts[i]
                v2 = verts[(i + 1) % n]
                scene.add_geometry(TriangleCommand(
                    cx,    cy,    0.0,
                    v1[0], v1[1], 0.0,
                    v2[0], v2[1], 0.0,
                    dz,
                    rock.material,
                ))
            scene.add_rock(Rock(x=cx, y=cy, radius=rock.radius, z_start=0.0, z_end=dz))

        # ── Antenna (monostatic, centred, 0.3m above surface) ─────────────────
        ant_x = scene.config.tx_x
        ant_y = gen.ANTENNA_HEIGHT
        ant_z = dz / 2
        freq  = scene.config.center_freq

        scene.add_geometry(WaveformCommand("ricker", 1, freq, "mbubia_wave"))
        scene.add_source(HertzianDipoleCommand("z", ant_x, ant_y, ant_z, "mbubia_wave"))
        scene.add_receiver(RxCommand(ant_x, ant_y, ant_z))

        # ── Metadata ──────────────────────────────────────────────────────────
        scene.metadata.update({
            'pvc':               pvc,
            'mbubia_scene':      True,
            'upper_material':    upper_material,
            'lower_material':    lower_material,
            'layer_interface_y': gen.LAYER_INTERFACE_Y,
            'n_rocks':           len(gen.rocks),
            'center_freq_hz':    freq,
            'freq_mhz':          freq / 1e6,
        })

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        errors = []
        if not any(isinstance(c, TriangleCommand) for c in scene.geometry):
            errors.append(f"{self.name}: No polygon rocks generated")
        if not scene.sources:
            errors.append(f"{self.name}: No antenna source configured")
        return errors
