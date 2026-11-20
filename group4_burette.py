"""
Group 4 - Virtual Burette
HCl-NaOH Titration: Virtual Lab Coding Assignment

Assumptions:
- Burette capacity: 50.00 mL
- Reading precision: 0.01 mL
- The burette is initially filled to its full capacity.
- Burette reading is the volume delivered (initial reading = 0.00 mL).
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class VirtualBurette:
    """Simulates a burette used to dispense NaOH solution."""

    CAPACITY_ML = Decimal("50.00")
    PRECISION_ML = Decimal("0.01")

    def __init__(self):
        self.remaining_volume = self.CAPACITY_ML
        self.delivered_volume = Decimal("0.00")

    def dispense(self, volume_ml):
        """Dispense the requested volume, if the operation is valid."""
        try:
            volume = Decimal(str(volume_ml))
        except (InvalidOperation, ValueError, TypeError):
            print("Error: Please enter a valid numeric volume.")
            return False

        if not volume.is_finite():
            print("Error: Volume must be a finite number.")
            return False

        if volume <= 0:
            print("Error: Dispensed volume must be greater than 0 mL.")
            return False

        # A burette reading is displayed to the nearest 0.01 mL.
        volume = volume.quantize(self.PRECISION_ML, rounding=ROUND_HALF_UP)

        if volume <= 0:
            print("Error: Volume is too small for the burette precision.")
            return False

        if volume > self.remaining_volume:
            print(
                f"Error: Only {self.remaining_volume:.2f} mL "
                "is left in the burette."
            )
            return False

        self.delivered_volume += volume
        self.remaining_volume -= volume

        print(f"Dispensed: {volume:.2f} mL NaOH")
        print(f"Current burette reading: {self.get_reading():.2f} mL")
        print(f"Remaining volume: {self.remaining_volume:.2f} mL")
        return True

    def get_reading(self):
        """Return the current burette reading in mL."""
        return self.delivered_volume.quantize(self.PRECISION_ML)

    def get_remaining_volume(self):
        """Return the volume still available in the burette."""
        return self.remaining_volume.quantize(self.PRECISION_ML)

    def refill(self):
        """Refill the burette to its stated capacity and reset its reading."""
        self.remaining_volume = self.CAPACITY_ML
        self.delivered_volume = Decimal("0.00")
        print("Burette refilled to 50.00 mL. Reading reset to 0.00 mL.")

    def display_status(self):
        """Display the current state of the burette."""
        print("\n--- BURETTE STATUS ---")
        print(f"Capacity: {self.CAPACITY_ML:.2f} mL")
        print(f"Reading: {self.get_reading():.2f} mL")
        print(f"Delivered: {self.get_reading():.2f} mL")
        print(f"Remaining: {self.get_remaining_volume():.2f} mL")
        print("----------------------")


def main():
    """Demonstrate the virtual burette."""
    burette = VirtualBurette()

    print("HCl-NaOH TITRATION: VIRTUAL BURETTE")
    print(f"Capacity: {burette.CAPACITY_ML:.2f} mL")
    print(f"Reading precision: {burette.PRECISION_ML:.2f} mL")
    burette.display_status()

    while True:
        print("\n1. Dispense NaOH")
        print("2. Display burette status")
        print("3. Refill burette")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            amount = input("Enter volume of NaOH to dispense (mL): ")
            burette.dispense(amount)
        elif choice == "2":
            burette.display_status()
        elif choice == "3":
            burette.refill()
        elif choice == "4":
            print("Virtual burette demonstration completed.")
            break
        else:
            print("Error: Invalid menu choice. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
