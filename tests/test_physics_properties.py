"""
Property-based tests for physics calculations.

Tests mathematical invariants and domain constraints using Hypothesis framework.
Hypothesis generates hundreds of random test cases to ensure properties hold universally.

## Properties Tested:
1. **Invertibility**: PVC ↔ FI conversions are true mathematical inverses
2. **Monotonicity**: FI classification never downgrades as contamination increases
3. **Range Constraints**: All outputs within physically valid ranges
4. **Topp Model**: Dielectric constant behaves correctly across moisture range
5. **PSD Interpolation**: Log-linear interpolation preserves monotonicity

## Running Tests:
- All property tests: `pytest tests/test_physics_properties.py -v`
- Specific test: `pytest tests/test_physics_properties.py::test_name -v`
- Verbose hypothesis output: `pytest tests/test_physics_properties.py -v --hypothesis-show-statistics`

## Debugging Failures:
When hypothesis finds a failing case, it will:
1. Show the minimal failing example (automated shrinking)
2. Print the exact inputs that caused the failure
3. Save the example in `.hypothesis/examples/` for regression testing

To reproduce a specific failure:
```python
@example(pvc=42.5, phi=0.3)  # Add this decorator above the test
```

## Adjusting Test Performance:
If tests are too slow, reduce `max_examples` in `@settings` decorator.
Default is 200 examples per test (~5-10 seconds per test).
"""
import pytest
from hypothesis import given, strategies as st, settings
from src.physics import (
    convert_pvc_to_fi,
    inverse_convert_fi_to_pvc,
    classify_fouling_index,
    topp_mixing_model,
    get_percent_passing
)


# Hypothesis Strategies
@st.composite
def valid_pvc_values(draw):
    """Generate valid PVC values in range [0, 100]."""
    return draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))


@st.composite
def valid_porosity_values(draw):
    """Generate realistic porosity values for ballast [0.1, 0.6]."""
    return draw(st.floats(min_value=0.1, max_value=0.6, allow_nan=False, allow_infinity=False))


@st.composite
def valid_specific_gravities(draw):
    """Generate realistic specific gravity values [2.0, 3.0]."""
    return draw(st.floats(min_value=2.0, max_value=3.0, allow_nan=False, allow_infinity=False))


# Test 1: PVC ↔ FI Invertibility
@given(pvc=valid_pvc_values(), phi=valid_porosity_values())
@settings(max_examples=200, deadline=5000)
def test_pvc_to_fi_conversion_inverse_property(pvc, phi):
    """
    Property: PVC → FI → PVC should return original PVC (within tolerance).
    
    This tests that the mathematical transformations are true inverses.
    """
    # Forward conversion
    fi = convert_pvc_to_fi(pvc, porosity=phi)
    
    # Inverse conversion
    pvc_recovered = inverse_convert_fi_to_pvc(fi, porosity=phi)
    
    # Check invertibility with 0.01% relative tolerance
    if pvc > 0.1:  # Avoid division by zero for very small PVC
        relative_error = abs(pvc_recovered - pvc) / pvc
        assert relative_error < 0.0001, f"PVC={pvc}, FI={fi}, Recovered={pvc_recovered}, Error={relative_error}"
    else:
        # For very small PVC, use absolute tolerance
        assert abs(pvc_recovered - pvc) < 0.01


# Test 2: FI Classification Monotonicity
@given(fi_values=st.lists(
    st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    min_size=2,
    max_size=10
))
@settings(max_examples=200, deadline=5000)
def test_fi_classification_monotonicity(fi_values):
    """
    Property: Classification should never downgrade as FI increases.
    
    Tests ordinal relationship: CL < MF < F < HF
    """
    # Sort FI values
    sorted_fi = sorted(fi_values)
    
    # Define classification order
    class_order = {"CL": 0, "MF": 1, "F": 2, "HF": 3}
    
    # Get classifications
    classifications = [classify_fouling_index(fi) for fi in sorted_fi]
    class_levels = [class_order[c] for c in classifications]
    
    # Check monotonicity
    for i in range(len(class_levels) - 1):
        assert class_levels[i] <= class_levels[i + 1], \
            f"Classification downgrade: FI={sorted_fi[i]:.2f}→{classifications[i]}, " \
            f"FI={sorted_fi[i+1]:.2f}→{classifications[i+1]}"


