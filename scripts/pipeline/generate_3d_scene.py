"""
Generate a 3D gprMax .in file for a 3D ballast scene with GSSI 400MHz antenna.

Coordinate system: X=along-track, Y=cross-track, Z=vertical (up).
The GSSI 400MHz antenna model from user_libs.antennas.GSSI uses this same
convention — the antenna lies in the XY plane with Z as vertical.

Domain: 0.50 × 0.50 × 0.80 m at dx=0.002 m → 250 × 250 × 400 cells (~25 M)
Geometry:
    z = 0.00 – 0.15 m   subgrade (eps=10)
    z = 0.15 – 0.50 m   ballast  (eps=5.1 clean OR rocks + void fill)
    z = 0.50 – 0.55 m   air standoff (5 cm)
    z = 0.55 m           GSSI 400 MHz antenna skid bottom

GPU run (RTX 2060, ~2 min):
    PYTHONIOENCODING=utf-8 conda run -n gprMax python -m gprMax <file.in> -gpu 0

Geometry-only (ParaView .vti):
    PYTHONIOENCODING=utf-8 conda run -n gprMax python -m gprMax <file.in> --geometry-only

Usage:
    python scripts/pipeline/generate_3d_scene.py
    python scripts/pipeline/generate_3d_scene.py --rocks
    python scripts/pipeline/generate_3d_scene.py --rocks --void-eps 4.5 --void-sigma 0.001
    python scripts/pipeline/generate_3d_scene.py --rocks --void-eps 9.5 --void-sigma 0.05
"""
import argparse
import datetime
import math
import subprocess
import sys
import tomllib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.constants import archie_sigma as _archie

from src.gpr_commands import (
    BoxCommand, DomainCommand, DxDyDzCommand, GeometryObjectsReadCommand,
    GeometryViewCommand, Header, MaterialCommand, PythonBlockCommand, RawCommand,
    SphereCommand, TimeWindowCommand,
)
from src.rock_voxelizer import (
    make_ellipsoid_shape, make_polyhedron_shape, make_scaled_sphere_shape,
    sphere_shape, spheres_to_domain_coords, voxelize_rocks,
    write_geometry_hdf5, write_materials_file,
)
from src.sphere_packing_3d import PackedSphere

# --rock-shape choices: "sphere" emits native #sphere commands (baseline);
# the "voxel-*" variants rasterise the SAME packing into an HDF5 array read
# via #geometry_objects_read. "voxel-sphere" replicates build_sphere's cell
# test exactly (control for validating the voxel path against #sphere).
ROCK_SHAPES = ("sphere", "voxel-sphere", "voxel-ellipsoid", "voxel-polyhedron",
               "voxel-sphere-small")  # r*0.745: volume-matched control (~0.41 vol
                                      # ratio, same as ellipsoid/polyhedron defaults)


