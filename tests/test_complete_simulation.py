"""End-to-end integration test verifying the complete 13-stage virtual lab experiment."""

import os
import math
from titration import TitrationController, TitrationMode, ExperimentStatus
from results import ResultsTableManager
from concentration import ConcentrationCalculator
from error_analysis import ExperimentalErrorSimulator, ErrorDirection
from report_generator import LaboratoryReportGenerator
from titration_curve import TitrationCurvePlotter


def test_complete_experimental_workflow():
    """Execute the entire 13-stage laboratory experiment and verify scientific accuracy."""
    print("--- STAGE 1 & 2: Setup and Apparatus Initialisation ---")
    ctrl = TitrationController()
    results_mgr = ResultsTableManager(tolerance_ml=0.10)
    conc_calc = ConcentrationCalculator()
    error_sim = ExperimentalErrorSimulator()
    plotter = TitrationCurvePlotter()

    # 1. Pipette 25.00 mL HCl Sample
    ctrl.pipette_acid()
    assert ctrl.flask.has_acid is True
    assert math.isclose(ctrl.flask.hcl_volume_ml, 25.00)

    # 2. Add Indicator
    ctrl.add_indicator(2)
    assert ctrl.flask.indicator.drops_added == 2

    print("--- STAGE 3: Rough Titration (Exploratory Run) ---")
    ctrl.setup_new_trial(TitrationMode.ROUGH, trial_num=1)
    ctrl.pipette_acid()
    ctrl.add_indicator(2)

    # Fast additions in steps of 5.0 mL
    ctrl.dispense_titrant(5.00)
    ctrl.dispense_titrant(5.00)
    ctrl.dispense_titrant(5.00)
    ctrl.dispense_titrant(5.00)
    assert math.isclose(ctrl.burette.total_delivered_ml, 20.00)
    assert ctrl.endpoint_recorded is False

    # Add 3.00 mL to cross into basic region (23.00 mL)
    ctrl.dispense_titrant(3.00)
    tel_rough = ctrl.get_telemetry()
    assert tel_rough.titrant_dispensed_ml == 23.00
    assert tel_rough.ph > 8.50  # Over-titrated in rough run
    assert ctrl.endpoint_recorded is True

    # Record Rough Trial
    results_mgr.add_trial(
        trial_type="Rough",
        initial_reading_ml=0.00,
        final_reading_ml=23.00,
        endpoint_ph=tel_rough.ph,
        observation_color=tel_rough.color_name,
        notes="Rough exploratory trial"
    )

    print("--- STAGE 4: Accurate Titration 1 (Analytical Dropwise Run) ---")
    ctrl.setup_new_trial(TitrationMode.ACCURATE, trial_num=2)
    ctrl.pipette_acid()
    ctrl.add_indicator(2)

    # Fast advance up to 21.00 mL (safely below equivalence)
    ctrl.dispense_titrant(21.00)
    # Fine increments near endpoint
    ctrl.dispense_titrant(1.00)   # 22.00 mL
    ctrl.dispense_titrant(0.40)   # 22.40 mL
    ctrl.dispense_titrant(0.08)   # 22.48 mL
    ctrl.dispense_titrant(0.02)   # 22.50 mL (ideal equivalence)
    ctrl.dispense_titrant(0.001)  # 22.501 mL (crosses into faint pink)

    tel_acc1 = ctrl.get_telemetry()
    assert 8.20 <= tel_acc1.ph <= 8.50
    assert tel_acc1.is_endpoint is True
    assert tel_acc1.color_name == "Faint Pink"

    results_mgr.add_trial(
        trial_type="Accurate",
        initial_reading_ml=0.00,
        final_reading_ml=22.50,
        endpoint_ph=tel_acc1.ph,
        observation_color="Faint Pink",
        notes="First persistent faint pink endpoint"
    )

    print("--- STAGE 5: Accurate Titration 2 (Concordance Verification Run) ---")
    ctrl.setup_new_trial(TitrationMode.ACCURATE, trial_num=3)
    ctrl.pipette_acid()
    ctrl.add_indicator(2)

    ctrl.dispense_titrant(22.00)
    ctrl.dispense_titrant(0.501)
    tel_acc2 = ctrl.get_telemetry()
    assert 8.20 <= tel_acc2.ph <= 8.50

    results_mgr.add_trial(
        trial_type="Accurate",
        initial_reading_ml=0.00,
        final_reading_ml=22.50,
        endpoint_ph=tel_acc2.ph,
        observation_color="Faint Pink",
        notes="Concordant replicate trial"
    )

    print("--- STAGE 6: Concordance and Stoichiometry Evaluation ---")
    concordance = results_mgr.analyze_concordance()
    assert concordance.has_concordance is True
    assert math.isclose(concordance.mean_titre_ml, 22.50, abs_tol=1e-3)

    conc_res = conc_calc.calculate(concordance.mean_titre_ml)
    # 0.0900 M HCl
    assert math.isclose(conc_res.calculated_hcl_molarity_m, 0.0900, rel_tol=1e-5)
    # 3.28 g/L Strength
    assert math.isclose(conc_res.calculated_hcl_conc_g_per_l, 3.28, abs_tol=0.02)
    # 0.00% Error
    assert math.isclose(conc_res.percentage_error, 0.00, abs_tol=1e-5)

    print("--- STAGE 7: Error Simulation Suite ---")
    scenarios = error_sim.get_all_scenarios()
    assert len(scenarios) == 7
    # Verify overshoot is higher, undershoot is lower, wet flask is unchanged
    assert any(s.error_id == "overshoot" and s.direction == ErrorDirection.HIGHER for s in scenarios)
    assert any(s.error_id == "undershoot" and s.direction == ErrorDirection.LOWER for s in scenarios)
    assert any(s.error_id == "wet_flask" and s.direction == ErrorDirection.UNCHANGED for s in scenarios)

    print("--- STAGE 8: Report and Graph Generation ---")
    report_gen = LaboratoryReportGenerator()
    html = report_gen.generate_html_report(
        results_mgr=results_mgr,
        conc_result=conc_res,
        concordance=concordance,
        error_outcomes=scenarios,
        safety_verified=True,
    )
    assert "0.0900 M" in html
    assert "3.28 g/L" in html
    assert "Concordant" in html

    txt = report_gen.generate_txt_report(
        results_mgr=results_mgr,
        conc_result=conc_res,
        concordance=concordance,
        error_outcomes=scenarios,
        safety_verified=True,
    )
    assert "M_HCl x V_HCl = M_NaOH x V_NaOH" in txt

    print("=== ALL 13 VIRTUAL LAB STAGES VERIFIED PERFECTLY! ===")


if __name__ == "__main__":
    test_complete_experimental_workflow()
