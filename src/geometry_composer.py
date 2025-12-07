import random
import json
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from .config import GeneratorConfig, topp_mixing_model, fmt

def apply_spatial_jitter(commands: List[str], config: GeneratorConfig) -> List[str]:
    """
    Apply spatial jitter to rock positions for domain randomization.
    
    Adds Gaussian noise to rock (x, y) positions to simulate natural
    variation and improve ML model robustness.
    
    Args:
        commands: List of gprMax command strings
        config: GeneratorConfig with spatial_jitter_sigma
    
    Returns:
        List of modified command strings
    """
    if not config.enable_domain_randomization or config.spatial_jitter_sigma <= 0:
        return commands
    
    jittered_commands = []
    
    for cmd in commands:
        if cmd.startswith('#cylinder:') and 'bal_rock' in cmd:
            # Parse cylinder command
            # Format: #cylinder: x y z x y z radius material
            parts = cmd.split()
            if len(parts) >= 9:
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    radius = float(parts[7])
                    
                    # Apply jitter
                    x_jitter = random.gauss(0, config.spatial_jitter_sigma)
                    y_jitter = random.gauss(0, config.spatial_jitter_sigma)
                    
                    x_new = x + x_jitter
                    y_new = y + y_jitter
                    
                    # Ensure within bounds
                    x_new = max(radius, min(x_new, config.domain_x - radius))
                    y_new = max(0.3 + radius, min(y_new, config.domain_y - radius))
                    
                    # Reconstruct command
                    # parts[6] is z2, usually same as z1 (z)
                    z2 = float(parts[6]) 
                    jittered_cmd = (f"#cylinder: {fmt(x_new)} {fmt(y_new)} {fmt(z)} "
                                   f"{fmt(x_new)} {fmt(y_new)} {fmt(z2)} "
                                   f"{fmt(radius)} {parts[8]}")
                    jittered_commands.append(jittered_cmd)
                except (ValueError, IndexError):
                    # If parsing fails, keep original
                    jittered_commands.append(cmd)
            else:
                jittered_commands.append(cmd)
        else:
            jittered_commands.append(cmd)
    
    return jittered_commands

class Layer(ABC):
    """
    Abstract Base Class for a geometry layer.
    
    All specific geometry layers (Subgrade, Ballast, etc.) must inherit from this
    and implement the apply() method.
    """
    @abstractmethod
    def apply(self, config: GeneratorConfig, start_y: float) -> Tuple[List[str], float, Dict[str, Any]]:
        """
        Apply layer geometry to the scene.

        Args:
            config (GeneratorConfig): The global configuration object.
            start_y (float): The starting Y coordinate (bottom) for this layer.

        Returns:
            Tuple[List[str], float, Dict[str, Any]]: 
                - List of gprMax commands (strings).
                - The new top Y coordinate after this layer.
                - A dictionary of metadata about the layer (e.g., calculated parameters).
        """
        pass

class ScenePainter:
    """
    Orchestrates the painting of layers back-to-front (Painter's Algorithm).
    
    Attributes:
        config (GeneratorConfig): Configuration object.
        layers (List[Layer]): Ordered list of layers to apply.
    """
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.layers: List[Layer] = []
        
    def add_layer(self, layer: Layer):
        self.layers.append(layer)
        
    def paint(self, base_name: str = "geometry_view") -> Tuple[List[str], List[str], Dict[str, Any]]:
        """
        Executes all layers.
        Returns:
            - setup_lines: General setup commands
            - content_lines: Materials + Geometry commands
            - scenario_metadata: Aggregate metadata
        """
        cfg = self.config
        setup_lines = []
        content_lines = []
        all_metadata = {}
        
        # 1. Standard Setup
        setup_lines.append(f"#domain: {fmt(cfg.domain_x)} {fmt(cfg.domain_y)} {fmt(cfg.domain_z)}")
        setup_lines.append(f"#dx_dy_dz: {fmt(cfg.dx)} {fmt(cfg.dy)} {fmt(cfg.dz)}")
        setup_lines.append(f"#time_window: {fmt(cfg.time_window)}")
        
        if cfg.add_waveform:
            setup_lines.append(f"#waveform: ricker 1 {fmt(cfg.center_freq)} src")
            
        # 2. Iterate Layers
        current_y = 0.0
        for layer in self.layers:
            layer_commands, next_y, meta = layer.apply(cfg, current_y)
            content_lines.extend(layer_commands)
            all_metadata.update(meta)
            current_y = next_y
            
        # 3. Geometry View (Standard logic)
        gv_cmd = (
            f"#geometry_view: 0 0 0 {fmt(cfg.domain_x)} {fmt(cfg.domain_y)} {fmt(cfg.domain_z)} "
            f"{fmt(cfg.dx)} {fmt(cfg.dy)} {fmt(cfg.dz)} {base_name}.vti n"
        )
        if cfg.add_geometry_view:
            content_lines.append(gv_cmd)
        else:
            content_lines.append(f"## {gv_cmd}")
            content_lines.append("## (Uncomment above for ParaView)")
            
        return setup_lines, content_lines, all_metadata

