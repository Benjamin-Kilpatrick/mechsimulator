from typing import List

from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism
from sim.ReactionSimulator import ReactionSimulator


class SensitivitySimulator(ReactionSimulator):
    @staticmethod
    def simulate_experiment_set(experiment: ExperimentSet, mechanisms: List[Mechanism]):
        raise NotImplementedError

    @staticmethod
    def rcm(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def const_t_p(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def free_flame(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def jsr(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def st(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError

    @staticmethod
    def pfr(experiment_set: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError
