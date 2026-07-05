"""
Frequency sweep: does particle shape become visible in the Mie regime?

rock_shape_ab + shape_dx_verify showed shape is invisible at 420 MHz (Rayleigh,
size parameter x~0.5). Prediction: raising frequency shrinks lambda; when the
rock approaches lambda (x~1-3, Mie regime) the sphere vs polyhedron waveforms
should DIVERGE. Same packing, same rocks (reuses the exact 1mm rock HDF5 from
shape_dx_verify), dx=1mm, only the ricker centre frequency changes.

Writes 8 decks: {sphere, poly} x {0.42, 1.0, 1.5, 2.4} GHz.
"""
from pathlib import Path

HERE = Path(__file__).parent

DOM_X = DOM_Y = 0.30
DOM_Z = 0.40
SUBGRADE_TOP = 0.12
BALLAST_TOP  = 0.32
STANDOFF_Z   = 0.35
DX = 0.001
TIME_WINDOW  = 18e-9
FREQS_GHZ = [0.42, 1.0, 1.5, 2.4]

VOID_EPS, VOID_SIG = 4.5, 0.001
SUBGRADE_EPS, SUBGRADE_SIG = 10.0, 0.010


def write_deck(shape, freq_ghz):
    tag = f"{shape}_{int(freq_ghz*1000)}mhz"
    h5 = f"{shape}_rocks.h5"
    mat = f"{shape}_materials.txt"
    def f(v): return f"{v:.5f}"
    cx = cy = DOM_X / 2
    lines = [
        f"## shape-freq sweep: {tag}",
        f"#domain: {DOM_X} {DOM_Y} {DOM_Z}",
        f"#dx_dy_dz: {DX} {DX} {DX}",
        f"#time_window: {TIME_WINDOW:g}",
        "",
        f"#material: {SUBGRADE_EPS} {SUBGRADE_SIG} 1.0 0.0 subgrade",
        f"#material: {VOID_EPS} {VOID_SIG} 1.0 0.0 void",
        "",
        f"#waveform: ricker 1 {freq_ghz*1e9:g} rick",
        f"#hertzian_dipole: y {f(cx)} {f(cy)} {f(STANDOFF_Z)} rick",
        f"#rx: {f(cx + 0.02)} {f(cy)} {f(STANDOFF_Z)}",
        "",
        f"#box: 0 0 0 {DOM_X} {DOM_Y} {SUBGRADE_TOP} subgrade",
        f"#box: 0 0 {SUBGRADE_TOP} {DOM_X} {DOM_Y} {BALLAST_TOP} void",
        f"#geometry_objects_read: 0 0 {SUBGRADE_TOP} {h5} {mat}",
        "",
        # geometry .vti written alongside the .out for each run (type 'n' =
        # per-Yee-cell, no averaging). Geometry is freq-independent, so the 4
        # decks of a given shape produce identical .vti.
        f"#geometry_view: 0 0 0 {DOM_X} {DOM_Y} {DOM_Z} {DX} {DX} {DX} {tag} n",
        "",
        "#messages: n",
    ]
    (HERE / f"{tag}.in").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[deck] {tag}.in")


for freq in FREQS_GHZ:
    for shape in ("sphere", "poly"):
        write_deck(shape, freq)
print(f"\n{len(FREQS_GHZ)*2} decks written")
