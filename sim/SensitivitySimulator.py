from typing import List

import numpy

from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from sim.OutcomeSimulator import OutcomeSimulator
from sim.ReactionSimulator import ReactionSimulator


class SensitivitySimulator(ReactionSimulator):
    FACTOR = 0.01

    def __init__(self):
        super().__init__()
        self.outcomeSimulator = OutcomeSimulator()

    def simulate_experiments(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        reference_results = experiment_set.all_simulated_experiments[0]
        if experiment_set.reaction == Reaction.SHOCKTUBE:
            self.outcomeSimulator.shock_tube(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.PLUG_FLOW_REACTOR:
            self.outcomeSimulator.plug_flow_reactor(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.JET_STREAM_REACTOR:
            self.jet_stream_reactor(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            self.outcomeSimulator.rapid_compression_machine(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.CONST_T_P:
            self.outcomeSimulator.const_t_p(experiment_set, experiments, mechanism)
        elif experiment_set == Reaction.FREE_FLAME:
            self.free_flame(experiment_set, experiments, mechanism)
        else:
            raise ValueError(f'Unknown reaction: {mechanism}')
        self.calculate_coefficients(experiment_set.get_target_species(), reference_results, experiments)

    def jet_stream_reactor(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        reference_results = experiment_set.all_simulated_experiments[0]
        self.outcomeSimulator.jet_stream_reactor(experiment_set, experiments, mechanism)
        self.calculate_coefficients(experiment_set.get_target_species(), reference_results, experiments)

    def free_flame(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        reference_results = experiment_set.all_simulated_experiments[0]
        self.outcomeSimulator.free_flame(experiment_set, experiments, mechanism)
        self.calculate_coefficients(experiment_set.get_target_species(), reference_results, experiments)

    def calculate_coefficients(self, targets: List[Species], reference_results: List[Experiment], experiments: List[Experiment]):
        for experiment_ndx in range(len(experiments)):
            for target in targets:
                reaction_data = experiments[experiment_ndx].results.get_target(target.name)
                reference_data = reference_results[experiment_ndx].results.get_target(target.name)
                sensitivity_coefficients = (reaction_data - reference_data) / (reference_data * SensitivitySimulator.FACTOR)
                experiments[experiment_ndx].results.set_target(target.name, sensitivity_coefficients)
