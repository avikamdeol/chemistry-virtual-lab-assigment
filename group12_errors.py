"""
Group 12 - Experimental Error Simulation
HCl-NaOH titration virtual lab (phenolphthalein indicator)

Idea: every error changes ONE thing in the experiment (the real NaOH
strength, the real acid volume, or the burette reading). The student then
calculates HCl concentration the normal way, using the NOMINAL values
(0.100 M NaOH, 25.00 mL acid). Comparing with the true 0.0900 M shows
whether the error gives a HIGH, LOW or NO-CHANGE result.

    M HCl = (M NaOH x V titre) / V acid
"""

# constants from the assignment
TRUE_HCL_M = 0.0900       # true concentration (simulation reference)
NOMINAL_NAOH_M = 0.100    # label value of the burette solution
NOMINAL_ACID_ML = 25.00   # pipetted acid volume
HCL_MOLAR_MASS = 36.46    # g/mol
TOLERANCE = 1e-4          # |difference| below this => "no change"


# core calculations
def true_titre(acid_conc, acid_vol, naoh_conc):
    """Volume of NaOH (mL) that truly neutralises the acid (1:1)."""
    return acid_conc * acid_vol / naoh_conc


def calculate_hcl(titre_ml, naoh_conc=NOMINAL_NAOH_M, acid_vol=NOMINAL_ACID_ML):
    """Student's calculation: M_HCl = M_NaOH * V_NaOH / V_HCl (mol/L)."""
    return naoh_conc * titre_ml / acid_vol


def percent_error(value, reference=TRUE_HCL_M):
    return (value - reference) / reference * 100


def classify(calculated, reference=TRUE_HCL_M):
    diff = calculated - reference
    if abs(diff) < TOLERANCE:
        return "NO CHANGE"
    return "HIGH" if diff > 0 else "LOW"


#error scenarios
# Each scenario changes real conditions:
#   naoh_factor  : real NaOH strength / nominal strength
#   acid_factor  : real acid volume delivered / 25.00 mL
#   reading_shift: mL added to (+) or removed from (-) the recorded titre
ERRORS = {
    "1": {
        "name": "Air bubble in burette tip (expelled during titration)",
        "naoh_factor": 1.00, "acid_factor": 1.00, "reading_shift": +0.40,
        "why": "The bubble is counted as liquid volume on the scale, so the "
               "recorded titre is larger than the NaOH really delivered.",
    },
    "2": {
        "name": "Burette not rinsed with NaOH (water droplets inside)",
        "naoh_factor": 0.98, "acid_factor": 1.00, "reading_shift": 0.0,
        "why": "NaOH is diluted, so more volume is needed to neutralise the "
               "acid. Titre rises, but the calculation still uses 0.100 M.",
    },
    "3": {
        "name": "Overshooting the endpoint (dark pink)",
        "naoh_factor": 1.00, "acid_factor": 1.00, "reading_shift": +0.30,
        "why": "Extra NaOH beyond the equivalence point is recorded as titre.",
    },
    "4": {
        "name": "Stopping before the pink colour appears (undershoot)",
        "naoh_factor": 1.00, "acid_factor": 1.00, "reading_shift": -0.30,
        "why": "Titration stopped before all acid was neutralised, so titre "
               "is too small.",
    },
    "5": {
        "name": "Pipette rinsed with water, not with acid",
        "naoh_factor": 1.00, "acid_factor": 0.98, "reading_shift": 0.0,
        "why": "Water in the pipette dilutes the sample, so less HCl is "
               "delivered and less NaOH is needed.",
    },
    "6": {
        "name": "Conical flask rinsed with distilled water",
        "naoh_factor": 1.00, "acid_factor": 1.00, "reading_shift": 0.0,
        "why": "Extra water does not change the moles of HCl, so the titre "
               "is unchanged. This rinse is allowed.",
    },
    "7": {
        "name": "Too much phenolphthalein indicator",
        "naoh_factor": 1.00, "acid_factor": 1.00, "reading_shift": +0.05,
        "why": "Phenolphthalein is a weak acid and itself consumes a little "
               "NaOH, slightly raising the titre.",
    },
}


def simulate_error(key):
    """Run one error scenario and return a result dictionary."""
    e = ERRORS[key]
    naoh_real = NOMINAL_NAOH_M * e["naoh_factor"]
    acid_real = NOMINAL_ACID_ML * e["acid_factor"]

    # what the chemistry really requires
    needed = true_titre(TRUE_HCL_M, acid_real, naoh_real)
    # what the student records
    recorded = needed + e["reading_shift"]
    # what the student calculates (nominal values!)
    calc = calculate_hcl(recorded)

    return {
        "name": e["name"], "why": e["why"],
        "recorded_titre": recorded, "calc_conc": calc,
        "error_pct": percent_error(calc), "effect": classify(calc),
    }


def print_result(r):
    print(f"\nError   : {r['name']}")
    print(f"Titre   : {r['recorded_titre']:.2f} mL (correct = "
          f"{true_titre(TRUE_HCL_M, NOMINAL_ACID_ML, NOMINAL_NAOH_M):.2f} mL)")
    print(f"HCl     : {r['calc_conc']:.4f} mol/L = "
          f"{r['calc_conc'] * HCL_MOLAR_MASS:.3f} g/L")
    print(f"Error % : {r['error_pct']:+.2f} %")
    print(f"Effect  : {r['effect']} result")
    print(f"Reason  : {r['why']}")


def print_summary():
    print("\n" + "=" * 78)
    print(f"{'Error':<52}{'HCl (M)':>9}{'Err %':>8}  Effect")
    print("-" * 78)
    for k in ERRORS:
        r = simulate_error(k)
        print(f"{r['name'][:51]:<52}{r['calc_conc']:>9.4f}"
              f"{r['error_pct']:>+8.2f}  {r['effect']}")
    print("=" * 78)


def main():
    print("GROUP 12 - EXPERIMENTAL ERROR SIMULATOR")
    print(f"True HCl = {TRUE_HCL_M} M | Correct titre = "
          f"{true_titre(TRUE_HCL_M, NOMINAL_ACID_ML, NOMINAL_NAOH_M):.2f} mL")
    while True:
        print("\nChoose an error (A = all, Q = quit):")
        for k, e in ERRORS.items():
            print(f"  {k}. {e['name']}")
        choice = input("Your choice: ").strip().upper()
        if choice == "Q":
            break
        if choice == "A":
            print_summary()
        elif choice in ERRORS:
            print_result(simulate_error(choice))
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:       # non-interactive test run
        for k in ERRORS:
            print_result(simulate_error(k))
        print_summary()
    else:
        main()
