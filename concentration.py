"""Module 11 — HCl Concentration and Quantitative Stoichiometry.

Implements analytical determination of unknown HCl molarity and mass concentration
from experimental titration titre results using volumetric law:
    M_HCl * V_HCl = M_NaOH * V_NaOH
    M_HCl = (M_NaOH * V_NaOH) / V_HCl

Calculates:
1. Molarity (mol/L)
2. Mass concentration (g/L) using molar mass 36.46 g/mol
3. Relative percentage error against true reference value (0.0900 M)
Provides rigorous educational step-by-step explanations for university students.
"""

from dataclasses import dataclass
from typing import Optional
from config import (
    ACID_VOLUME_ML,
    NAOH_CONCENTRATION_M,
    TRUE_HCL_CONCENTRATION_M,
    MOLAR_MASS_HCL,
    STOICHIOMETRIC_RATIO,
)


@dataclass(frozen=True)
class ConcentrationResult:
    """Detailed quantitative outcome of HCl concentration determination."""
    titre_volume_ml: float
    acid_volume_ml: float
    naoh_molarity_m: float
    calculated_hcl_molarity_m: float
    calculated_hcl_conc_g_per_l: float
    reference_hcl_molarity_m: float
    reference_hcl_conc_g_per_l: float
    absolute_error_m: float
    percentage_error: float
    is_accurate_within_tolerance: bool
    step_by_step_derivation: str


class ConcentrationCalculator:
    """Quantitative titrimetric calculation engine for unknown HCl sample."""

    def __init__(
        self,
        acid_vol_ml: float = ACID_VOLUME_ML,
        naoh_conc_m: float = NAOH_CONCENTRATION_M,
        reference_hcl_m: float = TRUE_HCL_CONCENTRATION_M,
        molar_mass_hcl: float = MOLAR_MASS_HCL,
        stoich_ratio: float = STOICHIOMETRIC_RATIO,
    ):
        if acid_vol_ml <= 0:
            raise ValueError("Acid sample volume must be strictly positive.")
        if naoh_conc_m <= 0:
            raise ValueError("NaOH titrant concentration must be strictly positive.")
            
        self.acid_vol_ml = acid_vol_ml
        self.naoh_conc_m = naoh_conc_m
        self.reference_hcl_m = reference_hcl_m
        self.molar_mass_hcl = molar_mass_hcl
        self.stoich_ratio = stoich_ratio

    def calculate(self, mean_titre_ml: float) -> ConcentrationResult:
        """Calculate HCl concentration in mol/L, g/L, and percentage error.
        
        Args:
            mean_titre_ml: Concordant mean titre volume of NaOH dispensed in mL.
        """
        if mean_titre_ml <= 0:
            raise ValueError(f"Titre volume must be strictly positive: {mean_titre_ml} mL")

        # M_HCl * V_HCl = M_NaOH * V_NaOH
        # M_HCl = (M_NaOH * V_NaOH) / V_HCl (for 1:1 reaction)
        calc_molarity = (self.naoh_conc_m * mean_titre_ml * self.stoich_ratio) / self.acid_vol_ml
        calc_conc_g_l = calc_molarity * self.molar_mass_hcl

        ref_conc_g_l = self.reference_hcl_m * self.molar_mass_hcl
        abs_error_m = abs(calc_molarity - self.reference_hcl_m)
        pct_error = (abs_error_m / self.reference_hcl_m) * 100.0

        # High accuracy benchmark: within 1.0% error
        is_accurate = pct_error <= 1.0

        derivation = (
            f"=== STEP-BY-STEP STOICHIOMETRIC CONCENTRATION DETERMINATION ===\n"
            f"1. Balanced Chemical Reaction:\n"
            f"   HCl (aq) + NaOH (aq) -> NaCl (aq) + H2O (l)\n"
            f"   Stoichiometric molar ratio: n(HCl) : n(NaOH) = 1 : 1\n\n"
            f"2. Experimental Parameters:\n"
            f"   - Volume of HCl pipetted (V_HCl) = {self.acid_vol_ml:.2f} mL\n"
            f"   - Standard NaOH Molarity (M_NaOH) = {self.naoh_conc_m:.4f} M\n"
            f"   - Mean Titre Volume of NaOH (V_NaOH) = {mean_titre_ml:.2f} mL\n\n"
            f"3. Neutralisation Formula:\n"
            f"   M_HCl x V_HCl = M_NaOH x V_NaOH\n"
            f"   M_HCl = (M_NaOH x V_NaOH) / V_HCl\n\n"
            f"4. Numerical Substitution:\n"
            f"   M_HCl = ({self.naoh_conc_m:.4f} mol/L x {mean_titre_ml:.2f} mL) / {self.acid_vol_ml:.2f} mL\n"
            f"   M_HCl = {calc_molarity:.4f} mol/L (M)\n\n"
            f"5. Mass Concentration (Strength in g/L):\n"
            f"   Strength (g/L) = Molarity (mol/L) x Molar Mass of HCl ({self.molar_mass_hcl:.2f} g/mol)\n"
            f"   Strength = {calc_molarity:.4f} mol/L x {self.molar_mass_hcl:.2f} g/mol\n"
            f"            = {calc_conc_g_l:.2f} g/L (exact: {calc_conc_g_l:.4f} g/L)\n\n"
            f"6. Accuracy and Experimental Error:\n"
            f"   - Simulation True Reference Molarity = {self.reference_hcl_m:.4f} M\n"
            f"   - Simulation True Strength           = {ref_conc_g_l:.2f} g/L\n"
            f"   - Absolute Error (|M_calc - M_true|) = {abs_error_m:.6f} M\n"
            f"   - Percentage Error = (|M_calc - M_true| / M_true) x 100%\n"
            f"                      = ({abs_error_m:.6f} / {self.reference_hcl_m:.4f}) x 100%\n"
            f"                      = {pct_error:.2f}%\n"
        )

        return ConcentrationResult(
            titre_volume_ml=mean_titre_ml,
            acid_volume_ml=self.acid_vol_ml,
            naoh_molarity_m=self.naoh_conc_m,
            calculated_hcl_molarity_m=round(calc_molarity, 6),
            calculated_hcl_conc_g_per_l=round(calc_conc_g_l, 4),
            reference_hcl_molarity_m=self.reference_hcl_m,
            reference_hcl_conc_g_per_l=round(ref_conc_g_l, 4),
            absolute_error_m=round(abs_error_m, 6),
            percentage_error=round(pct_error, 2),
            is_accurate_within_tolerance=is_accurate,
            step_by_step_derivation=derivation,
        )
