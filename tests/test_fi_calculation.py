"""
Tests for the FI (Fouling Index) calculation in LabWorker.

Covers:
  - FI = 0 for clean ballast (no fouling geometry)
  - FI formula: Lab_FI == Lab_P4 + Lab_P200  (Selig & Waters 1994)
  - PSD curve is monotonically non-increasing (larger sieve → higher % passing)
  - PSD internal consistency: psd[4.75mm] == Lab_P4 and psd[0.075mm] == Lab_P200
  - FI increases with PVC
"""

import json
import pytest
from dataclasses import dataclass

from src.lab_worker import LabWorker
from src.worker import SceneCheckpoint
from src.config import GeneratorConfig
from src.gpr_commands import BoxCommand
from src.constants import MC


@dataclass
class _Rock:
    x: float
    y: float
    radius: float


BALLAST_BOTTOM = 0.3
BALLAST_TOP = 0.8


def _make_scene(pvc: float = 0.0, fouling_y_top: float | None = None) -> SceneCheckpoint:
    config = GeneratorConfig()
    scene = SceneCheckpoint(config)
    scene.metadata['pvc'] = pvc
    scene.metadata['ballast_bottom_y'] = BALLAST_BOTTOM
    scene.metadata['ballast_top_y'] = BALLAST_TOP

    # One rock (diameter=80mm) — retained by every sieve, contributes only to denominator
    scene.add_rock(_Rock(config.domain_x / 2, 0.55, 0.04))

    # Fouling box spanning the lower part of the ballast column
    if fouling_y_top is not None:
        scene.add_geometry(BoxCommand(
            x1=0, y1=BALLAST_BOTTOM, z1=0,
            x2=config.domain_x, y2=fouling_y_top, z2=config.dx,
            material=MC.FOULING_DENSE,
        ))

    return scene


def _run(scene: SceneCheckpoint) -> dict:
    LabWorker().execute(scene, {}, None, None)
    return scene.metadata


class TestFIFormula:
    def test_clean_ballast_fi_is_zero(self):
        """No fouling geometry → FI=0 and class is Clean."""
        meta = _run(_make_scene(pvc=0.0, fouling_y_top=None))
        assert meta['Lab_FI'] == 0.0
        assert meta['Lab_Class'] == 'C'

    def test_fi_equals_p4_plus_p200(self):
        """Core Selig & Waters formula: FI = P4 + P200."""
        meta = _run(_make_scene(pvc=25.0, fouling_y_top=0.5))
        fi = meta['Lab_FI']
        p4 = meta['Lab_P4']
        p200 = meta['Lab_P200']
        assert abs(fi - (p4 + p200)) < 1e-9, f"FI={fi:.6f} != P4+P200={p4+p200:.6f}"

    def test_p4_greater_than_p200(self):
        """P4 (% < 4.75mm) must always exceed P200 (% < 0.075mm)."""
        meta = _run(_make_scene(pvc=30.0, fouling_y_top=0.6))
        assert meta['Lab_P4'] > meta['Lab_P200']

    def test_fi_increases_with_fouling_depth(self):
        """More fouling (higher fouling_y_top) → higher FI."""
        meta_low = _run(_make_scene(pvc=20.0, fouling_y_top=0.45))
        meta_high = _run(_make_scene(pvc=20.0, fouling_y_top=0.70))
        assert meta_high['Lab_FI'] > meta_low['Lab_FI']


class TestPSDCurve:
    def test_psd_monotonically_non_increasing(self):
        """Each sieve in the PSD must have % passing <= the coarser sieve above it."""
        meta = _run(_make_scene(pvc=25.0, fouling_y_top=0.55))
        psd = json.loads(meta['Lab_PSD'])  # list of [size_mm, pct_passing]
        for i in range(len(psd) - 1):
            size_coarse, pct_coarse = psd[i]
            size_fine, pct_fine = psd[i + 1]
            assert pct_coarse >= pct_fine - 1e-9, (
                f"PSD not monotonic: sieve {size_coarse}mm ({pct_coarse:.3f}%) "
                f"> sieve {size_fine}mm ({pct_fine:.3f}%)"
            )

    def test_psd_p4_matches_lab_p4(self):
        """PSD value at the 4.75mm sieve must equal Lab_P4 (no unit mismatch)."""
        meta = _run(_make_scene(pvc=25.0, fouling_y_top=0.55))
        psd = dict(json.loads(meta['Lab_PSD']))
        assert abs(psd[4.75] - meta['Lab_P4']) < 1e-6, (
            f"PSD[4.75mm]={psd[4.75]:.4f} != Lab_P4={meta['Lab_P4']:.4f}"
        )

    def test_psd_p200_matches_lab_p200(self):
        """PSD value at the 0.075mm sieve must equal Lab_P200."""
        meta = _run(_make_scene(pvc=25.0, fouling_y_top=0.55))
        psd = dict(json.loads(meta['Lab_PSD']))
        assert abs(psd[0.075] - meta['Lab_P200']) < 1e-6, (
            f"PSD[0.075mm]={psd[0.075]:.4f} != Lab_P200={meta['Lab_P200']:.4f}"
        )

    def test_psd_coarsest_sieve_not_100(self):
        """63mm sieve must not pass 100% — the 80mm rocks are retained there."""
        meta = _run(_make_scene(pvc=25.0, fouling_y_top=0.55))
        psd = dict(json.loads(meta['Lab_PSD']))
        assert psd[63.0] < 100.0, f"Expected rocks to be retained at 63mm sieve"

    def test_psd_has_correct_sieve_count(self):
        """PSD must contain all 16 standard sieves."""
        meta = _run(_make_scene(pvc=10.0, fouling_y_top=0.45))
        psd = json.loads(meta['Lab_PSD'])
        assert len(psd) == 16
