"""
Shared headless gprMax runner.

Single home for the gprMax conda-env interpreter path and the subprocess
invocation conventions that were previously duplicated per script:

- The deck is passed by BARE NAME with cwd = deck directory. This sidesteps
  gprMax's ':'-splitting of Windows drive-letter paths AND the double-relative
  bug (relative deck path + cwd=deck dir resolves the path twice). Any
  companion files (#excitation_file, #geometry_objects_read .h5/.txt) must sit
  next to the deck, by the same rule.
- Failures print the tail of gprMax's output instead of being swallowed.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# gprMax lives in its own conda env (see memory/gprmax_run_procedure);
# machine-specific — ajmpc.
GPRMAX_PYTHON = r"C:\Users\barba\.conda\envs\gprMax\python.exe"


def run_gprmax(in_path: Path, timeout: int = 600, gpu: bool = False,
               geometry_only: bool = False) -> bool:
    """Run one gprMax deck headless; True iff it succeeded and wrote the .out
    (.vti for geometry_only)."""
    in_path = Path(in_path)
    cmd = [GPRMAX_PYTHON, "-m", "gprMax", in_path.name]
    if gpu:
        cmd += ["-gpu", "0"]
    if geometry_only:
        cmd += ["--geometry-only"]
    r = subprocess.run(cmd, capture_output=True, timeout=timeout,
                       cwd=str(in_path.parent))
    expected = in_path.with_suffix(".vti" if geometry_only else ".out")
    ok = r.returncode == 0 and expected.exists()
    if not ok:
        tail = (r.stderr or r.stdout or b"").decode("utf-8", "replace")[-800:]
        print(f"  [gprMax rc={r.returncode}] {tail}")
    return ok
