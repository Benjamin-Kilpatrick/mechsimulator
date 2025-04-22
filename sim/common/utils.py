from typing import Dict, List, Tuple

from data.experiments.common.target import Target
from data.experiments.experiment_set import ExperimentSet
from data.experiments.measurement import Measurement
from data.experiments.mixture import Mixture
from data.experiments.mixture_type import MixtureType
from data.experiments.reaction import Reaction
from data.experiments.target_species import TargetSpecies
from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species


class Utils:
    REACTION_COMPATIBLE_MEASUREMENTS: Dict[Reaction, List[Measurement]] = {
        Reaction.SHOCKTUBE: [
            Measurement.ABSORPTION, Measurement.EMISSION,
            Measurement.IGNITION_DELAY_TIME, Measurement.OUTLET,
            Measurement.ION, Measurement.PRESSURE,
            Measurement.CONCENTRATION, Measurement.HALF_LIFE
        ],
        Reaction.PLUG_FLOW_REACTOR: [Measurement.OUTLET],
        Reaction.JET_STREAM_REACTOR: [Measurement.OUTLET],
        Reaction.RAPID_COMPRESSION_MACHINE: [
            Measurement.IGNITION_DELAY_TIME, Measurement.PRESSURE
        ],
        Reaction.CONST_T_P: [
            Measurement.ABSORPTION, Measurement.EMISSION,
            Measurement.IGNITION_DELAY_TIME, Measurement.OUTLET,
            Measurement.ION, Measurement.PRESSURE,
            Measurement.CONCENTRATION
        ],
        Reaction.FREE_FLAME: [Measurement.LAMINAR_FLAME_SPEED]
    }
    @staticmethod
    def get_compatible_measurements(reaction: Reaction) -> List[Measurement]:
        if reaction not in Utils.REACTION_COMPATIBLE_MEASUREMENTS:
            raise NotImplementedError(f'Reaction {reaction.name} not implemented yet')
        return Utils.REACTION_COMPATIBLE_MEASUREMENTS[reaction]


    @staticmethod
    def set_gas_state():
        pass