class Value:
    def __init__(self,
                 name: str,
                 value: float,
                 upper_bound: float,
                 lower_bound: float):
        self.name = name
        self.value: float = value
        self.upper_bound: float = upper_bound
        self.lower_bound: float = lower_bound
