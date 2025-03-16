import numpy


class Result:
    """
    The result of an experiment.
    TODO! more detail
    """
    def __init__(self,
                 name: str,
                 values: numpy.ndarray,
                 upper_bounds: numpy.ndarray,
                 lower_bounds: numpy.ndarray):
        self.name: str = name
        self.values: numpy.ndarray = values
        self.upper_bounds: numpy.ndarray = upper_bounds
        self.lower_bounds: numpy.ndarray = lower_bounds

    def __repr__(self):
        return f'<Result name:{self.name}>'
