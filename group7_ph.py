# Group 7 - pH measurement
# HCl-NaOH titration virtual lab (strong acid - strong base)
#
# Idea used here:
#   HCl + NaOH -> NaCl + H2O   (1:1 ratio)
#   Before equivalence : some HCl is left over, so the solution is acidic
#   At equivalence     : no HCl and no NaOH left, pH = 7 (at 25 C)
#   After equivalence  : some NaOH is left over, so the solution is basic
#
# Units: volume in mL, molarity in mol/L.
# Tip: mL x mol/L = millimoles (mmol), so we can skip converting to litres.

import math

# ---------- experiment values from the assignment ----------
ACID_VOLUME_ML = 25.00      # HCl in the flask
ACID_MOLARITY = 0.0900      # true HCl concentration in the simulation
BASE_MOLARITY = 0.100       # NaOH in the burette
EQUIVALENCE_VOLUME_ML = 22.50   # theoretical equivalence volume


def calculate_ph(naoh_volume_ml,
                 acid_volume_ml=ACID_VOLUME_ML,
                 acid_molarity=ACID_MOLARITY,
                 base_molarity=BASE_MOLARITY):
    """Return the pH after adding naoh_volume_ml of NaOH to the flask."""

    # handle wrong inputs
    try:
        naoh_volume_ml = float(naoh_volume_ml)
    except (TypeError, ValueError):
        raise ValueError("Volume must be a number.")
    if math.isnan(naoh_volume_ml) or math.isinf(naoh_volume_ml):
        raise ValueError("Volume must be a real number.")
    if naoh_volume_ml < 0:
        raise ValueError("Volume cannot be negative.")

    acid_mmol = acid_volume_ml * acid_molarity
    base_mmol = naoh_volume_ml * base_molarity
    total_volume_ml = acid_volume_ml + naoh_volume_ml

    difference = acid_mmol - base_mmol

    # equivalence point (tiny tolerance because of decimal rounding)
    if abs(difference) < 1e-9:
        return 7.0

    # acid left over -> pH from H+ concentration
    if difference > 0:
        h_concentration = difference / total_volume_ml
        return -math.log10(h_concentration)

    # base left over -> pOH from OH- concentration, then pH = 14 - pOH
    oh_concentration = (-difference) / total_volume_ml
    poh = -math.log10(oh_concentration)
    return 14 - poh


def get_stage(naoh_volume_ml,
              acid_volume_ml=ACID_VOLUME_ML,
              acid_molarity=ACID_MOLARITY,
              base_molarity=BASE_MOLARITY):
    """Tell which part of the titration we are in."""
    acid_mmol = acid_volume_ml * acid_molarity
    base_mmol = naoh_volume_ml * base_molarity
    difference = acid_mmol - base_mmol

    if abs(difference) < 1e-9:
        return "Equivalence point"
    if difference > 0:
        return "Before equivalence (acid left)"
    return "After equivalence (base left)"


def get_nature(ph):
    """Say if the solution is acidic, neutral or basic."""
    if ph < 6.99:
        return "Acidic"
    if ph > 7.01:
        return "Basic"
    return "Neutral"


def run_tests():
    """Small checks with answers worked out by hand."""
    tests = [
        (0.0, 1.046),     # only 0.0900 M HCl -> -log(0.09)
        (10.0, 1.447),    # 1.25 mmol HCl left in 35 mL
        (22.5, 7.000),    # equivalence point
        (25.0, 11.699),   # 0.25 mmol NaOH extra in 50 mL
    ]
    print("Running test cases...")
    all_passed = True
    for volume, expected in tests:
        answer = calculate_ph(volume)
        passed = abs(answer - expected) < 0.001
        if not passed:
            all_passed = False
        status = "PASS" if passed else "FAIL"
        print(f"  V = {volume:5.2f} mL | expected {expected:6.3f} | got {answer:6.3f} | {status}")

    # negative volume should give an error
    try:
        calculate_ph(-1)
        print("  Negative volume test: FAIL")
        all_passed = False
    except ValueError:
        print("  Negative volume test: PASS (error caught)")

    # text instead of number should give an error
    try:
        calculate_ph("abc")
        print("  Text input test     : FAIL")
        all_passed = False
    except ValueError:
        print("  Text input test     : PASS (error caught)")

    print("All tests passed!\n" if all_passed else "Some tests failed.\n")


def show_table():
    """Print pH at different NaOH volumes."""
    volumes = [0, 5, 10, 15, 20, 22, 22.4, 22.5, 22.6, 23, 25, 30, 35, 40]

    print("=" * 62)
    print("  HCl - NaOH TITRATION : pH TABLE")
    print("  Flask: 25.00 mL HCl (0.0900 M)   Burette: 0.100 M NaOH")
    print("=" * 62)
    print(f"{'NaOH (mL)':<12}{'pH':<10}{'Nature':<10}Stage")
    print("-" * 62)
    for v in volumes:
        ph = calculate_ph(v)
        print(f"{v:<12.2f}{ph:<10.3f}{get_nature(ph):<10}{get_stage(v)}")
    print("-" * 62)
    print(f"Theoretical equivalence volume = {EQUIVALENCE_VOLUME_ML} mL\n")


def ask_user():
    """Let the user type a volume and get the pH."""
    print("Type a NaOH volume in mL to get its pH (type q to quit).")
    while True:
        text = input("NaOH volume (mL): ").strip()
        if text.lower() == "q":
            print("Bye!")
            break
        try:
            ph = calculate_ph(text)
        except ValueError as error:
            print("  Error:", error)
            continue
        volume = float(text)
        print(f"  pH = {ph:.3f}  |  {get_nature(ph)}  |  {get_stage(volume)}")


# This part runs only when you run this file directly,
# so other groups can import the functions without the output.
if __name__ == "__main__":
    run_tests()
    show_table()
    ask_user()
