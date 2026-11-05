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
            item_id="lab_coat",
            title="Wear Buttoned Lab Coat",
            category="PPE",
            is_mandatory=True,
            hazard_rationale=(
                "Both 0.1 M NaOH and 0.09 M HCl cause degradation of personal clothing "
                "and can leach onto skin upon accidental splashing."
            ),
            guidance="Standard 100% cotton lab coat fastened completely to wrists.",
        ),
        SafetyItem(
            item_id="safety_goggles",
            title="Wear Splash-Resistant Safety Goggles",
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
            title="Wear Chemical-Resistant Nitrile Gloves",
            category="PPE",
            is_mandatory=True,
            hazard_rationale=(
                "Hydrochloric acid causes skin irritation and burns. NaOH causes slippery "
                "caustic chemical burns on epidermis."
            ),
            guidance="Powder-free disposable nitrile gloves; change immediately if contaminated.",
        ),
        SafetyItem(
            item_id="clean_apparatus",
            title="Inspect Clean & Crack-Free Glassware",
            category="Apparatus",
            is_mandatory=True,
            hazard_rationale=(
                "Hairline cracks in burettes or flasks can catastrophically fracture under liquid "
                "pressure, dispersing chemical solutions across bench surfaces."
            ),
            guidance="Inspect burette barrel, tip, stopcock seal, and pipette bulb for flaws.",
        ),
        SafetyItem(
            item_id="hcl_handling",
            title="Safe Handling of Hydrochloric Acid (HCl)",
            category="Chemical Protocol",
            is_mandatory=True,
            hazard_rationale=(
                "HCl solutions emit acidic vapour. Pipetting must never be performed by mouth; "
                "acid must always be transferred using a rubber suction bulb or pipette pump."
            ),
            guidance="Never pipette by mouth. Keep stock bottles capped when not withdrawing.",
        ),
        SafetyItem(
            item_id="naoh_handling",
            title="Safe Handling of Sodium Hydroxide (NaOH)",
            category="Chemical Protocol",
            is_mandatory=True,
            hazard_rationale=(
                "Solid NaOH is strongly hygroscopic and dissolves exothermically in water, "
                "generating significant local heat that can crack glass if added too quickly."
            ),
            guidance="Dissolve slowly in cold water with constant stirring; store in polyethylene bottles.",
        ),
        SafetyItem(
            item_id="spill_eyewash",
            title="Locate Eyewash Station, Safety Shower & Spill Kit",
            category="Emergency",
            is_mandatory=True,
            hazard_rationale=(
                "Immediate 15-minute continuous water flushing is the essential first response "
                "for acid or alkali splashes in eyes or on skin."
            ),
            guidance="Know exact route to emergency shower, eyewash fountain, and neutralising spill kit.",
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
