#!/usr/bin/env python3
"""
Dense rock packing MP4 animator with correctly placed GPR antennas.

Features:
  - MP4 video output (better quality than GIF)
  - Proper TX/RX antenna visualization above domain
  - Monostatic (co-located) or bistatic antenna modes
  - 122 densely-packed rocks
"""

import math
import random
import subprocess
import tempfile
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
        """Generate densely packed rocks using collision detection."""
        if seed is not None:
            random.seed(seed)

        y_min, y_max = layer_bounds
        layer_height = y_max - y_min
        rocks = []
        rock_id = 0

        # Pass 1: Large rocks (55%)
        num_large = int(num_rocks * 0.55)
        for i in range(num_large):
            max_attempts = 5
            for attempt in range(max_attempts):
                x = random.uniform(0.03, domain_width - 0.03)
                y = random.uniform(y_min + 0.03, y_max - 0.03)
                radius = 0.015 + random.random() * 0.020

                collision = False
                for rock in rocks:
                    dist = math.sqrt((rock.x - x) ** 2 + (rock.y - y) ** 2)
                    if dist < (rock.radius + radius) * 1.1:
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

        # Pass 2: Medium rocks (35%)
        num_medium = int(num_rocks * 0.35)
        for i in range(num_medium):
            max_attempts = 3
            for attempt in range(max_attempts):
                x = random.uniform(0.02, domain_width - 0.02)
                y = random.uniform(y_min + 0.02, y_max - 0.02)
                radius = 0.008 + random.random() * 0.012

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

        # Pass 3: Small rocks (fill remaining)
        num_small = num_rocks - len(rocks)
        for i in range(num_small):
            max_attempts = 2
            for attempt in range(max_attempts):
                x = random.uniform(0.015, domain_width - 0.015)
                y = random.uniform(y_min + 0.015, y_max - 0.015)
                radius = 0.003 + random.random() * 0.007

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


