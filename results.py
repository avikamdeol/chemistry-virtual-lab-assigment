"""Module 10 — Results, Observations Table, and Concordance Analysis.

Records volumetric titration observations across rough and accurate trials:
- Initial burette reading (V1, mL)
- Final burette reading (V2, mL)
- Titre value (V2 - V1, mL)
- Endpoint pH and visual color observation
- Trial classification (Rough vs. Accurate)

Performs rigorous concordance analysis based on analytical chemistry standards:
- Identifies concordant trials agreeing within configurable tolerance (default 0.10 mL)
- Computes concordant mean titre only when at least two accurate trials are consistent
- Flags discordant/outlier trials and alerts student to perform additional runs
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from config import DEFAULT_CONCORDANCE_TOLERANCE_ML


@dataclass
class TitrationTrialRecord:
    """Record of a single titration run."""
    trial_number: int
    trial_type: str            # 'Rough' or 'Accurate'
    initial_reading_ml: float
    final_reading_ml: float
    titre_ml: float
    endpoint_ph: float
    observation_color: str
    is_concordant: bool = False
    notes: str = ""


@dataclass(frozen=True)
class ConcordanceAnalysisResult:
    """Summary of concordance evaluation across accurate trials."""
    total_trials: int
    rough_trials_count: int
    accurate_trials_count: int
    concordance_tolerance_ml: float
    has_concordance: bool
    concordant_trial_numbers: List[int]
    concordant_titres_ml: List[float]
    mean_titre_ml: Optional[float]
    status_message: str
    detailed_feedback: str


class ResultsTableManager:
    """Manages titration observations, record keeping, and statistical concordance."""

    def __init__(self, tolerance_ml: float = DEFAULT_CONCORDANCE_TOLERANCE_ML):
        self.tolerance_ml = tolerance_ml
        self.records: List[TitrationTrialRecord] = []

    def add_trial(
        self,
        trial_type: str,
        initial_reading_ml: float,
        final_reading_ml: float,
        endpoint_ph: float,
        observation_color: str,
        notes: str = "",
    ) -> TitrationTrialRecord:
        """Add a completed titration trial record."""
        trial_num = len(self.records) + 1
        titre = round(final_reading_ml - initial_reading_ml, 2)
        if titre < 0:
            raise ValueError(f"Final reading ({final_reading_ml}) cannot be less than initial ({initial_reading_ml})")

        rec = TitrationTrialRecord(
            trial_number=trial_num,
            trial_type=trial_type.capitalize(),
            initial_reading_ml=round(initial_reading_ml, 2),
            final_reading_ml=round(final_reading_ml, 2),
            titre_ml=titre,
            endpoint_ph=round(endpoint_ph, 2),
            observation_color=observation_color,
            is_concordant=False,
            notes=notes,
        )
        self.records.append(rec)
        self._update_concordance()
        return rec

    def _update_concordance(self) -> None:
        """Re-evaluate concordance tags across all accurate trials."""
        accurate_records = [r for r in self.records if r.trial_type == "Accurate"]
        # Reset all concordant flags
        for r in self.records:
            r.is_concordant = False

        if len(accurate_records) < 2:
            return

        # Find subset of accurate records that agree within tolerance
        best_concordant_indices = []
        for i in range(len(accurate_records)):
            group = [i]
            for j in range(len(accurate_records)):
                if i != j:
                    diff = abs(accurate_records[i].titre_ml - accurate_records[j].titre_ml)
                    if diff <= self.tolerance_ml:
                        group.append(j)
            if len(group) > len(best_concordant_indices):
                best_concordant_indices = group

        if len(best_concordant_indices) >= 2:
            for idx in best_concordant_indices:
                accurate_records[idx].is_concordant = True

    def analyze_concordance(self) -> ConcordanceAnalysisResult:
        """Perform formal concordance evaluation."""
        rough_count = sum(1 for r in self.records if r.trial_type == "Rough")
        accurate_records = [r for r in self.records if r.trial_type == "Accurate"]
        concordant_records = [r for r in accurate_records if r.is_concordant]

        if len(accurate_records) == 0:
            return ConcordanceAnalysisResult(
                total_trials=len(self.records),
                rough_trials_count=rough_count,
                accurate_trials_count=0,
                concordance_tolerance_ml=self.tolerance_ml,
                has_concordance=False,
                concordant_trial_numbers=[],
                concordant_titres_ml=[],
                mean_titre_ml=None,
                status_message="No accurate trials recorded yet.",
                detailed_feedback=(
                    "Only rough trials exist. Standard analytical protocol requires performing "
                    "at least two accurate titrations to establish concordant readings."
                ),
            )

        if len(accurate_records) == 1:
            return ConcordanceAnalysisResult(
                total_trials=len(self.records),
                rough_trials_count=rough_count,
                accurate_trials_count=1,
                concordance_tolerance_ml=self.tolerance_ml,
                has_concordance=False,
                concordant_trial_numbers=[accurate_records[0].trial_number],
                concordant_titres_ml=[accurate_records[0].titre_ml],
                mean_titre_ml=None,
                status_message="Single accurate trial recorded. Additional trial needed.",
                detailed_feedback=(
                    "A single titre cannot establish precision. Perform a second accurate titration "
                    f"to check for concordance within ±{self.tolerance_ml:.2f} mL."
                ),
            )

        if len(concordant_records) >= 2:
            titres = [r.titre_ml for r in concordant_records]
            mean_val = round(sum(titres) / len(titres), 2)
            trial_nums = [r.trial_number for r in concordant_records]
            return ConcordanceAnalysisResult(
                total_trials=len(self.records),
                rough_trials_count=rough_count,
                accurate_trials_count=len(accurate_records),
                concordance_tolerance_ml=self.tolerance_ml,
                has_concordance=True,
                concordant_trial_numbers=trial_nums,
                concordant_titres_ml=titres,
                mean_titre_ml=mean_val,
                status_message=f"Concordance achieved across Trials {trial_nums} (Mean: {mean_val:.2f} mL)",
                detailed_feedback=(
                    f"Success: {len(concordant_records)} accurate trials agree within the "
                    f"tolerance of ±{self.tolerance_ml:.2f} mL. The calculated concordant mean titre is "
                    f"{mean_val:.2f} mL, which will be used for stoichiometric concentration determination."
                ),
            )
        else:
            return ConcordanceAnalysisResult(
                total_trials=len(self.records),
                rough_trials_count=rough_count,
                accurate_trials_count=len(accurate_records),
                concordance_tolerance_ml=self.tolerance_ml,
                has_concordance=False,
                concordant_trial_numbers=[],
                concordant_titres_ml=[],
                mean_titre_ml=None,
                status_message=f"Discordant accurate trials (Difference > {self.tolerance_ml:.2f} mL)",
                detailed_feedback=(
                    f"Warning: Accurate trial titres diverge by more than the accepted limit of "
                    f"±{self.tolerance_ml:.2f} mL. Do not average discordant values; please conduct "
                    f"another careful accurate trial to achieve concordant readings."
                ),
            )

    def clear(self) -> None:
        """Clear all trial records."""
        self.records.clear()
