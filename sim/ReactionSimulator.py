from typing import List

from data.experiments.experiment import Experiment
from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism


class ReactionSimulator:
    def __init__(self):
        pass

    def simulate_experiments(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        if experiment_set.reaction == Reaction.SHOCKTUBE:
            self.shock_tube(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.PLUG_FLOW_REACTOR:
            self.plug_flow_reactor(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.JET_STREAM_REACTOR:
            self.jet_stream_reactor(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.RAPID_COMPRESSION_MACHINE:
            self.rapid_compression_machine(experiment_set, experiments, mechanism)
        elif experiment_set.reaction == Reaction.CONST_T_P:
            self.const_t_p(experiment_set, experiments, mechanism)
        elif experiment_set == Reaction.FREE_FLAME:
            self.free_flame(experiment_set, experiments, mechanism)
        else:
            raise ValueError(f'Unknown reaction: {mechanism}')

    def shock_tube(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError

    def plug_flow_reactor(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError

    def jet_stream_reactor(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError

    def rapid_compression_machine(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError

    def const_t_p(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError

    def free_flame(self, experiment_set: ExperimentSet, experiments: List[Experiment], mechanism: Mechanism):
        raise NotImplementedError
