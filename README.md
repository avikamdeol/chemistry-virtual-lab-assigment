# HCl–NaOH Potentiometric & Volumetric Titration — Virtual Chemistry Laboratory

An interactive, scientifically rigorous, and professional Virtual Chemistry Laboratory built with **Python 3**, **Tkinter**, and **Matplotlib**. Developed for First Semester B.Tech Engineering Chemistry students and faculty.

The laboratory simulates the quantitative determination of the unknown concentration of **Hydrochloric Acid (HCl)** by titrating against standard **0.100 M Sodium Hydroxide (NaOH)** using **phenolphthalein** indicator.

---

## 1. Experimental Overview & Theoretical Foundations

### Reaction Stoichiometry
$$\text{HCl (aq)} + \text{NaOH (aq)} \longrightarrow \text{NaCl (aq)} + \text{H}_2\text{O (l)}$$

Because $\text{HCl}$ is a strong monoprotic acid and $\text{NaOH}$ is a strong monobasic alkali, the reaction proceeds in a strictly **1:1 molar ratio**.

### Volumetric Law of Neutralisation
$$M_{\text{HCl}} \times V_{\text{HCl}} = M_{\text{NaOH}} \times V_{\text{NaOH}}$$
$$M_{\text{HCl}} = \frac{M_{\text{NaOH}} \times V_{\text{NaOH}}}{V_{\text{HCl}}}$$

### Experimental Constants & Parameters
| Parameter | Specification | Chemical Description |
| :--- | :--- | :--- |
| **Acid Aliquot ($V_{\text{HCl}}$)** | **$25.00\text{ mL}$** | Measured using a calibrated Class-A volumetric bulb pipette |
| **Unknown $\text{HCl}$ Reference** | **$0.0900\text{ M}$** | Simulation benchmark concentration ($3.2814\text{ g/L}$) |
| **Standard Titrant ($M_{\text{NaOH}}$)** | **$0.1000\text{ M}$** | Standardised analytical-grade titrant in the burette |
| **Theoretical Equivalence Vol** | **$22.50\text{ mL}$** | Calculated from formula: $(0.0900 \times 25.00) / 0.1000$ |
| **Indicator** | **Phenolphthalein** | Colorless lactone ($\text{pH} < 8.2$) $\rightarrow$ Faint Pink dianion ($\text{pH } 8.2\text{--}8.5$) |
| **Endpoint Criterion** | **First persistent faint pink** | Lasts $\ge 30\text{ seconds}$ after complete swirling |
| **Equivalence Point pH** | **$\text{pH } 7.00$ at $25^\circ\text{C}$** | Complete neutralisation yielding neutral aqueous $\text{NaCl}$ |

---

## 2. Modular Architecture (13 Group Tasks)

```
virtual_titration_lab/
│
├── main.py                     # [Group 13] Main Application & Master GUI Orchestrator
├── config.py                   # Physical, chemical, and UI design token configuration
├── lab_environment.py          # [Group 1] Virtual Lab Overview & Interactive Glassware Canvas
├── safety.py                   # [Group 2] Laboratory Safety Checklist & Protocol Gating
├── solution_preparation.py     # [Group 3] NaOH Mass Preparation & Stock Dilution Calculator
├── burette.py                  # [Group 4] 50 mL Class-A Burette with Precision Meniscus Tracking
├── flask.py                    # [Group 5] 25 mL Pipette & Erlenmeyer Flask Inventory Manager
├── indicator.py                # [Group 6] Phenolphthalein Chromophore & Persistence Model
├── ph_calculator.py            # [Group 7] Strong Acid-Base pH Calculation with Water Autoionisation
├── titration.py                # [Group 8] Rough & Accurate Titration State Machine Controller
├── titration_curve.py          # [Group 9] Embedded Matplotlib Live Potentiometric Curve & PNG Export
├── results.py                  # [Group 10] Volumetric Observation Table & Concordance Analyzer
├── concentration.py            # [Group 11] Stoichiometric Molarity, Strength (g/L), & Error Derivation
├── error_analysis.py           # [Group 12] Interactive 6-Scenario Laboratory Error Simulation Suite
├── report_generator.py         # [Group 13] Formal Laboratory Report Generator (HTML & TXT)
├── requirements.txt            # Python dependencies (matplotlib, pytest)
├── run.sh                      # Universal macOS/Linux launch & test script
├── run.bat                     # Windows launch script
│
├── tests/                      # Automated Verification & Unit Test Suite
│   ├── test_ph.py              # pH calculation & equivalence testing
│   ├── test_titration.py       # Burette, flask, indicator & controller workflow tests
│   ├── test_concentration.py   # Stoichiometry, solution prep & concordance tests
│   ├── test_errors.py          # All 6 experimental error model tests
│   └── test_complete_simulation.py # Full 13-stage end-to-end integration test
│
└── output/                     # Generated Reports & Graph Exports
    ├── graphs/                 # High-resolution PNG titration curve images
    └── reports/                # Formatted HTML and TXT academic lab reports
```

