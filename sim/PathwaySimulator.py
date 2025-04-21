from typing import List

from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism
from sim.ReactionSimulator import ReactionSimulator


class PathwaySimulator(ReactionSimulator):
    @staticmethod
    def simulate_experiments(experiment_set: ExperimentSet, mechanisms: List[Mechanism]):
        raise NotImplementedError

    @staticmethod
    def rapid_compression_machine(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_rcm(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def const_t_p(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_const_t_p(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def free_flame(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_free_flame(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def jet_stream_reactor(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_jsr(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def shock_tube(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_st(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def plug_flow_reactor(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def process_pfr(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError
