"""Module 13 & Report Generator — Comprehensive Laboratory Report Generation.

Generates professional, publication-quality chemistry laboratory reports:
- Title, student details, course information, and experiment aim
- Chemical theory, balanced reaction stoichiometry, and indicator mechanism
- Verified safety checklist records
- Volumetric observation tables (rough and accurate trials)
- Concordance evaluation and mean titre calculation
- HCl concentration derivation (mol/L, g/L, and percentage error)
- Analytical error simulations and diagnostic takeaways
- Links and embeds generated Matplotlib titration curve
- Exports to formatted, print-ready HTML and clean structured plaintext (TXT)
"""

import os
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import (
    ACID_NAME,
    ACID_VOLUME_ML,
    TITRANT_NAME,
    NAOH_CONCENTRATION_M,
    TRUE_HCL_CONCENTRATION_M,
    REACTION_EQUATION,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
    MOLAR_MASS_HCL,
    MOLAR_MASS_NAOH,
)
from results import ResultsTableManager, ConcordanceAnalysisResult
from concentration import ConcentrationResult
from error_analysis import ErrorSimulationOutcome


class LaboratoryReportGenerator:
    """Generates complete formal academic laboratory reports in HTML and TXT formats."""

    def __init__(
        self,
        student_name: str = "First Semester B.Tech Student",
        institution: str = "Department of Chemistry, Engineering Sciences",
        course_title: str = "Engineering Chemistry Laboratory (First Semester B.Tech)",
    ):
        self.student_name = student_name
        self.institution = institution
        self.course_title = course_title

    def generate_html_report(
        self,
        results_mgr: ResultsTableManager,
        conc_result: Optional[ConcentrationResult],
        concordance: ConcordanceAnalysisResult,
        error_outcomes: List[ErrorSimulationOutcome],
        safety_verified: bool,
        graph_image_path: Optional[str] = None,
        output_file_path: Optional[str] = None,
    ) -> str:
        """Generate a modern, responsive HTML laboratory report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Encode graph as base64 if available
        graph_html = ""
        if graph_image_path and os.path.exists(graph_image_path):
            try:
                with open(graph_image_path, "rb") as img_f:
                    b64_data = base64.b64encode(img_f.read()).decode("utf-8")
                graph_html = f"""
                <div class="graph-card">
                    <h3>Generated Potentiometric Titration Curve</h3>
                    <img src="data:image/png;base64,{b64_data}" alt="Titration Curve" class="report-img"/>
                    <p class="caption">Figure 1: Measured pH vs. 0.100 M NaOH Volume (mL) illustrating equivalence at 22.50 mL and Phenolphthalein transition band.</p>
                </div>
                """
            except Exception:
                graph_html = f"<p><em>Titration graph generated at: {graph_image_path}</em></p>"

        # Build table rows
        rows_html = ""
        for rec in results_mgr.records:
            badge_class = "badge-concordant" if rec.is_concordant else "badge-normal"
            rows_html += f"""
            <tr>
                <td><strong>{rec.trial_number}</strong></td>
                <td><span class="badge {badge_class}">{rec.trial_type}</span></td>
                <td>{rec.initial_reading_ml:.2f} mL</td>
                <td>{rec.final_reading_ml:.2f} mL</td>
                <td><strong>{rec.titre_ml:.2f} mL</strong></td>
                <td>{rec.endpoint_ph:.2f}</td>
                <td><span class="color-dot" style="background-color: {'#fad2e1' if 'Pink' in rec.observation_color else '#e2e8f0'};"></span> {rec.observation_color}</td>
                <td>{'Yes (Concordant)' if rec.is_concordant else 'No'}</td>
            </tr>
            """

        # Build error rows
        error_rows_html = ""
        for err in error_outcomes:
            color_dir = "#10b981" if "UNCHANGED" in err.direction.value else ("#f43f5e" if "HIGHER" in err.direction.value else "#38bdf8")
            error_rows_html += f"""
            <div class="error-item">
                <div class="error-header">
                    <h4>{err.error_title}</h4>
                    <span class="badge-direction" style="background: {color_dir}22; color: {color_dir}; border: 1px solid {color_dir};">
                        {err.direction.value}
                    </span>
                </div>
                <p><strong>Condition:</strong> {err.parameter_description}</p>
                <p><strong>Simulated Titre:</strong> {err.simulated_titre_ml:.2f} mL (Ideal: {err.ideal_titre_ml:.2f} mL) | 
                   <strong>Calculated Molarity:</strong> {err.calculated_hcl_m:.4f} M (Error: {err.percentage_error:+.2f}%)</p>
                <p class="chem-desc"><strong>Chemical Principle:</strong> {err.chemical_mechanism}</p>
                <p class="prevention"><strong>Prevention Protocol:</strong> {err.prevention_protocol}</p>
            </div>
            """

        calc_section_html = ""
        if conc_result:
            calc_section_html = f"""
            <div class="calc-box">
                <h3>Quantitative Stoichiometric Results</h3>
                <div class="grid-3">
                    <div class="metric-card">
                        <span class="metric-label">Calculated HCl Molarity</span>
                        <span class="metric-val">{conc_result.calculated_hcl_molarity_m:.4f} M</span>
                        <span class="metric-sub">Reference: {conc_result.reference_hcl_molarity_m:.4f} M</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Mass Strength</span>
                        <span class="metric-val">{conc_result.calculated_hcl_conc_g_per_l:.2f} g/L</span>
                        <span class="metric-sub">Molar mass HCl: 36.46 g/mol</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">Percentage Error</span>
                        <span class="metric-val" style="color: {'#10b981' if conc_result.percentage_error <= 1.0 else '#f59e0b'};">
                            {conc_result.percentage_error:.2f}%
                        </span>
                        <span class="metric-sub">Deviation: {conc_result.absolute_error_m:.5f} M</span>
                    </div>
                </div>
                <div class="derivation-text">
                    <pre>{conc_result.step_by_step_derivation}</pre>
                </div>
            </div>
            """
        else:
            calc_section_html = "<div class='alert-box'>Concordance not yet established across accurate trials. Concentration calculation pending concordant runs.</div>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Virtual Chemistry Lab Report — HCl-NaOH Titration</title>
    <style>
        :root {{
            --bg-body: #0b0f19;
            --bg-card: #151d2e;
            --bg-card-alt: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-emerald: #10b981;
            --accent-pink: #ec4899;
            --border: #2e3c54;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            line-height: 1.6;
            margin: 0;
            padding: 24px;
        }}
        .report-container {{
            max-width: 960px;
            margin: 0 auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 36px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        .header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 24px;
            color: var(--accent-cyan);
        }}
        .header h2 {{
            margin: 0 0 12px 0;
            font-size: 16px;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            font-size: 13px;
            background: var(--bg-card-alt);
            padding: 14px;
            border-radius: 8px;
            margin-top: 14px;
        }}
        .meta-item strong {{ color: var(--accent-cyan); }}
        h3 {{
            color: var(--text-primary);
            border-left: 4px solid var(--accent-cyan);
            padding-left: 10px;
            margin-top: 28px;
            margin-bottom: 14px;
            font-size: 16px;
        }}
        .table-responsive {{
            overflow-x: auto;
            margin: 16px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        th, td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--bg-card-alt);
            color: var(--accent-cyan);
            font-weight: 600;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }}
        .badge-concordant {{ background: #10b98122; color: #10b981; border: 1px solid #10b981; }}
        .badge-normal {{ background: #334155; color: #cbd5e1; }}
        .color-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
            border: 1px solid #94a3b8;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin: 16px 0;
        }}
        .metric-card {{
            background: var(--bg-card-alt);
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--border);
        }}
        .metric-label {{ display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; }}
        .metric-val {{ display: block; font-size: 22px; font-weight: bold; color: var(--accent-cyan); }}
        .metric-sub {{ display: block; font-size: 11px; color: var(--text-secondary); margin-top: 4px; }}
        .graph-card {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border);
            padding: 18px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        .report-img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid var(--border);
        }}
        .caption {{ font-size: 12px; color: var(--text-secondary); margin-top: 8px; }}
        .derivation-text pre {{
            background: #090d16;
            color: #38bdf8;
            padding: 16px;
            border-radius: 8px;
            font-size: 12px;
            overflow-x: auto;
            border: 1px solid var(--border);
        }}
        .error-item {{
            background: var(--bg-card-alt);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 12px;
        }}
        .error-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .error-header h4 {{ margin: 0; color: var(--text-primary); font-size: 14px; }}
        .badge-direction {{ font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 4px; }}
        .chem-desc {{ font-size: 12px; color: #cbd5e1; margin: 4px 0; }}
        .prevention {{ font-size: 12px; color: #10b981; margin: 4px 0; }}
        .conclusion-box {{
            background: #10b98115;
            border: 1px solid #10b98144;
            padding: 18px;
            border-radius: 8px;
            margin-top: 24px;
        }}
        .conclusion-box h3 {{ border-left-color: #10b981; }}
        .footer {{
            text-align: center;
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 32px;
            border-top: 1px solid var(--border);
            padding-top: 14px;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>Virtual Chemistry Laboratory Final Report</h1>
            <h2>Determination of Unknown Hydrochloric Acid Concentration by Acid-Base Titrimetry</h2>
            <div class="meta-grid">
                <div class="meta-item"><strong>Course:</strong> {self.course_title}</div>
                <div class="meta-item"><strong>Student:</strong> {self.student_name}</div>
                <div class="meta-item"><strong>Institution:</strong> {self.institution}</div>
                <div class="meta-item"><strong>Generated:</strong> {timestamp}</div>
            </div>
        </div>

        <h3>1. Experiment Aim and Theoretical Principles</h3>
        <p>
            <strong>Aim:</strong> To quantitatively determine the molar concentration (M) and mass strength (g/L)
            of an unknown Hydrochloric Acid (HCl) solution by titrating it against a standard 0.100 M Sodium Hydroxide (NaOH)
            solution using phenolphthalein as an internal indicator.
        </p>
        <p>
            <strong>Neutralisation Reaction:</strong>
            <br>
            <code>{REACTION_EQUATION}</code>
            <br>
            Because HCl is a monoprotic strong acid and NaOH is a monobasic strong base, the stoichiometric molar ratio is 1:1.
            At equivalence, <code>M_HCl x V_HCl = M_NaOH x V_NaOH</code>.
        </p>
        <p>
            <strong>Indicator Mechanism:</strong> Phenolphthalein acts as a weak organic acid existing in a colorless lactone
            form (H2In) in acidic medium. At pH 8.2–8.5, loss of protons triggers opening of the lactone ring to form the
            conjugated pink quinoid dianion (In2-). The virtual endpoint is identified by the first persistent faint blush pink color.
        </p>

        <h3>2. Safety Verification Record</h3>
        <p>
            Status: <strong>{'VERIFIED AND COMPLIANT' if safety_verified else 'NON-COMPLIANT / BYPASSED'}</strong>.
            Mandatory personal protective equipment (PPE) including chemical splash goggles, buttoned cotton lab coat,
            nitrile gloves, apparatus inspection, and emergency eyewash awareness were completed prior to experiment execution.
        </p>

        <h3>3. Experimental Parameters</h3>
        <div class="meta-grid">
            <div class="meta-item"><strong>Acid Aliquot (V_HCl):</strong> {ACID_VOLUME_ML:.2f} mL</div>
            <div class="meta-item"><strong>Standard Titrant (M_NaOH):</strong> {NAOH_CONCENTRATION_M:.4f} M</div>
            <div class="meta-item"><strong>Indicator:</strong> Phenolphthalein (2 drops)</div>
            <div class="meta-item"><strong>Theoretical Eq. Volume:</strong> {THEORETICAL_EQUIVALENCE_VOLUME_ML:.2f} mL</div>
        </div>

        <h3>4. Volumetric Observation Table</h3>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>Trial #</th>
                        <th>Type</th>
                        <th>Initial (V1)</th>
                        <th>Final (V2)</th>
                        <th>Titre (V2 - V1)</th>
                        <th>Endpoint pH</th>
                        <th>Observation</th>
                        <th>Concordant?</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else "<tr><td colspan='8'>No trials recorded.</td></tr>"}
                </tbody>
            </table>
        </div>
        <p><strong>Concordance Analysis:</strong> {concordance.detailed_feedback}</p>

        {graph_html}

        <h3>5. Stoichiometric Calculations & Quantitative Derivation</h3>
        {calc_section_html}

        <h3>6. Experimental Error Analysis and Diagnostics</h3>
        <div class="error-container">
            {error_rows_html}
        </div>

        <div class="conclusion-box">
            <h3>7. Academic Conclusion</h3>
            <p>
                The unknown concentration of the sample Hydrochloric Acid solution was determined to be
                <strong>{f"{conc_result.calculated_hcl_molarity_m:.4f} M ({conc_result.calculated_hcl_conc_g_per_l:.2f} g/L)" if conc_result else "Pending concordant trials"}</strong>,
                achieving a percentage error of <strong>{f"{conc_result.percentage_error:.2f}%" if conc_result else "N/A"}</strong>
                relative to the reference benchmark of {TRUE_HCL_CONCENTRATION_M:.4f} M.
                The experiment confirmed that concordant dropwise additions in the steep inflection region of the strong acid-strong base
                neutralisation curve yield high analytical precision.
            </p>
        </div>

        <div class="footer">
            Virtual Chemistry Laboratory &copy; 2026 First Semester B.Tech Courseware. Built with Python 3, Tkinter & Matplotlib.
        </div>
    </div>
</body>
</html>
"""
        if output_file_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        return html_content

    def generate_txt_report(
        self,
        results_mgr: ResultsTableManager,
        conc_result: Optional[ConcentrationResult],
        concordance: ConcordanceAnalysisResult,
        error_outcomes: List[ErrorSimulationOutcome],
        safety_verified: bool,
        output_file_path: Optional[str] = None,
    ) -> str:
        """Generate structured plaintext laboratory report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "=" * 78,
            "     HCL-NAOH ACID-BASE TITRATION — VIRTUAL CHEMISTRY LAB REPORT",
            "=" * 78,
            f"Course:      {self.course_title}",
            f"Student:     {self.student_name}",
            f"Institution: {self.institution}",
            f"Generated:   {timestamp}",
            "-" * 78,
            "\n1. EXPERIMENTAL AIM & PARAMETERS:",
            "Aim: To determine the concentration of unknown HCl by titrating against",
            "     0.100 M standard NaOH using phenolphthalein indicator.",
            f"Reaction:    {REACTION_EQUATION}",
            f"Pipetted HCl Aliquot (V_HCl): {ACID_VOLUME_ML:.2f} mL",
            f"Standard NaOH Molarity:       {NAOH_CONCENTRATION_M:.4f} M",
            f"Theoretical Equivalence Vol:  {THEORETICAL_EQUIVALENCE_VOLUME_ML:.2f} mL",
            f"Safety Protocol Verified:     {'YES' if safety_verified else 'NO'}",
            "\n" + "-" * 78,
            "2. OBSERVATION TABLE:",
            f"{'Trial':<8}{'Type':<10}{'Initial (mL)':<14}{'Final (mL)':<12}{'Titre (mL)':<12}{'pH':<8}{'Concordant?'}",
            "-" * 78,
        ]

        for rec in results_mgr.records:
            lines.append(
                f"{rec.trial_number:<8}{rec.trial_type:<10}{rec.initial_reading_ml:<14.2f}"
                f"{rec.final_reading_ml:<12.2f}{rec.titre_ml:<12.2f}{rec.endpoint_ph:<8.2f}"
                f"{'Yes' if rec.is_concordant else 'No'}"
            )

        lines.extend([
            "-" * 78,
            f"Concordance Status: {concordance.status_message}",
            f"Mean Accurate Titre: {f'{concordance.mean_titre_ml:.2f} mL' if concordance.mean_titre_ml else 'N/A'}",
            "\n" + "-" * 78,
            "3. STOICHIOMETRIC CALCULATIONS & QUANTITATIVE DERIVATION:",
        ])

        if conc_result:
            lines.append(conc_result.step_by_step_derivation)
        else:
            lines.append("Concordant trials not established. Calculation pending.")

        lines.extend([
            "-" * 78,
            "4. EXPERIMENTAL ERROR ANALYSIS SUMMARY:",
            "-" * 78,
        ])

        for err in error_outcomes:
            lines.extend([
                f"Error: {err.error_title}",
                f"  Condition:       {err.parameter_description}",
                f"  Direction:       {err.direction.value}",
                f"  Simulated Titre: {err.simulated_titre_ml:.2f} mL | Calc HCl: {err.calculated_hcl_m:.4f} M (Error: {err.percentage_error:+.2f}%)",
                f"  Mechanism:       {err.chemical_mechanism}",
                f"  Prevention:      {err.prevention_protocol}",
                "",
            ])

        lines.extend([
            "=" * 78,
            "5. CONCLUSION:",
            f"Calculated HCl Molarity: {f'{conc_result.calculated_hcl_molarity_m:.4f} M' if conc_result else 'N/A'}",
            f"Calculated Mass Strength: {f'{conc_result.calculated_hcl_conc_g_per_l:.2f} g/L' if conc_result else 'N/A'}",
            f"Percentage Error:         {f'{conc_result.percentage_error:.2f}%' if conc_result else 'N/A'}",
            "=" * 78,
        ])

        txt_content = "\n".join(lines)
        if output_file_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

        return txt_content
