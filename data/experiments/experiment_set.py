from typing import List, Set

import numpy
from pint import Quantity
from typing_extensions import Any

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.variable import Variable
from data.experiments.common.variable_range import VariableRange
from data.experiments.common.variable_set import VariableSet
from data.experiments.experiment import Experiment
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.reaction import Reaction
from data.experiments.results import Results
from data.mechanism.species import Species
from data.mixtures.compound import Compound


class ExperimentSet:
    def __init__(self,
                 metadata: MetaData,
                 calculation_type: CalculationType,
                 x_source: DataSource,
                 condition_source: DataSource,
                 variable_range: VariableRange,
                 reaction: Reaction,
                 measurement: Measurement,
                 simulated_species: List[Species],
                 simulated_compounds: List[Compound],
                 measured_experiments: List[Experiment]):
        self.metadata: MetaData = metadata
        self.calculation_type: CalculationType = calculation_type
        self.x_source: DataSource = x_source
        self.condition_source: DataSource = condition_source

        self.variable_range: VariableRange = variable_range

        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement

        self.simulated_species: List[Species] = simulated_species
        self.simulated_compounds: List[Compound] = simulated_compounds
        self.simulated_experiments: List[Experiment] = []

        # TODO implement this operation
        self.measured_experiments: List[Experiment] = measured_experiments

    def generate_simulated_variable_conditions(self) -> List[Experiment]:
        simulated: List[Experiment] = []
        conditions: List[VariableSet] = self.variable_range.generate()
        condition: VariableSet
        for condition in conditions:
            simulated.append(
                Experiment(
                    condition,
                    self.simulated_compounds,
                    Results()
                )
            )

        return simulated

    def generate_measured_variable_conditions(self) -> List[Experiment]:
        return self.measured_experiments

    def get(self, variable: Variable) -> Any:
        return self.variable_range.get(variable)

    def get_variable_x_data(self) -> numpy.ndarray:
        if self.x_source == DataSource.SIMULATION:
            num = (self.variable_range.end - self.variable_range.start) // self.variable_range.inc
            return numpy.linspace(self.variable_range.start, self.variable_range.end, num, endpoint=True)
        if self.x_source == DataSource.MEASURED:
            condition_variable_range: List[Quantity] = []
            experiment: Experiment
            for experiment in self.measured_experiments:
                condition_variable_range.append(experiment.variables.get(self.variable_range.variable))
            return numpy.asarray(condition_variable_range)

    def get_time_x_data(self) -> numpy.ndarray:
        if self.x_source == DataSource.SIMULATION:
            end_time: Quantity = self.variable_range.get(Variable.END_TIME)
            num = end_time // self.variable_range.get(Variable.TIME_STEP)
            return numpy.linspace(0, end_time, num, endpoint=True)
        if self.x_source == DataSource.MEASURED:
            times: Set[Quantity] = set()
            experiment: Experiment
            for experiment in self.measured_experiments:
                times.update(experiment.results.get_variable(Variable.TIME)[0])

            return numpy.asarray(sorted(list(times)))
