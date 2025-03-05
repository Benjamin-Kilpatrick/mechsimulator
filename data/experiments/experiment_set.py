from typing import List

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.variable_range import VariableRange
from data.experiments.experiment import Experiment
from data.experiments.metadata import MetaData
from data.mechanism.species import Species
from data.mixtures.compound import Compound


class ExperimentSet:
    def __init__(self,
                 metadata: MetaData,
                 calculation_type: CalculationType,
                 source_mode: DataSource,
                 variable_range: VariableRange,
                 simulated_species: List[Species],
                 simulated_compounds: List[Compound],
                 measured_experiments: List[Experiment]):
        self.metadata: MetaData = metadata
        self.calculation_type: CalculationType = calculation_type
        self.source_mode: DataSource = source_mode

        self.variable_range: VariableRange = variable_range

        self.simulated_species: List[Species] = simulated_species
        self.simulated_compounds: List[Compound] = simulated_compounds
        self.simulated_experiments: List[Experiment] = []

        # TODO implement this operation
        self.measured_experiments: List[Experiment] = measured_experiments

