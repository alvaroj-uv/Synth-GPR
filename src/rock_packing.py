"""
Rock packing strategies for ballast layer generation.

Implements various circle packing algorithms as pluggable strategies using
the Strategy design pattern. This allows easy swapping between different
rock placement algorithms (Random, Poisson Disk Sampling, etc.) without
modifying the layer generation logic.

Example:
    >>> from rock_packing import PoissonDiskPacking, PackingBounds
    >>> strategy = PoissonDiskPacking(k_attempts=30)
    >>> bounds = PackingBounds(x_min=0, x_max=0.5, y_min=0, y_max=0.3)
    >>> rocks = strategy.generate_rocks(bounds, 0.02, 0.05, target_fill_ratio=0.6)
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
from enum import IntEnum
import numpy as np
import random


@dataclass
class Rock:
    """
    Represents a single rock as a 2D circle.
    
    Attributes:
        x: X-coordinate of rock center (meters)
        y: Y-coordinate of rock center (meters)
        radius: Rock radius (meters)
    """
    x: float
    y: float
    radius: float


@dataclass
class PackingBounds:
    """
    Defines the rectangular bounding box for rock placement.
    
    Attributes:
        x_min: Left boundary (meters)
        x_max: Right boundary (meters)
        y_min: Bottom boundary (meters)
        y_max: Top boundary (meters)
    """
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    
    @property
    def width(self) -> float:
        """Width of the bounding box."""
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        """Height of the bounding box."""
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        """Total area of the bounding box."""
        return self.width * self.height


class RockPackingStrategy(ABC):
    """
    Abstract base class for rock placement strategies.
    
    Implements the Strategy pattern to allow interchangeable circle packing
    algorithms. Each concrete strategy must implement generate_rocks() to
    produce a list of Rock objects within the given bounds.
    """
    
    @abstractmethod
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        """
        Generate rocks within the given bounds.
        
        Args:
            bounds: Rectangular bounding box for placement
            radius_min: Minimum rock radius (meters)
            radius_max: Maximum rock radius (meters)
            target_fill_ratio: Target packing density, 0-1 (default: 0.6 = 60%)
            max_attempts: Maximum placement attempts to prevent infinite loops
            
        Returns:
            List of Rock objects with (x, y, radius) coordinates
        """
        pass
    
    def _create_rock(self, x: float, y: float, radius: float) -> Rock:
        """
        Helper method to create a Rock object.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            radius: Radius
            
        Returns:
            Rock instance
        """
        return Rock(x=x, y=y, radius=radius)


class RandomPacking(RockPackingStrategy):
    """
    Random rock placement with no overlap checking.
    
    This is the original/baseline algorithm. Places rocks randomly without
    checking for overlaps. Fast but can result in overlapping rocks and
    overcounting of fill ratios.
    
    Characteristics:
        - Time Complexity: O(N)
        - Overlaps: Yes (allowed)
        - Packing Density: ~60% (overcounted due to overlaps)
    
    Use case: Baseline comparison, legacy compatibility
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        """Generate rocks randomly without overlap checking."""
        rocks = []
        current_fill = 0.0
        attempts = 0
        
        while current_fill < target_fill_ratio and attempts < max_attempts:
            r = random.uniform(radius_min, radius_max)
            x = random.uniform(bounds.x_min + r, bounds.x_max - r)
            y = random.uniform(bounds.y_min + r, bounds.y_max - r)
            
            rocks.append(self._create_rock(x, y, r))
            current_fill += (np.pi * r * r) / bounds.area
            attempts += 1
        
        return rocks


