class Species:
    def __init__(self, name: str, smiles: str, spin: int, charge: int, excited: bool):
        self.name: str = name
        self.smiles: str = smiles
        self.spin: int = spin
        self.charge: int = charge
        self.excited: bool = excited