#!/usr/bin/env python3
"""
=============================================================================
VIRTUAL CHEMISTRY LABORATORY — ALL GROUPS UNIFIED PLATFORM
Course: First Semester B.Tech Engineering Chemistry
Experiment: Determination of Unknown HCl Concentration by Titration with 0.100 M NaOH
=============================================================================
Combines and coordinates all student group assignments:
  - Group 1  : Virtual Laboratory Environment & Apparatus
  - Group 2  : Pre-Experiment Laboratory Safety Checklist
  - Group 3  : NaOH Solution Preparation & Stock Dilution Calculator
  - Group 4  : 50 mL Class-A Virtual Burette Model
  - Group 5  : 25 mL Pipette & Conical Flask Simulation
  - Group 6  : Phenolphthalein Indicator Chromophore & Persistence Model
  - Group 7  : Strong Acid - Strong Base pH Calculation Engine
  - Group 8  : Titration Procedure State Machine (Rough & Accurate Runs)
  - Group 9  : Potentiometric Titration Curve Visualiser & PNG Export
  - Group 10 : Volumetric Observation Table & Concordance Analyzer
  - Group 11 : Stoichiometric HCl Concentration & Strength (g/L) Derivation
  - Group 12 : 7-Scenario Experimental Error Laboratory Simulation
  - Group 13 : Master GUI Orchestrator & Formal Lab Report Generator
=============================================================================
"""

import sys
import os
import subprocess

# Ensure current folder is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def banner():
    print("=" * 74)
    print("      VIRTUAL CHEMISTRY LABORATORY — ALL GROUPS UNIFIED PLATFORM        ")
    print("         HCl - NaOH Volumetric & Potentiometric Titration Suite         ")
    print("=" * 74)


def menu():
    print("""
Select an option or individual group module to test:

  [1]  Group 1  — Virtual Laboratory Environment (Overview & Aim)
  [2]  Group 2  — Laboratory Safety Verification Checklist (8 Questions)
  [3]  Group 3  — NaOH Solution Preparation & Dilution Analysis
  [4]  Group 4  — Virtual Burette Simulator (50.00 mL, 0.01 mL Precision)
  [5]  Group 5  — Conical Flask & Pipette Simulation
  [6]  Group 6  — Phenolphthalein Indicator Module (Color Transitions)
  [7]  Group 7  — pH Measurement Engine & Equivalence Table
  [8]  Group 8  — Titration Procedure (Rough & Accurate State Machine)
  [9]  Group 9  — Titration Curve Plotter (Generate & Save PNG)
  [10] Group 10 — Results & Observations Table (Concordance Verification)
  [11] Group 11 — HCl Concentration & Stoichiometry (Molarity, g/L, % Error)
  [12] Group 12 — Experimental Error Simulation Suite (7 Scenarios)
  [13] Group 13 — Complete Automated End-to-End Simulation & Lab Report
  [14] Launch Master GUI Desktop Application (Full Graphical Suite)
  [15] Run Automated Test Suite (All 23 Verification Tests)
  [0]  Exit
""")


def run_group1():
    print("\n>>> Launching Group 1 — Virtual Laboratory Environment Window...")
    import group1_environment
    group1_environment.launch_standalone()


def run_group2():
    print("\n>>> Running Group 2 — Laboratory Safety Protocol Checklist...")
    import group2_safety
    group2_safety.main()


def run_group3():
    print("\n>>> Running Group 3 — NaOH Solution Preparation & Dilution...")
    import group3_solution_prep
    app = group3_solution_prep.SolutionPreparation()
    app.run_module()


def run_group4():
    print("\n>>> Running Group 4 — Virtual Burette Simulator...")
    import group4_burette
    group4_burette.main()


def run_group5():
    print("\n>>> Running Group 5 — Pipette & Conical Flask Simulation...")
    try:
        import group5_flask
        print("Launching Group 5 Flask Animation...")
        # Run flask script
        subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "group5_flask.py")])
    except Exception as e:
        print(f"Error launching Group 5: {e}")


