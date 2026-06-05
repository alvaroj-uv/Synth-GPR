# Visualization Ideas from PINN4GPR for Synth-GPR

## Overview

The PINN4GPR project (neural networks for GPR field prediction) has several sophisticated visualization approaches that can be adapted to enhance Synth-GPR's annotated input files and scene visualization.

---

## 1. Field Animation Visualization

### From PINN4GPR: `field.py`

```python
def save_field_animation(field: np.ndarray, output_path: str | Path, 
                        bound_mult_factor: float = 0.2, interval: float = 400):
    """
    Creates and saves an animation of field evolution over time.
    Shows how EM field evolves timestep by timestep.
    """
```

### Application to Synth-GPR:

Generate **animated layer construction visualization** showing how the scene is painted:

```python
class SceneAnimationVisualizer:
    """Animate the painter's algorithm scene construction"""
    
    def animate_scene_building(self, scene: SceneCheckpoint, output_path: str):
        """
        Generate animation showing:
        1. Paint air (baseline) ← Frame 1
        2. Paint subgrade        ← Frame 2
        3. Paint formation       ← Frame 3
        4. Paint ballast         ← Frame 4
        5. Paint rocks           ← Frames 5-N
        6. Paint fouling         ← Frame N+1
        
        Each frame shows the current material configuration with color coding:
        • Blue: Air (ER=1)
        • Brown: Soil (ER=10)
        • Gray: Formation (ER=10)
        • Tan: Ballast (ER=5)
        • Red: Rocks
        • Dark Red: Fouling covering rocks
        """
        frames = []
        
        # Frame 1: All air
        frames.append(self._render_layer_frame("Air", [0, 1.15], color='lightblue'))
        
        # Frame 2: Add subgrade
        frames.append(self._render_layer_frame(
            "Subgrade (0→0.2m)",
            [0, 0.2],
            color='brown'
        ))
        
        # ... Continue for each layer ...
        
        # Create animation
        self._create_animation(frames, output_path)
```

### Benefits:
✅ Users understand the layer ordering intuitively
✅ Shows how painter's algorithm works step-by-step
✅ Verifies no overlaps or gaps
✅ Educational tool for learning

---

## 2. Multi-Panel Comparison Figures

### From PINN4GPR: `model_predictions.py`

```python
def save_4_5_fig(path, imgs, vmin, vmax, extent):
    """
    Side-by-side comparison of 4-5 images with shared colorbar.
    Used for comparing predictions vs ground truth.
    """
    fig, axs = plt.subplots(ncols=len(imgs), sharey=True)
    # ... plot each image with consistent scaling ...
    fig.colorbar(mappable, cax=cbar_ax)
```

### Application to Synth-GPR:

Generate **configuration comparison figures**:

```python
class ConfigurationComparator:
    """Compare multiple scene configurations side-by-side"""
    
    def compare_pvc_levels(self, configs: List[GeneratorConfig], output_path: str):
        """
        Generate 5-panel figure showing:
        
        [0% PVC]  [25% PVC]  [50% PVC]  [75% PVC]  [100% PVC]
        
        Each panel shows:
        • Coordinate system (Y-axis with layer boundaries)
        • Rock distribution
        • Fouling depth
        • Color-coded materials
        • Shared colorbar for ER values
        """
        fig, axs = plt.subplots(ncols=5, sharey=True, figsize=(20, 5))
        
        for i, (ax, config) in enumerate(zip(axs, configs)):
            # Render configuration as 2D cross-section
            scene = self.generate_scene(config)
            img = self._scene_to_image(scene)
            
            # Plot with consistent scaling
            mappable = ax.imshow(img, vmin=1, vmax=20, cmap="jet")
            ax.set_title(f"{config.pvc}% PVC")
            if i > 0:
                ax.set_ylabel(None)
        
        # Shared colorbar showing ER values
        fig.colorbar(mappable, ax=axs, label="Relative Permittivity (ER)")
        fig.tight_layout()
        fig.savefig(output_path)
```

