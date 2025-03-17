from typing import Optional


class Phi:
    """
    Phi
    TODO! What is this again?
    """
    def __init__(self,
                 fuel: str,
                 oxidizer: str,
                 fuel_ratio: Optional[float] = None,
                 oxidizer_ratio: Optional[float] = None):
        self.fuel: str = fuel
        self.oxidizer: str = oxidizer
        self.fuel_ratio: Optional[float] = fuel_ratio
        self.oxidizer_ratio: Optional[float] = oxidizer_ratio

    def __repr__(self) -> str:
        return f"<Phi fuel:{self.fuel} oxidizer:{self.oxidizer} fuel_ratio:{repr(self.fuel_ratio)} oxidizer_ratio:{repr(self.oxidizer_ratio)}>"