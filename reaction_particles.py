"""
Submicroscopic Reaction Particle Simulator
HCl + NaOH -> NaCl + H2O  (H+ + OH- -> H2O)

Models the submicroscopic molecular view of strong acid - strong base neutralization.
Tracks individual H+, OH-, H2O, Na+, and Cl- particles, their Brownian drifting,
attractive collisions, neutralization reaction flashes, and particle balance.
"""

import math
import random
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Tuple, Optional


class Particle:
    """Submicroscopic ion or molecule in aqueous solution."""
    def __init__(self, x: float, y: float, p_type: str, vx: float = 0.0, vy: float = 0.0):
        self.x = x
        self.y = y
        self.p_type = p_type  # 'H', 'OH', 'H2O', 'Na', 'Cl'
        self.vx = vx or random.uniform(-0.8, 0.8)
        self.vy = vy or random.uniform(-0.8, 0.8)
        self.radius = 6 if p_type in ('H', 'OH') else (8 if p_type == 'H2O' else 5)
        self.glow_timer = 0  # for neutralization sparkle animation

        # Colors
        if p_type == 'H':
            self.color = "#ef4444"       # Glowing Acidic Red
            self.label = "H⁺"
            self.text_color = "#ffffff"
        elif p_type == 'OH':
            self.color = "#3b82f6"      # Alkaline Deep Blue
            self.label = "OH⁻"
            self.text_color = "#ffffff"
        elif p_type == 'H2O':
            self.color = "#06b6d4"      # Neutral Water Cyan
            self.label = "H₂O"
            self.text_color = "#083344"
        elif p_type == 'Na':
            self.color = "#f59e0b"      # Amber Spectator Cation
            self.label = "Na⁺"
            self.text_color = "#000000"
        elif p_type == 'Cl':
            self.color = "#10b981"      # Emerald Spectator Anion
            self.label = "Cl⁻"
            self.text_color = "#000000"


