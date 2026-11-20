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
# Transition range is 8.20 to 10.00+. The first drop of excess NaOH past equivalence (22.55 mL)
# produces pH ~10.02, which represents the standard visual faint/light pink endpoint.
INDICATOR_PH_COLORLESS_LIMIT: float = 8.20
INDICATOR_PH_FAINT_PINK_LIMIT: float = 10.30
INDICATOR_PH_DEEP_PINK_LIMIT: float = 10.80

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
    # Backgrounds - Clean, bright, professional laboratory palette
    BG_DARKEST: str = "#ffffff"     # Clean bright lab canvas background
    BG_MAIN: str = "#f1f5f9"        # Soft crisp lab workbench main background
    BG_PANEL: str = "#ffffff"       # Clean pure white card / panel background
    BG_PANEL_ALT: str = "#f8fafc"   # Slightly elevated panel background
    BG_INPUT: str = "#ffffff"       # Clean white entry / input background
    
    # Borders & Dividers
    BORDER_SUBTLE: str = "#cbd5e1"  # Crisp slate-300 border
    BORDER_FOCUS: str = "#0284c7"   # Vivid lab cyan/blue focus
    
    # Typography (High Contrast, Highly Legible, Professional)
    TEXT_PRIMARY: str = "#0f172a"   # Deep slate 900
    TEXT_SECONDARY: str = "#334155" # Slate 700
    TEXT_MUTED: str = "#64748b"     # Slate 500
    TEXT_HIGHLIGHT: str = "#0284c7"
    
    # Scientific Functional Accents
    ACCENT_CYAN: str = "#0284c7"    # Deep Sky / Lab Blue
    ACCENT_EMERALD: str = "#059669" # Forest / Emerald Green
    ACCENT_AMBER: str = "#d97706"   # Golden Amber
    ACCENT_ROSE: str = "#e11d48"    # Vivid Rose
    ACCENT_INDIGO: str = "#4f46e5"  # Modern Indigo
    ACCENT_PINK: str = "#db2777"    # Vivid Phenolphthalein Pink
    
    # Liquid Colors for Canvas Apparatus
    LIQUID_HCL_CLEAR: str = "#f0f9ff"        # Crystal-clear water/acid with soft sky tint
    LIQUID_FAINT_PINK: str = "#fbcfe8"       # Pale blush pink (first persistent endpoint)
    LIQUID_MID_PINK: str = "#f472b6"         # Transition pink
    LIQUID_DEEP_MAGENTA: str = "#db2777"     # Over-titrated basic magenta
    GLASS_OUTLINE: str = "#334155"           # Crisp slate glass outline
    GLASS_FILL: str = "#f8fafc"              # Clear glass reflection tint


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