def run_group6():
    print("\n>>> Running Group 6 — Phenolphthalein Indicator Module...")
    import group6_indicator
    group6_indicator.test_indicator()


def run_group7():
    print("\n>>> Running Group 7 — pH Measurement Engine & Table...")
    import group7_ph
    group7_ph.run_tests()
    group7_ph.show_table()


def run_group8():
    print("\n>>> Running Group 8 — Titration Procedure Simulation Demo...")
    import group8_titration
    # Run the Group 8 CLI demo
    subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "group8_titration.py")])


def run_group9():
    print("\n>>> Running Group 9 — Titration Curve Plotter...")
    import group9_curve
    group9_curve.run_tests()
    out_file = os.path.join(SCRIPT_DIR, "output", "graphs", "group9_titration_curve.png")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    group9_curve.generate_titration_curve(save_path=out_file, show_plot=False)
    print(f"Group 9 graph saved to: {out_file}")


def run_group10():
    print("\n>>> Running Group 10 — Results & Concordance Table...")
    import group10_results
    group10_results.run_interactive_session()


def run_group11():
    print("\n>>> Running Group 11 — HCl Concentration Determination...")
    import group11_concentration
    print("Testing with standard concordant mean titre of 22.50 mL NaOH:")
    res = group11_concentration.analyse_hcl_concentration(22.50)
    group11_concentration.display_results(res)


def run_group12():
    print("\n>>> Running Group 12 — Experimental Error Simulation...")
    import group12_errors
    print("=" * 60)
    print("  GROUP 12 — EXPERIMENTAL ERROR SIMULATION REPORT")
    print("=" * 60)
    for err_id in group12_errors.ERRORS:
        try:
            r = group12_errors.simulate(err_id)
            print(f"Error: {r['name']}")
            print(f"  Classification   : {r['effect']}")
            print(f"  Apparent Titre   : {r['apparent_titre_ml']:.2f} mL")
            print(f"  Apparent HCl [M] : {r['apparent_hcl_m']:.4f} M (Error: {r['error_pct']:+.2f}%)")
            print(f"  Explanation      : {r['explanation'][:100]}...\n")
        except Exception:
            pass


def run_group13():
    print("\n>>> Running Group 13 — Complete Automated End-to-End Simulation...")
    import tests.test_complete_simulation as complete_test
    complete_test.test_complete_experimental_workflow()
    print("\n[SUCCESS] End-to-end integration verified perfectly!")


def launch_gui():
    print("\n>>> Launching Full Desktop Virtual Chemistry Laboratory (Tkinter Suite)...")
    import main
    app = main.VirtualTitrationApp()
    app.mainloop()


def run_tests():
    print("\n>>> Running Universal Pytest Test Suite...")
    subprocess.run([sys.executable, "-m", "pytest", os.path.join(SCRIPT_DIR, "tests"), "-v"])


def main_loop():
    banner()
    while True:
        menu()
        choice = input("Enter your selection (0-15): ").strip()
        if choice == "0":
            print("\nExiting Virtual Chemistry Laboratory. Goodbye!\n")
            break
        elif choice == "1":
            run_group1()
        elif choice == "2":
            run_group2()
        elif choice == "3":
            run_group3()
        elif choice == "4":
            run_group4()
        elif choice == "5":
            run_group5()
        elif choice == "6":
            run_group6()
        elif choice == "7":
            run_group7()
        elif choice == "8":
            run_group8()
        elif choice == "9":
            run_group9()
        elif choice == "10":
            run_group10()
        elif choice == "11":
            run_group11()
        elif choice == "12":
            run_group12()
        elif choice == "13":
            run_group13()
        elif choice == "14":
            launch_gui()
        elif choice == "15":
            run_tests()
        else:
            print("Invalid selection! Please enter a number between 0 and 15.")
        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        launch_gui()
    else:
        main_loop()