def _git_sha() -> str:
    """Short git SHA of the working tree, for .in provenance headers (mirrors
    the same helper in src/layer_scene_builder.py, so 2D and 3D decks carry
    the same kind of reproducibility metadata)."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def load_config(toml_path: Path) -> dict:
    """Load a scene TOML and return a flat config dict with defaults filled in."""
    with open(toml_path, "rb") as f:
        cfg = tomllib.load(f)

    sim  = cfg.get("sim",  {})
    geom = cfg.get("geometry", {})
    mats = cfg.get("materials", {})
    foul = cfg.get("fouling",   {})
    pack = cfg.get("packing",   {})

    # Archie's law parameters (optional [archie] section)
    arch = cfg.get("archie", {})
    arch_rho_w = float(arch.get("rho_w", 40.0))
    arch_a     = float(arch.get("a",     0.88))
    arch_m     = float(arch.get("m",     1.37))
    arch_n     = float(arch.get("n",     2.0))

    def _resolve_sigma(s: dict, default: float) -> float:
        """Return sigma: explicit value wins; else compute from Archie if porosity given."""
        if "sigma" in s:
            return float(s["sigma"])
        if "porosity" in s and "saturation" in s:
            sig = _archie(float(s["porosity"]), float(s["saturation"]),
                          rho_w=arch_rho_w, a=arch_a, m=arch_m, n=arch_n)
            name = s.get("name", "layer")
            print(f"  [Archie] {name}: φ={s['porosity']}  Sw={s['saturation']}  "
                  f"ρ_w={arch_rho_w}Ω·m  →  σ={sig:.6f} S/m")
            return sig
        return default

    # Sleepers: support both [[sleepers]] array and legacy [sleeper] singular
    raw_sleepers = cfg.get("sleepers", [])
    slp = cfg.get("sleeper", {})
    if slp.get("enabled", False) and not raw_sleepers:
        raw_sleepers = [slp]

    def _slp(s: dict) -> dict:
        return {
            "eps":   float(s.get("eps",   6.5)),
            "sigma": _resolve_sigma(s, 0.010),
            "x_min": float(s.get("x_min", 0.12)),
            "x_max": float(s.get("x_max", 0.38)),
            "depth": float(s.get("depth", 0.20)),
        }

    def _sublayer(s: dict, idx: int) -> dict:
        return {
            "name":  str(s.get("name",  f"sub_layer_{idx}")),
            "h":     float(s.get("h",     0.10)),
            "eps":   float(s.get("eps",   7.5)),
            "sigma": _resolve_sigma(s, 0.005),
        }

    raw_sub_layers = cfg.get("sub_layers", [])

    sg_mat = mats.get("subgrade", {})
    sg_sig = _resolve_sigma(sg_mat, 0.010)

    return {
        "domain_x":      float(sim.get("domain_x",  DOMAIN_X)),
        "domain_y":      float(sim.get("domain_y",  DOMAIN_Y)),
        "domain_z":      float(sim.get("domain_z",  DOMAIN_Z)),
        "time_window":   float(sim.get("time_window", TIME_WINDOW)),
        "subgrade_h":    float(geom.get("subgrade_h",   SUBGRADE_H)),
        "subballast_h":  float(geom.get("subballast_h", 0.0)),
        "ballast_h":     float(geom.get("ballast_h",    BALLAST_H)),
        "standoff":      float(geom.get("standoff",     STANDOFF)),
        "subgrade_eps":  float(sg_mat.get("eps",   10.0)),
        "subgrade_sig":  sg_sig,
        "subballast_eps": float(mats.get("subballast", {}).get("eps",  7.5)),
        "subballast_sig": float(mats.get("subballast", {}).get("sigma", 0.005)),
        "granite_eps":   float(mats.get("granite",    {}).get("eps",   6.1)),
        "granite_sig":   float(mats.get("granite",    {}).get("sigma", 0.001)),
        "void_eps":      float(foul.get("void_eps",   1.0)),
        "void_sigma":    float(foul.get("void_sigma", 0.0)),
        "seed":             int(pack.get("seed",       42)),
        "r_min":            float(pack.get("r_min",    0.020)),
        "r_max":            float(pack.get("r_max",    0.033)),
        "target_phi":       float(pack.get("target_phi", 0.38)),
        "size_dist":        str(pack.get("size_dist",  "uniform")),
        "lognormal_sigma":  float(pack.get("lognormal_sigma", 0.35)),
        "rock_shape":       str(pack.get("rock_shape", "sphere")),
        "sleepers":         [_slp(s) for s in raw_sleepers],
        "sub_layers":       [_sublayer(s, i) for i, s in enumerate(raw_sub_layers)],
    }


# ── Geometry constants ────────────────────────────────────────────────────────
# dx=0.002 m required by GSSI 400MHz antenna model (accepts 0.0005, 0.001, 0.002)
DX = 0.002
DX = round(DX, 6)

SUBBALLAST_H = 0.0   # m  (sub-ballast layer thickness; 0 = disabled)

DOMAIN_X = 0.50   # m  (horizontal, along-track)
DOMAIN_Y = 0.50   # m  (horizontal, cross-track)
DOMAIN_Z = 0.80   # m  (vertical, Z-up: PML 20mm + subgrade 150mm + ballast 350mm
                  #      + standoff 50mm + antenna 178mm + clearance 52mm + PML 20mm)

SUBGRADE_H  = 0.15   # m  (subgrade thickness)
BALLAST_H   = 0.35   # m  (ballast layer thickness)
SURFACE_Z   = SUBGRADE_H + BALLAST_H   # = 0.50 m  (ballast top / air-ballast interface)
STANDOFF    = 0.05                      # = 5 cm (air gap between surface and skid)
SKID_Z      = SURFACE_Z + STANDOFF     # = 0.55 m  (GSSI skid bottom coordinate)

ANT_CX = DOMAIN_X / 2   # = 0.25 m  (antenna centre in X)
ANT_CY = DOMAIN_Y / 2   # = 0.25 m  (antenna centre in Y)

TIME_WINDOW = 30e-9   # 30 ns  (~8 ns round-trip through ballast; includes ringing)

PML_CELLS = 10        # gprMax default PML thickness

PHI_GRANITE = 0.39    # granite volume fraction from inflation packing


# ── Material properties ───────────────────────────────────────────────────────
MATS_BASE = {
    "ballast_clean": (5.1,  0.001, 1.0, 0.0),
    "subgrade":      (10.0, 0.010, 1.0, 0.0),
    "granite":       (6.1,  0.001, 1.0, 0.0),
}

# Void-fill sweep: eps_void that reproduces real eps_eff via LINEAR volumetric
# mixing (arithmetic average — NOT CRIM, which mixes sqrt(eps); see
# src.physics.crim_bulk_eps. At rock/void contrast the two differ <1%, so the
# ladder below is fine, but do not extend it to wet/high-contrast mixes with
# this formula):
# eps_eff = (1-phi)*eps_void + phi*eps_granite
# eps_void = (eps_eff - phi*eps_granite) / (1-phi)
# Clean target eps_eff=5.1: void_eps = (5.1 - 0.39*6.1)/0.61 = 4.46 → 4.5
# Fully fouled eps_eff=8.2: void_eps = 9.5
SWEEP_STEPS = [
    # (eps_void, sigma_void)  — sigma scales with PVC relative to eps_void=4.5 baseline
    (2.0, 0.0003),   # FI≈13%  (LF)
    (3.0, 0.0006),   # FI≈23%  (MF)
    (3.5, 0.0007),   # FI≈27%  (MF/HF)
    (4.5, 0.001),    # FI≈34%  (HF)
    (5.5, 0.011),
    (6.5, 0.021),
    (7.5, 0.031),
    (8.5, 0.041),
    (9.5, 0.050),    # FI≈53%  (VHF)
]


def eps_eff_linear(eps_void: float) -> float:
    """LINEAR volumetric mixing: eps_eff = (1-phi)*eps_void + phi*eps_granite.

    NOT CRIM (that is sqrt-eps mixing — src.physics.crim_bulk_eps); at
    rock/void contrast they differ <1% so this stays for the sweep ladder,
    but never reuse it for wet or high-contrast mixes.
    """
    return (1 - PHI_GRANITE) * eps_void + PHI_GRANITE * 6.1


def _snap(v: float) -> float:
    """Snap value to nearest cell multiple of DX."""
    return round(round(v / DX) * DX, 8)


def inflation_spheres(r_min: float = 0.020, r_max: float = 0.033,
                      target_phi: float = 0.38, seed: int = 42,
                      domain_x: float | None = None, domain_y: float | None = None,
                      ballast_bot: float | None = None, surface_z: float | None = None,
                      size_dist: str = "uniform", lognormal_sigma: float = 0.35):
    """
    Pack spheres into the ballast layer using RCPGenerator (C++ ADAM packing).

    Coordinate mapping (packing axis → gprMax Z-up):
      axis 0 → gprMax X (along-track)    → PackedSphere.x
      axis 1 → gprMax Z (vertical)       → PackedSphere.y
      axis 2 → gprMax Y (cross-track)    → PackedSphere.z

    Emit: SphereCommand(_snap(s.x), _snap(s.z), _snap(s.y), s.r, "granite")
    """
    import rcpgenerator

    dx_m  = domain_x  if domain_x  is not None else DOMAIN_X
    dy_m  = domain_y  if domain_y  is not None else DOMAIN_Y
    b_bot = ballast_bot if ballast_bot is not None else SUBGRADE_H
    s_z   = surface_z  if surface_z  is not None else SURFACE_Z
    pml_m = PML_CELLS * DX

    bx = dx_m - 2 * (pml_m + r_max)        # gprMax X extent of packing zone
    by = s_z - b_bot - 2 * (r_max + DX)    # gprMax Z extent (vertical)
    bz = dy_m - 2 * (pml_m + r_max)        # gprMax Y extent

    r_rep   = math.sqrt(r_min * r_max)
    vol_per = (4.0 / 3.0) * math.pi * r_rep ** 3
    n = min(int(target_phi * bx * by * bz / vol_per) + 1, 2000)

    d_geom = 2.0 * r_rep
    if size_dist == "lognormal":
        dist = {"type": "lognormal", "mu": math.log(d_geom), "sigma": lognormal_sigma}
    else:
        dist = {"type": "flat", "d_min": 2 * r_min, "d_max": 2 * r_max}

    p = rcpgenerator.Packing(N=n, Ndim=3, box=[bx, by, bz],
                             walls=[1, 1, 1], dist=dist, seed=seed, phi=0.01)
    p.relax(n_steps=5000, target_phi=target_phi)

    pos = np.array(p.positions)  # (N, 3) in [0,bx]×[0,by]×[0,bz]
    dia = np.array(p.diameters)  # (N,) diameters

    x_off = pml_m + r_max       # gprMax X start of packing zone
    y_off = b_bot + r_max + DX  # gprMax Z start (vertical, PackedSphere.y)
    z_off = pml_m + r_max       # gprMax Y start (PackedSphere.z)

    spheres = [
        PackedSphere(
            x=float(pos[i, 0]) + x_off,
            y=float(pos[i, 1]) + y_off,
            z=float(pos[i, 2]) + z_off,
            r=float(dia[i] / 2.0),
        )
        for i in range(len(pos))
    ]

    print(f"[RCP] {len(spheres)} spheres  phi={p.phi_final:.3f}  "
          f"r=[{dia.min()/2*1000:.0f}-{dia.max()/2*1000:.0f}] mm  "
          f"box={bx:.2f}x{by:.2f}x{bz:.2f} m")
    return spheres


def generate(out_path: Path, with_rocks: bool,
             void_eps: float = 1.0, void_sigma: float = 0.0,
             geometry_name: str | None = None,
             domain_xy: float | None = None,
             cfg: dict | None = None,
             config_path: Path | None = None,
             rock_shape: str = "sphere",
             sphere_file: Path | None = None,
             sphere_smoothing: str | None = None) -> None:
    """Generate a gprMax .in file.

    cfg:         config dict from load_config() — overrides all other keyword args.
    domain_xy:   override DOMAIN_X/Y (metres); ignored when cfg is given.
    config_path: path to the source TOML (if any) — embedded verbatim in the
                 deck header for reproducibility, matching the 2D "layers"
                 pipeline's convention (src/layer_scene_builder.py write_scene).
    """
    c = cfg or {}

    dx_m      = c.get("domain_x",   domain_xy if domain_xy is not None else DOMAIN_X)
    dy_m      = c.get("domain_y",   domain_xy if domain_xy is not None else DOMAIN_Y)
    dz_m      = c.get("domain_z",   DOMAIN_Z)
    tw        = c.get("time_window", TIME_WINDOW)

    sg_h      = c.get("subgrade_h",   SUBGRADE_H)
    sb_h      = c.get("subballast_h", SUBBALLAST_H)   # legacy single sub-ballast layer
    bl_h      = c.get("ballast_h",    BALLAST_H)
    standoff  = c.get("standoff",     STANDOFF)

    sg_eps    = c.get("subgrade_eps",   10.0)
    sg_sig    = c.get("subgrade_sig",   0.010)
    sb_eps    = c.get("subballast_eps", 7.5)
    sb_sig    = c.get("subballast_sig", 0.005)
    gr_eps    = c.get("granite_eps",    6.1)
    gr_sig    = c.get("granite_sig",    0.001)

    void_eps   = c.get("void_eps",   void_eps)
    void_sigma = c.get("void_sigma", void_sigma)

    seed       = c.get("seed",       42)
    r_min      = c.get("r_min",      0.020)
    r_max      = c.get("r_max",      0.033)
    target_phi = c.get("target_phi", 0.38)
    rock_shape = c.get("rock_shape", rock_shape)
    if rock_shape not in ROCK_SHAPES:
        raise ValueError(f"rock_shape must be one of {ROCK_SHAPES}, got '{rock_shape}'")

    # [[sub_layers]]: generic layers stacked above subgrade, bottom-to-top order.
    # Falls back to legacy subballast_h if not specified.
    sub_layers = c.get("sub_layers", [])
    if not sub_layers and sb_h > 0:
        sub_layers = [{"name": "subballast", "h": sb_h, "eps": sb_eps, "sigma": sb_sig}]

    # Derived geometry
    ballast_bot = sg_h + sum(l["h"] for l in sub_layers)
    surface_z   = ballast_bot + bl_h    # z of ballast top / air interface
    skid_z      = surface_z + standoff  # z of antenna skid bottom
    ant_cx      = dx_m / 2
    ant_cy      = dy_m / 2

    lines: list[str] = []

    def emit(cmd) -> None:
        lines.append(cmd.get_cmd_string() if hasattr(cmd, "get_cmd_string") else str(cmd))

    n_x = int(dx_m / DX)
    n_y = int(dy_m / DX)
    n_z = int(dz_m / DX)

    void_is_air = (void_eps == 1.0 and void_sigma == 0.0)
    void_mat    = "free_space" if void_is_air else f"void_eps{void_eps:.1f}"

    # ── Provenance / CONFIG_* replication block ──────────────────────────────
    # Mirrors src/layer_scene_builder.py write_scene's header so 3D decks carry
    # the same reproducibility metadata as the 2D "layers" pipeline (date, git
    # sha, CONFIG_* keys, full source TOML embedded verbatim).
    _BAR = "## " + "=" * 58
    emit(RawCommand(_BAR))
    emit(Header("Generated gprMax Input File (3D GSSI ballast scene)"))
    emit(RawCommand(f"## Date: {datetime.date.today().isoformat()}"))
    emit(RawCommand(f"## Git Version: {_git_sha()}"))
    if config_path is not None:
        emit(RawCommand(f"## Source config: {Path(config_path).name}"))
    emit(RawCommand(_BAR))
    emit(RawCommand("## CONFIG (replication)"))
    emit(RawCommand(f"## CONFIG_domain_xyz: {dx_m:g} {dy_m:g} {dz_m:g}"))
    emit(RawCommand(f"## CONFIG_dx: {DX:g}"))
    emit(RawCommand(f"## CONFIG_time_window: {tw:g}"))
    emit(RawCommand(f"## CONFIG_subgrade_h: {sg_h:g}"))
    emit(RawCommand(f"## CONFIG_ballast_h: {bl_h:g}"))
    emit(RawCommand(f"## CONFIG_standoff: {standoff:g}"))
    emit(RawCommand(f"## CONFIG_with_rocks: {with_rocks}"))
    if with_rocks:
        emit(RawCommand(f"## CONFIG_packing_seed: {seed}"))
        emit(RawCommand(f"## CONFIG_r_min: {r_min:g}"))
        emit(RawCommand(f"## CONFIG_r_max: {r_max:g}"))
        emit(RawCommand(f"## CONFIG_target_phi: {target_phi:g}"))
        emit(RawCommand(f"## CONFIG_void_eps: {void_eps:g}"))
        emit(RawCommand(f"## CONFIG_void_sigma: {void_sigma:g}"))
        emit(RawCommand(f"## CONFIG_rock_shape: {rock_shape}"))
    emit(RawCommand(_BAR))
    if config_path is not None and Path(config_path).exists():
        emit(RawCommand("## SOURCE TOML (embedded verbatim for reproducibility)"))
        for toml_line in Path(config_path).read_text(encoding="utf-8").splitlines():
            emit(RawCommand(f"## {toml_line}"))
        emit(RawCommand(_BAR))

    emit(Header("3D ballast scene — GSSI 400 MHz antenna"))
    emit(RawCommand(f"## Domain {dx_m}x{dy_m}x{dz_m} m  "
                    f"dx={DX} m  {n_x}x{n_y}x{n_z} cells (~{n_x*n_y*n_z//1_000_000}M)"))
    emit(DomainCommand(dx_m, dy_m, dz_m))
    emit(DxDyDzCommand(DX, DX, DX))
    emit(TimeWindowCommand(tw))

    emit(Header("Materials"))
    emit(MaterialCommand(5.1,   0.001, 1.0, 0.0, "ballast_clean"))
    emit(MaterialCommand(sg_eps, sg_sig, 1.0, 0.0, "subgrade"))
    emit(MaterialCommand(gr_eps, gr_sig, 1.0, 0.0, "granite"))
    seen_mats: set[str] = set()
    for layer in sub_layers:
        if layer["name"] not in seen_mats:
            emit(MaterialCommand(layer["eps"], layer["sigma"], 1.0, 0.0, layer["name"]))
            seen_mats.add(layer["name"])
    if not void_is_air:
        ee = eps_eff_linear(void_eps)
        emit(RawCommand(f"## void fill: eps={void_eps:.1f} sigma={void_sigma:.4f}  "
                        f"-> eps_eff(linear mix)={ee:.2f}"))
        emit(MaterialCommand(void_eps, void_sigma, 1.0, 0.0, void_mat))

    layer_desc = f"subgrade 0-{sg_h}m"
    z_cur = sg_h
    for l in sub_layers:
        layer_desc += f", {l['name']} {z_cur:.2f}-{z_cur+l['h']:.2f}m"
        z_cur += l["h"]
    layer_desc += f", ballast {ballast_bot:.2f}-{surface_z:.2f}m"
    emit(Header(f"Geometry  (Z-up: {layer_desc})"))
    emit(BoxCommand(0, 0, 0, dx_m, dy_m, sg_h, "subgrade"))
    z_cur = sg_h
    for layer in sub_layers:
        emit(BoxCommand(0, 0, z_cur, dx_m, dy_m, z_cur + layer["h"], layer["name"]))
        z_cur += layer["h"]

    if with_rocks:
        ee = eps_eff_linear(void_eps)
        emit(Header(
            f"Ballast rocks — granite spheres in {void_mat}  "
            f"(phi~{target_phi:.2f}, eps_eff≈{ee:.2f})"
        ))
        if not void_is_air:
            emit(BoxCommand(0, 0, ballast_bot, dx_m, dy_m, surface_z, void_mat))
        # rcpgenerator is NOT deterministic across runs even with a fixed seed
        # (C++ relaxation). For matched-pair A/B scenes (e.g. #sphere vs voxel
        # shapes on the SAME packing) pass sphere_file: first run packs and
        # saves x,y,z,r CSV; later runs reload it verbatim — the 3D analogue of
        # the 2D rock-library / config.rock_source_file pattern.
        sphere_file = c.get("sphere_file", sphere_file)
        if sphere_file is not None and Path(sphere_file).exists():
            arr = np.loadtxt(sphere_file, delimiter=",", skiprows=1, ndmin=2)
            spheres = [PackedSphere(x=row[0], y=row[1], z=row[2], r=row[3]) for row in arr]
            print(f"[gen] loaded {len(spheres)} spheres from {sphere_file}")
        else:
            spheres = inflation_spheres(r_min=r_min, r_max=r_max,
                                        target_phi=target_phi, seed=seed,
                                        domain_x=dx_m, domain_y=dy_m,
                                        ballast_bot=ballast_bot, surface_z=surface_z,
                                        size_dist=c.get("size_dist", "uniform"),
                                        lognormal_sigma=c.get("lognormal_sigma", 0.35))
            if sphere_file is not None:
                np.savetxt(sphere_file, [(s.x, s.y, s.z, s.r) for s in spheres],
                           delimiter=",", header="x,y,z,r", comments="")
                print(f"[gen] saved packing to {sphere_file}")
        if rock_shape == "sphere":
            # sphere_smoothing: None = gprMax default (dielectric smoothing ON);
            # 'n' for like-for-like comparison with voxel rocks (never smoothed)
            avg = c.get("sphere_smoothing", sphere_smoothing)
            for s in spheres:
                emit(SphereCommand(_snap(s.x), _snap(s.z), _snap(s.y), s.r,
                                   "granite", averaging=avg))
        else:
            # Voxel path: rasterise the SAME packing into an int16 array read
            # via #geometry_objects_read (-1 = keep void fill already built).
            # Files use bare names next to the deck — gprMax resolves them
            # against the input-file directory (Windows drive-letter caveat).
            shape_fn = {"voxel-sphere":       lambda: sphere_shape,
                        "voxel-ellipsoid":    lambda: make_ellipsoid_shape(seed=seed),
                        "voxel-polyhedron":   lambda: make_polyhedron_shape(seed=seed),
                        "voxel-sphere-small": lambda: make_scaled_sphere_shape(0.745),
                        }[rock_shape]()
            z0 = _snap(ballast_bot)
            n_zb = int(round((_snap(surface_z) - z0) / DX))
            data = voxelize_rocks(
                rocks=spheres_to_domain_coords(spheres),
                origin=(0.0, 0.0, z0),
                size_cells=(n_x, n_y, n_zb),
                dx=DX,
                shape_fn=shape_fn,
            )
            h5_name  = f"{out_path.stem}_rocks.h5"
            mat_name = f"{out_path.stem}_rock_materials.txt"
            write_geometry_hdf5(out_path.parent / h5_name, data, DX)
            write_materials_file(out_path.parent / mat_name,
                                 [MaterialCommand(gr_eps, gr_sig, 1.0, 0.0, "granite")])
            n_rock = int((data >= 0).sum())
            phi_vox = n_rock / data.size
            emit(RawCommand(f"## Voxelised rocks ({rock_shape}): {len(spheres)} rocks, "
                            f"{n_rock} cells, slab fill fraction {phi_vox:.3f}"))
            emit(GeometryObjectsReadCommand(0.0, 0.0, z0, h5_name, mat_name))
            print(f"[gen] voxel rocks: {h5_name}  ({n_x}x{n_y}x{n_zb} int16, "
                  f"{n_rock} rock cells, phi_slab={phi_vox:.3f})")
        print(f"[gen] {len(spheres)} rocks ({rock_shape}) | void={void_mat} | eps_eff~{ee:.2f} "
              f"| domain={dx_m:.2f}x{dy_m:.2f}m | ballast={ballast_bot:.2f}-{surface_z:.2f}m")
    else:
        emit(BoxCommand(0, 0, ballast_bot, dx_m, dy_m, surface_z, "ballast_clean"))

    sleepers = c.get("sleepers", [])
    if sleepers:
        emit(Header(f"Concrete sleepers ({len(sleepers)})  "
                    f"z_top={surface_z:.3f}m  eps={sleepers[0]['eps']}"))
        emit(MaterialCommand(sleepers[0]["eps"], sleepers[0]["sigma"], 1.0, 0.0, "concrete"))
        for sl in sleepers:
            sl_xmin  = sl["x_min"]
            sl_xmax  = sl["x_max"]
            sl_depth = sl["depth"]
            # Full Y span — sleeper runs cross-track; overwrites any spheres in this zone
            emit(BoxCommand(sl_xmin, 0, surface_z - sl_depth,
                            sl_xmax, dy_m, surface_z, "concrete"))
            print(f"[gen] sleeper: x={sl_xmin:.2f}-{sl_xmax:.2f}m  "
                  f"z={surface_z - sl_depth:.3f}-{surface_z:.3f}m")

    geo_name = geometry_name or out_path.stem
    emit(Header(f"Geometry view — open {geo_name}.vti in ParaView"))
    emit(GeometryViewCommand(0, 0, 0, dx_m, dy_m, dz_m, DX, DX, DX, geo_name, "n"))

    emit(Header(
        f"GSSI 400 MHz antenna — skid bottom z={skid_z:.3f} m, "
        f"centred at x={ant_cx:.3f} y={ant_cy:.3f}"
    ))
    emit(PythonBlockCommand(
        code=(
            f"from user_libs.antennas.GSSI import antenna_like_GSSI_400\n"
            f"antenna_like_GSSI_400({ant_cx:.3f}, {ant_cy:.3f}, {skid_z:.3f}, resolution={DX})"
        ),
    ))

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[gen] {out_path}  ({n_x}x{n_y}x{n_z} cells)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=None,
                    help="TOML scene config file (overrides all geometry defaults)")
    ap.add_argument("--rocks", action="store_true",
                    help="Add granite spheres to ballast layer")
    ap.add_argument("--void-eps", type=float, default=1.0,
                    help="Permittivity of void fill material (default=1.0 air); requires --rocks")
    ap.add_argument("--void-sigma", type=float, default=0.0,
                    help="Conductivity of void fill (S/m, default=0.0); requires --rocks")
    ap.add_argument("--rock-shape", choices=ROCK_SHAPES, default="sphere",
                    help="Rock geometry: native #sphere (default), or voxelised "
                         "shapes via #geometry_objects_read (voxel-sphere = "
                         "control that replicates #sphere cell-for-cell)")
    ap.add_argument("--sphere-file", type=Path, default=None,
                    help="Packing CSV (x,y,z,r): saved on first run, reloaded on "
                         "later runs — required for matched-pair A/B because "
                         "rcpgenerator is not deterministic across runs")
    ap.add_argument("--sphere-smoothing", choices=["y", "n"], default=None,
                    help="Dielectric smoothing for native #sphere rocks (default: "
                         "gprMax default = on). Use 'n' to compare against voxel "
                         "rocks, which never get smoothing")
    ap.add_argument("--out", default=None,
                    help="Output .in path (default: auto-named)")
    args = ap.parse_args()

    cfg = load_config(args.config) if args.config else None

    with_rocks  = args.rocks or (cfg is not None)
    void_eps    = args.void_eps
    void_sigma  = args.void_sigma

    if cfg is not None:
        void_eps   = cfg.get("void_eps",   void_eps)
        void_sigma = cfg.get("void_sigma", void_sigma)
        with_rocks = True   # TOML scenes always include rocks

    if (void_eps != 1.0 or void_sigma != 0.0) and not with_rocks:
        ap.error("--void-eps / --void-sigma require --rocks")

    if args.config:
        suffix = args.config.stem
    elif with_rocks:
        suffix = f"rocks_veps{void_eps:.1f}" if void_eps != 1.0 else "rocks_clean"
    else:
        suffix = "clean"
    if args.rock_shape != "sphere" and not args.config:
        suffix += f"_{args.rock_shape.replace('-', '_')}"
    out_path = Path(args.out) if args.out else Path(f"gssi_400_3d_{suffix}.in")
    generate(out_path, with_rocks=with_rocks,
             void_eps=void_eps, void_sigma=void_sigma, cfg=cfg,
             config_path=args.config, rock_shape=args.rock_shape,
             sphere_file=args.sphere_file, sphere_smoothing=args.sphere_smoothing)


if __name__ == "__main__":
    main()
