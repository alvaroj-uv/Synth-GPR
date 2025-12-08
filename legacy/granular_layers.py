import random
from .config import GeneratorConfig, topp_mixing_model
from .scene_descriptor import LayerResult
from .scene_graph import LeafLayer, CompositeNode, BuildContext
from .gpr_commands import Header, BoxCommand, CylinderCommand, MaterialCommand
from .rock_packing import RockPackingStrategy, PoissonDiskPacking, PackingBounds
from .ballast_stats import BallastStatsCalculator

# Alias for backward compatibility / cleanliness
Layer = LeafLayer
SETTLED_FOULING_FRACTION = 0.7
DISPERSED_FOULING_FRACTION = 0.3
TARGET_ROCK_FILL_RATIO = 0.6
NUM_ROCK_LAYERS = 3
MAX_ROCK_PLACEMENT_ATTEMPTS = 1000
BASE_PARTICLE_COUNT_PER_100_PVC = 50
PARTICLE_ATTEMPT_MULTIPLIER = 5
MIN_FOULING_PARTICLE_SIZE = 0.002
MAX_FOULING_PARTICLE_SIZE = 0.008

class SettledFoulingLayer(Layer):
    """
    Generates the gravity-settled fouling layer at the bottom of the ballast.
    """
    def __init__(self, pvc: float):
        super().__init__("SettledFouling")
        self.pvc = pvc

    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        # Note: We need access to ballast_thickness and fouling_height which are dynamic.
        # We can expect them in config? No, they are per-instance random.
        # We must rely on 'ctx.params' injected by the parent Composite.
        # BUT this adapter signature _apply_layer_logic(config, start_y) hides ctx!
        # We should OVERRIDE _generate(ctx) instead of using the adapter if we need ctx.params.
        pass

    def _generate(self, ctx: BuildContext) -> LayerResult:
        res = LayerResult()
        
        # Read parameters from context (set by parent GranularBallastLayer)
        if 'fouling_height' not in ctx.params:
             # Fallback or strict error? 
             # For robustness, if not present, assume 0
             return res

        fouling_height = ctx.params['fouling_height']
        
        # Increase threshold to avoid extremely thin layers (< 1 cell)
        if fouling_height < ctx.config.dy:
            return res
        
        res.geometry.append(Header(f"Fouling: Gravity-Settled Distribution (PVC={self.pvc:.1f}%)"))
        
        settled_height = fouling_height * SETTLED_FOULING_FRACTION
        if settled_height < 1e-6:
             return res
             
        foul_horizon_y = ctx.current_y + settled_height
        
        # Constraint check
        if foul_horizon_y <= ctx.current_y:
            foul_horizon_y = ctx.current_y + 1e-5
        
        res.geometry.append(Header("- Settled Layer (bottom)"))
        res.geometry.append(BoxCommand(0.0, ctx.current_y, 0.0, ctx.config.domain_x, foul_horizon_y, ctx.config.domain_z, "bal_foul_granular"))
        
        # Export metadata for siblings
        res.metadata.update({
            'dispersed_enabled': True,
            'dispersed_y_min': foul_horizon_y,
            'dispersed_y_max': ctx.current_y + fouling_height,
        })
        
        # IMPORTANT: Does settled fouling raise the "base" for rocks?
        # Usually rocks sit ON TOP of subgrade/formation, possibly mingling with fouling.
        # If we return top_y, the next layer (Rocks) starts there.
        # But rocks usually span the whole ballast thickness.
        # So we should probably NOT return a top_y that shifts the context cursor, OR parent handles it.
        # Let's say settled layer is an underlay. Rocks start at start_y anyway?
        # Actually, rocks are placed in `_create_rock_layers` referencing `start_y` (bottom of ballast).
        # So rocks overlap settled fouling.
        # Thus, we do NOT advance ctx.current_y (or we return 0/same).
        
        return res

