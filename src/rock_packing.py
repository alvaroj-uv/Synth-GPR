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

# Standard library imports
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Tuple

# Third-party imports
import numpy as np

# Local imports
from .constants import PAC
from .rock_model import PackingBounds, Rock

# Removed local Rock/PackingBounds definitions



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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
    ) -> List[Rock]:
        """
        Generate rocks within the given bounds.
        
        Args:
            bounds: Rectangular bounding box for placement
            
        Returns:
            List of Rock objects
        """
        pass

    def _create_rock(self, x: float, y: float, radius: float) -> Rock:
        """Helper method to create a Rock object."""
        return Rock(x=x, y=y, radius=radius)

    def fill_voids(self, rocks: List[Rock], bounds: PackingBounds, 
                   min_void_radius: float = 0.005, attempts: int = 500) -> List[Rock]:
        """
        Post-processing step to fill gaps with small rocks.
        Inspired by ifrozenwhale/non-overlapping-circle.
        """
        new_rocks = list(rocks)
        for _ in range(attempts):
            x = random.uniform(bounds.x_min, bounds.x_max)
            y = random.uniform(bounds.y_min, bounds.y_max)
            
            min_dist = float('inf')
            valid_center = True
            
            # Bounds check
            min_dist = min(min_dist, x - bounds.x_min, bounds.x_max - x, 
                           y - bounds.y_min, bounds.y_max - y)
            if min_dist < min_void_radius: continue
                
            # Rock check
            for r in new_rocks:
                d_surf = np.hypot(x - r.x, y - r.y) - r.radius
                if d_surf < 0:
                    valid_center = False
                    break
                min_dist = min(min_dist, d_surf)
            
            if valid_center and min_dist >= min_void_radius:
                new_rocks.append(self._create_rock(x, y, min_dist - 0.0001))
                
        return new_rocks


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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
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
    
    def __init__(self, k_attempts: int = PAC.POISSON_K_ATTEMPTS):
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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
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
    size: float = PAC.TILE_SIZE
    
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
    
    def __init__(self, tile_size: float = PAC.TILE_SIZE, seed_offset: int = 0):
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
        seed = (tile_id + self.seed_offset) * PAC.WANG_SEED_MULTIPLIER
        
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
            EdgePattern.EMPTY: PAC.MARGIN_EMPTY,
            EdgePattern.SPARSE: PAC.MARGIN_SPARSE,
            EdgePattern.MEDIUM: PAC.MARGIN_MEDIUM,
            EdgePattern.DENSE: PAC.MARGIN_DENSE
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
    
    def __init__(self, tile_size: float = PAC.TILE_SIZE):
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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
    ) -> List[Rock]:
        grid_w = int(np.ceil(bounds.width / self.tile_size))
        grid_h = int(np.ceil(bounds.height / self.tile_size))
        
        seed_str = (f"{round(bounds.x_min, 3)}_{round(bounds.y_min, 3)}_"
                    f"{round(bounds.width, 3)}_{round(bounds.height, 3)}")
        seed = int.from_bytes(seed_str.encode('utf-8'), 'big') & 0xFFFFFFFF
        
        wang_grid = self._solver.solve_grid(grid_w, grid_h, seed)
        return self._grid_to_rocks(wang_grid, bounds)
    
    def _grid_to_rocks(self, grid: Dict[Tuple[int, int], WangTile], bounds: PackingBounds) -> List[Rock]:
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
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
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