### Benefits:
✅ Understand PVC effect on geometry visually
✅ Compare different configurations immediately
✅ Consistent scale makes comparisons valid
✅ Professional publication quality

---

## 3. Distribution Histograms

### From PINN4GPR: `distribs.py`

```python
def show_ballast_distributions():
    """
    Create histograms comparing clean vs fouled ballast radii distributions.
    Uses stacked bars with transparency for comparison.
    """
    plt.bar(x=positions, height=height_clean, width=width, 
            label="clean", align='edge', alpha=1)
    plt.bar(x=positions, height=height_fouled, width=width, 
            label="fouled", align='edge', alpha=0.7)
```

### Application to Synth-GPR:

Generate **rock property distributions**:

```python
class RockDistributionVisualizer:
    """Visualize rock aggregate statistics"""
    
    def plot_rock_size_distribution(self, scene: SceneCheckpoint, 
                                    output_path: str):
        """
        Generate histogram of rock radii in the generated scene.
        Shows how packing algorithm distributed particle sizes.
        
        Helps verify:
        • No clustering of same-size particles
        • Expected distribution (should match input spec)
        • Visible vs hidden rocks (fouling effect)
        """
        rocks = scene.rocks
        radii = [rock.radius for rock in rocks]
        
        # Separate visible from hidden (fouled)
        visible_radii = [r for r, rock in zip(radii, rocks) 
                        if rock.center_y > scene.fouling_top_y]
        hidden_radii = [r for r, rock in zip(radii, rocks) 
                       if rock.center_y <= scene.fouling_top_y]
        
        # Plot stacked histogram
        plt.hist(hidden_radii, bins=20, alpha=0.7, label="Hidden by fouling")
        plt.hist(visible_radii, bins=20, alpha=1.0, label="Visible to antenna")
        plt.xlabel("Rock Radius (m)")
        plt.ylabel("Frequency")
        plt.legend()
        plt.savefig(output_path)
    
    def plot_rock_position_heatmap(self, scene: SceneCheckpoint, 
                                   output_path: str):
        """
        2D heatmap showing rock positions and density distribution.
        
        X-axis: Horizontal position in domain
        Y-axis: Depth in track
        Color intensity: Rock density at each location
        
        Helps verify:
        • Even distribution (no packing artifacts)
        • Gravity settling worked correctly
        • Fouling coverage is as expected
        """
        x_bins = np.linspace(0, scene.domain_x, 20)
        y_bins = np.linspace(0.3, 0.55, 15)  # Ballast region
        
        hist, xedges, yedges = np.histogram2d(
            [rock.center_x for rock in scene.rocks],
            [rock.center_y for rock in scene.rocks],
            bins=[x_bins, y_bins]
        )
        
        plt.imshow(hist.T, aspect='auto', origin='lower')
        plt.colorbar(label="Rock count")
        plt.xlabel("Position in X (m)")
        plt.ylabel("Depth in Y (m)")
        plt.axhline(scene.fouling_top_y, color='red', linestyle='--', 
                   label='Fouling coverage')
        plt.savefig(output_path)
```

### Benefits:
✅ Understand rock distribution quality
✅ Verify packing algorithm worked correctly
✅ See fouling effect on visible rocks
✅ Detect artifacts or clustering

---

## 4. High-Quality Figure Export

### From PINN4GPR: `model_predictions.py`

```python
def save_image_and_colorbar(path, img, vmin=None, vmax=None, 
                           extent=None, xlabel="Distance (m)"):
    fig = plt.figure(num=1, clear=True)
    plt.imshow(img, vmin=vmin, vmax=vmax, extent=extent)
    plt.colorbar(pad=0.01)
    plt.tight_layout(pad=0, h_pad=0, w_pad=0)
    plt.savefig(path, bbox_inches="tight", pad_inches=0)
```

