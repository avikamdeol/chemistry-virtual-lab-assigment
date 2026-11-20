"""
group11_hcl_concentration.py
============================
HCl-NaOH Titration Virtual Lab  |  Group 11 : HCl Concentration

Purpose
-------
Use the experimental (mean) titre of NaOH and the 1:1 reaction
stoichiometry to determine the unknown HCl concentration, then report it
in mol/L and g/L together with the percentage error relative to the
simulation's reference value.

Chemistry
---------
    HCl + NaOH -> NaCl + H2O            (1 : 1 mole ratio)
    At the end point:   M_acid x V_acid = M_base x V_base
    Hence:              M_acid = (M_base x V_base) / V_acid

Only the Python standard library is used.
"""

# --------------------------------------------------------------------------
# 1. Experimental constants (taken from the assignment sheet)
# --------------------------------------------------------------------------
ACID_VOLUME_ML = 25.00            # volume of HCl in the flask (mL)
BASE_MOLARITY = 0.100             # standard NaOH in the burette (mol/L)
TRUE_HCL_MOLARITY = 0.0900        # simulation reference value (mol/L)
HCL_MOLAR_MASS = 36.46            # g/mol  (H = 1.008, Cl = 35.45)
MOLE_RATIO_ACID_TO_BASE = 1       # HCl : NaOH = 1 : 1


# --------------------------------------------------------------------------
# 2. Input validation
# --------------------------------------------------------------------------
def _validate_positive(value, name):
    """Return value as float if it is a positive, finite number; else raise."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}.")
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be a finite number.")
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero (got {value}).")
    return float(value)


# --------------------------------------------------------------------------
# 3. Core calculations
# --------------------------------------------------------------------------
def calculate_hcl_concentration(mean_titre_ml,
                                acid_volume_ml=ACID_VOLUME_ML,
                                base_molarity=BASE_MOLARITY):
    """Return the HCl concentration in mol/L from the mean NaOH titre (mL)."""
    titre = _validate_positive(mean_titre_ml, "Mean titre (mL)")
    v_acid = _validate_positive(acid_volume_ml, "Acid volume (mL)")
    m_base = _validate_positive(base_molarity, "Base molarity (mol/L)")
    moles_naoh = m_base * titre / 1000.0                  # mol
    moles_hcl = moles_naoh * MOLE_RATIO_ACID_TO_BASE      # 1:1 ratio
    return moles_hcl / (v_acid / 1000.0)                  # mol/L


def molarity_to_grams_per_litre(molarity, molar_mass=HCL_MOLAR_MASS):
    """Convert a concentration from mol/L to g/L."""
    return _validate_positive(molarity, "Molarity (mol/L)") * molar_mass


def percentage_error(experimental, reference=TRUE_HCL_MOLARITY):
    """Signed percentage error = (experimental - reference) / reference x 100."""
    ref = _validate_positive(reference, "Reference value")
    return (float(experimental) - ref) / ref * 100.0


def interpret_error(error_percent, tolerance=1.0):
    """Give a short verbal verdict on the percentage error."""
    if abs(error_percent) <= tolerance:
        return "Excellent agreement (within +/-{:.1f} %).".format(tolerance)
    direction = "higher" if error_percent > 0 else "lower"
    return "Result is {} than the true value; check for experimental error."\
        .format(direction)


# --------------------------------------------------------------------------
# 4. Main analysis function (the one Group 13 will call)
# --------------------------------------------------------------------------
def analyse_hcl_concentration(mean_titre_ml):
    """Run the full Group 11 analysis and return the results as a dictionary."""
    conc_mol_l = calculate_hcl_concentration(mean_titre_ml)
    conc_g_l = molarity_to_grams_per_litre(conc_mol_l)
    error = round(percentage_error(conc_mol_l), 10) + 0.0   # avoids '-0.00'
    return {
        "mean_titre_ml": float(mean_titre_ml),
        "acid_volume_ml": ACID_VOLUME_ML,
        "base_molarity": BASE_MOLARITY,
        "hcl_mol_per_l": conc_mol_l,
        "hcl_g_per_l": conc_g_l,
        "true_mol_per_l": TRUE_HCL_MOLARITY,
        "percentage_error": error,
        "verdict": interpret_error(error),
    }


# --------------------------------------------------------------------------
# 5. Display
# --------------------------------------------------------------------------
def display_results(results):
    """Print a neat, readable result summary."""
    line = "=" * 56
    print(line)
    print("  HCl CONCENTRATION  -  RESULT (Group 11)")
    print(line)
    print("  Reaction            : HCl + NaOH -> NaCl + H2O (1:1)")
    print(f"  Volume of HCl       : {results['acid_volume_ml']:.2f} mL")
    print(f"  Molarity of NaOH    : {results['base_molarity']:.3f} mol/L")
    print(f"  Mean titre of NaOH  : {results['mean_titre_ml']:.2f} mL")
    print("-" * 56)
    print(f"  HCl concentration   : {results['hcl_mol_per_l']:.4f} mol/L")
    print(f"  HCl concentration   : {results['hcl_g_per_l']:.3f} g/L")
    print(f"  Reference value     : {results['true_mol_per_l']:.4f} mol/L")
    print(f"  Percentage error    : {results['percentage_error']:+.2f} %")
    print(f"  Verdict             : {results['verdict']}")
    print(line)


# --------------------------------------------------------------------------
# 6. Stand-alone run
# --------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        entered = float(input("Enter the mean titre of NaOH (mL): "))
        display_results(analyse_hcl_concentration(entered))
    except (ValueError, TypeError) as err:
        print(f"Invalid input: {err}")