class RockAggregateLayer(Layer):
    """
    Generates the main rock aggregates using a packing strategy.
    """
    def __init__(self, packing_strategy: RockPackingStrategy):
        super().__init__("RockAggregates")
        self.packing_strategy = packing_strategy or PoissonDiskPacking()

    def _generate(self, ctx: BuildContext) -> LayerResult:
        res = LayerResult()
        
        ballast_thickness = ctx.params.get('ballast_thickness', 0.4) # Default fallback
        start_y = ctx.current_y
        
        res.geometry.append(Header("Granular Aggregates"))
        
        # Generation Logic
        commands = []
        total_rocks = 0
        rock_list_for_meta = []
        
        n_layers = NUM_ROCK_LAYERS
        layer_height = ballast_thickness / n_layers
        radius_step = (ctx.config.rock_radius_max - ctx.config.rock_radius_min) / n_layers
        
        for i in range(n_layers):
            y_min = start_y + i * layer_height
            y_max = start_y + (i + 1) * layer_height
            
            # 100% overlap with previous layer to ensure dense packing
            if i > 0:
                y_min -= layer_height
            
            radius_min = ctx.config.rock_radius_min + i * radius_step
            radius_max = radius_min + radius_step
            
            # Use strategy
            bounds = PackingBounds(0.0, ctx.config.domain_x, y_min, y_max)
            rocks = self.packing_strategy.generate_rocks(
                bounds, radius_min, radius_max, 
                TARGET_ROCK_FILL_RATIO, MAX_ROCK_PLACEMENT_ATTEMPTS
            )
            
            # Convert
            for rock in rocks:
                commands.append(CylinderCommand(
                    rock.x, rock.y, 0.0,
                    rock.x, rock.y, ctx.config.domain_z,
                    rock.radius, "bal_rock"
                ))
                rock_list_for_meta.append({'x': rock.x, 'y': rock.y, 'radius': rock.radius})
                
            total_rocks += len(rocks)
            
        res.geometry.extend(commands)
        
        # Share rock positions for DispersedFouling
        ctx.params['rock_list'] = rock_list_for_meta
        res.metadata['rock_count'] = total_rocks
        
        # Rocks define the top of the ballast layer effectively
        res.top_y = start_y + ballast_thickness
        
        return res

class DispersedFoulingLayer(Layer):
    """
    Generates dispersed fouling particles in the voids between rocks.
    """
    def __init__(self, pvc: float):
        super().__init__("DispersedFouling")
        self.pvc = pvc

    def _generate(self, ctx: BuildContext) -> LayerResult:
        res = LayerResult()
        
        # Dependencies
        if 'rock_list' not in ctx.params:
            return res
            
        rock_list = ctx.params['rock_list']
        
        # Metadata from SettledFouling?
        # Or recalculate/params?
        # Settled layer set metadata `dispersed_y_min`.
        # But `SceneNode.build` merges metadata into `result`, not `ctx` automatically unless parent does it.
        # Parent Composite updates `result.metadata`.
        # `ctx.metadata` is shared?
        # `BuildContext` definition has `metadata` field.
        # Check `CompositeNode.build`:
        # `combined_result.metadata.update(child_result.metadata)`
        # It does NOT update `ctx.metadata`.
        # However, `SettledFoulingLayer` *should* probably stick it in `ctx.params` if it wants to pass to sibling.
        # Or `DispersedFoulingLayer` should calculate it itself.
        # Let's use `ctx.params` for passing data between siblings if orchestrated by parent.
        
        # Re-calc simply using params for safety
        if 'fouling_height' not in ctx.params: return res
        
        fouling_height = ctx.params['fouling_height']
        settled_height = fouling_height * SETTLED_FOULING_FRACTION
        
        y_min = ctx.current_y + settled_height
        y_max = ctx.current_y + fouling_height
        
        # Generate
        cmds = []
        target_count = int(BASE_PARTICLE_COUNT_PER_100_PVC * (self.pvc / 100.0))
        
        if target_count > 0:
            res.geometry.append(Header("- Dispersed Particles (upper voids)"))
            
            max_attempts = target_count * PARTICLE_ATTEMPT_MULTIPLIER
            placed_count = 0
            
            for _ in range(max_attempts):
                if placed_count >= target_count: break
                
                x = random.uniform(0, ctx.config.domain_x)
                y = random.uniform(y_min, y_max)
                r = random.uniform(MIN_FOULING_PARTICLE_SIZE, MAX_FOULING_PARTICLE_SIZE)
                
                in_void = True
                for rock in rock_list:
                    dist_sq = (x - rock['x'])**2 + (y - rock['y'])**2
                    if dist_sq <= (rock['radius'] + r + 0.001)**2:
                        in_void = False
                        break
                
                if in_void:
                    cmds.append(CylinderCommand(x, y, 0.0, x, y, ctx.config.domain_z, r, "bal_foul_granular"))
                    placed_count += 1
                    
            res.geometry.extend(cmds)
            res.metadata['dispersed_particle_count'] = placed_count
            
        return res