# Test 3: FI Range Constraints
@given(
    pvc=st.floats(min_value=-100.0, max_value=200.0, allow_nan=False, allow_infinity=False),
    porosity=st.floats(min_value=-1.0, max_value=2.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=200, deadline=5000)
def test_fi_conversion_range_constraints(pvc, porosity):
    """
    Property: FI output must be in [0, 100] for any input.
    
    Tests defensive programming and edge case handling.
    """
    fi = convert_pvc_to_fi(pvc, porosity=porosity)
    
    # FI must be in valid range
    assert 0.0 <= fi <= 100.0, f"FI={fi} out of range for PVC={pvc}, phi={porosity}"
    
    # Negative PVC should give 0
    if pvc <= 0:
        assert fi == 0.0, f"Negative PVC={pvc} should give FI=0, got {fi}"
    
    # Invalid porosity should give 0
    if porosity <= 0:
        assert fi == 0.0, f"Invalid porosity={porosity} should give FI=0, got {fi}"


# Test 4: Topp Model Constraints
@given(theta=st.floats(min_value=-1.0, max_value=2.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=200, deadline=5000)
def test_topp_model_domain_constraints(theta):
    """
    Property: Topp model should clamp inputs and produce valid dielectric constants.
    
    Tests: 1) Output in valid range, 2) Clamping behavior
    """
    epsilon_r = topp_mixing_model(theta)
    
    # Dielectric constant should be >= 1.0 (air/dry soil minimum)
    assert epsilon_r >= 1.0, f"Dielectric constant {epsilon_r} < 1.0 for theta={theta}"
    
    # Should be <= 81 (water at room temp)
    assert epsilon_r <= 81.0, f"Dielectric constant {epsilon_r} > 81 for theta={theta}"


@given(
    theta_values=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=10
    )
)
@settings(max_examples=100, deadline=5000)
def test_topp_model_monotonicity(theta_values):
    """
    Property: Dielectric constant increases with water content.
    """
    sorted_theta = sorted(theta_values)
    dielectrics = [topp_mixing_model(t) for t in sorted_theta]
    
    # Check monotonic increase (allowing small numerical errors)
    for i in range(len(dielectrics) - 1):
        assert dielectrics[i] <= dielectrics[i + 1] + 1e-6, \
            f"Non-monotonic: theta={sorted_theta[i]:.3f}→ε={dielectrics[i]:.2f}, " \
            f"theta={sorted_theta[i+1]:.3f}→ε={dielectrics[i+1]:.2f}"


# Test 5: PSD Interpolation
@st.composite
def sorted_psd_points(draw):
    """Generate realistic sorted PSD curve points."""
    n_points = draw(st.integers(min_value=3, max_value=8))
    
    # Generate diameters in log-space for realism (clay to gravel)
    log_diameters = sorted([draw(st.floats(min_value=-3, max_value=1)) for _ in range(n_points)])
    diameters = [10**ld for ld in log_diameters]
    
    # Generate percent passing (must be non-decreasing)
    percent_passing = []
    current = draw(st.floats(min_value=0, max_value=20))
    for _ in range(n_points):
        percent_passing.append(current)
        current += draw(st.floats(min_value=0, max_value=30))
    
    # Clamp to 100
    percent_passing = [min(p, 100) for p in percent_passing]

    # Deduplicate by diameter — a valid PSD maps each diameter to exactly one value
    seen: dict = {}
    for d, p in zip(diameters, percent_passing):
        seen[d] = p
    return sorted(seen.items())


@given(psd=sorted_psd_points())
@settings(max_examples=100, deadline=5000)
def test_psd_interpolation_monotonicity(psd):
    """
    Property: Interpolated percent passing should be monotonic with diameter.
    """
    # Test at multiple query points
    d_min = psd[0][0]
    d_max = psd[-1][0]
    
    query_points = [d_min * (d_max / d_min) ** (i / 10) for i in range(11)]
    
    results = [get_percent_passing(d, psd) for d in query_points]
    
    # Check monotonicity
    for i in range(len(results) - 1):
        assert results[i] <= results[i + 1] + 1e-6, \
            f"Non-monotonic interpolation at d={query_points[i]:.4f}, {query_points[i+1]:.4f}"


@given(psd=sorted_psd_points())
@settings(max_examples=100, deadline=5000)
def test_psd_exact_match_values(psd):
    """
    Property: Querying exact PSD points should return exact percent passing.
    """
    for diameter, expected_percent in psd:
        result = get_percent_passing(diameter, psd)
        assert abs(result - expected_percent) < 1e-6, \
            f"Exact match failed: d={diameter}, expected={expected_percent}, got={result}"
