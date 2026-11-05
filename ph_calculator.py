"""Module 7 — pH Measurement and Chemical Calculation Engine.

Implements rigorous physical chemistry calculations for a strong acid (HCl)
titrated with a strong base (NaOH). Accounts for dilution, neutralisation stoichiometry,
water autoionisation equilibrium quadratic solutions, and numerical stability.
"""

import math
from dataclasses import dataclass
from typing import Optional
from config import (
    ACID_VOLUME_ML,
    TRUE_HCL_CONCENTRATION_M,
    NAOH_CONCENTRATION_M,
    WATER_KW,
    NEUTRAL_PH,
    calculate_theoretical_equivalence_volume,
)


@dataclass(frozen=True)
class TitrationState:
    """Immutable snapshot of the solution state at a specific titrant addition."""
    v_acid_ml: float
    m_acid_m: float
    v_base_ml: float
    m_base_m: float
    v_total_ml: float
    moles_acid_initial: float
    moles_base_added: float
    h_concentration: float      # [H+] in mol/L
    oh_concentration: float     # [OH-] in mol/L
    ph: float
    poh: float
    is_at_equivalence: bool
    condition_description: str  # Acidic, Neutral, Basic description
    equivalence_status: str     # Pre-equivalence, Equivalence, Post-equivalence


class PHCalculator:
    """Strong acid – strong base titration pH calculator with quadratic equilibrium."""

    def __init__(
        self,
        acid_vol_ml: float = ACID_VOLUME_ML,
        acid_conc_m: float = TRUE_HCL_CONCENTRATION_M,
        base_conc_m: float = NAOH_CONCENTRATION_M,
        kw: float = WATER_KW,
    ):
        if acid_vol_ml <= 0:
            raise ValueError("Acid volume must be strictly positive.")
        if acid_conc_m <= 0:
            raise ValueError("Acid concentration must be strictly positive.")
        if base_conc_m <= 0:
            raise ValueError("Base concentration must be strictly positive.")
            
        self.acid_vol_ml = acid_vol_ml
        self.acid_conc_m = acid_conc_m
        self.base_conc_m = base_conc_m
        self.kw = kw
        self.v_eq_ml = calculate_theoretical_equivalence_volume(
            acid_vol_ml=acid_vol_ml,
            acid_conc_m=acid_conc_m,
            base_conc_m=base_conc_m
        )

    def calculate_ph(self, v_base_ml: float) -> TitrationState:
        """Calculate exact pH, [H+], and [OH-] for a given dispensed volume of NaOH.
        
        Args:
            v_base_ml: Volume of NaOH titrant added in mL.
            
        Returns:
            TitrationState with all calculated physical and chemical properties.
        """
        if v_base_ml < 0:
            raise ValueError(f"Titrant volume cannot be negative: {v_base_ml} mL")

        v_acid_l = self.acid_vol_ml / 1000.0
        v_base_l = v_base_ml / 1000.0
        v_total_l = v_acid_l + v_base_l
        v_total_ml = self.acid_vol_ml + v_base_ml

        n_acid_init = self.acid_conc_m * v_acid_l
        n_base_added = self.base_conc_m * v_base_l

        delta_n = n_acid_init - n_base_added

        # Tolerance for numerical equivalence (within ~0.0001 mL of base)
        eq_tolerance_moles = 1e-11
        is_at_equivalence = abs(delta_n) < eq_tolerance_moles

        if is_at_equivalence:
            # At exact equivalence: only NaCl in water at 25 °C
            # [H+] = [OH-] = sqrt(Kw) = 1.0e-7 M
            h_conc = math.sqrt(self.kw)
            oh_conc = h_conc
            ph = NEUTRAL_PH
            poh = NEUTRAL_PH
            condition = "Neutral (pH = 7.00)"
            eq_status = "At Equivalence Point"

        elif delta_n > 0:
            # Pre-equivalence: excess strong acid HCl in solution
            excess_h_nominal = delta_n / v_total_l
            # Quadratic solution incorporating water dissociation equilibrium:
            # [H+]^2 - [H+]_excess * [H+] - Kw = 0  =>  [H+] = (excess + sqrt(excess^2 + 4*Kw)) / 2
            h_conc = (excess_h_nominal + math.sqrt(excess_h_nominal**2 + 4 * self.kw)) / 2.0
            oh_conc = self.kw / h_conc
            ph = -math.log10(h_conc)
            poh = 14.00 - ph

            if ph < 3.0:
                condition = "Strongly Acidic"
            elif ph < 6.0:
                condition = "Moderately Acidic"
            else:
                condition = "Weakly Acidic (Near Equivalence)"
            eq_status = "Before Equivalence"

        else:
            # Post-equivalence: excess strong base NaOH in solution
            excess_oh_nominal = (-delta_n) / v_total_l
            # Quadratic solution for [OH-]:
            oh_conc = (excess_oh_nominal + math.sqrt(excess_oh_nominal**2 + 4 * self.kw)) / 2.0
            h_conc = self.kw / oh_conc
            poh = -math.log10(oh_conc)
            ph = 14.00 - poh

            if ph > 11.0:
                condition = "Strongly Basic (Over-titrated)"
            elif ph > 8.5:
                condition = "Moderately Basic (Post-endpoint)"
            else:
                condition = "Weakly Basic (Immediately Past Equivalence)"
            eq_status = "After Equivalence"

        return TitrationState(
            v_acid_ml=self.acid_vol_ml,
            m_acid_m=self.acid_conc_m,
            v_base_ml=v_base_ml,
            m_base_m=self.base_conc_m,
            v_total_ml=v_total_ml,
            moles_acid_initial=n_acid_init,
            moles_base_added=n_base_added,
            h_concentration=h_conc,
            oh_concentration=oh_conc,
            ph=round(ph, 4),
            poh=round(poh, 4),
            is_at_equivalence=is_at_equivalence,
            condition_description=condition,
            equivalence_status=eq_status,
        )

    def generate_curve_data(self, v_max_ml: float = 35.0, step_ml: float = 0.1):
        """Generate high-resolution (volume, pH) points for plotting."""
        volumes = []
        phs = []
        current_v = 0.0
        while current_v <= v_max_ml:
            state = self.calculate_ph(current_v)
            volumes.append(current_v)
            phs.append(state.ph)
            # Denser sampling near equivalence (22.0 to 23.0 mL)
            if 22.0 <= current_v <= 23.0:
                current_v = round(current_v + min(step_ml, 0.02), 4)
            else:
                current_v = round(current_v + step_ml, 4)
        return volumes, phs