class SceneAnimatorMP4:
    """MP4 animator with proper antenna placement."""

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

    def __init__(self, domain_x: float, domain_y: float, antenna_mode: str = "monostatic",
                 tx_x: float = 0.5, rx_x: float = 0.5, width: int = 900, height: int = 700,
                 title: str = "GPR Model Generation"):
        self.domain_x = domain_x
        self.domain_y = domain_y
        self.antenna_mode = antenna_mode  # "monostatic" or "bistatic"
        self.tx_x = tx_x  # TX position (world coords)
        self.rx_x = rx_x  # RX position (world coords)
        self.width = width
        self.height = height
        self.title = title

        self.pad_left = 60
        self.pad_right = 40
        self.pad_top = 80
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
        num_frames = max(2, int(duration * 30))  # 30 fps for MP4

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

        num_batches = max(3, int(duration * 30))
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
        self._draw_antennas(draw)
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

    def _draw_antennas(self, draw: ImageDraw.ImageDraw):
        """Draw TX/RX antennas above the domain."""
        domain_top = self._pixel_y(self.domain_y)
        antenna_height = 30
        antenna_width = 8

        # Transmitter (TX) - Red dipole
        tx_x = self._pixel_x(self.tx_x)
        tx_top = domain_top - antenna_height - 10
        tx_mid = tx_top + antenna_height // 2

        # Vertical antenna pole
        draw.line([(tx_x, tx_top), (tx_x, tx_mid + antenna_height // 4)],
                 fill=(255, 0, 0), width=3)

        # Dipole arms
        draw.line([(tx_x - antenna_width, tx_mid), (tx_x + antenna_width, tx_mid)],
                 fill=(255, 0, 0), width=4)

        # Top and bottom nubs
        draw.ellipse([(tx_x - 4, tx_top - 4), (tx_x + 4, tx_top + 4)],
                    fill=(255, 0, 0), outline=(0, 0, 0), width=1)
        draw.ellipse([(tx_x - 4, tx_mid + antenna_height // 4 - 4),
                     (tx_x + 4, tx_mid + antenna_height // 4 + 4)],
                    fill=(255, 0, 0), outline=(0, 0, 0), width=1)

        # TX label
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        except:
            font = ImageFont.load_default()

        draw.text((tx_x - 12, tx_top - 25), "TX", fill=(255, 0, 0), font=font)

        # Receiver (RX) - Blue dipole
        rx_x = self._pixel_x(self.rx_x)
        rx_top = domain_top - antenna_height - 10
        rx_mid = rx_top + antenna_height // 2

        # Vertical antenna pole
        draw.line([(rx_x, rx_top), (rx_x, rx_mid + antenna_height // 4)],
                 fill=(0, 0, 255), width=3)

        # Dipole arms
        draw.line([(rx_x - antenna_width, rx_mid), (rx_x + antenna_width, rx_mid)],
                 fill=(0, 0, 255), width=4)

        # Top and bottom nubs
        draw.ellipse([(rx_x - 4, rx_top - 4), (rx_x + 4, rx_top + 4)],
                    fill=(0, 0, 255), outline=(0, 0, 0), width=1)
        draw.ellipse([(rx_x - 4, rx_mid + antenna_height // 4 - 4),
                     (rx_x + 4, rx_mid + antenna_height // 4 + 4)],
                    fill=(0, 0, 255), outline=(0, 0, 0), width=1)

        # RX label
        draw.text((rx_x - 12, rx_top - 25), "RX", fill=(0, 0, 255), font=font)

        # Monostatic note
        if abs(self.tx_x - self.rx_x) < 0.01:
            draw.text((self.width // 2 - 50, domain_top - 55), "Monostatic (co-located)",
                     fill=(100, 100, 100), font=font)

    def _draw_overlay(self, draw: ImageDraw.ImageDraw, action: str, data: Dict[str, Any]):
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

    def render_mp4(self, output_path: Path, fps: int = 30) -> Path:
        """Render all frames as MP4 using ffmpeg."""
        if not self.frames:
            raise ValueError("No frames to render.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Save all frames
            print(f"  Saving {len(self.frames)} frames...")
            for i, frame in enumerate(self.frames):
                frame_path = tmpdir / f"frame_{i:04d}.png"
                frame.save(frame_path)

            # Use ffmpeg to create MP4
            print(f"  Encoding MP4 with ffmpeg ({fps} fps)...")
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-framerate', str(fps),
                '-i', str(tmpdir / 'frame_%04d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',  # Quality (lower = better)
                str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("ffmpeg error:", result.stderr)
                raise RuntimeError("ffmpeg encoding failed")

        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ MP4 saved: {output_path}")
        print(f"  Frames: {len(self.frames)} | FPS: {fps} | Duration: {self.current_time:.2f}s | Size: {file_size_mb:.1f}MB")
        print(f"  Layers: {len(self.layers)} | Rocks: {len(self.rocks)}")

        return output_path


# Main
if __name__ == "__main__":
    print("Generating dense rock packing MP4 with antennas...")

    animator = SceneAnimatorMP4(
        domain_x=1.0,
        domain_y=1.0,
        antenna_mode="monostatic",
        tx_x=0.5,  # Center
        rx_x=0.5,  # Co-located
        title="Dense GPR Ballast Packing - 122 Rocks",
        width=1000,
        height=800
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

    # Clean Ballast
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

    # Dense rocks
    print("  Generating 150 densely-packed rocks...")
    rocks = DenseRockGenerator.generate_dense_rocks(
        layer_bounds=(0.35, 0.75),
        domain_width=1.0,
        num_rocks=150,
        seed=42
    )
    print(f"  Placed {len(rocks)} rocks")

    animator.add_rocks_fast(rocks, duration=0.8)

    # Render MP4
    output_path = Path("gpr_dense_packing.mp4")
    animator.render_mp4(output_path, fps=30)
    print(f"\n✓ Done! Open {output_path}")
