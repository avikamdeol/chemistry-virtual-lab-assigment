"""Tests for Module 12: Experimental Error Laboratory Simulations."""

import pytest
import math
from error_analysis import ExperimentalErrorSimulator, ErrorDirection
from config import TRUE_HCL_CONCENTRATION_M


def test_overshoot_error():
    """Verify overshooting endpoint leads to falsely HIGHER calculated HCl concentration."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_overshoot(excess_volume_ml=1.50)

    assert res.direction == ErrorDirection.HIGHER
    assert res.calculated_hcl_m > TRUE_HCL_CONCENTRATION_M
    assert res.percentage_error > 0.0


def test_undershoot_error():
    """Verify undershooting endpoint leads to falsely LOWER calculated HCl concentration."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_undershoot(premature_deficit_ml=0.80)

    assert res.direction == ErrorDirection.LOWER
    assert res.calculated_hcl_m < TRUE_HCL_CONCENTRATION_M
    assert res.percentage_error < 0.0


def test_reading_parallax_error():
    """Verify burette reading offset shifts calculated concentration accordingly."""
    sim = ExperimentalErrorSimulator()
    res_high = sim.simulate_reading_error(offset_ml=+0.35)
    assert res_high.direction == ErrorDirection.HIGHER
    assert res_high.calculated_hcl_m > TRUE_HCL_CONCENTRATION_M

    res_low = sim.simulate_reading_error(offset_ml=-0.35)
    assert res_low.direction == ErrorDirection.LOWER
    assert res_low.calculated_hcl_m < TRUE_HCL_CONCENTRATION_M


def test_pipette_error():
    """Verify delivering less acid (e.g. 24.20 mL) leads to falsely LOWER calculated HCl concentration."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_pipette_error(actual_pipetted_vol_ml=24.20)

    assert res.direction == ErrorDirection.LOWER
    assert res.calculated_hcl_m < TRUE_HCL_CONCENTRATION_M


def test_air_bubble_in_burette():
    """Verify dislodged air bubble in burette tip inflates titre and gives falsely HIGHER concentration."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_air_bubble_in_burette(bubble_volume_ml=0.40)

    assert res.direction == ErrorDirection.HIGHER
    assert res.calculated_hcl_m > TRUE_HCL_CONCENTRATION_M


def test_wet_flask_with_water():
    """Verify residual water in the conical flask leaves the calculated concentration UNCHANGED."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_wet_flask_with_water(water_drops_ml=5.0)

    assert res.direction == ErrorDirection.UNCHANGED
    assert math.isclose(res.calculated_hcl_m, TRUE_HCL_CONCENTRATION_M, abs_tol=1e-5)
    assert math.isclose(res.percentage_error, 0.00, abs_tol=1e-5)


def test_wet_burette_with_water():
    """Verify unrinsed wet burette dilutes titrant and gives falsely HIGHER concentration."""
    sim = ExperimentalErrorSimulator()
    res = sim.simulate_wet_burette_with_water(dilution_factor=0.05)

    assert res.direction == ErrorDirection.HIGHER
    assert res.calculated_hcl_m > TRUE_HCL_CONCENTRATION_M
