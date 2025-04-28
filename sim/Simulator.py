from typing import List

import numpy

from data.experiments.common.calculation_type import CalculationType
from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism
from sim.OutcomeSimulator import OutcomeSimulator
from sim.PathwaySimulator import PathwaySimulator
from sim.SensitivitySimulator import SensitivitySimulator


class Simulator:
    outcome_simulator: OutcomeSimulator = OutcomeSimulator()
    sensitivity_simulator: SensitivitySimulator = SensitivitySimulator(outcome_simulator)

    @staticmethod
    def run_experiment_set(experiment_set: ExperimentSet, mechanisms: List[Mechanism]):
        for mechanism in mechanisms:
            if experiment_set.calculation_type == CalculationType.OUTCOME or experiment_set.calculation_type == CalculationType.PATHWAY:
                Simulator.outcome_simulator.simulate_experiments(experiment_set, experiment_set.all_simulated_experiments[0], mechanism)

            elif experiment_set.calculation_type == CalculationType.SENSITIVITY:
                previous_solutions = None
                if SensitivitySimulator.requires_previous_solutions(experiment_set.reaction):
                    previous_solutions = Simulator.sensitivity_simulator.get_previous_solutions(experiment_set, experiment_set.all_simulated_experiments[0], mechanism)
                else:
                    Simulator.outcome_simulator.simulate_experiments(experiment_set, experiment_set.all_simulated_experiments[0], mechanism)
                    # add epsilon to prevent divide by 0
                    if experiment_set.reaction == Reaction.SHOCKTUBE:
                        experiment_set.all_simulated_experiments[0] += numpy.finfo(float).eps
                for reaction_ndx, experiments in enumerate(experiment_set.all_simulated_experiments[1:]):
                    mechanism.solution.set_multiplier(1.0)  # Reset all multipliers to original values
                    mechanism.solution.set_multiplier(1 + SensitivitySimulator.FACTOR, reaction_ndx)
                    Simulator.sensitivity_simulator.simulate_experiments(experiment_set, experiments, mechanism, previous_solutions)

            else:
                raise NotImplementedError(f"{experiment_set.calculation_type} does not have a simulator associated with "
                                          f"it yet.")
