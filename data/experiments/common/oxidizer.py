import pint

from data.mechanism.species import Species


class Oxidizer:
    def __init__(self, species: Species, ratio: pint.Quantity):
        self.species: Species = species
        self.ratio: pint.Quantity = ratio
