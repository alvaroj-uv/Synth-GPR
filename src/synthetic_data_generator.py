from __future__ import annotations
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# Utility: FI and classification
# ------------------------------------------------------------

def compute_fi(rock_h: float, foul_h: float) -> float:
    total = rock_h + foul_h
    if total <= 0:
        return 0.0
    return (foul_h / total) * 100.0


def classify_fi(FI: float) -> str:
    # Selig & Waters style bands - short codes
    if FI < 20:
        return "CL"
    elif FI < 40:
        return "MF"
    elif FI < 60:
        return "F"
    else:
        return "HF"


# ------------------------------------------------------------
# Config dataclass
# ------------------------------------------------------------

@dataclass
class GeneratorConfig:
    # Geometry and grid
    domain_x: float = 0.5
    domain_y: float = 1.0
    domain_z: float = 0.001

    dx: float = 0.005
    dy: float = 0.0005
    dz: float = 0.001

    # Time window
    time_window: float = 1.5e-8

    # Waveform / antenna
    center_freq: float = 1.5e9  # Hz
    tx_x: float = 0.300
    rx_x: float = 0.35
    tx_rx_y: float = 0.904
    tx_rx_z: float = 0.0
    add_waveform: bool = True
    add_source: bool = True
    add_geometry_view: bool = False

    # Ballast/subgrade nominal depths (y-direction)
    min_ballast_thickness: float = 0.18  # rock + foul
    max_ballast_thickness: float = 0.30  # rock + foul

    min_foul_thickness: float = 0.00
    max_foul_thickness: float = 0.10

    formation_thickness: float = 0.10
    subgrade_thickness: float = 0.05

    # Material ranges
    # Clean ballast
    bal_rock_eps: float = 4.5
    bal_rock_sigma: float = 0.001

    # Base fouled ballast range (dry)
    bal_foul_eps_min: float = 6.0
    bal_foul_eps_max: float = 8.0
    bal_foul_sigma_min: float = 0.002
    bal_foul_sigma_max: float = 0.01

    # Wet fouling amplification factors
    wet_eps_factor_min: float = 1.2
    wet_eps_factor_max: float = 1.8
    wet_sigma_factor_min: float = 2.0
    wet_sigma_factor_max: float = 5.0

    # Pockets
    max_pockets: int = 4
    pocket_eps_min: float = 7.0
    pocket_eps_max: float = 10.0
    pocket_sigma_min: float = 0.005
    pocket_sigma_max: float = 0.03

    # Vertical gradient: number of fouled sublayers
    grad_min_layers: int = 2
    grad_max_layers: int = 5

    # Random seed base (optional)
    base_seed: int | None = None


# ------------------------------------------------------------
# Scenario generator
# ------------------------------------------------------------

