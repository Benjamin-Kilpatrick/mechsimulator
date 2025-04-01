from data.common.value import Value
from data.mechanism.species import Species


class Concentration:
    """
    Compound is the concentration information for a species
    """
    def __init__(self,
                 species: Species,
                 concentration: Value,
                 is_balanced: bool):
        self.species = species
        self.concentration: Value = concentration
        self.is_balanced: bool = is_balanced

    def __repr__(self):
        return f"<Compound species:{self.species} concentration:{self.concentration} balanced:{self.is_balanced}>"

