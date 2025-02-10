from common.UnitValue import UnitValue


class Mixture:
    def __init__(self, name: str, quantity: UnitValue, bounds: UnitValue):
        self.name = name
        self.quantity = quantity
        self.bounds = bounds