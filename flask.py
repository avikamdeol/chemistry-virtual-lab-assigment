"""Module 5 — Pipette and Conical Flask Simulation.

Models the transfer of the 25.00 mL unknown HCl acid aliquot into an Erlenmeyer
conical flask, addition of phenolphthalein indicator, and mixing with NaOH titrant.
Maintains chemical inventory of all ionic species (H+, Cl-, Na+, OH-, H2O) and
drives liquid volume and color state for the visual apparatus display.
"""

from dataclasses import dataclass
from typing import Optional, Dict
from config import (
    ACID_VOLUME_ML,
    TRUE_HCL_CONCENTRATION_M,
    NAOH_CONCENTRATION_M,
    THEME,
)
from ph_calculator import PHCalculator, TitrationState
from indicator import PhenolphthaleinIndicator, IndicatorObservation


@dataclass(frozen=True)
class FlaskContentsSnapshot:
    """Snapshot of chemical and physical inventory inside the conical flask."""
    hcl_transferred_ml: float
    naoh_added_ml: float
    total_volume_ml: float
    has_acid: bool
    has_indicator: bool
    indicator_drops: int
    ph: float
    color_hex: str
    color_name: str
    is_swirled: bool
    moles_h_ions: float
    moles_oh_ions: float
    moles_na_ions: float
    moles_cl_ions: float
    status_text: str


class ConicalFlask:
    """Erlenmeyer titration flask receiving acid, indicator, and titrant."""

    def __init__(
        self,
        true_hcl_conc_m: float = TRUE_HCL_CONCENTRATION_M,
        naoh_conc_m: float = NAOH_CONCENTRATION_M,
    ):
        self.true_hcl_conc_m = true_hcl_conc_m
        self.naoh_conc_m = naoh_conc_m
        self.ph_calc = PHCalculator(
            acid_vol_ml=ACID_VOLUME_ML,
            acid_conc_m=true_hcl_conc_m,
            base_conc_m=naoh_conc_m,
        )
        self.indicator = PhenolphthaleinIndicator()

        # Operational state
        self.hcl_volume_ml: float = 0.00
        self.naoh_added_ml: float = 0.00
        self.has_acid: bool = False
        self.is_swirled: bool = True
        self.current_ph: float = 7.00  # pure deionised water before acid transfer

    def pipette_hcl_sample(self, volume_ml: float = ACID_VOLUME_ML) -> None:
        """Transfer calibrated volume of unknown HCl into the flask via pipette."""
        if volume_ml <= 0:
            raise ValueError("Pipetted volume must be strictly positive.")
        self.hcl_volume_ml = volume_ml
        self.has_acid = True
        # Calculate initial acid pH with 0 base added
        state = self.ph_calc.calculate_ph(0.0)
        self.current_ph = state.ph
        self.is_swirled = True

    def add_indicator(self, drops: int = 2) -> None:
        """Add drops of phenolphthalein indicator to the flask."""
        self.indicator.add_drops(drops)

    def receive_naoh(self, volume_ml: float) -> None:
        """Receive an aliquot of NaOH titrant from the burette."""
        if not self.has_acid:
            raise RuntimeError(
                "Cannot titrate: Conical flask is empty! Pipette 25.00 mL HCl into the flask first."
            )
        if volume_ml < 0:
            raise ValueError(f"Received volume cannot be negative: {volume_ml} mL")

        self.naoh_added_ml = round(self.naoh_added_ml + volume_ml, 4)
        state = self.ph_calc.calculate_ph(self.naoh_added_ml)
        self.current_ph = state.ph
        self.is_swirled = True

    def swirl(self) -> None:
        """Swirl the conical flask to ensure complete homogenisation."""
        self.is_swirled = True

    def get_snapshot(self) -> FlaskContentsSnapshot:
        """Get complete physical, chemical, and visual inventory of the flask."""
        total_vol = self.hcl_volume_ml + self.naoh_added_ml
        obs = self.indicator.evaluate(self.current_ph, swirled=self.is_swirled)

        if not self.has_acid:
            moles_cl = 0.0
            moles_h = 0.0
            moles_na = 0.0
            moles_oh = 0.0
            status = "Empty Clean Flask (Ready for Acid Pipetting)"
            color_hex = THEME.LIQUID_HCL_CLEAR
            color_name = "Empty"
        else:
            v_acid_l = self.hcl_volume_ml / 1000.0
            v_naoh_l = self.naoh_added_ml / 1000.0
            moles_cl = self.true_hcl_conc_m * v_acid_l
            moles_na = self.naoh_conc_m * v_naoh_l

            state = self.ph_calc.calculate_ph(self.naoh_added_ml)
            v_tot_l = (self.hcl_volume_ml + self.naoh_added_ml) / 1000.0
            moles_h = state.h_concentration * v_tot_l
            moles_oh = state.oh_concentration * v_tot_l

            color_hex = obs.color_hex
            color_name = obs.color_name
            status = f"{obs.persistence_status} | pH {self.current_ph:.2f}"

        return FlaskContentsSnapshot(
            hcl_transferred_ml=round(self.hcl_volume_ml, 2),
            naoh_added_ml=round(self.naoh_added_ml, 2),
            total_volume_ml=round(total_vol, 2),
            has_acid=self.has_acid,
            has_indicator=self.indicator.drops_added > 0,
            indicator_drops=self.indicator.drops_added,
            ph=round(self.current_ph, 2),
            color_hex=color_hex,
            color_name=color_name,
            is_swirled=self.is_swirled,
            moles_h_ions=moles_h,
            moles_oh_ions=moles_oh,
            moles_na_ions=moles_na,
            moles_cl_ions=moles_cl,
            status_text=status,
        )

    def reset(self) -> None:
        """Reset flask contents for a fresh trial."""
        self.hcl_volume_ml = 0.00
        self.naoh_added_ml = 0.00
        self.has_acid = False
        self.is_swirled = True
        self.current_ph = 7.00
        self.indicator.reset()