class ParticleReactionChamber:
    """Manages 2D physics, boundaries, and chemical reaction collisions."""
    def __init__(self, bounds: Tuple[float, float, float, float] = (10, 10, 290, 190)):
        # bounds: (min_x, min_y, max_x, max_y)
        self.min_x, self.min_y, self.max_x, self.max_y = bounds
        self.particles: List[Particle] = []
        self.neutralized_count: int = 0
        self.sparkles: List[Dict] = []  # temporary sparks upon reaction

    def reset(self) -> None:
        self.particles.clear()
        self.neutralized_count = 0
        self.sparkles.clear()

    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def add_acid(self, count: int = 4) -> None:
        """Add HCl (H+ and Cl- ions)."""
        for _ in range(count):
            x = random.uniform(self.min_x + 10, self.max_x - 10)
            y = random.uniform(self.min_y + 10, self.min_y + 40)
            self.particles.append(Particle(x, y, 'H', random.uniform(-0.6, 0.6), random.uniform(0.5, 1.2)))
            # spectator Cl-
            self.particles.append(Particle(x + random.uniform(-8, 8), y, 'Cl', random.uniform(-0.5, 0.5), random.uniform(0.4, 1.0)))

    def add_base(self, count: int = 4) -> None:
        """Add NaOH (OH- and Na+ ions)."""
        for _ in range(count):
            x = random.uniform(self.min_x + 10, self.max_x - 10)
            y = self.min_y + 5
            self.particles.append(Particle(x, y, 'OH', random.uniform(-0.5, 0.5), random.uniform(1.0, 1.8)))
            # spectator Na+
            self.particles.append(Particle(x + random.uniform(-8, 8), y, 'Na', random.uniform(-0.5, 0.5), random.uniform(0.8, 1.5)))

    def step(self, trapezoid_bottom_w: Optional[float] = None) -> None:
        """Advance physical positions, check wall bounces and chemical reaction."""
        # 1. Update sparkles
        for sp in self.sparkles:
            sp["age"] += 1
            sp["radius"] += 0.8
        self.sparkles = [sp for sp in self.sparkles if sp["age"] < 12]

        # 2. Move particles
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vx += random.uniform(-0.04, 0.04)
            p.vy += random.uniform(-0.04, 0.04)

            # Dampen excessive velocities
            p.vx = max(-1.8, min(1.8, p.vx))
            p.vy = max(-1.8, min(1.8, p.vy))

            # Wall boundaries
            if trapezoid_bottom_w is not None:
                # Conical flask trapezoid boundary calculation
                # top width is narrower than bottom width
                frac = max(0.0, min(1.0, (p.y - self.min_y) / max(1.0, self.max_y - self.min_y)))
                half_w = 20.0 + frac * (trapezoid_bottom_w / 2.0 - 20.0)
                center_x = (self.min_x + self.max_x) / 2.0
                if p.x < center_x - half_w + p.radius:
                    p.x = center_x - half_w + p.radius
                    p.vx = abs(p.vx) * 0.8
                elif p.x > center_x + half_w - p.radius:
                    p.x = center_x + half_w - p.radius
                    p.vx = -abs(p.vx) * 0.8
            else:
                if p.x - p.radius < self.min_x:
                    p.x = self.min_x + p.radius
                    p.vx = abs(p.vx)
                elif p.x + p.radius > self.max_x:
                    p.x = self.max_x - p.radius
                    p.vx = -abs(p.vx)

            # Top and bottom boundaries
            if p.y - p.radius < self.min_y:
                p.y = self.min_y + p.radius
                p.vy = abs(p.vy)
            elif p.y + p.radius > self.max_y:
                p.y = self.max_y - p.radius
                p.vy = -abs(p.vy)

        # 3. Electrostatic attraction and reaction between H+ and OH-
        h_particles = [p for p in self.particles if p.p_type == 'H']
        oh_particles = [p for p in self.particles if p.p_type == 'OH']

        # Mutual electrostatic drift toward nearest opposite ion
        for oh in oh_particles:
            closest_h = None
            min_dist = 9999.0
            for h in h_particles:
                dist = math.hypot(h.x - oh.x, h.y - oh.y)
                if dist < min_dist:
                    min_dist = dist
                    closest_h = h

            if closest_h and min_dist < 60.0:
                dx = closest_h.x - oh.x
                dy = closest_h.y - oh.y
                if min_dist > 0:
                    attract = 0.25 / min_dist
                    oh.vx += dx * attract
                    oh.vy += dy * attract
                    closest_h.vx -= dx * attract
                    closest_h.vy -= dy * attract

        # Collision & Neutralization check
        reacted_h = set()
        reacted_oh = set()

        for h in h_particles:
            if h in reacted_h:
                continue
            for oh in oh_particles:
                if oh in reacted_oh:
                    continue
                dist = math.hypot(h.x - oh.x, h.y - oh.y)
                if dist <= (h.radius + oh.radius + 2.0):
                    # Collision! Neutralization Reaction Occurs: H+ + OH- -> H2O
                    reacted_h.add(h)
                    reacted_oh.add(oh)
                    rx = (h.x + oh.x) / 2.0
                    ry = (h.y + oh.y) / 2.0

                    # Spawn neutral H2O molecule
                    water_mol = Particle(rx, ry, 'H2O', (h.vx + oh.vx) * 0.4, (h.vy + oh.vy) * 0.4)
                    self.particles.append(water_mol)
                    self.neutralized_count += 1

                    # Neutralization sparkle energy flash
                    self.sparkles.append({
                        "x": rx,
                        "y": ry,
                        "radius": 4.0,
                        "age": 0,
                        "color": "#38bdf8"
                    })
                    break

        # Remove reacted ions
        if reacted_h or reacted_oh:
            self.particles = [p for p in self.particles if p not in reacted_h and p not in reacted_oh]

    def get_counts(self) -> Dict[str, int]:
        counts = {'H': 0, 'OH': 0, 'H2O': 0, 'Na': 0, 'Cl': 0}
        for p in self.particles:
            if p.p_type in counts:
                counts[p.p_type] += 1
        return counts

    def get_chemical_condition(self) -> str:
        c = self.get_counts()
        if c['H'] > c['OH']:
            return "Acidic (Excess H⁺ Ions)"
        elif c['H'] == c['OH'] and c['H2O'] > 0:
            return "Neutral Equivalence Point (100% Neutralised to H₂O)"
        elif c['OH'] > c['H']:
            return "Alkaline / Basic (Excess OH⁻ Ions)"
        return "Pure Aqueous Solvent"


