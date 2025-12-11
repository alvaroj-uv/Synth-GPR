class MatplotlibDrawer(GeometryVisitor):
    """
    Concrete Visitor that draws geometry objects using Matplotlib.
    """
    def __init__(self, ax: Any, cmap: Any, min_eps: float, max_eps: float, visualizer: 'GprMaxBlueprintVisualizer'):
        self.ax = ax
        self.cmap = cmap
        self.min_eps = min_eps
        self.max_eps = max_eps
        self.visualizer = visualizer

    def visit_box(self, box: Box) -> Any:
        color, alpha = self.visualizer._get_mat_color_alpha(
            box.material, self.min_eps, self.max_eps, self.cmap
        )
        z_order = 1 + box.order
        
        width = box.p2.x - box.p1.x
        height = box.p2.y - box.p1.y
        rect = mpatches.Rectangle(
            (box.p1.x, box.p1.y), width, height,
            linewidth=0.3, edgecolor='#404040', facecolor=color, alpha=alpha, zorder=z_order
        )
        self.ax.add_patch(rect)

    def visit_cylinder(self, cylinder: Cylinder) -> Any:
        color, alpha = self.visualizer._get_mat_color_alpha(
            cylinder.material, self.min_eps, self.max_eps, self.cmap
        )
        z_order = 1 + cylinder.order
        
        # Smart Projection: Check alignment
        dx = abs(cylinder.p1.x - cylinder.p2.x)
        dy = abs(cylinder.p1.y - cylinder.p2.y)
        is_vertical_z = (dx < 1e-6 and dy < 1e-6)

        if is_vertical_z:
            # Vertical (Z-aligned) -> Draw Circle
            circle = mpatches.Circle(
                (cylinder.p1.x, cylinder.p1.y), cylinder.radius,
                linewidth=0.3, edgecolor='#404040', facecolor=color, alpha=alpha, zorder=z_order
            )
            self.ax.add_patch(circle)
        else:
            # Horizontal/Diagonal -> Draw Projected Rectangle
            angle_rad = np.arctan2(cylinder.p2.y - cylinder.p1.y, cylinder.p2.x - cylinder.p1.x)
            length = np.sqrt(dx**2 + dy**2)
            angle_deg = np.degrees(angle_rad)
            
            # Calculate anchor point (bottom-left corner of rotated rect)
            # Shift from center line by radius perpendicular to axis
            anchor_x = cylinder.p1.x - cylinder.radius * np.sin(angle_rad)
            anchor_y = cylinder.p1.y + cylinder.radius * np.cos(angle_rad)

            rect = mpatches.Rectangle(
                (anchor_x, anchor_y), length, 2*cylinder.radius, angle=angle_deg,
                linewidth=0.3, edgecolor='#404040', facecolor=color, alpha=alpha, zorder=z_order
            )
            self.ax.add_patch(rect)