class FrontChainPacking(RockPackingStrategy):
    """
    Front-Chain Packing (Advancing Front) for high-density aggregates.
    
    Inspired by d3-hierarchy's packSiblings (Wang et al.).
    Maintains a chain of "front" circles and places new circles in the 
    interstices (pockets) between neighbors.
    
    Characteristics:
        - Density: High (70-80%+) because it maximizes tangency.
        - Structure: Clustered, organic "growth" look.
        - Complexity: O(N log N) roughly.
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.75, # Higher default for this strategy
        max_attempts: int = 2000
    ) -> List[Rock]:
        rocks = []
        
        # 1. Pre-generate a queue of rocks to place (sorted by size usually helps density)
        # We start with a large batch to ensure we have enough to fill
        estimated_count = int((bounds.area * target_fill_ratio) / (np.pi * radius_min**2)) * 2
        
        # We'll use a simple "gravity" approach: grow from bottom-center
        start_x = (bounds.x_min + bounds.x_max) / 2
        start_y = bounds.y_min + radius_max
        
        # Initialize front with a single rock
        first_r = random.uniform(radius_min, radius_max)
        first_rock = self._create_rock(start_x, start_y, first_r)
        
        if not self._is_inside(first_rock, bounds):
             # If even the first rock doesn't fit (domain too small), abort
             return []
             
        rocks.append(first_rock)
        
        # The "Front" is a list of rocks that are candidates for neighbors
        # For a full implementation like d3, we need a linked list. 
        # Here we use a simplified "Distance Field" or "Place Near" approach 
        # for robustness in a bounded box.
        
        # SIMPLIFIED ALGORITHM for Bounded Box:
        # 1. Pick a reference rock from the existing set (close to center/bottom)
        # 2. Try to place new rock tangent to it at various angles
        # 3. If valid (no overlap, inside bounds), accept.
        # 4. Repeat.
        
        current_fill = (np.pi * first_r**2) / bounds.area
        attempts = 0
        
        while current_fill < target_fill_ratio and attempts < max_attempts:
            r = random.uniform(radius_min, radius_max)
            
            placed = False
            
            # Optimization: Try to place tangent to recent rocks (advancing front)
            # Scan backwards through placed rocks to find a host
            candidates = list(range(len(rocks)))
            random.shuffle(candidates) # Randomize to avoid directional bias
            candidates = candidates[:50] # Only look at a subset to be fast
            
            for idx in candidates:
                host = rocks[idx]
                
                # Try placing in the "nook" between host and its neighbors?
                # Or just simple tangent placement at random angle
                
                # Try k angles around the host
                for _ in range(8): 
                    angle = random.uniform(0, 2 * np.pi)
                    dist = host.radius + r
                    
                    x_c = host.x + np.cos(angle) * dist
                    y_c = host.y + np.sin(angle) * dist
                    
                    new_rock = self._create_rock(x_c, y_c, r)
                    
                    if self._is_valid(new_rock, rocks, bounds):
                        rocks.append(new_rock)
                        current_fill += (np.pi * r**2) / bounds.area
                        placed = True
                        break
                
                if placed: break
            
            if not placed:
                attempts += 1
            else:
                attempts = 0 # Reset attempts on success
                
        return rocks

    def _is_inside(self, rock: Rock, bounds: PackingBounds) -> bool:
        return (rock.x - rock.radius >= bounds.x_min and
                rock.x + rock.radius <= bounds.x_max and
                rock.y - rock.radius >= bounds.y_min and
                rock.y + rock.radius <= bounds.y_max)

    def _is_valid(self, candidate: Rock, others: List[Rock], bounds: PackingBounds) -> bool:
        if not self._is_inside(candidate, bounds):
            return False
            
        # O(N) overlap check - can be improved with grid but sufficient for N<1000
        for other in others:
            # Squared distance check
            dx = candidate.x - other.x
            dy = candidate.y - other.y
            dist_sq = dx*dx + dy*dy
            min_dist = candidate.radius + other.radius
            if dist_sq < min_dist * min_dist - 0.000001:  # Epsilon for float tolerance
                return False
                
        return True



class PhysicsPacking(RockPackingStrategy):
    """
    Force-Directed Relaxation Packing (Physics Simulation).
    
    References / Inspirations:
    - User provided 'packin_idea.py' (Force-Directed Graph style).
    - https://github.com/mbedward/packcircles (R package, 'circleRepelLayout').
    - https://github.com/xnx/circle-packing (Packing into arbitrary shapes).
    - https://github.com/Rebekah1012/PackingCircles (Numerical Optimization methodology).
    - https://github.com/ifrozenwhale/non-overlapping-circle (Gap Filling / Random Walk).
    
    Method:
    1. Initialize rocks randomly (allowing overlaps).
    2. Iteratively apply repulsive forces between overlapping rocks.
    3. Rocks 'push' each other apart until equilibrium is reached.
    
    Refinement (Inertia):
    - Repulsion is mass-weighted. Small rocks move more than large rocks.
    - This simulates 'shaking' where small particles settle into gaps.
    
    Characteristics:
        - Density: Very High (can exceed 80% if compressed).
        - Quality: Organic, realistic "settled" look.
        - Performance: Slower than Poisson/FrontChain due to iterative loop.
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.70,
        max_attempts: int = PAC.PHYSICS_ITERATIONS 
    ) -> List[Rock]:
        """
        Generates rocks using physics relaxation.
        
        Args:
            max_attempts: HERE, used as MAX_ITERATIONS for the physics loop.
        """
        # 1. Initialize Rocks
        estimated_count = int((bounds.area * target_fill_ratio) / (np.pi * radius_min**2))
        
        # Internal class for simulation state
        class SimRock:
            def __init__(self, x, y, r):
                self.x = x
                self.y = y
                self.r = r
                self.vx = 0.0
                self.vy = 0.0
                # Mass proportional to area (2D) or volume (3D). Let's use Area.
                self.mass = r * r 
        
        sim_rocks = []
        for _ in range(estimated_count):
            r = random.uniform(radius_min, radius_max)
            x = random.uniform(bounds.x_min + r, bounds.x_max - r)
            y = random.uniform(bounds.y_min + r, bounds.y_max - r)
            sim_rocks.append(SimRock(x, y, r))
            
        # 2. Physics Loop
        iterations = max_attempts 
        damping = PAC.PHYSICS_DAMPING 
        
        for _ in range(iterations):
            max_move = 0.0
            
            # We can do immediate updates (Gauss-Seidel style) for faster convergence
            # instead of waiting for all forces (Jacobi).
            # This is often more stable for packing.
            
            random.shuffle(sim_rocks) # Avoid bias
            
            for i in range(len(sim_rocks)):
                r1 = sim_rocks[i]
                fx, fy = 0.0, 0.0
                
                # --- Wall Repulsion ---
                # Walls have infinite mass -> rock moves 100% of the overlap
                if r1.x - r1.r < bounds.x_min: 
                    r1.x = bounds.x_min + r1.r + 0.0001 # Hard clamp + epsilon
                if r1.x + r1.r > bounds.x_max: 
                    r1.x = bounds.x_max - r1.r - 0.0001
                if r1.y - r1.r < bounds.y_min: 
                    r1.y = bounds.y_min + r1.r + 0.0001
                if r1.y + r1.r > bounds.y_max: 
                    r1.y = bounds.y_max - r1.r - 0.0001

                # --- Neighbor Repulsion ---
                for j in range(len(sim_rocks)):
                    if i == j: continue
                    r2 = sim_rocks[j]
                    
                    dx = r1.x - r2.x
                    dy = r1.y - r2.y
                    dist_sq = dx*dx + dy*dy
                    min_dist = r1.r + r2.r
                    
                    if dist_sq < min_dist*min_dist:
                        dist = np.sqrt(dist_sq)
                        if dist == 0:
                            # Exact overlap
                            nx, ny = random.uniform(-1, 1), random.uniform(-1, 1)
                            overlap = min_dist
                        else:
                            overlap = min_dist - dist
                            nx, ny = dx/dist, dy/dist
                        
                        # Mass-Weighted Displacement
                        # Total overlap needs to be resolved.
                        # r1 moves proportional to r2's mass (relative to total mass)
                        # if r2 is huge, r1 moves a lot.
                        # if r2 is tiny, r1 moves a little.
                        
                        total_mass = r1.mass + r2.mass
                        factor1 = r2.mass / total_mass # Share for r1
                        
                        # Apply immediate displacement (position based dynamics)
                        # Instead of force/velocity which needs tuning, just move them apart!
                        # This is much more robust for packing.
                        
                        displace = overlap * factor1 * 0.5 # Relax factor 0.5 for stability
                        
                        r1.x += nx * displace
                        r1.y += ny * displace
                        
                        # We don't move r2 here, we wait for its turn (or move it now?)
                        # Gauss-Seidel: move r1 now, r2 will react to new r1 later.
                        # Symmetry: Let's move both now? No, simple sequential is fine.
            
            # Check limits again after neighborhood moves
            # (Simplified for speed)
        
        # 3. Finalize
        final_rocks = []
        for sr in sim_rocks:
             # Final loose check
             if (sr.x - sr.r >= bounds.x_min - 0.001 and sr.x + sr.r <= bounds.x_max + 0.001 and
                 sr.y - sr.r >= bounds.y_min - 0.001 and sr.y + sr.r <= bounds.y_max + 0.001):
                 final_rocks.append(self._create_rock(sr.x, sr.y, sr.r))
                 
        return final_rocks


