from typing import List

import cantera

from data.mechanism.mechanism import Mechanism
from data.mechanism.species import Species


class MechanismReader:
    @staticmethod
    def read_species_file(species_file: str) -> List[Species]:
        raise NotImplementedError

    @staticmethod
    def read_mechanism_file(mechanism_file: str) -> cantera.Solution:
        solution: cantera.Solution = cantera.Solution(mechanism_file)
        return solution


    @staticmethod
    def read_file(
            mechanism_file: str,
            species_file: str
    ) -> Mechanism:
        solution: cantera.Solution = MechanismReader.read_mechanism_file(mechanism_file)
        species: List[Species] = MechanismReader.read_species_file(species_file)
        return Mechanism(solution, species)

