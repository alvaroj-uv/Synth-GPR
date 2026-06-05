# Layer Management — Executive Summary

## 🚨 Critical Finding

The codebase has **two conflicting layer coordinate systems** in use simultaneously:

| Aspect | Old System (layer_config.py) | New System (domain/coordinates.py) |
|--------|------------------------------|--------------------------------------|
| **Type** | Static class with hardcoded coordinates | Dynamic dataclass from config |
| **Coordinates** | Fixed (0.2, 0.3, 0.55) | Configurable (from LayerStack) |
| **Maintainability** | Must manually sync with config | Auto-computed from config |
| **Status** | ❌ Legacy, being phased out | ✓ Current standard |
| **Used By** | granular_worker.py, lab_worker.py (fallback) | Core production pipeline |

---

## 🎯 The Problem

### Two Systems in Use
```
ProductionLine
├─ Creates LayerStack (NEW SYSTEM)
├─ Creates CoordinateSystem (NEW SYSTEM)
└─ Calls Workers
    ├─ Most workers: Use CoordinateSystem.bounds(Layer.X)
    └─ GranularMatrixWorker, LabWorker: 
        Try NEW system, fall back to OLD system if missing
```

### Risks
1. **Coordinate Drift** — If both systems configured differently, geometry inconsistent
2. **Silent Failures** — Fallback code masks issues; uses old system without error
3. **Maintenance Burden** — Two systems to keep in sync

### Example: What Happens if Configs Diverge

**Config says:** ballast_thickness = 0.35 m  
**layer_config.py says:** BALLAST.y_top = 0.55 m (implying 0.25 m thickness)

**Result:**
- GranularMatrixWorker tries NEW system first → ballast 0.30–0.65 m
- If coordinate_system missing → falls back to OLD → ballast 0.30–0.55 m
- Rocks packed in wrong volume!

---

## 📋 Current State (Before Refactoring)

### File Breakdown

**Old System:**
```
src/layer_config.py
├─ LayerDefinition class (value object)
└─ LayerStack class (STATIC)
    ├─ SUBGRADE = LayerDefinition(y_bottom=0.0, y_top=0.2)
    ├─ FORMATION = LayerDefinition(y_bottom=0.2, y_top=0.3)
    ├─ BALLAST = LayerDefinition(y_bottom=0.3, y_top=0.55)
    └─ validate() method
```

**New System:**
```
src/domain/coordinates.py
├─ LayerStack dataclass (DYNAMIC from thicknesses)
│   ├─ subgrade_thickness: 0.20
│   ├─ formation_thickness: 0.10
│   ├─ ballast_thickness: 0.25
│   ├─ antenna_clearance: 0.5
│   └─ air_buffer: 0.1
├─ CoordinateSystem class (RESOLVER)
│   └─ bounds(layer: Layer) → LayerBounds
├─ Layer enum (type-safe)
├─ Anchor enum (semantic coordinates)
└─ LayerBounds dataclass
```

### Usage Pattern

**In granular_worker.py (lines 42-50):**
```python
if scene.coordinate_system:
    bounds_obj = scene.coordinate_system.bounds(Layer.BALLAST)  # NEW
else:
    ballast = LayerStack.BALLAST  # OLD (fallback)
    bounds = (ballast.y_bottom, ballast.y_top)
```

**In lab_worker.py (lines 38-48):**
```python
ballast = LayerStack.BALLAST  # OLD
ballast_bottom = scene.metadata.get('ballast_bottom_y', ballast.y_bottom)
ballast_top = ballast_bottom + ballast_thickness
```

---

## ✅ Recommended Solution

### Remove the Old System Completely

**Steps:**
1. Delete `src/layer_config.py`
2. Remove fallback code from `granular_worker.py`
3. Update `lab_worker.py` to use coordinate_system
4. Add validation to CoordinateSystem
5. Run tests to verify

**Time:** ~1 hour

**Benefit:** Single source of truth, no silent failures, simpler maintenance

---

## 📚 Documentation

Two detailed guides created:

### 1. [LAYER_MANAGEMENT_ANALYSIS.md](LAYER_MANAGEMENT_ANALYSIS.md)
**What:** Deep dive into the problem  
**Length:** 400 lines  
**Contents:**
- Side-by-side comparison of both systems
- How they're currently used
- Why the dual system exists
- Risks and failure modes
- Data consistency map
- Validation approaches

**Read when:** Understanding the architecture & design decisions

### 2. [LAYER_MANAGEMENT_REFACTORING.md](LAYER_MANAGEMENT_REFACTORING.md)
**What:** Step-by-step instructions to fix it  
**Length:** 300 lines  
**Contents:**
- Exact code changes (before/after)
- Line numbers for each file
- Verification checklist
- Git commands
- Rollback plan
- Time estimates

**Read when:** Ready to implement the refactoring

---

## 🔄 Refactoring Steps Overview

### Step 1: Clean up granular_worker.py
Remove: `from .layer_config import LayerStack`  
Remove: 5 lines of fallback if/else  
Keep: Use only `scene.coordinate_system.bounds(Layer.BALLAST)`

