from typing import List

from data.experiments.experiment_set import ExperimentSet
from data.experiments.reaction import Reaction
from data.mechanism.mechanism import Mechanism


class ReactionSimulator:
    def __init__(self):
        pass

    def simulate_experiment_set(self, experiment_set: ExperimentSet, mechanisms: List[Mechanism]):
        for mechanism in mechanisms:
            if experiment_set.reaction == Reaction.SHOCKTUBE:
                return self.shock_tube(experiment_set, mechanism)
            elif experiment_set.reaction == Reaction.PLUG_FLOW_REACTOR:
                return self.plug_flow_reactor(experiment_set, mechanism)
            elif experiment_set.reaction == Reaction.JET_STREAM_REACTOR:
                return self.jet_stream_reactor(experiment_set, mechanism)
            elif experiment_set.reaction == Reaction.RAPID_COMPRESSION_MACHINE:
                return self.rapid_compression_machine(experiment_set, mechanism)
            elif experiment_set.reaction == Reaction.CONST_T_P:
                return self.const_t_p(experiment_set, mechanism)
            elif experiment_set == Reaction.FREE_FLAME:
                return self.free_flame(experiment_set, mechanism)
            else:
                raise ValueError(f'Unknown reaction: {mechanism}')

    def shock_tube(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def plug_flow_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def jet_stream_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def rapid_compression_machine(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError
