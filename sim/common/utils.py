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
        Reaction.FREE_FLAME: [Measurement.LFS]
    }
    @staticmethod
    def get_compatible_measurements(reaction: Reaction) -> List[Measurement]:
        if reaction not in Utils.REACTION_COMPATIBLE_MEASUREMENTS:
            raise NotImplementedError(f'Reaction {reaction.name} not implemented yet')
        return Utils.REACTION_COMPATIBLE_MEASUREMENTS[reaction]

    @staticmethod
    def rename_list_species(species: List[Species], mech_dict: Dict[Species, Species]):
        for spc in species:
            if spc in mech_dict:
                spc.name = mech_dict[spc].name

    @staticmethod
    def rename_targets(targets: TargetSpecies, mech_dict: Dict[Species, Species]):
        Utils.rename_list_species(targets.all_targets, mech_dict)
        for target_type in targets.get_special_target_enumerations():
            Utils.rename_list_species(targets.get_special_targets(target_type), mech_dict)

    @staticmethod
    def rename_mixture(mixtures: Dict[MixtureType, Mixture], mech_dict: Dict[Species, Species]):
        for mixture_type, mixture in mixtures.items():
            mix_list = [spc for spc, _ in mixture.species]
            Utils.rename_list_species(mix_list, mech_dict)

            if mixture.balanced in mech_dict:
                mixture.balanced.name = mech_dict[mixture.balanced].name
    @staticmethod
    def rename_all_species(experiment_set: ExperimentSet, mechanism: Mechanism):
        mech_species: Dict[Species, Species] = {}
        for species in mechanism.species:
            mech_species[species] = species

        # rename simulated species
        Utils.rename_list_species(experiment_set.simulated_species, mech_species)
        Utils.rename_targets(experiment_set.targets, mech_species)
        Utils.rename_mixture(experiment_set.simulated_mixture, mech_species)

        # rename the mixtures in measured experiments
        for measured in experiment_set.measured_experiments:
            Utils.rename_mixture(measured.mixtures, mech_species)


    @staticmethod
    def convert_gas_mixture(mixture: Mixture) -> Dict[str, float]:
        out: Dict[str, float] = {}
        sum: float = 0.0
        for spc, quantity in mixture.species:
            # maybe works???
            out[spc.name] = quantity.to('%')
            sum += out[spc.name]

        if mixture.balanced is not None:
            out[mixture.balanced.name] = 1.0 - sum

        return out

    @staticmethod
    def convert_fuel_mixture(fuel: Mixture, oxidizers: Mixture) -> Tuple[str, str]:
        fuel_strs: List[str] = [f'{spc.name}: {ratio.magnitude}' for spc, ratio in fuel.species]
        oxid_strs: List[str] = [f'{spc.name}: {ratio.magnitude}' for spc, ratio in oxidizers.species]

        fuel_string: str = ', '.join(fuel_strs)
        oxid_string: str = ', '.join(oxid_strs)

        return fuel_string, oxid_string


    @staticmethod
    def set_gas_state():
        pass