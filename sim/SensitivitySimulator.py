from typing import List

import numpy

from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from sim.OutcomeSimulator import OutcomeSimulator
from sim.ReactionSimulator import ReactionSimulator
from sim.SimulatorUtils import SimulatorUtils


class SensitivitySimulator(ReactionSimulator):
    FACTOR = 0.01  # TODO: Make a command line arg?

    def __init__(self, outcome_simulator):
        super().__init__()
        self.outcome_simulator = outcome_simulator

    def simulate_experiments(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism, previous_solutions=None):
        reference_results = experiment_set.all_simulated_experiments[0]
        if experiment_set.reaction == Reaction.SHOCKTUBE:
            self.outcome_simulator.shock_tube(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.PLUG_FLOW_REACTOR:
            self.outcome_simulator.plug_flow_reactor(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.JET_STREAM_REACTOR:
            self.outcome_simulator.jet_stream_reactor(experiment_set, experiments, mechanism, previous_solutions)
        elif experiment_set.reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            self.outcome_simulator.rapid_compression_machine(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.CONST_T_P:
            self.outcome_simulator.const_t_p(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.FREE_FLAME:
            self.outcome_simulator.free_flame(experiment_set, experiments, mechanism, previous_solutions)
        else:
            raise ValueError(f'Unknown reaction: {mechanism}')
        SensitivitySimulator.calculate_coefficients(experiment_set.get_target_species(), reference_results, experiments)

    @staticmethod
    def calculate_coefficients(targets: List[Species], reference_results: List[Experiment], experiments: List[Experiment]):
        for experiment_ndx in range(len(experiments)):
            for target in targets:
                reaction_data = experiments[experiment_ndx].results.get_target(target.name)
                reference_data = reference_results[experiment_ndx].results.get_target(target.name)
                sensitivity_coefficients = (reaction_data - reference_data) / (reference_data * SensitivitySimulator.FACTOR)
                experiments[experiment_ndx].results.set_target(target.name, sensitivity_coefficients)

    @staticmethod
    def requires_previous_solutions(reaction_type: Reaction):
        return reaction_type in (Reaction.JET_STREAM_REACTOR, Reaction.FREE_FLAME)

    def get_previous_solutions(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism):
        if experiment_set.reaction == Reaction.JET_STREAM_REACTOR:
            previous_solutions = self.outcome_simulator.jet_stream_reactor(experiment_set, experiments, mechanism)
            self.outcome_simulator.jet_stream_reactor(experiment_set, experiments, mechanism, previous_solutions)
        elif experiment_set.reaction == Reaction.FREE_FLAME:
            previous_solutions = self.outcome_simulator.free_flame(experiment_set, experiments, mechanism)
            self.outcome_simulator.free_flame(experiment_set, experiments, mechanism, previous_solutions)
        else:
            raise ValueError(f"{experiment_set.reaction} does not use previous solutions")
        return previous_solutions
