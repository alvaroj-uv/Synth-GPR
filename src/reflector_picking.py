"""
Physics-based reflector picking and model generation: Hilbert-envelope horizon picks, Sussmann travel-time-to-depth, and picks -> gprMax layers TOML.

Split out of signal_processing.py (2026-07-02, debt D12); import via src.signal_processing.
"""
import numpy as np
from scipy.signal import hilbert


# ─────────────────────────────────────────────────────────────────────────────
# Physics-based reflector travel-time picker  (Sussmann 2000, Eq. 1)
# ─────────────────────────────────────────────────────────────────────────────

C_M_NS = 0.299_792_458   # speed of light in m/ns


def pick_reflector(
    signal: np.ndarray,
    dt_s: float,
    skip_after_direct_ns: float = 2.5,
    min_prominence: float = 0.05,
    search_window_ns: float | None = None,
) -> dict:
    """Pick the first subsurface reflector peak using the Hilbert envelope.

    Implements the reflector-picking step required before applying Sussmann (2000)
    Eq. 1: d = c · t_oneway / sqrt(eps).  The two-way travel time dt_twoway_ns
    returned here maps directly to t_oneway = dt_twoway_ns / 2.

    Algorithm:
      1. Compute the Hilbert envelope.
      2. Locate the direct-wave peak (global maximum of the envelope).
      3. Skip `skip_after_direct_ns` ns after the direct-wave peak to avoid
         ringing (default 2.5 ns ≈ 1 period at 400 MHz).
      4. Find the first local maximum in the envelope after the skip that has
         at least `min_prominence` * direct-wave-amplitude prominence.

    Reference:
        Sussmann, T.R. et al. (2000). Development of GPR for Railway Infrastructure
        Condition Detection. TRB 2000 Annual Meeting, Paper 00-0558. [Eq. 1]

    Args:
        signal:                1-D numpy array (any amplitude units).
        dt_s:                  Time step in seconds.
        skip_after_direct_ns:  Minimum time gap (ns) between direct-wave peak
                               and the search window.  Default 2.5 ns covers
                               ~1 period of a 400 MHz antenna.
        min_prominence:        Fraction of direct-wave amplitude used as the
                               peak-detection prominence threshold (0–1).
        search_window_ns:      Optional: restrict search to the first N ns
                               after the skip window.  None = search to end.

    Returns:
        dict with keys:
          t_direct_ns    – time of direct-wave peak (ns)
          t_reflector_ns – time of first reflector peak (ns), or NaN if not found
          dt_twoway_ns   – t_reflector_ns - t_direct_ns  (two-way travel time, ns)
          peak_ratio     – reflector amplitude / direct amplitude
          found          – bool
    """
    from scipy.signal import hilbert, find_peaks

    dt_ns  = dt_s * 1e9
    n      = len(signal)
    t_ns   = np.arange(n) * dt_ns
    env    = np.abs(hilbert(signal))

    # 1. Direct-wave peak
    direct_idx = int(np.argmax(env))
    t_direct   = t_ns[direct_idx]
    direct_amp = env[direct_idx]
    if direct_amp == 0:
        return dict(t_direct_ns=t_direct, t_reflector_ns=np.nan,
                    dt_twoway_ns=np.nan, peak_ratio=np.nan, found=False)

    # 2. Search window start
    skip_samples = int(np.ceil(skip_after_direct_ns / dt_ns))
    search_start = direct_idx + skip_samples
    if search_start >= n:
        return dict(t_direct_ns=t_direct, t_reflector_ns=np.nan,
                    dt_twoway_ns=np.nan, peak_ratio=np.nan, found=False)

    # 3. Search window end
    if search_window_ns is not None:
        search_end = min(n, search_start + int(search_window_ns / dt_ns))
    else:
        search_end = n

    segment  = env[search_start:search_end]
    threshold = min_prominence * direct_amp

    # 4. Find peaks in segment
    min_dist_samples = max(1, int(1.0 / dt_ns))   # at least 1 ns apart
    peaks, props = find_peaks(
        segment,
        height=threshold,
        distance=min_dist_samples,
        prominence=threshold * 0.5,
    )

    if len(peaks) == 0:
        return dict(t_direct_ns=t_direct, t_reflector_ns=np.nan,
                    dt_twoway_ns=np.nan, peak_ratio=np.nan, found=False)

    refl_idx_in_seg = peaks[0]
    refl_idx        = search_start + refl_idx_in_seg
    t_reflector     = t_ns[refl_idx]
    dt_twoway       = t_reflector - t_direct

    return dict(
        t_direct_ns    = float(t_direct),
        t_reflector_ns = float(t_reflector),
        dt_twoway_ns   = float(dt_twoway),
        peak_ratio     = float(env[refl_idx] / direct_amp),
        found          = True,
    )


