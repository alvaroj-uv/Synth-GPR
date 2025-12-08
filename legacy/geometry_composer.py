import random
from abc import abstractmethod
from typing import List
from .config import GeneratorConfig, fmt
from .gpr_commands import (
    GPRCommand, DomainCommand, DxDyDzCommand, TimeWindowCommand, 
    MaterialCommand, BoxCommand, CylinderCommand, WaveformCommand, 
    HertzianDipoleCommand, RxCommand, GeometryViewCommand, Header
)

from .scene_descriptor import LayerResult, SceneDefinition
from .scene_graph import LeafLayer, CompositeNode, BuildContext, SceneNode

def apply_spatial_jitter(commands: List[GPRCommand], config: GeneratorConfig) -> List[GPRCommand]:
    # Apply spatial jitter to rock positions for domain randomization.
    # 
    # Args:
    #     commands: List of GPRCommand objects
    #     config: GeneratorConfig with spatial_jitter_sigma
    # 
    # Returns:
    #     List of modified GPRCommand objects
    if not config.enable_domain_randomization or config.spatial_jitter_sigma <= 0:
        return commands
    
    jittered_commands = []
    
    for cmd in commands:
        if isinstance(cmd, CylinderCommand) and 'bal_rock' in cmd.material:
            # Apply jitter
            x_jitter = random.gauss(0, config.spatial_jitter_sigma)
            y_jitter = random.gauss(0, config.spatial_jitter_sigma)
            
            x_new = cmd.x1 + x_jitter
            y_new = cmd.y1 + y_jitter # Assume vertical cylinder, y1=y2? No, y is up. Cylinder is usually horizontal or vertical.
            # checks: `#cylinder: {fmt(x)} {fmt(y)} 0.0 {fmt(x)} {fmt(y)} {fmt(cfg.domain_z)} {fmt(r)} bal_rock`
            # Yes, they are vertical cylinders (x1=x2, y1=y2).
            # But wait, original code x_jitter adds to x, y_jitter adds to y.
            
            x_new = max(cmd.radius, min(x_new, config.domain_x - cmd.radius))
            y_new = max(0.3 + cmd.radius, min(y_new, config.domain_y - cmd.radius))
            
            # Create new command
            new_cmd = CylinderCommand(
                x1=x_new, y1=y_new, z1=cmd.z1,
                x2=x_new, y2=y_new, z2=cmd.z2,
                radius=cmd.radius,
                material=cmd.material
            )
            jittered_commands.append(new_cmd)
        else:
            jittered_commands.append(cmd)
    
    return jittered_commands

class Layer(LeafLayer):
    # Abstract Base Class for a geometry layer.
    # Adapted to SceneGraph architecture.
    
    def _generate(self, ctx: BuildContext) -> LayerResult:
        # Adapter: Calls the legacy _apply_layer_logic with unpacked context
        return self._apply_layer_logic(ctx.config, ctx.current_y)

    @abstractmethod
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        """
        Abstract Hook: Implement specific layer geometry logic here.
        Must return a LayerResult.
        """
        pass

class ScenePainter:
    # Main orchestrator using Scene Graph.
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.root = CompositeNode("Root")
        
    def add_layer(self, layer: SceneNode):
        self.root.add(layer)
        
    def paint(self, base_name: str = "custom") -> SceneDefinition:
        # Execute the Scene Graph build process.
        
        # 1. Prepare Context
        ctx = BuildContext(config=self.config, current_y=0.0)
        
        # 2. Build Root
        result = self.root.build(ctx)
        
        # 3. Assemble SceneDefinition
        
        scene = SceneDefinition(config=self.config)
        
        # Base commands 
        scene.domain_commands.append(DomainCommand(self.config.domain_x, self.config.domain_y, self.config.domain_z))
        scene.domain_commands.append(DxDyDzCommand(self.config.dx, self.config.dy, self.config.dz))
        scene.domain_commands.append(TimeWindowCommand(self.config.time_window))
        
        # 1b. Waveform (Source)
        if self.config.add_waveform:
            # Add waveform definition before any sources that use it
            scene.source_commands.append(WaveformCommand("ricker", 1, self.config.center_freq, "ricker"))
        
        # Merge Layer Results
        scene.geometry_commands.extend(result.geometry)
        scene.material_commands.extend(result.materials)
        scene.source_commands.extend(result.sources)
        scene.metadata.update(result.metadata)
        
        # Handle Jitter (Global Post-Process)
        if self.config.enable_domain_randomization:
            scene.geometry_commands = apply_spatial_jitter(scene.geometry_commands, self.config)

        # Legacy: geometry view command might be needed (or extracted to a node?)
        # For now, let's keep the logic if it was there, or rebuild it.
        # The previous code added a geometry view.
        
        gv = GeometryViewCommand(
            0, 0, 0, self.config.domain_x, self.config.domain_y, self.config.domain_z,
            self.config.dx, self.config.dy, self.config.dz, f"{base_name}.vti", 'n'
        )
        if self.config.add_geometry_view:
            scene.geometry_commands.append(gv)
        else:
             scene.geometry_commands.append(Header("Geometry View disabled (uncomment in source to enable)"))
             scene.geometry_commands.append(Header(gv.render()))
             
        return scene

