"""
Group 9 - HCl-NaOH Titration Curve
First Semester B.Tech Virtual Lab Assignment

Plots pH against the volume of 0.100 M NaOH added to 25.00 mL
of 0.0900 M HCl, marks the theoretical equivalence point, and
saves the graph as group9_titration_curve.png.

Requirement: Python 3 and matplotlib
Install matplotlib if needed: python -m pip install matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt


# -------------------- Experimental constants --------------------

HCL_VOLUME_ML = 25.00
HCL_CONCENTRATION_M = 0.0900
NAOH_CONCENTRATION_M = 0.100
WATER_KW = 1.0e-14

# HCl + NaOH -> NaCl + H2O (1:1 reaction)
EQUIVALENCE_VOLUME_ML = (
    HCL_CONCENTRATION_M * HCL_VOLUME_ML / NAOH_CONCENTRATION_M
)


def calculate_ph(naoh_volume_ml):
    """
    Calculate the pH after adding a specified volume of NaOH.

    This calculation assumes a strong acid-strong base reaction at
    25 degrees C, with complete dissociation and ideal-solution behavior.

    Args:
        naoh_volume_ml (float): Volume of NaOH added, in mL.

    Returns:
        float: Calculated pH.

    Raises:
        ValueError: If the supplied volume is negative.
    """
    if naoh_volume_ml < 0:
        raise ValueError("NaOH volume cannot be negative.")

    # Convert volumes from mL to L.
    hcl_volume_l = HCL_VOLUME_ML / 1000.0
    naoh_volume_l = naoh_volume_ml / 1000.0

    # Calculate initial moles of HCl and added moles of NaOH.
    moles_hcl = HCL_CONCENTRATION_M * hcl_volume_l
    moles_naoh = NAOH_CONCENTRATION_M * naoh_volume_l

    # Total solution volume after mixing.
    total_volume_l = hcl_volume_l + naoh_volume_l

    # Compare acid and base moles to find the excess reagent.
    difference = moles_hcl - moles_naoh

    if np.isclose(difference, 0.0, atol=1e-14):
        # At equivalence, a strong acid and strong base form a neutral
        # solution at 25 degrees C.
        return 7.0

    elif difference > 0:
        # Acid is in excess.
        hydrogen_concentration = difference / total_volume_l
        return -np.log10(hydrogen_concentration)

    else:
        # Base is in excess.
        hydroxide_concentration = (-difference) / total_volume_l
        poh = -np.log10(hydroxide_concentration)
        return 14.0 - poh


def generate_titration_curve(
    max_naoh_volume_ml=45.0,
    step_ml=0.1,
    save_path="group9_titration_curve.png",
    show_plot=True,
):
    """
    Generate and save the pH-versus-NaOH-volume titration curve.

    The exact theoretical equivalence volume is inserted into the
    plotted data so that it is represented even if it is not a
    multiple of step_ml.

    Returns:
        tuple: (volumes_ml, ph_values, figure)
    """
    if max_naoh_volume_ml <= 0:
        raise ValueError("Maximum NaOH volume must be greater than zero.")
    if step_ml <= 0:
        raise ValueError("Step size must be greater than zero.")
    if max_naoh_volume_ml < EQUIVALENCE_VOLUME_ML:
        raise ValueError(
            "Maximum NaOH volume must reach the equivalence point "
            f"({EQUIVALENCE_VOLUME_ML:.2f} mL)."
        )

    volumes = np.arange(0.0, max_naoh_volume_ml + step_ml / 2, step_ml)
    volumes = np.append(volumes, EQUIVALENCE_VOLUME_ML)
    volumes = np.unique(np.round(volumes, 8))

    ph_values = np.array([calculate_ph(v) for v in volumes])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        volumes,
        ph_values,
        color="blue",
        linewidth=2,
        label="HCl–NaOH titration curve",
    )

    # Mark the theoretical equivalence point.
    ax.axvline(
        EQUIVALENCE_VOLUME_ML,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Theoretical equivalence = {EQUIVALENCE_VOLUME_ML:.2f} mL",
    )
    ax.scatter(
        [EQUIVALENCE_VOLUME_ML],
        [7.0],
        color="red",
        zorder=5,
        label="Equivalence point (pH 7.00)",
    )

    ax.set_title("Titration Curve: 25.00 mL HCl vs 0.100 M NaOH")
    ax.set_xlabel("Volume of NaOH added (mL)")
    ax.set_ylabel("pH")
    ax.set_xlim(0, max_naoh_volume_ml)
    ax.set_ylim(0, 14)
    ax.set_yticks(np.arange(0, 15, 1))
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.legend()
    fig.tight_layout()

    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"Graph saved successfully as: {save_path}")
    print(f"Theoretical equivalence volume: {EQUIVALENCE_VOLUME_ML:.2f} mL")
    print(f"pH at equivalence: {calculate_ph(EQUIVALENCE_VOLUME_ML):.2f}")

    if show_plot:
        plt.show()
    else:
        plt.close(fig)

    return volumes, ph_values, fig


def run_tests():
    """Run basic checks for the Group 9 calculations."""
    assert abs(EQUIVALENCE_VOLUME_ML - 22.50) < 1e-9
    assert abs(calculate_ph(0.0) - (-np.log10(0.0900))) < 1e-9
    assert abs(calculate_ph(22.50) - 7.0) < 1e-9
    assert calculate_ph(30.0) > 7.0
    assert calculate_ph(10.0) < 7.0

    try:
        calculate_ph(-1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative NaOH volume should raise ValueError.")

    print("All Group 9 tests passed.")


if __name__ == "__main__":
    run_tests()
    generate_titration_curve()
