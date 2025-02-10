from typing import List

from experiments.Experiment import Experiment
from experiments.ExperimentConfig import ExperimentConfig
from experiments.ExperimentMetaData import MetaData


class ExperimentSet:
    def __init__(self,
                 meta_data: MetaData,
                 experiment_config: ExperimentConfig,
                 experiments: List[Experiment]
                 ):
        self.meta_data = meta_data
        self.experiment_config = experiment_config
        self.experiments = experiments

        self.simulated_experiments: List[Experiment] = []
