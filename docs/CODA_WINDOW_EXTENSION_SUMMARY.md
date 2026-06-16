# Coda Window Extension: 10ns → 50ns

## Problem
Synthetic simulations for ballast and rocks materials were configured with only **10 ns time window**, but real field GPR data has **49.8 ns window**. This caused **80% data loss** when comparing synthetic coda structure to real field responses.

### Evidence
| Configuration | Samples | dt (ns) | Window (ns) | Status |
|---|---|---|---|---|
| Real GPR (DZT) | 510 | 0.0978 | 49.8 | ✓ Reference |
| Freespace 420MHz | 7068 | 0.00708 | 50.01 | ✓ Correct |
| **Ballast (OLD)** | **1415** | **0.00708** | **10.01** | ✗ 80% missing |
| **Rocks (OLD)** | **1415** | **0.00708** | **10.01** | ✗ 80% missing |

## Solution
Extended `time_window` parameter in TOML configurations from `1.0e-8` (10 ns) to `5.0e-8` (50 ns).

### Files Modified
1. **examples/DEFAULT_with_ballast.toml** (line 28)
   - `time_window = 1.0e-8` → `time_window = 5.0e-8`

2. **examples/rocks_420mhz_50cm_antenna.toml** (line 29)
   - `time_window = 1.0e-8` → `time_window = 5.0e-8`

### New Simulations Generated
- **output_test/ballast_50ns.out**: 7068 samples, 50.01 ns window
- **output_test/rocks_50ns.out**: 7068 samples, 50.01 ns window
- Replaced old versions as defaults (ballast_layer.out, rocks_420mhz_50cm.out)

## Results
### Correlation with Real Field GPR (trace #15000)

**Before (10ns incomplete):**
- Only first 10 ns visible, missing all late-time coda
- Incomplete comparison metrics

**After (50ns complete):**
| Material | Correlation | Change |
|---|---|---|
| Ballast | +0.912963 | 🟢 Full coda visible |
| Rocks   | +0.903764 | 🟢 Full coda visible |

Both materials now show **~91% correlation** with complete waveform comparison.

## Impact
- ✓ Full synthetic-real coda comparison now possible
- ✓ Material characterization complete (direct wave + coda)
- ✓ Proper foundation for fouling discrimination models
- ✓ 50ns window aligns with real field data acquisition

## Next Steps
1. Validate across multiple real traces (not just #15000)
2. Test fouled vs clean ballast discrimination with full coda
3. Optimize material epsilon with extended window data
4. Consider multi-layer configurations with proper time resolution

## References
- [Waveform Scaling Result](project_waveform_scaling_result.md)
- [Real GPR Sampling](reference_real_gpr_sampling.md)
- [DZT Format and Cleaning](reference_dzt_format_and_cleaning.md)
