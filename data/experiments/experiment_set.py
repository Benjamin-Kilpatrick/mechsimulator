from typing import List, Set, Optional, Dict

import numpy
import pint
from numpy import ndarray
from pint import Quantity
from pint.facets.plain import PlainQuantity

from data.experiments.common.calculation_type import CalculationType
from data.experiments.common.condition import Condition
from data.experiments.common.condition_range import ConditionRange
from data.experiments.common.condition_set import ConditionSet
from data.experiments.common.data_source import DataSource
from data.experiments.experiment import Experiment
from data.experiments.measurement import Measurement
from data.experiments.metadata import MetaData
from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from data.experiments.reaction import Reaction
from data.experiments.results import Results
from data.experiments.target_species import TargetSpecies
from data.mechanism.species import Species


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
                 simulated_mixture: Dict[MixtureType, Mixture],
                 measured_experiments: List[Experiment],
                 targets: TargetSpecies):
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
        :param simulated_mixture: The chemical mixtures of the starting solution
        :param measured_experiments: All of the real data of real experiments run
        :param targets: All species targets and special subset targets
        """
        self.metadata: MetaData = metadata
        self.calculation_type: CalculationType = calculation_type
        self.x_source: DataSource = x_source
        self.condition_source: DataSource = condition_source

        self.condition_range: ConditionRange = condition_range

        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement

        self.simulated_species: List[Species] = simulated_species
        self.simulated_mixture: Dict[MixtureType, Mixture] = simulated_mixture
        self.all_simulated_experiments: List[List[Experiment]] = []

        self.measured_experiments: List[Experiment] = measured_experiments
        self.targets: TargetSpecies = targets

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
                    self.simulated_mixture,
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

    def generate_conditions(self) -> List[Experiment]:
        """
        generate the experiment conditions based on the condition source
        """
        if self.condition_source == DataSource.SIMULATION:
            return self.generate_simulated_conditions()
        else:
            return self.generate_measured_conditions()

    def add_simulated_experiments(self, simulated_experiments: List[Experiment]):
        self.all_simulated_experiments.append(simulated_experiments)

    def get_condition_x_data(self, x_source: DataSource = None) -> PlainQuantity[ndarray]:
        """
        Get the variable of interest data based on the x source
        :return: Simulated variable of interest if x source is simulation, measured variable of interest otherwise
        """
        source: DataSource = x_source if x_source is not None else self.x_source
        if source == DataSource.SIMULATION:
            num = int((
                                  self.condition_range.end.magnitude - self.condition_range.start.magnitude) // self.condition_range.inc.magnitude)
            return numpy.linspace(self.condition_range.start, self.condition_range.end, num, endpoint=True)
        if source == DataSource.MEASURED:
            condition_variable_range: List[Quantity] = []
            experiment: Experiment
            for experiment in self.measured_experiments:
                condition_variable_range.append(experiment.conditions.get(self.condition_range.variable_of_interest))
            return pint.Quantity.from_list(condition_variable_range)

    def get_time_x_data(self, x_source: DataSource = None) -> numpy.ndarray:
        """
        Get the time data based on the x source
        :return: Simulated time if x source is simulation, measured time otherwise
        """
        source: DataSource = x_source if x_source is not None else self.x_source
        if source == DataSource.SIMULATION:
            end_time: Quantity = self.condition_range.get(Condition.END_TIME)
            num = end_time.magnitude // self.condition_range.get(Condition.TIME_STEP).magnitude
            return numpy.linspace(0, end_time, num, endpoint=True)
        if source == DataSource.MEASURED:
            times: Set[Quantity] = set()
            experiment: Experiment
            for experiment in self.measured_experiments:
                times.update(experiment.results.get_variable(Condition.TIME)[0])

            return numpy.asarray(sorted(list(times)))

    def get_x_data(self, x_source: DataSource = None) -> pint.Quantity:
        source: DataSource = x_source if x_source is not None else self.x_source
        if self.has(Condition.END_TIME):
            return self.get_time_x_data(source)
        return self.get_x_data(source)

    def get_target_species(self) -> List[Species]:
        return self.simulated_species

    def set_simulated_experiments(self, experiments: List[Experiment]):
        self.all_simulated_experiments = experiments

    def has(self, condition: Condition) -> bool:
        return self.condition_range.has(condition)
