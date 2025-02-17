from typing import List

from experiments.experiment import Experiment
from experiments.metadata import MetaData


class ExperimentSet:
    def __init__(self,
                 metadata: MetaData):
        self.metadata: MetaData = metadata
        self.simulated_experiments: List[Experiment] = []

        # TODO implement this operation
        self.measured_experiments: List[Experiment] = []

