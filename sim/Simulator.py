from typing import List

import numpy

from data.experiments.common.calculation_type import CalculationType
from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism
from sim.OutcomeSimulator import OutcomeSimulator
from sim.SensitivitySimulator import SensitivitySimulator
from sim.SimulatorUtils import SimulatorUtils


class Simulator:
    outcome_simulator: OutcomeSimulator = OutcomeSimulator()
    sensitivity_simulator: SensitivitySimulator = SensitivitySimulator()

    @staticmethod
    def run_experiment_set(experiment_set: ExperimentSet, mechanisms: List[Mechanism]) -> List[ExperimentSet]:
        simulated_experiment_sets: List[ExperimentSet] = []
        for mechanism in mechanisms:
            curr_experiment_set: ExperimentSet = experiment_set.copy()
            SimulatorUtils.rename_all_species(curr_experiment_set, mechanism)
            if curr_experiment_set.calculation_type == CalculationType.OUTCOME or curr_experiment_set.calculation_type == CalculationType.PATHWAY:
                Simulator.outcome_simulator.simulate_experiments(curr_experiment_set, curr_experiment_set.all_simulated_experiments[0], mechanism)

            elif curr_experiment_set.calculation_type == CalculationType.SENSITIVITY:
                Simulator.outcome_simulator.simulate_experiments(curr_experiment_set, curr_experiment_set.all_simulated_experiments[0], mechanism)
                if curr_experiment_set.reaction == Reaction.SHOCKTUBE:
                    # add epsilon to prevent divide by 0
                    curr_experiment_set.all_simulated_experiments[0] += numpy.finfo(float).eps
                for reaction_ndx, experiments in enumerate(curr_experiment_set.all_simulated_experiments[1:]):
                    mechanism.solution.set_multiplier(1.0)  # Reset all multipliers to original values
                    mechanism.solution.set_multiplier(1 + SensitivitySimulator.FACTOR, reaction_ndx)
                    Simulator.sensitivity_simulator.simulate_experiments(curr_experiment_set, experiments, mechanism)

            else:
                raise NotImplementedError(f"{curr_experiment_set.calculation_type} does not have a simulator associated with "
                                          f"it yet.")
            simulated_experiment_sets.append(curr_experiment_set)

        return simulated_experiment_sets
