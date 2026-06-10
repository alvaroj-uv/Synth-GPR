"""
Unit tests for SceneParameters.
"""
import pytest
from src.domain.scene_parameters import SceneParameters


class TestSceneParameters:
    
    def test_default_creation(self):
        """SceneParameters can be created with defaults."""
        params = SceneParameters()
        assert params.pvc == 0.0
        assert params.moisture == 0.0
        # Default updated from 0.45 -> 0.25 (see SceneParameters; old value outdated)
        assert params.ballast_thickness == 0.25
        
    def test_custom_values(self):
        """SceneParameters accepts custom values."""
        params = SceneParameters(
            pvc=25.0,
            moisture=0.15,
            ballast_thickness=0.5
        )
        assert params.pvc == 25.0
        assert params.moisture == 0.15
        assert params.ballast_thickness == 0.5
        
    def test_pvc_validation(self):
        """PVC must be 0-100."""
        with pytest.raises(ValueError, match="pvc must be 0-100"):
            SceneParameters(pvc=150.0)
            
        with pytest.raises(ValueError, match="pvc must be 0-100"):
            SceneParameters(pvc=-10.0)
            
    def test_moisture_validation(self):
        """Moisture must be 0-1.0."""
        with pytest.raises(ValueError, match="moisture must be 0-1.0"):
            SceneParameters(moisture=1.5)
            
        with pytest.raises(ValueError, match="moisture must be 0-1.0"):
            SceneParameters(moisture=-0.1)
            
    def test_ballast_thickness_validation(self):
        """Ballast thickness must be positive."""
        with pytest.raises(ValueError, match="ballast_thickness must be positive"):
            SceneParameters(ballast_thickness=-0.1)
            
    def test_immutability(self):
        """SceneParameters is immutable."""
        params = SceneParameters(pvc=10.0)
        with pytest.raises(Exception):  # FrozenInstanceError
            params.pvc = 20.0
            
    def test_to_dict(self):
        """SceneParameters converts to dict."""
        params = SceneParameters(pvc=15.0, moisture=0.1)
        d = params.to_dict()
        
        assert d['pvc'] == 15.0
        assert d['moisture'] == 0.1
        assert 'ballast_thickness' in d
