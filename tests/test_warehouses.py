"""Tier 2: ToolWarehouse must raise on an unknown/retired rock_packing_algorithm
name, never silently substitute RSAPacking (a typo or an archived name — e.g.
'rip'/'rcp', consolidated to attic/ in T11 — would otherwise pack with RSA
while the scene's own CONFIG header still claims the original name, a
reproducibility-breaking silent mismatch)."""
import pytest

from src.warehouses import ToolWarehouse
from src.rock_packing import RSAPacking


class _Cfg:
    def __init__(self, algo):
        self.rock_packing_algorithm = algo


def test_known_algorithm_still_resolves():
    tw = ToolWarehouse(_Cfg("rsa"))
    packer = tw.get_tool("rock_packer")
    assert isinstance(packer, RSAPacking)


@pytest.mark.parametrize("bad_algo", ["rip", "rcp", "typo_name", "RSA"])
def test_unknown_or_retired_algorithm_raises(bad_algo):
    tw = ToolWarehouse(_Cfg(bad_algo))
    with pytest.raises(ValueError, match="Unknown rock_packing_algorithm"):
        tw.get_tool("rock_packer")


def test_unknown_tool_name_raises():
    tw = ToolWarehouse(_Cfg("rsa"))
    with pytest.raises(ValueError, match="Unknown tool requested"):
        tw.get_tool("not_a_real_tool")
