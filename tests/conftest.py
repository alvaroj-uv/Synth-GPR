"""
Pytest configuration and fixtures for Synth-GPR tests.

Provides shared fixtures for testing infrastructure including:
- Sample signals for feature extraction tests
- Minimal scene checkpoints for worker tests
- Work order instances for contract tests
- Fixed random seeds for deterministic tests
"""

# Standard library imports
import random

# Third-party imports
import numpy as np
import pytest

# Local imports
from src.scene_geometry import SceneCheckpoint
from src.work_order import WorkOrder


@pytest.fixture
def fixed_random_seed():
    """
    Fix random seeds for deterministic tests.
    
    Automatically restores original state after test completes.
    Use this fixture whenever tests involve random number generation.
    """
    # Save original states
    np_state = np.random.get_state()
    py_state = random.getstate()
    
    # Set fixed seeds
    np.random.seed(42)
    random.seed(42)
    
    yield
    
    # Restore original states
    np.random.set_state(np_state)
    random.setstate(py_state)


@pytest.fixture
def sample_signal_clean(fixed_random_seed):
    """
    Generate a deterministic 512-sample clean ballast GPR signal.
    
    Returns:
        numpy.ndarray: 512 samples representing clean ballast response
    """
    # Simulate clean ballast: sharp reflection + some noise
    time_samples = 512
    signal = np.zeros(time_samples)
    
    # Add main reflection at sample 100
    signal[100] = 1.0
    
    # Add exponential decay
    decay_samples = np.arange(100, time_samples)
    signal[100:] = np.exp(-(decay_samples - 100) / 50.0)
    
    # Add small noise
    noise = np.random.normal(0, 0.02, time_samples)
    signal += noise
    
    return signal


@pytest.fixture
def sample_signal_fouled(fixed_random_seed):
    """
    Generate a deterministic 512-sample fouled ballast GPR signal.
    
    Returns:
        numpy.ndarray: 512 samples representing fouled ballast response  
    """
    # Simulate fouled ballast: weaker reflection + more scattering
    time_samples = 512
    signal = np.zeros(time_samples)
    
    # Weaker main reflection
    signal[100] = 0.7
    
    # Slower decay (more absorption)
    decay_samples = np.arange(100, time_samples)
    signal[100:] = 0.7 * np.exp(-(decay_samples - 100) / 80.0)
    
    # Add multiple scattering events
    signal[150] += 0.3
    signal[200] += 0.2
    signal[250] += 0.15
    
    # Larger noise (more scattering)
    noise = np.random.normal(0, 0.05, time_samples)
    signal += noise
    
    return signal


@pytest.fixture
def minimal_scene_checkpoint():
    """
    Create a minimal valid SceneCheckpoint for testing.
    
    Returns:
        SceneCheckpoint: Instance with basic required state
    """
    from src.config import Config
    
    # Create minimal config
    config = Config()
    config.domain_x = 1.0
    config.domain_y = 0.8
    config.domain_z = 0.5
    
    # Create scene
    scene = SceneCheckpoint(config=config)
    
    return scene


@pytest.fixture
def temp_work_order():
    """
    Create a fresh WorkOrder instance for testing.
    
    Returns:
        WorkOrder: Clean instance with no history
    """
    return WorkOrder()


@pytest.fixture
def sample_packing_bounds():
    """
    Create standard packing bounds for rock packing tests.
    
    Returns:
        PackingBounds: 1.0m x 0.3m rectangular region
    """
    from src.rock_model import PackingBounds
    
    return PackingBounds(
        x_min=0.0,
        x_max=1.0,
        y_min=0.0,
        y_max=0.3
    )
