# 2026-06-27 — Mbubia comparison + 3D GSSI void-eps sweep (main run)

Validation against Mbubia 2024 setup, then main 3D GSSI 400 MHz void-eps sweep.

**Experiments:**
- `mbubia_1p4ghz_{rip,clean}` — 1.4 GHz Mbubia geometry (RIP + clean)
- `mbubia_420mhz_{rip,pymunk}` — 420 MHz variants (RIP source + pymunk packing)
- `validated_420mhz_{clean,fouled}` — 2D validated baseline at 420 MHz
- `validated_3d_{rocks,wide,freespace_ref,no_rocks}` — 3D geometry validation
- `gssi_400_3d_clean` — 3D GSSI 400 MHz, homogeneous ballast (eps=5.1)
- `gssi_400_3d_rocks_veps{1.0,2.0,4.5,5.5,6.5,7.5,8.5,9.5}` — void-eps sweep (8 points)

**Plots:** `gssi_400_3d_clean_ey.png`, `gssi_400_3d_clean_vs_rocks.png`, `gssi_400_3d_threeway.png`

**Key result:** Coda RMS increases monotonically with void_eps. FI axis maps to eps_void via CRIM.
Virtual sieve showed gap in LF/MF range → triggered gap-fill experiment (2026-06-28).