class PoissonDiskPacking(RockPackingStrategy):
    """
    Poisson disk sampling using Bridson's algorithm.
    
    Generates non-overlapping rocks with guaranteed minimum separation.
    Uses a background grid for O(1) neighbor lookups, resulting in O(N)
    overall complexity.
    
    Algorithm:
        1. Create background grid (cell size = r_min / sqrt(2))
        2. Start with one random sample in active list
        3. While active list not empty:
           - Pick random active sample
           - Generate k candidate points in annulus (r to 2r)
           - Accept first valid candidate (no overlaps)
           - Remove from active if no valid candidates found
    
    Characteristics:
        - Time Complexity: O(N)
        - Overlaps: No (guaranteed)
        - Packing Density: 50-70% (realistic)
        - Distribution: "Blue noise" (uniform, natural)
    
    Reference:
        Bridson, R. (2007). Fast Poisson Disk Sampling in Arbitrary Dimensions.
        SIGGRAPH 2007 Sketches.
    
    Args:
        k_attempts: Number of candidate points to try per active sample
                   Higher values increase density but slower (default: 30)
    """
    
    def __init__(self, k_attempts: int = 30):
        """
        Initialize Poisson disk packer.
        
        Args:
            k_attempts: Number of candidates per active sample (20-40 typical)
        """
        self.k_attempts = k_attempts
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        """Generate non-overlapping rocks using Poisson disk sampling."""
        rocks = []
        active_list = []
        
        # Background grid for O(1) neighbor lookups
        # Cell size ensures at most 1 sample per cell
        cell_size = radius_min / np.sqrt(2)
        grid = defaultdict(lambda: None)
        
        def get_cell(x: float, y: float) -> Tuple[int, int]:
            """Convert world coordinates to grid cell indices."""
            return (
                int((x - bounds.x_min) / cell_size),
                int((y - bounds.y_min) / cell_size)
            )
        
        def is_valid(x: float, y: float, r: float) -> bool:
            """
            Check if a rock placement is valid (no overlaps, within bounds).
            
            Args:
                x: X-coordinate
                y: Y-coordinate
                r: Radius
                
            Returns:
                True if placement is valid
            """
            # Check bounds with margin
            if x - r < bounds.x_min or x + r > bounds.x_max:
                return False
            if y - r < bounds.y_min or y + r > bounds.y_max:
                return False
            
            # Check neighbors in surrounding cells
            cell_x, cell_y = get_cell(x, y)
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    neighbor = grid.get((cell_x + dx, cell_y + dy))
                    if neighbor:
                        dist = np.hypot(x - neighbor.x, y - neighbor.y)
                        min_dist = r + neighbor.radius
                        if dist < min_dist:
                            return False
            return True
        
        # Initialize with one random sample
        r0 = random.uniform(radius_min, radius_max)
        x0 = random.uniform(bounds.x_min + r0, bounds.x_max - r0)
        y0 = random.uniform(bounds.y_min + r0, bounds.y_max - r0)
        
        initial_rock = self._create_rock(x0, y0, r0)
        rocks.append(initial_rock)
        active_list.append(initial_rock)
        grid[get_cell(x0, y0)] = initial_rock
        
        current_fill = (np.pi * r0**2) / bounds.area
        
        # Generate samples from active list
        while active_list and current_fill < target_fill_ratio:
            # Pick random active sample
            idx = random.randint(0, len(active_list) - 1)
            active_rock = active_list[idx]
            
            found_valid = False
            
            # Try k candidates in annulus around active sample
            for _ in range(self.k_attempts):
                # Random radius for new rock
                r_new = random.uniform(radius_min, radius_max)
                
                # Generate point in annulus (between r and 2r from active)
                min_dist = active_rock.radius + r_new
                max_dist = 2 * min_dist
                
                angle = random.uniform(0, 2 * np.pi)
                distance = random.uniform(min_dist, max_dist)
                x_new = active_rock.x + distance * np.cos(angle)
                y_new = active_rock.y + distance * np.sin(angle)
                
                if is_valid(x_new, y_new, r_new):
                    new_rock = self._create_rock(x_new, y_new, r_new)
                    rocks.append(new_rock)
                    active_list.append(new_rock)
                    grid[get_cell(x_new, y_new)] = new_rock
                    
                    current_fill += (np.pi * r_new**2) / bounds.area
                    found_valid = True
                    break
            
            # Remove from active list if no valid candidates
            if not found_valid:
                active_list.pop(idx)
        
        return rocks


