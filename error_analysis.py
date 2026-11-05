"""Module 12 — Experimental Error Simulation and Analytical Diagnostics.

Models and analyzes the six fundamental laboratory errors in volumetric titrimetry:
1. Overshooting the endpoint (excess NaOH dispensed)
2. Undershooting the endpoint (premature cessation upon transient color)
3. Incorrect burette reading (parallax / meniscus curvature errors)
4. Incorrect pipette delivery volume (air bubble / improper drainage)
5. Air bubble trapped in burette tip dislodging during titrant flow
6. Contaminated apparatus (water in conical flask vs unrinsed water in burette)

For each error, provides:
- Qualitative effect on calculated HCl concentration: HIGHER, LOWER, or UNCHANGED
- Quantitative calculation of simulated titre and resultant calculated molarity
- Percentage deviation relative to the true 0.0900 M reference
- In-depth chemical and operational pedagogical rationale
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any
from config import (
    ACID_VOLUME_ML,
    NAOH_CONCENTRATION_M,
    TRUE_HCL_CONCENTRATION_M,
    MOLAR_MASS_HCL,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
)


class ErrorDirection(Enum):
    HIGHER = "Falsely HIGHER"
    LOWER = "Falsely LOWER"
    UNCHANGED = "UNCHANGED (Accurate)"


@dataclass(frozen=True)
class ErrorSimulationOutcome:
    """Quantitative and diagnostic outcome of an experimental error simulation."""
    error_id: str
    error_title: str
    parameter_description: str
    ideal_titre_ml: float
    simulated_titre_ml: float
    true_hcl_m: float
    calculated_hcl_m: float
    percentage_error: float
    direction: ErrorDirection
    chemical_mechanism: str
    prevention_protocol: str


class ExperimentalErrorSimulator:
    """Engine for simulating and explaining volumetric analytical errors."""

    def __init__(
        self,
        true_hcl_m: float = TRUE_HCL_CONCENTRATION_M,
        acid_vol_ml: float = ACID_VOLUME_ML,
        naoh_conc_m: float = NAOH_CONCENTRATION_M,
    ):
        self.true_hcl_m = true_hcl_m
        self.acid_vol_ml = acid_vol_ml
        self.naoh_conc_m = naoh_conc_m
        self.ideal_titre_ml = THEORETICAL_EQUIVALENCE_VOLUME_ML

    def simulate_overshoot(self, excess_volume_ml: float = 1.50) -> ErrorSimulationOutcome:
        """Simulate overshooting the endpoint (deep pink instead of faint blush)."""
        sim_titre = self.ideal_titre_ml + excess_volume_ml
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0

        return ErrorSimulationOutcome(
            error_id="overshoot",
            error_title="Overshooting the Endpoint (Excess NaOH Added)",
            parameter_description=f"Added +{excess_volume_ml:.2f} mL excess NaOH beyond endpoint",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=sim_titre,
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=ErrorDirection.HIGHER,
            chemical_mechanism=(
                "When titration proceeds until a deep magenta color forms, an excess of OH- ions "
                "has been introduced beyond stoichiometric neutralisation. Because V_NaOH in the formula "
                "M_HCl = (M_NaOH * V_NaOH) / V_HCl is falsely elevated, the numerator increases, "
                "yielding a calculated HCl concentration that is falsely HIGH."
            ),
            prevention_protocol=(
                "Near the expected equivalence volume (~21-22 mL), switch to dropwise additions "
                "(0.05 mL increments) with vigorous swirling. Stop at the first faint blush pink "
                "that persists for at least 30 seconds."
            ),
        )

    def simulate_undershoot(self, premature_deficit_ml: float = 0.80) -> ErrorSimulationOutcome:
        """Simulate undershooting the endpoint (stopping at transient flash)."""
        sim_titre = max(0.1, self.ideal_titre_ml - premature_deficit_ml)
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0

        return ErrorSimulationOutcome(
            error_id="undershoot",
            error_title="Undershooting the Endpoint (Premature Cessation)",
            parameter_description=f"Stopped {premature_deficit_ml:.2f} mL before true persistence",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=sim_titre,
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=ErrorDirection.LOWER,
            chemical_mechanism=(
                "A local high concentration of OH- around the entering drop produces a momentary "
                "flash of pink before diffusion occurs. If the student mistakes this transient flash "
                "for the endpoint without complete swirling, V_NaOH recorded is lower than required "
                "for stoichiometric neutralisation, yielding a calculated HCl concentration that is falsely LOW."
            ),
            prevention_protocol=(
                "Always swirl the conical flask continuously during additions. The genuine endpoint "
                "is defined by a uniform faint pink tint across the entire solution lasting >= 30 seconds."
            ),
        )

    def simulate_reading_error(self, offset_ml: float = 0.35) -> ErrorSimulationOutcome:
        """Simulate incorrect burette meniscus reading (e.g. parallax error)."""
        sim_titre = self.ideal_titre_ml + offset_ml
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0
        direction = ErrorDirection.HIGHER if offset_ml > 0 else ErrorDirection.LOWER

        return ErrorSimulationOutcome(
            error_id="reading_error",
            error_title="Incorrect Burette Reading (Parallax / Top of Meniscus)",
            parameter_description=f"Burette reading recorded with offset of {offset_ml:+.2f} mL",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=sim_titre,
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=direction,
            chemical_mechanism=(
                "Burette graduations are calibrated for aqueous liquids with a concave meniscus "
                "read at eye level at the lowest point of curvature. Viewing from an angle (parallax) "
                "or reading from the top edges artificially shifts the measured volume. An artificially "
                "enlarged titre directly inflates the calculated molarity proportionally."
            ),
            prevention_protocol=(
                "Position your eyes exactly level with the bottom of the liquid meniscus. Use a white "
                "card with a dark horizontal line behind the burette to sharpen meniscus visibility."
            ),
        )

    def simulate_pipette_error(self, actual_pipetted_vol_ml: float = 24.20) -> ErrorSimulationOutcome:
        """Simulate pipetting error (e.g. air bubble or liquid retained in pipette)."""
        # Actual moles of HCl delivered to flask:
        actual_moles = self.true_hcl_m * (actual_pipetted_vol_ml / 1000.0)
        # Volume of NaOH needed to neutralise actual moles:
        actual_titre_needed = (actual_moles / self.naoh_conc_m) * 1000.0
        # Student uses nominal 25.00 mL in calculation formula:
        calc_m = (self.naoh_conc_m * actual_titre_needed) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0

        direction = ErrorDirection.LOWER if actual_pipetted_vol_ml < self.acid_vol_ml else ErrorDirection.HIGHER

        return ErrorSimulationOutcome(
            error_id="pipette_error",
            error_title="Incorrect Pipette Volume (Air Bubble / Incomplete Delivery)",
            parameter_description=f"Delivered {actual_pipetted_vol_ml:.2f} mL HCl instead of nominal 25.00 mL",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=round(actual_titre_needed, 2),
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=direction,
            chemical_mechanism=(
                "If an air bubble is drawn into the pipette or the pipette is not drained properly, "
                f"only {actual_pipetted_vol_ml:.2f} mL of acid is placed into the flask. The flask contains "
                "fewer moles of H+ than assumed. Consequently, less NaOH is required to reach the endpoint. "
                "When dividing this smaller titre by the assumed nominal 25.00 mL, the calculated HCl "
                "concentration is falsely LOW."
            ),
            prevention_protocol=(
                "Fill the pipette past the calibration line, wipe the exterior with clean tissue, "
                "slowly adjust the meniscus to the mark at eye level, and allow full gravity drainage "
                "touching the tip against the flask wall for 3 seconds without blowing out the tip."
            ),
        )

    def simulate_air_bubble_in_burette(self, bubble_volume_ml: float = 0.40) -> ErrorSimulationOutcome:
        """Simulate air bubble trapped below stopcock dislodging during titration."""
        sim_titre = self.ideal_titre_ml + bubble_volume_ml
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0

        return ErrorSimulationOutcome(
            error_id="air_bubble",
            error_title="Air Bubble in Burette Tip Dislodging",
            parameter_description=f"Air bubble of {bubble_volume_ml:.2f} mL flushed during titration",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=sim_titre,
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=ErrorDirection.HIGHER,
            chemical_mechanism=(
                "An air pocket trapped in the burette tip below the stopcock counts toward the initial "
                "liquid column height. When liquid flows, the bubble is expelled and replaced by titrant. "
                "The burette reading indicates a larger volume loss than the actual volume of NaOH delivered "
                "to the flask. This artificially high titre leads to a calculated HCl molarity that is falsely HIGH."
            ),
            prevention_protocol=(
                "Always flush the burette tip before recording the initial volume. Open the stopcock "
                "fully over a waste beaker to dislodge all air bubbles from the tip and ensure a solid "
                "column of liquid throughout."
            ),
        )

    def simulate_wet_flask_with_water(self, water_drops_ml: float = 5.0) -> ErrorSimulationOutcome:
        """Simulate deionised water remaining in the conical flask before acid addition."""
        # Moles of HCl pipetted into flask remain unchanged!
        # Total volume of liquid in flask increases, but stoichiometric moles remain unchanged!
        sim_titre = self.ideal_titre_ml
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = 0.0

        return ErrorSimulationOutcome(
            error_id="wet_flask",
            error_title="Deionised Water Drops in Conical Flask",
            parameter_description=f"Flask contains {water_drops_ml:.1f} mL residual deionised water",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=sim_titre,
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=0.0,
            direction=ErrorDirection.UNCHANGED,
            chemical_mechanism=(
                "Residual pure water in the receiving conical flask dilutes the concentration of the acid "
                "in the flask, but does NOT alter the total number of moles of H+ ions transferred from the pipette "
                f"(n = M_HCl * V_pipette = {self.true_hcl_m * 0.025:.5f} mol). Since neutralisation depends strictly "
                "on molar stoichiometry (mole for mole), the exact same volume of NaOH is required to neutralise "
                "all H+ ions. Thus, the calculated HCl concentration is UNCHANGED (100% accurate)!"
            ),
            prevention_protocol=(
                "Rinsing the conical flask with deionised water is completely acceptable and standard practice. "
                "Never rinse the conical flask with the acid sample, as this would introduce unmeasured extra moles."
            ),
        )

    def simulate_wet_burette_with_water(self, dilution_factor: float = 0.05) -> ErrorSimulationOutcome:
        """Simulate burette rinsed with water but not primed/rinsed with NaOH titrant."""
        # NaOH is diluted in the burette by residual water:
        actual_naoh_m = self.naoh_conc_m * (1.0 - dilution_factor)
        # Volume of this diluted titrant needed:
        moles_hcl = self.true_hcl_m * (self.acid_vol_ml / 1000.0)
        sim_titre = (moles_hcl / actual_naoh_m) * 1000.0
        # Student calculates using nominal 0.100 M NaOH:
        calc_m = (self.naoh_conc_m * sim_titre) / self.acid_vol_ml
        pct_err = ((calc_m - self.true_hcl_m) / self.true_hcl_m) * 100.0

        return ErrorSimulationOutcome(
            error_id="wet_burette",
            error_title="Burette Wet with Water (Not Rinsed with NaOH Titrant)",
            parameter_description=f"Residual water dilutes titrant by {dilution_factor * 100:.1f}%",
            ideal_titre_ml=self.ideal_titre_ml,
            simulated_titre_ml=round(sim_titre, 2),
            true_hcl_m=self.true_hcl_m,
            calculated_hcl_m=round(calc_m, 4),
            percentage_error=round(pct_err, 2),
            direction=ErrorDirection.HIGHER,
            chemical_mechanism=(
                "If the burette is wet with water and not primed with standard NaOH solution, the titrant "
                "is diluted inside the burette. Delivering the required moles of NaOH now demands a larger "
                "physical volume of titrant. Because the student assumes the nominal 0.100 M concentration in "
                "their formula, the inflated volume results in a calculated HCl concentration that is falsely HIGH."
            ),
            prevention_protocol=(
                "Always rinse the cleaned burette at least twice with small 5 mL portions of the standard "
                "NaOH solution, coating all inner walls and allowing it to drain through the tip, before filling."
            ),
        )

    def get_all_scenarios(self) -> List[ErrorSimulationOutcome]:
        """Return all standard simulated error scenarios."""
        return [
            self.simulate_overshoot(),
            self.simulate_undershoot(),
            self.simulate_reading_error(),
            self.simulate_pipette_error(),
            self.simulate_air_bubble_in_burette(),
            self.simulate_wet_flask_with_water(),
            self.simulate_wet_burette_with_water(),
        ]
