"""
Railway ballast fouling classification system.

Defines fouling classes (CL, MC, MF, F, HF) and their corresponding
Particle Volume Concentration (PVC) ranges.

Context:
- PVC: Percentage of ballast volume filled with fine materials
- Clean ballast: 0-5% PVC (good drainage, performance)
- Highly fouled: 60-100% PVC (poor drainage, degraded performance)
"""


FOULING_CLASSES = {
    'CL': {
        'name': 'Clean',
        'pvc_range': (0.0, 5.0),
        'description': 'Good ballast condition, excellent drainage'
    },
    'MC': {
        'name': 'Moderately Clean',
        'pvc_range': (5.0, 20.0),
        'description': 'Light fouling, acceptable drainage'
    },
    'MF': {
        'name': 'Moderately Fouled',
        'pvc_range': (20.0, 40.0),
        'description': 'Moderate fouling, degraded drainage'
    },
    'F': {
        'name': 'Fouled',
        'pvc_range': (40.0, 60.0),
        'description': 'Heavy fouling, poor drainage'
    },
    'HF': {
        'name': 'Highly Fouled',
        'pvc_range': (60.0, 100.0),
        'description': 'Severe fouling, very poor drainage'
    },
}


def get_pvc_range(label: str) -> tuple[float, float]:
    """
    Get PVC (Particle Volume Concentration) range for a fouling class.

    Args:
        label: Fouling class code (CL, MC, MF, F, HF)

    Returns:
        Tuple of (pvc_min, pvc_max) as percentages

    Raises:
        ValueError: If label is not a recognized fouling class
    """
    if label not in FOULING_CLASSES:
        valid = ', '.join(sorted(FOULING_CLASSES.keys()))
        raise ValueError(
            f"Unknown fouling class '{label}'. Valid classes: {valid}"
        )
    return FOULING_CLASSES[label]['pvc_range']


def get_fouling_name(label: str) -> str:
    """Get full name of fouling class (e.g., 'CL' → 'Clean')."""
    if label not in FOULING_CLASSES:
        raise ValueError(f"Unknown fouling class '{label}'")
    return FOULING_CLASSES[label]['name']


def get_fouling_description(label: str) -> str:
    """Get description of fouling class."""
    if label not in FOULING_CLASSES:
        raise ValueError(f"Unknown fouling class '{label}'")
    return FOULING_CLASSES[label]['description']


def list_all_classes() -> list[str]:
    """List all valid fouling class codes."""
    return sorted(FOULING_CLASSES.keys())
