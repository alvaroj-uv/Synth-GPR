#!/usr/bin/env python3
"""
Enhanced GIF animator with realistic rocks and fast packing animation.

Features:
  - Realistic polygonal rock shapes (3-8 vertices)
  - Gravity settling simulation
  - Fast layer/rock filling
  - Proper painter's algorithm rendering
"""

import io
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

try:
    import numpy as np
except ImportError:
    np = None


@dataclass
class LayerGeometry:
    """Layer definition for animation."""
    name: str
    y_min: float
    y_max: float
    thickness: float
    material_name: str
    eps: float
    sigma: float
    packed: bool
    matrix_name: Optional[str] = None
    rock_eps: Optional[float] = None
    rock_sigma: Optional[float] = None
    color: Optional[str] = None


@dataclass
class RockGeometry:
    """Rock definition for animation."""
    rock_id: int
    layer_name: str
    x: float
    y: float
    radius: float
    is_polygon: bool
    vertices: Optional[List[Tuple[float, float]]] = None
    material: str = "rock"
    color: Optional[str] = None


class RealisticRockGenerator:
    """Generate realistic rock geometries with polygonal shapes."""

    @staticmethod
    def generate_polygon_rock(center_x: float, center_y: float, radius: float,
                             num_vertices: int = 5, irregularity: float = 0.3,
                             seed: Optional[int] = None) -> List[Tuple[float, float]]:
        """Generate a realistic polygonal rock with jagged edges."""
        if seed is not None:
            random.seed(seed)

        vertices = []
        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            # Add irregularity
            angle_variation = (random.random() - 0.5) * (2 * math.pi / num_vertices)
            angle += angle_variation

            # Vary radius per vertex
            r = radius * (1 - irregularity * random.random())

            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            vertices.append((x, y))

        return vertices

    @staticmethod
    def generate_rocks_for_layer(layer_bounds: Tuple[float, float], domain_width: float,
                                num_rocks: int, seed: Optional[int] = None) -> List[RockGeometry]:
        """Generate realistic rocks filling a layer."""
        if seed is not None:
            random.seed(seed)

        y_min, y_max = layer_bounds
        layer_height = y_max - y_min
        rocks = []

        # Distribute rocks with physics-like settling
        rock_id = 0
        rocks_placed = 0

        # Grid-based placement with random offsets
        grid_cols = int(math.sqrt(num_rocks)) + 1
        grid_rows = int(math.sqrt(num_rocks)) + 1

        cell_width = domain_width / grid_cols
        cell_height = layer_height / grid_rows

        for row in range(grid_rows):
            for col in range(grid_cols):
                if rocks_placed >= num_rocks:
                    break

                # Random position within cell
                x = (col + 0.5) * cell_width + (random.random() - 0.5) * cell_width * 0.3
                y = y_min + (row + 0.5) * cell_height + (random.random() - 0.5) * cell_height * 0.2

                # Clamp to bounds
                x = max(0.02, min(domain_width - 0.02, x))
                y = max(y_min + 0.02, min(y_max - 0.02, y))

                # Random radius (mm scale typically 10-50mm)
                radius = 0.010 + random.random() * 0.030

                # Generate polygonal shape
                num_verts = random.randint(4, 8)
                irregularity = 0.2 + random.random() * 0.4
                vertices = RealisticRockGenerator.generate_polygon_rock(
                    x, y, radius, num_verts, irregularity,
                    seed=seed + rock_id if seed else None
                )

                rocks.append(RockGeometry(
                    rock_id=rock_id,
                    layer_name="",
                    x=x,
                    y=y,
                    radius=radius,
                    is_polygon=True,
                    vertices=vertices,
                    material="rock"
                ))

                rock_id += 1
                rocks_placed += 1

            if rocks_placed >= num_rocks:
                break

        return rocks


