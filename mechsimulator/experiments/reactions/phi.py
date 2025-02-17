from typing import Optional


class Phi:
    def __init__(self,
                 fuel: str,
                 oxidizer: str,
                 fuel_ratio: Optional[float] = None,
                 oxidizer_ratio: Optional[float] = None):
        self.fuel: str = fuel
        self.oxidizer: str = oxidizer
        self.fuel_ratio: Optional[float] = fuel_ratio
        self.oxidizer_ratio: Optional[float] = oxidizer_ratio