### Step 2: Clean up lab_worker.py
Remove: `from .layer_config import LayerStack`  
Update: Use `scene.coordinate_system.bounds(Layer.BALLAST)`  
Keep: Support work_order overrides

### Step 3: Add validation
Add method: `CoordinateSystem._validate_layer_stack()`  
Validates: All thicknesses positive, total height reasonable

### Step 4: Delete layer_config.py
```bash
rm src/layer_config.py
```

### Step 5: Test
```bash
pytest tests/ -v
```

---

## 📊 Before vs. After

### BEFORE (Current — Problematic)

```python
# granular_worker.py
if scene.coordinate_system:
    bounds = scene.coordinate_system.bounds(Layer.BALLAST)  # NEW
else:
    ballast = LayerStack.BALLAST  # OLD
    bounds = (ballast.y_bottom, ballast.y_top)

# lab_worker.py
ballast = LayerStack.BALLAST  # OLD
...

# Maintenance
# - 2 files to update when changing layer thickness
# - Easy to forget and cause drift
# - Fallback code masks issues (silent failures)
```

### AFTER (Proposed — Clean)

```python
# granular_worker.py
bounds = scene.coordinate_system.bounds(Layer.BALLAST)  # NEW only

# lab_worker.py
ballast_bounds = scene.coordinate_system.bounds(Layer.BALLAST)  # NEW
ballast_bottom = ballast_bounds.bottom
ballast_top = ballast_bounds.top

# Maintenance
# - 1 source of truth (config → LayerStack → CoordinateSystem)
# - No synchronization needed
# - Validation at init time (fail fast)
```

---

## 🎓 Key Learnings

### Design Pattern: Transitional Refactoring
The codebase shows an **in-progress refactoring** where:
1. ✓ New system created (better design)
2. ✓ Core pipeline switched to new system
3. ⚠️ Legacy system remains as fallback
4. ❌ Fallback code not removed (incomplete)

**Best practice:** Complete the transition by removing legacy code entirely.

### Anti-Pattern: Dual Systems
Having two ways to do the same thing:
- ❌ Creates decision burden (which to use?)
- ❌ Enables silent failures (fallback hides issues)
- ❌ Increases maintenance (sync two systems)
- ❌ Confuses new developers

**Best practice:** One system, one way to do it.

### Fallback Pattern Risk
```python
if new_system:
    use_new_system()
else:
    use_old_system()  # ← Silent fallback is dangerous
```

**Risk:** If new_system is accidentally None/empty, old_system silently activates. Bug is subtle and hard to find.

**Better:** Remove the else branch entirely. Let it fail loudly if new_system is missing.

---

## 🚀 Next Steps

### Immediate (Before Using Layers)
1. Read [LAYER_MANAGEMENT_ANALYSIS.md](LAYER_MANAGEMENT_ANALYSIS.md) to understand the issue
2. Read [LAYER_MANAGEMENT_REFACTORING.md](LAYER_MANAGEMENT_REFACTORING.md) for how to fix it

### Short Term (This Sprint)
1. Execute refactoring steps 1-5 (~1 hour)
2. Run full test suite
3. Verify no coordinate drift between old and new systems

### Medium Term (Next Sprint)
1. Centralize layer configuration in `config.py` (optional but recommended)
2. Add comprehensive layer validation tests
3. Document layer system in README

---

## 📖 Related Documentation

- [SCENE_CREATION_ARCHITECTURE.md](SCENE_CREATION_ARCHITECTURE.md) — How layers fit into full architecture
- [SCENE_CREATION_SEQUENCES.md](SCENE_CREATION_SEQUENCES.md) — Diagram showing coordinate resolution
- [Quick Reference](SCENE_CREATION_QUICK_REFERENCE.md) — Layer stack values table

---

## ❓ FAQs

**Q: Is this a bug?**  
A: Not yet, but it's a **latent risk**. Both systems currently compute similar values, so it works. But if they diverge, you'll get silent coordinate inconsistencies.

**Q: Why wasn't this completed during the refactoring?**  
A: Likely incomplete migration. Core pipeline was updated, but fallback code in older workers wasn't removed.

**Q: Is it safe to remove layer_config.py now?**  
A: Yes, if we ensure ProductionLine **always** initializes CoordinateSystem (which it does).

**Q: What if I need the old system as fallback?**  
A: Better approach: Make CoordinateSystem optional in workers (raise clear error if missing), rather than silently using old system.

**Q: How much will this slow down generation?**  
A: No impact. CoordinateSystem pre-computes Y levels at init, so lookups are O(1).

---

## ✨ Summary

| Aspect | Current | After Refactoring |
|--------|---------|-------------------|
| **Systems** | 2 (old + new) | 1 (new) |
| **Source of Truth** | Split | Single (config) |
| **Fallback Code** | Yes (risky) | No (fail fast) |
| **Maintenance** | Sync 2 files | Sync 1 file |
| **Error Detection** | Silent | Loud & clear |

**Recommendation:** Spend 1 hour now to clean this up, avoid hours of debugging coordinate issues later.

