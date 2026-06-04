"""
Config extraction and recovery from gprMax .in files.

Allows reconstructing GeneratorConfig from embedded CONFIG_* headers in .in files,
enabling exact replication of geometries using the same random seed.

Also hosts ``parse_metadata_comments`` — the single, dependency-light parser for
the generic ``## key: value`` header substrate shared by the geometry parser,
the A-scan visualizer, and the scene repository. (The CONFIG_*/SOURCE_* readers
below are a separate, type-inferred replication sublanguage and are intentionally
kept distinct — see docs/architecture/IO_CONSOLIDATION_PLAN.md.)
"""

import json
from pathlib import Path
from typing import Dict, Any, Iterable


def parse_metadata_comments(lines: Iterable[str]) -> Dict[str, Any]:
    """
    Parse ``## key: value`` header comments into a dict with JSON-decoded values.

    This is the one place that interprets gprMax metadata comments. Values that
    parse as JSON (numbers, true/false, lists) are decoded; everything else is
    kept as a stripped string.

    Args:
        lines: Any iterable of strings — an open file handle, ``content.splitlines()``,
            etc. The whole iterable is scanned (metadata may appear anywhere).

    Returns:
        Dict mapping metadata keys to JSON-decoded values.
    """
    meta: Dict[str, Any] = {}
    for raw in lines:
        line = raw.strip()
        if line.startswith("## ") and ":" in line:
            key, _, val = line[3:].partition(":")
            k, v = key.strip(), val.strip()
            try:
                meta[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                meta[k] = v
    return meta


def parse_metadata_file(in_path) -> Dict[str, Any]:
    """Read a .in file and return its ``## key: value`` metadata (see
    ``parse_metadata_comments``)."""
    with open(in_path, encoding="utf-8", errors="replace") as fh:
        return parse_metadata_comments(fh)


def extract_config_from_in_file(in_path: str) -> Dict[str, Any]:
    """
    Extract CONFIG_* parameters from .in file header comments.

    Parses lines starting with "## CONFIG_" and extracts key-value pairs.
    Attempts type conversion for common types (bool, int, float).

    Args:
        in_path: Path to .in file

    Returns:
        Dict mapping lowercase config keys to values
        Example: {"center_freq_hz": 1.5e9, "angular_rocks": True, ...}

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is not a valid .in file
    """
    config_dict = {}

    try:
        with open(in_path) as f:
            for line in f:
                # Stop at first non-header line
                if line.strip() and not line.startswith("##"):
                    break

                if "CONFIG_" in line:
                    # Parse: ## CONFIG_key: value
                    if ":" in line:
                        parts = line.split(":", 1)
                        key_part = parts[0].strip()

                        # Extract key (remove ## and CONFIG_)
                        if key_part.startswith("##"):
                            key_part = key_part[2:].strip()
                        if key_part.startswith("CONFIG_"):
                            key = key_part[7:].lower()  # Remove CONFIG_ prefix
                        else:
                            continue

                        # Extract and parse value
                        value = parts[1].strip()

                        # Type inference
                        if value.lower() == "true":
                            config_dict[key] = True
                        elif value.lower() == "false":
                            config_dict[key] = False
                        elif value.isdigit():
                            config_dict[key] = int(value)
                        else:
                            # Try float
                            try:
                                config_dict[key] = float(value)
                            except ValueError:
                                # Keep as string
                                config_dict[key] = value
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {in_path}")

    if not config_dict:
        raise ValueError(f"No CONFIG_* headers found in {in_path}. File may be outdated.")

    return config_dict


def reconstruct_generator_config(in_path: str):
    """
    Reconstruct GeneratorConfig from .in file headers for replication.

    Extracts CONFIG_* parameters from .in file and rebuilds GeneratorConfig
    using frequency-aware domain scaling (create_physically_perfect).

    This allows exact geometry replication when using the same base_seed.

    Args:
        in_path: Path to .in file with embedded config

    Returns:
        Tuple of (GeneratorConfig, sampled_params_dict)
        sampled_params_dict contains extracted PVC/moisture if available

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If required config parameters are missing
    """
    from .config import GeneratorConfig

    config_dict = extract_config_from_in_file(in_path)

    # Map header keys to constructor params (handle both old and new naming)
    center_freq = config_dict.get("center_freq_hz", 1.5e9)

    # Use actual_seed if available (for batch mode), otherwise use base_seed
    if "actual_seed" in config_dict:
        final_seed = int(config_dict.get("actual_seed"))
    else:
        final_seed = int(config_dict.get("base_seed")) if config_dict.get("base_seed") else None

    # Reconstruct using frequency-aware constructor
    # This ensures domain dimensions scale correctly per IEEE 2025 guidelines
    config = GeneratorConfig.create_physically_perfect(
        center_freq_hz=center_freq,
        rock_packing_algorithm=config_dict.get("rock_packing_algorithm", "circlify"),
        rock_psd_type=config_dict.get("packing_psd_type", "uniform"),
        angular_rocks=config_dict.get("angular_rocks", False),
        rock_sides=int(config_dict.get("rock_sides", 6)),
        num_receivers=int(config_dict.get("num_receivers", 1)),
        receiver_spacing=float(config_dict.get("receiver_spacing", 0.05)),
        base_seed=final_seed,
    )

    # Extract sampled parameters if available (PVC/moisture from original generation)
    sampled_params = {}
    if "pvc_sampled" in config_dict:
        sampled_params['pvc'] = float(config_dict.get("pvc_sampled"))
    if "moisture_sampled" in config_dict:
        sampled_params['moisture'] = float(config_dict.get("moisture_sampled"))

    return config, sampled_params


def extract_sources_from_in_file(in_path: str) -> Dict[str, str]:
    """
    Extract SOURCE_* markers indicating where parameters came from.

    Parses lines starting with "## SOURCE_" and maps parameter names to their sources.

    Source types:
    - CLI_OVERRIDE: explicitly set via command-line flag
    - SAMPLED: randomized from distribution
    - BATCH_AUTO: automatically assigned in batch mode
    - DEFAULT: using hardcoded/config default

    Args:
        in_path: Path to .in file

    Returns:
        Dict mapping parameter names to source type
        Example: {"pvc": "CLI_OVERRIDE", "moisture": "SAMPLED", "actual_seed": "BATCH_AUTO"}
    """
    sources = {}

    try:
        with open(in_path) as f:
            for line in f:
                # Stop at first non-header line
                if line.strip() and not line.startswith("##"):
                    break

                if "SOURCE_" in line and ":" in line:
                    parts = line.split(":", 1)
                    key_part = parts[0].strip()

                    # Extract key (remove ## and SOURCE_)
                    if key_part.startswith("##"):
                        key_part = key_part[2:].strip()
                    if key_part.startswith("SOURCE_"):
                        param_name = key_part[7:].lower()  # Remove SOURCE_ prefix
                        source_type = parts[1].strip()
                        sources[param_name] = source_type
                    else:
                        continue

    except FileNotFoundError:
        return {}

    return sources


def get_config_summary(in_path: str) -> str:
    """
    Generate a human-readable summary of config from .in file.

    Args:
        in_path: Path to .in file

    Returns:
        Formatted string describing configuration

    Example output:
        Frequency: 400 MHz
        Angular Rocks: Yes (hexagon)
        Packing: circlify (uniform PSD)
        Seed: 42
    """
    config_dict = extract_config_from_in_file(in_path)

    freq_hz = config_dict.get("center_freq_hz", 1.5e9)
    freq_mhz = freq_hz / 1e6

    angular = config_dict.get("angular_rocks", False)
    sides = config_dict.get("rock_sides", 6) if angular else None
    packing = config_dict.get("rock_packing_algorithm", "unknown")
    psd = config_dict.get("packing_psd_type", "unknown")
    seed = config_dict.get("base_seed", "None")
    num_rx = config_dict.get("num_receivers", 1)

    lines = [
        f"Frequency: {freq_mhz:.0f} MHz",
        f"Rocks: {'Angular' if angular else 'Circular'}" + (f" ({sides}-sided)" if angular else ""),
        f"Packing: {packing} ({psd} PSD)",
        f"Receivers: {num_rx}",
        f"Seed: {seed}",
    ]

    return "\n".join(lines)
