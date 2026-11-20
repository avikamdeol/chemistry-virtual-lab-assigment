"""
Group 3 — Solution Preparation Module
NaOH Solid Mass Calculation and Stock Solution Dilution
"""

import sys
import numpy as np
import matplotlib.pyplot as plt


class SolutionPreparation:
    """Group 3: NaOH Solution Preparation and Dilution Analysis."""
    def __init__(self):
        self.molar_mass_naoh = 39.997 

    def calculate_solid_mass(self, concentration_molar: float, volume_ml: float) -> float:
        if concentration_molar <= 0 or volume_ml <= 0:
            raise ValueError("Concentration and volume must be strictly positive values.")
        volume_l = volume_ml / 1000.0
        mass_g = concentration_molar * volume_l * self.molar_mass_naoh
        return mass_g

    def calculate_dilution(self, m_stock: float, v_final_ml: float, m_target: float) -> float:
        if m_stock <= 0 or v_final_ml <= 0 or m_target <= 0:
            raise ValueError("All parameters must be strictly positive.")
        if m_target > m_stock:
            raise ValueError("Target concentration cannot be larger than the stock.")
        v_stock_ml = (m_target * v_final_ml) / m_stock
        return v_stock_ml

    def validate_input(self, prompt_text: str, data_type=float):
        while True:
            try:
                value = data_type(input(prompt_text))
                if value <= 0:
                    print("  [Validation Error] Value should be positive. Re-enter.")
                    continue
                return value
            except ValueError:
                print("  [Validation Error] Invalid format. Enter a numerical value.")

    def display_results_table(self, title: str, data_dict: dict):
        print(f"\n{'-'*60}")
        print(f" {title.upper().center(56)} ")
        print(f"{'-'*60}")
        for key, value in data_dict.items():
            print(f" {key:<35} : {value}")
        print(f"{'-'*60}\n")

    def plot_dilution_curve(self, stock_conc: float, final_vol: float, target_conc: float, req_vol: float, show_plot=True):
        print("\n[Group 3 Task] Generating Analytical Dilution Curve...")
        target_concs = np.linspace(0.01, stock_conc, 150)
        stock_vols = [(m_t * final_vol) / stock_conc for m_t in target_concs]

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100, facecolor='w', edgecolor='k')
        ax.grid(which='major', axis='both', color="#E11010", linestyle='--', alpha=0.6)
        ax.plot(target_concs, stock_vols, color="#680de8", linewidth=2.2, label=f'Stock Curve ({stock_conc} M)')
        ax.scatter([target_conc], [req_vol], color='red', s=90, zorder=5, label=f'Selected Point ({target_conc}M, {req_vol:.2f}mL)')
        
        ax.set_title("Dilution Curve: Target Concentration vs Stock Volume Required", fontsize=13, fontweight='bold')
        ax.set_xlabel("Target Concentration ($M_2$ in M)", fontsize=11)
        ax.set_ylabel("Required Stock Volume ($V_1$ in mL)", fontsize=11)
        ax.legend(fontsize=10, loc='upper left')
        
        output_filename = "group3_dilution_analysis.png"
        fig.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"  [SUCCESS] Plot saved as '{output_filename}'.")
        if show_plot:
            plt.show()
        else:
            plt.close(fig)
        return fig

    def run_test_cases(self):
        print("\n[Group 3 Verification] Running Test Cases...")
        try:
            mass_test = self.calculate_solid_mass(0.100, 250.0)
            expected_mass = 0.100 * (250.0 / 1000.0) * self.molar_mass_naoh
            assert round(mass_test, 4) == round(expected_mass, 4), "Mass calculation error."

            v1_test = self.calculate_dilution(1.0, 250.0, 0.100)
            assert round(v1_test, 2) == 25.00, "Dilution volume calculation error."
            print("  [PASS] All verification checks passed!\n")
        except AssertionError as err:
            print(f"  [FAIL] Assertion Error: {err}\n")

    def run_module(self):
        print("="*60)
        print("     GROUP 3: SOLUTION PREPARATION (VIRTUAL LAB)       ")
        print("="*60)
        self.run_test_cases()
        try:
            print(">>> PART A: Solid NaOH Solution Preparation")
            target_conc = self.validate_input("Enter target concentration (M, e.g., 0.100): ")
            target_vol = self.validate_input("Enter target volume (mL, e.g., 250.0): ")
            mass_needed = self.calculate_solid_mass(target_conc, target_vol)
            table_a = {
                "Target Molarity": f"{target_conc:.4f} M",
                "Prepared Volume": f"{target_vol:.2f} mL",
                "Molar Mass of NaOH": f"{self.molar_mass_naoh} g/mol",
                "Required Solid Mass": f"{mass_needed:.4f} g"
            }
            self.display_results_table("Solid NaOH Results", table_a)

            print(">>> PART B: Stock Solution Dilution Analysis")
            stock_conc = self.validate_input("Enter stock solution molarity (M, e.g., 1.0): ")
            final_vol = self.validate_input("Enter final desired volume (mL, e.g., 250.0): ")
            desired_conc = self.validate_input("Enter desired target concentration (M, e.g., 0.100): ")
            vol_needed = self.calculate_dilution(stock_conc, final_vol, desired_conc)
            table_b = {
                "Stock Concentration (M1)": f"{stock_conc:.4f} M",
                "Target Concentration (M2)": f"{desired_conc:.4f} M",
                "Final Target Volume (V2)": f"{final_vol:.2f} mL",
                "Stock Volume Needed (V1)": f"{vol_needed:.2f} mL"
            }
            self.display_results_table("Dilution Parameters", table_b)
            self.plot_dilution_curve(stock_conc, final_vol, desired_conc, vol_needed)
        except Exception as e:
            print(f"  [Error]: {e}")


if __name__ == "__main__":
    app = SolutionPreparation()
    app.run_module()
