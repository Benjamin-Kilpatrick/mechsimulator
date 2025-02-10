from typing import List

from common.MeasurementType import MeasurementType
from common.RangedValue import RangedValue
from common.ReactionType import ReactionType
from common.UnitValue import UnitValue
from experiments.Mixture import Mixture
from experiments.Species import Species


class ExperimentConfig:
    def __init__(self,
                 reaction_type: ReactionType,
                 measurement_types: List[MeasurementType],
                 initial_mixtures: List[Mixture],
                 expected_species: List[Species],
                 end_time: UnitValue,
                 temperature: RangedValue,
                 pressure: RangedValue
                 ):
        self.reaction_type: ReactionType = reaction_type
        self.measurement_types: List[MeasurementType] = measurement_types
        self.initial_mixtures: List[Mixture] = initial_mixtures
        self.expected_species: List[Species] = expected_species
        self.end_time: UnitValue = end_time
        self.temperature: RangedValue = temperature
        self.pressure: RangedValue = pressure