class InteractiveReactionWidget(ttk.Frame):
    """Rich interactive GUI panel demonstrating H+ + OH- -> H2O molecular reaction."""
    def __init__(self, parent, width: int = 500, height: int = 240, **kwargs):
        super().__init__(parent, **kwargs)
        self.width = width
        self.height = height
        self.chamber = ParticleReactionChamber(bounds=(15, 15, width - 15, height - 35))
        self.is_running = True
        self.auto_demo_job = None

        self._build_ui()
        self._seed_initial_state()
        self._start_animation_loop()

    def _build_ui(self) -> None:
        # Header banner
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(
            header,
            text="SUBMICROSCOPIC MOLECULAR REACTION:  H⁺ + OH⁻  ⟶  H₂O",
            font=("Helvetica", 11, "bold"),
            foreground="#38bdf8"
        ).pack(side=tk.LEFT)

        self.state_lbl = ttk.Label(
            header,
            text="State: Acidic (Excess H⁺)",
            font=("Helvetica", 9, "bold"),
            foreground="#ef4444"
        )
        self.state_lbl.pack(side=tk.RIGHT)

        # Particle Canvas
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#080c14",
            highlightthickness=1,
            highlightbackground="#2d3c52"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control & Counters Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(6, 0))

        add_acid_btn = ttk.Button(toolbar, text="+ Add Acid (HCl)", command=self._add_acid_burst)
        add_acid_btn.pack(side=tk.LEFT, padx=2)

        add_base_btn = ttk.Button(toolbar, text="+ Add Base (NaOH)", command=self._add_base_burst)
        add_base_btn.pack(side=tk.LEFT, padx=2)

        demo_btn = ttk.Button(toolbar, text="▶ Auto-Titrate Demo", command=self._toggle_auto_demo)
        demo_btn.pack(side=tk.LEFT, padx=6)
        self.demo_btn = demo_btn

        reset_btn = ttk.Button(toolbar, text="⟲ Reset", command=self._reset_chamber)
        reset_btn.pack(side=tk.LEFT, padx=2)

        # Live Counts Badge
        self.counts_lbl = ttk.Label(
            toolbar,
            text="H⁺: 12  |  OH⁻: 0  |  H₂O: 0  |  Na⁺: 0  |  Cl⁻: 12",
            font=("Menlo", 9, "bold"),
            foreground="#38bdf8"
        )
        self.counts_lbl.pack(side=tk.RIGHT, padx=4)

    def _seed_initial_state(self) -> None:
        """Seed initial acid solution with H+ and Cl- ions."""
        self.chamber.reset()
        self.chamber.add_acid(count=12)

    def _add_acid_burst(self) -> None:
        self.chamber.add_acid(count=4)

    def _add_base_burst(self) -> None:
        self.chamber.add_base(count=4)

    def _reset_chamber(self) -> None:
        self._stop_auto_demo()
        self._seed_initial_state()

    def _toggle_auto_demo(self) -> None:
        if self.auto_demo_job:
            self._stop_auto_demo()
        else:
            self.demo_btn.config(text="⏹ Stop Demo")
            self._seed_initial_state()
            self._run_auto_demo_step(step=0)

    def _run_auto_demo_step(self, step: int) -> None:
        if step < 8:
            # Drop 2 base pairs every 500ms
            self.chamber.add_base(count=3)
            self.auto_demo_job = self.after(550, lambda: self._run_auto_demo_step(step + 1))
        else:
            self._stop_auto_demo()

    def _stop_auto_demo(self) -> None:
        if self.auto_demo_job:
            self.after_cancel(self.auto_demo_job)
            self.auto_demo_job = None
        self.demo_btn.config(text="▶ Auto-Titrate Demo")

    def _start_animation_loop(self) -> None:
        def update():
            if not self.winfo_exists():
                return
            self.chamber.step()
            self._render_canvas()
            self.after(30, update)  # ~33 fps smooth simulation

        self.after(50, update)

    def _render_canvas(self) -> None:
        c = self.canvas
        c.delete("all")
        w = self.canvas.winfo_width() or self.width
        h = self.canvas.winfo_height() or self.height
        self.chamber.set_bounds(15, 15, w - 15, h - 25)

        # 1. Beaker/Chamber Glass Outline
        c.create_rectangle(10, 10, w - 10, h - 20, outline="#334155", width=1.5, fill="#0b1120")
        # Aqueous solvent subtle tint
        c.create_rectangle(11, 25, w - 11, h - 21, outline="", fill="#0f172a")

        # 2. Render Neutralization Energy Sparkles
        for sp in self.chamber.sparkles:
            r = sp["radius"]
            c.create_oval(
                sp["x"] - r, sp["y"] - r, sp["x"] + r, sp["y"] + r,
                outline="#38bdf8", width=1.5, fill=""
            )
            # Energy flash rays
            c.create_line(sp["x"] - r * 1.5, sp["y"], sp["x"] + r * 1.5, sp["y"], fill="#ffffff", width=1)
            c.create_line(sp["x"], sp["y"] - r * 1.5, sp["x"], sp["y"] + r * 1.5, fill="#ffffff", width=1)

        # 3. Render Particles
        for p in self.chamber.particles:
            r = p.radius
            if p.p_type == 'H2O':
                # Water molecule representation: central oxygen ring with 2 white hydrogen dots
                c.create_oval(p.x - r, p.y - r, p.x + r, p.y + r, fill="#083344", outline="#06b6d4", width=2)
                # Two small hydrogen atoms bonded at ~104.5 degrees
                c.create_oval(p.x - r - 2, p.y - 3, p.x - r + 2, p.y + 1, fill="#ffffff", outline="#06b6d4", width=1)
                c.create_oval(p.x + r - 2, p.y - 3, p.x + r + 2, p.y + 1, fill="#ffffff", outline="#06b6d4", width=1)
                c.create_text(p.x, p.y, text="H₂O", font=("Helvetica", 6, "bold"), fill="#67e8f9")
            else:
                # Spherical ion with charge symbol
                c.create_oval(p.x - r, p.y - r, p.x + r, p.y + r, fill=p.color, outline="#ffffff", width=1)
                c.create_text(p.x, p.y, text=p.label, font=("Helvetica", 6, "bold"), fill=p.text_color)

        # 4. Update Header Counts and Condition
        counts = self.chamber.get_counts()
        cond_text = self.chamber.get_chemical_condition()
        self.counts_lbl.config(
            text=f"🔴 H⁺: {counts['H']}  |  🔵 OH⁻: {counts['OH']}  |  ⭕ H₂O: {counts['H2O']}  |  Na⁺: {counts['Na']}  |  Cl⁻: {counts['Cl']}"
        )
        self.state_lbl.config(text=f"State: {cond_text}")
        if counts['H'] > counts['OH']:
            self.state_lbl.config(foreground="#ef4444")
        elif counts['H'] == counts['OH'] and counts['H2O'] > 0:
            self.state_lbl.config(foreground="#10b981")
        else:
            self.state_lbl.config(foreground="#3b82f6")