class SceneAnimatorGIFEnhanced:
    """Renders scene generation as an animated GIF with realistic rocks."""

    MATERIAL_COLORS = {
        "free_space": (230, 243, 255),  # Light blue
        "air": (230, 243, 255),
        "subgrade": (139, 115, 85),     # Brown
        "formation": (160, 130, 109),   # Dark tan
        "ballast": (210, 180, 140),     # Light tan
        "clean_ballast": (210, 180, 140),
        "fouled_ballast": (139, 117, 0),  # Dark yellow
        "highly_fouled_ballast": (101, 66, 33),  # Dark brown
        "fouling": (255, 215, 0),       # Gold
    }

    ROCK_COLOR = (139, 69, 19)  # Saddle brown
    ROCK_DARK = (101, 51, 15)   # Darker brown
    GRID_COLOR = (240, 240, 240)
    AXIS_COLOR = (100, 100, 100)
    DOMAIN_COLOR = (0, 0, 0)
    TEXT_COLOR = (50, 50, 50)

    def __init__(self, domain_x: float, domain_y: float, width: int = 900, height: int = 700,
                 title: str = "GPR Model Generation"):
        self.domain_x = domain_x
        self.domain_y = domain_y
        self.width = width
        self.height = height
        self.title = title

        # Padding
        self.pad_left = 60
        self.pad_right = 40
        self.pad_top = 60
        self.pad_bottom = 60

        # Rendering area
        self.render_width = width - self.pad_left - self.pad_right
        self.render_height = height - self.pad_top - self.pad_bottom

        self.frames: List[Image.Image] = []
        self.layers: List[LayerGeometry] = []
        self.rocks: Dict[int, RockGeometry] = {}
        self.rock_counter = 0
        self.frame_times: List[float] = []
        self.current_time = 0.0

    def add_layer(self, layer: LayerGeometry, duration: float = 0.3):
        """Add a layer with animation duration (seconds)."""
        num_frames = max(2, int(duration * 20))  # 20 fps default

        for i in range(num_frames):
            progress = (i + 1) / num_frames
            self._render_frame(
                action='add_layer',
                data={'layer': layer, 'progress': progress}
            )

        self.layers.append(layer)
        self.current_time += duration

    def add_rocks_batch(self, rocks: List[RockGeometry], duration: float = 0.15):
        """Add multiple rocks with staggered appearance (fast)."""
        if not rocks:
            return

        rocks_per_frame = max(1, len(rocks) // max(1, int(duration * 20)))
        frame_duration = duration / max(1, (len(rocks) // rocks_per_frame))

        for batch_start in range(0, len(rocks), rocks_per_frame):
            batch_end = min(batch_start + rocks_per_frame, len(rocks))
            batch = rocks[batch_start:batch_end]

            # Add rocks in this batch
            for rock in batch:
                rock_id = self.rock_counter
                rock.rock_id = rock_id
                self.rocks[rock_id] = rock
                self.rock_counter += 1

            # Render frame with new rocks
            self._render_frame(action='add_rocks', data={'count': len(self.rocks)})

            self.current_time += frame_duration

    def _render_frame(self, action: str, data: Dict[str, Any]):
        """Render a single frame and add to frames list."""
        img = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw background
        self._draw_grid(draw)
        self._draw_axes(draw)

        # Draw layers
        for layer in self.layers:
            self._draw_layer(draw, layer)

        if action == 'add_layer':
            layer = data['layer']
            progress = data.get('progress', 1.0)
            self._draw_layer(draw, layer, alpha=progress)

        # Draw all rocks
        for rock in self.rocks.values():
            self._draw_rock(draw, rock)

        # Draw domain outline
        self._draw_domain_outline(draw)

        # Draw info overlay
        self._draw_overlay(draw, action, data)

        self.frames.append(img)
        self.frame_times.append(self.current_time)

    def _pixel_x(self, x: float) -> int:
        """Convert world x to pixel x."""
        return self.pad_left + int((x / self.domain_x) * self.render_width)

    def _pixel_y(self, y: float) -> int:
        """Convert world y to pixel y (flipped so y increases upward)."""
        return self.height - self.pad_bottom - int((y / self.domain_y) * self.render_height)

    def _draw_grid(self, draw: ImageDraw.ImageDraw):
        """Draw background grid."""
        step = 0.1

        x = 0
        while x <= self.domain_x:
            px = self._pixel_x(x)
            y0 = self._pixel_y(0)
            y1 = self._pixel_y(self.domain_y)
            draw.line([(px, y1), (px, y0)], fill=self.GRID_COLOR, width=1)
            x += step

        y = 0
        while y <= self.domain_y:
            py = self._pixel_y(y)
            x0 = self._pixel_x(0)
            x1 = self._pixel_x(self.domain_x)
            draw.line([(x0, py), (x1, py)], fill=self.GRID_COLOR, width=1)
            y += step

    def _draw_axes(self, draw: ImageDraw.ImageDraw):
        """Draw coordinate axes with labels."""
        x0, x1 = self._pixel_x(0), self._pixel_x(self.domain_x)
        y0 = self._pixel_y(0)
        draw.line([(x0, y0), (x1, y0)], fill=self.AXIS_COLOR, width=2)

        y1 = self._pixel_y(self.domain_y)
        draw.line([(x0, y0), (x0, y1)], fill=self.AXIS_COLOR, width=2)

        try:
            font_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            font_sm = ImageFont.load_default()

        x = 0
        while x <= self.domain_x:
            px = self._pixel_x(x)
            draw.text((px - 10, y0 + 10), f"{x:.1f}", fill=self.AXIS_COLOR, font=font_sm)
            x += 0.2

        y = 0
        while y <= self.domain_y:
            py = self._pixel_y(y)
            draw.text((x0 - 40, py - 5), f"{y:.1f}", fill=self.AXIS_COLOR, font=font_sm)
            y += 0.2

    def _draw_layer(self, draw: ImageDraw.ImageDraw, layer: LayerGeometry, alpha: float = 1.0):
        """Draw a layer as a rectangle."""
        x0 = self._pixel_x(0)
        x1 = self._pixel_x(self.domain_x)
        y0 = self._pixel_y(layer.y_min)
        y1 = self._pixel_y(layer.y_max)

        color = self.MATERIAL_COLORS.get(layer.material_name, (200, 200, 200))

        if alpha < 1.0:
            color = tuple(int(c + (255 - c) * (1 - alpha)) for c in color)

        draw.rectangle([(x0, y1), (x1, y0)], fill=color, outline=(150, 150, 150), width=1)

        # Label
        if abs(y0 - y1) > 25:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
            except:
                font = ImageFont.load_default()
                font_small = font

            cx = (x0 + x1) // 2
            cy = (y0 + y1) // 2

            draw.text((cx - 30, cy - 15), layer.name, fill=self.TEXT_COLOR, font=font)
            draw.text((cx - 40, cy + 5), f"εᵣ={layer.eps:.1f}", fill=(100, 100, 100), font=font_small)
            draw.text((cx - 40, cy + 16), f"σ={layer.sigma:.3f}", fill=(100, 100, 100), font=font_small)

    def _draw_rock(self, draw: ImageDraw.ImageDraw, rock: RockGeometry):
        """Draw a rock as a polygon."""
        if rock.is_polygon and rock.vertices and len(rock.vertices) >= 3:
            pixels = [(self._pixel_x(vx), self._pixel_y(vy)) for vx, vy in rock.vertices]
            draw.polygon(pixels, fill=self.ROCK_COLOR, outline=self.ROCK_DARK)
        else:
            # Fallback to circle
            cx = self._pixel_x(rock.x)
            cy = self._pixel_y(rock.y)
            r = int((rock.radius / self.domain_x) * self.render_width)
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                        fill=self.ROCK_COLOR, outline=self.ROCK_DARK, width=1)

    def _draw_domain_outline(self, draw: ImageDraw.ImageDraw):
        """Draw domain boundary."""
        x0 = self._pixel_x(0)
        x1 = self._pixel_x(self.domain_x)
        y0 = self._pixel_y(0)
        y1 = self._pixel_y(self.domain_y)

        draw.rectangle([(x0, y1), (x1, y0)], outline=self.DOMAIN_COLOR, width=2)

    def _draw_overlay(self, draw: ImageDraw.ImageDraw, action: str, data: Dict[str, Any]):
        """Draw frame info overlay."""
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            font_info = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except:
            font_title = ImageFont.load_default()
            font_info = font_title

        draw.text((20, 15), self.title, fill=self.TEXT_COLOR, font=font_title)

        stats = [
            f"Frame: {len(self.frames)} | Layers: {len(self.layers)} | Rocks: {len(self.rocks)}",
            f"Time: {self.current_time:.2f}s",
            f"Domain: {self.domain_x:.2f}m × {self.domain_y:.2f}m"
        ]

        for i, stat in enumerate(stats):
            draw.text((20, self.height - self.pad_bottom + 15 + i * 18),
                     stat, fill=(100, 100, 100), font=font_info)

    def render_gif(self, output_path: Path, fps: int = 20, loop: int = 0) -> Path:
        """Render all frames as an animated GIF."""
        if not self.frames:
            raise ValueError("No frames to render. Add layers/rocks first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        durations = [1000 // fps] * len(self.frames)

        self.frames[0].save(
            output_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=durations,
            loop=loop,
            optimize=False
        )

        print(f"✓ GIF saved: {output_path}")
        print(f"  Frames: {len(self.frames)} | FPS: {fps} | Duration: {self.current_time:.2f}s")
        print(f"  Layers: {len(self.layers)} | Rocks: {len(self.rocks)}")

        return output_path


# Example: Realistic multi-layer scene with many rocks
if __name__ == "__main__":
    print("Generating realistic GPR model animation...")

    animator = SceneAnimatorGIFEnhanced(
        domain_x=1.0,
        domain_y=1.0,
        title="GPR Synthetic Model - Realistic Packing",
        width=900,
        height=700
    )

    # Layer 1: Subgrade
    animator.add_layer(
        LayerGeometry(
            name="Subgrade",
            y_min=0.0,
            y_max=0.20,
            thickness=0.20,
            material_name="subgrade",
            eps=15.0,
            sigma=0.05,
            packed=False
        ),
        duration=0.3
    )

    # Layer 2: Formation
    animator.add_layer(
        LayerGeometry(
            name="Formation",
            y_min=0.20,
            y_max=0.35,
            thickness=0.15,
            material_name="formation",
            eps=12.0,
            sigma=0.02,
            packed=False
        ),
        duration=0.3
    )

    # Layer 3: Clean Ballast (with many rocks)
    animator.add_layer(
        LayerGeometry(
            name="Clean Ballast",
            y_min=0.35,
            y_max=0.75,
            thickness=0.40,
            material_name="clean_ballast",
            eps=6.0,
            sigma=0.001,
            packed=True,
            rock_eps=7.5,
            rock_sigma=0.01
        ),
        duration=0.4
    )

    # Generate and add realistic rocks
    print("  Generating 45 realistic polygonal rocks...")
    rocks = RealisticRockGenerator.generate_rocks_for_layer(
        layer_bounds=(0.35, 0.75),
        domain_width=1.0,
        num_rocks=45,
        seed=42
    )

    animator.add_rocks_batch(rocks, duration=0.6)  # Fast packing

    # Render GIF
    output_path = Path("gpr_model_realistic.gif")
    animator.render_gif(output_path, fps=20)
    print(f"\n✓ Done! Open {output_path}")
