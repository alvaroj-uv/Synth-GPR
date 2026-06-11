# Publication-Quality Figure Export Guide

## Overview

The `PublicationFigureGenerator` module creates professional, print-ready figures suitable for:
- Journal articles (300+ DPI)
- Conference presentations
- Thesis/dissertations  
- Technical reports
- Web publishing

All figures are optimized for readability and professional appearance with:
- High-resolution export (up to 300 DPI)
- Professional font selection and sizing
- Proper aspect ratios and spacing
- Vector format support (PDF, SVG)
- Metadata annotation boxes

---

## Quick Start

### Basic Usage: Export as PNG

```python
from pathlib import Path
from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.parser import parse_in_file

# Parse a gprMax .in file
scene = parse_in_file(Path("data/scene_001.in"))

# Export as high-quality PNG (300 DPI for printing)
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path="figures/scene_001_publication.png",
    title="Railway Ballast Scene",
    dpi=300
)
```

### Export as Vector (PDF/SVG)

```python
from src.visualization.publication_figures import (
    export_scene_as_pdf,
    export_scene_as_svg,
)

# PDF: Ideal for documents and printing
export_scene_as_pdf(
    in_path="data/scene_001.in",
    output_path="figures/scene_001.pdf"
)

# SVG: Editable in vector graphics software
export_scene_as_svg(
    in_path="data/scene_001.in", 
    output_path="figures/scene_001.svg"
)
```

---

## Features

### 1. High-Quality Figure Export

**Function:** `save_high_quality_figure()`

Saves matplotlib figures with professional settings:
- 300 DPI for print (150 DPI for screen)
- Tight layout with minimal whitespace
- Optional transparent background
- Automatic directory creation

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([1, 2, 3], [1, 2, 3])

PublicationFigureGenerator.save_high_quality_figure(
    fig, 
    "output/my_figure.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.1,
    transparent=False
)
```

### 2. Scene Cross-Section Visualization

**Function:** `save_scene_cross_section()`

Creates publication-quality cross-sections showing:
- Layer structure with Y-coordinates
- Rock distributions
- Fouling regions
- Antenna positions
- Material color coding
- Metadata annotation box

```python
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path="figures/cross_section.png",
    title="Fouled Ballast Scene (50% PVC)",
    dpi=300,
    figsize=(8, 6)  # (width, height) in inches
)
```

### 3. Comparison Figures (Side-by-Side)

**Function:** `save_comparison_figures()`

Creates side-by-side comparisons of multiple scenes:
- Useful for showing configuration variations
- Shared color scheme for consistency
- Synchronized scales

```python
in_files = [
    "data/scene_clean.in",
    "data/scene_fouled_25.in", 
    "data/scene_fouled_50.in",
    "data/scene_fouled_75.in",
]

PublicationFigureGenerator.save_comparison_figures(
    in_files,
    output_dir="figures/comparisons",
    dpi=300
)
```

Output: `comparison_all_4_panel.png` with all 4 scenes side-by-side.

### 4. PVC Variation Series

**Function:** `save_pvc_variation_series()`

Generate series showing PVC effect:

```python
# Template for generating multiple PVC levels
PublicationFigureGenerator.save_pvc_variation_series(
    base_in_path="data/base_scene.in",
    pvc_levels=[0, 25, 50, 75, 100],  # Percentages
    output_dir="figures/pvc_series",
    dpi=300
)
```

### 5. Grid Layout (Dataset Overview)

**Function:** `save_grid_layout()`

Create N×M grid showing multiple scenes:

```python
in_files = [
    f"data/scene_{i:03d}.in" 
    for i in range(9)  # 9 scenes
]

PublicationFigureGenerator.save_grid_layout(
    in_files,
    output_path="figures/dataset_overview_3x3.png",
    ncols=3,  # 3 columns = 3×3 grid for 9 scenes
    dpi=300
)
```

---

## Supported Export Formats

| Format | Extension | Best For | Pros | Cons |
|--------|-----------|----------|------|------|
| **PNG** | `.png` | Presentations, web | Fast, universal | Raster, not editable |
| **PDF** | `.pdf` | Documents, printing | Scalable, professional | Large file size |
| **SVG** | `.svg` | Editing in Illustrator | Editable, scalable | May have rendering issues |
| **JPEG** | `.jpg` | Web, thumbnails | Small file size | Lossy compression |

### PNG (Raster)
```python
# 150 DPI for screen/presentations
PublicationFigureGenerator.save_high_quality_figure(fig, "out.png", dpi=150)