# --- Concrete Layers ---

class BackgroundLayer(Layer):
    # Fills the simulation domain with free_space as the base canvas.
    
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        res = LayerResult()
        res.geometry.append(Header("Background: free_space canvas"))
        res.geometry.append(BoxCommand(0.0, 0.0, 0.0, config.domain_x, config.domain_y, config.domain_z, "free_space"))
        res.top_y = start_y
        return res

class SubgradeLayer(Layer):
    # Adds the subgrade (foundation soil) layer at the bottom of the domain.
    
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        res = LayerResult()
        thickness = config.subgrade_thickness
        res.top_y = start_y + thickness
        
        res.materials.append(MaterialCommand(7.0, 0.01, 1, 0, "subgrade"))
        res.geometry.append(Header(f"Subgrade layer ({fmt(start_y)} to {fmt(res.top_y)})"))
        res.geometry.append(BoxCommand(0.0, start_y, 0.0, config.domain_x, res.top_y, config.domain_z, "subgrade"))
        
        return res

class FormationLayer(Layer):
    # Adds a Formation layer (Capping layer).
    # Thickness is defined in config.formation_thickness.
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        res = LayerResult()
        h = config.formation_thickness
        res.top_y = start_y + h
        
        res.materials.append(MaterialCommand(10.0, 0.03, 1, 0, "formation"))
        res.geometry.append(Header(f"Layer: formation ({fmt(start_y)}-{fmt(res.top_y)})"))
        res.geometry.append(BoxCommand(0.0, start_y, 0.0, config.domain_x, res.top_y, config.domain_z, "formation"))
        return res

class SleeperLayer(Layer):
    # Adds periodic railway sleepers (ties) on top of the ballast.
    # Simulates concrete sleepers causing periodic noise/reflections.
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        res = LayerResult()
        
        sleeper_w = 0.25  # Width in direction of travel (X)
        sleeper_h = 0.15  # Height (Y)
        spacing = 0.60    # Center-to-center spacing
        
        # Material: Concrete
        res.materials.append(MaterialCommand(9.0, 0.01, 1, 0, "concrete_sleeper"))
        res.geometry.append(Header("Sleepers (Concrete)"))
        
        # Start placing from X=0 with some offset
        current_x = 0.1 
        
        count = 0
        while current_x + sleeper_w < config.domain_x:
            x_start = current_x
            x_end = current_x + sleeper_w
            y_start = start_y
            y_end = start_y + sleeper_h
            
            res.geometry.append(BoxCommand(x_start, y_start, 0.0, x_end, y_end, config.domain_z, "concrete_sleeper"))
            
            current_x += spacing
            count += 1
            

    


class AntennaLayer(Layer):
    # Adds the antenna source and receiver commands.
    
    def _apply_layer_logic(self, config: GeneratorConfig, start_y: float) -> LayerResult:
        res = LayerResult()
        
        # We don't change geometry or materials, just sources
        # We use the config coordinates
        
        res.geometry.append(Header("Antenna: Hertzian Dipole + Rx"))
        
        # Transmitter (Hz Dipole)
        # Note: In gprMax, hertzian_dipole is a source. 
        # We put it slightly above the surface if air-coupled, or at specific coords.
        # Config has tx_x, tx_rx_y, tx_rx_z
        
        res.sources.append(HertzianDipoleCommand(
            "z", 
            config.tx_x, config.tx_rx_y, config.tx_rx_z, 
            "ricker"
        ))
        
        # Receiver
        res.sources.append(RxCommand(
            config.rx_x, config.tx_rx_y, config.tx_rx_z
        ))
        
        # Don't update top_y as this is an overlay
        res.top_y = start_y
        
        return res