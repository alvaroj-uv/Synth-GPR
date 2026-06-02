# Decision: Keep Triangles or Switch to Spheres for 3D Mini-Test?

**Question:** For 3D FDTD domain (1.5 × 0.4 × 0.4 m), should we:
- A) Keep 2D triangles (circular rocks, no z-extent)
- B) Switch to 3D spheres (actual 3D rocks)
- C) Hybrid: Keep triangles but extend domain in z

---

## 1. WHAT DO TRIANGLES REPRESENT?

### Current 2D Setup
```
#triangle: x1 y1 z1  x2 y2 z2  x3 y3 z3  radius  material
```

- **Defines a 2D triangle in x-y plane**
- **Infinite extent in z-direction** (implicit infinite plate perpendicular to z)
- **Effectively:** An infinite circular cylinder in z (rock extends forever)
- **Radius parameter:** Circumradius of triangle (not rock diameter!)

### In Physical Terms
- A 4 cm diameter rock becomes an **infinite rod** perpendicular to z-axis
- Ballast layer becomes a **2D packing of infinite cylindrical rocks**
- Receiver sees a **2D slice** of infinite geometry

**Problem for 3D:** This is fundamentally 2D, not 3D. Infinite z-extent means:
- No lateral scattering (only downward/upward)
- No 3D diffraction
- Doesn't match real ballast (spheres, finite)

---

## 2. WHAT DO SPHERES REPRESENT?

### 3D Setup
```
#sphere: x y z radius material
```

- **Defines a finite 3D sphere** at position (x, y, z)
- **Finite radius** (e.g., 2–2.5 cm for 4–5 cm diameter rock)
- **Real ballast geometry** (crushed granite rocks are roughly spherical)

### In Physical Terms
- A 4 cm diameter rock becomes an **actual finite sphere**
- Ballast layer becomes a **3D random close packing** of spheres
- Receiver sees a **3D scattering volume** with real depth effects

**Advantage:** Matches real ballast structure

---

## 3. QUANTITATIVE COMPARISON

### 3.1 Scattering Patterns

| Property | Triangles (2D, infinite z) | Spheres (3D, finite) |
|----------|---|---|
| **Wave spreading** | Cylindrical (1/r) | Spherical (1/r²) |
| **Diffraction** | Limited (2D) | Full 3D diffraction |
| **Rock shadow** | Linear stripe | 3D cone |
| **Multiple scattering** | Confined to x-y plane | Full 3D paths |
| **Lateral attenuation** | Weak (infinite rock) | Strong (finite rock) |

**Impact on waveforms:**
- **Triangles:** Coda is organized, repeatable (2D interference patterns)
- **Spheres:** Coda is chaotic, longer (3D scattering, multiple paths)

---

### 3.2 Feature Extraction Quality

| Feature | Triangles | Spheres | Winner |
|---------|-----------|---------|--------|
| **hilbert_standard_deviation** | Clear envelope | Noisy envelope | Triangles (clearer signal) |
| **area_fourier** | Concentrated spectrum | Diffused spectrum | Triangles (sharper) |
| **coda_length** | Short, organized | Long, complex | Spheres (more realistic) |
| **spectral_entropy** | Low (organized) | High (chaotic) | Spheres (real-world match) |
| **Phase coherence** | Good (2D interference) | Poor (3D scattering) | Triangles (clearer phases) |

**Overall:** Triangles make features SHARPER and EASIER TO LEARN (higher 2D accuracy)

---

### 3.3 Domain Size Realism

| Aspect | Triangles | Spheres |
|--------|-----------|---------|
| **Rock extent** | Infinite in z | ~4 cm diameter |
| **Domain z (needed)** | 0.013 m (minimal) | 0.4–0.6 m (real ballast depth) |
| **Vertical scattering** | No (infinite rod) | Yes (finite sphere) |
| **Receiver placement** | Immaterial (infinite layer) | Critical (near/far field effects) |
| **Fouling seepage** | 2D (fills voids in layer) | 3D (percolates through pores) |

**Verdict:** Triangles are fundamentally 2D in a 3D domain (physically inconsistent)

---

## 4. EXPECTED ACCURACY IMPACT