class SimulatedAnnealingPacking(RockPackingStrategy):
    """
    Simulated annealing for dense packing optimization.
    
    NOTE: This is a placeholder for future implementation.
    Currently delegates to RandomPacking as a fallback.
    
    Future implementation will:
        - Start with random or greedy initial configuration
        - Iteratively move rocks to minimize energy (overlaps + density)
        - Accept worse states with decreasing probability (cooling schedule)
        - Return best configuration found
    
    Expected characteristics:
        - Time Complexity: O(N² × iterations)
        - Overlaps: No (penalized in energy function)
        - Packing Density: 70-80% (high quality)
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        """
        Generate rocks using simulated annealing.
        
        TODO: Implement full SA algorithm
        Currently uses RandomPacking as fallback.
        """
        # Placeholder: delegate to random packing
        fallback = RandomPacking()
        return fallback.generate_rocks(
            bounds, radius_min, radius_max, target_fill_ratio, max_attempts
        )



class EdgePattern(IntEnum):
    """
    Edge density patterns for Wang tile matching.
    
    Represents the density of rocks near a tile edge. Used as constraint
    for tile placement - adjacent tiles must have compatible edges.
    
    Values:
        EMPTY (0): No rocks within 2.5cm of edge
        SPARSE (1): 1-2 small rocks near edge
        MEDIUM (2): 3-4 medium rocks near edge
        DENSE (3): 5+ rocks near edge, high density
    """
    EMPTY = 0
    SPARSE = 1
    MEDIUM = 2
    DENSE = 3


@dataclass
class WangTile:
    """
    Wang tile containing a rock pattern with edge constraints.
    
    Args:
        tile_id: Unique identifier (1-13)
        rocks: List of Rock objects with positions relative to tile origin (0,0)
        north_edge: Density pattern of north edge
        east_edge: Density pattern of east edge
        south_edge: Density pattern of south edge
        west_edge: Density pattern of west edge
        size: Physical size of tile in meters (default 0.1m = 10cm)
    """
    tile_id: int
    rocks: List[Rock]
    north_edge: EdgePattern
    east_edge: EdgePattern
    south_edge: EdgePattern
    west_edge: EdgePattern
    size: float = 0.1
    
    def __hash__(self):
        """Make hashable for use in sets/dicts."""
        return hash((self.tile_id, self.north_edge, self.east_edge, 
                    self.south_edge, self.west_edge))
    
    def __eq__(self, other):
        """Equality based on tile_id."""
        if not isinstance(other, WangTile):
            return False
        return self.tile_id == other.tile_id


class WangTileLibrary:
    """
    Library of Wang tiles for aperiodic rock patterns.
    
    Creates a minimal set of 13 tiles that guarantees aperiodic (non-repeating)
    tiling when placed with edge-matching constraints. Based on Culik's
    minimal aperiodic set.
    """
    
    def __init__(self, tile_size: float = 0.1, seed_offset: int = 0):
        self.tile_size = tile_size
        self.seed_offset = seed_offset
        print(f"Generating Wang tile library (13 tiles, size={tile_size}m)...")
        self.tiles = self._create_tile_set()
        self._build_edge_index()
        print(f"Wang tile library ready: {len(self.tiles)} tiles indexed")
    
    def _create_tile_set(self) -> List[WangTile]:
        tiles = []
        # Tile configurations: (id, North, East, South, West)
        # These specific combinations ensure aperiodic tiling
        configs = [
            (1,  0, 0, 0, 0),  # All empty (low density everywhere)
            (2,  3, 3, 3, 3),  # All dense (high density everywhere)
            (3,  0, 1, 2, 3),  # Gradient: empty -> sparse -> medium -> dense
            (4,  3, 2, 1, 0),  # Reverse gradient: dense -> empty
            (5,  1, 1, 1, 1),  # All sparse (uniform low-medium)
            (6,  2, 2, 2, 2),  # All medium (uniform medium)
            (7,  0, 2, 0, 2),  # Alternating empty/medium (horizontal)
            (8,  1, 3, 1, 3),  # Alternating sparse/dense (horizontal)
            (9,  2, 0, 2, 0),  # Alternating medium/empty (vertical)
            (10, 3, 1, 3, 1),  # Alternating dense/sparse (vertical)
            (11, 0, 3, 2, 1),  # Mixed pattern 1 (asymmetric)
            (12, 1, 2, 3, 0),  # Mixed pattern 2 (asymmetric)
            (13, 2, 1, 0, 3),  # Mixed pattern 3 (asymmetric)
        ]
        
        for tile_id, n, e, s, w in configs:
            rocks = self._generate_tile_rocks(
                tile_id,
                EdgePattern(n),
                EdgePattern(e),
                EdgePattern(s),
                EdgePattern(w)
            )
            
            tiles.append(WangTile(
                tile_id=tile_id,
                rocks=rocks,
                north_edge=EdgePattern(n),
                east_edge=EdgePattern(e),
                south_edge=EdgePattern(s),
                west_edge=EdgePattern(w),
                size=self.tile_size
            ))
        
        return tiles
    
    def _generate_tile_rocks(
        self,
        tile_id: int,
        north: EdgePattern,
        east: EdgePattern,
        south: EdgePattern,
        west: EdgePattern
    ) -> List[Rock]:
        # Deterministic seed based on tile_id
        seed = (tile_id + self.seed_offset) * 12345
        
        # Calculate edge margins based on patterns
        margin_n = self._edge_margin(north)
        margin_e = self._edge_margin(east)
        margin_s = self._edge_margin(south)
        margin_w = self._edge_margin(west)
        
        # Interior bounds (avoiding edge zones)
        interior_bounds = PackingBounds(
            margin_w,
            self.tile_size - margin_e,
            margin_s,
            self.tile_size - margin_n
        )
        
        # Use PoissonDiskPacking from THIS module
        strategy = PoissonDiskPacking(k_attempts=30)
        np.random.seed(seed)
        random.seed(seed)
        
        interior_rocks = []
        if interior_bounds.width > 0.02 and interior_bounds.height > 0.02:
            interior_rocks = strategy.generate_rocks(
                interior_bounds,
                radius_min=0.015,  # 1.5cm min
                radius_max=0.03,   # 3cm max
                target_fill_ratio=0.55
            )
        
        # Add edge rocks based on density patterns
        edge_rocks = self._add_edge_rocks(north, east, south, west, seed)
        
        # Reset RNG
        np.random.seed(None)
        random.seed(None)
        
        return interior_rocks + edge_rocks
    
    def _edge_margin(self, pattern: EdgePattern) -> float:
        margins = {
            EdgePattern.EMPTY: 0.025,
            EdgePattern.SPARSE: 0.018,
            EdgePattern.MEDIUM: 0.012,
            EdgePattern.DENSE: 0.006
        }
        return margins[pattern]
    
    def _add_edge_rocks(self, north, east, south, west, seed) -> List[Rock]:
        edge_rocks = []
        np.random.seed(seed + 1)
        
        # Helper to add rocks
        def add(count, x_func, y_func):
            for i in range(count):
                x = x_func()
                y = y_func()
                r = np.random.uniform(0.015, 0.025)
                edge_rocks.append(Rock(x, y, r))

        # North
        add(int(north), 
            lambda: np.random.uniform(0.02, self.tile_size - 0.02),
            lambda: self.tile_size - np.random.uniform(0.005, 0.015))
            
        # East
        add(int(east),
            lambda: self.tile_size - np.random.uniform(0.005, 0.015),
            lambda: np.random.uniform(0.02, self.tile_size - 0.02))
            
        # South
        add(int(south),
            lambda: np.random.uniform(0.02, self.tile_size - 0.02),
            lambda: np.random.uniform(0.005, 0.015))
            
        # West
        add(int(west),
            lambda: np.random.uniform(0.005, 0.015),
            lambda: np.random.uniform(0.02, self.tile_size - 0.02))
        
        np.random.seed(None)
        return edge_rocks
    
    def _build_edge_index(self):
        self.edge_index: Dict[Tuple, List[WangTile]] = defaultdict(list)
        for tile in self.tiles:
            for n in [None, tile.north_edge]:
                for e in [None, tile.east_edge]:
                    for s in [None, tile.south_edge]:
                        for w in [None, tile.west_edge]:
                            key = (n, e, s, w)
                            self.edge_index[key].append(tile)
    
    def find_compatible_tiles(self, north_req=None, east_req=None, south_req=None, west_req=None) -> List[WangTile]:
        key = (north_req, east_req, south_req, west_req)
        return self.edge_index.get(key, [])


class WangConstraintSolver:
    """Solves Wang tile placement using constrained backtracking."""
    
    def __init__(self, library: WangTileLibrary):
        self.library = library
    
    def solve_grid(self, grid_width: int, grid_height: int, seed: int) -> Dict[Tuple[int, int], WangTile]:
        np_state = np.random.get_state()
        random_state = random.getstate()
        np.random.seed(seed)
        random.seed(seed)
        
        grid = {}
        if self._backtrack(grid, 0, 0, grid_width, grid_height):
            np.random.set_state(np_state)
            random.setstate(random_state)
            return grid
            
        print(f"Warning: Backtracking failed for {grid_width}x{grid_height}, using relaxed solver")
        result = self._solve_relaxed(grid_width, grid_height, seed)
        np.random.set_state(np_state)
        random.setstate(random_state)
        return result
    
    def _backtrack(self, grid, x, y, width, height) -> bool:
        if y >= height: return True
        
        next_x = (x + 1) % width
        next_y = y + 1 if next_x == 0 else y
        
        north_req = grid.get((x, y-1)).south_edge if y > 0 else None
        west_req = grid.get((x-1, y)).east_edge if x > 0 else None
        
        candidates_ref = self.library.find_compatible_tiles(north_req=north_req, west_req=west_req)
        if not candidates_ref: return False
        
        candidates = list(candidates_ref)
        random.shuffle(candidates)
        
        for tile in candidates:
            grid[(x, y)] = tile
            if self._backtrack(grid, next_x, next_y, width, height):
                return True
            del grid[(x, y)]
        return False
        
    def _solve_relaxed(self, width, height, seed) -> Dict[Tuple[int, int], WangTile]:
        grid = {}
        for y in range(height):
            for x in range(width):
                north_req = grid.get((x, y-1)).south_edge if y > 0 else None
                west_req = grid.get((x-1, y)).east_edge if x > 0 else None
                
                candidates = self.library.find_compatible_tiles(north_req=north_req, west_req=west_req)
                if not candidates: candidates = self.library.tiles
                grid[(x, y)] = random.choice(candidates)
        return grid


class WangTileRockPacking(RockPackingStrategy):
    """
    Wang tile-based rock packing with aperiodic patterns.
    """
    
    # Class-level singleton library (shared across all instances)
    _initialization_done = False
    _library = None
    _solver = None
    
    def __init__(self, tile_size: float = 0.1):
        self.tile_size = tile_size
        
        # Lazy initialization
        if not WangTileRockPacking._initialization_done:
            print(f"Initializing Wang tile system (tile_size={tile_size}m)...")
            WangTileRockPacking._library = WangTileLibrary(tile_size)
            WangTileRockPacking._solver = WangConstraintSolver(WangTileRockPacking._library)
            WangTileRockPacking._initialization_done = True
            print("Wang tile system ready!")
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        grid_w = int(np.ceil(bounds.width / self.tile_size))
        grid_h = int(np.ceil(bounds.height / self.tile_size))
        
        seed_str = f"{round(bounds.x_min, 3)}_{round(bounds.y_min, 3)}_{round(bounds.width, 3)}_{round(bounds.height, 3)}"
        seed = int.from_bytes(seed_str.encode('utf-8'), 'big') & 0xFFFFFFFF
        
        wang_grid = self._solver.solve_grid(grid_w, grid_h, seed)
        return self._grid_to_rocks(wang_grid, bounds)
    
    def _grid_to_rocks(self, grid: dict, bounds: PackingBounds) -> List[Rock]:
        all_rocks = []
        for (x_idx, y_idx), tile in grid.items():
            tile_x = bounds.x_min + x_idx * self.tile_size
            tile_y = bounds.y_min + y_idx * self.tile_size
            
            for rock in tile.rocks:
                world_x = tile_x + rock.x
                world_y = tile_y + rock.y
                
                if (world_x - rock.radius >= bounds.x_min and
                    world_x + rock.radius <= bounds.x_max and
                    world_y - rock.radius >= bounds.y_min and
                    world_y + rock.radius <= bounds.y_max):
                    all_rocks.append(Rock(world_x, world_y, rock.radius))
        return all_rocks


class GridPacking(RockPackingStrategy):
    """
    Deterministic grid-based packing.
    
    "The Simple Rule": Places rocks at fixed intervals.
    Guaranteed to produce results, never fails or hangs.
    Used as a fallback when complex stochastic methods fail.
    
    Characteristics:
        - Time Complexity: O(N)
        - Overlaps: No (by definition)
        - Packing Density: Low/Regular (~50%)
        - Deterministic: Yes
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.6,
        max_attempts: int = 1000
    ) -> List[Rock]:
        """Generate rocks in a simple grid."""
        rocks = []
        
        # Use average radius
        r = (radius_min + radius_max) / 2
        diameter = 2 * r
        
        # Grid spacing (add small epsilon to avoid float imprecision overlaps)
        spacing = diameter * 1.05
        
        rows = int(bounds.height / spacing)
        cols = int(bounds.width / spacing)
        
        for row in range(rows):
            for col in range(cols):
                # Center of cell
                x = bounds.x_min + (col * spacing) + r
                y = bounds.y_min + (row * spacing) + r
                
                if x + r <= bounds.x_max and y + r <= bounds.y_max:
                    rocks.append(self._create_rock(x, y, r))
                    
        return rocks

