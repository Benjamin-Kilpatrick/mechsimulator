from typing import List, Set

import numpy
from pint import Quantity

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.data_source import DataSource
from data.experiments.common.condition import Condition
from data.experiments.common.condition_range import ConditionRange
from data.experiments.common.condition_set import ConditionSet
from data.experiments.experiment import Experiment
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.reaction import Reaction
from data.experiments.results import Results
from data.mechanism.species import Species
from data.mixtures.compound import Compound


class ExperimentSet:
    """
    A set of measured experiments and data for simulating an equivalent experiment
    """

    def __init__(self,
                 metadata: MetaData,
                 calculation_type: CalculationType,
                 x_source: DataSource,
                 condition_source: DataSource,
                 condition_range: ConditionRange,
                 reaction: Reaction,
                 measurement: Measurement,
                 simulated_species: List[Species],
                 simulated_compounds: List[Compound],
                 measured_experiments: List[Experiment]):
        """
        Constructor
        :param metadata: The meta data about the experiment
        :param calculation_type: The type of simulation calculation to perform
        :param x_source: Where the x data is sourced, MEASURED for the measured experiments, SIMULATED for the simulation variable of interest
        :param condition_source: Where the condition data is sourced, MEASURED for the measured experiments, SIMULATED for the simulation conditions
        :param condition_range: A generator for the conditions for each value of the variable of interest
        :param reaction: The type of reaction to simulate
        :param measurement: The type of measurement to perform
        :param simulated_species: The chemical species to describe
        :param simulated_compounds: The chemical mixtures of the starting solution
        :param measured_experiments: All of the real data of real experiments run
        """
        self.metadata: MetaData = metadata
        self.calculation_type: CalculationType = calculation_type
        self.x_source: DataSource = x_source
        self.condition_source: DataSource = condition_source

        self.condition_range: ConditionRange = condition_range

        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement

        self.simulated_species: List[Species] = simulated_species
        self.simulated_compounds: List[Compound] = simulated_compounds
        self.simulated_experiments: List[Experiment] = []

        # TODO implement this operation
        self.measured_experiments: List[Experiment] = measured_experiments

    def __repr__(self) -> str:
        return f"<ExperimentSet calculation_type:{self.calculation_type.name} reaction:{self.reaction.name}>"

    def generate_simulated_conditions(self) -> List[Experiment]:
        """
        Generate from start to end with inc interval of the variable of interest a copy of the
        conditions
        :return: A list of all of the possible simulated conditions as experiment objects
        """
        simulated: List[Experiment] = []
        conditions: List[ConditionSet] = self.condition_range.generate()
        condition: ConditionSet
        for condition in conditions:
            simulated.append(
                Experiment(
                    condition,
                    self.simulated_compounds,
                    Results()
                )
            )

        return simulated

    def generate_measured_conditions(self) -> List[Experiment]:
        """
        Get the conditions of measured experiments
        :return: measured experiments
        """
        return self.measured_experiments

    def get_conditions(self) -> List[Experiment]:
        """
        Get the experiment conditions based on the condition source
        :return: Simulated variable conditions if condition source is simulation, measured experiment conditions otherwise
        """
        if self.condition_source == DataSource.SIMULATION:
            return self.generate_simulated_conditions()
        else:
            return self.generate_measured_conditions()

    def get_condition_x_data(self) -> numpy.ndarray:
        """
        Get the variable of interest data based on the x source
        :return: Simulated variable of interest if x source is simulation, measured variable of interest otherwise
        """
        if self.x_source == DataSource.SIMULATION:
            num = (self.condition_range.end - self.condition_range.start) // self.condition_range.inc
            return numpy.linspace(self.condition_range.start, self.condition_range.end, num, endpoint=True)
        if self.x_source == DataSource.MEASURED:
            condition_variable_range: List[Quantity] = []
            experiment: Experiment
            for experiment in self.measured_experiments:
                condition_variable_range.append(experiment.conditions.get(self.condition_range.variable_of_interest))
            return numpy.asarray(condition_variable_range)

    def get_time_x_data(self) -> numpy.ndarray:
        """
        Get the time data based on the x source
        :return: Simulated time if x source is simulation, measured time otherwise
        """
        if self.x_source == DataSource.SIMULATION:
            end_time: Quantity = self.condition_range.get(Condition.END_TIME)
            num = end_time // self.condition_range.get(Condition.TIME_STEP)
            return numpy.linspace(0, end_time, num, endpoint=True)
        if self.x_source == DataSource.MEASURED:
            times: Set[Quantity] = set()
            experiment: Experiment
            for experiment in self.measured_experiments:
                times.update(experiment.results.get_variable(Condition.TIME)[0])

            return numpy.asarray(sorted(list(times)))

    def get_target_species(self) -> List[Species]:
        return self.simulated_species
