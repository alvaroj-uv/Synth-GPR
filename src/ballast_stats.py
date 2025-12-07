import random
import numpy as np
from typing import List, Dict, Any
from .gpr_commands import GPRCommand, BoxCommand, CylinderCommand

class BallastStatsCalculator:
    """
    Calculates accurate volume statistics for the ballast layer using Monte Carlo integration,
    respecting the Painter's Algorithm (last command wins).
    """

    @staticmethod
    def calculate_stats(commands: List[GPRCommand], 
                        domain_x: float, domain_z: float, 
                        y_min: float, y_max: float, 
                        n_samples: int = 10000) -> Dict[str, float]:
        """
        Calculate volume fractions for Rock, Fouling, and Air in the specified Y-range.
        
        Args:
            commands: List of geometry commands (should only include relevant layer commands if possible, 
                      or check bounds carefully).
            domain_x, domain_z: Domain lateral dimensions.
            y_min, y_max: Vertical range of the ballast layer.
            n_samples: Number of Monte Carlo samples.
            
        Returns:
            Dict with 'perc_rock', 'perc_fouling', 'perc_air', 'calculated_pvc'.
        """
        
        # 1. Filter commands relevant to the ballast volume
        # We perform a simple bound check to see if command affects the [y_min, y_max] region.
        # But for simplicity/correctness with Painter's, we can just check point-in-shape for ALL commands.
        # Optimization: Filter by Y-bounds overlap.
        
        relevant_cmds = []
        for cmd in commands:
            if isinstance(cmd, BoxCommand):
                # Check Y overlap
                if not (cmd.y2 <= y_min or cmd.y1 >= y_max):
                    relevant_cmds.append(cmd)
            elif isinstance(cmd, CylinderCommand):
                # Cylinders are vertical usually (y1=bottom, y2=top)
                if not (cmd.y2 <= y_min or cmd.y1 >= y_max):
                    relevant_cmds.append(cmd)
                    
        # 2. Monte Carlo Sampling
        # Generate random points (x, y, z) within the ballast box
        pts_x = np.random.uniform(0, domain_x, n_samples)
        pts_y = np.random.uniform(y_min, y_max, n_samples)
        pts_z = np.random.uniform(0, domain_z, n_samples)
        
        counts = {'rock': 0, 'fouling': 0, 'air': 0}
        
        # We need to process each point against the command stack.
        # "Painter's Algorithm": The LAST command that contains the point dictates the material.
        # Iterating BACKWARDS is efficient: find the first command hitting the point, that's the winner.
        
        # Pre-process commands for speed? 
        # For 10k samples and ~3000 rocks, this is 30M comparisons. Might be slow in pure Python.
        # Vectorization is better.
        
        # Vectorized Approach:
        # Initialize 'material_idx' array with 'air' (0).
        # Iterate commands FORWARD. For each command, update mask of points inside it.
        
        # Material IDs: 0=Air, 1=Fouling, 2=Rock
        material_map = np.zeros(n_samples, dtype=int) 
        
        for cmd in relevant_cmds:
            mat_id = 0
            if 'bal_rock' in cmd.material:
                mat_id = 2
            elif 'bal_foul' in cmd.material:
                mat_id = 1
            else:
                continue # Other materials (sleepers?) ignored or treat as air/obstruction
            
            if isinstance(cmd, BoxCommand):
                # Vectorized check
                mask = (pts_x >= cmd.x1) & (pts_x <= cmd.x2) & \
                       (pts_y >= cmd.y1) & (pts_y <= cmd.y2) & \
                       (pts_z >= cmd.z1) & (pts_z <= cmd.z2)
                material_map[mask] = mat_id
                
            elif isinstance(cmd, CylinderCommand):
                # Vertical cylinder check
                # Check Y bounds first
                mask_y = (pts_y >= cmd.y1) & (pts_y <= cmd.y2)
                # Check radius (X-Z plane distance) usually, but gprMax cylinder definition varies.
                # Standard #cylinder: x1 y1 z1 x2 y2 z2 radius
                # If axis is Y-axis (vertical): x1=x2, z1=z2.
                # Distance squared = (px - x1)^2 + (pz - z1)^2
                
                # Assuming vertical cylinders for ballast rocks
                dist_sq = (pts_x - cmd.x1)**2 + (pts_z - cmd.z1)**2 # using z1 as center? 
                # cmd.z1 is typically 0.0 for start and domain_z for end if generic.
                # Actually, rocks are vertical cylinders?
                # geometry_composer: CylinderCommand(rock.x, rock.y, 0.0, rock.x, rock.y, domain_z, radius, ...)
                # Wait, y1=rock.y, y2=rock.y? No.
                # In _generate_rocks:
                # cmd.x1 = rock.x, cmd.y1 = rock.y (Wait, Y1?), cmd.z1=0.0
                # cmd.x2 = rock.x, cmd.y2 = rock.y, cmd.z2 = domain_z
                # This defines a cylinder from Z=0 to Z=domain_z?
                # NO. gprMax cylinder is defined by two points on the axis + radius.
                # If Z1=0 and Z2=domain_z, the axis is parallel to Z.
                # So the cross section is in XY plane.
                # This means rocks are horizontal cylinders running distinct in Z? 
                # Let's re-read _generate_rocks in granular_layers.py carefully.
                
                # "CylinderCommand(rock.x, rock.y, 0.0, rock.x, rock.y, cfg.domain_z, rock.radius, ...)"
                # Axis points: (x, y, 0) and (x, y, Z_max).
                # This is a cylinder along the Z-axis.
                # So it looks like a circle in the XY plane (Front view).
                # Yes, 2D TMz simulation usually implies invariant in Z or specific structure.
                # "Mode: 2D TMz" in user request confirms 2D or 2.5D.
                # So rocks are "logs" extending through the slice.
                
                # So distance check is in (X, Y) plane? No, axis is fixed at (x, y).
                # Point P(px, py, pz).
                # Distance from line Z-axis at (cx, cy) is sqrt((px-cx)^2 + (py-cy)^2).
                
                # Wait. Input to CylinderCommand was:
                # rock.x and rock.y generated in `_generate_rocks` using `y_min` to `y_max`.
                # So `rock.y` varies vertically.
                # `rock.x` varied horizontally.
                # So the circle is indeed in the XY plane.
                # So the check is: (pts_x - cmd.x1)**2 + (pts_y - cmd.y1)**2 <= radius^2
                # AND we don't need to check pts_z overlap if it spans 0 to domain_z (which it does).
                
                dist_sq = (pts_x - cmd.x1)**2 + (pts_y - cmd.y1)**2
                mask = (dist_sq <= cmd.radius**2) 
                
                # But wait, rocks are limited in Y?
                # No, the CylinderCommand spans the FULL Z-axis (0 to domain_z).
                # But does it span finite Y?
                # The cylinder is infinite in Z (or finite 0-domain_z).
                # It is defined by `radius` around axis (x, y).
                # So it is a full "log" at that (x,y) position running through the domain dept.
                # So the "rock" is a circle in the 2D slice.
                
                material_map[mask] = mat_id

        # 3. Aggregation
        counts['air'] = np.sum(material_map == 0)
        counts['fouling'] = np.sum(material_map == 1)
        counts['rock'] = np.sum(material_map == 2)
        
        total = n_samples
        stats = {
            'perc_air': (counts['air'] / total) * 100,
            'perc_fouling': (counts['fouling'] / total) * 100,
            'perc_rock': (counts['rock'] / total) * 100,
        }
        
        # Calculated PVC = Fouling / (Fouling + Air) * 100 ? Or Volume Fraction?
        # PVC is usually Percent Void Contamination.
        # "Percentage of voids occupied by fouling".
        # Voids = Space not occupied by Rock. (Air + Fouling).
        # PVC = Fouling / (Air + Fouling) * 100.
        
        void_space = counts['air'] + counts['fouling']
        if void_space > 0:
            stats['calculated_pvc'] = (counts['fouling'] / void_space) * 100
        else:
            stats['calculated_pvc'] = 0.0
            
        return stats