### Application to Synth-GPR:

Generate **publication-quality figures**:

```python
class PublicationFigureGenerator:
    """Generate publication-ready visualizations of scenes"""
    
    @staticmethod
    def save_scene_cross_section(scene: SceneCheckpoint, 
                                output_path: str,
                                figsize=(12, 8)):
        """
        Generate high-quality cross-section visualization.
        
        Shows:
        • All layers with correct Y-coordinates
        • Rock positions as circles
        • Fouling region as shaded area
        • Material color coding (ER-based)
        • Scale bar and annotations
        • Professional fonts and sizing
        
        Suitable for:
        • Journal articles
        • Thesis/dissertation
        • Presentation slides
        • Technical reports
        """
        fig, ax = plt.subplots(figsize=figsize, dpi=300)
        
        # Layer backgrounds
        ax.axhspan(0.00, 0.20, alpha=0.3, color='brown', label='Subgrade')
        ax.axhspan(0.20, 0.30, alpha=0.3, color='gray', label='Formation')
        ax.axhspan(0.30, scene.fouling_top_y, alpha=0.3, color='tan', 
                  label='Ballast')
        ax.axhspan(scene.fouling_top_y, 0.55, alpha=0.5, color='darkred', 
                  label='Fouling')
        
        # Rocks
        for rock in scene.rocks:
            if rock.center_y > scene.fouling_top_y:
                color = 'orange'  # Visible
                zorder = 3
            else:
                color = 'red'  # Hidden
                zorder = 2
            circle = plt.Circle((rock.center_x, rock.center_y), rock.radius,
                              color=color, alpha=0.7, zorder=zorder)
            ax.add_patch(circle)
        
        # Antenna
        ax.plot(1.124, 1.05, 'g^', markersize=12, label='TX')
        ax.plot(1.174, 1.05, 'b^', markersize=12, label='RX')
        
        # Formatting
        ax.set_xlim(0, 2.248)
        ax.set_ylim(0, 1.15)
        ax.set_xlabel('Position X (m)', fontsize=12)
        ax.set_ylabel('Depth Y (m)', fontsize=12)
        ax.set_title(f'Scene Configuration ({scene.pvc:.0f}% PVC)', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        fig.tight_layout()
        fig.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close()
        
        return output_path
    
    @staticmethod
    def save_side_by_side_comparison(scene1: SceneCheckpoint, 
                                     scene2: SceneCheckpoint,
                                     output_path: str):
        """
        Compare two scenes (e.g., 0% vs 50% fouling) side-by-side.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
        
        for ax, scene in zip([ax1, ax2], [scene1, scene2]):
            # ... render scene on ax ...
            pass
        
        fig.tight_layout()
        fig.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
```

### Benefits:
✅ Publication-quality output for papers
✅ Professional appearance in presentations
✅ High DPI for printing
✅ Correct scaling and proportions

---

## 5. Summary Report Generation

### Combining All Visualization Elements:

