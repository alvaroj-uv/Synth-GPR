"""
Tests for material EM properties.

The former domain.materials.Materials/Material table was DEAD (only these tests
referenced it) and asserted values that never reached the generator (ballast 4.0,
subgrade 5.0, ...). It has been removed. Material EM properties now have a SINGLE
SOURCE OF TRUTH: constants.MC. These tests guard that source and that the live
config + MaterialWarehouse trace back to it.
"""

import pytest

from src.constants import MC
from src.config import GeneratorConfig
from src.warehouses import MaterialWarehouse


class TestMaterialConstantsSSOT:
    """constants.MC is the single source of truth for base material EM props."""

    def test_canonical_values_present(self):
        # (permittivity, conductivity) tuples — the values that actually generate.
        # Values re-locked to the current literature-cited constants (constants.py).
        # If these change again, update intentionally — this guard locks them.
        assert MC.AIR_PROPS == (1.0, 0.0)
        assert MC.SUBGRADE_PROPS[0] == 8.0          # dry/compact railway formation (PMC9003199)
        assert MC.FORMATION_PROPS[0] == 10.0        # S&W
        assert MC.BALLAST_ROCK_PROPS == (4.0, 0.001)   # clean dry granite/limestone, 400 MHz (Tosti 2018)
        assert MC.FOULING_BASE_PROPS == (5.0, 0.005)   # lightly fouled ~10-24% (Benedetto 2017)
        assert MC.FOULING_DENSE_PROPS == (6.5, 0.012)  # fully fouled dry fines (Shang 2021)


class TestConfigTracesToMC:
    """GeneratorConfig material defaults must come from MC (no separate numbers)."""

    def test_ballast_default_from_mc(self):
        cfg = GeneratorConfig()
        assert cfg.bal_rock_eps == MC.BALLAST_ROCK_PROPS[0]
        assert cfg.bal_rock_sigma == MC.BALLAST_ROCK_PROPS[1]

    def test_fouling_defaults_from_mc(self):
        cfg = GeneratorConfig()
        assert cfg.bal_foul_eps_min == MC.FOULING_BASE_PROPS[0]
        assert cfg.bal_foul_eps_max == MC.FOULING_DENSE_PROPS[0]
        assert cfg.bal_foul_sigma_min == MC.FOULING_BASE_PROPS[1]
        assert cfg.bal_foul_sigma_max == MC.FOULING_DENSE_PROPS[1]


class TestWarehouseEmitsCanonical:
    """The LIVE MaterialWarehouse emits the canonical MC values."""

    def test_ballast_material_matches_mc(self):
        wh = MaterialWarehouse(GeneratorConfig())
        bal = wh.get_material(MC.BALLAST_ROCK)
        assert bal.eps == MC.BALLAST_ROCK_PROPS[0]
        assert bal.sigma == MC.BALLAST_ROCK_PROPS[1]
        assert bal.identifier == MC.BALLAST_ROCK

    def test_subgrade_formation_match_mc(self):
        wh = MaterialWarehouse(GeneratorConfig())
        sub = wh.get_material(MC.SUBGRADE)
        form = wh.get_material(MC.FORMATION)
        assert sub.eps == MC.SUBGRADE_PROPS[0]
        assert form.eps == MC.FORMATION_PROPS[0]
