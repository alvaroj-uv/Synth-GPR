#!/usr/bin/env python3
"""
Dense rock packing GIF animator - pack 150+ realistic rocks fast.
"""

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


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


class DenseRockGenerator:
    """Generate dense realistic rock packings."""

    @staticmethod
    def generate_polygon_rock(center_x: float, center_y: float, radius: float,
                             num_vertices: int = 5, irregularity: float = 0.3,
                             seed: Optional[int] = None) -> List[Tuple[float, float]]:
        """Generate a realistic polygonal rock."""
        if seed is not None:
            random.seed(seed)

        vertices = []
        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            angle_variation = (random.random() - 0.5) * (2 * math.pi / num_vertices)
            angle += angle_variation
            r = radius * (1 - irregularity * random.random())
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            vertices.append((x, y))

        return vertices

    @staticmethod
    def generate_dense_rocks(layer_bounds: Tuple[float, float], domain_width: float,
                            num_rocks: int, seed: Optional[int] = None) -> List[RockGeometry]:
        """Generate densely packed rocks using Poisson-disk-like distribution."""
        if seed is not None:
            random.seed(seed)

        y_min, y_max = layer_bounds
        layer_height = y_max - y_min
        rocks = []

        # Multiple passes: large rocks first, then fill gaps with smaller rocks
        rock_id = 0

        # Pass 1: Large rocks (50-60% of rocks, 25-35mm radius)
        num_large = int(num_rocks * 0.55)
        for i in range(num_large):
            max_attempts = 5
            for attempt in range(max_attempts):
                x = random.uniform(0.03, domain_width - 0.03)
                y = random.uniform(y_min + 0.03, y_max - 0.03)
                radius = 0.015 + random.random() * 0.020  # 15-35mm

                # Check collision with existing rocks
                collision = False
                for rock in rocks:
                    dist = math.sqrt((rock.x - x) ** 2 + (rock.y - y) ** 2)
                    if dist < (rock.radius + radius) * 1.1:  # 10% safety margin
                        collision = True
                        break

                if not collision:
                    num_verts = random.randint(5, 8)
                    irregularity = 0.25 + random.random() * 0.35
                    vertices = DenseRockGenerator.generate_polygon_rock(
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
                    break

        # Pass 2: Medium rocks (30-35% of rocks, 10-20mm radius)
        num_medium = int(num_rocks * 0.35)
        for i in range(num_medium):
            max_attempts = 3
            for attempt in range(max_attempts):
                x = random.uniform(0.02, domain_width - 0.02)
                y = random.uniform(y_min + 0.02, y_max - 0.02)
                radius = 0.008 + random.random() * 0.012  # 8-20mm

                collision = False
                for rock in rocks:
                    dist = math.sqrt((rock.x - x) ** 2 + (rock.y - y) ** 2)
                    if dist < (rock.radius + radius) * 1.05:
                        collision = True
                        break

                if not collision:
                    num_verts = random.randint(4, 6)
                    irregularity = 0.20 + random.random() * 0.40
                    vertices = DenseRockGenerator.generate_polygon_rock(
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
                    break

        # Pass 3: Small rocks (15-20% of rocks, 3-10mm radius) - fill gaps
        num_small = num_rocks - len(rocks)
        for i in range(num_small):
            max_attempts = 2
            for attempt in range(max_attempts):
                x = random.uniform(0.015, domain_width - 0.015)
                y = random.uniform(y_min + 0.015, y_max - 0.015)
                radius = 0.003 + random.random() * 0.007  # 3-10mm

                collision = False
                for rock in rocks:
                    dist = math.sqrt((rock.x - x) ** 2 + (rock.y - y) ** 2)
                    if dist < (rock.radius + radius) * 1.02:
                        collision = True
                        break

                if not collision:
                    num_verts = random.randint(4, 6)
                    irregularity = 0.15 + random.random() * 0.35
                    vertices = DenseRockGenerator.generate_polygon_rock(
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
                    break

        return rocks


class SceneAnimatorDense:
    """Dense rock animation with fast filling."""

    MATERIAL_COLORS = {
        "free_space": (230, 243, 255),
        "air": (230, 243, 255),
        "subgrade": (139, 115, 85),
        "formation": (160, 130, 109),
        "ballast": (210, 180, 140),
        "clean_ballast": (210, 180, 140),
        "fouled_ballast": (139, 117, 0),
        "highly_fouled_ballast": (101, 66, 33),
        "fouling": (255, 215, 0),
    }

    ROCK_COLOR = (139, 69, 19)
    ROCK_DARK = (101, 51, 15)
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

        self.pad_left = 60
        self.pad_right = 40
        self.pad_top = 60
        self.pad_bottom = 60

        self.render_width = width - self.pad_left - self.pad_right
        self.render_height = height - self.pad_top - self.pad_bottom

        self.frames: List[Image.Image] = []
        self.layers: List[LayerGeometry] = []
        self.rocks: Dict[int, RockGeometry] = {}
        self.rock_counter = 0
        self.current_time = 0.0

    def add_layer(self, layer: LayerGeometry, duration: float = 0.3):
        """Add a layer."""
        num_frames = max(2, int(duration * 20))

        for i in range(num_frames):
            progress = (i + 1) / num_frames
            self._render_frame(
                action='add_layer',
                data={'layer': layer, 'progress': progress}
            )

        self.layers.append(layer)
        self.current_time += duration

    def add_rocks_fast(self, rocks: List[RockGeometry], duration: float = 0.8):
        """Add many rocks very fast."""
        if not rocks:
            return

        # Batch rocks into groups for progressive filling
        num_batches = max(3, int(duration * 20))
        rocks_per_batch = (len(rocks) + num_batches - 1) // num_batches
        batch_duration = duration / num_batches

        for batch_start in range(0, len(rocks), rocks_per_batch):
            batch_end = min(batch_start + rocks_per_batch, len(rocks))
            batch = rocks[batch_start:batch_end]

            for rock in batch:
                rock_id = self.rock_counter
                rock.rock_id = rock_id
                self.rocks[rock_id] = rock
                self.rock_counter += 1

            self._render_frame(action='add_rocks', data={'count': len(self.rocks)})
            self.current_time += batch_duration

    def _render_frame(self, action: str, data: Dict[str, Any]):
        """Render a single frame."""
        img = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        self._draw_grid(draw)
        self._draw_axes(draw)

        for layer in self.layers:
            self._draw_layer(draw, layer)

        if action == 'add_layer':
            layer = data['layer']
            progress = data.get('progress', 1.0)
            self._draw_layer(draw, layer, alpha=progress)

        for rock in self.rocks.values():
            self._draw_rock(draw, rock)

        self._draw_domain_outline(draw)
        self._draw_overlay(draw, action, data)

        self.frames.append(img)

    def _pixel_x(self, x: float) -> int:
        return self.pad_left + int((x / self.domain_x) * self.render_width)

    def _pixel_y(self, y: float) -> int:
        return self.height - self.pad_bottom - int((y / self.domain_y) * self.render_height)

    def _draw_grid(self, draw: ImageDraw.ImageDraw):
        step = 0.1
        x = 0
        while x <= self.domain_x:
            px = self._pixel_x(x)
            y0, y1 = self._pixel_y(0), self._pixel_y(self.domain_y)
            draw.line([(px, y1), (px, y0)], fill=self.GRID_COLOR, width=1)
            x += step

        y = 0
        while y <= self.domain_y:
            py = self._pixel_y(y)
            x0, x1 = self._pixel_x(0), self._pixel_x(self.domain_x)
            draw.line([(x0, py), (x1, py)], fill=self.GRID_COLOR, width=1)
            y += step

    def _draw_axes(self, draw: ImageDraw.ImageDraw):
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
        x0 = self._pixel_x(0)
        x1 = self._pixel_x(self.domain_x)
        y0 = self._pixel_y(layer.y_min)
        y1 = self._pixel_y(layer.y_max)

        color = self.MATERIAL_COLORS.get(layer.material_name, (200, 200, 200))

        if alpha < 1.0:
            color = tuple(int(c + (255 - c) * (1 - alpha)) for c in color)

        draw.rectangle([(x0, y1), (x1, y0)], fill=color, outline=(150, 150, 150), width=1)

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
        if rock.is_polygon and rock.vertices and len(rock.vertices) >= 3:
            pixels = [(self._pixel_x(vx), self._pixel_y(vy)) for vx, vy in rock.vertices]
            draw.polygon(pixels, fill=self.ROCK_COLOR, outline=self.ROCK_DARK)

    def _draw_domain_outline(self, draw: ImageDraw.ImageDraw):
        x0 = self._pixel_x(0)
        x1 = self._pixel_x(self.domain_x)
        y0 = self._pixel_y(0)
        y1 = self._pixel_y(self.domain_y)
        draw.rectangle([(x0, y1), (x1, y0)], outline=self.DOMAIN_COLOR, width=2)

    def _draw_antenna(self, draw: ImageDraw.ImageDraw, x_world: float, label: str, color):
        """Draw a GPR antenna at position."""
        x = self._pixel_x(x_world)
        y = self._pixel_y(self.domain_y) - 30  # Above domain

        # Antenna dipole (vertical line with dots at ends)
        draw.line([(x, y - 15), (x, y + 5)], fill=color, width=3)
        draw.ellipse([(x - 4, y - 19), (x + 4, y - 11)], fill=color, outline=(0, 0, 0), width=1)
        draw.ellipse([(x - 4, y + 1), (x + 4, y + 9)], fill=color, outline=(0, 0, 0), width=1)

        # Label
        try:
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            font_small = ImageFont.load_default()

        draw.text((x - 15, y + 15), label, fill=color, font=font_small)

    def _draw_overlay(self, draw: ImageDraw.ImageDraw, action: str, data: Dict[str, Any]):
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            font_info = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except:
            font_title = ImageFont.load_default()
            font_info = font_title

        draw.text((20, 15), self.title, fill=self.TEXT_COLOR, font=font_title)

        # Draw antennas
        tx_color = (255, 0, 0)    # Red for TX
        rx_color = (0, 0, 255)    # Blue for RX

        # Transmitter at left
        self._draw_antenna(draw, 0.2, "TX", tx_color)

        # Receiver at right (monostatic: co-located)
        self._draw_antenna(draw, 0.2, "RX", rx_color)

        stats = [
            f"Frame: {len(self.frames)} | Layers: {len(self.layers)} | Rocks: {len(self.rocks)}",
            f"Time: {self.current_time:.2f}s",
            f"Domain: {self.domain_x:.2f}m × {self.domain_y:.2f}m"
        ]

        for i, stat in enumerate(stats):
            draw.text((20, self.height - self.pad_bottom + 15 + i * 18),
                     stat, fill=(100, 100, 100), font=font_info)

    def render_gif(self, output_path: Path, fps: int = 25, loop: int = 0) -> Path:
        """Render GIF."""
        if not self.frames:
            raise ValueError("No frames to render.")

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


# Main: Dense packing with 150+ rocks
if __name__ == "__main__":
    print("Generating DENSE rock packing animation (150+ rocks)...")

    animator = SceneAnimatorDense(
        domain_x=1.0,
        domain_y=1.0,
        title="Dense GPR Ballast Packing - 150+ Rocks",
        width=900,
        height=700
    )

    # Subgrade
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
        duration=0.2
    )

    # Formation
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
        duration=0.2
    )

    # Clean Ballast with many rocks
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
        duration=0.3
    )

    # Generate dense rocks: 3-pass collision detection
    print("  Generating 150 densely-packed rocks with collision detection...")
    rocks = DenseRockGenerator.generate_dense_rocks(
        layer_bounds=(0.35, 0.75),
        domain_width=1.0,
        num_rocks=150,
        seed=42
    )
    print(f"  Placed {len(rocks)} rocks")

    animator.add_rocks_fast(rocks, duration=0.8)

    # Render
    output_path = Path("gpr_dense_packing.gif")
    animator.render_gif(output_path, fps=25)
    print(f"\n✓ Done! Open {output_path}")
