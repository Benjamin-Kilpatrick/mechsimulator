import numpy


class TemperatureProfile:
    def __init__(self,
                 temperature: float,
                 profile: numpy.ndarray):
        self.temperature: float = temperature
        self.profile: numpy.ndarray = profile
