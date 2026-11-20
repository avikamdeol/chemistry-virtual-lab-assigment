"""
Group 5 - Pipette & Conical Flask Lab  (Python / matplotlib port)

25.00 mL HCl is pipetted into a conical flask and titrated with 0.100 M NaOH
using phenolphthalein. Red dots = H+, blue dots = OH-, cyan rings = neutralised.

Requires: numpy, matplotlib      ->   pip install numpy matplotlib
Run:      python group5_titration_lab.py
"""
import heapq
import itertools
import math
import random
import time
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle
from matplotlib.transforms import Affine2D
from matplotlib.widgets import Button

# ----------------------------------------------------------------- constants
HCL, NAOH = 0.09, 0.100      # mol/L
CAP = 250                     # flask capacity, mL
DROP = 0.05                   # mL per drop (burette / indicator)
MAXD = 5                      # max indicator drops
UNIT = 7.5e-5                 # mol represented by one dot
FLASK_HOME, FLASK_PIPETTE, FLASK_Y = 380, 110, 240

FLASK_OUTLINE = [(-14, 0), (-14, 40), (-55, 112), (-52, 121), (-44, 124),
                 (44, 124), (52, 121), (55, 112), (14, 40), (14, 0)]


# ----------------------------------------------------------------- chemistry
def ph_calc(acid_ml, naoh_ml, extra_ml):
    """pH of HCl + NaOH mixture (strong acid / strong base)."""
    if acid_ml <= 0:
        return None
    excess = HCL * acid_ml / 1000 - NAOH * naoh_ml / 1000     # mol
    vol = (acid_ml + naoh_ml + extra_ml) / 1000                # L
    if abs(excess) < 1e-9:
        return 7.0
    if excess > 0:
        return -math.log10(excess / vol)
    return 14 + math.log10(-excess / vol)


class Lab:
    def __init__(self):
        self.heap, self.counter = [], itertools.count()
        self.log_lines = deque(maxlen=8)
        self.busy = 0
        self.drip_id = 0
        self.dripping = False
        self.fx, self.fx_target = FLASK_HOME, FLASK_HOME
        self.swirl_t0 = None
        self.drop_t0 = None
        self.stream_on = False
        self.particles, self.rings = [], []
        self.trail = []
        self.banner_text = ""
        self.fresh()
        self.build_ui()
        self.ok("Ready. Rinse, fill and deliver the acid, or press Auto-run demo.")
        self.render()

    # ------------------------------------------------------------- state
    def fresh(self):
        self.rinsed = self.filled = self.ep = False
        self.acid = self.tit = 0.0
        self.drops = 0

    def total(self):
        return round(self.acid + self.drops * DROP + self.tit, 4)

    def ph(self):
        return ph_calc(self.acid, self.tit, self.drops * DROP)

    def colour(self, p):
        if p is None or self.drops == 0 or p < 8.2:
            return "colourless", "#8ec5ff", 0.45
        t = min(1.0, (p - 8.2) / 2.8)
        rgb = ((247 - 23 * t) / 255, (198 - 147 * t) / 255, (220 - 80 * t) / 255)
        return ("faint pink" if t < .35 else "pink"), rgb, 0.6 + 0.3 * t

    # ------------------------------------------------------------- logging
    def log(self, msg, colour="#1d2330"):
        self.log_lines.append((msg, colour))

    def ok(self, msg):
        self.log(msg, "#2e7d32")
        return True

    def err(self, msg):
        self.log("Error: " + msg, "#c62828")
        return False

    # ------------------------------------------------------------- scheduler
    def schedule(self, delay_ms, fn):
        heapq.heappush(self.heap, (time.time() + delay_ms / 1000, next(self.counter), fn))

    def run_due(self):
        now = time.time()
        while self.heap and self.heap[0][0] <= now:
            _, _, fn = heapq.heappop(self.heap)
            fn()

    def U(self, fn, *args):
        """Run a user action unless something is in progress."""
        if self.busy > 0:
            self.err("Please wait for the current action to finish.")
        else:
            fn(*args)
        self.render()

    # ------------------------------------------------------------- actions
    def do_rinse(self):
        self.rinsed = True
        self.ok("Pipette rinsed with HCl solution.")

    def do_fill(self):
        if self.filled:
            return self.err("Pipette is already full.")
        self.filled = True
        self.ok("Pipette filled to the 25.00 mL mark.")

    def do_deliver(self):
        if not self.filled:
            return self.err("Pipette is empty. Fill it before delivering.")
        if self.acid > 0:
            return self.err("Acid sample already in flask. Use a clean flask.")
        self.busy += 1
        self.fx_target = FLASK_PIPETTE

        def pour():
            self.stream_on = True
            self.filled = False
            self.acid = 25.0
            self.trail = [(0.0, self.ph())]
            self.ok("Delivered 25.00 mL HCl into the flask.")

        def back():
            self.stream_on = False
            self.fx_target = FLASK_HOME

        def done():
            self.busy -= 1

        self.schedule(1050, pour)
        self.schedule(2450, back)
        self.schedule(3500, done)

    def do_ind(self, n):
        if self.acid <= 0:
            return self.err("Add the acid sample before the indicator.")
        if self.tit > 0:
            return self.err("Indicator must be added before titration begins.")
        if self.drops + n > MAXD:
            return self.err(f"Too much indicator (max {MAXD} drops).")
        self.drops += n
        self.ok(f"{n} drop(s) of phenolphthalein added. Still colourless in acid.")

    def do_naoh(self, v, quiet=False):
        if self.acid <= 0:
            return self.err("No acid in the flask yet.")
        if self.drops == 0:
            return self.err("Add indicator before titrating.")
        if self.tit + v > 50 + 1e-9:
            return self.err("Burette is empty (50 mL capacity).")
        if self.total() + v > CAP + 1e-9:
            return self.err(f"Flask overflow: capacity is {CAP} mL.")
        self.tit = round(self.tit + v, 4)
        self.drop_t0 = time.time()
        if not quiet:
            self.ok(f"+{v:.2f} mL NaOH. Total volume = {self.total():.2f} mL.")
        self.trail.append((self.tit, self.ph()))
        if not self.ep and self.drops > 0 and self.ph() >= 8.2:
            self.ep = True
            self.banner_text = (f"Endpoint reached: first faint pink at {self.tit:.2f} mL "
                                f"(theoretical equivalence 22.50 mL).")
            self.ok(f"Endpoint! Faint pink appears at {self.tit:.2f} mL.")
            return "ep"
        return True

    def do_swirl(self):
        if self.acid <= 0:
            return self.err("Nothing to swirl yet.")
        self.swirl_t0 = time.time()
        for q in self.particles:
            q["vx"] *= 3
            q["vy"] *= 3
        self.ok("Flask swirled; contents mixed.")

    def do_reset(self):
        self.drip_id += 1
        self.dripping = False
        self.fresh()
        self.trail = []
        self.banner_text = ""
        self.log_lines.clear()
        self.fx_target = FLASK_HOME
        self.stream_on = False
        self.ok("Flask and pipette reset.")

    def toggle_drip(self):
        if self.dripping:
            self.dripping = False
            self.log(f"Stopped dripping at {self.tit:.2f} mL.")
            return
        self.dripping = True
        self.drip_id += 1
        my_id = self.drip_id

        def step():
            if not self.dripping or self.drip_id != my_id:
                return
            if self.do_naoh(DROP, quiet=True) is True:
                self.schedule(130, step)
            else:
                self.dripping = False
        self.schedule(0, step)

    def do_auto(self):
        if self.busy > 0:
            return
        self.busy += 1
        t = 0

        def at(dt, fn):
            nonlocal t
            t += dt
            self.schedule(t, fn)

        at(0, self.do_reset)
        at(600, self.do_rinse)
        at(900, self.do_fill)
        at(1400, self.do_deliver)
        at(4000, lambda: self.do_ind(2))
        for _ in range(4):
            at(650, lambda: self.do_naoh(5))
        at(500, self.do_swirl)
        at(700, lambda: self.do_naoh(1))
        at(600, lambda: self.do_naoh(1))
        for _ in range(5):
            at(550, lambda: self.do_naoh(0.1))

        def finish_loop():
            if not self.ep and self.tit < 40:
                self.do_naoh(DROP)
                self.schedule(450, finish_loop)
            else:
                self.busy -= 1
        at(450, finish_loop)

    # ------------------------------------------------------------- particles
    @staticmethod
    def wall_half_width(y):
        return 13 if y < 40 else 13 + (y - 40) * .57

    def liquid_top(self):
        return 124 - min(1.0, self.total() / 100) * 80

    def spawn(self, kind):
        top = self.liquid_top()
        y = top + 4 + random.random() * max(4, 116 - top)
        w = self.wall_half_width(y) - 6
        q = dict(t=kind, x=random.uniform(-1, 1) * w, y=y,
                 vx=random.random() - .5, vy=random.random() - .5)
        self.particles.append(q)
        return q

    def pop(self, q):
        if q in self.particles:
            self.particles.remove(q)
        self.rings.append((q["x"], q["y"], time.time()))

    def adjust(self, kind, n):
        lst = [q for q in self.particles if q["t"] == kind]
        while len(lst) < n:
            lst.append(self.spawn(kind))
        while len(lst) > n:
            self.pop(lst.pop())

    def sync_particles(self):
        ex = HCL * self.acid / 1000 - NAOH * self.tit / 1000
        nh = min(60, max(1, round(ex / UNIT))) if ex > 5e-7 else 0
        no = min(60, max(1, round(-ex / UNIT))) if ex < -5e-7 else 0
        if self.acid <= 0:
            nh = no = 0
        self.adjust("H", nh)
        self.adjust("O", no)

    def move_particles(self):
        top = self.liquid_top()
        for q in self.particles:
            q["vx"] = max(-.8, min(.8, q["vx"] + (random.random() - .5) * .14))
            q["vy"] = max(-.8, min(.8, q["vy"] + (random.random() - .5) * .14))
            q["x"] += q["vx"]
            q["y"] += q["vy"]
            if q["y"] < top + 3:
                q["y"], q["vy"] = top + 3, abs(q["vy"])
            if q["y"] > 119:
                q["y"], q["vy"] = 119, -abs(q["vy"])
            w = self.wall_half_width(q["y"]) - 4
            if q["x"] > w:
                q["x"], q["vx"] = w, -abs(q["vx"])
            if q["x"] < -w:
                q["x"], q["vx"] = -w, abs(q["vx"])

    # ------------------------------------------------------------- UI build
    def build_ui(self):
        self.fig = plt.figure(figsize=(13, 8.2))
        self.fig.canvas.manager.set_window_title("Group 5 - Pipette & Conical Flask Lab")
        self.fig.patch.set_facecolor("#f3f5f9")
        self.fig.text(0.02, 0.975, "Group 5 – Pipette & Conical Flask Lab", fontsize=16,
                      weight="bold", va="top")
        self.fig.text(0.02, 0.945,
                      "25.00 mL HCl is pipetted into the flask and titrated with 0.100 M NaOH "
                      "using phenolphthalein.", fontsize=9, color="#5d6678", va="top")
        self.banner = self.fig.text(0.02, 0.905, "", fontsize=10, weight="bold", color="white",
                                    va="top", bbox=dict(boxstyle="round,pad=0.4", fc="#e91e8c",
                                                        ec="none"), visible=False)

        # ---- scene (SVG coordinate system: y grows downward)
        ax = self.ax = self.fig.add_axes([0.02, 0.40, 0.52, 0.46])
        ax.set_xlim(0, 540)
        ax.set_ylim(400, 0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 540, 365, fc="#e4ecf7", ec="none"))
        ax.add_patch(Rectangle((0, 365), 540, 35, fc="#b8956a", ec="none"))
        # stand
        ax.add_patch(Rectangle((440, 356), 90, 9, fc="#6b7280", ec="none"))
        ax.add_patch(Rectangle((482, 30), 6, 326, fc="#6b7280", ec="none"))
        ax.add_patch(Rectangle((388, 62), 100, 6, fc="#7b8494", ec="none"))
        ax.add_patch(Rectangle((368, 54), 24, 22, fc="none", ec="#7b8494", lw=2.5))
        # burette
        ax.text(380, 12, "NaOH burette", ha="center", fontsize=8, color="#5d6678")
        self.bl = Rectangle((373, 24), 14, 168, fc="#7db9f5", ec="none", alpha=.75)
        ax.add_patch(self.bl)
        ax.add_patch(Rectangle((372, 20), 16, 172, fc="#8cb4dc", alpha=.16, ec="#3b4458", lw=1.8))
        for i, ml in enumerate(range(0, 51, 10)):
            y = 24 + i * 33.6
            ax.plot([372, 379], [y, y], c="#3b4458", lw=1)
            ax.text(366, y + 3, str(ml), ha="right", fontsize=7, color="#5d6678")
        ax.plot([368, 392], [196, 196], c="#2563eb", lw=3, solid_capstyle="round")
        ax.add_patch(Polygon([(375, 200), (380, 214), (385, 200)], fc="#8cb4dc", alpha=.3,
                             ec="#3b4458", lw=1.8))
        ax.text(398, 112, "reading", fontsize=7, color="#5d6678")
        self.bread = ax.text(398, 126, "0.00 mL", fontsize=10, weight="bold")
        # pipette
        ax.text(110, 28, "25.00 mL pipette", ha="center", fontsize=8, color="#5d6678")
        self.pl_bulb = Ellipse((110, 96), 34, 50, fc="#7db9f5", ec="none", alpha=.8, visible=False)
        self.pl_stem = Rectangle((106, 70), 8, 132, fc="#7db9f5", ec="none", alpha=.8, visible=False)
        ax.add_patch(self.pl_bulb)
        ax.add_patch(self.pl_stem)
        glass = dict(fc="#8cb4dc", alpha=.16, ec="#3b4458", lw=1.8)
        ax.add_patch(Rectangle((105, 40), 10, 30, **glass))
        ax.add_patch(Ellipse((110, 96), 36, 52, **glass))
        ax.add_patch(Rectangle((105, 122), 10, 80, **glass))
        ax.add_patch(Polygon([(105, 202), (110, 220), (115, 202)], **glass))
        ax.plot([100, 120], [150, 150], c="#3b4458", lw=1.8)
        ax.text(124, 154, "mark", fontsize=7, color="#5d6678")
        self.stream, = ax.plot([110, 110], [220, 300], c="#7db9f5", lw=2.5, ls=(0, (2, 1.7)),
                               visible=False)
        self.drop = Circle((380, 218), 3.5, fc="#7db9f5", ec="none", visible=False)
        ax.add_patch(self.drop)
        # flask (transform is updated every frame)
        self.T = Affine2D().translate(FLASK_HOME, FLASK_Y)
        tr = self.T + ax.transData
        self.flask = Polygon(FLASK_OUTLINE, closed=True, fc="#8cb4dc", ec="#3b4458", lw=2.2,
                             alpha=1, transform=tr)
        self.flask.set_facecolor((0.55, 0.71, 0.86, 0.16))
        ax.add_patch(self.flask)
        self.liq = Rectangle((-70, 124), 140, 140, ec="none", transform=tr)
        ax.add_patch(self.liq)
        self.liq.set_clip_path(self.flask)
        self.pts = ax.scatter([], [], s=22, zorder=5)
        self.pts.set_clip_path(self.flask)
        self.ring_sc = ax.scatter([], [], s=[], facecolors="none", zorder=6)
        self.ring_sc.set_clip_path(self.flask)
        ax.add_patch(Polygon(FLASK_OUTLINE, closed=True, fc="none", ec="#3b4458", lw=2.2,
                             transform=tr, zorder=7))
        ax.plot([-19, 19], [0, 0], c="#3b4458", lw=2.5, solid_capstyle="round", transform=tr)
        ax.text(0, 144, "250 mL conical flask", ha="center", fontsize=8, color="#5d6678",
                transform=tr)
        # legend
        ax.scatter([], [], c="#e53935", s=25, label="H⁺ (acid)")
        ax.scatter([], [], c="#1e88e5", s=25, label="OH⁻ (excess base)")
        ax.scatter([], [], fc="none", ec="#26c6da", s=25, label="neutralised to H₂O")
        ax.scatter([], [], c="none", label="1 dot ≈ 7.5×10⁻⁵ mol")
        ax.legend(loc="lower left", ncol=2, fontsize=7.5, frameon=False,
                  bbox_to_anchor=(0, -0.12))

        # ---- titration curve
        ac = self.ac = self.fig.add_axes([0.07, 0.07, 0.45, 0.25])
        ac.set_xlim(0, 40)
        ac.set_ylim(0, 14)
        ac.set_xlabel("NaOH added (mL)", fontsize=9)
        ac.set_ylabel("pH", fontsize=9)
        ac.set_title("Live titration curve", fontsize=9, color="#5d6678", loc="left")
        ac.axhspan(8.2, 10, color="#e91e8c", alpha=.12)
        ac.text(0.5, 9.0, "phenolphthalein range 8.2–10", fontsize=7, color="#5d6678",
                va="center")
        ac.axvline(22.5, c="#2e7d32", ls="--", lw=1)
        ac.text(23, 12.8, "22.50 mL", fontsize=7, color="#2e7d32")
        v = np.linspace(0, 40, 401)
        ac.plot(v, [ph_calc(25, x, 0) for x in v], c="#5d6678", lw=1.5, alpha=.5)
        self.trail_line, = ac.plot([], [], c="#2563eb", lw=2.2)
        self.cur_pt, = ac.plot([], [], "o", c="#2563eb", mec="white", ms=7)

        # ---- right-hand controls
        specs = [
            ("1 Rinse", lambda e: self.U(self.do_rinse)),
            ("2 Fill", lambda e: self.U(self.do_fill)),
            ("3 Deliver 25.00 mL", lambda e: self.U(self.do_deliver)),
            ("4 Add 2 drops", lambda e: self.U(self.do_ind, 2)),
            ("+1 drop", lambda e: self.U(self.do_ind, 1)),
            ("Swirl", lambda e: self.U(self.do_swirl)),
            ("+0.10 mL", lambda e: self.U(self.do_naoh, .1)),
            ("+1 mL", lambda e: self.U(self.do_naoh, 1)),
            ("+5 mL", lambda e: self.U(self.do_naoh, 5)),
            ("+10 mL", lambda e: self.U(self.do_naoh, 10)),
            ("Drip on/off", lambda e: self.U(self.toggle_drip)),
            ("Reset", lambda e: self.U(self.do_reset)),
            ("Auto-run demo", lambda e: (self.do_auto(), self.render())),
        ]
        self.buttons = []
        for i, (label, cb) in enumerate(specs):
            r, c = divmod(i, 3)
            bax = self.fig.add_axes([0.57 + c * 0.14, 0.88 - r * 0.055, 0.13, 0.045])
            b = Button(bax, label, color="#eef1f6", hovercolor="#dbe6ff")
            b.label.set_fontsize(8.5)
            b.on_clicked(cb)
            self.buttons.append(b)

        self.fig.text(0.57, 0.575, "PROCEDURE", fontsize=8, weight="bold", color="#5d6678")
        self.steps_txt = [self.fig.text(0.57 + (i % 2) * 0.21, 0.545 - (i // 2) * 0.03, "",
                                        fontsize=9) for i in range(6)]
        self.fig.text(0.57, 0.435, "FLASK READOUT", fontsize=8, weight="bold", color="#5d6678")
        self.ph_txt = self.fig.text(0.57, 0.375, "–", fontsize=26, weight="bold")
        self.sw = Circle((0.69, 0.385), 0.014, transform=self.fig.transFigure, fc="none",
                         ec="#3b4458", lw=2)
        self.fig.add_artist(self.sw)
        self.col_txt = self.fig.text(0.715, 0.385, "colourless", fontsize=10, weight="bold")
        self.table_txt = self.fig.text(0.57, 0.345, "", fontsize=9, family="monospace",
                                       va="top", linespacing=1.4)
        self.fig.text(0.57, 0.185, "LAB LOG", fontsize=8, weight="bold", color="#5d6678")
        self.log_txt = [self.fig.text(0.57, 0.16 - i * 0.019, "", fontsize=8, family="monospace")
                        for i in range(8)]

    # ------------------------------------------------------------- render
    def render(self):
        t, p = self.total(), self.ph()
        name, fill, op = self.colour(p)
        self.liq.set_y(self.liquid_top())
        self.liq.set_facecolor(fill)
        self.liq.set_alpha(op)
        self.pl_bulb.set_visible(self.filled)
        self.pl_stem.set_visible(self.filled)
        by = 24 + min(self.tit, 50) / 50 * 168
        self.bl.set_y(by)
        self.bl.set_height(192 - by)
        self.bread.set_text(f"{self.tit:.2f} mL")

        self.ph_txt.set_text("–" if p is None else f"{p:.2f}")
        self.col_txt.set_text(name)
        self.sw.set_facecolor("none" if name == "colourless" else fill)
        self.table_txt.set_text(
            f"Acid (HCl)     {self.acid:>9.2f} mL\n"
            f"Indicator      {self.drops:>3d} drop{'s' if self.drops != 1 else ' '}\n"
            f"NaOH added     {self.tit:>9.2f} mL\n"
            f"Total volume   {t:>5.2f} / {CAP} mL\n"
            f"n(HCl) initial {HCL * self.acid / 1000:>11.3e} mol\n"
            f"n(NaOH) added  {NAOH * self.tit / 1000:>11.3e} mol")
        steps = [("Rinse pipette", self.rinsed),
                 ("Fill to the mark", self.filled or self.acid > 0),
                 ("Deliver 25.00 mL HCl", self.acid > 0),
                 ("Add indicator", self.drops > 0),
                 ("Titrate with NaOH", self.tit > 0),
                 ("Faint-pink endpoint", self.ep)]
        for txt, (label, done) in zip(self.steps_txt, steps):
            txt.set_text(("✔ " if done else "○ ") + label)
            txt.set_color("#2e7d32" if done else "#5d6678")
            txt.set_weight("bold" if done else "normal")
        lines = list(self.log_lines)
        for i, txt in enumerate(self.log_txt):
            if i < len(lines):
                txt.set_text(lines[-(i + 1)][0][:62])
                txt.set_color(lines[-(i + 1)][1])
            else:
                txt.set_text("")
        self.banner.set_visible(bool(self.banner_text))
        self.banner.set_text(self.banner_text)

        if self.trail:
            xs, ys = zip(*self.trail)
            self.trail_line.set_data(xs, ys)
            self.cur_pt.set_data([xs[-1]], [ys[-1]])
        else:
            self.trail_line.set_data([], [])
            self.cur_pt.set_data([], [])
        self.sync_particles()

    # ------------------------------------------------------------- animation
    def frame(self, _):
        self.run_due()
        now = time.time()
        # flask slides between bench and pipette
        self.fx += (self.fx_target - self.fx) * 0.12
        angle = 0.0
        if self.swirl_t0 is not None:
            s = (now - self.swirl_t0) / 0.65
            if s >= 1:
                self.swirl_t0 = None
            else:
                angle = 6 * math.sin(s * 2 * math.pi) * (1 - s)
        self.T.clear().rotate_deg(-angle).translate(self.fx, FLASK_Y)
        self.stream.set_visible(self.stream_on)
        # falling burette drop
        if self.drop_t0 is not None:
            f = (now - self.drop_t0) / 0.32
            if f >= 1:
                self.drop_t0 = None
                self.drop.set_visible(False)
            else:
                self.drop.center = (380, 218 + 42 * f)
                self.drop.set_alpha(1 - 0.9 * f)
                self.drop.set_visible(True)
        # ions
        self.move_particles()
        if self.particles:
            self.pts.set_offsets([(self.fx + q["x"], FLASK_Y + q["y"]) for q in self.particles])
            self.pts.set_facecolors(["#e53935" if q["t"] == "H" else "#1e88e5"
                                     for q in self.particles])
        else:
            self.pts.set_offsets(np.empty((0, 2)))
        # neutralisation rings
        self.rings = [r for r in self.rings if now - r[2] < 0.65]
        if self.rings:
            self.ring_sc.set_offsets([(self.fx + x, FLASK_Y + y) for x, y, _ in self.rings])
            self.ring_sc.set_sizes([30 * (1 + 3.5 * (now - t0) / 0.65) ** 2 / 4
                                    for _, _, t0 in self.rings])
            self.ring_sc.set_edgecolors([(0.15, 0.78, 0.85, 1 - (now - t0) / 0.65)
                                         for _, _, t0 in self.rings])
        else:
            self.ring_sc.set_offsets(np.empty((0, 2)))
        # keep readouts fresh while scheduled actions run
        if self.heap or self.busy:
            self.render()
        return []


def main():
    lab = Lab()
    lab.anim = FuncAnimation(lab.fig, lab.frame, interval=33, blit=False,
                             cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()
