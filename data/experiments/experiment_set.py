from typing import List

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.experiment import Experiment
from data.experiments.metadata import MetaData


class ExperimentSet:
    def __init__(self,
                 metadata: MetaData,
                 calculation_type: CalculationType,
                 source_mode: DataSource,
                 simulated_experiments: List[Experiment],
                 measured_experiments: List[Experiment]):
        self.metadata: MetaData = metadata
        self.calculation_type: CalculationType = calculation_type
        self.source_mode: DataSource = source_mode

        self.simulated_experiments: List[Experiment] = simulated_experiments

        # TODO implement this operation
        self.measured_experiments: List[Experiment] = measured_experiments

