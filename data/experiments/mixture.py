from typing import List, Tuple, Optional, Dict

from pint import Quantity

from data.mechanism.species import Species


class Mixture:
    def __init__(self):
        self.species: List[Tuple[Species, Quantity]] = []
        self.balanced: Optional[Species] = None

    def add_species(self, species: Species, quantity: Quantity):
        self.species.append((species, quantity))

    def add_balanced_species(self, species: Species):
        if self.balanced is None:
            self.balanced = species
        else:
            raise Exception('Balanced species already set')

    def copy(self):
        species = [(spc.copy(), quantity) for spc, quantity in self.species]
        balanced = self.balanced.copy() if self.balanced is not None else None

        mixture: Mixture = Mixture()
        mixture.species = species
        mixture.balanced = balanced

        return mixture