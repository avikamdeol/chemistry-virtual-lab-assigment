"""Tests for Module 7 (pH Measurement) and Physical Equilibrium."""

import pytest
import math
from ph_calculator import PHCalculator
from config import (
    ACID_VOLUME_ML,
    TRUE_HCL_CONCENTRATION_M,
    NAOH_CONCENTRATION_M,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
    NEUTRAL_PH,
)


def test_initial_conditions():
    """Verify initial acid moles and pH before any NaOH is added."""
    calc = PHCalculator()
    state = calc.calculate_ph(0.0)

    # Initial moles = 0.0900 M * 0.025 L = 0.00225 mol
    expected_moles = 0.00225
    assert math.isclose(state.moles_acid_initial, expected_moles, rel_tol=1e-6)

    # Initial pH for 0.0900 M strong acid: -log10(0.0900) ≈ 1.0458
    assert state.ph < 2.0
    assert state.is_at_equivalence is False
    assert state.equivalence_status == "Before Equivalence"


def test_theoretical_equivalence_volume():
    """Verify theoretical equivalence volume is calculated strictly using chemical formula."""
    calc = PHCalculator(
        acid_vol_ml=25.00,
        acid_conc_m=0.0900,
        base_conc_m=0.100,
    )
    # V_base = (0.0900 * 25.00) / 0.100 = 22.50 mL
    assert math.isclose(calc.v_eq_ml, 22.50, rel_tol=1e-6)


def test_ph_before_equivalence():
    """Verify solution remains strongly/moderately acidic prior to 22.50 mL."""
    calc = PHCalculator()

    # After 10.00 mL NaOH
    s10 = calc.calculate_ph(10.00)
    assert s10.ph > 1.0
    assert s10.ph < 3.0
    assert s10.is_at_equivalence is False

    # After 20.00 mL NaOH
    s20 = calc.calculate_ph(20.00)
    assert s20.ph > 2.0
    assert s20.ph < 4.0
    assert s20.is_at_equivalence is False

    # After 22.40 mL NaOH (very close to equivalence)
    s22_4 = calc.calculate_ph(22.40)
    assert 3.0 < s22_4.ph < 7.0
    assert s22_4.is_at_equivalence is False


def test_ph_at_ideal_equivalence():
    """Verify pH is exactly 7.00 at theoretical equivalence volume (22.50 mL)."""
    calc = PHCalculator()
    s_eq = calc.calculate_ph(22.50)

    assert s_eq.is_at_equivalence is True
    assert math.isclose(s_eq.ph, NEUTRAL_PH, abs_tol=1e-2)
    assert math.isclose(s_eq.poh, NEUTRAL_PH, abs_tol=1e-2)
    assert s_eq.equivalence_status == "At Equivalence Point"


def test_ph_after_equivalence():
    """Verify solution becomes distinctly basic after equivalence."""
    calc = PHCalculator()

    # At 22.60 mL (0.10 mL past equivalence)
    s22_6 = calc.calculate_ph(22.60)
    assert s22_6.ph > 7.0
    assert s22_6.is_at_equivalence is False
    assert s22_6.equivalence_status == "After Equivalence"

    # At 25.00 mL
    s25 = calc.calculate_ph(25.00)
    assert s25.ph > 10.0
    assert s25.ph <= 14.0


def test_negative_volume_rejection():
    """Verify negative titrant volume raises ValueError."""
    calc = PHCalculator()
    with pytest.raises(ValueError):
        calc.calculate_ph(-1.0)