---

## 3. Installation & Quick Start

### Prerequisites
- Python 3.8+ (Python 3.11 recommended)
- Operating System: macOS, Windows, or Linux

### Installation
1. Clone or extract the `virtual_titration_lab` directory:
   ```bash
   cd virtual_titration_lab
   ```

2. Install the minimal dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Launching the Application
- **On macOS / Linux**:
  ```bash
  ./run.sh
  ```
  *(Or explicitly: `python3 main.py`)*

- **On Windows**:
  Double-click `run.bat` or run in Command Prompt:
  ```cmd
  run.bat
  ```

---

## 4. Running Automated Tests

Run the full automated test suite (23 comprehensive tests):

```bash
./run.sh test
```
*Or using pytest directly:*
```bash
pytest tests/ -v
```

All calculations are mathematically validated against known physical chemistry conditions:
- Initial $\text{HCl}$ moles = $0.00225\text{ mol}$
- Theoretical equivalence volume = $22.50\text{ mL}$
- Equivalence $\text{pH} = 7.000$ at $25^\circ\text{C}$
- Calculated $\text{HCl}$ molarity for $22.50\text{ mL}$ titre = $0.0900\text{ M}$
- Mass concentration = $3.28\text{ g/L}$
- Percentage error = $0.00\%$

---

## 5. Live Demonstration Guide for Professors & Teachers

Follow this 5-minute walkthrough to demonstrate the full virtual experiment:

### Step 1: Laboratory Overview & Apparatus (Tab 1)
- Explain the experiment aim, chemical reaction, and theoretical parameters.
- Point to the interactive apparatus canvas illustrating the $50\text{ mL}$ burette, $25\text{ mL}$ bulb pipette, conical flask, indicator dropper, and reagent bottles.

### Step 2: Safety Protocol Verification (Tab 2)
- Highlight the mandatory safety gating: show that titrating without PPE is blocked.
- Click **"Verify All Protocols"** (or check each item: goggles, coat, gloves, acid handling, emergency eyewash). The safety badge turns green (`SAFETY: VERIFIED & CLEAR`).

### Step 3: Solution Preparation Calculator (Tab 3)
- Demonstrate calculating the mass of solid $\text{NaOH}$ pellets:
  $$\text{Mass} = 0.100\text{ M} \times 0.250\text{ L} \times 40.00\text{ g/mol} = 1.0000\text{ g}$$
- Demonstrate stock dilution calculation ($M_1V_1 = M_2V_2$).

### Step 4: Interactive Titration Workbench (Tab 4)
- **Pipette Acid**: Click `1. Pipette 25 mL HCl`. The conical flask fills with acid, and the pH meter displays $\text{pH } 1.05$.
- **Add Indicator**: Click `2. Add Indicator (2 drops)`.
- **Rough Titration**:
  - Select *Rough Titration*.
  - Add in bursts ($+5\text{ mL}, +5\text{ mL}, +5\text{ mL}, +5\text{ mL}, +3\text{ mL}$).
  - At $23.00\text{ mL}$, the solution turns deep magenta ($\text{pH } 9.80$).
  - Click **Record Trial to Table**.
