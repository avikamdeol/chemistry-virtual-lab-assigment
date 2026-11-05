"""Module 8 — Titration Procedure State Machine and Experiment Controller.

Coordinates the complete interactive titration workflow across physical apparatus:
- Integrates VirtualBurette, ConicalFlask, PhenolphthaleinIndicator, and PHCalculator
- Manages Rough Titration mode (fast macroscopic exploratory additions)
- Manages Accurate Titration mode (dropwise fine-volume additions near endpoint)
- Implements continuous endpoint surveillance and persistence tracking
- Emits real-time telemetry (pH, volume, ionic concentrations, color, state)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable
from config import (
    ACID_VOLUME_ML,
    TRUE_HCL_CONCENTRATION_M,
    NAOH_CONCENTRATION_M,
    THEORETICAL_EQUIVALENCE_VOLUME_ML,
)
from burette import VirtualBurette, BuretteReading
from flask import ConicalFlask, FlaskContentsSnapshot
from ph_calculator import PHCalculator, TitrationState
from indicator import IndicatorObservation


class TitrationMode(Enum):
    ROUGH = "Rough"
    ACCURATE = "Accurate"


class ExperimentStatus(Enum):
    STANDBY = "Standby (Safety & Prep Required)"
    READY = "Ready to Begin Trial"
    PIPETTING_ACID = "Transferring 25.00 mL HCl Sample"
    ADDING_INDICATOR = "Adding Phenolphthalein Indicator"
    IN_PROGRESS = "Titration In Progress"
    PAUSED = "Titration Paused"
    ENDPOINT_REACHED = "Endpoint Reached (Faint Pink Persistent)"
    OVERTITRATED = "Over-titrated (Excess Base Dispensed)"
    TRIAL_COMPLETED = "Trial Completed & Recorded"


@dataclass(frozen=True)
class TitrationTelemetry:
    """Comprehensive instantaneous snapshot of the active titration."""
    trial_number: int
    mode: TitrationMode
    status: ExperimentStatus
    burette_initial_ml: float
    burette_current_ml: float
    titrant_dispensed_ml: float
    flask_total_volume_ml: float
    ph: float
    poh: float
    h_conc: float
    oh_conc: float
    color_hex: str
    color_name: str
    is_endpoint: bool
    is_overtitrated: bool
    status_message: str


class TitrationController:
    """Master controller coordinating apparatus and protocol execution."""

    def __init__(
        self,
        true_hcl_m: float = TRUE_HCL_CONCENTRATION_M,
        naoh_m: float = NAOH_CONCENTRATION_M,
        acid_vol_ml: float = ACID_VOLUME_ML,
    ):
        self.true_hcl_m = true_hcl_m
        self.naoh_m = naoh_m
        self.acid_vol_ml = acid_vol_ml

        # Apparatus instances
        self.burette = VirtualBurette()
        self.flask = ConicalFlask(true_hcl_conc_m=true_hcl_m, naoh_conc_m=naoh_m)
        self.ph_calc = PHCalculator(acid_vol_ml=acid_vol_ml, acid_conc_m=true_hcl_m, base_conc_m=naoh_m)

        # State tracking
        self.current_trial_num: int = 1
        self.current_mode: TitrationMode = TitrationMode.ROUGH
        self.status: ExperimentStatus = ExperimentStatus.READY
        self.endpoint_recorded: bool = False
        self.endpoint_volume_ml: Optional[float] = None
        self.endpoint_ph: Optional[float] = None

        # Telemetry listeners
        self._listeners: List[Callable[[TitrationTelemetry], None]] = []

    def subscribe(self, callback: Callable[[TitrationTelemetry], None]) -> None:
        """Register a callback for telemetry updates."""
        self._listeners.append(callback)

    def _notify(self) -> None:
        """Broadcast current telemetry to all registered listeners."""
        telemetry = self.get_telemetry()
        for callback in self._listeners:
            try:
                callback(telemetry)
            except Exception:
                pass

    def setup_new_trial(self, mode: TitrationMode, trial_num: Optional[int] = None) -> None:
        """Prepare fresh apparatus for a new titration trial."""
        if trial_num is not None:
            self.current_trial_num = trial_num
        self.current_mode = mode
        self.endpoint_recorded = False
        self.endpoint_volume_ml = None
        self.endpoint_ph = None

        # Reset flask and burette
        self.flask.reset()
        self.burette.fill_to_mark(0.00)
        self.status = ExperimentStatus.READY
        self._notify()

    def pipette_acid(self) -> None:
        """Transfer 25.00 mL of unknown HCl into the flask."""
        self.flask.pipette_hcl_sample(self.acid_vol_ml)
        self.status = ExperimentStatus.READY
        self._notify()

    def add_indicator(self, drops: int = 2) -> None:
        """Add phenolphthalein drops to the flask."""
        self.flask.add_indicator(drops)
        self.status = ExperimentStatus.READY
        self._notify()

    def dispense_titrant(self, volume_ml: float) -> float:
        """Dispense a given volume of NaOH titrant from burette into flask."""
        if self.status == ExperimentStatus.PAUSED:
            return 0.00
        if not self.flask.has_acid:
            raise RuntimeError("Cannot dispense titrant: Acid sample has not been pipetted into flask.")
        if self.flask.indicator.drops_added == 0:
            raise RuntimeError("Cannot titrate accurately: Indicator has not been added to flask.")

        actual_dispensed = self.burette.dispense(volume_ml)
        if actual_dispensed > 0:
            self.flask.receive_naoh(actual_dispensed)
            self.status = ExperimentStatus.IN_PROGRESS

            # Check for endpoint or overtitration
            snapshot = self.flask.get_snapshot()
            obs = self.flask.indicator.evaluate(snapshot.ph, swirled=True)

            if obs.is_endpoint and not self.endpoint_recorded:
                self.endpoint_recorded = True
                self.endpoint_volume_ml = self.burette.total_delivered_ml
                self.endpoint_ph = snapshot.ph
                self.status = ExperimentStatus.ENDPOINT_REACHED

            elif obs.is_overtitrated:
                if not self.endpoint_recorded:
                    self.endpoint_recorded = True
                    self.endpoint_volume_ml = self.burette.total_delivered_ml
                    self.endpoint_ph = snapshot.ph
                self.status = ExperimentStatus.OVERTITRATED

        self._notify()
        return actual_dispensed

    def swirl_flask(self) -> None:
        """Swirl the conical flask to ensure complete mixing."""
        self.flask.swirl()
        self._notify()

    def pause(self) -> None:
        """Pause active titration."""
        if self.status == ExperimentStatus.IN_PROGRESS:
            self.status = ExperimentStatus.PAUSED
            self._notify()

    def resume(self) -> None:
        """Resume paused titration."""
        if self.status == ExperimentStatus.PAUSED:
            self.status = ExperimentStatus.IN_PROGRESS
            self._notify()

    def get_telemetry(self) -> TitrationTelemetry:
        """Generate instantaneous telemetry snapshot."""
        b_reading = self.burette.get_reading()
        f_snapshot = self.flask.get_snapshot()

        total_delivered = self.burette.total_delivered_ml
        state = self.ph_calc.calculate_ph(total_delivered) if f_snapshot.has_acid else None
        ph = state.ph if state else 7.00
        poh = state.poh if state else 7.00
        h_conc = state.h_concentration if state else 1.0e-7
        oh_conc = state.oh_concentration if state else 1.0e-7

        msg = f"Status: {self.status.value}"
        if self.status == ExperimentStatus.ENDPOINT_REACHED:
            msg = f"ENDPOINT DETECTED at {b_reading.delivered_volume_ml:.2f} mL (pH {ph:.2f})!"
        elif self.status == ExperimentStatus.OVERTITRATED:
            msg = f"OVER-TITRATED at {b_reading.delivered_volume_ml:.2f} mL (pH {ph:.2f}) — Deep Pink."

        return TitrationTelemetry(
            trial_number=self.current_trial_num,
            mode=self.current_mode,
            status=self.status,
            burette_initial_ml=b_reading.initial_reading_ml,
            burette_current_ml=b_reading.current_reading_ml,
            titrant_dispensed_ml=b_reading.delivered_volume_ml,
            flask_total_volume_ml=f_snapshot.total_volume_ml,
            ph=ph,
            poh=poh,
            h_conc=h_conc,
            oh_conc=oh_conc,
            color_hex=f_snapshot.color_hex,
            color_name=f_snapshot.color_name,
            is_endpoint=self.endpoint_recorded,
            is_overtitrated=(self.status == ExperimentStatus.OVERTITRATED),
            status_message=msg,
        )