# 300 DPI for printing
PublicationFigureGenerator.save_high_quality_figure(fig, "out.png", dpi=300)
```

### PDF (Vector, Best for Print)
```python
export_scene_as_pdf("data/scene.in", "output/scene.pdf")

# Or directly with matplotlib
fig.savefig("output.pdf", format='pdf', bbox_inches='tight')
```

### SVG (Editable Vector)
```python
export_scene_as_svg("data/scene.in", "output/scene.svg")

# Then open in:
# - Adobe Illustrator
# - Inkscape
# - CorelDRAW
```

---

## Professional Style Settings

**Function:** `apply_publication_style()`

Applies optimized matplotlib settings:

```python
from src.visualization.publication_figures import apply_publication_style

apply_publication_style()  # Call once at script start

# Then all matplotlib figures use professional styling:
# - Helvetica/Arial fonts
# - Optimal font sizes
# - High-quality lines
# - Professional appearance
```

Applied settings:
```python
{
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
}
```

---

## Metadata Annotation

Figures automatically include metadata boxes showing:
- PVC (Percentage Void Contamination)
- Lab FI (Fouling Index)
- Class
- Rock count
- Domain dimensions

The annotation box is styled with:
- White background (80% opacity)
- Rounded corners
- Monospace font for readability
- Positioned in top-left corner

Customize with:
```python
ax.text(
    0.02, 0.98,
    custom_metadata_text,
    transform=ax.transAxes,
    fontsize=9,
    verticalalignment='top',
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
)
```

---

## Common Use Cases

### 1. Publication Figure Pipeline

```python
# Workflow for journal submission
from pathlib import Path
from src.visualization.publication_figures import PublicationFigureGenerator

# Output directory
output_dir = Path("paper_figures")
output_dir.mkdir(exist_ok=True)

# List of scenes to visualize
scenes = [
    "data/clean_ballast.in",
    "data/fouled_light.in",
    "data/fouled_heavy.in",
]

for scene_path in scenes:
    scene = parse_in_file(Path(scene_path))
    
    # Export all formats
    PublicationFigureGenerator.save_scene_cross_section(
        scene,
        output_dir / f"{scene_path.stem}_figure.png",
        title=f"Scene: {scene_path.stem}",
        dpi=300  # For journal submission
    )
    
    export_scene_as_pdf(
        scene_path,
        output_dir / f"{scene_path.stem}_figure.pdf"
    )

print(f"Figures saved to {output_dir}")
```

### 2. Presentation Figures

```python
# For PowerPoint/Keynote presentations
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path="presentation_figures/slide_1.png",
    dpi=150,  # 150 DPI sufficient for screen
    figsize=(10, 7.5)  # 4:3 aspect ratio
)
```

### 3. Thesis Figures

```python
# High-quality for thesis
for i, scene_file in enumerate(Path("data").glob("*.in"))[:10]:
    scene = parse_in_file(scene_file)
    
    PublicationFigureGenerator.save_scene_cross_section(
        scene,
        f"thesis_figures/figure_3_{i+1}.png",
        title=f"Configuration {i+1}",
        dpi=300  # Thesis quality
    )
```

### 4. Dataset Overview

```python
# Show variety in dataset
all_scenes = list(Path("data").glob("*.in"))

PublicationFigureGenerator.save_grid_layout(
    all_scenes[:12],
    output_path="dataset_overview.png",
    ncols=4,  # 4×3 grid
    dpi=300
)
```

---

## DPI Guidelines

| Use Case | Recommended DPI | Rationale |
|----------|-----------------|-----------|
| **Screen/Web** | 72-150 | Display resolution |
| **Presentations** | 150 | PowerPoint/Keynote |
| **Documents** | 150-200 | PDF, Word, LaTeX |
| **Journal Submission** | 300 | Publishing standard |
| **High-Quality Print** | 300-600 | Professional printing |

---

## File Size Reference

Typical file sizes at different DPI for 8×6 inch figure:

| Format | 150 DPI | 300 DPI |
|--------|---------|---------|
| PNG | 200-400 KB | 600-1000 KB |
| PDF | 100-200 KB | 150-300 KB |
| SVG | 50-150 KB | 50-150 KB (scale-independent) |

---

## Customization

### Change Figure Size

```python
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path="output.png",
    figsize=(10, 8)  # Width and height in inches
)
```

### Add Custom Title

```python
PublicationFigureGenerator.save_scene_cross_section(
    scene,
    output_path="output.png",
    title="Custom Title - Can include HTML/LaTeX"
)
```

### Change Resolution

```python
# For presentations
PublicationFigureGenerator.save_scene_cross_section(
    scene, "output.png", dpi=150
)

