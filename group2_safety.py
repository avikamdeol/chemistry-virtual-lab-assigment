"""
Group 2 — Laboratory Safety Protocol
HCl-NaOH Virtual Titration Experiment
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

SAFETY_QUESTIONS = [
    "Are safety goggles being worn?",
    "Are protective gloves being worn?",
    "Is a laboratory coat being worn?",
    "Are closed-toe shoes being worn?",
    "Is long hair properly tied back?",
    "Is the working area clean and uncluttered?",
    "Is eating and drinking avoided in the lab?",
    "Are chemical handling and spill precautions understood?"
]


def display_welcome():
    print("=" * 50)
    print("       HCl-NaOH VIRTUAL TITRATION LAB")
    print("              SAFETY CHECK")
    print("=" * 50)
    print("\nPlease complete all safety checks.")
    print("Answer each question with Yes or No.\n")


def get_answer(question):
    while True:
        answer = input(question + " (Yes/No): ").strip().lower()
        if answer in ["yes", "y"]:
            return True
        elif answer in ["no", "n"]:
            return False
        else:
            print("Invalid input! Please enter Yes or No.")


def perform_safety_check():
    missing_precautions = []
    print("\n--- LABORATORY SAFETY CHECKLIST ---\n")
    for question in SAFETY_QUESTIONS:
        result = get_answer(question)
        if result:
            print(" [PASS] Safety requirement satisfied.\n")
        else:
            print(" [FAIL] Safety requirement not satisfied.\n")
            missing_precautions.append(question)
    return missing_precautions


def start_experiment():
    print("\n" + "=" * 50)
    print("ALL SAFETY CHECKS PASSED!")
    print("The virtual titration experiment can now begin.")
    print("=" * 50)


def block_experiment(missing_precautions):
    print("\n" + "=" * 50)
    print("SAFETY CHECK FAILED!")
    print("The experiment cannot be started.")
    print("=" * 50)
    print("\nMissing safety precautions:")
    for item in missing_precautions:
        print("- " + item)
    print("\nPlease complete all missing safety requirements")
    print("before attempting to start the experiment.")


def main():
    display_welcome()
    missing_precautions = perform_safety_check()
    if len(missing_precautions) == 0:
        start_experiment()
    else:
        block_experiment(missing_precautions)


if __name__ == "__main__":
    main()
