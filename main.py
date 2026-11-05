"""Main Application & Integration Orchestrator — Virtual Chemistry Laboratory.

Module 13 & Full System Integration:
- Professional scientific instrument dashboard with dark slate/charcoal styling
- Seamless workflow orchestration across all 12 modules
- Interactive Glassware Apparatus & Canvas Animation
- Digital pH Instrument & Potentiometric Monitor
- Embedded Real-Time Matplotlib Titration Curve Visualiser
- Solution Preparation & Dilution Calculator
- Observation Table with Statistical Concordance Analysis
- Unknown Concentration Stoichiometric Derivations
- Interactive 6-Scenario Experimental Error Analysis Laboratory
- Final Report Generation (HTML & TXT) with Graph Image Export
"""

import os
import sys
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List

# Matplotlib embedded canvas
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Project modules
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
    FONT_FAMILY,
    FONT_MONO,
)
from safety import LaboratorySafetySystem
from solution_preparation import SolutionPreparationCalculator
from titration import TitrationController, TitrationMode, ExperimentStatus, TitrationTelemetry
from titration_curve import TitrationCurvePlotter
from results import ResultsTableManager, ConcordanceAnalysisResult
from concentration import ConcentrationCalculator, ConcentrationResult
from error_analysis import ExperimentalErrorSimulator, ErrorSimulationOutcome, ErrorDirection
from report_generator import LaboratoryReportGenerator
from lab_environment import LabEnvironmentView