class BallastScenarioGenerator:
    def __init__(self, config: GeneratorConfig):
        self.cfg = config
        if self.cfg.base_seed is not None:
            random.seed(self.cfg.base_seed)
            np.random.seed(self.cfg.base_seed)

    # --------------- main public API -----------------

    def generate_dataset(
        self,
        out_dir: str | Path,
        n_samples: int = 50,
        csv_name: str = "metadata.csv",
    ) -> pd.DataFrame:
        """
        Generate n_samples .in files under out_dir and a CSV with metadata.
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        metadata_rows: List[Dict[str, Any]] = []

        for idx in range(n_samples):
            # Decide scenario
            scenario_type = random.choice(
                ["uniform", "vertical_gradient", "pockets", "wet"]
            )

            # Sample geometry (ballast and fouling thicknesses)
            rock_h, foul_h = self._sample_heights()

            # Compute FI and class
            FI = compute_fi(rock_h, foul_h)
            FI_class = classify_fi(FI)

            # File naming
            base_name = f"sample_{idx:04d}_{scenario_type}"
            in_filename = f"{base_name}.in"

            # Build content
            in_text, scenario_info = self._compose_file(
                base_name=base_name,
                scenario_type=scenario_type,
                rock_h=rock_h,
                foul_h=foul_h,
                FI=FI,
                FI_class=FI_class,
            )

            # Normalize line endings to CRLF for Windows/gprMax compatibility
            lines = in_text.split("\n")
            text_crlf = "\r\n".join(lines) + "\r\n"

            # Write file
            (out_dir / in_filename).write_text(text_crlf, encoding="utf-8")

            # Collect metadata
            row = {
                "sample_id": idx,
                "filename": in_filename,
                "scenario_type": scenario_type,
                "rock_height_m": rock_h,
                "foul_height_m": foul_h,
                "FI_percent": FI,
                "FI_class": FI_class,
            }
            row.update(scenario_info)  # add scenario-specific fields
            metadata_rows.append(row)

        df = pd.DataFrame(metadata_rows)
        df.to_csv(out_dir / csv_name, index=False)
        return df

    # --------------- geometry sampling -----------------

    def _sample_heights(self) -> tuple[float, float]:
        """
        Sample rock and foul heights in a physically realistic way.
        """
        cfg = self.cfg
        total_ballast = random.uniform(
            cfg.min_ballast_thickness, cfg.max_ballast_thickness
        )
        foul = random.uniform(cfg.min_foul_thickness, cfg.max_foul_thickness)
        foul = min(foul, total_ballast)  # just in case
        rock = total_ballast - foul
        return rock, foul

    # --------------- file composition -----------------

    def _compose_file(
        self,
        base_name: str,
        scenario_type: str,
        rock_h: float,
        foul_h: float,
        FI: float,
        FI_class: str,
    ) -> tuple[str, Dict[str, Any]]:
        """
        Create the text of the .in file and return (text, scenario_metadata).
        """
        cfg = self.cfg

        # Base fouled material properties
        base_foul_eps = random.uniform(cfg.bal_foul_eps_min, cfg.bal_foul_eps_max)
        base_foul_sigma = random.uniform(
            cfg.bal_foul_sigma_min, cfg.bal_foul_sigma_max
        )

        scenario_info: Dict[str, Any] = {
            "bal_rock_eps": cfg.bal_rock_eps,
            "bal_rock_sigma": cfg.bal_rock_sigma,
            "bal_foul_eps_base": base_foul_eps,
            "bal_foul_sigma_base": base_foul_sigma,
        }

        # --- SECTIONS ---
        header_lines: List[str] = []
        setup_lines: List[str] = []
        material_lines: List[str] = []
        geometry_lines: List[str] = []
        
        # 1. Header
        header_lines.append("## ------------------------------------------------------------")
        header_lines.append("## Generated gprMax Input File")
        header_lines.append(f"## Scenario: {scenario_type}")
        header_lines.append(f"## Rock Height: {rock_h:.4f}")
        header_lines.append(f"## Foul Height: {foul_h:.4f}")
        header_lines.append(f"## FI (%): {FI:.2f}")
        header_lines.append(f"## FI class: {FI_class}")
        header_lines.append("## ------------------------------------------------------------")

        # 2. Setup (Domain, Time, etc.)
        setup_lines.append(f"#title: {FI_class}")
        setup_lines.append(f"#domain: {cfg.domain_x} {cfg.domain_y} {cfg.domain_z}")
        setup_lines.append(f"#dx_dy_dz: {cfg.dx} {cfg.dy} {cfg.dz}")
        setup_lines.append(f"#time_window: {cfg.time_window}")

        # 3. Materials (Base definitions)
        material_lines.append(f"#material: {cfg.bal_rock_eps} {cfg.bal_rock_sigma} 1 0 bal_rock")
        material_lines.append(f"#material: {base_foul_eps} {base_foul_sigma} 1 0 bal_foul")
        material_lines.append("#material: 7.0 0.01 1 0 subgrade")
        material_lines.append("#material: 10.0 0.03 1 0 formation")

        # 4. Waveform
        if cfg.add_waveform:
            setup_lines.append(f"#waveform: ricker 1 {cfg.center_freq:.3e} src")

        # 5. Geometry - Painter's Algorithm (Back to Front)
        
        # A. Background (Free Space)
        geometry_lines.append("## Fondo completo (free_space)")
        geometry_lines.append(f"#box: 0.0 0.0 0.0   {cfg.domain_x} {cfg.domain_y} {cfg.domain_z} free_space")

        # B. Subgrade
        y_subgrade = cfg.subgrade_thickness
        geometry_lines.append(f"## Layer: subgrade (0.00–{y_subgrade:.4f})")
        geometry_lines.append(f"#box: 0.0 0.0 0.0   {cfg.domain_x} {y_subgrade:.4f} {cfg.domain_z} subgrade")

        # C. Formation
        y_formation_top = y_subgrade + cfg.formation_thickness
        geometry_lines.append(f"## Layer: formation ({y_subgrade:.4f}–{y_formation_top:.4f})")
        geometry_lines.append(f"#box: 0.0 {y_subgrade:.4f} 0.0   {cfg.domain_x} {y_formation_top:.4f} {cfg.domain_z} formation")

        # D. Ballast Region (Fouled + Rock)
        ballast_bottom = y_formation_top
        foul_top = ballast_bottom + foul_h
        rock_top = ballast_bottom + foul_h + rock_h
        rock_top = min(rock_top, cfg.domain_y)

        # 1. Define the entire ballast layer as Clean Rock (Largest Area for this section)
        geometry_lines.append(f"## Layer: bal_rock (Entire Ballast: {ballast_bottom:.4f}–{rock_top:.4f})")
        geometry_lines.append(f"#box: 0.0 {ballast_bottom:.4f} 0.0   {cfg.domain_x} {rock_top:.4f} {cfg.domain_z} bal_rock")

        # 2. Overwrite with Fouling (Smaller/Inner Area)
        if scenario_type == "uniform":
            scenario_info.update(
                self._add_uniform_fouling(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma)
            )
        elif scenario_type == "vertical_gradient":
            scenario_info.update(
                self._add_vertical_gradient(
                    material_lines,
                    geometry_lines,
                    ballast_bottom,
                    foul_top,
                    base_foul_eps,
                    base_foul_sigma,
                )
            )
        elif scenario_type == "pockets":
            scenario_info.update(
                self._add_pockets(
                    material_lines,
                    geometry_lines,
                    ballast_bottom,
                    foul_top,
                    base_foul_eps,
                    base_foul_sigma,
                )
            )
        elif scenario_type == "wet":
            scenario_info.update(
                self._add_wet_fouling(
                    material_lines,
                    geometry_lines,
                    ballast_bottom,
                    foul_top,
                    base_foul_eps,
                    base_foul_sigma,
                )
            )
        else:
            scenario_info.update(
                self._add_uniform_fouling(material_lines, geometry_lines, ballast_bottom, foul_top, base_foul_eps, base_foul_sigma)
            )

        # E. TX/RX
        if cfg.add_source:
            geometry_lines.append("## TX/RX en aire (sobre la superficie)")
            geometry_lines.append(f"#hertzian_dipole: z {cfg.tx_x} {cfg.tx_rx_y} {cfg.tx_rx_z} src")
            geometry_lines.append(f"#rx: {cfg.rx_x} {cfg.tx_rx_y} {cfg.tx_rx_z}")

        # F. Geometry View
        if cfg.add_geometry_view:
            geometry_lines.append(
                f"#geometry_view: 0 0 0  {cfg.domain_x} {cfg.domain_y} {cfg.domain_z}  "
                f"{cfg.dx} {cfg.dy} {cfg.dz} {base_name}.vtk n"
            )

        # Assemble final text
        all_lines = header_lines + setup_lines + material_lines + geometry_lines
        text = "\n".join(all_lines)
        return text, scenario_info

    # --------------- scenario implementations -----------------

    def _add_uniform_fouling(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float = 0.0,
        base_sigma: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Simple case: one fouled layer overwriting the bottom of the rock.
        """
        cfg = self.cfg

        # Fouled layer
        geometry.append(f"## Layer: bal_foul ({ballast_bottom:.4f}–{foul_top:.4f})")
        geometry.append(f"#box: 0.0 {ballast_bottom:.4f} 0.0   {cfg.domain_x} {foul_top:.4f} {cfg.domain_z} bal_foul")

        return {"scenario_detail": "uniform"}

    def _add_vertical_gradient(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Split fouled region into several sublayers with increasing eps/sigma.
        """
        cfg = self.cfg
        foul_thickness = foul_top - ballast_bottom
        if foul_thickness <= 0:
            return self._add_uniform_fouling(materials, geometry, ballast_bottom, ballast_bottom, base_eps, base_sigma)

        n_layers = random.randint(cfg.grad_min_layers, cfg.grad_max_layers)
        sub_thick = foul_thickness / n_layers
        eps_bottom = base_eps * 0.8
        eps_top = base_eps * 1.2
        sigma_bottom = base_sigma * 0.5
        sigma_top = base_sigma * 1.5

        eps_values = np.linspace(eps_bottom, eps_top, n_layers)
        sigma_values = np.linspace(sigma_bottom, sigma_top, n_layers)

        # Define materials
        grad_labels = []
        for i in range(n_layers):
            label = f"bal_foul_g{i+1}"
            grad_labels.append(label)
            materials.append(f"#material: {eps_values[i]:.3f} {sigma_values[i]:.4e} 1 0 {label}")

        # Define geometry (bottom up)
        y0 = ballast_bottom
        for i, label in enumerate(grad_labels):
            y1 = ballast_bottom + (i + 1) * sub_thick
            geometry.append(f"## Gradient Layer {i+1}: {label} ({y0:.4f}–{y1:.4f})")
            geometry.append(f"#box: 0.0 {y0:.4f} 0.0   {cfg.domain_x} {y1:.4f} {cfg.domain_z} {label}")
            y0 = y1

        return {
            "scenario_detail": "vertical_gradient",
            "grad_layers": n_layers,
            "grad_eps_min": float(eps_bottom),
            "grad_eps_max": float(eps_top),
        }

    def _add_pockets(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Uniform fouling layer plus localized high-contrast pockets.
        """
        cfg = self.cfg

        # Base fouled layer
        geometry.append(f"## Layer: bal_foul ({ballast_bottom:.4f}–{foul_top:.4f})")
        geometry.append(f"#box: 0.0 {ballast_bottom:.4f} 0.0   {cfg.domain_x} {foul_top:.4f} {cfg.domain_z} bal_foul")

        # Pocket material
        pocket_eps = random.uniform(cfg.pocket_eps_min, cfg.pocket_eps_max)
        pocket_sigma = random.uniform(cfg.pocket_sigma_min, cfg.pocket_sigma_max)
        materials.append(f"#material: {pocket_eps:.3f} {pocket_sigma:.4e} 1 0 foul_pocket")

        # Pockets (defined AFTER layers so they overwrite)
        n_pockets = random.randint(1, cfg.max_pockets)
        for i in range(n_pockets):
            x1 = random.uniform(0.05, cfg.domain_x * 0.7)
            x2 = x1 + random.uniform(0.05, 0.2)
            x2 = min(x2, cfg.domain_x)

            y1 = random.uniform(ballast_bottom, foul_top)
            y2 = y1 + random.uniform(0.01, (foul_top - ballast_bottom) * 0.6)
            y2 = min(y2, foul_top)

            geometry.append(f"## Fouling pocket {i+1} (x: {x1:.3f}-{x2:.3f}, y: {y1:.3f}-{y2:.3f})")
            geometry.append(f"#box: {x1:.3f} {y1:.4f} 0.0   {x2:.3f} {y2:.4f} {cfg.domain_z} foul_pocket")

        return {
            "scenario_detail": "pockets",
            "pocket_count": n_pockets,
            "pocket_eps": float(pocket_eps),
            "pocket_sigma": float(pocket_sigma),
        }

    def _add_wet_fouling(
        self,
        materials: List[str],
        geometry: List[str],
        ballast_bottom: float,
        foul_top: float,
        base_eps: float,
        base_sigma: float,
    ) -> Dict[str, Any]:
        """
        Wet fouling: top portion of fouled layer is saturated.
        """
        cfg = self.cfg
        foul_thickness = foul_top - ballast_bottom
        if foul_thickness <= 0:
            return self._add_uniform_fouling(materials, geometry, ballast_bottom, ballast_bottom, base_eps, base_sigma)

        wet_frac = random.uniform(0.3, 0.9)
        wet_thickness = foul_thickness * wet_frac
        wet_top = ballast_bottom + wet_thickness

        eps_factor = random.uniform(cfg.wet_eps_factor_min, cfg.wet_eps_factor_max)
        sigma_factor = random.uniform(cfg.wet_sigma_factor_min, cfg.wet_sigma_factor_max)
        wet_eps = base_eps * eps_factor
        wet_sigma = base_sigma * sigma_factor

        materials.append(f"#material: {wet_eps:.3f} {wet_sigma:.4e} 1 0 bal_foul_wet")

        # Dry fouling (bottom part)
        geometry.append(f"## Layer: bal_foul (dry) ({ballast_bottom:.4f}–{wet_top:.4f})")
        geometry.append(f"#box: 0.0 {ballast_bottom:.4f} 0.0   {cfg.domain_x} {wet_top:.4f} {cfg.domain_z} bal_foul")

        # Wet fouling (top part)
        geometry.append(f"## Layer: bal_foul_wet ({wet_top:.4f}–{foul_top:.4f})")
        geometry.append(f"#box: 0.0 {wet_top:.4f} 0.0   {cfg.domain_x} {foul_top:.4f} {cfg.domain_z} bal_foul_wet")

        return {
            "scenario_detail": "wet",
            "wet_fraction": wet_frac,
            "wet_eps": float(wet_eps),
            "wet_sigma": float(wet_sigma),
        }


# ------------------------------------------------------------
# Example usage
# ------------------------------------------------------------
if __name__ == "__main__":
    cfg = GeneratorConfig(
        base_seed=42,  # for reproducibility; remove or change if you want randomness each run
        add_waveform=True,
        add_source=True,
        add_geometry_view=False
    )
    gen = BallastScenarioGenerator(cfg)

    # This will create e.g. 100 samples in ./synthetic_inputs/
    # and a metadata.csv with FI and scenario info.
    out_df = gen.generate_dataset(
        out_dir="synthetic_inputs",
        n_samples=5000,
        csv_name="metadata.csv",
    )
    print(out_df.head())