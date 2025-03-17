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

    def __repr__(self) -> str:
        return f"<Species name:{self.name} smiles:{self.smiles} InChI:{self.InChI} spin:{self.spin} charge:{self.charge} excited:{self.excited}>"
