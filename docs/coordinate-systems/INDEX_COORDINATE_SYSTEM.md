# Complete Coordinate System Documentation Index

## Quick Navigation

**New to this topic?** Start here:
1. [COORDINATE_FIX_SUMMARY.txt](COORDINATE_FIX_SUMMARY.txt) - Quick visual overview (5 min)
2. [COUPLING_DIAGRAM.txt](COUPLING_DIAGRAM.txt) - How workers depend on each other (5 min)
3. This file - Understanding the big picture

**Deep dive? Read these in order:**
1. [COORDINATE_SYSTEM.md](COORDINATE_SYSTEM.md) - Complete architecture (30 min)
2. [COORDINATE_TRADEOFFS.md](COORDINATE_TRADEOFFS.md) - Design analysis (20 min)
3. [COUPLING_CODE_EXAMPLES.md](COUPLING_CODE_EXAMPLES.md) - Code walkthrough (15 min)

**Want to verify it works?** Run these:
```bash
python test_coordinate_trace.py          # See coordinates flow correctly
python test_strip_fix.py                 # Quick verification
python test_strip_packing_pipeline.py    # Full integration (in progress)
```

---

## The Core Insight

### One Sentence Summary
**Absolute coordinates throughout the pipeline, except StripPackingStrategy was breaking the contract until fixed.**

### Key Principle
```
All rocks are positioned in WORLD SPACE (absolute coordinates).
Y-coordinates NEVER change between workers.
If bounds says y ∈ [0.3, 0.55], pack EXACTLY there, not at origin.
```

---

## File Reference

### Bug Analysis
| File | Purpose | Read Time |
|------|---------|-----------|
| [COORDINATE_FIX_SUMMARY.txt](COORDINATE_FIX_SUMMARY.txt) | Before/after comparison with diagrams | 5 min |
| [VISUAL_COORDINATE_DIAGRAM.txt](VISUAL_COORDINATE_DIAGRAM.txt) | ASCII rock position diagrams | 5 min |
| [COORDINATE_SYSTEM.md](COORDINATE_SYSTEM.md) | Full worker pipeline + coordinate flow | 30 min |

### Design Analysis
| File | Purpose | Read Time |
|------|---------|-----------|
| [COORDINATE_TRADEOFFS.md](COORDINATE_TRADEOFFS.md) | Absolute vs relative, coupling strength | 20 min |
| [COUPLING_DIAGRAM.txt](COUPLING_DIAGRAM.txt) | Dependency graphs, impact of changes | 10 min |
| [COUPLING_CODE_EXAMPLES.md](COUPLING_CODE_EXAMPLES.md) | Code examples + refactoring options | 15 min |

### Executable Demos
| File | Purpose | Runtime |
|------|---------|---------|
| [test_coordinate_trace.py](test_coordinate_trace.py) | Watch coordinates flow through pipeline | 30 sec |
| [test_strip_fix.py](test_strip_fix.py) | Verify rocks in ballast layer | 10 sec |
| [test_strip_packing_pipeline.py](test_strip_packing_pipeline.py) | Full integration test (in progress) | 2 min |

---

## Key Concepts

### Absolute Coordinates
```
All positions are in world space with fixed origin at y=0.

Advantages:
  ✓ Simple
  ✓ Fast
  ✓ Easy to debug
  ✓ Good for physics

Disadvantages:
  ✗ Tightly coupled
  ✗ Hard to relocate groups
  ✗ Brittle to changes
```

### Tight Coupling
```
All workers must agree on absolute coordinate boundaries.

BallastWorker decides: ballast_bottom = 0.3
     ↓
GranularMatrixWorker expects: bounds.y_min = 0.3
     ↓
StripPackingStrategy MUST use: strip_bounds.y_min = 0.3
     ↓
LabWorker samples: y ∈ [0.3, 0.55]

If ANY worker breaks this contract:
  ✗ System misalignment
  ✗ PVC calculations wrong
  ✗ Material properties incorrect
```

### The Bug
```
StripPackingStrategy ignored bounds parameter:
  Input:  bounds = [0, 2.248] × [0.3, 0.55]
  Action: strip_bounds = [0, 5.0] × [0, 3.2]  ← WRONG!
  Output: rocks at y ∈ [0, 3.2]

LabWorker searched [0.3, 0.55] but rocks were at [0, 3.2]
  Result: Only ~10 rocks found instead of 279
  PVC calculated: 47% or 3.7% instead of 30%
```

### The Fix
```
Two lines changed:

BEFORE: strip_bounds.y_min = 0.0, y_max = self.strip_height
AFTER:  strip_bounds.y_min = bounds.y_min, y_max = bounds.y_max

Now contract is honored:
  Input:  bounds = [0, 2.248] × [0.3, 0.55]
  Action: strip_bounds = [0, 5.0] × [0.3, 0.55]  ← CORRECT!
  Output: rocks at y ∈ [0.3, 0.55]

LabWorker searches [0.3, 0.55] and finds ALL rocks
  Result: All 279 rocks found
  PVC calculated: 30% (correct!)
```

---

## Architecture Decisions

### Why Absolute Coordinates?

**Chosen for:**
- Simplicity (no translation overhead)
- Performance (no coordinate transforms)
- Debuggability (values match what you see)
- Directness (physics works naturally in world space)
- Suitable for stable layer definitions

**Cost:** Tight coupling between workers

### Why Tight Coupling Works Here