# For printing
PublicationFigureGenerator.save_scene_cross_section(
    scene, "output.png", dpi=300
)

# For high-end printing
PublicationFigureGenerator.save_scene_cross_section(
    scene, "output.png", dpi=600
)
```

### Batch Export

```python
from pathlib import Path

output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

for in_file in Path("data").glob("*.in"):
    scene = parse_in_file(in_file)
    
    PublicationFigureGenerator.save_scene_cross_section(
        scene,
        output_dir / f"{in_file.stem}.png",
        title=f"Scene: {in_file.stem}",
        dpi=300
    )
```

---

## Examples

### Example 1: Single Publication Figure

```python
from src.visualization.publication_figures import PublicationFigureGenerator
from src.visualization.parser import parse_in_file

scene = parse_in_file("data/ballast_50pvc.in")

PublicationFigureGenerator.save_scene_cross_section(
    scene,
    "figures/ballast_50pvc_publication.png",
    title="Railway Ballast (50% Fouled)",
    dpi=300
)
```

### Example 2: Comparison for Paper

```python
scenes = [
    "data/clean_ballast.in",
    "data/fouled_25pvc.in",
    "data/fouled_50pvc.in",
    "data/fouled_75pvc.in",
]

PublicationFigureGenerator.save_comparison_figures(
    scenes,
    output_dir="paper_figures/comparisons",
    dpi=300
)
```

### Example 3: Vector Export for Editing

```python
from src.visualization.publication_figures import export_scene_as_svg

# Export as editable SVG
export_scene_as_svg(
    "data/scene.in",
    "output/scene_editable.svg"
)

# Open in Illustrator or Inkscape
# Add annotations, adjust colors, etc.
```

---

## Integration with Annotated Files

The publication figures work seamlessly with annotated .in files:

```python
# Generate annotated .in file
from src.annotated_file_writer import AnnotatedGPRMaxFileWriter

AnnotatedGPRMaxFileWriter.write_to_file(
    scene, "output/scene.in",
    include_annotations=True
)

# Generate corresponding publication figure
PublicationFigureGenerator.save_scene_cross_section(
    scene, 
    "output/scene_figure.png",
    dpi=300
)

# Result: Complete package with both explained .in file and visualization
```

---

## Testing

Tests are in `tests/test_publication_figures.py`:

```bash
# Run all publication figure tests
pytest tests/test_publication_figures.py -v

# Run specific test
pytest tests/test_publication_figures.py::TestPublicationFigureGenerator::test_save_high_quality_figure -v
```

---

## Troubleshooting

### Figure looks blurry

**Solution:** Increase DPI
```python
PublicationFigureGenerator.save_scene_cross_section(
    scene, "output.png", dpi=300  # Increase from 150
)
```

### Font not rendering

**Solution:** Ensure Helvetica/Arial installed
```bash
# macOS/Linux
fc-list | grep -i helvetica

# Or use system fonts
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
```

### File too large

**Solution:** Use PDF instead of PNG
```python
export_scene_as_pdf("data/scene.in", "output.pdf")
# PDF typically 50% smaller than PNG for same content
```

### Colors not printing correctly

**Solution:** Use CMYK for print
```python
fig.savefig("output.pdf", format='pdf', metadata={'Creator': 'Synth-GPR'})
```

---

## Best Practices

1. **Use 300 DPI for print** - 150 DPI for screen
2. **Export as PDF for publications** - More reliable than PNG
3. **Use SVG for editing** - Maintain scalability
4. **Include metadata boxes** - Helps readers understand context
5. **Test output before submitting** - Check in actual publication software
6. **Use consistent sizing** - Makes multipart figures more professional
7. **Batch export all figures** - Ensures consistent settings

---

## Demo

Run the demonstration script:

```bash
python examples/publication_figures_demo.py
```

This will:
1. Export PNG at 300 DPI (printing quality)
2. Export PDF (for documents)
3. Export SVG (for editing)
4. Create comparison figures
5. Create grid layout
6. Show file sizes and information

---

## Summary

The `PublicationFigureGenerator` module provides:

✅ **High-quality exports** (PNG, PDF, SVG)
✅ **Professional styling** (fonts, sizes, spacing)
✅ **Multiple views** (single, comparison, grid)
✅ **Metadata annotation** (automatic or custom)
✅ **Batch processing** (apply settings to many figures)
✅ **Vector formats** (scalable, editable)

Perfect for:
- 📄 Journal articles
- 🎤 Conference presentations
- 📚 Thesis/dissertations
- 📊 Technical reports
- 🌐 Web publishing

