from typing import List

from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism
from sim.ReactionSimulator import ReactionSimulator


class OutcomeSimulator(ReactionSimulator):
    def shock_tube(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_st(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def plug_flow_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_pfr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def jet_stream_reactor(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_jsr(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def rapid_compression_machine(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_rcm(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_const_t_p(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def process_free_flame(self, experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    def get_basic_conditions(self, experiment_set: ExperimentSet):