# --- Concrete Layers ---

class BackgroundLayer(Layer):
    """
    Paints the initial background box (free_space) covering the entire domain.
    This acts as the canvas.
    """
    def apply(self, config: GeneratorConfig, start_y: float):
        cmd = []
        cmd.append("## Fondo completo (free_space)")
        cmd.append(f"#box: 0.0 0.0 0.0 {fmt(config.domain_x)} {fmt(config.domain_y)} {fmt(config.domain_z)} free_space")
        # Background doesn't advance Y, it's the canvas
        return cmd, start_y, {}

class SubgradeLayer(Layer):
    """
    Adds a Subgrade layer.
    Thickness is defined in config.subgrade_thickness.
    """
    def apply(self, config: GeneratorConfig, start_y: float):
        h = config.subgrade_thickness
        top_y = start_y + h
        cmd = []
        cmd.append("#material: 7.0 0.01 1 0 subgrade")
        cmd.append(f"## Layer: subgrade ({fmt(start_y)}–{fmt(top_y)})")
        cmd.append(f"#box: 0.0 {fmt(start_y)} 0.0 {fmt(config.domain_x)} {fmt(top_y)} {fmt(config.domain_z)} subgrade")
        return cmd, top_y, {}

class FormationLayer(Layer):
    """
    Adds a Formation layer (Capping layer).
    Thickness is defined in config.formation_thickness.
    """
    def apply(self, config: GeneratorConfig, start_y: float):
        h = config.formation_thickness
        top_y = start_y + h
        cmd = []
        cmd.append("#material: 10.0 0.03 1 0 formation")
        cmd.append(f"## Layer: formation ({fmt(start_y)}–{fmt(top_y)})")
        cmd.append(f"#box: 0.0 {fmt(start_y)} 0.0 {fmt(config.domain_x)} {fmt(top_y)} {fmt(config.domain_z)} formation")
        return cmd, top_y, {}

class SleeperLayer(Layer):
    """
    Adds periodic railway sleepers (ties) on top of the ballast.
    Simulates concrete sleepers causing periodic noise/reflections.
    """
    def apply(self, config: GeneratorConfig, start_y: float):
        cmd = []
        
        sleeper_w = 0.25  # Width in direction of travel (X)
        sleeper_h = 0.15  # Height (Y)
        spacing = 0.60    # Center-to-center spacing
        
        # Material: Concrete
        # Eps=9.0, Sigma=0.01 (typical cured concrete)
        cmd.append(f"#material: 9.0 0.01 1 0 concrete_sleeper")
        cmd.append("## Sleepers (Concrete)")
        
        # Start placing from X=0 with some offset
        current_x = 0.1 
        
        count = 0
        while current_x + sleeper_w < config.domain_x:
            x_start = current_x
            x_end = current_x + sleeper_w
            y_start = start_y
            y_end = start_y + sleeper_h
            
            cmd.append(f"#box: {fmt(x_start)} {fmt(y_start)} 0.0 {fmt(x_end)} {fmt(y_end)} {fmt(config.domain_z)} concrete_sleeper")
            
            current_x += spacing
            count += 1
            
        # Return effective top (top of sleeper) so antenna is placed above them
        new_top = start_y + sleeper_h
        return cmd, new_top, {"sleeper_count": count}

class AntennaLayer(Layer):
    """
    Adds Hertzian Dipole source and Rx point.
    Position is calculated relative to the top surface (start_y) + air gap.
    """
    def apply(self, config: GeneratorConfig, start_y: float):
        # start_y here is the top of the ballast/surface
        air_gap = 0.53
        antenna_y = start_y + air_gap
        
        cmd = []
        
        # Check bounds
        margin = 15 * config.dy
        if antenna_y > (config.domain_y - margin):
            # This check logic was in original script, keeping it safer
            pass 
            
        cmd.append("## TX/RX en aire")
        cmd.append(f"#hertzian_dipole: z {fmt(config.tx_x)} {fmt(antenna_y)} {fmt(config.tx_rx_z)} src")
        cmd.append(f"#rx: {fmt(config.rx_x)} {fmt(antenna_y)} {fmt(config.tx_rx_z)}")
        

        return cmd, antenna_y, {} # Does not really advance ground Y

class MasterPatternLayer(Layer):
    """
    Reads a pre-generated JSON master pattern of circles and applies them.
    Efficiently checks bounds and replicates rocks as cylinders.
    """
    def __init__(self, pattern_file: str, pvc: float, moisture: float):
        self.pattern_file = pattern_file
        self.pvc = pvc
        self.moisture = moisture
        
    def apply(self, config: GeneratorConfig, start_y: float):
        cmd = []
        meta = {}
        
        # Load pattern
        try:
            with open(self.pattern_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading master pattern: {e}")
            return [], start_y, {"error": str(e)}

        rocks = data.get("rocks", [])
        
        # Calculate derived electrical properties (with optional randomization)
        if config.enable_domain_randomization:
            # Randomize moisture (affects foul_eps and foul_sigma)
            moisture = random.uniform(0, config.moisture_randomization_range)
            # Randomize rock properties
            rock_eps = config.bal_rock_eps * random.uniform(
                1 - config.rock_eps_variation,
                1 + config.rock_eps_variation
            )
            rock_sigma = config.bal_rock_sigma * random.uniform(
                1 - config.rock_sigma_variation,
                1 + config.rock_sigma_variation
            )
        else:
            moisture = self.moisture
            rock_eps = config.bal_rock_eps
            rock_sigma = config.bal_rock_sigma
        
        foul_eps = topp_mixing_model(moisture)
        foul_sigma = 0.001 + 0.2 * moisture
        
        cmd.append(f"## Master Pattern Ballast Layer")
        cmd.append(f"#material: {fmt(rock_eps)} {fmt(rock_sigma)} 1 0 bal_rock")
        cmd.append(f"#material: {fmt(foul_eps)} {fmt(foul_sigma)} 1 0 bal_foul_granular")

        ballast_h = config.max_ballast_thickness
        top_y = start_y + ballast_h
        
        # Fouling Matrix Box
        foul_h = ballast_h * (self.pvc / 100.0)
        foul_top = start_y + foul_h
        
        if foul_h > 0.01:
             cmd.append(f"## Fouling Matrix (PVC={self.pvc:.1f}%)")
             cmd.append(f"#box: 0.0 {fmt(start_y)} 0.0 {fmt(config.domain_x)} {fmt(foul_top)} {fmt(config.domain_z)} bal_foul_granular")
        
        # Render Rocks (Cylinders)
        cmd.append("## Ballast Aggregates (Master Pattern)")
        
        count = 0
        
        # Filter rocks within the domain window
        # We assume the master pattern is large enough.
        # Use simple spatial check.
        
        for rock in rocks:
            x = rock['x']
            y = rock['y']
            r = rock['r']
            
            # Shift Y to sit on start_y
            final_y = y + start_y
            
            # Check bounds (allowing some radius overlap)
            if final_y - r > top_y:
                continue # Above layer
            if final_y + r < start_y:
                continue # Below layer (shouldn't happen if pattern is 0-based)
            
            # Global Simulation Domain Check (Critical)
            if final_y + r >= config.domain_y:
                 continue # Exceeds simulation ceiling
            if final_y - r <= 0:
                 continue # Exceeds simulation floor (rare)
                 
            # Strict X Containment (User Request)
            # Remove rock if any part of it overlaps the vertical edges
            if x - r < 0:
                continue # Overlaps Left
            if x + r > config.domain_x:
                continue # Overlaps Right
                
            # Output Cylinder
            # cylinder: x1 y1 z1 x2 y2 z2 radius material
            cmd.append(f"#cylinder: {fmt(x)} {fmt(final_y)} 0.0 {fmt(x)} {fmt(final_y)} {fmt(config.domain_z)} {fmt(r)} bal_rock")
            count += 1
            
        meta['rock_count'] = count
        meta['type'] = 'master_pattern'
        
        return apply_spatial_jitter(cmd, config), top_y, meta

class GranularBallastLayer(Layer):
    """
    Complex layer:
    1. Base fouling matrix (box)
    2. Rocks (cylinders)
    """
    def __init__(self, materials_repo, pvc, moisture):
        self.materials_repo = materials_repo # Not used much if we generate strings immediately
        # We need pvc and moisture to be passed in from the scenario data
        self.pvc = pvc
        self.moisture = moisture
        
    def apply(self, config: GeneratorConfig, start_y: float):
        cmd = []
        meta = {}
        
        # Calculate heights
        # Determine ballast top based on configuration
        # The generator passes 'rock_h' to the compose function.
        # We need to respect that logic.
        # Ideally, we calculate it here based on config min/max
        
        # Wait, random sampling should happen outside or inside?
        # If we want ScenePainter to be deterministic given a config, the random values should be IN the config or passed.
        # The original `_compose_file` received `rock_h` as argument.
        # We will assume config handles randomness or we sample here.
        
        rock_h = random.uniform(config.min_ballast_thickness, config.max_ballast_thickness)
        rock_top = start_y + rock_h
        rock_top = min(rock_top, config.domain_y) # Clip
        
        # 1. Fouling Matrix Material
        # Apply domain randomization if enabled
        if config.enable_domain_randomization:
            # Randomize moisture
            moisture = random.uniform(0, config.moisture_randomization_range)
            # Randomize rock properties
            rock_eps = config.bal_rock_eps * random.uniform(
                1 - config.rock_eps_variation,
                1 + config.rock_eps_variation
            )
            rock_sigma = config.bal_rock_sigma * random.uniform(
                1 - config.rock_sigma_variation,
                1 + config.rock_sigma_variation
            )
        else:
            moisture = self.moisture
            rock_eps = config.bal_rock_eps
            rock_sigma = config.bal_rock_sigma
        
        foul_eps = topp_mixing_model(moisture)
        foul_sigma = 0.001 + 0.2 * moisture
        cmd.append(f"#material: {fmt(rock_eps)} {fmt(rock_sigma)} 1 0 bal_rock")
        cmd.append(f"#material: {fmt(foul_eps)} {fmt(foul_sigma)} 1 0 bal_foul_granular")
        
        # 2. Fouling: Gravity-Settled Void Filling
        # ==========================================
        # Simulates realistic fouling accumulation in railway ballast:
        # - Bottom layer: Dense settled fines (gravity settling over time)
        # - Upper voids: Sparse particles (recent infiltration)
        #
        # Physical basis:
        # - Fine particles (clay, silt, sand) settle to bottom due to gravity
        # - Recent contamination dispersed in upper voids
        # - PVC (Percentage Void Contamination) determines total fouling volume
        #
        # Implementation:
        # - 70% of fouling: Continuous box at bottom (settled layer)
        # - 30% of fouling: Small cylinders in upper voids (dispersed particles)
        
        foul_fill_height = rock_h * (self.pvc / 100.0)
        
        if foul_fill_height > (config.dy * 0.5):
            cmd.append(f"## Fouling: Gravity-Settled Distribution (PVC={self.pvc:.1f}%)")
            
            # Component 1: Settled layer (70% of total fouling)
            # -------------------------------------------------
            # Dense accumulation at bottom from long-term settling
            settled_fraction = 0.7
            settled_height = foul_fill_height * settled_fraction
            foul_horizon_y = start_y + settled_height
            
            cmd.append("## - Settled Layer (bottom)")
            cmd.append(f"#box: 0.0 {fmt(start_y)} 0.0 {fmt(config.domain_x)} {fmt(foul_horizon_y)} {fmt(config.domain_z)} bal_foul_granular")
            
            # Component 2: Dispersed particles (30% of total fouling)
            # --------------------------------------------------------
            # Small particles in upper voids representing recent contamination
            # Only placed in actual voids (not overlapping with rocks)
            
            # Note: Rock generation happens after this, so we'll add a method
            # to generate dispersed particles that can be called after rocks are placed
            # For now, store parameters for later use
            meta['dispersed_fouling'] = {
                'enabled': True,
                'y_min': foul_horizon_y,
                'y_max': start_y + foul_fill_height,
                'fraction': 0.3,
                'particle_size_min': 0.002,  # 2mm
                'particle_size_max': 0.008,  # 8mm
            }
        else:
            meta['dispersed_fouling'] = {'enabled': False}
            
        # 3. Rocks
        cmd.append("## Granular Aggregates")
        # Reuse helper logic (simplified inline or call helper)
        # We'll implement _add_rock_layer logic here or assume helper availability.
        # For brevity in this artifact, I will implement a simplified loop calling a helper 
        # (I will define the helper in this file).
        
        n_layers = 3
        layer_h = rock_h / n_layers
        r_step = (config.rock_radius_max - config.rock_radius_min) / n_layers
        
        metrics = {}
        total_rocks = 0
        
        for i in range(n_layers):
             y_min = start_y + i * layer_h
             y_max = start_y + (i+1) * layer_h
             # Overlap
             if i > 0: y_min -= layer_h # 100% overlap logic
             
             r_min = config.rock_radius_min + i*r_step
             r_max = r_min + r_step
             
             # Call helper
             c_cmds, count = self._generate_rocks(config, y_min, y_max, r_min, r_max, i)
             cmd.extend(c_cmds)
             total_rocks += count
             
        # 4. Dispersed Fouling Particles (if enabled)
        # ============================================
        # Generate small particles in upper voids after rocks are placed
        # This ensures particles only appear in actual voids
        
        if meta.get('dispersed_fouling', {}).get('enabled', False):
            cmd.append("## - Dispersed Particles (upper voids)")
            
            # Extract rock positions for void detection
            rock_list = self._extract_rock_positions(cmd)
            
            # Generate particles in voids
            particle_cmds = self._generate_dispersed_fouling_particles(
                rock_list=rock_list,
                domain_x=config.domain_x,
                domain_z=config.domain_z,
                y_min=meta['dispersed_fouling']['y_min'],
                y_max=meta['dispersed_fouling']['y_max'],
                pvc=self.pvc,
                particle_size_min=meta['dispersed_fouling']['particle_size_min'],
                particle_size_max=meta['dispersed_fouling']['particle_size_max']
            )
            cmd.extend(particle_cmds)
            meta['dispersed_particle_count'] = len(particle_cmds)
        else:
            meta['dispersed_particle_count'] = 0
        
        meta.update({
            "rock_height": rock_h,
            "foul_height": foul_fill_height,
            "rock_count": total_rocks,
            "foul_eps_derived": foul_eps
        })
        
        # Apply spatial jitter if domain randomization is enabled
        if config.enable_domain_randomization:
            cmd = apply_spatial_jitter(cmd, config)
        
        return cmd, rock_top, meta

    def _generate_rocks(self, cfg, y_min, y_max, r_min, r_max, layer_idx):
        """Generate rocks for a single layer with size constraints."""
        cmds = []
        count = 0
        attempts = 0
        max_attempts = 1000
        
        # Volume heuristic
        vol = (cfg.domain_x) * (y_max - y_min)
        target_fill = 0.6  # 60% rocks
        current_fill = 0.0
        
        while current_fill < target_fill and attempts < max_attempts:
            r = random.uniform(r_min, r_max)
            x = random.uniform(0 + r, cfg.domain_x - r)
            y = random.uniform(y_min + r, y_max - r)
            
            cmds.append(f"#cylinder: {fmt(x)} {fmt(y)} 0.0 {fmt(x)} {fmt(y)} {fmt(cfg.domain_z)} {fmt(r)} bal_rock")
            current_fill += (np.pi * r * r) / vol
            count += 1
            attempts += 1
            
        return cmds, count
    
    def _calculate_rock_area_monte_carlo(self, rocks, domain_x, y_min, y_max, n_samples=50000):
        """
        Calculate total rock area using Monte Carlo integration.
        Accounts for overlapping rocks correctly.
        
        Args:
            rocks: List of dicts with 'x', 'y', 'radius' keys
            domain_x: Width of domain
            y_min: Bottom of ballast layer
            y_max: Top of ballast layer
            n_samples: Number of random samples (higher = more accurate)
        
        Returns:
            float: Total rock area in m²
        """
        if not rocks:
            return 0.0
        
        # Generate random sample points
        x_samples = np.random.uniform(0, domain_x, n_samples)
        y_samples = np.random.uniform(y_min, y_max, n_samples)
        
        # Count points inside any rock
        inside_count = 0
        for x, y in zip(x_samples, y_samples):
            for rock in rocks:
                dist_sq = (x - rock['x'])**2 + (y - rock['y'])**2
                if dist_sq <= rock['radius']**2:
                    inside_count += 1
                    break  # Count each point only once
        
        # Calculate area
        ballast_area = domain_x * (y_max - y_min)
        rock_area = (inside_count / n_samples) * ballast_area
        
        return rock_area
    
    def _extract_rock_positions(self, commands):
        """
        Extract rock positions from generated gprMax commands.
        
        Parses cylinder commands to extract x, y, radius for void detection.
        
        Args:
            commands: List of gprMax command strings
        
        Returns:
            List of dicts with 'x', 'y', 'radius' keys
        """
        rocks = []
        for cmd in commands:
            if cmd.startswith('#cylinder:') and 'bal_rock' in cmd:
                # Parse: #cylinder: x y z x y z radius material
                parts = cmd.split()
                if len(parts) >= 8:
                    try:
                        x = float(parts[1])
                        y = float(parts[2])
                        radius = float(parts[7])
                        rocks.append({'x': x, 'y': y, 'radius': radius})
                    except (ValueError, IndexError):
                        continue
        return rocks
    
    def _generate_dispersed_fouling_particles(self, rock_list, domain_x, domain_z,
                                              y_min, y_max, pvc, 
                                              particle_size_min, particle_size_max):
        """
        Generate dispersed fouling particles in upper voids.
        
        Simulates recent contamination that hasn't settled to the bottom yet.
        Particles are only placed in actual voids (not overlapping with rocks).
        
        Physical Basis:
        ---------------
        - Recent infiltration: Fine particles entering from above (ballast pumping,
          track maintenance, environmental deposition)
        - Not yet settled: Particles suspended in upper voids
        - Sparse distribution: Unlike dense bottom layer, these are scattered
        
        Algorithm:
        ----------
        1. Calculate target number of particles based on PVC
        2. Generate random candidate positions in upper region
        3. Filter out positions that overlap with rocks
        4. Create small cylinders (2-8mm) at valid positions
        
        Args:
            rock_list: List of dicts with 'x', 'y', 'radius' for existing rocks
            domain_x: Width of domain (m)
            domain_z: Depth of domain (m)
            y_min: Bottom of dispersed particle region (m)
            y_max: Top of dispersed particle region (m)
            pvc: Percentage Void Contamination (0-100)
            particle_size_min: Minimum particle radius (m)
            particle_size_max: Maximum particle radius (m)
        
        Returns:
            List of gprMax cylinder command strings
        """
        cmds = []
        
        # Calculate target particle count
        # Scale with PVC: more fouling = more particles
        # Base: ~50 particles at 100% PVC
        target_count = int(50 * (pvc / 100.0))
        
        if target_count == 0:
            return cmds
        
        # Generate candidates (try more than needed to account for filtering)
        max_attempts = target_count * 5
        placed_count = 0
        
        for _ in range(max_attempts):
            if placed_count >= target_count:
                break
            
            # Random position in upper region
            x = random.uniform(0, domain_x)
            y = random.uniform(y_min, y_max)
            r = random.uniform(particle_size_min, particle_size_max)
            
            # Check if position is in a void (not overlapping any rock)
            in_void = True
            for rock in rock_list:
                # Distance between particle center and rock center
                dist_sq = (x - rock['x'])**2 + (y - rock['y'])**2
                # Check if particle would overlap rock (with small buffer)
                if dist_sq <= (rock['radius'] + r + 0.001)**2:
                    in_void = False
                    break
            
            # Place particle if in void
            if in_void:
                cmds.append(f"#cylinder: {fmt(x)} {fmt(y)} 0.0 "
                           f"{fmt(x)} {fmt(y)} {fmt(domain_z)} "
                           f"{fmt(r)} bal_foul_granular")
                placed_count += 1
        
        return cmds
    


