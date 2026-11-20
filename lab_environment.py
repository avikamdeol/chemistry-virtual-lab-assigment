"""Module 1 — Virtual Laboratory Environment and Apparatus Visualiser.

Provides the comprehensive laboratory overview and introduction screen:
- Experiment title, curriculum aim, stoichiometric chemical reaction
- Experimental parameters and standard reference values
- Detailed theoretical foundation of strong acid - strong base titrimetry
- Interactive visual glassware and apparatus rendering using Tkinter Canvas:
  * Graduated burette on cast iron retorting stand with clamp
  * Precision volumetric bulb pipette with calibration mark
  * Erlenmeyer conical flask with magnetic stirrer base
  * Borosilicate reagent beakers
  * Phenolphthalein indicator dropper bottle
  * Reagent stock bottles (0.100 M NaOH, Unknown HCl) with chemical hazard labels
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from config import (
    ACID_NAME,
    ACID_VOLUME_ML,
    TITRANT_NAME,
    NAOH_CONCENTRATION_M,
    TRUE_HCL_CONCENTRATION_M,
    REACTION_EQUATION,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
    THEME,
    FONTS,
)


class ApparatusVisualiser(tk.Canvas):
    """Custom Tkinter Canvas drawing high-definition laboratory apparatus."""

    def __init__(self, parent, width: int = 560, height: int = 380, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=THEME.BG_DARKEST,
            highlightthickness=1,
            highlightbackground=THEME.BORDER_SUBTLE,
            **kwargs,
        )
        self.width = width
        self.height = height
        self.draw_all_apparatus()

    def draw_all_apparatus(self) -> None:
        """Render all glassware and chemical reagents on the laboratory bench."""
        self.delete("all")

        # 1. Benchtop / Work Surface
        bench_y = self.height - 35
        self.create_rectangle(
            0, bench_y, self.width, self.height,
            fill="#e2e8f0", outline="#cbd5e1", width=1.5
        )
        self.create_line(0, bench_y, self.width, bench_y, fill=THEME.ACCENT_CYAN, width=2)
        self.create_text(
            self.width / 2, self.height - 16,
            text="ANALYTICAL CHEMISTRY WORKBENCH — VIRTUAL LAB",
            fill=THEME.TEXT_SECONDARY, font=FONTS["small"]
        )

        # 2. Retort Stand and Clamped Burette (Left-Center)
        stand_x = 120
        # Cast Iron Stand Base
        self.create_rectangle(stand_x - 45, bench_y - 12, stand_x + 45, bench_y, fill="#475569", outline="#334155", width=1.5)
        # Vertical Steel Rod
        self.create_rectangle(stand_x - 3, 30, stand_x + 3, bench_y - 12, fill="#94a3b8", outline="#64748b")
        # Clamp Bosshead
        self.create_rectangle(stand_x - 6, 95, stand_x + 25, 110, fill="#64748b", outline="#475569")
        # Burette Glass Barrel
        bx = stand_x + 35
        b_top = 40
        b_bottom = bench_y - 90
        # Glass body
        self.create_rectangle(bx - 9, b_top, bx + 9, b_bottom, fill="#ffffff", outline=THEME.GLASS_OUTLINE, width=1.5)
        # Liquid column in burette (0.1 M NaOH)
        liq_top = b_top + 25
        self.create_rectangle(bx - 7, liq_top, bx + 7, b_bottom - 10, fill="#0284c7", stipple="gray50", outline="")
        # Meniscus curve
        self.create_arc(bx - 7, liq_top - 4, bx + 7, liq_top + 4, start=180, extent=180, outline="#0284c7", width=1.5)
        # Burette Graduations
        for gy in range(b_top + 10, b_bottom - 15, 8):
            is_major = ((gy - b_top) % 24 == 0)
            length = 6 if is_major else 3
            self.create_line(bx - 8, gy, bx - 8 + length, gy, fill="#475569", width=1)
        # Stopcock Valve
        self.create_polygon(
            bx - 5, b_bottom - 10, bx + 5, b_bottom - 10,
            bx + 3, b_bottom, bx - 3, b_bottom,
            fill="#64748b", outline=THEME.GLASS_OUTLINE
        )
        self.create_rectangle(bx - 12, b_bottom - 7, bx + 12, b_bottom - 3, fill=THEME.ACCENT_CYAN, outline="#334155")
        # Burette Jet Tip
        self.create_polygon(bx - 3, b_bottom, bx + 3, b_bottom, bx, b_bottom + 18, fill="#ffffff", outline=THEME.GLASS_OUTLINE)
        self.create_text(bx, b_top - 12, text="50.00 mL Burette", fill=THEME.ACCENT_CYAN, font=FONTS["small"])

        # 3. Conical Flask (Directly Under Burette Tip)
        fx = bx
        f_top = bench_y - 65
        f_base = bench_y - 2
        f_neck_top = f_top - 14
        # Neck
        self.create_rectangle(fx - 7, f_neck_top, fx + 7, f_top, fill="#ffffff", outline=THEME.GLASS_OUTLINE, width=1.5)
        # Conical body
        self.create_polygon(
            fx - 7, f_top, fx + 7, f_top,
            fx + 30, f_base, fx - 30, f_base,
            fill="#ffffff", outline=THEME.GLASS_OUTLINE, width=1.5
        )
        # Liquid in Flask (Clear Acid + Faint Pink hint)
        liq_h = f_base - 18
        self.create_polygon(
            fx - 18, liq_h, fx + 18, liq_h,
            fx + 28, f_base - 1, fx - 28, f_base - 1,
            fill="#fbcfe8", outline="", stipple="gray75"
        )
        self.create_text(fx, bench_y + 16, text="Conical Flask", fill=THEME.TEXT_SECONDARY, font=FONTS["small"])

        # 4. Volumetric Bulb Pipette (Center-Right)
        px = 250
        # Upper stem
        self.create_rectangle(px - 3, 50, px + 3, 140, fill="#ffffff", outline=THEME.GLASS_OUTLINE)
        # Calibration Mark line
        self.create_line(px - 6, 80, px + 6, 80, fill=THEME.ACCENT_EMERALD, width=2)
        self.create_text(px + 38, 80, text="25.00 mL Mark", fill=THEME.ACCENT_EMERALD, font=FONTS["small"])
        # Bulb
        self.create_oval(px - 14, 140, px + 14, 210, fill="#ffffff", outline=THEME.GLASS_OUTLINE, width=1.5)
        # Liquid in bulb
        self.create_oval(px - 11, 145, px + 11, 205, fill="#e0f2fe", outline="")
        # Lower stem & tip
        self.create_polygon(
            px - 3, 210, px + 3, 210,
            px, bench_y - 2,
            fill="#ffffff", outline=THEME.GLASS_OUTLINE
        )
        self.create_text(px, 35, text="Bulb Pipette", fill=THEME.ACCENT_CYAN, font=FONTS["small"])

        # 5. Phenolphthalein Indicator Bottle with Dropper
        ix = 345
        # Dropper bulb (rubber)
        self.create_oval(ix - 8, bench_y - 90, ix + 8, bench_y - 72, fill="#ec4899", outline="#f472b6")
        # Glass tube
        self.create_rectangle(ix - 3, bench_y - 72, ix + 3, bench_y - 55, fill="#cbd5e1", outline="#94a3b8")
        # Bottle body
        self.create_rectangle(ix - 18, bench_y - 55, ix + 18, bench_y, fill="#1e1b4b", outline=THEME.GLASS_OUTLINE, width=1.5)
        # Label
        self.create_rectangle(ix - 14, bench_y - 42, ix + 14, bench_y - 10, fill="#f8fafc", outline="")
        self.create_text(ix, bench_y - 26, text="Indicator\npH 8.2-10", fill="#0f172a", font=(FONTS["small"][0], 7, "bold"))
        self.create_text(ix, bench_y - 102, text="Phenolphthalein", fill=THEME.ACCENT_PINK, font=FONTS["small"])

        # 6. Reagent Bottles: NaOH and HCl (Far Right)
        # 0.100 M NaOH
        rx1 = 430
        self.create_rectangle(rx1 - 20, bench_y - 75, rx1 + 20, bench_y, fill="#0c4a6e", outline=THEME.GLASS_OUTLINE, width=1.5)
        self.create_rectangle(rx1 - 10, bench_y - 88, rx1 + 10, bench_y - 75, fill="#0284c7", outline="")
        self.create_rectangle(rx1 - 16, bench_y - 58, rx1 + 16, bench_y - 18, fill="#f8fafc", outline="")
        self.create_text(rx1, bench_y - 38, text="0.100 M\nNaOH", fill="#0369a1", font=(FONTS["small"][0], 8, "bold"))
        self.create_text(rx1, bench_y - 102, text="Titrant", fill=THEME.ACCENT_CYAN, font=FONTS["small"])

        # Unknown HCl
        rx2 = 505
        self.create_rectangle(rx2 - 20, bench_y - 75, rx2 + 20, bench_y, fill="#4c0519", outline=THEME.GLASS_OUTLINE, width=1.5)
        self.create_rectangle(rx2 - 10, bench_y - 88, rx2 + 10, bench_y - 75, fill="#be123c", outline="")
        self.create_rectangle(rx2 - 16, bench_y - 58, rx2 + 16, bench_y - 18, fill="#f8fafc", outline="")
        self.create_text(rx2, bench_y - 38, text="Unknown\nHCL", fill="#9f1239", font=(FONTS["small"][0], 8, "bold"))
        self.create_text(rx2, bench_y - 102, text="Sample", fill=THEME.ACCENT_ROSE, font=FONTS["small"])


from reaction_particles import InteractiveReactionWidget


class LabEnvironmentView(ttk.Frame):
    """Complete Module 1 Overview Panel with apparatus display and theory notes."""

    def __init__(self, parent, on_proceed_to_safety=None):
        super().__init__(parent)
        self.on_proceed_to_safety = on_proceed_to_safety
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the Module 1 layout."""
        # Main container with two columns
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left Column: Dual View (Macroscopic Glassware + Submicroscopic Reaction Particles)
        left_frame = ttk.LabelFrame(paned, text=" Laboratory Setup & Molecular Reaction ", padding=8)
        paned.add(left_frame, weight=1)

        self.visual_notebook = ttk.Notebook(left_frame)
        self.visual_notebook.pack(fill=tk.BOTH, expand=True)

        # Sub-Tab A: Macroscopic Glassware Canvas
        tab_apparatus = ttk.Frame(self.visual_notebook)
        self.visual_notebook.add(tab_apparatus, text=" ⚗ Glassware Setup (Macro) ")

        self.apparatus_canvas = ApparatusVisualiser(tab_apparatus, width=540, height=360)
        self.apparatus_canvas.pack(fill=tk.BOTH, expand=True)

        legend_frame = ttk.Frame(tab_apparatus)
        legend_frame.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(
            legend_frame,
            text="Apparatus: 50 mL Class-A Burette | 25 mL Bulb Pipette | 250 mL Conical Flask | Reagent Bottles",
            font=FONTS["small"],
            foreground=THEME.TEXT_MUTED,
        ).pack(side=tk.LEFT)

        # Sub-Tab B: Submicroscopic Particle Reaction Chamber (H+ + OH- -> H2O)
        self.tab_particles = ttk.Frame(self.visual_notebook)
        self.visual_notebook.add(self.tab_particles, text=" 🔬 Molecular Reaction: H⁺ + OH⁻ ⟶ H₂O ")

        self.reaction_widget = InteractiveReactionWidget(self.tab_particles, width=540, height=340)
        self.reaction_widget.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Right Column: Experiment Title, Aim, Theory & Chemical Parameters
        right_frame = ttk.LabelFrame(paned, text=" Theoretical Principles & Parameters ", padding=12)
        paned.add(right_frame, weight=1)

        # Scrollable container for text
        canvas_txt = tk.Canvas(right_frame, bg=THEME.BG_PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=canvas_txt.yview)
        scroll_content = ttk.Frame(canvas_txt)

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas_txt.configure(scrollregion=canvas_txt.bbox("all"))
        )
        canvas_txt.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas_txt.configure(yscrollcommand=scrollbar.set)

        canvas_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Content elements
        ttk.Label(
            scroll_content,
            text="HCl–NaOH ACID-BASE VOLUMETRIC TITRATION",
            font=FONTS["h2"],
            foreground=THEME.ACCENT_CYAN,
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            scroll_content,
            text="Course: First Semester B.Tech Engineering Chemistry",
            font=FONTS["small"],
            foreground=THEME.TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 10))

        # Aim Box
        aim_frame = ttk.Frame(scroll_content)
        aim_frame.pack(fill=tk.X, pady=6)
        ttk.Label(aim_frame, text="Aim:", font=FONTS["body_bold"], foreground=THEME.ACCENT_CYAN).pack(anchor="w")
        aim_txt = (
            "To determine the unknown molar concentration and strength (g/L) of a hydrochloric acid (HCl) "
            "solution by titrating it against a standard 0.100 M sodium hydroxide (NaOH) solution "
            "using phenolphthalein indicator."
        )
        ttk.Label(aim_frame, text=aim_txt, wraplength=420, font=FONTS["body"], justify=tk.LEFT).pack(anchor="w", padx=6)

        # Reaction Box
        rxn_frame = ttk.Frame(scroll_content)
        rxn_frame.pack(fill=tk.X, pady=6)
        ttk.Label(rxn_frame, text="Chemical Reaction:", font=FONTS["body_bold"], foreground=THEME.ACCENT_CYAN).pack(anchor="w")
        ttk.Label(
            rxn_frame,
            text=f"  {REACTION_EQUATION}  (Stoichiometric Ratio = 1 : 1)",
            font=FONTS["mono_bold"],
            foreground=THEME.TEXT_PRIMARY,
        ).pack(anchor="w", pady=2)

        # Button to switch to particle view
        view_particles_btn = ttk.Button(
            rxn_frame,
            text="🔬 Watch Submicroscopic H⁺ & OH⁻ Particles Joining Together",
            command=lambda: self.visual_notebook.select(self.tab_particles)
        )
        view_particles_btn.pack(anchor="w", pady=(4, 2))

        # Parameters Grid
        param_frame = ttk.Frame(scroll_content)
        param_frame.pack(fill=tk.X, pady=6)
        ttk.Label(param_frame, text="Experimental Parameters:", font=FONTS["body_bold"], foreground=THEME.ACCENT_CYAN).pack(anchor="w")

        params = [
            ("Acid in Flask (V_HCl):", f"{ACID_VOLUME_ML:.2f} mL unknown HCl"),
            ("Standard Titrant (M_NaOH):", f"{NAOH_CONCENTRATION_M:.4f} M NaOH"),
            ("True HCl Concentration:", f"{TRUE_HCL_CONCENTRATION_M:.4f} M (Simulation Reference)"),
            ("Theoretical Eq. Volume:", f"{THEORETICAL_EQUIVALENCE_VOLUME_ML:.2f} mL NaOH"),
            ("Indicator:", "Phenolphthalein (Transition pH 8.2 - 10.0)"),
        ]
        for label, val in params:
            row = ttk.Frame(param_frame)
            row.pack(fill=tk.X, padx=8, pady=1)
            ttk.Label(row, text=label, font=FONTS["small"], foreground=THEME.TEXT_SECONDARY, width=24).pack(side=tk.LEFT)
            ttk.Label(row, text=val, font=FONTS["mono"], foreground=THEME.TEXT_PRIMARY).pack(side=tk.LEFT)

        # Theory Brief
        theory_frame = ttk.Frame(scroll_content)
        theory_frame.pack(fill=tk.X, pady=8)
        ttk.Label(theory_frame, text="Chemical Theory & Indicator Principle:", font=FONTS["body_bold"], foreground=THEME.ACCENT_CYAN).pack(anchor="w")
        theory_txt = (
            "During titration, standard NaOH is progressively added to neutralise the HCl. "
            "At equivalence, moles of H+ equal moles of OH- (pH = 7.00 at 25 °C). "
            "Because phenolphthalein changes from colorless (H2In) to pink (In2-) at pH 8.2–8.5, "
            "the first persistent faint blush pink marks the virtual endpoint. "
            "Due to the steepness of the strong acid-base titration curve, the volume difference "
            "between equivalence and endpoint is less than 0.05 mL."
        )
        ttk.Label(theory_frame, text=theory_txt, wraplength=420, font=FONTS["body"], justify=tk.LEFT).pack(anchor="w", padx=6)

        # Proceed Button
        if self.on_proceed_to_safety:
            btn_frame = ttk.Frame(scroll_content)
            btn_frame.pack(fill=tk.X, pady=(14, 6))
            proceed_btn = ttk.Button(
                btn_frame,
                text="Proceed to Safety Verification Check ->",
                command=self.on_proceed_to_safety,
            )
            proceed_btn.pack(side=tk.RIGHT)
