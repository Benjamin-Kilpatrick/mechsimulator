
class Value:
    def __init__(self,
                 value: float,
                 upper_bound: float,
                 lower_bound: float):
        self.value: float = value
        self.upper_bound: float = upper_bound
        self.lower_bound: float = lower_bound
