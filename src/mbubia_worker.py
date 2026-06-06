"""
MbubiaWorker — two-layer ballast scene worker for the production pipeline.

Replaces the standard Air/Subgrade/Formation/Ballast/GranularMatrix worker
chain with a direct call to MbubiaPymunkSceneGenerator, producing a
physically settled, two-layer ballast cross-section scene.

Recipe trigger: config.rock_packing_algorithm == "mbubia"

Scene structure:
  - Domain:     4.0m × 1.2m × 0.05m  (Mbubia standard)
  - Resolution: 0.002m                (1.4 GHz adequate)
  - Time window 20e-9s
  - Upper layer: clean_ballast or fouled_ballast (PVC-determined)
  - Lower layer: fouled_ballast or subgrade_soil  (PVC-determined)
  - Antenna:    monostatic at x=2.0m, y=1.5m (0.3m above surface)
"""

from typing import List, Dict, Any
from pathlib import Path

from .worker import Worker, SceneCheckpoint
from .gpr_commands import (
    BoxCommand, MaterialCommand, TriangleCommand,
    HertzianDipoleCommand, RxCommand, WaveformCommand,
)
from .pymunk_packing import MbubiaPymunkSceneGenerator
from .rock_model import Rock


# PVC thresholds for material selection
_PVC_CLEAN_MAX   = 10.0   # < 10% → clean upper layer
_PVC_FOULED_MAX  = 40.0   # 10-40% → fouled upper layer
# > 40% → highly fouled


def _select_materials(pvc: float) -> tuple[str, str]:
    """Return (upper_material, lower_material) based on PVC %."""
    if pvc < _PVC_CLEAN_MAX:
        return "clean_ballast", "fouled_ballast"
    elif pvc < _PVC_FOULED_MAX:
        return "fouled_ballast", "subgrade_soil"
    else:
        return "fouled_ballast", "highly_fouled_ballast"


class MbubiaWorker(Worker):
    """
    Generates a two-layer Mbubia ballast scene using pymunk physics.

    Completely replaces the standard layer-by-layer pipeline with a
    single physics-based scene generation step.
    """

    name = "MbubiaWorker"

    def execute(
        self,
        scene: SceneCheckpoint,
        params: Dict[str, Any],
        materials: Any,
        tools: Any,
    ) -> None:
        # Resolve PVC from work order
        pvc = 0.0
        if scene.work_order:
            pvc = scene.work_order.get_input('pvc', 0.0)
        else:
            pvc = params.get('pvc', 0.0)

        upper_material, lower_material = _select_materials(pvc)

        print(f"[{self.name}] PVC={pvc:.1f}% -> upper={upper_material}, lower={lower_material}")

        # Run MbubiaPymunkSceneGenerator (physics settling)
        BALLAST_HEIGHT = 1.2  # m — ballast-only height for BallastSimulation
        gen = MbubiaPymunkSceneGenerator(
            scene_name="pipeline",
            upper_material=upper_material,
            lower_material=lower_material,
            output_dir=Path("temp_mbubia"),  # not used; we populate checkpoint directly
            verbose=True,
            domain_x=scene.config.domain_x,
            domain_y=BALLAST_HEIGHT,   # rocks fill only the ballast region
            domain_z=0.05,             # rock polygon export (not the 2D sim z-cell)
        )
        gen.generate(running_time=2.0)

        print(f"[{self.name}] Generated {len(gen.rocks)} rocks")

        # ── Materials ────────────────────────────────────────────────────────
        for mat_name, props in gen.LAYER_PROPERTIES.items():
            scene.add_material(MaterialCommand(
                eps=props['epsilon_r'],
                sigma=props['sigma'],
                mu=1.0,
                mag_loss=0.0,
                identifier=mat_name,
            ))

        # ── Background layer boxes ────────────────────────────────────────────
        dz = scene.config.domain_z  # 2D sim: single z-cell thickness
        # Fill entire domain with upper material, then overwrite lower portion
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
        # gprMax does not support #polygon — fan-triangulate each rock polygon
        # into n #triangle commands sharing the rock centre as the apex.
        import math
        dx, dy = gen.DOMAIN_X, BALLAST_HEIGHT
        for rock in gen.rocks:
            # Clamp vertices to domain — polygon noise can push them outside
            raw   = rock['vertices']
            verts = [(max(0.0, min(v[0], dx)), max(0.0, min(v[1], dy))) for v in raw]
            n     = len(verts)
            xs    = [v[0] for v in verts]
            ys    = [v[1] for v in verts]
            cx    = sum(xs) / n
            cy    = sum(ys) / n
            for i in range(n):
                v1 = verts[i]
                v2 = verts[(i + 1) % n]
                scene.add_geometry(TriangleCommand(
                    cx,    cy,    0.0,
                    v1[0], v1[1], 0.0,
                    v2[0], v2[1], 0.0,
                    dz,
                    rock['material'],
                ))
            r = math.sqrt(sum((x-cx)**2+(y-cy)**2 for x,y in zip(xs,ys)) / n)
            scene.add_rock(Rock(x=cx, y=cy, radius=r, z_start=0.0, z_end=dz))

        # ── Antenna (monostatic, centred, 0.3m above surface) ─────────────────
        ant_x = scene.config.tx_x  # centred on the actual domain width
        ant_y = gen.ANTENNA_HEIGHT
        ant_z = dz / 2
        freq  = scene.config.center_freq  # honour --freq flag

        scene.add_geometry(WaveformCommand("ricker", 1, freq, "mbubia_wave"))
        scene.add_source(HertzianDipoleCommand("z", ant_x, ant_y, ant_z, "mbubia_wave"))
        scene.add_receiver(RxCommand(ant_x, ant_y, ant_z))

        # ── Metadata ──────────────────────────────────────────────────────────
        scene.metadata.update({
            'pvc': pvc,
            'mbubia_scene': True,
            'upper_material': upper_material,
            'lower_material': lower_material,
            'layer_interface_y': gen.LAYER_INTERFACE_Y,
            'n_rocks': len(gen.rocks),
            'center_freq_hz': freq,
            'freq_mhz': freq / 1e6,
        })

    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        errors = []
        rock_cmds = [c for c in scene.geometry if isinstance(c, TriangleCommand)]
        if not rock_cmds:
            errors.append(f"{self.name}: No polygon rocks generated")
        if not scene.sources:
            errors.append(f"{self.name}: No antenna source configured")
        return errors
