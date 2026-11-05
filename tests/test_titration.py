"""Tests for Modules 4, 5, 6, and 8: Burette, Flask, Indicator, and Titration Controller."""

import pytest
import math
from burette import VirtualBurette
from flask import ConicalFlask
from indicator import PhenolphthaleinIndicator
from titration import TitrationController, TitrationMode, ExperimentStatus


def test_burette_operations():
    """Verify burette filling, dispensing, precision, and limits."""
    b = VirtualBurette(capacity_ml=50.00, precision_ml=0.05)
    b.fill_to_mark(0.00)

    reading = b.get_reading()
    assert reading.current_reading_ml == 0.00
    assert reading.remaining_volume_ml == 50.00

    # Dispense 10.00 mL
    dispensed = b.dispense(10.00)
    assert math.isclose(dispensed, 10.00)
    reading = b.get_reading()
    assert reading.current_reading_ml == 10.00
    assert reading.delivered_volume_ml == 10.00
    assert reading.remaining_volume_ml == 40.00

    # Prevent negative dispensing
    with pytest.raises(ValueError):
        b.dispense(-2.0)

    # Exceeding capacity
    b.dispense(40.00)
    assert b.get_reading().is_empty is True
    with pytest.raises(ValueError):
        b.dispense(1.0)


def test_flask_pipette_and_indicator():
    """Verify conical flask sample pipetting, indicator addition, and volume tracking."""
    flask = ConicalFlask()
    assert flask.has_acid is False

    # Pipette 25.00 mL HCl
    flask.pipette_hcl_sample(25.00)
    assert flask.has_acid is True
    assert flask.hcl_volume_ml == 25.00
    assert flask.current_ph < 2.0

    # Add indicator drops
    flask.add_indicator(2)
    assert flask.indicator.drops_added == 2

    # Receive titrant
    flask.receive_naoh(5.00)
    snapshot = flask.get_snapshot()
    assert snapshot.total_volume_ml == 30.00
    assert snapshot.naoh_added_ml == 5.00


def test_indicator_transitions():
    """Verify phenolphthalein chromophore transitions: colorless -> faint pink -> deep pink."""
    ind = PhenolphthaleinIndicator()
    ind.add_drops(2)

    # Acidic / Neutral (pH 1.0 to 7.0) -> Colorless
    obs_acid = ind.evaluate(ph=2.0)
    assert obs_acid.color_name == "Colorless"
    assert obs_acid.is_endpoint is False

    obs_neutral = ind.evaluate(ph=7.0)
    assert obs_neutral.color_name == "Colorless"
    assert obs_neutral.is_endpoint is False

    # Faint pink transition (pH 8.3) -> First persistent faint pink endpoint
    obs_ep = ind.evaluate(ph=8.30, swirled=True)
    assert obs_ep.color_name == "Faint Pink"
    assert obs_ep.is_endpoint is True

    # Strongly alkaline (pH 11.0) -> Over-titrated deep magenta
    obs_over = ind.evaluate(ph=11.0)
    assert obs_over.color_name == "Deep Pink / Magenta"
    assert obs_over.is_overtitrated is True


def test_titration_controller_workflow():
    """Verify complete titration run and endpoint detection."""
    controller = TitrationController()
    controller.setup_new_trial(TitrationMode.ACCURATE)

    controller.pipette_acid()
    controller.add_indicator(2)

    # Add NaOH up to 22.00 mL (approaching endpoint)
    controller.dispense_titrant(22.00)
    tel = controller.get_telemetry()
    assert tel.is_endpoint is False
    assert tel.titrant_dispensed_ml == 22.00

    # Add dropwise increment to reach 22.501 mL (faint pink endpoint, pH ~ 8.32)
    controller.dispense_titrant(0.501)
    tel_ep = controller.get_telemetry()
    assert 8.20 <= tel_ep.ph <= 8.50
    assert tel_ep.is_endpoint is True
    assert controller.endpoint_recorded is True
    assert controller.status == ExperimentStatus.ENDPOINT_REACHED

    # Additional titrant triggers over-titrated status
    controller.dispense_titrant(1.00)
    tel_over = controller.get_telemetry()
    assert tel_over.is_overtitrated is True
    assert controller.status == ExperimentStatus.OVERTITRATED
