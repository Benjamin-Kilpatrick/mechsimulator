import warnings
from typing import List

import cantera

from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species
from serial.common.env_path import EnvPath
from serial.common.utils import Utils


class MechanismReader:
    @staticmethod
    def read_species_file(species_file: str) -> List[Species]:
        warnings.warn('species parsing not implemented yet')
        return []

    @staticmethod
    def read_mechanism_file(mechanism_file: str) -> cantera.Solution:
        solution: cantera.Solution = cantera.Solution(
            Utils.get_full_path(EnvPath.MECHANISM, mechanism_file)
        )
        return solution


    @staticmethod
    def read_file(
            mechanism_file: str,
            species_file: str,
            mechanism_name: str
    ) -> Mechanism:
        solution: cantera.Solution = MechanismReader.read_mechanism_file(mechanism_file)
        species: List[Species] = MechanismReader.read_species_file(species_file)
        return Mechanism(solution, species, mechanism_name)

