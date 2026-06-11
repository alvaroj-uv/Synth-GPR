#!/usr/bin/env python3
"""
GIF animator for GPR synthetic model generation.

Creates animated GIFs showing:
  1. Domain construction (coordinate system)
  2. Layer painting (bottom → top, painter's algorithm)
  3. Rock placement with gravity settling
  4. Material properties and statistics

Fixes: Y-axis now points UP (geologically correct), not down.

Usage:
    animator = SceneAnimatorGIF(domain_x=1.0, domain_y=1.0)
    animator.add_layer(layer_spec, duration=0.5)
    animator.add_rock(rock_spec, settle_duration=0.3)
    animator.render_gif('output.gif', fps=20)
"""

import io
import math
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


class SceneAnimatorGIF:
    """Renders scene generation as an animated GIF."""

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

    def __init__(self, domain_x: float, domain_y: float, width: int = 800, height: int = 600,
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

    def add_layer(self, layer: LayerGeometry, duration: float = 0.5):
        """Add a layer with animation duration (seconds)."""
        # Render frames for layer fade-in
        num_frames = max(1, int(duration * 20))  # 20 fps default

        for i in range(num_frames):
            progress = (i + 1) / num_frames
            self._render_frame(
                action='add_layer',
                data={'layer': layer, 'progress': progress}
            )

        self.layers.append(layer)
        self.current_time += duration

    def add_rock(self, rock: RockGeometry, settle_duration: float = 0.3):
        """Add a rock with settling animation."""
        rock_id = self.rock_counter
        self.rock_counter += 1

        # Placement frame
        self._render_frame(
            action='place_rock',
            data={'rock': rock, 'rock_id': rock_id}
        )

        # Settling animation (y changes gradually)
        if settle_duration > 0:
            num_frames = max(1, int(settle_duration * 20))
            for i in range(num_frames):
                progress = (i + 1) / num_frames
                self._render_frame(
                    action='settle_rock',
                    data={'rock': rock, 'rock_id': rock_id, 'progress': progress}
                )
            self.current_time += settle_duration

        self.rocks[rock_id] = rock

    def _render_frame(self, action: str, data: Dict[str, Any]):
        """Render a single frame and add to frames list."""
        # Create image
        img = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Draw background
        self._draw_grid(draw)
        self._draw_axes(draw)

        # Draw existing layers
        for layer in self.layers:
            self._draw_layer(draw, layer)

        # Handle action-specific drawing
        if action == 'add_layer':
            layer = data['layer']
            progress = data.get('progress', 1.0)
            self._draw_layer(draw, layer, alpha=progress)

        # Draw existing rocks
        for rock in self.rocks.values():
            self._draw_rock(draw, rock)

        if action in ('place_rock', 'settle_rock'):
            rock = data['rock']
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
        # Y-axis: 0 at bottom, domain_y at top
        return self.height - self.pad_bottom - int((y / self.domain_y) * self.render_height)

    def _draw_grid(self, draw: ImageDraw.ImageDraw):
        """Draw background grid."""
        step = 0.1  # 10 cm

        # Vertical lines
        x = 0
        while x <= self.domain_x:
            px = self._pixel_x(x)
            y0 = self._pixel_y(0)
            y1 = self._pixel_y(self.domain_y)
            draw.line([(px, y1), (px, y0)], fill=self.GRID_COLOR, width=1)
            x += step

        # Horizontal lines
        y = 0
        while y <= self.domain_y:
            py = self._pixel_y(y)
            x0 = self._pixel_x(0)
            x1 = self._pixel_x(self.domain_x)
            draw.line([(x0, py), (x1, py)], fill=self.GRID_COLOR, width=1)
            y += step

    def _draw_axes(self, draw: ImageDraw.ImageDraw):
        """Draw coordinate axes with labels."""
        # X-axis
        x0, x1 = self._pixel_x(0), self._pixel_x(self.domain_x)
        y0 = self._pixel_y(0)
        draw.line([(x0, y0), (x1, y0)], fill=self.AXIS_COLOR, width=2)

        # Y-axis
        y1 = self._pixel_y(self.domain_y)
        draw.line([(x0, y0), (x0, y1)], fill=self.AXIS_COLOR, width=2)

        # X labels
        try:
            font_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            font_sm = ImageFont.load_default()

        x = 0
        while x <= self.domain_x:
            px = self._pixel_x(x)
            draw.text((px - 10, y0 + 10), f"{x:.1f}", fill=self.AXIS_COLOR, font=font_sm)
            x += 0.2

        # Y labels
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

        # Apply alpha by blending with white
        if alpha < 1.0:
            color = tuple(int(c + (255 - c) * (1 - alpha)) for c in color)

        draw.rectangle([(x0, y1), (x1, y0)], fill=color, outline=(150, 150, 150), width=1)

        # Layer label (if thick enough)
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
            eps_text = f"εᵣ={layer.eps:.1f}"
            sigma_text = f"σ={layer.sigma:.3f}"
            draw.text((cx - 40, cy + 5), eps_text, fill=(100, 100, 100), font=font_small)
            draw.text((cx - 40, cy + 16), sigma_text, fill=(100, 100, 100), font=font_small)

    def _draw_rock(self, draw: ImageDraw.ImageDraw, rock: RockGeometry):
        """Draw a rock as a circle or polygon."""
        if rock.is_polygon and rock.vertices:
            self._draw_polygon_rock(draw, rock)
        else:
            self._draw_circle_rock(draw, rock)

    def _draw_circle_rock(self, draw: ImageDraw.ImageDraw, rock: RockGeometry):
        """Draw rock as a circle."""
        cx = self._pixel_x(rock.x)
        cy = self._pixel_y(rock.y)
        r = int((rock.radius / self.domain_x) * self.render_width)

        color = rock.color if rock.color else self.ROCK_COLOR
        if isinstance(color, str):
            # Convert hex to RGB
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                     fill=color, outline=self.ROCK_DARK, width=1)

    def _draw_polygon_rock(self, draw: ImageDraw.ImageDraw, rock: RockGeometry):
        """Draw rock as a polygon."""
        if not rock.vertices or len(rock.vertices) < 3:
            return

        pixels = [(self._pixel_x(vx), self._pixel_y(vy)) for vx, vy in rock.vertices]
        color = rock.color if rock.color else self.ROCK_COLOR
        if isinstance(color, str):
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        draw.polygon(pixels, fill=color, outline=self.ROCK_DARK)

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

        # Title
        draw.text((20, 15), self.title, fill=self.TEXT_COLOR, font=font_title)

        # Stats
        stats = [
            f"Frame: {len(self.frames)} | Layers: {len(self.layers)} | Rocks: {len(self.rocks)}",
            f"Time: {self.current_time:.2f}s",
            f"Domain: {self.domain_x:.2f}m × {self.domain_y:.2f}m"
        ]

        for i, stat in enumerate(stats):
            draw.text((20, self.height - self.pad_bottom + 15 + i * 18),
                     stat, fill=(100, 100, 100), font=font_info)

    def render_gif(self, output_path: Path, fps: int = 20, loop: int = 0) -> Path:
        """Render all frames as an animated GIF.

        Args:
            output_path: Path to save GIF
            fps: Frames per second
            loop: 0 = infinite loop, N = loop N times

        Returns:
            Path to generated GIF
        """
        if not self.frames:
            raise ValueError("No frames to render. Add layers/rocks first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate frame durations (in milliseconds)
        durations = []
        frame_time_delta = 1000 // fps  # ms per frame at target fps

        for i, img in enumerate(self.frames):
            durations.append(frame_time_delta)

        # Save GIF
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

        return output_path


# Example usage
if __name__ == "__main__":
    print("Generating sample animation...")

    animator = SceneAnimatorGIF(
        domain_x=1.0,
        domain_y=1.0,
        title="GPR Synthetic Model Generation",
        width=900,
        height=700
    )

    # Add layers bottom-to-top
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
        duration=1.0
    )

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
        duration=1.0
    )

    animator.add_layer(
        LayerGeometry(
            name="Clean Ballast",
            y_min=0.35,
            y_max=0.70,
            thickness=0.35,
            material_name="clean_ballast",
            eps=6.0,
            sigma=0.001,
            packed=True,
            rock_eps=7.5,
            rock_sigma=0.01
        ),
        duration=1.5
    )

    # Add rocks
    import random
    random.seed(42)
    for i in range(12):
        animator.add_rock(
            RockGeometry(
                rock_id=i,
                layer_name="Clean Ballast",
                x=0.05 + random.random() * 0.90,
                y=0.40 + random.random() * 0.28,
                radius=0.015 + random.random() * 0.025,
                is_polygon=False,
                material="rock"
            ),
            settle_duration=0.4
        )

    # Render GIF
    output_path = Path("gpr_model_animation.gif")
    animator.render_gif(output_path, fps=15)
    print(f"\nOpen {output_path} to view the animation!")
