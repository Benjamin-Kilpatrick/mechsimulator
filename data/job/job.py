from typing import List

from data.experiments.experiment_set import ExperimentSet
from data.mechanism.mechanism import Mechanism


class Job:
    """
    Job both the experiment files and the mechanisms to run a job
    """
    def __init__(self,
                 name: str,
                 experiment_files: List[ExperimentSet],
                 mechanisms: List[Mechanism]):
        """
        Initialize a job
        :param name: name of the original file object
        :param experiment_files: list of experiment sets
        :param mechanisms: list of mechanisms
        """
        self.name: str = name
        self.experiment_files: List[ExperimentSet] = experiment_files
        self.mechanisms: List[Mechanism] = mechanisms

    def get_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        """
        Create a string representation of the job
        """
        out = "Job\n\texperiment sets"
        for e in self.experiment_files:
            out += f"\n\t\t{str(e)}"
        out = out + "\n\tmechanisms"
        for m in self.mechanisms:
            out += f"\n\t\t{str(m)}"
        return out
