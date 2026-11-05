"""Configuration and scientific constants for the Virtual Titration Laboratory.

Provides chemical parameters, physical constants, simulation defaults,
and UI styling tokens adhering to a professional scientific dashboard aesthetic.
"""

from dataclasses import dataclass
from typing import Dict, Any


# ==============================================================================
# Chemical and Experimental Parameters (Assignment Specification)
# ==============================================================================

ACID_NAME: str = "Hydrochloric Acid (HCl)"
ACID_FORMULA: str = "HCl"
ACID_VOLUME_ML: float = 25.00  # Stated pipette volume in mL
TRUE_HCL_CONCENTRATION_M: float = 0.0900  # Reference unknown HCl molarity (mol/L)

TITRANT_NAME: str = "Sodium Hydroxide (NaOH)"
TITRANT_FORMULA: str = "NaOH"
NAOH_CONCENTRATION_M: float = 0.100  # Standard titrant molarity (mol/L)

INDICATOR_NAME: str = "Phenolphthalein"
REACTION_EQUATION: str = "HCl + NaOH -> NaCl + H2O"
STOICHIOMETRIC_RATIO: float = 1.0  # 1:1 molar reaction

# Molar Masses in g/mol
MOLAR_MASS_NAOH: float = 40.00  # approx 39.997 g/mol as per assignment
MOLAR_MASS_HCL: float = 36.46   # g/mol
MOLAR_MASS_NACL: float = 58.44  # g/mol
MOLAR_MASS_H2O: float = 18.015  # g/mol

# Physical Constants at 25 °C (298.15 K)
WATER_KW: float = 1.0e-14
NEUTRAL_PH: float = 7.00

# Indicator Transition Limits (Phenolphthalein)
INDICATOR_PH_COLORLESS_LIMIT: float = 8.20
INDICATOR_PH_FAINT_PINK_LIMIT: float = 8.50
INDICATOR_PH_DEEP_PINK_LIMIT: float = 10.00

# Burette & Measurement Defaults
DEFAULT_BURETTE_CAPACITY_ML: float = 50.00
DEFAULT_BURETTE_PRECISION_ML: float = 0.05
DEFAULT_CONCORDANCE_TOLERANCE_ML: float = 0.10


def calculate_theoretical_equivalence_volume(
    acid_vol_ml: float = ACID_VOLUME_ML,
    acid_conc_m: float = TRUE_HCL_CONCENTRATION_M,
    base_conc_m: float = NAOH_CONCENTRATION_M,
    stoich_ratio: float = STOICHIOMETRIC_RATIO
) -> float:
    """Calculate theoretical equivalence volume of NaOH using chemical stoichiometry.
    
    Formula: M_HCl * V_HCl = M_NaOH * V_NaOH (for 1:1 ratio)
             V_NaOH = (M_HCl * V_HCl * ratio) / M_NaOH
    """
    if base_conc_m <= 0:
        raise ValueError("Base concentration must be strictly positive.")
    return (acid_conc_m * acid_vol_ml * stoich_ratio) / base_conc_m


THEORETICAL_EQUIVALENCE_VOLUME_ML: float = calculate_theoretical_equivalence_volume()
# For reference: (0.0900 * 25.00 * 1.0) / 0.100 = 22.50 mL


# ==============================================================================
# UI Color Palette (Dark Charcoal / Laboratory Instrument Dashboard)
# ==============================================================================

@dataclass(frozen=True)
class UIColors:
    # Backgrounds
    BG_DARKEST: str = "#090d16"     # Deep canvas background
    BG_MAIN: str = "#0f172a"        # Charcoal slate dashboard main
    BG_PANEL: str = "#1e293b"       # Card / panel background
    BG_PANEL_ALT: str = "#243247"   # Elevated card background
    BG_INPUT: str = "#141e2e"       # Entry / input background
    
    # Borders & Dividers
    BORDER_SUBTLE: str = "#2d3c52"
    BORDER_FOCUS: str = "#38bdf8"
    
    # Typography
    TEXT_PRIMARY: str = "#f8fafc"
    TEXT_SECONDARY: str = "#cbd5e1"
    TEXT_MUTED: str = "#64748b"
    TEXT_HIGHLIGHT: str = "#38bdf8"
    
    # Scientific Functional Accents
    ACCENT_CYAN: str = "#38bdf8"    # Primary instrument highlight
    ACCENT_EMERALD: str = "#10b981" # Equivalence / Pass / Success
    ACCENT_AMBER: str = "#f59e0b"   # Warning / Precaution / Near Endpoint
    ACCENT_ROSE: str = "#f43f5e"    # Acidic / Hazard / Error
    ACCENT_INDIGO: str = "#6366f1"  # Base / Neutral
    ACCENT_PINK: str = "#ec4899"    # Phenolphthalein Endpoint Pink
    
    # Liquid Colors for Canvas Apparatus
    LIQUID_HCL_CLEAR: str = "#e2e8f0"        # Water-clear with faint meniscus tint
    LIQUID_FAINT_PINK: str = "#fbcfe8"       # Pale blush pink (first persistent endpoint)
    LIQUID_MID_PINK: str = "#f472b6"         # Transition pink
    LIQUID_DEEP_MAGENTA: str = "#db2777"     # Over-titrated basic magenta
    GLASS_OUTLINE: str = "#94a3b8"           # Glass apparatus stroke
    GLASS_FILL: str = "#1e293b"              # Glass reflection tint


THEME = UIColors()


# ==============================================================================
# Typography Font Settings
# ==============================================================================

FONT_FAMILY = "Helvetica"
FONT_MONO = "Menlo" if "darwin" else "Courier"

FONTS = {
    "h1": (FONT_FAMILY, 16, "bold"),
    "h2": (FONT_FAMILY, 13, "bold"),
    "h3": (FONT_FAMILY, 11, "bold"),
    "body": (FONT_FAMILY, 10, "normal"),
    "body_bold": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9, "normal"),
    "mono": (FONT_MONO, 10, "normal"),
    "mono_bold": (FONT_MONO, 10, "bold"),
    "mono_large": (FONT_MONO, 13, "bold"),
}
