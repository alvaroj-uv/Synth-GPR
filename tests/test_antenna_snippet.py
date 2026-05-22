
from src.workers import Layer, LayerResult
from src.gpr_commands import HertzianDipoleCommand, RxCommand, Header
from src.config import GeneratorConfig

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
        # Antenna Y coordinate is computed from CoordinateSystem based on layer stack.
        # This is legacy test code - antenna placement is now handled by AntennaWorker.

        # This test is outdated and should use AntennaWorker instead.
        # Keeping for reference only.

        # res.sources.append(HertzianDipoleCommand(
        #     "z",
        #     config.tx_x, antenna_y, config.tx_rx_z,
        #     "ricker"
        # ))
        #
        # res.sources.append(RxCommand(
        #     config.rx_x, antenna_y, config.tx_rx_z
        # ))
        
        # Don't update top_y as this is an overlay
        res.top_y = start_y
        
        return res