class VirtualTitrationApp(tk.Tk):
    """Integrated Virtual Titration Laboratory Desktop Application."""

    def __init__(self):
        super().__init__()
        self.title("Virtual Chemistry Laboratory — HCl–NaOH Titration Suite")
        self.geometry("1240x820")
        self.minsize(1100, 750)
        self.configure(bg=THEME.BG_MAIN)

        # Output Directories
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.graphs_dir = os.path.join(self.output_dir, "graphs")
        self.reports_dir = os.path.join(self.output_dir, "reports")
        os.makedirs(self.graphs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        # Core Engines
        self.safety_sys = LaboratorySafetySystem()
        self.sol_prep_calc = SolutionPreparationCalculator()
        self.titration_ctrl = TitrationController()
        self.curve_plotter = TitrationCurvePlotter()
        self.results_mgr = ResultsTableManager()
        self.conc_calc = ConcentrationCalculator()
        self.error_sim = ExperimentalErrorSimulator()
        self.report_gen = LaboratoryReportGenerator()

        # Operational State
        self.is_safety_verified: bool = False
        self.current_conc_result: Optional[ConcentrationResult] = None
        self.auto_flow_job: Optional[str] = None
        self.graph_canvas: Optional[FigureCanvasTkAgg] = None

        # Style Configuration
        self._init_theme_styles()

        # UI Layout Construction
        self._build_header_banner()
        self._build_tab_notebook()

        # Telemetry Subscription
        self.titration_ctrl.subscribe(self._on_telemetry_update)

        # Initialize default state
        self._update_safety_badge()

    def _init_theme_styles(self) -> None:
        """Configure ttk visual styles for dark scientific dashboard."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Frame styles
        style.configure("TFrame", background=THEME.BG_MAIN)
        style.configure("Card.TFrame", background=THEME.BG_PANEL, relief="flat")
        style.configure("TLabelframe", background=THEME.BG_PANEL, foreground=THEME.TEXT_PRIMARY)
        style.configure("TLabelframe.Label", background=THEME.BG_PANEL, foreground=THEME.ACCENT_CYAN, font=FONTS["body_bold"])

        # Label styles
        style.configure("TLabel", background=THEME.BG_PANEL, foreground=THEME.TEXT_PRIMARY, font=FONTS["body"])
        style.configure("Header.TLabel", background=THEME.BG_MAIN, foreground=THEME.TEXT_PRIMARY, font=FONTS["h1"])
        style.configure("SubHeader.TLabel", background=THEME.BG_MAIN, foreground=THEME.TEXT_SECONDARY, font=FONTS["small"])
        style.configure("Muted.TLabel", background=THEME.BG_PANEL, foreground=THEME.TEXT_MUTED, font=FONTS["small"])
        style.configure("Highlight.TLabel", background=THEME.BG_PANEL, foreground=THEME.ACCENT_CYAN, font=FONTS["body_bold"])
        style.configure("Status.TLabel", background=THEME.BG_PANEL, foreground=THEME.ACCENT_EMERALD, font=FONTS["mono_bold"])

        # Button styles
        style.configure("TButton", font=FONTS["body_bold"], padding=6)
        style.map("TButton", background=[("active", THEME.BG_PANEL_ALT), ("!disabled", THEME.BG_PANEL)])

        # Entry & Spinbox
        style.configure("TEntry", fieldbackground=THEME.BG_INPUT, foreground=THEME.TEXT_PRIMARY)
        style.configure("TCombobox", fieldbackground=THEME.BG_INPUT, foreground=THEME.TEXT_PRIMARY)

        # Notebook Tabs
        style.configure("TNotebook", background=THEME.BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab", background=THEME.BG_PANEL, foreground=THEME.TEXT_SECONDARY, padding=[14, 6], font=FONTS["body_bold"])
        style.map("TNotebook.Tab",
                  background=[("selected", THEME.BG_MAIN), ("active", THEME.BG_PANEL_ALT)],
                  foreground=[("selected", THEME.ACCENT_CYAN), ("active", THEME.TEXT_PRIMARY)])

        # Treeview (Results Table)
        style.configure("Treeview",
                        background=THEME.BG_DARKEST,
                        foreground=THEME.TEXT_PRIMARY,
                        fieldbackground=THEME.BG_DARKEST,
                        rowheight=26,
                        font=FONTS["small"])
        style.configure("Treeview.Heading",
                        background=THEME.BG_PANEL_ALT,
                        foreground=THEME.ACCENT_CYAN,
                        font=FONTS["body_bold"])
        style.map("Treeview", background=[("selected", "#0284c7")])

    def _build_header_banner(self) -> None:
        """Top scientific header banner with title and safety status."""
        header_frame = tk.Frame(self, bg=THEME.BG_MAIN, height=64)
        header_frame.pack(fill=tk.X, padx=16, pady=(10, 4))

        # Title Block
        title_box = tk.Frame(header_frame, bg=THEME.BG_MAIN)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="VIRTUAL CHEMISTRY LABORATORY — POTENTIOMETRIC TITRIMETRY",
            font=FONTS["h1"],
            fg=THEME.TEXT_PRIMARY,
            bg=THEME.BG_MAIN,
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="First Semester B.Tech Courseware | Reaction: HCl + NaOH -> NaCl + H2O | Monoprotic 1:1 Stoichiometry",
            font=FONTS["small"],
            fg=THEME.TEXT_SECONDARY,
            bg=THEME.BG_MAIN,
        ).pack(anchor="w")

        # Right Status Block
        status_box = tk.Frame(header_frame, bg=THEME.BG_MAIN)
        status_box.pack(side=tk.RIGHT)

        self.safety_badge = tk.Label(
            status_box,
            text="SAFETY: PENDING VERIFICATION",
            font=FONTS["mono_bold"],
            fg="#ef4444",
            bg="#3b1219",
            padx=12,
            pady=4,
            relief="solid",
            bd=1,
        )
        self.safety_badge.pack(side=tk.RIGHT, padx=6)

    def _build_tab_notebook(self) -> None:
        """Construct main navigation tab notebook covering all 13 modules."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        # Tab 1: Module 1 — Overview & Apparatus
        self.tab_overview = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_overview, text=" 1. Lab Overview ")
        self._build_overview_tab()

        # Tab 2: Module 2 — Laboratory Safety Protocol
        self.tab_safety = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_safety, text=" 2. Safety Verification ")
        self._build_safety_tab()

        # Tab 3: Module 3 — Solution Preparation Calculator
        self.tab_prep = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prep, text=" 3. Solution Preparation ")
        self._build_solution_prep_tab()

        # Tab 4: Modules 4-9 — Virtual Titration Workbench (Main Simulation)
        self.tab_workbench = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_workbench, text=" 4. Titration Workbench ")
        self._build_workbench_tab()

        # Tab 5: Module 10 — Results & Concordance Table
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text=" 5. Results & Observations ")
        self._build_results_tab()

        # Tab 6: Module 11 — Stoichiometric Calculations
        self.tab_conc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_conc, text=" 6. HCl Concentration ")
        self._build_concentration_tab()

        # Tab 7: Module 12 — Experimental Error Simulation
        self.tab_errors = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_errors, text=" 7. Error Analysis Lab ")
        self._build_error_analysis_tab()

        # Tab 8: Module 13 — Final Laboratory Report
        self.tab_report = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text=" 8. Laboratory Report ")
        self._build_report_tab()

    # ==========================================================================
    # TAB 1: Laboratory Overview & Apparatus (Module 1)
    # ==========================================================================
    def _build_overview_tab(self) -> None:
        view = LabEnvironmentView(
            self.tab_overview,
            on_proceed_to_safety=lambda: self.notebook.select(self.tab_safety)
        )
        view.pack(fill=tk.BOTH, expand=True)

    # ==========================================================================
    # TAB 2: Laboratory Safety (Module 2)
    # ==========================================================================
    def _build_safety_tab(self) -> None:
        main_box = ttk.Frame(self.tab_safety, padding=16)
        main_box.pack(fill=tk.BOTH, expand=True)

        header_lbl = ttk.Label(
            main_box,
            text="MANDATORY LABORATORY SAFETY CHECKLIST",
            font=FONTS["h2"],
            foreground=THEME.ACCENT_CYAN
        )
        header_lbl.pack(anchor="w", pady=(0, 6))

        intro_text = (
            "In accordance with analytical laboratory regulations, all safety protocols and personal "
            "protective equipment (PPE) must be verified before handling corrosive hydrochloric acid "
            "and caustic sodium hydroxide. Titration controls are locked until all mandatory items are checked."
        )
        ttk.Label(main_box, text=intro_text, wraplength=900, justify=tk.LEFT).pack(anchor="w", pady=(0, 14))

        # Checklist frame
        checklist_card = ttk.LabelFrame(main_box, text=" Pre-Experiment Safety Verification ", padding=14)
        checklist_card.pack(fill=tk.BOTH, expand=True)

        self.safety_check_vars = {}
        for item in self.safety_sys.PRECAUTIONS:
            var = tk.BooleanVar(value=False)
            self.safety_check_vars[item.item_id] = var

            row = ttk.Frame(checklist_card)
            row.pack(fill=tk.X, pady=6)

            cb = ttk.Checkbutton(
                row,
                text=f"{item.title}  [{item.category}]",
                variable=var,
                command=lambda i_id=item.item_id, v=var: self._on_safety_check_toggled(i_id, v)
            )
            cb.pack(side=tk.LEFT, anchor="w")

            detail_lbl = ttk.Label(
                row,
                text=f"— {item.hazard_rationale}",
                font=FONTS["small"],
                foreground=THEME.TEXT_MUTED
            )
            detail_lbl.pack(side=tk.LEFT, padx=12)

        # Action Buttons & Feedback
        btn_bar = ttk.Frame(main_box)
        btn_bar.pack(fill=tk.X, pady=16)

        verify_btn = ttk.Button(
            btn_bar,
            text="Verify Safety & Unlock Titration Laboratory",
            command=self._verify_safety_action
        )
        verify_btn.pack(side=tk.LEFT, padx=(0, 10))

        check_all_btn = ttk.Button(
            btn_bar,
            text="Verify All Protocols (Fast-Track for Demo)",
            command=self._verify_all_safety_fast
        )
        check_all_btn.pack(side=tk.LEFT)

        self.safety_feedback_lbl = ttk.Label(
            main_box,
            text="Status: Safety check pending. Check all 7 precautions above to proceed.",
            font=FONTS["body_bold"],
            foreground=THEME.ACCENT_AMBER
        )
        self.safety_feedback_lbl.pack(anchor="w")

    def _on_safety_check_toggled(self, item_id: str, var: tk.BooleanVar) -> None:
        self.safety_sys.set_item_checked(item_id, var.get())

    def _verify_safety_action(self) -> None:
        is_safe, missing, msg = self.safety_sys.verify_all_mandatory()
        if is_safe:
            self.is_safety_verified = True
            self._update_safety_badge()
            self.safety_feedback_lbl.config(
                text="Safety Verification Complete! You may proceed to Solution Preparation or Titration Workbench.",
                foreground=THEME.ACCENT_EMERALD
            )
            messagebox.showinfo("Safety Protocol Cleared", "All mandatory safety items verified! The titration workbench is now unlocked.")
            self.notebook.select(self.tab_workbench)
        else:
            self.is_safety_verified = False
            self._update_safety_badge()
            self.safety_feedback_lbl.config(text=f"Cannot proceed: {len(missing)} safety precaution(s) missing.", foreground=THEME.ACCENT_ROSE)
            messagebox.showwarning("Safety Verification Incomplete", msg)

    def _verify_all_safety_fast(self) -> None:
        for item in self.safety_sys.PRECAUTIONS:
            self.safety_check_vars[item.item_id].set(True)
            self.safety_sys.set_item_checked(item.item_id, True)
        self._verify_safety_action()

    def _update_safety_badge(self) -> None:
        if self.is_safety_verified:
            self.safety_badge.config(
                text="SAFETY: VERIFIED & CLEAR",
                fg=THEME.ACCENT_EMERALD,
                bg="#064e3b"
            )
        else:
            self.safety_badge.config(
                text="SAFETY: PENDING VERIFICATION",
                fg="#f87171",
                bg="#450a0a"
            )

    # ==========================================================================
    # TAB 3: Solution Preparation Calculator (Module 3)
    # ==========================================================================
    def _build_solution_prep_tab(self) -> None:
        paned = ttk.PanedWindow(self.tab_prep, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # Left Column: Interactive Calculators
        left_box = ttk.Frame(paned)
        paned.add(left_box, weight=1)

        # Calculator 1: Solid NaOH
        solid_card = ttk.LabelFrame(left_box, text=" 1. Solid NaOH Dissolution Calculator ", padding=12)
        solid_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(solid_card, text="Formula: Mass = Molarity x Volume (L) x 40.00 g/mol", font=FONTS["small"], foreground=THEME.ACCENT_CYAN).pack(anchor="w", pady=(0, 8))

        row1 = ttk.Frame(solid_card)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="Target Molarity (M):", width=22).pack(side=tk.LEFT)
        self.solid_m_entry = ttk.Entry(row1, width=12)
        self.solid_m_entry.insert(0, "0.100")
        self.solid_m_entry.pack(side=tk.LEFT)

        row2 = ttk.Frame(solid_card)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="Target Volume (mL):", width=22).pack(side=tk.LEFT)
        self.solid_v_entry = ttk.Entry(row2, width=12)
        self.solid_v_entry.insert(0, "250.0")
        self.solid_v_entry.pack(side=tk.LEFT)

        calc_solid_btn = ttk.Button(solid_card, text="Calculate Required NaOH Mass", command=self._calc_solid_naoh)
        calc_solid_btn.pack(anchor="w", pady=(8, 0))

        # Calculator 2: Stock Solution Dilution
        dil_card = ttk.LabelFrame(left_box, text=" 2. Stock Solution Dilution Calculator (M1V1 = M2V2) ", padding=12)
        dil_card.pack(fill=tk.X)

        ttk.Label(dil_card, text="Formula: V1 = (M2 x V2) / M1", font=FONTS["small"], foreground=THEME.ACCENT_CYAN).pack(anchor="w", pady=(0, 8))

        d_row1 = ttk.Frame(dil_card)
        d_row1.pack(fill=tk.X, pady=3)
        ttk.Label(d_row1, text="Stock Molarity M1 (M):", width=22).pack(side=tk.LEFT)
        self.dil_m1_entry = ttk.Entry(d_row1, width=12)
        self.dil_m1_entry.insert(0, "1.000")
        self.dil_m1_entry.pack(side=tk.LEFT)

        d_row2 = ttk.Frame(dil_card)
        d_row2.pack(fill=tk.X, pady=3)
        ttk.Label(d_row2, text="Target Molarity M2 (M):", width=22).pack(side=tk.LEFT)
        self.dil_m2_entry = ttk.Entry(d_row2, width=12)
        self.dil_m2_entry.insert(0, "0.100")
        self.dil_m2_entry.pack(side=tk.LEFT)

        d_row3 = ttk.Frame(dil_card)
        d_row3.pack(fill=tk.X, pady=3)
        ttk.Label(d_row3, text="Target Volume V2 (mL):", width=22).pack(side=tk.LEFT)
        self.dil_v2_entry = ttk.Entry(d_row3, width=12)
        self.dil_v2_entry.insert(0, "250.0")
        self.dil_v2_entry.pack(side=tk.LEFT)

        calc_dil_btn = ttk.Button(dil_card, text="Calculate Required Stock Volume", command=self._calc_dilution)
        calc_dil_btn.pack(anchor="w", pady=(8, 0))

        # Right Column: Step-by-Step Derivation and Laboratory Procedure
        right_card = ttk.LabelFrame(paned, text=" Step-by-Step Derivation & Chemical Procedure ", padding=12)
        paned.add(right_card, weight=2)

        self.prep_output_txt = tk.Text(
            right_card,
            bg=THEME.BG_DARKEST,
            fg="#38bdf8",
            insertbackground="#ffffff",
            font=FONTS["mono"],
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10
        )
        self.prep_output_txt.pack(fill=tk.BOTH, expand=True)

        # Trigger initial calculation display
        self._calc_solid_naoh()

    def _calc_solid_naoh(self) -> None:
        try:
            m = float(self.solid_m_entry.get())
            v = float(self.solid_v_entry.get())
            res = self.sol_prep_calc.calculate_solid_naoh_mass(m, v)
            self.prep_output_txt.delete("1.0", tk.END)
            self.prep_output_txt.insert(tk.END, res.step_by_step_explanation)
        except ValueError as err:
            messagebox.showerror("Invalid Input", str(err))

    def _calc_dilution(self) -> None:
        try:
            m1 = float(self.dil_m1_entry.get())
            m2 = float(self.dil_m2_entry.get())
            v2 = float(self.dil_v2_entry.get())
            res = self.sol_prep_calc.calculate_dilution(m1, m2, v2)
            self.prep_output_txt.delete("1.0", tk.END)
            self.prep_output_txt.insert(tk.END, res.step_by_step_explanation)
        except ValueError as err:
            messagebox.showerror("Invalid Input", str(err))

    # ==========================================================================
    # TAB 4: Virtual Titration Workbench (Modules 4 - 9)
    # ==========================================================================
    def _build_workbench_tab(self) -> None:
        main_paned = ttk.PanedWindow(self.tab_workbench, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ----------------------------------------------------------------------
        # Left Column: Interactive Glassware Apparatus Canvas
        # ----------------------------------------------------------------------
        left_col = ttk.Frame(main_paned)
        main_paned.add(left_col, weight=1)

        apparatus_card = ttk.LabelFrame(left_col, text=" Interactive Titration Apparatus ", padding=6)
        apparatus_card.pack(fill=tk.BOTH, expand=True)

        self.workbench_canvas = tk.Canvas(
            apparatus_card,
            width=280,
            height=460,
            bg=THEME.BG_DARKEST,
            highlightthickness=1,
            highlightbackground=THEME.BORDER_SUBTLE
        )
        self.workbench_canvas.pack(fill=tk.BOTH, expand=True)

        # Apparatus Stage Control Buttons
        stage_btn_frame = ttk.Frame(apparatus_card)
        stage_btn_frame.pack(fill=tk.X, pady=(6, 0))

        self.btn_pipette = ttk.Button(
            stage_btn_frame,
            text="1. Pipette 25 mL HCl",
            command=self._action_pipette_acid
        )
        self.btn_pipette.pack(fill=tk.X, pady=2)

        self.btn_indicator = ttk.Button(
            stage_btn_frame,
            text="2. Add Indicator (2 drops)",
            command=self._action_add_indicator
        )
        self.btn_indicator.pack(fill=tk.X, pady=2)

        self.btn_swirl = ttk.Button(
            stage_btn_frame,
            text="Swirl Flask",
            command=self._action_swirl
        )
        self.btn_swirl.pack(fill=tk.X, pady=2)

        # ----------------------------------------------------------------------
        # Center-Right Column: Instruments, Controls, and Live Curve
        # ----------------------------------------------------------------------
        right_col = ttk.Frame(main_paned)
        main_paned.add(right_col, weight=2)

        # Row 1: Digital Instrument Panel (pH, pOH, Concentrations, Meniscus Readings)
        inst_card = ttk.LabelFrame(right_col, text=" Digital Potentiometric & Volumetric Instrument ", padding=8)
        inst_card.pack(fill=tk.X, pady=(0, 6))

        inst_grid = ttk.Frame(inst_card)
        inst_grid.pack(fill=tk.X)

        # Digital pH Display
        ph_box = tk.Frame(inst_grid, bg="#090d16", padx=14, pady=8, bd=1, relief="solid")
        ph_box.pack(side=tk.LEFT, padx=4)
        tk.Label(ph_box, text="SOLUTION pH", font=FONTS["small"], fg=THEME.TEXT_MUTED, bg="#090d16").pack()
        self.ph_display_lbl = tk.Label(ph_box, text="7.00", font=(FONT_FAMILY, 24, "bold"), fg=THEME.ACCENT_CYAN, bg="#090d16")
        self.ph_display_lbl.pack()
        self.ph_condition_lbl = tk.Label(ph_box, text="Neutral", font=FONTS["small"], fg=THEME.TEXT_SECONDARY, bg="#090d16")
        self.ph_condition_lbl.pack()

        # Digital pOH & Ionic Species
        ions_box = tk.Frame(inst_grid, bg="#090d16", padx=12, pady=8, bd=1, relief="solid")
        ions_box.pack(side=tk.LEFT, padx=4)
        self.poh_lbl = tk.Label(ions_box, text="pOH: 7.00", font=FONTS["mono_bold"], fg=THEME.TEXT_PRIMARY, bg="#090d16")
        self.poh_lbl.pack(anchor="w")
        self.h_conc_lbl = tk.Label(ions_box, text="[H+]:  1.00e-07 M", font=FONTS["mono"], fg=THEME.ACCENT_CYAN, bg="#090d16")
        self.h_conc_lbl.pack(anchor="w")
        self.oh_conc_lbl = tk.Label(ions_box, text="[OH-]: 1.00e-07 M", font=FONTS["mono"], fg=THEME.ACCENT_PINK, bg="#090d16")
        self.oh_conc_lbl.pack(anchor="w")

        # Volumetric Burette Status
        b_box = tk.Frame(inst_grid, bg="#090d16", padx=12, pady=8, bd=1, relief="solid")
        b_box.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)
        self.b_delivered_lbl = tk.Label(b_box, text="Titrant Added: 0.00 mL", font=FONTS["mono_bold"], fg=THEME.ACCENT_CYAN, bg="#090d16")
        self.b_delivered_lbl.pack(anchor="w")
        self.b_reading_lbl = tk.Label(b_box, text="Burette Mark:  0.00 mL (V1: 0.00)", font=FONTS["mono"], fg=THEME.TEXT_SECONDARY, bg="#090d16")
        self.b_reading_lbl.pack(anchor="w")
        self.flask_vol_lbl = tk.Label(b_box, text="Flask Total:   0.00 mL", font=FONTS["mono"], fg=THEME.TEXT_SECONDARY, bg="#090d16")
        self.flask_vol_lbl.pack(anchor="w")

        # Live Status Bar
        self.status_banner = tk.Label(
            inst_card,
            text="STATUS: Standby. Please verify safety and pipette 25.00 mL HCl.",
            font=FONTS["body_bold"],
            fg=THEME.TEXT_PRIMARY,
            bg=THEME.BG_PANEL_ALT,
            anchor="w",
            padx=8,
            pady=4
        )
        self.status_banner.pack(fill=tk.X, pady=(6, 0))

        # Row 2: Titration Experiment Controls (Rough / Accurate Mode, Additions)
        ctrl_card = ttk.LabelFrame(right_col, text=" Experiment Controls ", padding=8)
        ctrl_card.pack(fill=tk.X, pady=(0, 6))

        ctrl_row1 = ttk.Frame(ctrl_card)
        ctrl_row1.pack(fill=tk.X, pady=2)

        ttk.Label(ctrl_row1, text="Trial Type:", font=FONTS["body_bold"]).pack(side=tk.LEFT, padx=(0, 4))
        self.trial_type_combo = ttk.Combobox(
            ctrl_row1,
            values=["Rough Titration", "Accurate Titration"],
            state="readonly",
            width=18
        )
        self.trial_type_combo.current(0)
        self.trial_type_combo.pack(side=tk.LEFT, padx=4)

        new_trial_btn = ttk.Button(ctrl_row1, text="Start Fresh Trial", command=self._action_new_trial)
        new_trial_btn.pack(side=tk.LEFT, padx=4)

        self.record_trial_btn = ttk.Button(ctrl_row1, text="Record Trial to Table", command=self._action_record_trial)
        self.record_trial_btn.pack(side=tk.RIGHT, padx=4)

        # Dispense Buttons Row
        disp_row = ttk.Frame(ctrl_card)
        disp_row.pack(fill=tk.X, pady=(6, 2))

        ttk.Label(disp_row, text="Dispense NaOH:", font=FONTS["small"]).pack(side=tk.LEFT, padx=(0, 6))

        drop_btn = ttk.Button(disp_row, text="+0.05 mL (Drop)", command=lambda: self._action_dispense(0.05))
        drop_btn.pack(side=tk.LEFT, padx=2)

        tenth_btn = ttk.Button(disp_row, text="+0.10 mL", command=lambda: self._action_dispense(0.10))
        tenth_btn.pack(side=tk.LEFT, padx=2)

        half_btn = ttk.Button(disp_row, text="+0.50 mL", command=lambda: self._action_dispense(0.50))
        half_btn.pack(side=tk.LEFT, padx=2)

        one_btn = ttk.Button(disp_row, text="+1.00 mL", command=lambda: self._action_dispense(1.00))
        one_btn.pack(side=tk.LEFT, padx=2)

        two_btn = ttk.Button(disp_row, text="+2.00 mL", command=lambda: self._action_dispense(2.00))
        two_btn.pack(side=tk.LEFT, padx=2)

        five_btn = ttk.Button(disp_row, text="+5.00 mL", command=lambda: self._action_dispense(5.00))
        five_btn.pack(side=tk.LEFT, padx=2)

        # Custom Volume & Auto Flow
        flow_row = ttk.Frame(ctrl_card)
        flow_row.pack(fill=tk.X, pady=(4, 0))

        ttk.Label(flow_row, text="Custom Volume (mL):", font=FONTS["small"]).pack(side=tk.LEFT, padx=(0, 4))
        self.custom_vol_entry = ttk.Entry(flow_row, width=8)
        self.custom_vol_entry.insert(0, "0.25")
        self.custom_vol_entry.pack(side=tk.LEFT, padx=2)

        custom_add_btn = ttk.Button(flow_row, text="Add", command=self._action_add_custom)
        custom_add_btn.pack(side=tk.LEFT, padx=4)

        self.auto_flow_btn = ttk.Button(flow_row, text="Start Continuous Drop Flow", command=self._toggle_auto_flow)
        self.auto_flow_btn.pack(side=tk.LEFT, padx=12)

        # Row 3: Embedded Matplotlib Titration Curve
        graph_card = ttk.LabelFrame(right_col, text=" Potentiometric Titration Curve (Real-Time Plot) ", padding=4)
        graph_card.pack(fill=tk.BOTH, expand=True)

        self.graph_canvas = FigureCanvasTkAgg(self.curve_plotter.fig, master=graph_card)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        graph_bar = ttk.Frame(graph_card)
        graph_bar.pack(fill=tk.X, pady=(4, 0))

        save_graph_btn = ttk.Button(graph_bar, text="Save Graph as PNG", command=self._action_save_graph)
        save_graph_btn.pack(side=tk.RIGHT, padx=4)

        # Initial apparatus render
        self._render_workbench_apparatus()

    # --------------------------------------------------------------------------
    # Workbench Canvas Rendering
    # --------------------------------------------------------------------------
    def _render_workbench_apparatus(self, drop_falling: bool = False, swirl_offset: int = 0) -> None:
        """Render realistic burette, falling drops, and Erlenmeyer flask with dynamic liquid."""
        c = self.workbench_canvas
        c.delete("all")
        w = c.winfo_width() or 280
        h = c.winfo_height() or 460

        telemetry = self.titration_ctrl.get_telemetry()
        v_dispensed = telemetry.titrant_dispensed_ml
        color_hex = telemetry.color_hex

        # 1. Cast Iron Retort Stand
        c_x = w // 2 - 20
        c.create_rectangle(c_x - 70, h - 30, c_x + 70, h - 16, fill="#334155", outline="#64748b", width=1.5)
        c.create_rectangle(c_x - 35, 20, c_x - 30, h - 30, fill="#94a3b8", outline="#64748b")
        c.create_rectangle(c_x - 38, 80, c_x - 10, 92, fill="#475569", outline="#64748b")

        # 2. Precision Burette
        bx = c_x
        b_top = 30
        b_bottom = 260

        # Glass barrel
        c.create_rectangle(bx - 10, b_top, bx + 10, b_bottom, fill="#0f172a", outline=THEME.GLASS_OUTLINE, width=1.5)

        # Liquid column inside burette (drops as volume is dispensed)
        # 50 mL = full span (b_bottom - b_top = 230 px)
        fraction_dispensed = min(1.0, v_dispensed / 50.0)
        liquid_meniscus_y = b_top + 10 + int(fraction_dispensed * 200)

        if liquid_meniscus_y < b_bottom - 10:
            c.create_rectangle(bx - 8, liquid_meniscus_y, bx + 8, b_bottom - 6, fill="#38bdf8", outline="")
            # Curved concave meniscus
            c.create_arc(bx - 8, liquid_meniscus_y - 4, bx + 8, liquid_meniscus_y + 4, start=180, extent=180, outline="#38bdf8", width=1.5)

        # Graduations and readings
        for ml in range(0, 51, 5):
            gy = b_top + 10 + int((ml / 50.0) * 200)
            c.create_line(bx - 9, gy, bx - 2, gy, fill="#cbd5e1", width=1)
            c.create_text(bx - 16, gy, text=str(ml), fill="#94a3b8", font=(FONT_FAMILY, 7))

        # Stopcock
        c.create_polygon(bx - 6, b_bottom - 6, bx + 6, b_bottom - 6, bx + 4, b_bottom + 4, bx - 4, b_bottom + 4, fill="#64748b", outline=THEME.GLASS_OUTLINE)
        valve_color = THEME.ACCENT_CYAN if not drop_falling else "#f59e0b"
        c.create_rectangle(bx - 14, b_bottom - 3, bx + 14, b_bottom + 1, fill=valve_color, outline="#ffffff")
        # Jet tip
        c.create_polygon(bx - 4, b_bottom + 4, bx + 4, b_bottom + 4, bx, b_bottom + 22, fill="#0f172a", outline=THEME.GLASS_OUTLINE)

        # Falling Drop Animation
        if drop_falling:
            drop_y = b_bottom + 35
            c.create_oval(bx - 2, drop_y, bx + 2, drop_y + 5, fill="#38bdf8", outline="")

        # 3. Conical Flask (Erlenmeyer)
        fx = bx + swirl_offset
        f_top = b_bottom + 45
        f_base = h - 35
        f_neck_top = f_top - 16

        # Neck
        c.create_rectangle(fx - 10, f_neck_top, fx + 10, f_top, fill="#0f172a", outline=THEME.GLASS_OUTLINE, width=1.5)
        # Body
        c.create_polygon(
            fx - 10, f_top, fx + 10, f_top,
            fx + 45, f_base, fx - 45, f_base,
            fill="#0f172a", outline=THEME.GLASS_OUTLINE, width=1.5
        )

        # Liquid in Flask
        flask_snapshot = self.titration_ctrl.flask.get_snapshot()
        if flask_snapshot.has_acid:
            # Volume scales from 25 mL to ~60 mL
            vol = flask_snapshot.total_volume_ml
            frac = min(1.0, (vol - 25.0) / 40.0)
            liq_top_y = f_base - 25 - int(frac * 30)
            liq_w = 26 + int(frac * 14)

            c.create_polygon(
                fx - liq_w, liq_top_y, fx + liq_w, liq_top_y,
                fx + 43, f_base - 2, fx - 43, f_base - 2,
                fill=color_hex, outline="", stipple="gray75" if color_hex == THEME.LIQUID_HCL_CLEAR else ""
            )
            # Meniscus surface line
            c.create_line(fx - liq_w, liq_top_y, fx + liq_w, liq_top_y, fill=color_hex, width=1.5)

        # Flask Volume & Status Text
        c.create_text(fx, f_base + 14, text=f"Flask: {flask_snapshot.total_volume_ml:.1f} mL", fill=THEME.TEXT_SECONDARY, font=FONTS["small"])

    # --------------------------------------------------------------------------
    # Workbench Actions & Handlers
    # --------------------------------------------------------------------------
    def _action_pipette_acid(self) -> None:
        if not self.is_safety_verified:
            messagebox.showwarning("Safety Incomplete", "Please complete the mandatory safety checklist in Tab 2 before pipetting chemicals.")
            self.notebook.select(self.tab_safety)
            return

        try:
            self.titration_ctrl.pipette_acid()
            self._render_workbench_apparatus()
            messagebox.showinfo("Acid Transferred", "Successfully pipetted exactly 25.00 mL of unknown HCl into the conical flask.")
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def _action_add_indicator(self) -> None:
        if not self.titration_ctrl.flask.has_acid:
            messagebox.showwarning("Empty Flask", "Please pipette 25.00 mL HCl into the flask first before adding indicator.")
            return

        self.titration_ctrl.add_indicator(2)
        self._render_workbench_apparatus()
        messagebox.showinfo("Indicator Added", "Added 2 drops of phenolphthalein indicator to the flask. Ready for titration.")

    def _action_swirl(self) -> None:
        # Subtle swirl animation
        def anim(step):
            offsets = [0, 6, -6, 4, -4, 2, 0]
            if step < len(offsets):
                self._render_workbench_apparatus(swirl_offset=offsets[step])
                self.after(50, lambda: anim(step + 1))
            else:
                self.titration_ctrl.swirl_flask()
                self._render_workbench_apparatus()

        anim(0)

    def _action_dispense(self, vol_ml: float) -> None:
        if not self.is_safety_verified:
            messagebox.showwarning("Safety Required", "Safety verification must be completed prior to titrant dispensing.")
            self.notebook.select(self.tab_safety)
            return

        try:
            actual = self.titration_ctrl.dispense_titrant(vol_ml)
            if actual > 0:
                tel = self.titration_ctrl.get_telemetry()
                # Record to curve
                self.curve_plotter.add_experimental_point(tel.titrant_dispensed_ml, tel.ph)
                if tel.is_endpoint:
                    self.curve_plotter.mark_endpoint(tel.titrant_dispensed_ml, tel.ph)
                self.curve_plotter.redraw()
                self.graph_canvas.draw_idle()

                # Animation
                self._render_workbench_apparatus(drop_falling=True)
                self.after(80, lambda: self._render_workbench_apparatus(drop_falling=False))

                # Check if endpoint reached or overtitrated
                if tel.status == ExperimentStatus.ENDPOINT_REACHED:
                    messagebox.showinfo("Endpoint Detected", f"ENDPOINT REACHED!\nPersistent faint blush pink observed at {tel.titrant_dispensed_ml:.2f} mL (pH {tel.ph:.2f}).\nPlease record this trial.")
                elif tel.status == ExperimentStatus.OVERTITRATED:
                    messagebox.showwarning("Over-titrated", f"Solution has turned deep pink at {tel.titrant_dispensed_ml:.2f} mL (pH {tel.ph:.2f}). Excess NaOH has been added.")

        except Exception as err:
            self._stop_auto_flow()
            messagebox.showerror("Titration Error", str(err))

    def _action_add_custom(self) -> None:
        try:
            val = float(self.custom_vol_entry.get())
            if val <= 0:
                raise ValueError("Volume must be greater than 0.")
            self._action_dispense(val)
        except ValueError as err:
            messagebox.showerror("Invalid Volume", f"Please enter a valid positive number: {err}")

    def _toggle_auto_flow(self) -> None:
        if self.auto_flow_job:
            self._stop_auto_flow()
        else:
            self.auto_flow_btn.config(text="Stop Continuous Flow")
            self._run_auto_flow_step()

    def _run_auto_flow_step(self) -> None:
        tel = self.titration_ctrl.get_telemetry()
        if tel.status in (ExperimentStatus.ENDPOINT_REACHED, ExperimentStatus.OVERTITRATED):
            self._stop_auto_flow()
            return

        # Dispense fine drop (0.05 mL)
        self._action_dispense(0.05)
        self.auto_flow_job = self.after(250, self._run_auto_flow_step)

    def _stop_auto_flow(self) -> None:
        if self.auto_flow_job:
            self.after_cancel(self.auto_flow_job)
            self.auto_flow_job = None
        self.auto_flow_btn.config(text="Start Continuous Drop Flow")

    def _action_new_trial(self) -> None:
        self._stop_auto_flow()
        mode_str = self.trial_type_combo.get()
        mode = TitrationMode.ROUGH if "Rough" in mode_str else TitrationMode.ACCURATE
        next_trial_num = len(self.results_mgr.records) + 1

        self.titration_ctrl.setup_new_trial(mode, next_trial_num)
        self.curve_plotter.reset_experimental_data()
        self.graph_canvas.draw_idle()
        self._render_workbench_apparatus()

    def _action_record_trial(self) -> None:
        tel = self.titration_ctrl.get_telemetry()
        if tel.titrant_dispensed_ml <= 0:
            messagebox.showwarning("No Titrant Dispensed", "Cannot record empty trial. Please dispense titrant to reach the endpoint.")
            return

        trial_type = "Rough" if tel.mode == TitrationMode.ROUGH else "Accurate"
        rec = self.results_mgr.add_trial(
            trial_type=trial_type,
            initial_reading_ml=tel.burette_initial_ml,
            final_reading_ml=tel.burette_current_ml,
            endpoint_ph=tel.ph,
            observation_color=tel.color_name,
            notes=tel.status_message
        )

        # Refresh Results Table Tab
        self._refresh_results_table_ui()

        # Update Concentration Tab
        concordance = self.results_mgr.analyze_concordance()
        if concordance.has_concordance and concordance.mean_titre_ml:
            self.current_conc_result = self.conc_calc.calculate(concordance.mean_titre_ml)
            self._refresh_concentration_ui()

        messagebox.showinfo(
            "Trial Recorded",
            f"Recorded Trial #{rec.trial_number} ({rec.trial_type}):\n"
            f"Initial: {rec.initial_reading_ml:.2f} mL | Final: {rec.final_reading_ml:.2f} mL\n"
            f"Titre: {rec.titre_ml:.2f} mL | Endpoint pH: {rec.endpoint_ph:.2f}"
        )

    def _action_save_graph(self) -> None:
        default_path = os.path.join(self.graphs_dir, "titration_curve.png")
        file_path = filedialog.asksaveasfilename(
            initialdir=self.graphs_dir,
            initialfile="titration_curve.png",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            out_file = self.curve_plotter.save_image(file_path)
            messagebox.showinfo("Graph Saved", f"Titration curve successfully saved to:\n{out_file}")

    def _on_telemetry_update(self, tel: TitrationTelemetry) -> None:
        """Handle real-time telemetry from titration controller."""
        # Update pH meter
        self.ph_display_lbl.config(text=f"{tel.ph:.2f}")
        self.ph_condition_lbl.config(text=f"{tel.color_name}")

        self.poh_lbl.config(text=f"pOH: {tel.poh:.2f}")
        self.h_conc_lbl.config(text=f"[H+]:  {tel.h_conc:.2e} M")
        self.oh_conc_lbl.config(text=f"[OH-]: {tel.oh_conc:.2e} M")

        self.b_delivered_lbl.config(text=f"Titrant Added: {tel.titrant_dispensed_ml:.2f} mL")
        self.b_reading_lbl.config(text=f"Burette Mark:  {tel.burette_current_ml:.2f} mL (V1: {tel.burette_initial_ml:.2f})")
        self.flask_vol_lbl.config(text=f"Flask Total:   {tel.flask_total_volume_ml:.2f} mL")

        self.status_banner.config(text=f"STATUS: {tel.status_message}")
        self._render_workbench_apparatus()

    # ==========================================================================
    # TAB 5: Results & Observations Table (Module 10)
    # ==========================================================================
    def _build_results_tab(self) -> None:
        main_box = ttk.Frame(self.tab_results, padding=14)
        main_box.pack(fill=tk.BOTH, expand=True)

        header_row = ttk.Frame(main_box)
        header_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_row, text="VOLUMETRIC OBSERVATION TABLE & CONCORDANCE EVALUATION", font=FONTS["h2"], foreground=THEME.ACCENT_CYAN).pack(side=tk.LEFT)

        # Tolerance config
        tol_box = ttk.Frame(header_row)
        tol_box.pack(side=tk.RIGHT)
        ttk.Label(tol_box, text="Concordance Tolerance (± mL):", font=FONTS["small"]).pack(side=tk.LEFT, padx=4)
        self.tol_spin = ttk.Spinbox(tol_box, from_=0.02, to=0.50, increment=0.01, width=6, command=self._on_tolerance_changed)
        self.tol_spin.set("0.10")
        self.tol_spin.pack(side=tk.LEFT)

        # Treeview Table
        table_frame = ttk.Frame(main_box)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("trial", "type", "v1", "v2", "titre", "ph", "obs", "concordant")
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        self.results_tree.heading("trial", text="Trial #")
        self.results_tree.heading("type", text="Trial Type")
        self.results_tree.heading("v1", text="Initial V1 (mL)")
        self.results_tree.heading("v2", text="Final V2 (mL)")
        self.results_tree.heading("titre", text="Titre (mL)")
        self.results_tree.heading("ph", text="Endpoint pH")
        self.results_tree.heading("obs", text="Solution Color")
        self.results_tree.heading("concordant", text="Concordant?")

        self.results_tree.column("trial", width=70, anchor="center")
        self.results_tree.column("type", width=110, anchor="center")
        self.results_tree.column("v1", width=110, anchor="center")
        self.results_tree.column("v2", width=110, anchor="center")
        self.results_tree.column("titre", width=110, anchor="center")
        self.results_tree.column("ph", width=100, anchor="center")
        self.results_tree.column("obs", width=160, anchor="w")
        self.results_tree.column("concordant", width=110, anchor="center")

        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Concordance Analysis Banner
        self.concordance_card = ttk.LabelFrame(main_box, text=" Concordance Analysis Summary ", padding=12)
        self.concordance_card.pack(fill=tk.X, pady=(12, 0))

        self.concordance_status_lbl = ttk.Label(
            self.concordance_card,
            text="No accurate trials recorded. Conduct at least 2 accurate titrations to determine concordant mean.",
            font=FONTS["body_bold"],
            foreground=THEME.ACCENT_AMBER
        )
        self.concordance_status_lbl.pack(anchor="w")

        self.concordance_detail_lbl = ttk.Label(
            self.concordance_card,
            text="Analytical Requirement: At least 2 accurate trials must agree within ±0.10 mL.",
            font=FONTS["small"],
            foreground=THEME.TEXT_SECONDARY
        )
        self.concordance_detail_lbl.pack(anchor="w", pady=(4, 0))

        # Demo Helper Buttons
        demo_btn_bar = ttk.Frame(main_box)
        demo_btn_bar.pack(fill=tk.X, pady=(10, 0))

        add_demo_btn = ttk.Button(demo_btn_bar, text="Populate Concordant Standard Trials (22.50 mL & 22.50 mL)", command=self._populate_demo_trials)
        add_demo_btn.pack(side=tk.LEFT, padx=4)

        clear_table_btn = ttk.Button(demo_btn_bar, text="Clear All Records", command=self._clear_all_records)
        clear_table_btn.pack(side=tk.RIGHT, padx=4)

    def _on_tolerance_changed(self) -> None:
        try:
            tol = float(self.tol_spin.get())
            self.results_mgr.tolerance_ml = tol
            self.results_mgr._update_concordance()
            self._refresh_results_table_ui()
        except ValueError:
            pass

    def _refresh_results_table_ui(self) -> None:
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for rec in self.results_mgr.records:
            concord_text = "YES (Concordant)" if rec.is_concordant else ("N/A (Rough)" if rec.trial_type == "Rough" else "No")
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    rec.trial_number,
                    rec.trial_type,
                    f"{rec.initial_reading_ml:.2f}",
                    f"{rec.final_reading_ml:.2f}",
                    f"{rec.titre_ml:.2f}",
                    f"{rec.endpoint_ph:.2f}",
                    rec.observation_color,
                    concord_text
                )
            )

        concordance = self.results_mgr.analyze_concordance()
        if concordance.has_concordance:
            self.concordance_status_lbl.config(text=concordance.status_message, foreground=THEME.ACCENT_EMERALD)
        else:
            self.concordance_status_lbl.config(text=concordance.status_message, foreground=THEME.ACCENT_AMBER)
        self.concordance_detail_lbl.config(text=concordance.detailed_feedback)

    def _populate_demo_trials(self) -> None:
        """Helper to quickly load realistic standard trials for classroom demonstration."""
        self.results_mgr.clear()
        # Rough Trial: 23.00 mL
        self.results_mgr.add_trial("Rough", 0.00, 23.00, 9.80, "Deep Pink")
        # Accurate Trial 1: 22.50 mL
        self.results_mgr.add_trial("Accurate", 0.00, 22.50, 8.30, "Faint Pink")
        # Accurate Trial 2: 22.50 mL
        self.results_mgr.add_trial("Accurate", 0.00, 22.50, 8.30, "Faint Pink")

        self._refresh_results_table_ui()
        concordance = self.results_mgr.analyze_concordance()
        if concordance.has_concordance and concordance.mean_titre_ml:
            self.current_conc_result = self.conc_calc.calculate(concordance.mean_titre_ml)
            self._refresh_concentration_ui()
        messagebox.showinfo("Demo Trials Loaded", "Loaded 1 Rough Trial (23.00 mL) and 2 Concordant Accurate Trials (22.50 mL).\nMean titre = 22.50 mL.")

    def _clear_all_records(self) -> None:
        if messagebox.askyesno("Confirm Clear", "Clear all recorded titration trial observations?"):
            self.results_mgr.clear()
            self._refresh_results_table_ui()
            self.current_conc_result = None
            self._refresh_concentration_ui()

    # ==========================================================================
    # TAB 6: Stoichiometric HCl Concentration (Module 11)
    # ==========================================================================
    def _build_concentration_tab(self) -> None:
        main_box = ttk.Frame(self.tab_conc, padding=14)
        main_box.pack(fill=tk.BOTH, expand=True)

        header_lbl = ttk.Label(main_box, text="QUANTITATIVE STOICHIOMETRIC DERIVATION OF UNKNOWN HCl CONCENTRATION", font=FONTS["h2"], foreground=THEME.ACCENT_CYAN)
        header_lbl.pack(anchor="w", pady=(0, 10))

        # Metric summary cards
        metric_bar = ttk.Frame(main_box)
        metric_bar.pack(fill=tk.X, pady=(0, 12))

        # Card 1: Calculated Molarity
        c1 = tk.Frame(metric_bar, bg=THEME.BG_PANEL, bd=1, relief="solid", padx=16, pady=10)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(c1, text="Calculated HCl Molarity", font=FONTS["small"], fg=THEME.TEXT_SECONDARY, bg=THEME.BG_PANEL).pack()
        self.card_molarity_lbl = tk.Label(c1, text="-- M", font=(FONT_FAMILY, 20, "bold"), fg=THEME.ACCENT_CYAN, bg=THEME.BG_PANEL)
        self.card_molarity_lbl.pack()
        self.card_ref_m_lbl = tk.Label(c1, text="Reference: 0.0900 M", font=FONTS["small"], fg=THEME.TEXT_MUTED, bg=THEME.BG_PANEL)
        self.card_ref_m_lbl.pack()

        # Card 2: Mass Strength
        c2 = tk.Frame(metric_bar, bg=THEME.BG_PANEL, bd=1, relief="solid", padx=16, pady=10)
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(c2, text="Calculated Mass Strength", font=FONTS["small"], fg=THEME.TEXT_SECONDARY, bg=THEME.BG_PANEL).pack()
        self.card_strength_lbl = tk.Label(c2, text="-- g/L", font=(FONT_FAMILY, 20, "bold"), fg=THEME.TEXT_PRIMARY, bg=THEME.BG_PANEL)
        self.card_strength_lbl.pack()
        tk.Label(c2, text="Formula: Molarity x 36.46 g/mol", font=FONTS["small"], fg=THEME.TEXT_MUTED, bg=THEME.BG_PANEL).pack()

        # Card 3: Percentage Error
        c3 = tk.Frame(metric_bar, bg=THEME.BG_PANEL, bd=1, relief="solid", padx=16, pady=10)
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(c3, text="Experimental Error (%)", font=FONTS["small"], fg=THEME.TEXT_SECONDARY, bg=THEME.BG_PANEL).pack()
        self.card_error_lbl = tk.Label(c3, text="-- %", font=(FONT_FAMILY, 20, "bold"), fg=THEME.ACCENT_EMERALD, bg=THEME.BG_PANEL)
        self.card_error_lbl.pack()
        tk.Label(c3, text="Target Accuracy: <= 1.00%", font=FONTS["small"], fg=THEME.TEXT_MUTED, bg=THEME.BG_PANEL).pack()

        # Full Step-by-Step Mathematical Derivation Box
        deriv_card = ttk.LabelFrame(main_box, text=" Formal Mathematical Derivation & Analytical Chemistry Report ", padding=10)
        deriv_card.pack(fill=tk.BOTH, expand=True)

        self.conc_derivation_txt = tk.Text(
            deriv_card,
            bg=THEME.BG_DARKEST,
            fg="#38bdf8",
            insertbackground="#ffffff",
            font=FONTS["mono"],
            wrap=tk.WORD,
            bd=0,
            padx=12,
            pady=12
        )
        self.conc_derivation_txt.pack(fill=tk.BOTH, expand=True)

        self._refresh_concentration_ui()

    def _refresh_concentration_ui(self) -> None:
        if self.current_conc_result:
            res = self.current_conc_result
            self.card_molarity_lbl.config(text=f"{res.calculated_hcl_molarity_m:.4f} M")
            self.card_strength_lbl.config(text=f"{res.calculated_hcl_conc_g_per_l:.2f} g/L")
            self.card_error_lbl.config(text=f"{res.percentage_error:.2f}%")
            err_color = THEME.ACCENT_EMERALD if res.percentage_error <= 1.0 else THEME.ACCENT_AMBER
            self.card_error_lbl.config(fg=err_color)

            self.conc_derivation_txt.delete("1.0", tk.END)
            self.conc_derivation_txt.insert(tk.END, res.step_by_step_derivation)
        else:
            self.card_molarity_lbl.config(text="-- M")
            self.card_strength_lbl.config(text="-- g/L")
            self.card_error_lbl.config(text="-- %", fg=THEME.TEXT_MUTED)
            self.conc_derivation_txt.delete("1.0", tk.END)
            placeholder = (
                "AWAITING CONCORDANT TITRATION DATA:\n\n"
                "1. Perform at least two accurate titrations in the 'Titration Workbench' tab.\n"
                "2. Ensure trials agree within the concordance tolerance (±0.10 mL).\n"
                "3. Record each trial to the observation table.\n"
                "4. The system will automatically compute the concordant mean titre and perform\n"
                "   the complete stoichiometric derivation here."
            )
            self.conc_derivation_txt.insert(tk.END, placeholder)

    # ==========================================================================
    # TAB 7: Experimental Error Analysis Lab (Module 12)
    # ==========================================================================
    def _build_error_analysis_tab(self) -> None:
        main_box = ttk.Frame(self.tab_errors, padding=14)
        main_box.pack(fill=tk.BOTH, expand=True)

        header_lbl = ttk.Label(main_box, text="INTERACTIVE EXPERIMENTAL ERROR SIMULATION LABORATORY", font=FONTS["h2"], foreground=THEME.ACCENT_CYAN)
        header_lbl.pack(anchor="w", pady=(0, 6))

        intro_text = (
            "Explore how individual analytical errors affect titration results. Select an error scenario "
            "or adjust custom parameters to see whether the calculated HCl concentration is falsely HIGHER, "
            "falsely LOWER, or UNCHANGED, and understand the chemical mechanism behind each effect."
        )
        ttk.Label(main_box, text=intro_text, wraplength=920, justify=tk.LEFT).pack(anchor="w", pady=(0, 12))

        paned = ttk.PanedWindow(main_box, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left Column: Error Scenario Selection
        left_card = ttk.LabelFrame(paned, text=" Error Scenarios ", padding=12)
        paned.add(left_card, weight=1)

        self.error_scenario_var = tk.StringVar(value="overshoot")

        scenarios = [
            ("overshoot", "1. Overshooting Endpoint (Excess NaOH Added)"),
            ("undershoot", "2. Undershooting Endpoint (Premature Stopping)"),
            ("reading_error", "3. Parallax Meniscus Reading Error"),
            ("pipette_error", "4. Pipette Drainage / Air Bubble Error"),
            ("air_bubble", "5. Air Bubble in Burette Tip Dislodged"),
            ("wet_flask", "6A. Deionised Water in Conical Flask"),
            ("wet_burette", "6B. Burette Wet with Water (Unrinsed)"),
        ]

        for s_id, label in scenarios:
            rb = ttk.Radiobutton(
                left_card,
                text=label,
                value=s_id,
                variable=self.error_scenario_var,
                command=self._on_error_scenario_selected
            )
            rb.pack(anchor="w", pady=6)

        # Right Column: Error Diagnostic Results & Pedagogical Takeaway
        right_card = ttk.LabelFrame(paned, text=" Diagnostic Outcome & Chemical Rationale ", padding=14)
        paned.add(right_card, weight=2)

        # Metric Banner
        metric_card = tk.Frame(right_card, bg=THEME.BG_PANEL_ALT, padx=14, pady=10, bd=1, relief="solid")
        metric_card.pack(fill=tk.X, pady=(0, 10))

        self.err_title_lbl = tk.Label(metric_card, text="Overshooting the Endpoint", font=FONTS["body_bold"], fg=THEME.TEXT_PRIMARY, bg=THEME.BG_PANEL_ALT)
        self.err_title_lbl.pack(anchor="w")

        dir_row = tk.Frame(metric_card, bg=THEME.BG_PANEL_ALT)
        dir_row.pack(fill=tk.X, pady=(4, 0))

        tk.Label(dir_row, text="Effect on Calculated HCl: ", font=FONTS["small"], fg=THEME.TEXT_SECONDARY, bg=THEME.BG_PANEL_ALT).pack(side=tk.LEFT)
        self.err_direction_lbl = tk.Label(dir_row, text="Falsely HIGHER", font=FONTS["mono_bold"], fg="#f43f5e", bg=THEME.BG_PANEL_ALT)
        self.err_direction_lbl.pack(side=tk.LEFT)

        self.err_stats_lbl = tk.Label(metric_card, text="Simulated Titre: 24.00 mL | Calculated Molarity: 0.0960 M (Error: +6.67%)", font=FONTS["mono"], fg=THEME.ACCENT_CYAN, bg=THEME.BG_PANEL_ALT)
        self.err_stats_lbl.pack(anchor="w", pady=(4, 0))

        # Detailed Chemical Mechanism Box
        self.err_detail_txt = tk.Text(
            right_card,
            bg=THEME.BG_DARKEST,
            fg="#f8fafc",
            font=FONTS["body"],
            wrap=tk.WORD,
            bd=0,
            padx=12,
            pady=12
        )
        self.err_detail_txt.pack(fill=tk.BOTH, expand=True)

        self._on_error_scenario_selected()

    def _on_error_scenario_selected(self) -> None:
        s_id = self.error_scenario_var.get()
        if s_id == "overshoot":
            outcome = self.error_sim.simulate_overshoot(1.50)
        elif s_id == "undershoot":
            outcome = self.error_sim.simulate_undershoot(0.80)
        elif s_id == "reading_error":
            outcome = self.error_sim.simulate_reading_error(0.35)
        elif s_id == "pipette_error":
            outcome = self.error_sim.simulate_pipette_error(24.20)
        elif s_id == "air_bubble":
            outcome = self.error_sim.simulate_air_bubble_in_burette(0.40)
        elif s_id == "wet_flask":
            outcome = self.error_sim.simulate_wet_flask_with_water(5.0)
        elif s_id == "wet_burette":
            outcome = self.error_sim.simulate_wet_burette_with_water(0.05)
        else:
            outcome = self.error_sim.simulate_overshoot()

        self.err_title_lbl.config(text=outcome.error_title)
        self.err_direction_lbl.config(text=outcome.direction.value)
        color = "#10b981" if outcome.direction == ErrorDirection.UNCHANGED else ("#f43f5e" if outcome.direction == ErrorDirection.HIGHER else "#38bdf8")
        self.err_direction_lbl.config(fg=color)

        self.err_stats_lbl.config(
            text=f"Condition: {outcome.parameter_description}\n"
                 f"Simulated Titre: {outcome.simulated_titre_ml:.2f} mL (Ideal: {outcome.ideal_titre_ml:.2f} mL) | "
                 f"Calc HCl: {outcome.calculated_hcl_m:.4f} M (Error: {outcome.percentage_error:+.2f}%)"
        )

        detail_text = (
            f"=== CHEMICAL & MATHEMATICAL MECHANISM ===\n\n"
            f"{outcome.chemical_mechanism}\n\n"
            f"=== LABORATORY PREVENTION PROTOCOL ===\n\n"
            f"{outcome.prevention_protocol}\n\n"
            f"=== KEY VIVA VOCA TAKEAWAY ===\n\n"
            f"Direction of Error: {outcome.direction.value}\n"
            f"Reference Concentration: {outcome.true_hcl_m:.4f} M\n"
            f"Simulated Concentration: {outcome.calculated_hcl_m:.4f} M"
        )
        self.err_detail_txt.delete("1.0", tk.END)
        self.err_detail_txt.insert(tk.END, detail_text)

    # ==========================================================================
    # TAB 8: Final Laboratory Report (Module 13)
    # ==========================================================================
    def _build_report_tab(self) -> None:
        main_box = ttk.Frame(self.tab_report, padding=14)
        main_box.pack(fill=tk.BOTH, expand=True)

        header_row = ttk.Frame(main_box)
        header_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_row, text="FINAL LABORATORY REPORT GENERATION & EXPORT", font=FONTS["h2"], foreground=THEME.ACCENT_CYAN).pack(side=tk.LEFT)

        # Export Buttons
        btn_box = ttk.Frame(header_row)
        btn_box.pack(side=tk.RIGHT)

        export_html_btn = ttk.Button(btn_box, text="Export HTML Report", command=self._action_export_html)
        export_html_btn.pack(side=tk.LEFT, padx=4)

        export_txt_btn = ttk.Button(btn_box, text="Export TXT Report", command=self._action_export_txt)
        export_txt_btn.pack(side=tk.LEFT, padx=4)

        refresh_preview_btn = ttk.Button(btn_box, text="Refresh Preview", command=self._refresh_report_preview)
        refresh_preview_btn.pack(side=tk.LEFT, padx=4)

        # Metadata Entry Row
        meta_card = ttk.LabelFrame(main_box, text=" Student & Course Details ", padding=8)
        meta_card.pack(fill=tk.X, pady=(0, 10))

        m_row = ttk.Frame(meta_card)
        m_row.pack(fill=tk.X)

        ttk.Label(m_row, text="Student Name / Group:", font=FONTS["small"]).pack(side=tk.LEFT, padx=4)
        self.report_name_entry = ttk.Entry(m_row, width=28)
        self.report_name_entry.insert(0, "First Semester B.Tech Student")
        self.report_name_entry.pack(side=tk.LEFT, padx=4)

        ttk.Label(m_row, text="Institution:", font=FONTS["small"]).pack(side=tk.LEFT, padx=(12, 4))
        self.report_inst_entry = ttk.Entry(m_row, width=32)
        self.report_inst_entry.insert(0, "Department of Chemistry, Engineering Sciences")
        self.report_inst_entry.pack(side=tk.LEFT, padx=4)

        # Preview Container
        preview_card = ttk.LabelFrame(main_box, text=" Report Plaintext Preview ", padding=8)
        preview_card.pack(fill=tk.BOTH, expand=True)

        self.report_preview_txt = tk.Text(
            preview_card,
            bg=THEME.BG_DARKEST,
            fg="#cbd5e1",
            insertbackground="#ffffff",
            font=FONTS["mono"],
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10
        )
        self.report_preview_txt.pack(fill=tk.BOTH, expand=True)

        self._refresh_report_preview()

    def _refresh_report_preview(self) -> None:
        concordance = self.results_mgr.analyze_concordance()
        error_scenarios = self.error_sim.get_all_scenarios()
        name = self.report_name_entry.get()
        inst = self.report_inst_entry.get()
        self.report_gen.student_name = name
        self.report_gen.institution = inst

        txt = self.report_gen.generate_txt_report(
            results_mgr=self.results_mgr,
            conc_result=self.current_conc_result,
            concordance=concordance,
            error_outcomes=error_scenarios,
            safety_verified=self.is_safety_verified
        )
        self.report_preview_txt.delete("1.0", tk.END)
        self.report_preview_txt.insert(tk.END, txt)

    def _action_export_html(self) -> None:
        default_file = os.path.join(self.reports_dir, "titration_lab_report.html")
        file_path = filedialog.asksaveasfilename(
            initialdir=self.reports_dir,
            initialfile="titration_lab_report.html",
            defaultextension=".html",
            filetypes=[("HTML Document", "*.html"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        # Save graph first to embed/link
        graph_path = os.path.join(self.graphs_dir, "titration_curve.png")
        self.curve_plotter.save_image(graph_path)

        concordance = self.results_mgr.analyze_concordance()
        error_scenarios = self.error_sim.get_all_scenarios()
        self.report_gen.student_name = self.report_name_entry.get()
        self.report_gen.institution = self.report_inst_entry.get()

        out_html = self.report_gen.generate_html_report(
            results_mgr=self.results_mgr,
            conc_result=self.current_conc_result,
            concordance=concordance,
            error_outcomes=error_scenarios,
            safety_verified=self.is_safety_verified,
            graph_image_path=graph_path,
            output_file_path=file_path
        )
        messagebox.showinfo("HTML Report Exported", f"Successfully exported publication-ready HTML report to:\n{file_path}")

    def _action_export_txt(self) -> None:
        default_file = os.path.join(self.reports_dir, "titration_lab_report.txt")
        file_path = filedialog.asksaveasfilename(
            initialdir=self.reports_dir,
            initialfile="titration_lab_report.txt",
            defaultextension=".txt",
            filetypes=[("Text Document", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        concordance = self.results_mgr.analyze_concordance()
        error_scenarios = self.error_sim.get_all_scenarios()
        self.report_gen.student_name = self.report_name_entry.get()
        self.report_gen.institution = self.report_inst_entry.get()

        self.report_gen.generate_txt_report(
            results_mgr=self.results_mgr,
            conc_result=self.current_conc_result,
            concordance=concordance,
            error_outcomes=error_scenarios,
            safety_verified=self.is_safety_verified,
            output_file_path=file_path
        )
        messagebox.showinfo("TXT Report Exported", f"Successfully exported structured TXT report to:\n{file_path}")


def main():
    """Main application entry point."""
    app = VirtualTitrationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
