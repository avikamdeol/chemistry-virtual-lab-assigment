"""Module 3 — Solution Preparation Calculator.

Provides exact chemical stoichiometry and dilution calculations:
1. Solid NaOH dissolution calculation:
   Mass (g) = Molarity (mol/L) * Volume (L) * Molar Mass (g/mol)
2. Stock solution dilution calculation:
   M1 * V1 = M2 * V2  =>  V1 = (M2 * V2) / M1

Includes comprehensive step-by-step mathematical explanations, unit handling,
and validation against invalid/negative inputs.
"""

from dataclasses import dataclass
from typing import Optional
from config import MOLAR_MASS_NAOH


@dataclass(frozen=True)
class SolidPrepResult:
    """Detailed result of solid NaOH solution preparation calculation."""
    desired_molarity_m: float
    desired_volume_ml: float
    desired_volume_l: float
    molar_mass_g_mol: float
    required_moles: float
    required_mass_g: float
    step_by_step_explanation: str


@dataclass(frozen=True)
class DilutionResult:
    """Detailed result of stock solution dilution calculation."""
    stock_molarity_m: float
    target_molarity_m: float
    target_volume_ml: float
    target_volume_l: float
    required_stock_volume_ml: float
    diluent_volume_water_ml: float
    dilution_factor: float
    step_by_step_explanation: str


class SolutionPreparationCalculator:
    """Chemical preparation calculator for solutions and dilutions."""

    def __init__(self, molar_mass_naoh: float = MOLAR_MASS_NAOH):
        self.molar_mass_naoh = molar_mass_naoh

    def calculate_solid_naoh_mass(
        self,
        target_molarity_m: float,
        target_volume_ml: float,
    ) -> SolidPrepResult:
        """Calculate mass of solid NaOH pellets needed to prepare target solution.
        
        Formula:
            Mass (g) = Molarity (mol/L) * Volume (L) * Molar Mass (g/mol)
        """
        if target_molarity_m <= 0:
            raise ValueError("Target molarity must be strictly positive.")
        if target_volume_ml <= 0:
            raise ValueError("Target volume must be strictly positive.")

        target_volume_l = target_volume_ml / 1000.0
        moles_needed = target_molarity_m * target_volume_l
        mass_g = moles_needed * self.molar_mass_naoh

        explanation = (
            f"=== STEP-BY-STEP CALCULATION: SOLID NaOH PREPARATION ===\n"
            f"1. Target Parameters:\n"
            f"   - Target Molarity (M) = {target_molarity_m:.4f} mol/L\n"
            f"   - Target Volume (V)   = {target_volume_ml:.2f} mL = {target_volume_l:.4f} L\n"
            f"   - Molar Mass of NaOH  = {self.molar_mass_naoh:.2f} g/mol\n\n"
            f"2. Chemical Formula:\n"
            f"   Mass (g) = Molarity (mol/L) x Volume (L) x Molar Mass (g/mol)\n\n"
            f"3. Substitution:\n"
            f"   Moles required = {target_molarity_m:.4f} mol/L x {target_volume_l:.4f} L\n"
            f"                  = {moles_needed:.6f} moles of NaOH\n\n"
            f"   Mass = {moles_needed:.6f} mol x {self.molar_mass_naoh:.2f} g/mol\n"
            f"        = {mass_g:.4f} g\n\n"
            f"4. Laboratory Procedure:\n"
            f"   - Weigh exactly {mass_g:.4f} g of analytical-grade NaOH pellets on a balance.\n"
            f"   - Dissolve pellets in ~{target_volume_ml * 0.6:.1f} mL deionised water in a beaker (exothermic!).\n"
            f"   - Allow solution to cool to 25 °C.\n"
            f"   - Transfer quantitatively to a {target_volume_ml:.1f} mL volumetric flask.\n"
            f"   - Make up to the calibration mark with deionised water and invert 10 times to mix."
        )

        return SolidPrepResult(
            desired_molarity_m=target_molarity_m,
            desired_volume_ml=target_volume_ml,
            desired_volume_l=target_volume_l,
            molar_mass_g_mol=self.molar_mass_naoh,
            required_moles=round(moles_needed, 6),
            required_mass_g=round(mass_g, 4),
            step_by_step_explanation=explanation,
        )

    def calculate_dilution(
        self,
        stock_molarity_m: float,
        target_molarity_m: float,
        target_volume_ml: float,
    ) -> DilutionResult:
        """Calculate volume of concentrated stock solution required for dilution.
        
        Formula:
            M1 * V1 = M2 * V2  =>  V1 = (M2 * V2) / M1
        """
        if stock_molarity_m <= 0:
            raise ValueError("Stock molarity must be strictly positive.")
        if target_molarity_m <= 0:
            raise ValueError("Target molarity must be strictly positive.")
        if target_volume_ml <= 0:
            raise ValueError("Target volume must be strictly positive.")
        if target_molarity_m > stock_molarity_m:
            raise ValueError(
                f"Target molarity ({target_molarity_m} M) cannot exceed "
                f"stock molarity ({stock_molarity_m} M)."
            )

        target_volume_l = target_volume_ml / 1000.0
        # V1 = (M2 * V2) / M1
        v_stock_ml = (target_molarity_m * target_volume_ml) / stock_molarity_m
        v_water_ml = target_volume_ml - v_stock_ml
        dilution_factor = stock_molarity_m / target_molarity_m

        explanation = (
            f"=== STEP-BY-STEP CALCULATION: STOCK DILUTION ===\n"
            f"1. Input Parameters:\n"
            f"   - Stock Concentration (M1) = {stock_molarity_m:.4f} M\n"
            f"   - Target Concentration (M2)= {target_molarity_m:.4f} M\n"
            f"   - Target Total Volume (V2) = {target_volume_ml:.2f} mL\n\n"
            f"2. Dilution Law:\n"
            f"   M1 x V1 = M2 x V2\n"
            f"   V1 = (M2 x V2) / M1\n\n"
            f"3. Substitution:\n"
            f"   V1 = ({target_molarity_m:.4f} M x {target_volume_ml:.2f} mL) / {stock_molarity_m:.4f} M\n"
            f"   V1 = {v_stock_ml:.4f} mL of Stock Solution\n"
            f"   Diluent Water Volume = {target_volume_ml:.2f} mL - {v_stock_ml:.2f} mL = {v_water_ml:.2f} mL\n"
            f"   Dilution Factor = {dilution_factor:.2f}x\n\n"
            f"4. Laboratory Procedure:\n"
            f"   - Pipette {v_stock_ml:.2f} mL of {stock_molarity_m:.4f} M stock solution.\n"
            f"   - Transfer to a {target_volume_ml:.1f} mL volumetric flask.\n"
            f"   - Add deionised water up to the calibration mark ({v_water_ml:.2f} mL added).\n"
            f"   - Stopper and invert to homogenise."
        )

        return DilutionResult(
            stock_molarity_m=stock_molarity_m,
            target_molarity_m=target_molarity_m,
            target_volume_ml=target_volume_ml,
            target_volume_l=target_volume_l,
            required_stock_volume_ml=round(v_stock_ml, 4),
            diluent_volume_water_ml=round(v_water_ml, 4),
            dilution_factor=round(dilution_factor, 2),
            step_by_step_explanation=explanation,
        )
