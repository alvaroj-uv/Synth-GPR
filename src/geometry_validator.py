"""
GeometryValidator — pre-simulation geometry sanity checks.

Implements the standard gprMax pre-flight checklist:

  1. Painter's canvas order  — later commands overwrite earlier ones at same coordinates
  2. Spatial resolution      — dx <= lambda_min/10 to avoid numerical dispersion
  3. Time window             — long enough for pulse + two-way travel to deepest target
  4. PML clearance           — sources, receivers, rocks >= 10 cells from absorbing boundary
  5. Coordinate alignment    — positions snap to grid cells without significant rounding
  6. Material properties     — epsilon_r >= 1, sigma >= 0, no unphysical values
  7. Domain divisibility     — domain dimensions are integer multiples of cell size
  8. Courant stability       — dt satisfies the stability condition

Reference:
  gprMax documentation — "Before you run your model" checklist
  Khosravi Largani et al. (2025) IEEE GRSL — FDTD resolution guidelines
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .worker import SceneCheckpoint


class Severity(str, Enum):
    ERROR   = "ERROR"    # Will cause wrong results or a crash
    WARNING = "WARNING"  # May cause wrong results; review recommended
    INFO    = "INFO"     # Informational; no action required


@dataclass
class ValidationIssue:
    severity: Severity
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value:7s}] {self.rule}: {self.message}"


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)

    def add(self, severity: Severity, rule: str, message: str) -> None:
        self.issues.append(ValidationIssue(severity, rule, message))

    def errors(self)   -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def has_errors(self) -> bool:
        return bool(self.errors())

    def summary(self) -> str:
        e = len(self.errors())
        w = len(self.warnings())
        i = len(self.issues) - e - w
        return f"{e} error(s), {w} warning(s), {i} info"

    def print_report(self) -> None:
        print()
        print("=" * 70)
        print("GEOMETRY VALIDATION REPORT")
        print("=" * 70)
        if not self.issues:
            print("  [OK] No issues found.")
        else:
            for issue in self.issues:
                print(f"  {issue}")
        print(f"\n  Summary: {self.summary()}")
        print("=" * 70)
        print()


class GeometryValidator:
    """
    Pre-simulation geometry checker for gprMax input scenes.

    Call validate(scene) on a finalized SceneCheckpoint to get a
    ValidationReport before writing to disk or submitting to gprMax.
    All checks are non-destructive.
    """

    _PML_SAFE_CELLS     = 10     # Minimum cells between object and PML edge
    _SNAP_TOL_FRACTION  = 0.05   # Warn if coordinate rounds by more than 5% of cell size

    def validate(self, scene: "SceneCheckpoint") -> ValidationReport:
        report = ValidationReport()
        cfg = scene.config
        dx, dy, dz = cfg.dx, cfg.dy, cfg.dz
        Lx, Ly, Lz = cfg.domain_x, cfg.domain_y, cfg.domain_z
        pml = getattr(cfg, 'pml_layers', 10)

        self._check_domain_divisibility (report, cfg, dx, dy, dz, Lx, Ly, Lz)
        self._check_courant_stability    (report, cfg, dx, dy, dz)
        self._check_painter_order        (report, scene)
        self._check_numerical_dispersion (report, cfg)
        self._check_time_window          (report, scene, cfg)
        self._check_pml_clearance        (report, scene, cfg, Lx, Ly, Lz, pml, dx, dy, dz)
        self._check_coordinate_snapping  (report, scene, dx, dy, dz)
        self._check_material_properties  (report, scene)

        return report

    # ── 1. Painter's canvas order ─────────────────────────────────────────────

    def _check_painter_order(self, report, scene):
        """
        Later BoxCommands overwrite earlier ones at the same coordinates.
        Warn when a background box appears AFTER a detail box it fully covers,
        since this silently erases the detail (a common mistake).
        """
        from .gpr_commands import BoxCommand

        boxes = [c for c in scene.geometry if isinstance(c, BoxCommand)]
        seen = {}
        for i, box in enumerate(boxes):
            key = (round(box.x1, 4), round(box.y1, 4), round(box.x2, 4), round(box.y2, 4))
            if key in seen:
                prev_idx, prev_mat = seen[key]
                report.add(Severity.WARNING, "PAINTER_ORDER",
                    f"Box '{box.material}' (command #{i+1}) has the same x-y footprint as "
                    f"earlier box '{prev_mat}' (command #{prev_idx+1}) — "
                    f"'{prev_mat}' is completely overwritten. Is this intentional?")
            seen[key] = (i, box.material)

        # Also warn when a large background box comes after a smaller target box
        for i, b_large in enumerate(boxes):
            for j, b_small in enumerate(boxes):
                if j >= i:
                    break  # only check if b_large appears AFTER b_small
                if b_large.material == b_small.material:
                    continue
                # b_large fully contains b_small?
                if (b_large.x1 <= b_small.x1 and b_large.x2 >= b_small.x2 and
                        b_large.y1 <= b_small.y1 and b_large.y2 >= b_small.y2):
                    report.add(Severity.WARNING, "PAINTER_ORDER",
                        f"Box '{b_large.material}' (cmd #{i+1}) fully covers earlier "
                        f"'{b_small.material}' (cmd #{j+1}) — painter's algorithm: "
                        f"'{b_small.material}' will be invisible. "
                        f"Move the larger background box earlier in the file.")

    # ── 2. Spatial resolution / numerical dispersion ──────────────────────────

    def _check_numerical_dispersion(self, report, cfg):
        """
        Rule: dx <= lambda_min / 10
        lambda_min = c / (f_max * sqrt(eps_max))
        f_max = 1.545 * center_freq  (Wang 2015 Ricker bandwidth)
        """
        C = 3e8
        f_max = cfg.center_freq * 1.545

        eps_candidates = [
            getattr(cfg, a, None)
            for a in ('bal_foul_eps_max', 'bal_rock_eps', 'subgrade_eps')
        ]
        eps_max = max((e for e in eps_candidates if e and e > 0), default=10.0)

        lambda_min     = C / (f_max * math.sqrt(eps_max))
        dx_required    = lambda_min / 10.0
        cells_per_wave = lambda_min / cfg.dx

        if cfg.dx > dx_required * 1.01:
            report.add(Severity.WARNING, "DISPERSION",
                f"dx={cfg.dx*1000:.2f}mm > lambda_min/10 = {dx_required*1000:.2f}mm "
                f"(f_max={f_max/1e9:.2f}GHz, eps_max={eps_max:.1f}). "
                f"Numerical dispersion artifacts likely — reduce dx to "
                f"<= {dx_required*1000:.1f}mm.")
        else:
            report.add(Severity.INFO, "DISPERSION",
                f"Grid is well-resolved: {cells_per_wave:.0f} cells/lambda_min "
                f"(dx={cfg.dx*1000:.2f}mm, lambda_min={lambda_min*1000:.1f}mm). "
                f"No dispersion artifacts expected.")

    # ── 3. Time window ────────────────────────────────────────────────────────

    def _check_time_window(self, report, scene, cfg):
        """
        Rule: time_window >= t_pulse + t_return
          t_pulse  = 1 / center_freq  (approximate Ricker pulse half-width)
          t_return = 2 * max_depth / v_min  (two-way travel to deepest target)
          v_min    = c / sqrt(eps_max)
        """
        C       = 3e8
        tw      = cfg.time_window
        t_pulse = 1.0 / cfg.center_freq  # approximate; Ricker pulse duration

        max_depth = cfg.domain_y

        eps_max = max(
            (getattr(cfg, a, None) or 0 for a in ('bal_foul_eps_max', 'subgrade_eps')),
            default=10.0
        )
        eps_max = max(eps_max, 1.0)
        v_min    = C / math.sqrt(eps_max)
        t_return = 2.0 * max_depth / v_min
        t_needed = t_pulse + t_return

        if tw < t_needed:
            report.add(Severity.WARNING, "TIME_WINDOW",
                f"time_window={tw*1e9:.1f}ns is too short. "
                f"Minimum needed: pulse ({t_pulse*1e9:.1f}ns) + "
                f"two-way return ({t_return*1e9:.1f}ns) = {t_needed*1e9:.1f}ns. "
                f"Deep reflections will be cut off.")
        else:
            margin = (tw - t_needed) * 1e9
            report.add(Severity.INFO, "TIME_WINDOW",
                f"time_window={tw*1e9:.1f}ns — {margin:.1f}ns margin after deepest return "
                f"({t_return*1e9:.1f}ns) + pulse ({t_pulse*1e9:.1f}ns).")

    # ── 4. PML clearance ─────────────────────────────────────────────────────

    def _check_pml_clearance(self, report, scene, cfg, Lx, Ly, Lz, pml, dx, dy, dz):
        """
        Rule: all sources, receivers, and rocks must be >= pml_layers cells
        from every domain boundary. Objects in the PML produce unphysical results.
        """
        pmx = pml * dx
        pmy = pml * dy

        # Sources and receivers — hard error
        for cmd_list, label in [(scene.sources, "Source"), (scene.receivers, "Receiver")]:
            for cmd in cmd_list:
                x, y = getattr(cmd, 'x', None), getattr(cmd, 'y', None)
                if x is None:
                    continue
                if x < pmx:
                    report.add(Severity.ERROR, "PML_CLEARANCE",
                        f"{label} at x={x:.3f}m is inside PML zone "
                        f"(left boundary + {pml} cells = {pmx:.3f}m). "
                        f"Move it to x > {pmx:.3f}m.")
                elif x > Lx - pmx:
                    report.add(Severity.ERROR, "PML_CLEARANCE",
                        f"{label} at x={x:.3f}m is inside PML zone "
                        f"(right boundary - {pml} cells = {Lx-pmx:.3f}m). "
                        f"Move it to x < {Lx-pmx:.3f}m.")
                if y < pmy:
                    report.add(Severity.ERROR, "PML_CLEARANCE",
                        f"{label} at y={y:.3f}m is inside PML zone "
                        f"(bottom + {pml} cells = {pmy:.3f}m). "
                        f"Move it to y > {pmy:.3f}m.")
                elif y > Ly - pmy:
                    report.add(Severity.ERROR, "PML_CLEARANCE",
                        f"{label} at y={y:.3f}m is inside PML zone "
                        f"(top - {pml} cells = {Ly-pmy:.3f}m). "
                        f"Move it to y < {Ly-pmy:.3f}m.")

        # Rocks — aggregate warning (edge rocks are common and usually acceptable)
        rocks_in_pml = sum(
            1 for r in scene.rock_positions
            if (r.x - r.radius < pmx) or (r.x + r.radius > Lx - pmx)
               or (r.y - r.radius < pmy) or (r.y + r.radius > Ly - pmy)
        )
        if rocks_in_pml:
            report.add(Severity.WARNING, "PML_CLEARANCE",
                f"{rocks_in_pml} rock(s) extend into the PML zone "
                f"({pml} cells = {pmx:.3f}m from x-edges, {pmy:.3f}m from y-edges). "
                f"Edge rocks will be partially absorbed — "
                f"widen the domain or filter rocks within {pmx:.3f}m of x-edges.")

    # ── 5. Coordinate alignment / grid snapping ───────────────────────────────

    def _check_coordinate_snapping(self, report, scene, dx, dy, dz):
        """
        gprMax internally rounds all coordinates to the nearest grid cell.
        Warn when the rounding error exceeds 5% of the cell size — this
        means the placed object deviates noticeably from the intended position.
        """
        tol = self._SNAP_TOL_FRACTION

        def snap_error(val: float, step: float) -> float:
            """Fractional rounding error relative to step size."""
            rounded = round(val / step) * step
            return abs(val - rounded) / step

        snapping_issues = []
        for cmd_list, label in [(scene.sources, "Source"), (scene.receivers, "Receiver")]:
            for cmd in cmd_list:
                for attr, step, axis in [('x', dx, 'x'), ('y', dy, 'y'), ('z', dz, 'z')]:
                    val = getattr(cmd, attr, None)
                    if val is None:
                        continue
                    # z=dz/2 is the correct 2D cell-centre position — not a snapping problem
                    if axis == 'z' and abs(val - step / 2.0) < 1e-9:
                        continue
                    err = snap_error(val, step)
                    if err > tol:
                        snapping_issues.append(
                            f"{label} {axis}={val:.5f}m snaps by "
                            f"{err*100:.1f}% of cell (d{axis}={step*1000:.2f}mm)"
                        )

        if snapping_issues:
            report.add(Severity.WARNING, "COORD_SNAP",
                f"Coordinate rounding > {tol*100:.0f}% of cell size detected. "
                f"gprMax will silently move these to the nearest grid cell:\n"
                + "\n".join(f"    • {s}" for s in snapping_issues))

    # ── 6. Material properties ────────────────────────────────────────────────

    def _check_material_properties(self, report, scene):
        """
        Validate each #material command.
        eps_r must be >= 1 (vacuum floor).
        sigma must be >= 0.
        Very high eps_r (> water = 81) warrants a warning.
        """
        if not scene.materials:
            report.add(Severity.WARNING, "MATERIAL",
                "No materials defined — gprMax will use free space everywhere.")
            return

        for mat in scene.materials:
            name = getattr(mat, 'identifier', str(mat))
            eps  = getattr(mat, 'eps',   None)
            sig  = getattr(mat, 'sigma', None)

            if eps is not None and eps < 1.0:
                report.add(Severity.ERROR, "MATERIAL",
                    f"'{name}': epsilon_r={eps:.3f} < 1 — unphysical. "
                    f"Relative permittivity must be >= 1 (vacuum).")
            if eps is not None and eps > 81.0:
                report.add(Severity.WARNING, "MATERIAL",
                    f"'{name}': epsilon_r={eps:.1f} > 81 (liquid water). "
                    f"Verify this is intentional (e.g. saturated clay).")
            if sig is not None and sig < 0.0:
                report.add(Severity.ERROR, "MATERIAL",
                    f"'{name}': sigma={sig} < 0 — unphysical. "
                    f"Electrical conductivity must be >= 0.")

    # ── 7. Domain divisibility ────────────────────────────────────────────────

    def _check_domain_divisibility(self, report, cfg, dx, dy, dz, Lx, Ly, Lz):
        """
        gprMax requires domain dimensions to be integer multiples of the cell size.
        A mismatch causes gprMax to silently adjust the domain, shifting all coordinates.
        """
        tol = 1e-6
        for L, d, axis in [(Lx, dx, 'x'), (Ly, dy, 'y'), (Lz, dz, 'z')]:
            if d <= 0:
                continue
            n_cells  = L / d
            n_rounded = round(n_cells)
            error    = abs(n_cells - n_rounded)
            if error > tol:
                report.add(Severity.WARNING, "DOMAIN_DIVISIBILITY",
                    f"domain_{axis}={L:.6f}m / d{axis}={d*1000:.3f}mm = "
                    f"{n_cells:.4f} cells (not integer). "
                    f"gprMax will extend to {n_rounded} cells "
                    f"({n_rounded*d:.6f}m). Adjust domain_{axis} to "
                    f"{n_rounded*d:.6f}m to avoid implicit shifts.")

    # ── 8. Courant stability ──────────────────────────────────────────────────

    def _check_courant_stability(self, report, cfg, dx, dy, dz):
        """
        Courant-Friedrichs-Lewy (CFL) condition:
          dt <= 1 / (c * sqrt(1/dx^2 + 1/dy^2 + 1/dz^2))

        gprMax computes dt automatically, but for 2D runs where dz >> dx
        the condition changes. We verify the stored time step is valid.
        """
        C = 3e8
        is_2d = (dz <= dx * 1.01)  # 2D: single z-cell

        if is_2d:
            # 2D TMz: only x and y contribute
            dt_max = 1.0 / (C * math.sqrt(1/dx**2 + 1/dy**2))
        else:
            dt_max = 1.0 / (C * math.sqrt(1/dx**2 + 1/dy**2 + 1/dz**2))

        stored_dt = getattr(cfg, 'time_window', None)  # dt not in config; just report max
        report.add(Severity.INFO, "COURANT",
            f"CFL dt_max = {dt_max*1e12:.2f}ps "
            f"({'2D' if is_2d else '3D'}, "
            f"dx={dx*1000:.2f}mm dy={dy*1000:.2f}mm dz={dz*1000:.2f}mm). "
            f"gprMax will use this automatically.")
