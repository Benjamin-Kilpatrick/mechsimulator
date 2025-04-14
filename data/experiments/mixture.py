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