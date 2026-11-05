"""Module 9 — Titration Curve Plotter and Real-Time Graph Visualiser.

Uses Matplotlib to generate a publication-grade titration curve:
- X-axis: Volume of 0.100 M NaOH Added (mL)
- Y-axis: pH (0 to 14)
- Plots theoretical sigmoidal neutralisation curve
- Plots live experimental titration points as student dispenses titrant
- Marks theoretical equivalence point (22.50 mL, pH 7.00) with dashed guidelines
- Marks experimental endpoint when detected
- Shaded band for Phenolphthalein transition range (pH 8.20 to 10.00)
- Themed in dark laboratory instrument style (#0f172a / #1e293b)
- Exports high-resolution PNG image for the final laboratory report
"""

import os
from typing import List, Tuple, Optional
import matplotlib
# Use Agg or TkAgg depending on environment
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from config import (
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
    NEUTRAL_PH,
    INDICATOR_PH_COLORLESS_LIMIT,
    INDICATOR_PH_DEEP_PINK_LIMIT,
    THEME,
)
from ph_calculator import PHCalculator


class TitrationCurvePlotter:
    """Manages creation, live updates, and disk export of the titration curve."""

    def __init__(self, ph_calculator: Optional[PHCalculator] = None):
        self.ph_calc = ph_calculator or PHCalculator()
        self.fig: Figure = Figure(figsize=(7.2, 4.8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.experimental_volumes: List[float] = []
        self.experimental_phs: List[float] = []
        self.endpoint_marker: Optional[Tuple[float, float]] = None

        # Precompute theoretical curve
        self.theo_v, self.theo_ph = self.ph_calc.generate_curve_data(v_max_ml=35.0, step_ml=0.1)

        self._apply_dark_instrument_style()
        self.redraw()

    def _apply_dark_instrument_style(self) -> None:
        """Apply sleek dark navy laboratory styling to figure and axes."""
        self.fig.patch.set_facecolor("#1e293b")  # Panel background
        self.ax.set_facecolor("#0f172a")        # Axes dark slate

        # Spines
        for spine in self.ax.spines.values():
            spine.set_color("#334155")
            spine.set_linewidth(1.0)

        # Ticks and Labels
        self.ax.tick_params(colors="#94a3b8", labelsize=9)
        self.ax.xaxis.label.set_color("#cbd5e1")
        self.ax.yaxis.label.set_color("#cbd5e1")
        self.ax.title.set_color("#f8fafc")

        # Grid
        self.ax.grid(True, linestyle="--", alpha=0.3, color="#475569")

    def reset_experimental_data(self) -> None:
        """Clear live experimental points for a fresh trial."""
        self.experimental_volumes.clear()
        self.experimental_phs.clear()
        self.endpoint_marker = None
        self.redraw()

    def add_experimental_point(self, volume_ml: float, ph: float) -> None:
        """Append a live measured (volume, pH) point during titration."""
        self.experimental_volumes.append(volume_ml)
        self.experimental_phs.append(ph)

    def mark_endpoint(self, volume_ml: float, ph: float) -> None:
        """Set the experimental endpoint marker."""
        self.endpoint_marker = (volume_ml, ph)

    def redraw(self) -> None:
        """Render the complete figure with theoretical curve, markers, and experimental data."""
        self.ax.clear()
        self._apply_dark_instrument_style()

        # 1. Phenolphthalein Transition Range Shading
        self.ax.axhspan(
            INDICATOR_PH_COLORLESS_LIMIT,
            INDICATOR_PH_DEEP_PINK_LIMIT,
            color="#ec4899",
            alpha=0.15,
            label="Phenolphthalein Range (pH 8.2–10.0)",
        )

        # 2. Theoretical Sigmoid Curve
        self.ax.plot(
            self.theo_v,
            self.theo_ph,
            color="#38bdf8",
            linewidth=1.8,
            linestyle="-",
            alpha=0.75,
            label="Theoretical HCl–NaOH Curve",
        )

        # 3. Theoretical Equivalence Point Reference Lines
        v_eq = THEORETICAL_EQUIVALENCE_VOLUME_ML
        self.ax.axvline(
            v_eq,
            color="#10b981",
            linestyle=":",
            linewidth=1.4,
            alpha=0.8,
            label=f"Equivalence Vol = {v_eq:.2f} mL",
        )
        self.ax.axhline(
            NEUTRAL_PH,
            color="#64748b",
            linestyle=":",
            linewidth=1.0,
            alpha=0.6,
        )
        self.ax.scatter(
            [v_eq],
            [NEUTRAL_PH],
            color="#10b981",
            s=65,
            zorder=5,
            edgecolors="#f8fafc",
            linewidth=1.5,
            label=f"Ideal Eq Point ({v_eq:.2f} mL, pH 7.00)",
        )

        # 4. Live Experimental Points
        if self.experimental_volumes:
            self.ax.plot(
                self.experimental_volumes,
                self.experimental_phs,
                color="#f43f5e",
                linewidth=2.0,
                marker="o",
                markersize=4.5,
                alpha=0.9,
                label="Experimental Run",
            )

        # 5. Experimental Endpoint Marker
        if self.endpoint_marker:
            ep_v, ep_ph = self.endpoint_marker
            self.ax.scatter(
                [ep_v],
                [ep_ph],
                color="#ec4899",
                s=110,
                zorder=6,
                marker="*",
                edgecolors="#ffffff",
                linewidth=1.5,
                label=f"Observed Endpoint ({ep_v:.2f} mL, pH {ep_ph:.2f})",
            )
            self.ax.annotate(
                f"Endpoint\n{ep_v:.2f} mL",
                xy=(ep_v, ep_ph),
                xytext=(ep_v + 1.2, ep_ph - 1.2),
                arrowprops=dict(facecolor="#ec4899", shrink=0.08, width=1.0, headwidth=5),
                color="#fbcfe8",
                fontsize=8,
                fontweight="bold",
            )

        # Axes Limits & Labels
        self.ax.set_xlim(0, 35)
        self.ax.set_ylim(0, 14)
        self.ax.set_xlabel("Volume of 0.100 M NaOH Added (mL)", fontsize=10, fontweight="bold", labelpad=8)
        self.ax.set_ylabel("Solution pH", fontsize=10, fontweight="bold", labelpad=8)
        self.ax.set_title("Potentiometric Titration Curve: 25.00 mL Unknown HCl vs 0.100 M NaOH", fontsize=11, fontweight="bold", pad=10)

        # Legend
        self.ax.legend(
            loc="lower right",
            fontsize=7.5,
            facecolor="#1e293b",
            edgecolor="#334155",
            labelcolor="#f8fafc",
            framealpha=0.9,
        )

        self.fig.tight_layout()

    def save_image(self, file_path: str) -> str:
        """Save high-resolution PNG image of current titration curve."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        self.fig.savefig(file_path, dpi=200, facecolor=self.fig.get_facecolor(), bbox_inches="tight")
        return file_path
