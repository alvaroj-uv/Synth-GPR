
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

@dataclass
class Rock:
    """
    Represents a single cylindrical rock in the ballast.
    
    Attributes:
        x: Horizontal center position (meters)
        y: Vertical center position (meters)
        radius: Rock radius (meters)
        z_start: Start of extrusion (meters, default 0)
        z_end: End of extrusion (meters, default domain_z)
    """
    x: float
    y: float
    radius: float
    z_start: float = 0.0
    z_end: float = 0.005
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Rock(center=({self.x:.3f}, {self.y:.3f}), r={self.radius:.3f}m)"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"Rock(x={self.x}, y={self.y}, radius={self.radius}, z_start={self.z_start}, z_end={self.z_end})"


@dataclass
class PackingBounds:
    """
    Defines the rectangular bounding box for rock placement.
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    
    @property
    def width(self) -> float:
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        return self.width * self.height


class RockCollection:
    """
    A collection of rocks representing the ballast layer.
    """
    def __init__(self, rocks: List[Rock] = None):
        self.rocks = rocks or []
        
    def add(self, rock: Rock):
        self.rocks.append(rock)
        
    def __len__(self):
        return len(self.rocks)
        
    def __iter__(self):
        return iter(self.rocks)
        
    def to_dataframe(self, default_z_start: float = None, default_z_end: float = None) -> pd.DataFrame:
        """
        Convert to DataFrame for storage/analytics.
        """
        data = []
        for r in self.rocks:
            data.append({
                'x': r.x,
                'y': r.y,
                'radius': r.radius,
                'z_start': r.z_start if r.z_start is not None else default_z_start,
                'z_end': r.z_end if r.z_end is not None else default_z_end,
                'material': 'bal_rock'
            })
        return pd.DataFrame(data)
        
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'RockCollection':
        """
        Reconstruct from DataFrame.
        """
        rocks = []
        for row in df.itertuples():
            r = Rock(
                x=row.x,
                y=row.y,
                radius=row.radius,
                z_start=getattr(row, 'z_start', None),
                z_end=getattr(row, 'z_end', None)
            )
            rocks.append(r)
        return cls(rocks)
        
    def calculate_density_monte_carlo(self, domain_x: float, y_min: float, y_max: float, samples: int = 5000) -> float:
        """
        Estimate 2D density using Monte Carlo sampling.
        """
        if not self.rocks:
            return 0.0
            
        sample_points_x = np.random.uniform(0, domain_x, samples)
        sample_points_y = np.random.uniform(y_min, y_max, samples)
        
        rock_centers_x = np.array([r.x for r in self.rocks])
        rock_centers_y = np.array([r.y for r in self.rocks])
        rock_squared_radii = np.array([r.radius**2 for r in self.rocks])
        
        # Vectorized check: dist_sq < radius^2
        difference_x = sample_points_x[:, np.newaxis] - rock_centers_x[np.newaxis, :]
        difference_y = sample_points_y[:, np.newaxis] - rock_centers_y[np.newaxis, :]
        distance_squared = difference_x**2 + difference_y**2
        
        is_inside_rock = distance_squared < rock_squared_radii[np.newaxis, :]
        
        hits = np.sum(np.any(is_inside_rock, axis=1))
        return float(hits) / float(samples)