# Redefine GranularBallastLayer as a Composite
class GranularBallastLayer(CompositeNode):
    """
    Composite Layer combining Settled Fouling, Rock Aggregates, and Dispersed Fouling.
    """
    def __init__(self, materials_repo, pvc: float, moisture: float, packing_strategy: RockPackingStrategy = None):
        super().__init__("GranularBallast")
        self.materials_repo = materials_repo # Unused?
        self.pvc = pvc
        self.moisture = moisture
        self.packing_strategy = packing_strategy
        
        # Add children
        self.add(SettledFoulingLayer(pvc))
        self.add(RockAggregateLayer(packing_strategy))
        self.add(DispersedFoulingLayer(pvc))

    def _compute_material_properties(self, config: GeneratorConfig) -> dict:
        # Legacy logic preserved
        if config.enable_domain_randomization:
            moisture = random.uniform(0, config.moisture_randomization_range)
            rock_eps = config.bal_rock_eps * random.uniform(1 - config.rock_eps_variation, 1 + config.rock_eps_variation)
            rock_sigma = config.bal_rock_sigma * random.uniform(1 - config.rock_sigma_variation, 1 + config.rock_sigma_variation)
        else:
            moisture = self.moisture
            rock_eps = config.bal_rock_eps
            rock_sigma = config.bal_rock_sigma
        
        return {
            'rock_eps': rock_eps, 'rock_sigma': rock_sigma,
            'foul_eps': topp_mixing_model(moisture), 'foul_sigma': 0.001 + 0.2 * moisture
        }

    def build(self, ctx: BuildContext) -> LayerResult:
        # Override to manage shared state (thickness, materials)
        
        # sample thickness
        ballast_thickness = random.uniform(ctx.config.min_ballast_thickness, ctx.config.max_ballast_thickness)
        pvc_fraction = min(max(self.pvc, 0), 100) / 100.0
        fouling_height = ballast_thickness * pvc_fraction
        
        # Inject into params for children
        ctx.params['ballast_thickness'] = ballast_thickness
        ctx.params['fouling_height'] = fouling_height
        
        # Compute materials
        props = self._compute_material_properties(ctx.config)
        
        # Build children
        result = super().build(ctx)
        
        # Add materials commands
        result.materials.append(MaterialCommand(props['rock_eps'], props['rock_sigma'], 1, 0, "bal_rock"))
        result.materials.append(MaterialCommand(props['foul_eps'], props['foul_sigma'], 1, 0, "bal_foul_granular"))
        
        # Add metadata
        result.metadata.update({
            "rock_thickness": ballast_thickness,
            "fouling_thickness": fouling_height,
            "foul_eps_derived": props['foul_eps']
        })
        
        # Ensure we set top_y correctly (RockLayer should have set it, but verify)
        result.top_y = ctx.current_y + ballast_thickness
        
        # --- Validate Statistics ---
        # Calculate accurate volume fractions now that all geometry is assembled
        stats = BallastStatsCalculator.calculate_stats(
            commands=result.geometry,
            domain_x=ctx.config.domain_x,
            domain_z=ctx.config.domain_z,
            y_min=ctx.current_y,
            y_max=result.top_y,
            n_samples=5000 # Enough for quick estimation
        )
        
        result.metadata.update(stats)
        result.metadata['pvc_error'] = stats['calculated_pvc'] - self.pvc
        
        return result

    def _apply_layer_logic(self, config, start_y):
        raise NotImplementedError("GranularBallastLayer is now a CompositeNode. Use build(ctx).")
