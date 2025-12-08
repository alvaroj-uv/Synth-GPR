
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
        # Config has tx_x, tx_rx_y, tx_rx_z
        
        # Ensure we are using the correct polarization ('x' by default for typically GPR?)
        # Standard GPR is often y-polarized (E-field along Y)? Or x? 
        # Usually infinite line source or dipole along Y (horizontal) or X.
        # Let's assume 'z' polarization (standard for 2D TM) or 'x'. 
        # But wait, config doesn't specify polarization. 
        # Ricker source 'ricker' is a waveform.
        # We will use 'z' (out of page) for 2D, or 'x' for 3D?
        # Let's default to 'x' polarization for now as common.
        
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
