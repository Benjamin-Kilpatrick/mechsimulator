from typing import List

import cantera

from data.mechanism.species import Species


class Mechanism:
    def __init__(self,
                 solution: cantera.Solution,
                 species: List[Species],
                 mechanism_name: str):
        self.solution: cantera.Solution = solution
        self.species: List[Species] = species
        self.mechanism_name = mechanism_name
