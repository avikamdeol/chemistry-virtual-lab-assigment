"""Module 6 — Phenolphthalein Indicator Simulation.

Models the chemical chromophore transition of phenolphthalein indicator:
- Colorless in acidic and neutral solutions (lactone form, H2In)
- Faint persistent pink at the titration endpoint (pH 8.2 - 8.5)
- Vivid pink/magenta in strongly alkaline solutions (quinoid dianion, In2-)

Features realistic droplet swirling/persistence dynamics and provides
exact visual color representations for GUI rendering.
"""

from dataclasses import dataclass
from typing import Tuple
from config import (
    INDICATOR_PH_COLORLESS_LIMIT,
    INDICATOR_PH_FAINT_PINK_LIMIT,
    INDICATOR_PH_DEEP_PINK_LIMIT,
    THEME,
)


@dataclass(frozen=True)
class IndicatorObservation:
    """State of the indicator observation in the titration flask."""
    ph: float
    color_name: str
    color_hex: str
    is_endpoint: bool
    is_overtitrated: bool
    persistence_status: str
    chemical_species: str
    description: str


class PhenolphthaleinIndicator:
    """Phenolphthalein indicator chemistry and color-transition model."""

    NAME: str = "Phenolphthalein"
    TRANSITION_RANGE: Tuple[float, float] = (8.20, 10.00)

    def __init__(self, drops_added: int = 0):
        self.drops_added = drops_added
        self._persistence_counter = 0

    def add_drops(self, count: int = 2) -> None:
        """Add indicator drops to the flask."""
        if count < 0:
            raise ValueError("Drop count cannot be negative.")
        self.drops_added += count

    def reset(self) -> None:
        """Reset indicator state."""
        self.drops_added = 0
        self._persistence_counter = 0

    def get_color_hex(self, ph: float) -> str:
        """Return the hex color representing the solution at the given pH."""
        if self.drops_added == 0:
            # Without indicator, solution remains water-clear regardless of pH
            return THEME.LIQUID_HCL_CLEAR

        if ph < INDICATOR_PH_COLORLESS_LIMIT:
            return THEME.LIQUID_HCL_CLEAR
        elif ph < INDICATOR_PH_FAINT_PINK_LIMIT:
            # Transition region: faint blush pink (true endpoint!)
            # Interpolate smoothly between faint blush and mid pink
            fraction = (ph - INDICATOR_PH_COLORLESS_LIMIT) / (
                INDICATOR_PH_FAINT_PINK_LIMIT - INDICATOR_PH_COLORLESS_LIMIT
            )
            # Faint pink tint: #fce7f3 (lightest) to #fbcfe8
            return "#fad2e1" if fraction < 0.5 else THEME.LIQUID_FAINT_PINK
        elif ph < INDICATOR_PH_DEEP_PINK_LIMIT:
            return THEME.LIQUID_MID_PINK
        else:
            return THEME.LIQUID_DEEP_MAGENTA

    def evaluate(self, ph: float, swirled: bool = True) -> IndicatorObservation:
        """Evaluate the visual and chemical state of the indicator at the current pH.
        
        Args:
            ph: Current solution bulk pH.
            swirled: True if flask has been swirled to achieve homogeneous mixing.
            
        Returns:
            IndicatorObservation with full optical, chemical, and endpoint diagnostic data.
        """
        if self.drops_added == 0:
            return IndicatorObservation(
                ph=ph,
                color_name="Colorless (No Indicator Added)",
                color_hex=THEME.LIQUID_HCL_CLEAR,
                is_endpoint=False,
                is_overtitrated=False,
                persistence_status="Indicator missing from flask",
                chemical_species="Unmonitored",
                description="Flask lacks phenolphthalein indicator. Solution remains clear.",
            )

        color_hex = self.get_color_hex(ph)

        if ph < INDICATOR_PH_COLORLESS_LIMIT:
            self._persistence_counter = 0
            return IndicatorObservation(
                ph=ph,
                color_name="Colorless",
                color_hex=color_hex,
                is_endpoint=False,
                is_overtitrated=False,
                persistence_status="Colorless (Stable)",
                chemical_species="H2In (Non-ionized Colorless Lactone Form)",
                description=(
                    "Solution is acidic or neutral (pH < 8.2). Phenolphthalein exists "
                    "in its colorless lactone form."
                ),
            )

        elif ph <= INDICATOR_PH_FAINT_PINK_LIMIT:
            if swirled:
                self._persistence_counter += 1
            is_persistent = self._persistence_counter >= 1

            return IndicatorObservation(
                ph=ph,
                color_name="Faint Pink",
                color_hex=color_hex,
                is_endpoint=is_persistent,
                is_overtitrated=False,
                persistence_status="Persistent Faint Pink (ENDPOINT ACHIEVED)" if is_persistent else "Transient Pink",
                chemical_species="In2- (Quinoid Dianion Chromophore forming)",
                description=(
                    "First persistent faint pink color observed! The quinoid dianion has formed. "
                    "This marks the virtual titration endpoint."
                ),
            )

        else:
            self._persistence_counter += 1
            return IndicatorObservation(
                ph=ph,
                color_name="Deep Pink / Magenta",
                color_hex=color_hex,
                is_endpoint=False,
                is_overtitrated=True,
                persistence_status="Over-titrated (Permanent Deep Color)",
                chemical_species="In2- (Fully Ionized Quinoid Form in Excess Base)",
                description=(
                    "Over-titrated! Deep magenta coloration indicates excess NaOH has been "
                    "dispensed beyond the faint pink endpoint."
                ),
            )
