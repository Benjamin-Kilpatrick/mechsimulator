from typing import List

from data.experiments.common.calculation_type import CalculationType
from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism
from sim.OutcomeSimulator import OutcomeSimulator
from sim.PathwaySimulator import PathwaySimulator
from sim.SensitivitySimulator import SensitivitySimulator


class Simulator:
    outcome_simulator: OutcomeSimulator = OutcomeSimulator()
    sensitivity_simulator: SensitivitySimulator = SensitivitySimulator()

    @staticmethod
    def run_experiment_set(experiment_set: ExperimentSet, mechanism: List[Mechanism]):
        if experiment_set.calculation_type == CalculationType.OUTCOME:
            Simulator.outcome_simulator.simulate_experiment_set(experiment_set, mechanism)
        elif experiment_set.calculation_type == CalculationType.PATHWAY:  # TODO: reconcile differing measurement types
            PathwaySimulator.simulate_experiment_set(experiment_set, mechanism)
            Simulator.outcome_simulator.simulate_experiment_set(experiment_set, mechanism)
        elif experiment_set.calculation_type == CalculationType.SENSITIVITY:
            Simulator.sensitivity_simulator.simulate_experiment_set(experiment_set, mechanism)
        else:
            raise NotImplementedError(f"{experiment_set.calculation_type} does not have a simulator associated with "
                                      f"it yet.")
