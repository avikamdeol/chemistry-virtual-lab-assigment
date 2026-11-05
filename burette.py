"""Module 4 — Virtual Burette Simulation.

Models a precision Class A laboratory burette:
- Configurable capacity (default 50.00 mL) and reading precision (default 0.05 mL)
- Tracks initial meniscus reading, current reading, total titrant dispensed, and remaining liquid
- Validates dispensing operations to prevent negative dispensing or exceeding capacity
- Supports single-drop (0.05 mL), fine volume increments, and burst additions
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from config import (
    DEFAULT_BURETTE_CAPACITY_ML,
    DEFAULT_BURETTE_PRECISION_ML,
    NAOH_CONCENTRATION_M,
)


@dataclass(frozen=True)
class BuretteReading:
    """Snapshot of burette state."""
    initial_reading_ml: float
    current_reading_ml: float
    delivered_volume_ml: float
    remaining_volume_ml: float
    capacity_ml: float
    precision_ml: float
    is_empty: bool


class VirtualBurette:
    """Class A volumetric burette model with precision meniscus tracking."""

    def __init__(
        self,
        capacity_ml: float = DEFAULT_BURETTE_CAPACITY_ML,
        precision_ml: float = DEFAULT_BURETTE_PRECISION_ML,
        titrant_name: str = "0.100 M NaOH",
    ):
        if capacity_ml <= 0:
            raise ValueError("Burette capacity must be strictly positive.")
        if precision_ml <= 0:
            raise ValueError("Burette precision must be strictly positive.")

        self.capacity_ml = capacity_ml
        self.precision_ml = precision_ml
        self.titrant_name = titrant_name

        self.initial_reading_ml: float = 0.00
        self.current_reading_ml: float = 0.00
        self.total_delivered_ml: float = 0.00
        self.is_stopcock_open: bool = False

    def fill_to_mark(self, initial_reading_ml: float = 0.00) -> None:
        """Fill the burette to an initial meniscus reading (default 0.00 mL)."""
        if not (0.00 <= initial_reading_ml < self.capacity_ml):
            raise ValueError(
                f"Initial reading {initial_reading_ml} mL must be between 0.00 and {self.capacity_ml} mL."
            )
        self.initial_reading_ml = round(initial_reading_ml, 2)
        self.current_reading_ml = self.initial_reading_ml
        self.total_delivered_ml = 0.00

    def dispense(self, volume_ml: float) -> float:
        """Dispense a volume of NaOH titrant from the burette.
        
        Args:
            volume_ml: Volume to dispense in mL.
            
        Returns:
            The actual volume dispensed (mL).
            
        Raises:
            ValueError: If volume_ml is negative or invalid.
        """
        if volume_ml < 0:
            raise ValueError(f"Cannot dispense negative volume: {volume_ml} mL")
        if volume_ml == 0:
            return 0.00

        max_available = self.capacity_ml - self.current_reading_ml
        if max_available <= 0:
            raise ValueError("Burette is empty! Please refill before dispensing more titrant.")

        actual_dispensed = min(volume_ml, max_available)
        self.current_reading_ml = round(self.current_reading_ml + actual_dispensed, 4)
        self.total_delivered_ml = round(self.current_reading_ml - self.initial_reading_ml, 4)
        return actual_dispensed

    def get_reading(self) -> BuretteReading:
        """Get current burette state and readings with appropriate precision."""
        remaining = round(self.capacity_ml - self.current_reading_ml, 4)
        return BuretteReading(
            initial_reading_ml=round(self.initial_reading_ml, 2),
            current_reading_ml=round(self.current_reading_ml, 2),
            delivered_volume_ml=round(self.total_delivered_ml, 2),
            remaining_volume_ml=round(remaining, 2),
            capacity_ml=self.capacity_ml,
            precision_ml=self.precision_ml,
            is_empty=remaining <= 0,
        )

    def reset_trial(self, new_initial_reading: Optional[float] = None) -> None:
        """Reset burette for a new titration trial."""
        if new_initial_reading is not None:
            self.fill_to_mark(new_initial_reading)
        else:
            # Continue from current reading if enough volume left, else refill to 0.00
            if (self.capacity_ml - self.current_reading_ml) >= 25.0:
                self.initial_reading_ml = self.current_reading_ml
                self.total_delivered_ml = 0.00
            else:
                self.fill_to_mark(0.00)