- **Accurate Titration**:
  - Click `Start Fresh Trial` and switch to *Accurate Titration*.
  - Click `1. Pipette 25 mL HCl` and `2. Add Indicator`.
  - Rapidly advance titrant to $21.00\text{ mL}$, then switch to dropwise increments ($+0.10\text{ mL}, +0.05\text{ mL}$).
  - As volume approaches $22.50\text{ mL}$, observe the steep sigmoidal rise on the real-time Matplotlib curve!
  - At $22.50\text{ mL}$, the first persistent faint blush pink appears ($\text{pH } 8.30$).
  - Click **Record Trial to Table**.
  - Repeat for a second accurate trial ($22.50\text{ mL}$) to achieve concordance.

### Step 5: Observations & Concordance (Tab 5)
- Inspect the observation table. Note that Trials 2 and 3 are flagged as **Concordant** ($|22.50 - 22.50| \le 0.10\text{ mL}$).
- The concordant mean titre is established as **$22.50\text{ mL}$**.

### Step 6: HCl Concentration & Derivation (Tab 6)
- Review the quantitative derivation:
  $$M_{\text{HCl}} = \frac{0.1000\text{ M} \times 22.50\text{ mL}}{25.00\text{ mL}} = 0.0900\text{ M}$$
  $$\text{Strength} = 0.0900\text{ M} \times 36.46\text{ g/mol} = 3.28\text{ g/L}$$
  $$\text{Percentage Error} = 0.00\%$$

### Step 7: Error Analysis Laboratory (Tab 7)
- Select the error scenarios to explain classical laboratory anomalies:
  1. **Overshoot (+1.50 mL)**: Deep pink $\rightarrow$ falsely **HIGHER** $M_{\text{HCl}}$ ($0.0960\text{ M}$).
  2. **Undershoot (-0.80 mL)**: Premature stop $\rightarrow$ falsely **LOWER** $M_{\text{HCl}}$ ($0.0872\text{ M}$).
  3. **Air bubble in burette tip**: Falsely **HIGHER** $M_{\text{HCl}}$.
  4. **Water drops in conical flask**: Moles of $\text{H}^+$ are unchanged $\rightarrow$ Result is **UNCHANGED** (100% accurate!).

### Step 8: Final Report Export (Tab 8)
- Click **Export HTML Report** and open the generated file in any web browser.
- Displays the complete formal report with student metadata, verified safety checklist, observation table, embedded potentiometric curve, derivations, error analysis, and conclusions.

---

## 6. Viva Voce Chemistry Concepts

1. **Why is the equivalence point pH exactly 7.00 for $\text{HCl}$–$\text{NaOH}$?**
   $\text{HCl}$ and $\text{NaOH}$ are a strong acid and strong base that ionise completely in aqueous solution. At stoichiometric equivalence, all $\text{H}^+$ and $\text{OH}^-$ ions neutralise to form water ($\text{H}_2\text{O}$) and neutral salt ($\text{NaCl}$). Neither $\text{Na}^+$ nor $\text{Cl}^-$ undergoes hydrolysis, so $[\text{H}^+] = [\text{OH}^-] = \sqrt{K_w} = 1.0 \times 10^{-7}\text{ M}$ at $25^\circ\text{C}$ ($\text{pH} = 7.00$).

2. **Why can phenolphthalein (transition pH 8.2–10.0) be used even though equivalence is pH 7.00?**
   The strong acid–strong base titration curve has an extremely steep vertical inflection extending from $\text{pH } 4.0$ to $\text{pH } 10.0$ over less than a fraction of a drop ($\approx 0.02\text{ mL}$) of titrant. Therefore, the volume difference between equivalence ($\text{pH } 7.00$) and the phenolphthalein endpoint ($\text{pH } 8.2\text{--}8.3$) is experimentally negligible ($< 0.1\%$).

3. **Why does residual deionised water in the conical flask not affect the titre?**
   Titration relies strictly on the *number of moles* of acid present ($n = M \times V$). Pipetting $25.00\text{ mL}$ of $0.0900\text{ M }\text{HCl}$ delivers exactly $0.00225\text{ mol}$ of $\text{H}^+$. Adding deionised water increases total volume but leaves the moles of $\text{H}^+$ unchanged. Consequently, the exact same moles of $\text{NaOH}$ ($22.50\text{ mL}$) are required for neutralisation.

---

## 7. License & Academic Attribution
Developed for First Semester B.Tech Engineering Chemistry Laboratory Courseware. Designed in modular Python 3 architecture with zero external paid APIs.
