"""
Tests for WorkOrder factory method.
"""
import pytest
from src.work_order import WorkOrder


class TestWorkOrderFactory:
    
    def test_from_sampled_params_basic(self):
        """Factory creates WorkOrder from sampled params."""
        params = {'pvc': 25.0, 'moisture': 0.1}
        wo = WorkOrder.from_sampled_params(5000, params)
        
        assert wo.id == "s_5000"
        assert wo.typed_params.pvc == 25.0
        assert wo.typed_params.moisture == 0.1
        
    def test_from_sampled_params_with_defaults(self):
        """Factory uses defaults for missing params."""
        params = {}  # Empty
        wo = WorkOrder.from_sampled_params(1234, params)
        
        assert wo.id == "s_1234"
        assert wo.typed_params.pvc == 0.0  # Default
        assert wo.typed_params.moisture == 0.0  # Default
        
    def test_from_sampled_params_id_formatting(self):
        """Factory formats sample_id correctly."""
        wo = WorkOrder.from_sampled_params(42, {'pvc': 10.0})
        assert wo.id == "s_0042"  # Zero-padded to 4 digits
