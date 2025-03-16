from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism


class ReactionSimulator:
    @staticmethod
    def run_experiment(experiment: ExperimentSet, mechanism: Mechanism):
        raise NotImplementedError
