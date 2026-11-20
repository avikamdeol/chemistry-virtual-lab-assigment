"""
Group 1 — Virtual Laboratory Environment
HCl-NaOH Titration Overview and Aim
"""

import tkinter as tk
from tkinter import messagebox


def create_group1_frame(parent, on_enter_callback=None):
    """Create the Group 1 laboratory overview frame."""
    frame = tk.Frame(parent, bg="#eaf4f4", padx=20, pady=20)

    heading = tk.Label(
        frame,
        text="VIRTUAL CHEMISTRY LABORATORY",
        font=("Arial", 20, "bold"),
        bg="#eaf4f4",
        fg="#145a66"
    )
    heading.pack(pady=15)

    experiment = tk.Label(
        frame,
        text="HCl - NaOH Titration",
        font=("Arial", 16, "bold"),
        bg="#eaf4f4",
        fg="#222222"
    )
    experiment.pack(pady=5)

    aim_title = tk.Label(
        frame, text="Aim",
        font=("Arial", 13, "bold"),
        bg="#eaf4f4"
    )
    aim_title.pack(pady=(15, 3))

    aim_text = tk.Label(
        frame,
        text="To determine the concentration of an unknown HCl solution\n"
             "by titrating it against standard NaOH solution.",
        font=("Arial", 11),
        bg="#eaf4f4"
    )
    aim_text.pack()

    reaction_title = tk.Label(
        frame, text="Chemical Reaction",
        font=("Arial", 13, "bold"),
        bg="#eaf4f4"
    )
    reaction_title.pack(pady=(15, 3))

    reaction_text = tk.Label(
        frame,
        text="HCl + NaOH -> NaCl + H2O",
        font=("Arial", 12, "bold"),
        bg="#eaf4f4",
        fg="#145a66"
    )
    reaction_text.pack()

    settings_title = tk.Label(
        frame, text="Experimental Settings",
        font=("Arial", 13, "bold"),
        bg="#eaf4f4"
    )
    settings_title.pack(pady=(15, 5))

    settings_text = tk.Label(
        frame,
        text="HCl volume in flask : 25.00 mL\n"
             "NaOH concentration : 0.100 M\n"
             "Indicator : Phenolphthalein\n"
             "Reference HCl concentration: 0.0900 M\n"
             "Theoretical equivalence volume: 22.50 mL",
        font=("Arial", 11),
        justify="left",
        bg="#eaf4f4"
    )
    settings_text.pack()

    apparatus_title = tk.Label(
        frame, text="Apparatus Required",
        font=("Arial", 13, "bold"),
        bg="#eaf4f4"
    )
    apparatus_title.pack(pady=(15, 3))

    apparatus_text = tk.Label(
        frame,
        text="Burette | Pipette | Conical Flask | Stand | Indicator",
        font=("Arial", 11),
        bg="#eaf4f4"
    )
    apparatus_text.pack()

    def start_lab():
        if on_enter_callback:
            on_enter_callback()
        else:
            messagebox.showinfo(
                "Virtual Lab",
                "Virtual laboratory environment is ready!\n"
                "Proceed to the next group module."
            )

    start_button = tk.Button(
        frame,
        text="Enter Virtual Lab",
        font=("Arial", 12, "bold"),
        bg="#145a66",
        fg="white",
        cursor="hand2",
        command=start_lab
    )
    start_button.pack(pady=25)

    return frame


def launch_standalone():
    """Launch Group 1 as standalone window."""
    window = tk.Tk()
    window.title("Virtual Chemistry Lab - HCl NaOH Titration (Group 1)")
    window.geometry("700x600")
    window.configure(bg="#eaf4f4")
    f = create_group1_frame(window)
    f.pack(fill=tk.BOTH, expand=True)
    window.mainloop()


if __name__ == "__main__":
    launch_standalone()
