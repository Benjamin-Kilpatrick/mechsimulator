from data.common.value import Value
from data.mechanism.species import Species


class Compound:
    def __init__(self,
                 species: Species,
                 concentration: Value,
                 is_balanced: bool):
        self.species = species
        self.concentration: Value = concentration
        self.is_balanced: bool = is_balanced

