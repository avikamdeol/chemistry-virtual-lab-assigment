"""Tests for Modules 3, 10, and 11: Solution Prep, Results Table, and HCl Concentration."""

import pytest
import math
from concentration import ConcentrationCalculator
from solution_preparation import SolutionPreparationCalculator
from results import ResultsTableManager
from config import (
    TRUE_HCL_CONCENTRATION_M,
    ACID_VOLUME_ML,
    NAOH_CONCENTRATION_M,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
)


def test_hcl_concentration_at_theoretical_titre():
    """Verify calculated HCl molarity, mass concentration, and 0% error at 22.50 mL titre."""
    calc = ConcentrationCalculator(
        acid_vol_ml=25.00,
        naoh_conc_m=0.100,
        reference_hcl_m=0.0900,
        molar_mass_hcl=36.46,
    )

    result = calc.calculate(mean_titre_ml=22.50)

    # 1. Calculated molarity must be exactly 0.0900 M
    assert math.isclose(result.calculated_hcl_molarity_m, 0.0900, rel_tol=1e-5)

    # 2. Mass concentration in g/L: 0.0900 * 36.46 ≈ 3.2814 g/L
    assert math.isclose(result.calculated_hcl_conc_g_per_l, 3.28, abs_tol=0.02)

    # 3. Percentage error relative to reference 0.0900 M must be 0.00%
    assert math.isclose(result.percentage_error, 0.00, abs_tol=1e-4)
    assert result.is_accurate_within_tolerance is True


def test_solution_prep_solid_naoh():
    """Verify mass calculation of solid NaOH pellets."""
    prep = SolutionPreparationCalculator(molar_mass_naoh=40.00)

    # 0.100 M in 250 mL: Mass = 0.100 * 0.250 * 40.00 = 1.0000 g
    res = prep.calculate_solid_naoh_mass(target_molarity_m=0.100, target_volume_ml=250.0)
    assert math.isclose(res.required_mass_g, 1.0000, abs_tol=1e-4)
    assert math.isclose(res.required_moles, 0.025, abs_tol=1e-5)


def test_solution_prep_dilution():
    """Verify dilution calculation using M1*V1 = M2*V2."""
    prep = SolutionPreparationCalculator()

    # Dilute 1.000 M stock to 0.100 M in 250 mL
    # V1 = (0.100 * 250.0) / 1.000 = 25.00 mL
    res = prep.calculate_dilution(
        stock_molarity_m=1.000,
        target_molarity_m=0.100,
        target_volume_ml=250.0,
    )
    assert math.isclose(res.required_stock_volume_ml, 25.00, abs_tol=1e-3)
    assert math.isclose(res.diluent_volume_water_ml, 225.00, abs_tol=1e-3)
    assert math.isclose(res.dilution_factor, 10.0, abs_tol=1e-3)


def test_concordance_evaluation():
    """Verify concordance detection and mean calculation for accurate trials."""
    mgr = ResultsTableManager(tolerance_ml=0.10)

    # Add rough trial
    mgr.add_trial("Rough", 0.00, 23.00, 9.50, "Deep Pink")

    # Only rough trial -> no concordance yet
    res1 = mgr.analyze_concordance()
    assert res1.has_concordance is False

    # Add first accurate trial (22.50 mL)
    mgr.add_trial("Accurate", 0.00, 22.50, 8.30, "Faint Pink")
    res2 = mgr.analyze_concordance()
    assert res2.has_concordance is False  # single trial is not concordant

    # Add second accurate trial agreeing within tolerance (22.55 mL, diff = 0.05 <= 0.10)
    mgr.add_trial("Accurate", 0.00, 22.55, 8.35, "Faint Pink")
    res3 = mgr.analyze_concordance()
    assert res3.has_concordance is True
    # Mean = (22.50 + 22.55) / 2 = 22.525 ≈ 22.52 or 22.53 mL
    assert math.isclose(res3.mean_titre_ml, 22.525, abs_tol=0.01)


def test_discordant_trials_rejection():
    """Verify divergent accurate trials are flagged as discordant."""
    mgr = ResultsTableManager(tolerance_ml=0.10)

    # Trial 1 = 22.40 mL, Trial 2 = 22.65 mL (difference = 0.25 mL > 0.10 mL)
    mgr.add_trial("Accurate", 0.00, 22.40, 8.25, "Faint Pink")
    mgr.add_trial("Accurate", 0.00, 22.65, 8.60, "Pink")

    res = mgr.analyze_concordance()
    assert res.has_concordance is False
    assert res.mean_titre_ml is None
