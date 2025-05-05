class Value:
    """
    Store a value with an upper and lower bound.
    """
    def __init__(self,
                 value: float,
                 upper_bound: float,
                 lower_bound: float):
        self.value: float = value
        self.upper_bound: float = upper_bound
        self.lower_bound: float = lower_bound

    def __repr__(self):
        return f"<Value: {self.value}, bound:({self.lower_bound}, {self.upper_bound})>"