def reflector_to_depth(dt_twoway_ns: float, eps: float = 3.45) -> float:
    """Convert two-way travel time (ns) to reflector depth (m).

    Uses Sussmann (2000) Eq. 1:  d = c * t_oneway / sqrt(eps)
    where t_oneway = dt_twoway / 2.

    Args:
        dt_twoway_ns: Two-way travel time in ns (from pick_reflector).
        eps:          Relative dielectric permittivity of the layer above the
                      reflector.  Default 3.45 = clean dry ballast.

    Returns:
        Estimated depth in metres.  Returns NaN if input is NaN.
    """
    if np.isnan(dt_twoway_ns):
        return np.nan
    t_oneway_ns = dt_twoway_ns / 2.0
    return C_M_NS * t_oneway_ns / np.sqrt(eps)


def picks_to_layer_toml(
    surface_time_ns: float,
    interface_times_ns: list,
    eps_layers: list,
    sigma_layers: list,
    layer_names: list,
    out_toml,
    freq_hz: float = 420e6,
    antenna_standoff_m: float = 0.05,
    domain_x: float = 0.5,
    dx: float = 0.003,
    time_window_s: float = 50e-9,
    subgrade_pad_m: float = 0.30,
    pk_m: float = None,
    title: str = None,
) -> 'Path':
    """Convert B-scan horizon picks into a gprMax-ready TOML layer file.

    Translates picked two-way travel times from a real GPR B-scan into physical
    layer thicknesses and writes a ``mode = "layers"`` TOML that
    ``scripts/pipeline/generate_gprmax_scenes.py`` can consume directly.

    **Depth conversion** (Sussmann 2000, :func:`reflector_to_depth`)::

        thickness_i = c × (t_i − t_{i-1}) / (2 × sqrt(eps_i))

    where *t* is two-way travel time in ns and *c* = 0.2998 m/ns.

    Args:
        surface_time_ns:     Two-way travel time (ns) to the ballast surface
                             in the raw B-scan (includes any hardware trigger
                             delay — used only to measure the *interval* to the
                             next interface, not to infer antenna height).
        interface_times_ns:  Two-way times (ns) for each subsequent interface,
                             ordered top-to-bottom.  E.g. [12.5, 20.0] gives
                             a ballast layer and a subgrade interface.
        eps_layers:          Relative dielectric permittivity for each layer
                             (same length as *interface_times_ns*).
                             Typical values — clean ballast: 3.45–5.1,
                             fouled ballast: 9–12, subgrade: 10–15.
        sigma_layers:        Electrical conductivity (S/m) for each layer.
                             Typical values — dry ballast: 0.001,
                             fouled/wet: 0.01–0.05.
        layer_names:         Human-readable name for each layer (same length).
        out_toml:            Output TOML path (created/overwritten).
        freq_hz:             Antenna centre frequency in Hz (default 420 MHz).
        antenna_standoff_m:  Physical antenna height above the ballast surface
                             in metres (default 0.05 m = 5 cm, GSSI-400 on-rail).
                             This controls *antenna_clearance* in the TOML;
                             the builder halves it to get the actual standoff.
        domain_x:            Domain width in metres (default 0.5 m, single A-scan).
        dx:                  Spatial step in metres (default 3 mm).
        time_window_s:       Simulation time window in seconds (default 50 ns).
        subgrade_pad_m:      Extra thickness added below the deepest picked
                             interface so the domain is not truncated at the
                             boundary (default 0.30 m).
        pk_m:                Optional track position in metres — appended to the
                             output filename and TOML title for provenance.
        title:               Optional simulation title; auto-generated if None.

    Returns:
        Path to the written TOML file.

    Example::

        from src.signal_processing import picks_to_layer_toml

        picks_to_layer_toml(
            surface_time_ns   = 5.3,
            interface_times_ns= [12.8, 20.1],
            eps_layers        = [5.1,  12.0],
            sigma_layers      = [0.001, 0.05],
            layer_names       = ['ballast', 'subgrade'],
            out_toml          = 'experiments/site1_pk5000m.toml',
            pk_m              = 5000.0,
        )

    References:
        Sussmann et al. (2000), TRB Annual Meeting — d = c·t_oneway/√ε.
        Rojas-Vivanco et al. (2025), Transportation Geotechnics 55:101701.
    """
    from pathlib import Path as _Path
    import textwrap

    out_toml = _Path(out_toml)
    n = len(interface_times_ns)

    if not (len(eps_layers) == len(sigma_layers) == len(layer_names) == n):
        raise ValueError(
            'interface_times_ns, eps_layers, sigma_layers, layer_names '
            'must all have the same length'
        )

    # ── Compute layer thicknesses ─────────────────────────────────────────────
    t_prev = surface_time_ns
    thicknesses = []
    for t_curr, eps in zip(interface_times_ns, eps_layers):
        dt_ns = t_curr - t_prev
        if dt_ns <= 0:
            raise ValueError(
                f'interface time {t_curr:.2f} ns is not greater than '
                f'previous time {t_prev:.2f} ns'
            )
        thicknesses.append(reflector_to_depth(dt_ns, eps=eps))
        t_prev = t_curr

    # ── Build TOML string ─────────────────────────────────────────────────────
    stem = out_toml.stem
    if pk_m is not None:
        stem = f'from_picks_pk{int(pk_m):05d}m'
    in_name = stem + '.in'

    if title is None:
        pk_str = f' | pk={pk_m:.0f} m' if pk_m is not None else ''
        title = (
            f'From B-scan picks{pk_str} | '
            f'freq={freq_hz/1e6:.0f} MHz | '
            + ', '.join(
                f'{n}:{e:.1f}' for n, e in zip(layer_names, eps_layers)
            )
        )

    lines = [
        f'# Auto-generated by picks_to_layer_toml() — do not edit by hand.',
        f'# Source: B-scan horizon picks'
        + (f' at PK {pk_m:.0f} m' if pk_m is not None else ''),
        f'# surface_time_ns = {surface_time_ns:.2f}',
        f'# interface_times_ns = {interface_times_ns}',
        '',
        '[job]',
        'mode   = "layers"',
        'render = true',
        f'output = "{in_name}"',
        '',
        '[sim]',
        f'freq_hz           = {freq_hz:.6g}',
        f'domain_x          = {domain_x}',
        f'dx                = {dx}',
        f'antenna_clearance = {2 * antenna_standoff_m:.4f}   '
        f'# actual standoff = {antenna_standoff_m:.4f} m (builder halves this)',
        'air_buffer        = 0.10',
        f'time_window       = {time_window_s:.2e}',
        'antenna_mode      = "bistatic"',
        'num_receivers     = 1',
        'receiver_spacing  = 0.03',
        f'title             = "{title}"',
        '',
        '[source]',
        'amplitude    = 1.0',
        'polarization = "z"',
        '',
    ]

    for name, thick, eps, sigma in zip(
            layer_names, thicknesses, eps_layers, sigma_layers):
        lines += [
            '[[layer]]',
            f'name      = "{name}"',
            f'thickness = {thick:.4f}   # metres — from pick interval',
            f'eps       = {eps}',
            f'sigma     = {sigma}',
            '',
        ]

    # Padding layer (repeat last eps/sigma so it is physically consistent)
    lines += [
        '[[layer]]',
        f'name      = "{layer_names[-1]}_pad"',
        f'thickness = {subgrade_pad_m:.4f}   # padding below deepest pick',
        f'eps       = {eps_layers[-1]}',
        f'sigma     = {sigma_layers[-1]}',
        '',
    ]

    out_toml.parent.mkdir(parents=True, exist_ok=True)
    out_toml.write_text('\n'.join(lines), encoding='utf-8')
    return out_toml


