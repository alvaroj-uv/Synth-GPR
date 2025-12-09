
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

@dataclass
class Rock:
    """
    Represents a single rock as a 2D circle.
    """
    x: float
    y: float
    radius: float
    
    # Optional 3D extent for generating cylinders
    z_start: Optional[float] = None
    z_end: Optional[float] = None


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
            
        pts_x = np.random.uniform(0, domain_x, samples)
        pts_y = np.random.uniform(y_min, y_max, samples)
        
        rock_x = np.array([r.x for r in self.rocks])
        rock_y = np.array([r.y for r in self.rocks])
        rock_r2 = np.array([r.radius**2 for r in self.rocks])
        
        diff_x = pts_x[:, np.newaxis] - rock_x[np.newaxis, :]
        diff_y = pts_y[:, np.newaxis] - rock_y[np.newaxis, :]
        dist_sq = diff_x**2 + diff_y**2
        mask = dist_sq < rock_r2[np.newaxis, :]
        
        hits = np.sum(np.any(mask, axis=1))
        return float(hits) / float(samples)
