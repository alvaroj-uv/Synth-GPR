import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.signal_processing import dewow, apply_gain, time_zero_correction, detect_first_break, compute_spectrogram
from src.visualization.nodes import FigureNode, GraphNode, TraceNode, LineStyle, SpectrogramNode
from src.visualization.renderer import MatplotlibRenderer

def create_noisy_signal(n=1000, dt=1e-9):
    t = np.arange(n) * dt * 1e9 # ns
    
    # Ricker wavelet-ish
    f = 400e6 # 400 MHz
    t_pulse = np.linspace(-3e-9, 3e-9, 100)
    pulse = (1.0 - 2.0*(np.pi**2)*(f**2)*(t_pulse**2)) * np.exp(-(np.pi**2)*(f**2)*(t_pulse**2))
    
    signal = np.zeros(n)
    start_pos = 200
    signal[start_pos:start_pos+len(pulse)] = pulse
    
    # Add low freq bias (wow)
    wow = np.sin(t / 100) * 0.2
    
    # Add attenuation and noise
    attenuation = np.exp(-t / 300)
    signal = (signal + wow) * attenuation + np.random.normal(0, 0.02, size=n)
    
    return t, signal

def main():
    print("Generating synthetic GPR signal...")
    t_ns, raw_signal = create_noisy_signal()
    dt = 1e-9
    
    print("Applying Processing Steps...")
    
    # 1. Dewow
    dewowed = dewow(raw_signal, window_size=50)
    
    # 2. Time Zero
    fb_idx = detect_first_break(dewowed)
    print(f"Detected First Break index: {fb_idx}")
    shifted = time_zero_correction(dewowed, fb_idx)
    
    # 3. AGC Gain
    agced = apply_gain(shifted, dt, type='agc', window_std=50)
    
    # Visualization using Node Model
    print("Building Figure...")
    fig_node = FigureNode(title="Processing Verification", figsize=(10, 12))
    
    # Raw Plot
    ax1 = GraphNode(position=311, title="1. Raw Signal (with Low Freq Bias)", xlabel="Sample", ylabel="Amp")
    ax1.add_child(TraceNode(x=t_ns, y=raw_signal, style=LineStyle(color='gray'), label='Raw'))
    fig_node.add_child(ax1)
    
    # Dewowed Plot
    ax2 = GraphNode(position=312, title=f"2. Dewow & TimeZero (Shift={fb_idx})", xlabel="Sample", ylabel="Amp")
    ax2.add_child(TraceNode(x=t_ns, y=dewowed, style=LineStyle(color='blue', alpha=0.5), label='Dewow'))
    ax2.add_child(TraceNode(x=t_ns, y=shifted, style=LineStyle(color='green'), label='Shifted'))
    fig_node.add_child(ax2)
    
    # AGC Plot
    ax3 = GraphNode(position=313, title="3. AGC Gain", xlabel="Sample", ylabel="Amp")
    ax3.add_child(TraceNode(x=t_ns, y=shifted, style=LineStyle(color='green', alpha=0.3), label='Input'))
    ax3.add_child(TraceNode(x=t_ns, y=agced, style=LineStyle(color='red'), label='AGC Output'))
    ax3.add_child(TraceNode(x=t_ns, y=agced, style=LineStyle(color='red'), label='AGC Output'))
    fig_node.add_child(ax3)
    
    # Spectrogram Plot
    ax4 = GraphNode(position=314, title="4. Spectrogram (Analytic Signal)", xlabel="Time (ns)", ylabel="Frequency (Hz)")
    # Compute spectrogram of the shifted signal
    f, t_spec, Sxx = compute_spectrogram(shifted, fs=1/dt, nperseg=64, noverlap=32)
    
    # Convert t_spec to ns
    t_spec_ns = t_spec * 1e9
    
    spec_node = SpectrogramNode(t=t_spec_ns, f=f, Sxx=Sxx, cmap='plasma', colorbar_label='Magnitude')
    ax4.add_child(spec_node)
    fig_node.add_child(ax4)
    # Adjust Figure Size
    fig_node.figsize = (12, 16)
    
    print("Rendering...")
    renderer = MatplotlibRenderer()
    fig = renderer.render(fig_node)
    
    out_file = "test_processing_result.webp"
    fig.savefig(out_file)
    print(f"Saved result to {out_file}")

if __name__ == "__main__":
    main()