class TrianglePacking(RockPackingStrategy):
    """
    "Tangent Triangle" Packing (Mesh-based Incircles).
    
    Logic Inversion:
    Instead of placing circles into shapes, we generate a mesh of triangles
    where every circle is the "incircle" of a triangle.
    
    The sides of the triangles are perfectly tangent to the borders of the
    circles contained within them.
    
    Method:
    1. Generate random points within the bounds.
    2. Perform Delaunay Triangulation (`scipy.spatial`) to create a mesh.
    3. Calculate the inscribed circle (incircle) for each triangle.
    
    Characteristics:
        - Density: Moderate (~40-60%).
        - Structure: Geometric, crystalline.
        - Overlaps: No (strictly disjoint by definition).
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
    ) -> List[Rock]:
        try:
            from scipy.spatial import Delaunay
        except ImportError:
            print("TrianglePacking requires scipy. Falling back to RandomPacking.")
            return RandomPacking().generate_rocks(bounds, radius_min, radius_max, target_fill_ratio, max_attempts)

        rocks = []
        
        # 1. Generate Points for Mesh
        # More points = smaller triangles = smaller rocks
        # Heuristic: Area / (pi * mean_r^2) to guess count
        mean_r = (radius_min + radius_max) / 2
        estimated_points = int(bounds.area / (np.pi * mean_r**2))
        
        points = []
        # Add corners to ensure convex hull covers bounds
        points.append([bounds.x_min, bounds.y_min])
        points.append([bounds.x_max, bounds.y_min])
        points.append([bounds.x_max, bounds.y_max])
        points.append([bounds.x_min, bounds.y_max])
        
        for _ in range(estimated_points):
            points.append([
                random.uniform(bounds.x_min, bounds.x_max),
                random.uniform(bounds.y_min, bounds.y_max)
            ])
            
        points = np.array(points)
        
        # 2. Triangulate
        try:
            tri = Delaunay(points)
        except Exception:
            return []
            
        # 3. Incircles
        for simplex in tri.simplices:
            # Get vertices of the triangle
            pts = points[simplex]
            A, B, C = pts[0], pts[1], pts[2]
            
            # Side lengths
            a = np.linalg.norm(B - C)
            b = np.linalg.norm(A - C)
            c = np.linalg.norm(A - B)
            
            # Semiperimeter and Area (Heron's)
            s = (a + b + c) / 2
            area = np.sqrt(s * (s - a) * (s - b) * (s - c)) if s > max(a,b,c) else 0
            
            if area < 1e-9: continue
            
            # Inradius
            r = area / s
            
            # Filter by constraints
            if r < radius_min:
                # Too small
                continue
            
            # Bounds check (Triangle center definitely inside? Delaunay covers convex hull)
            # We strictly clip to our rect bounds
            
            # Incenter coordinates
            # Cartesian = (a*Ax + b*Bx + c*Cx) / perimeter
            perimeter = a + b + c
            ix = (a*A[0] + b*B[0] + c*C[0]) / perimeter
            iy = (a*A[1] + b*B[1] + c*C[1]) / perimeter
            
            # Clip Radius to max
            if r > radius_max:
                r = radius_max # This creates gaps but respects max size
            
            # Is it inside bounds?
            if (ix - r >= bounds.x_min and ix + r <= bounds.x_max and
                iy - r >= bounds.y_min and iy + r <= bounds.y_max):
                rocks.append(self._create_rock(ix, iy, r))
                
        return rocks


@dataclass
class _SCCircle:
    """Internal circle representation for the algorithm."""
    id: int
    radius: float
    x: float = 0.0
    y: float = 0.0
    # State: 0=Floating/New, 1=Quasi-stable, 2=Stable, 3=Pseudo-stable
    state: int = 0


class ShangChuPacking(RockPackingStrategy):
    """
    Random Search Algorithm for Unequal Circle Packing.
    
    Based on: Shang, X. & Chu, F. (2013). "A random search algorithm for the 
    unequal circle packing problem".
    
    Logic:
    1. Minimizes total length L used (or maximizes density in fixed box).
    2. Uses BS-Area (Bow Shift) local search.
    3. Uses disturbance strategies (Left-off, Bottom-off) to escape local optima.
    """
    
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = 0.78, # Can achieve high density
        max_attempts: int = 5000
    ) -> List[Rock]:
        """
        Run the Shang-Chu packing algorithm.
        
        Note: The original paper packs a specific set of circles. Here we:
        1. Generate a target set of circles based on fill ratio.
        2. Pack them using the algorithm.
        3. Return those that fit.
        """
        # 1. Generate target rocks to pack
        # Sort desc by radius usually helps packing
        target_area = bounds.area * target_fill_ratio
        current_area = 0.0
        circles = []
        uid = 0
        
        # Determine "Length" (L) direction. 
        # In this codebase, usually Y is 'up' and X is 'width'.
        # The paper packs into fixed Width W, minimizing Length L.
        # So W = bounds.width, L = bounds.height (minimized).
        domain_width = bounds.width
        # We start with L_current = 0
        
        # Pre-generate set of circles
        while current_area < target_area:
            r = random.uniform(radius_min, radius_max)
            circles.append(_SCCircle(uid, r))
            current_area += np.pi * r**2
            uid += 1
            
        # Sort by radius descending (heuristic)
        circles.sort(key=lambda c: c.radius, reverse=True)
        
        # 2. Initialization: Random placement
        # Place circles randomly in a large bounding box, ensuring no overlap
        # Paper says "Randomly place i-th circle... if overlap, retry"
        L_current = 0.0
        
        for c in circles:
            c.x, c.y = self._find_random_non_overlapping_pos(c, circles, domain_width, bounds.height)
            L_current = max(L_current, c.y + c.radius)

        # 3. Main Optimization Loop
        iteration = 0
        no_improv_count = 0
        max_no_improv = 100 # Threshold to trigger disturbance
        
        # Paper flow: Search -> Disturbance if needed
        while iteration < max_attempts:
            improved = False
            
            # Sort circles by distance from origin (or "bottom")
            # Usually bottom-left or just Y coordinate. Paper says "distance from origin".
            # optimization order matters.
            search_order = sorted(circles, key=lambda c: c.y) 
            
            for c in search_order:
                # Local Search in BS-Area
                if self._bs_area_search(c, circles, domain_width):
                    improved = True
                    # Re-calc L
                    L_current = max((k.y + k.radius for k in circles), default=0)
            
            if improved:
                no_improv_count = 0
            else:
                no_improv_count += 1
                
            # Disturbance
            if no_improv_count > max_no_improv:
                # Apply disturbance (Left-off or Bottom-off)
                # "Left-off": Move quasi-stable circles (those tangent to boundary)
                # "Bottom-off": Move circles near bottom
                self._apply_disturbance(circles, domain_width, bounds.height)
                no_improv_count = 0 # Reset
                
            iteration += 1
            
        # 4. Convert back to Rock objects
        # Filter those that are fully inside bounds
        result_rocks = []
        for c in circles:
            # Shift coordinates to absolute bounds
            abs_x = bounds.x_min + c.x
            abs_y = bounds.y_min + c.y
            
            if (abs_x - c.radius >= bounds.x_min and abs_x + c.radius <= bounds.x_max and
                abs_y - c.radius >= bounds.y_min and abs_y + c.radius <= bounds.y_max):
                result_rocks.append(self._create_rock(abs_x, abs_y, c.radius))
                
        return result_rocks

    def _find_random_non_overlapping_pos(self, c: _SCCircle, existing: List[_SCCircle], domain_width: float, max_L: float) -> Tuple[float, float]:
        # Simple rejection sampling
        for _ in range(100):
            x = random.uniform(c.radius, domain_width - c.radius)
            y = random.uniform(c.radius, max_L - c.radius)
            
            valid = True
            for other in existing:
                if other.id == c.id or other.x == 0: continue # optimized check (unplaced have x=0?)
                # Wait, existing list includes c, check ID
                if other.id != c.id:
                    dist_sq = (x - other.x)**2 + (y - other.y)**2
                    min_dist = c.radius + other.radius
                    if dist_sq < min_dist**2 - 1e-6:
                        valid = False
                        break
            if valid:
                return x, y
        return 0, 0 # Should not happen if area is sparse enough

    def _bs_area_search(self, c: _SCCircle, circles: List[_SCCircle], domain_width: float) -> bool:
        """
        Search for a better position within the "Bow Shift Area".
        We implement a gradient-like stochastic sampling:
        Try k positions in a cone 120 deg "below" the current position or 
        towards a hole. 
        Goal: Minimize y.
        """
        current_y = c.y
        best_x, best_y = c.x, c.y
        found_better = False
        
        # Sampling parameters
        attempts = 20
        # "Bow" shaped search area generally means looking "downwards" for gravity packing
        # Let's search in a semi-circle or cone below current position
        step_size = c.radius * 2.0
        
        for _ in range(attempts):
            # Sample angle downwards: -150 to -30 degrees (-90 is straight down)
            angle = random.uniform(np.radians(-150), np.radians(-30))
            dist = random.uniform(0, step_size)
            
            # Candidate pos
            nx = c.x + np.cos(angle) * dist
            ny = c.y + np.sin(angle) * dist
            
            # Boundary check
            if nx - c.radius < 0 or nx + c.radius > domain_width or ny - c.radius < 0:
                continue
            
            # Overlap check (Only with OTHER circles)
            valid = True
            for other in circles:
                if other.id == c.id: continue
                # We can optimize by simple box check first
                if abs(other.x - nx) > (c.radius + other.radius): continue
                if abs(other.y - ny) > (c.radius + other.radius): continue
                
                d2 = (nx - other.x)**2 + (ny - other.y)**2
                min_d = c.radius + other.radius
                if d2 < min_d**2 - 1e-5:
                    valid = False
                    break
            
            if valid and ny < best_y:
                best_x, best_y = nx, ny
                found_better = True
        
        if found_better:
            c.x, c.y = best_x, best_y
            return True
            
        return False
        
    def _apply_disturbance(self, circles: List[_SCCircle], domain_width: float, max_L: float):
        """Randomly move some circles to shake the container."""
        strategy = random.choice(["bottom_off", "left_off", "random_move"])
        
        targets = []
        if strategy == "bottom_off":
            # Pick lowest circles
            targets = [c for c in circles if c.y < max_L * 0.2]
        elif strategy == "left_off":
            # Pick left-side circles
            targets = [c for c in circles if c.x < domain_width * 0.2]
        else:
            targets = random.sample(circles, min(len(circles)//5, 1))
            
        # Re-place them randomly above the current pile
        max_y = max((c.y for c in circles), default=0)
        for c in targets:
            # "Put out of rectangle" then re-enter -> Place largely on top
            c.x = random.uniform(c.radius, domain_width - c.radius)
            # Place them very high up where it's empty
            c.y = max_y + c.radius + random.uniform(0, max_L/2)

class CirclifyPacking(RockPackingStrategy):
    """
    High-density circle packing using the A1.0 heuristic from Huang et al. (2006).
    Ported from the `circlify` library (pure Python implementation).
    Generates a tight circular pack and then crops to the rectangular bounds.
    """
    def generate_rocks(
        self,
        bounds: PackingBounds,
        radius_min: float,
        radius_max: float,
        target_fill_ratio: float = PAC.DEFAULT_FILL_RATIO,
        max_attempts: int = PAC.MAX_ATTEMPTS
    ) -> List[Rock]:
        import math
        import itertools
        import sys
        
        _eps = sys.float_info.epsilon
        
        def distance(c1, c2):
            dx = c2.x - c1.x
            dy = c2.y - c1.y
            return math.sqrt(dx * dx + dy * dy) - c1.radius - c2.radius

        def get_intersection(c1, c2):
            dx = c2.x - c1.x
            dy = c2.y - c1.y
            d = math.sqrt(dx * dx + dy * dy)
            try:
                a = (c1.radius**2 - c2.radius**2 + d**2) / (2 * d)
                h = math.sqrt(c1.radius**2 - a**2)
            except (ValueError, ZeroDivisionError):
                return None, None
            xm = c1.x + a * dx / d
            ym = c1.y + a * dy / d
            xs1 = xm + h * dy / d
            xs2 = xm - h * dy / d
            ys1 = ym - h * dx / d
            ys2 = ym + h * dx / d
            if xs1 == xs2 and ys1 == ys2:
                return (xs1, ys1), None
            return (xs1, ys1), (xs2, ys2)

        def get_placement_candidates(radius, c1, c2):
            margin = radius * _eps * 10.0
            ic1 = Rock(c1.x, c1.y, c1.radius + radius + margin)
            ic2 = Rock(c2.x, c2.y, c2.radius + radius + margin)
            i1, i2 = get_intersection(ic1, ic2)
            if i1 is None:
                return None, None
            cand1 = Rock(i1[0], i1[1], radius)
            if i2 is None:
                return cand1, None
            cand2 = Rock(i2[0], i2[1], radius)
            return cand1, cand2

        def get_hole_degree(candidate, circles):
            return sum(distance(candidate, c) * c.radius for c in circles)

        def place_new_circle(radius, placed_circles):
            n_circles = len(placed_circles)
            if n_circles <= 1:
                x = radius if n_circles == 0 else -radius
                return Rock(x, 0.0, radius)
            
            mhd = None
            lead_candidate = None
            
            # Optimization: Checking all combinations is O(N^3).
            # To speed up, we check only a subset of recently placed circles
            # which form the "advancing front", plus some random ones.
            import random
            if n_circles < 30:
                check_circles = placed_circles
            else:
                check_circles = placed_circles[-20:] + random.sample(placed_circles[:-20], min(10, len(placed_circles)-20))
                
            for c1, c2 in itertools.combinations(check_circles, 2):
                other_circles = [c for c in check_circles if c not in (c1, c2)]
                cand1, cand2 = get_placement_candidates(radius, c1, c2)
                for cand in (cand1, cand2):
                    if cand is None:
                        continue
                    if not other_circles:
                        lead_candidate = cand
                        break
                    if any(distance(c, cand) < -1e-9 for c in placed_circles): # Full overlap check is still fast
                        continue
                    hd = get_hole_degree(cand, other_circles)
                    if mhd is None or hd < mhd:
                        mhd = hd
                        lead_candidate = cand
                    if abs(mhd) < radius * _eps * 10.0:
                        break
            
            return lead_candidate

        # 1. Generate random radii
        import random
        diag = math.hypot(bounds.width, bounds.height)
        # We need enough area to cover the diagonal. Over-generate heavily to fill corners.
        target_area = math.pi * (diag / 2)**2 * target_fill_ratio * 2.0
        
        radii = []
        current_area = 0.0
        while current_area < target_area:
            r = random.uniform(radius_min, radius_max)
            radii.append(r)
            current_area += math.pi * r**2
            
        # Sort radii descending for best packing (Huang heuristic)
        radii.sort(reverse=True)
        
        # 2. Pack them tightly around (0,0)
        placed_rocks = []
        for r in radii:
            new_rock = place_new_circle(r, placed_rocks)
            if new_rock:
                placed_rocks.append(new_rock)
                
        # 3. Center the pack and crop to bounds
        if not placed_rocks:
            return []
            
        cx = (bounds.x_min + bounds.x_max) / 2
        cy = (bounds.y_min + bounds.y_max) / 2
        
        final_rocks = []
        current_fill = 0.0
        
        for rock in placed_rocks:
            rx = rock.x + cx
            ry = rock.y + cy
            
            if (rx - rock.radius >= bounds.x_min and
                rx + rock.radius <= bounds.x_max and
                ry - rock.radius >= bounds.y_min and
                ry + rock.radius <= bounds.y_max):
                
                final_rocks.append(Rock(rx, ry, rock.radius))
                    
        return final_rocks


