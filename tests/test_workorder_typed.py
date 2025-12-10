"""
Test WorkOrder integration with SceneParameters.
"""
import pytest
from src.work_order import WorkOrder
from src.domain import SceneParameters


class TestWorkOrderTypedParams:
    
    def test_workorder_requires_typed_params(self):
        """WorkOrder now requires typed_params."""
        params = SceneParameters(pvc=15.0, moisture=0.1)
        wo = WorkOrder(id="test_001", typed_params=params)
        
        assert wo.id == "test_001"
        assert wo.typed_params.pvc == 15.0
        assert wo.typed_params.moisture == 0.1
        
    def test_get_uses_typed_params(self):
        """get() uses typed_params."""
        params = SceneParameters(pvc=25.0, ballast_thickness=0.5)
        wo = WorkOrder(id="test_002", typed_params=params)
        
        assert wo.get('pvc', 0.0) == 25.0
        assert wo.get('ballast_thickness', 0.0) == 0.5
        
    def test_get_default_for_missing_key(self):
        """get() returns default if key not found."""
        params = SceneParameters()
        wo = WorkOrder(id="test_003", typed_params=params)
        
        assert wo.get('nonexistent_key', 99.0) == 99.0
        
    def test_validation(self):
        """validate() checks cross-parameter constraints."""
        params = SceneParameters(antenna_offset=0.2, domain_x=1.0)
        wo = WorkOrder(id="test_004", typed_params=params)
        
        # Should pass - offset 0.2 < domain_x/2 (0.5)
        wo.validate()
        
    def test_validation_fails_for_out_of_bounds_offset(self):
        """validate() fails if antenna offset exceeds domain."""
        params = SceneParameters(antenna_offset=0.5, domain_x=0.5)
        wo = WorkOrder(id="test_005", typed_params=params)
        
        # Should fail - offset 0.5 > domain_x/2 (0.25)
        with pytest.raises(ValueError, match="antenna_offset.*exceeds domain bounds"):
            wo.validate()
