from typing import List, Tuple

from typing_extensions import Self


class Species:
    """
    Reaction species
    TODO! More detail
    """
    def __init__(self,
                 name: str,
                 smiles: str,
                 InChI: str,
                 spin: int,
                 charge: int,
                 excited: bool):
        self.name: str = name
        self.smiles: str = smiles
        self.InChI: str = InChI
        self.spin: int = spin
        self.charge: int = charge
        self.excited: bool = excited

    def __eq__(self, other: Self):
        return self.name == other.name and self.smiles == other.smiles and self.InChI == other.InChI

    def __repr__(self) -> str:
        return f"<Species name:{self.name} smiles:{self.smiles} InChI:{self.InChI} spin:{self.spin} charge:{self.charge} excited:{self.excited}>"

    def __hash__(self):
        params: Tuple = (self.InChI, self.spin, self.charge, self.excited)
        return hash(params)

    def copy(self):
        return Species(
            self.name,
            self.smiles,
            self.InChI,
            self.spin,
            self.charge,
            self.excited
        )
