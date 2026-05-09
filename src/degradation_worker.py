"""
Ballast Degradation Worker - Simulates realistic particle breakage and fines migration.

Based on railway ballast degradation literature:
- Larger particles (>40mm) have higher breakage probability
- Fine particles (<10mm) migrate downward through voids
- Fines accumulate in bottom 30% of ballast layer
"""

from typing import List, Dict, Any
import random
import numpy as np
from .worker import Worker, SceneCheckpoint
from .rock_model import Rock
from .gpr_commands import CylinderCommand


class DegradationWorker(Worker):
    """
    Simulates ballast degradation over time.
    
    Mechanisms:
    1. Particle breakage (larger rocks → smaller fragments)
    2. Fines migration (small particles settle to bottom)
    
    This models the time-dependent degradation process observed in railway ballast,
    not the initial design state.
    """
    name = "DegradationWorker"
    
    def execute(self, scene: SceneCheckpoint, params: Dict[str, Any], materials: Any, tools: Any) -> None:
        # Get degradation level (0-100%)
        degradation_level = params.get('degradation_level', 0.0)
        
        if scene.work_order:
            degradation_level = scene.work_order.get_input('degradation_level', degradation_level)
        
        scene.metadata['degradation_level'] = degradation_level
        
        if degradation_level <= 0:
            print(f"[{self.name}] No degradation (fresh ballast)")
            return  # Fresh ballast, no degradation
        
        # Get existing rocks directly from the scene
        if not scene.rock_positions:
            scene.log_issue(self.name, "missing_dependency", "error", "No rocks found in scene.")
            return

        # Get ballast bounds
        start_y = scene.work_order.get('ballast_bottom_y', 0.5)
        ballast_thickness = scene.work_order.get('ballast_thickness', 0.4)
        top_y = start_y + ballast_thickness
        
        domain_x, _, domain_z = scene.get_domain_params()
        
        # Get Z extent
        z_start = scene.config.rock_z_start
        z_end = scene.config.rock_z_end
        if scene.work_order:
            z_start = scene.work_order.get_input('rock_z_start', z_start)
            z_end = scene.work_order.get_input('rock_z_end', z_end)
        
        print(f"[{self.name}] Simulating degradation (level={degradation_level:.1f}%)")
        
        # 1. Simulate particle breakage
        broken_rocks, fines = self._simulate_breakage(
            scene.rock_positions, degradation_level, scene.config
        )
        
        # 2. Migrate fines to bottom zone
        fines_zone_height = ballast_thickness * scene.config.fines_accumulation_zone
        fines_zone_top = start_y + fines_zone_height
        
        migrated_fines = self._migrate_fines_to_bottom(
            fines, start_y, fines_zone_top, domain_x, domain_z, z_start, z_end
        )
        
        # 3. Add broken rocks and migrated fines to scene
        for rock in broken_rocks:
            cmd = CylinderCommand(
                rock.x, rock.y, z_start,
                rock.x, rock.y, z_end,
                rock.radius, "bal_rock"
            )
            scene.add_geometry(cmd)
            scene.add_rock(rock)

        for fine in migrated_fines:
            cmd = CylinderCommand(
                fine.x, fine.y, z_start,
                fine.x, fine.y, z_end,
                fine.radius, "bal_rock"
            )
            scene.add_geometry(cmd)
            scene.add_rock(fine)
        
        # Update metadata
        scene.metadata['degradation_broken_count'] = len(broken_rocks)
        scene.metadata['degradation_fines_count'] = len(migrated_fines)
        
        print(f"[{self.name}] Generated {len(broken_rocks)} broken fragments, {len(migrated_fines)} migrated fines")
    
    def _simulate_breakage(self, rock_positions: List[Rock], degradation_level: float,
                           config: Any) -> tuple[List[Rock], List[Rock]]:
        """
        Simulate particle breakage based on size and degradation level.
        
        Returns:
            (broken_rocks, fines): Fragments from breakage and fine particles
        """
        degradation_fraction = degradation_level / 100.0
        
        # Breakage probabilities from config
        prob_large = config.breakage_probability_large * degradation_fraction
        prob_medium = config.breakage_probability_medium * degradation_fraction
        
        broken_rocks = []
        fines = []
        
        for rock in rock_positions:
            # Determine breakage probability based on size
            # Literature: larger particles (>40mm) more susceptible to breakage
            if rock.radius > 0.020:  # >40mm diameter
                breakage_prob = prob_large
            elif rock.radius > 0.010:  # 20-40mm diameter
                breakage_prob = prob_medium
            else:
                breakage_prob = 0.0  # Small particles don't break further
            
            # Roll for breakage
            if random.random() < breakage_prob:
                # Generate 2-4 smaller fragments
                num_fragments = random.randint(2, 4)
                
                for _ in range(num_fragments):
                    # Fragment size: 30-60% of original
                    fragment_radius = rock.radius * random.uniform(0.3, 0.6)
                    
                    # Position near original rock (small scatter)
                    scatter = rock.radius * 0.5
                    fragment_x = rock.x + random.uniform(-scatter, scatter)
                    fragment_y = rock.y + random.uniform(-scatter, scatter)
                    
                    fragment = Rock(
                        x=fragment_x,
                        y=fragment_y,
                        radius=fragment_radius,
                        z_start=rock.z_start,
                        z_end=rock.z_end
                    )
                    
                    # Classify as fine or broken rock
                    if fragment_radius < config.fines_threshold:
                        fines.append(fragment)
                    else:
                        broken_rocks.append(fragment)
        
        return broken_rocks, fines
    
    def _migrate_fines_to_bottom(self, fines: List[Rock], y_min: float, y_max: float,
                                 domain_x: float, domain_z: float,
                                 z_start: float, z_end: float) -> List[Rock]:
        """
        Migrate fine particles to bottom zone of ballast.
        
        Simulates gravity settling and vibration-induced migration.
        """
        migrated = []
        
        for fine in fines:
            # Redistribute fines uniformly in bottom zone
            new_x = random.uniform(0, domain_x)
            new_y = random.uniform(y_min, y_max)
            
            migrated_fine = Rock(
                x=new_x,
                y=new_y,
                radius=fine.radius,
                z_start=z_start,
                z_end=z_end
            )
            migrated.append(migrated_fine)
        
        return migrated
    
    def quality_check(self, scene: SceneCheckpoint) -> List[str]:
        """Quality checks for degradation simulation."""
        errors = []
        
        degradation_level = scene.metadata.get('degradation_level', 0.0)
        
        if degradation_level > 0:
            # Check that degradation actually produced results
            broken_count = scene.metadata.get('degradation_broken_count', 0)
            fines_count = scene.metadata.get('degradation_fines_count', 0)
            
            if broken_count == 0 and fines_count == 0:
                errors.append(f"DegradationWorker: No degradation products generated despite level={degradation_level}")
        
        return errors