```python
class SceneVisualizationReport:
    """Generate comprehensive visual report of a scene configuration"""
    
    def generate_html_report(self, scene: SceneCheckpoint, 
                           output_dir: str = "reports"):
        """
        Create HTML report with all visualizations:
        
        1. Scene Overview
           • High-quality cross-section
           • Layer stack diagram
           • Antenna configuration
        
        2. Detailed Analysis
           • Rock size distribution histogram
           • Rock position heatmap
           • Fouling coverage breakdown
        
        3. Configuration Comparison
           • Side-by-side with nearby PVC levels
           • Differences highlighted
        
        4. Metadata Table
           • All parameters listed
           • Physical interpretations
           • Expected signal characteristics
        
        5. Animation
           • Scene construction (painter's algorithm)
           • Interactive viewer
        
        Output: Single HTML file that can be:
        • Opened in any browser
        • Shared via email
        • Published on website
        • Included in documentation
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scene Configuration Report: {scene.id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .section {{ margin: 30px 0; border: 1px solid #ddd; padding: 20px; }}
                img {{ max-width: 100%; height: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Scene Configuration Report</h1>
            
            <div class="section">
                <h2>Overview</h2>
                <img src="scene_cross_section.png" alt="Scene cross-section">
            </div>
            
            <div class="section">
                <h2>Configuration Parameters</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th><th>Interpretation</th></tr>
                    <tr><td>PVC</td><td>{scene.pvc:.1f}%</td>
                        <td>Void contamination level</td></tr>
                    <!-- More rows... -->
                </table>
            </div>
            
            <div class="section">
                <h2>Rock Distribution Analysis</h2>
                <img src="rock_size_histogram.png" alt="Rock size distribution">
                <img src="rock_position_heatmap.png" alt="Rock position density">
            </div>
            
            <div class="section">
                <h2>Scene Construction Animation</h2>
                <video width="400" controls>
                    <source src="scene_animation.mp4" type="video/mp4">
                </video>
            </div>
        </body>
        </html>
        """
        
        report_path = Path(output_dir) / f"scene_{scene.id}_report.html"
        report_path.write_text(html)
        return report_path
```

---

## 6. Integration with Annotated Files

The visualizations should be generated alongside annotated .in files:

```python
class AnnotatedFileWithVisualization:
    """Generate annotated .in file + comprehensive visualizations"""
    
    def generate_complete_package(self, scene: SceneCheckpoint, 
                                 output_dir: str):
        """
        Generate all deliverables:
        
        1. Annotated .in file
           └─ s_00000.in (with all explanations)
        
        2. Visualization package
           ├─ scene_cross_section.png (publication quality)
           ├─ rock_size_histogram.png
           ├─ rock_position_heatmap.png
           ├─ scene_animation.mp4 (painter's algorithm)
           └─ comparison_5_panels.png (PVC variations)
        
        3. Interactive report
           └─ scene_report.html (opens in browser)
        
        This allows users to:
        • Verify geometry before simulation (visual confirmation)
        • Understand configuration intuitively (visualizations)
        • Read detailed explanations (annotations)
        • Share results (HTML report)
        """
        output_path = Path(output_dir)
        
        # 1. Write annotated .in file
        AnnotatedGPRMaxFileWriter.write_to_file(
            scene, str(output_path / "s_00000.in"),
            include_annotations=True
        )
        
        # 2. Generate visualizations
        visualizer = PublicationFigureGenerator()
        visualizer.save_scene_cross_section(scene, 
            str(output_path / "scene_cross_section.png"))
        
        # 3. Generate HTML report combining everything
        report_generator = SceneVisualizationReport()
        report_generator.generate_html_report(scene, str(output_path))
        
        # 4. Generate comparison figures
        self.generate_pvc_comparison(scene, str(output_path))
        
        return output_path
```

---

## Integration Summary

| PINN4GPR Feature | Synth-GPR Application | Benefit |
|------------------|----------------------|---------|
| Field animation | Scene construction animation | Understand layer ordering |
| Multi-panel comparison | PVC level comparison | Visual impact of fouling |
| Distribution histograms | Rock size/position analysis | Verify packing quality |
| High-quality export | Publication-ready figures | Professional output |
| Tight layout control | Precise figure formatting | Consistent appearance |

---

## Implementation Priority

1. **High Impact, Low Effort:**
   - High-quality cross-section figure ✅ 
   - Rock distribution histograms ✅
   - Side-by-side PVC comparison ✅

2. **Medium Effort:**
   - HTML report generation ✅
   - Rock position heatmap ✅
   - Publication quality export ✅

3. **Higher Effort (Future):**
   - Scene construction animation 🎬
   - Interactive 3D viewer 🎯
   - Real-time parameter exploration 🎮

---

This approach transforms the annotated files from text-based explanations into a **comprehensive visual understanding system** that makes the generated scenes immediately interpretable! 🎨

