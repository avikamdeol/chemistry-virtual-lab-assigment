"""Module 2 — Laboratory Safety Protocol and Pre-experiment Verification.

Enforces mandatory laboratory safety standards before chemical simulation begins:
- Personal Protective Equipment (PPE): Lab coat, safety goggles, chemical-resistant gloves
- Chemical Hazard Awareness: Corrosive HCl (acid), Caustic NaOH (strong alkali)
- Operational Safety: Apparatus inspection, spill management, eyewash protocol

Prevents experiment initiation if any mandatory precaution is unverified,
providing informative chemical safety guidance.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass(frozen=True)
class SafetyItem:
    """Specification of an individual laboratory safety precaution."""
    item_id: str
    title: str
    category: str
    is_mandatory: bool
    hazard_rationale: str
    guidance: str


class LaboratorySafetySystem:
    """Safety verification checklist and protocol enforcement engine."""

    PRECAUTIONS: List[SafetyItem] = [
        SafetyItem(
            item_id="goggles",
            title="Are safety goggles being worn?",
            category="PPE",
            is_mandatory=True,
            hazard_rationale=(
                "Sodium hydroxide (NaOH) is a severe corneal hazard. Alkaline solutions "
                "saponify ocular fats causing permanent blindness within seconds of contact."
            ),
            guidance="ANSI Z87.1 certified chemical splash goggles with side shields.",
        ),
        SafetyItem(
            item_id="gloves",
            title="Are protective gloves being worn?",
            category="PPE",
            is_mandatory=True,
            hazard_rationale=(
                "Hydrochloric acid causes skin irritation and burns. NaOH causes slippery "
                "caustic chemical burns on epidermis."
            ),
            guidance="Powder-free disposable nitrile gloves; change immediately if contaminated.",
        ),
        SafetyItem(
            item_id="lab_coat",
            title="Is a laboratory coat being worn?",
            category="PPE",
            is_mandatory=True,
            hazard_rationale=(
                "Both 0.1 M NaOH and 0.09 M HCl cause degradation of personal clothing "
                "and can leach onto skin upon accidental splashing."
            ),
            guidance="Standard 100% cotton lab coat fastened completely to wrists.",
        ),
        SafetyItem(
            item_id="shoes",
            title="Are closed-toe shoes being worn?",
            category="PPE",
            is_mandatory=True,
            hazard_rationale="Protects feet against falling glassware fragments and spilled corrosive liquids.",
            guidance="Leather or synthetic closed-toe footwear completely covering feet.",
        ),
        SafetyItem(
            item_id="hair",
            title="Is long hair properly tied back?",
            category="Personal Safety",
            is_mandatory=True,
            hazard_rationale="Prevents hair from coming into contact with chemicals, apparatus, or reagents.",
            guidance="Tie hair securely back behind shoulders.",
        ),
        SafetyItem(
            item_id="clean_area",
            title="Is the working area clean and uncluttered?",
            category="Workplace Safety",
            is_mandatory=True,
            hazard_rationale="Clutter increases the risk of tipping over volumetric glassware or reagent bottles.",
            guidance="Clear benchtop of backpacks, unnecessary papers, and non-essential items.",
        ),
        SafetyItem(
            item_id="no_eating",
            title="Is eating and drinking avoided in the lab?",
            category="Hygiene Protocol",
            is_mandatory=True,
            hazard_rationale="Prevents accidental ingestion of toxic or corrosive chemicals via contaminated hands or food.",
            guidance="No food, beverages, chewing gum, or water bottles allowed in laboratory.",
        ),
        SafetyItem(
            item_id="chemical_handling",
            title="Are chemical handling and spill precautions understood?",
            category="Emergency Protocol",
            is_mandatory=True,
            hazard_rationale=(
                "Immediate 15-minute continuous water flushing is the essential first response "
                "for acid or alkali splashes in eyes or on skin."
            ),
            guidance="Know location of eyewash, safety shower, and neutralising spill kits.",
        ),
    ]

    def __init__(self):
        self._checked_items: Dict[str, bool] = {
            item.item_id: False for item in self.PRECAUTIONS
        }

    def set_item_checked(self, item_id: str, is_checked: bool) -> None:
        """Update checked state for a precaution."""
        if item_id in self._checked_items:
            self._checked_items[item_id] = bool(is_checked)

    def is_item_checked(self, item_id: str) -> bool:
        """Check if an item has been verified."""
        return self._checked_items.get(item_id, False)

    def verify_all_mandatory(self) -> Tuple[bool, List[SafetyItem], str]:
        """Verify whether all mandatory safety precautions have been checked.
        
        Returns:
            Tuple of:
            - is_safe (bool)
            - missing_items (List[SafetyItem])
            - feedback_message (str)
        """
        missing: List[SafetyItem] = []
        for item in self.PRECAUTIONS:
            if item.is_mandatory and not self._checked_items.get(item.item_id, False):
                missing.append(item)

        if not missing:
            return (
                True,
                [],
                "All mandatory safety requirements verified. Chemical simulation cleared to proceed.",
            )

        missing_titles = [f"• {m.title} ({m.hazard_rationale})" for m in missing]
        msg = (
            f"SAFETY CHECK FAILED: Cannot begin titration experiment.\n"
            f"The following {len(missing)} mandatory precaution(s) have not been verified:\n"
            + "\n".join(missing_titles)
            + "\n\nPlease review and verify all safety measures to protect personnel."
        )
        return (False, missing, msg)

    def reset(self) -> None:
        """Reset all checklist verifications."""
        for item_id in self._checked_items:
            self._checked_items[item_id] = False
