"""
Group 10: Results and Observations Module (Interactive & Integration-Ready)
Course: First Semester B.Tech - Virtual Lab
Titration: HCl vs Standard NaOH (Phenolphthalein Indicator)
"""

from typing import List, Optional, Tuple


class TitrationTrial:
    """Represents a single titration trial record."""
    def __init__(self, trial_type: str, initial_reading: float, final_reading: float):
        self.trial_type = trial_type.capitalize()
        self.initial_reading = round(float(initial_reading), 2)
        self.final_reading = round(float(final_reading), 2)
        self.titre = round(self.final_reading - self.initial_reading, 2)

        if self.initial_reading < 0 or self.final_reading > 50.00:
            raise ValueError("Burette readings must be between 0.00 mL and 50.00 mL.")
        if self.titre <= 0:
            raise ValueError(
                f"Final reading ({self.final_reading:.2f} mL) must be greater than "
                f"initial reading ({self.initial_reading:.2f} mL)."
            )


class TitrationResultsRecorder:
    """Manages recording, concordance verification, and tabular reporting of titration results."""
    def __init__(self, concordance_limit: float = 0.10):
        self.concordance_limit = concordance_limit
        self.trials: List[TitrationTrial] = []

    def add_trial(self, trial_type: str, initial_reading: float, final_reading: float) -> TitrationTrial:
        """Add a validated titration run to the record."""
        trial = TitrationTrial(trial_type, initial_reading, final_reading)
        self.trials.append(trial)
        return trial

    def get_accurate_trials(self) -> List[TitrationTrial]:
        """Filter and return only the accurate titration runs."""
        return [t for t in self.trials if t.trial_type.lower() == "accurate"]

    def check_concordance(self) -> Tuple[bool, List[float], str]:
        """Check if at least two accurate readings agree within the tolerance (0.10 mL)."""
        accurate = self.get_accurate_trials()
        if len(accurate) < 2:
            return False, [], "Need at least 2 accurate trials to check concordance."

        titres = [t.titre for t in accurate]
        concordant_set = []

        for i in range(len(titres)):
            cluster = [titres[i]]
            for j in range(len(titres)):
                if i != j and abs(titres[i] - titres[j]) <= self.concordance_limit:
                    cluster.append(titres[j])
            if len(cluster) >= 2 and len(cluster) > len(concordant_set):
                concordant_set = cluster

        if len(concordant_set) >= 2:
            spread = max(concordant_set) - min(concordant_set)
            return True, concordant_set, f"PASS - Concordant readings found (spread: {spread:.2f} mL <= {self.concordance_limit:.2f} mL)."
        else:
            return False, [], f"FAIL - Readings differ by more than {self.concordance_limit:.2f} mL. Perform another accurate trial."

    def calculate_mean_titre(self) -> Optional[float]:
        """Calculate the average titre from concordant accurate runs."""
        is_concordant, concordant_titres, _ = self.check_concordance()
        if not is_concordant:
            return None
        return round(sum(concordant_titres) / len(concordant_titres), 2)

    def display_results_table(self) -> None:
        """Print a formatted laboratory observation table."""
        print("\n" + "=" * 74)
        print("            TITRATION OBSERVATION TABLE (HCl vs 0.100 M NaOH)           ")
        print("=" * 74)
        if not self.trials:
            print("  No trials recorded yet.")
            print("=" * 74 + "\n")
            return

        print(f"{'Trial #':<9} | {'Type':<10} | {'Initial (mL)':<14} | {'Final (mL)':<12} | {'Titre (mL)':<10}")
        print("-" * 74)

        for idx, t in enumerate(self.trials, start=1):
            print(f"{idx:<9} | {t.trial_type:<10} | {t.initial_reading:<14.2f} | {t.final_reading:<12.2f} | {t.titre:<10.2f}")

        print("-" * 74)
        is_concordant, concordant_vals, msg = self.check_concordance()
        print(f"Status            : {msg}")

        if is_concordant:
            mean_v = self.calculate_mean_titre()
            formatted_vals = ", ".join(f"{v:.2f}" for v in concordant_vals)
            print(f"Concordant Titres : [{formatted_vals}] mL")
            print(f"Mean Titre        : {mean_v:.2f} mL (Ready for Group 11 HCl calculation)")
        else:
            print("Mean Titre        : Not available until concordant readings are obtained.")
        print("=" * 74 + "\n")


# ----------------------------------------------------------------------
# Interactive User Input Helpers
# ----------------------------------------------------------------------
def get_valid_float(prompt: str) -> float:
    """Safely prompt the user for a numeric burette reading."""
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("  [!] Invalid input. Please enter a numeric value (e.g., 22.50).")


def get_trial_type() -> str:
    """Prompt the user to choose Rough or Accurate trial."""
    while True:
        choice = input("Select Trial Type - [R]ough or [A]ccurate: ").strip().lower()
        if choice in ("r", "rough"):
            return "Rough"
        elif choice in ("a", "accurate"):
            return "Accurate"
        print("  [!] Invalid choice. Please enter 'R' for Rough or 'A' for Accurate.")


def run_interactive_session():
    """Interactive CLI menu for user input and live demonstration."""
    recorder = TitrationResultsRecorder(concordance_limit=0.10)

    print("\n" + "*" * 65)
    print("   VIRTUAL CHEMISTRY LAB - GROUP 10: RESULTS & OBSERVATIONS")
    print("*" * 65)
    print("Instructions:")
    print(" - Standard burette capacity: 0.00 mL to 50.00 mL.")
    print(" - Record 1 Rough titration followed by Accurate titrations.")
    print(" - Accurate readings within 0.10 mL of each other are concordant.\n")

    while True:
        print("Menu Options:")
        print("  1. Add a new titration trial")
        print("  2. View observation table & check concordance")
        print("  3. Load sample test data (Quick Demo)")
        print("  4. Clear all records")
        print("  5. Finish & Exit")

        option = input("\nEnter your choice (1-5): ").strip()

        if option == "1":
            print("\n--- Enter New Titration Reading ---")
            t_type = get_trial_type()
            initial = get_valid_float("Enter Initial Burette Reading (mL): ")
            final = get_valid_float("Enter Final Burette Reading (mL)  : ")

            try:
                trial = recorder.add_trial(t_type, initial, final)
                print(f"\n  [+] Recorded {trial.trial_type} trial -> Volume delivered (Titre): {trial.titre:.2f} mL")
                recorder.display_results_table()
            except ValueError as err:
                print(f"\n  [!] Error: {err}\n")
            input("Press Enter to return to menu...")

        elif option == "2":
            recorder.display_results_table()
            input("Press Enter to return to menu...")

        elif option == "3":
            recorder.trials.clear()
            recorder.add_trial("Rough", 0.00, 22.80)
            recorder.add_trial("Accurate", 0.00, 22.50)
            recorder.add_trial("Accurate", 22.50, 45.05)
            print("\n  [+] Loaded 1 Rough and 2 Concordant Accurate sample trials.")
            recorder.display_results_table()
            input("Press Enter to return to menu...")

        elif option == "4":
            recorder.trials.clear()
            print("\n  [+] All recorded trials have been cleared.\n")
            input("Press Enter to return to menu...")

        elif option == "5":
            print("\nFinal Observation Summary:")
            recorder.display_results_table()
            print("Exiting Group 10 module. Goodbye!")
            break

        else:
            print("  [!] Please select a valid option between 1 and 5.\n")


if __name__ == "__main__":
    run_interactive_session()