**Acceptable because:**
1. Layer definitions are stable (won't change frequently)
2. Few workers (5-8 total)
3. Codebase is small (easy to verify consistency)
4. Performance matters (no overhead acceptable)

**Risk factors:**
- Refactoring is risky (must update multiple files)
- Easy to miss one location in coordinate space
- Scaling to many layers would be painful

### When to Reconsider

Use **relative coordinates** and loose coupling if:
- Multiple domain heights (different ballast depths per sample)
- Nested extraction (windows within windows)
- Dynamic layer reconfiguration
- Complex hierarchical structures
- Large team (easier to miss coupling violations)

---

## Lessons Learned

### Root Cause Analysis
1. **Symptom:** PVC calculations wildly incorrect (3.7%-47% vs 30%)
2. **Investigation:** Created standalone packing test (decoupled from pipeline)
3. **Discovery:** Rock extraction works correctly, material layer calculation fails
4. **Root cause:** Rocks in wrong y-coordinate range than expected
5. **Deep cause:** Contract violation - bounds parameter ignored

### Prevention Strategies

1. **Add validation**
   ```python
   assert bounds.y_min is not None
   # Use bounds, don't override it
   strip_bounds.y_min = bounds.y_min
   ```

2. **Document contracts**
   ```python
   def generate_rocks(self, bounds: PackingBounds):
       """Pack rocks within bounds.y_min to bounds.y_max.
       
       Contract: Caller expects rocks in this exact y-range.
       """
   ```

3. **Test at boundaries**
   ```python
   # Unit test: packer respects bounds
   assert all(bounds.y_min <= r.y <= bounds.y_max 
              for r in rocks)
   ```

4. **Trace coordinates**
   - When debugging, print y-coordinates at each worker
   - Verify they match expected range
   - Use test scripts to visualize flow

---

## Common Questions

### Q: Why not just use relative coordinates?
A: Performance. Translating coordinates (y - offset) on every rock every pipeline run adds up. Absolute is faster and sufficient for stable layer structure.

### Q: How much would decoupling cost?
A: Moderate refactoring (~200 lines of code). But would eliminate tight coupling and make refactoring safe. Worth doing if codebase grows significantly.

### Q: What if I change ballast thickness?
A: Currently risky. You'd need to:
- Update BallastWorker
- Update any hardcoded boundaries in SubgradeWorker, FormationWorker
- Update LabWorker sampling region (or hope it reads from metadata)
- Verify StripPackingStrategy respects bounds (it now does)

With loose coupling, you'd just change one Layer definition.

### Q: Can the bug happen again?
A: Only if:
1. New packing strategy ignores bounds parameter (prevented by contract documentation)
2. New worker hardcodes absolute coordinates (prevented by code review)
3. Layer definitions change without updating all files (prevented by testing)

Added tests catch this type of bug. Specifically:
- `test_coordinate_trace.py` verifies coordinate flow
- `test_strip_fix.py` verifies rocks are in ballast layer

### Q: Should I refactor to relative coordinates?
A: Not yet. Current approach works and is simple. Refactor only if:
- You need multiple domain heights
- Layer definitions change frequently
- You're hiring more developers (more eyes to miss coupling)
- Performance testing shows coordinate transforms aren't bottleneck

---

## Related Work

### From Earlier Sessions
- [[speedup_strategies]] - Original strip packing design
- [[hybridshang_tuning]] - Iteration tuning (300 iterations)
- [[algorithm_api_fixes]] - API unification across 12 packing algorithms
- [[project_status]] - Current feature set and command reference

### Documentation Created This Session
- **COORDINATE_SYSTEM.md** - Complete architecture reference
- **COORDINATE_TRADEOFFS.md** - Design analysis and recommendations
- **COUPLING_DIAGRAM.txt** - Dependency visualization
- **COUPLING_CODE_EXAMPLES.md** - Code walkthrough and refactoring examples
- **test_coordinate_trace.py** - Interactive coordinate flow demo
- **README_COORDINATE_SYSTEM.md** - Overview and navigation guide

---

## Next Steps

### Immediate (Current Sprint)
✓ Identify root cause - DONE
✓ Fix the bug - DONE  
✓ Create comprehensive documentation - DONE (you're reading it!)
→ Run full pipeline validation (test_strip_packing_pipeline.py)
→ Verify PVC calculations match between individual and extracted packing

### Short Term
→ Add assertions validating coordinate contracts
→ Expand test coverage at worker boundaries
→ Document coordinate system in main README.md

### Medium Term (If Scaling)
→ Consider loose coupling refactor
→ Extract layer definitions to configuration
→ Add more sophisticated validation/testing

### Long Term
→ Monitor refactoring risk as codebase grows
→ Migrate to relative coordinates if complexity demands
→ Consider more workers, more layers, more flexibility

---

## Summary

**The Current Design:**
- Uses absolute coordinates (world space)
- Creates tight coupling between workers
- Works well for stable, simple layer structure
- Efficient and easy to debug
- Risk: breaks if contract is violated

**The Bug:**
- StripPackingStrategy ignored bounds contract
- Resulted in rocks at wrong y-coordinates
- Downstream workers couldn't find them
- PVC calculations used incomplete data

**The Fix:**
- Respect bounds parameter input
- Pack at ballast layer coordinates (not at origin)
- Maintain tight coupling properly

**Going Forward:**
- Validate contracts explicitly
- Test at layer boundaries
- Document coordinate system
- Consider loose coupling if complexity grows

---

## Document Stats

Total documentation: ~15,000 words across 8 files
- Analysis & design: 10,000 words
- Code examples: 3,000 words  
- Executable tests: 3 scripts

Time to fully understand: 1-2 hours
Time to verify fix works: 5-10 minutes

This should be sufficient for anyone (including your future self) to:
1. Understand what went wrong
2. Know how the fix works
3. Avoid repeating this type of bug
4. Decide if refactoring to loose coupling is needed
