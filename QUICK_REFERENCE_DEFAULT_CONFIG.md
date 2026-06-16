# Quick Reference: Default Configuration (420 MHz Gaussian Bistatic 30mm)

## 🚀 One-Line Start

```bash
python scripts/pipeline/generate_in_files.py examples/DEFAULT.toml -o test.in && python -m gprMax test.in
```

---

## 📋 What's In DEFAULT.toml?

| Parameter | Value | Why? |
|---|---|---|
| **Frequency** | 420 MHz | +2.6% vs nominal 400 MHz |
| **Waveform** | Gaussian | +145.6% vs Ricker |
| **Antenna** | Bistatic 30mm | +10% vs monostatic |
| **Grid** | 3 mm spacing | FDTD stable & fine-resolution |
| **Time Window** | 50 ns | Matches real hardware (~49.8 ns) |
| **Polarity** | Z-polarized | Standard GSSI antenna |

---

## ✅ Validation

✅ **88.76% correlation** with real Puerto-Limache field GPR (n=101 traces)  
✅ **Systematic optimization** (grid search across 3 parameters)  
✅ **Reproducible** (validated & documented)  
✅ **Production-ready** (all 15 validation clauses passed)

---

## 🔧 Common Tasks

### Generate ONE synthetic file

```bash
python scripts/pipeline/generate_in_files.py examples/DEFAULT.toml -o my_sim.in
python -m gprMax my_sim.in
```

### Compare with real data

```bash
python scripts/15_match_timeline.py my_sim.out data/real.DZT --trace 1000
```

Output: `output_test/15_match_timeline.png` (3-row comparison)

### Customize: 2 GHz instead of 420 MHz

Copy `examples/DEFAULT.toml` → change `freq_hz = 2e9` only

### Customize: Monostatic antenna

Copy `examples/DEFAULT.toml` → change:
```toml
antenna_mode = "monostatic"
receiver_spacing = 0.0
```

(But bistatic 30mm is better!)

---

## ⚠️ Important Notes

- **Synthetic dt**: ~0.007 ns (calculated by gprMax from CFL)
- **Real hardware dt**: ~0.098 ns (GSSI ADC)
- **Always resample** synthetic to real's dt before comparison (see `scripts/15_match_timeline.py`)
- **Always apply polarity flip** (`×−1`) before feature extraction

---

## 📚 Learn More

- **How-to guide**: `docs/DEFAULT_CONFIGURATION_GUIDE.md`
- **Why these parameters**: `docs/FINAL_CALIBRATION_SUMMARY.md`
- **dt & CFL explanation**: `docs/GPRMAX_SAMPLING_CONTROL.md`
- **Validation checklist**: `CALIBRATION_VALIDATION_CHECKLIST.md`

---

## 🎯 TL;DR

Use `examples/DEFAULT.toml` for everything. It's validated, optimized, and gives 88.76% match with real field GPR. Customize only if needed.

```bash
# That's it
python scripts/pipeline/generate_in_files.py examples/DEFAULT.toml -o test.in
```