### Scenario 1: Keep Triangles (1.5 × 0.4 × 0.4 domain)
```
Domain z-extent:  0.4 m (but rocks are infinite!)
Physics:          Hybrid 2D-like in 3D box
Receiver depth:   Middle of 0.4 m box (0.2 m)
Distance to layer: 0.2 m above, 0.2 m below infinite rock layer

Expected accuracy:
  - Spherical spreading loss: −3% (real 3D domain effects)
  - But scattering is 2D-ish: ±0% (advantage: clearer signal)
  - Antenna coupling: −8% (same as expected)
  - NET: ~77–80% (less drop than full 3D!)
```

**Result:** Better accuracy than true 3D, but **unphysical**

---

### Scenario 2: Switch to Spheres (1.5 × 0.4 × 0.4 domain)
```
Domain z-extent:  0.4 m (rocks now finite, ~4 cm diameter)
Physics:          True 3D ballast structure
Receiver depth:   0.2 m (middle of rock layer)
Packing density:  ~64% (realistic RCP)

Expected accuracy:
  - Spherical spreading loss: −3%
  - 3D scattering diffusion: −4% (feature blur from complex coda)
  - Antenna coupling: −8%
  - Realistic geometry gain: +2%
  - NET: ~74–77% (full 3D effect, more realistic)
```

**Result:** More accurate to real ballast, but **accuracy drops more**

---

### Scenario 3: Keep Triangles + Thinner z-Domain (1.5 × 0.4 × 0.013 m)
```
Domain z-extent:  0.013 m (same as 2D, squeeze into thin slice)
Physics:          Exactly 2D, but in gprMax 3D engine
Receiver depth:   0.0066 m (at rock layer)
Propagation:      Nearly 1D (flat layers)

Expected accuracy:
  - Spherical spreading loss: Minimal (wave stays in thin layer)
  - Scattering: 2D-like (same as current 2D model)
  - Antenna coupling: −5% (reduced, thin domain)
  - NET: ~83–86% (similar to 2D, validates engine)
```

**Result:** Validates gprMax 3D engine without 3D complexity; **acceleration test**

---

## 5. WHAT ARE YOU REALLY TESTING?

### If You Keep Triangles (Option A: Hybrid)
**Testing:** "Does gprMax 3D engine give same results as 2D engine on 2D geometry?"
- **Goal:** Validate engine consistency
- **Expected outcome:** ~85% accuracy (similar to 2D)
- **Validity:** Low (not testing 3D physics)
- **Publishability:** Low ("we ran 2D in a 3D box")

### If You Switch to Spheres (Option B: True 3D)
**Testing:** "How much does 3D ballast geometry hurt waveform-only classification?"
- **Goal:** Measure sim-to-real domain gap from geometry alone
- **Expected outcome:** ~74% accuracy (10% drop)
- **Validity:** High (tests real 3D physics)
- **Publishability:** High ("here's how geometry affects waveforms")

### If You Keep Triangles + Thin Domain (Option C: Controlled 2D)
**Testing:** "Can we reproduce 2D results exactly in gprMax 3D engine?"
- **Goal:** Validate that platform switch (gprMax 2D→3D) isn't the problem
- **Expected outcome:** ~88% accuracy (same as current)
- **Validity:** Medium (controls for one variable)
- **Publishability:** Low (not novel)

---

## 6. RESEARCH GOAL ALIGNMENT

### Your Original Question
> "What would happen in a 3D model?"

**This asks:** How does 3D reality affect waveform-only predictions?

**To answer it, you MUST use spheres**, because:
- Triangles don't represent 3D reality (infinite extent)
- Spheres do represent 3D reality (finite, random packing)
- The question is inherently about geometry changes
- Keeping triangles means you're NOT testing 3D

---

## 7. RECOMMENDATION MATRIX

**Choose based on your research question:**

| Research Question | Keep Triangles | Switch to Spheres |
|---|---|---|
| "Is gprMax 3D engine reliable?" | ✓ Use triangles | ✗ No |
| "How does 3D geometry hurt accuracy?" | ✗ No | ✓ Use spheres |
| "Can we transfer 2D→3D models?" | ~ Both work | ✓ Spheres better |
| "What's the sim-to-real gap?" | ✗ No (unphysical) | ✓ Use spheres |
| "How much does antenna matter in 3D?" | ~ Triangles OK | ✓ Spheres better |

**Bottom line:** **SWITCH TO SPHERES** (Option B)

---

## 8. PRACTICAL CONSIDERATIONS

### Effort Needed to Switch

**Triangles → Spheres changes:**

1. **Rock generation code:**
   - Current: `_generate_angular_rocks()` → triangles in x-y plane
   - New: `_generate_spheres_3d()` → spheres in x-y-z space
   - Effort: ~2 hours (reuse existing rock packing code, add z-dimension)

2. **Domain sizing:**
   - Current: z = 0.0132 m (thin)
   - New: z = 0.4 m (thick, contains full ballast depth)
   - Effort: Change 1 parameter, negligible

3. **gprMax input format:**
   - Current: `#triangle: x1 y1 z1 x2 y2 z2 x3 y3 z3 radius material`
   - New: `#sphere: x y z radius material`
   - Effort: 10 lines of code change

4. **Feature extraction:**
   - Current: Works as-is (features don't care about geometry)
   - New: Works as-is (same 572 features)
   - Effort: Zero

**Total effort:** ~3 hours (mostly rock generation)

---

### Validation Strategy

**To be safe, do BOTH mini-tests in sequence:**

```
Week 1: Option C (Quick validation)
  - Keep triangles, thin domain z=0.013m
  - Generate 100 samples (1 per class, replicate 100×)
  - Run gprMax: ~30 min (tiny domain)
  - Check: Accuracy ~88% (should match 2D)
  - Cost: $2
  - Goal: "Confirm gprMax 3D engine works"

Week 2: Option B (True 3D test)
  - Switch to spheres, thick domain z=0.4m
  - Generate 1000 samples (200 per class)
  - Run gprMax: 4 hours
  - Check: Accuracy ~74-77% (3D physics effect)
  - Cost: $15
  - Goal: "Measure real domain gap"
```

**Parallel work:** While gprMax runs, develop antenna calibration code (Taguchi)

---

## 9. DECISION SUMMARY

### Keep Triangles?
**No.** Triangles represent infinite cylindrical rocks (2D geometry). Infinite extent in z means:
- No 3D scattering (rocks don't cast shadows)
- No vertical wave spreading (infinite rod carries wave)
- Not realistic for actual ballast (rocks are finite spheres)

### Switch to Spheres?
**Yes.** Spheres represent finite 3D rocks (realistic ballast). Switching gives:
- True 3D scattering patterns
- Realistic vertical propagation and diffraction
- Answers your original question ("What happens in 3D?")
- Publishable results ("3D geometry impact on waveform features")

### Hybrid Approach?
**Option C is good for validation:** First run thin-domain triangles to confirm gprMax engine, then do thick-domain spheres for real 3D testing.

---

## 10. FINAL RECOMMENDATION

### Go with This Plan:

**Phase 1 (Validation, 30 min GPU, $2):**
```
Domain:     1.5 × 0.4 × 0.013 m (thin, 2D-like)
Geometry:   Triangles (infinite rods)
Samples:    100 (single random rock configuration, 100 receivers)
Purpose:    "Confirm gprMax 3D engine = gprMax 2D engine"
Expected:   ~88% accuracy (validates platform)
```

**Phase 2 (True 3D, 4 hours GPU, $15):**
```
Domain:     1.5 × 0.4 × 0.4 m (thick, 3D)
Geometry:   Spheres (finite rocks, random 3D packing)
Samples:    1000 (200 per class)
Purpose:    "Measure how 3D geometry affects waveform-only classification"
Expected:   ~74-77% accuracy (shows real domain gap)
```

**Why both?**
- Phase 1 rules out "gprMax engine is broken" problem (low risk)
- Phase 2 answers your actual research question (high impact)
- Total cost: $17, total time: 5 hours GPU + 3 hours CPU setup

**Start with:** Option C (triangles, thin domain) → if accuracy ~88%, proceed to Option B (spheres, thick domain)

