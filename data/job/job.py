from typing import List

from experiments.experiment_set import ExperimentSet
from mechanism.mechanism import Mechanism


class Job:
    def __init__(self,
                 experiment_files: List[ExperimentSet],
                 mechanisms: List[Mechanism]):
        self.experiment_files: List[ExperimentSet] = experiment_files
        self.mechanisms: List[Mechanism] = mechanisms

