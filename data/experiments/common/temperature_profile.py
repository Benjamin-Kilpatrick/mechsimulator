import numpy


class TemperatureProfile:
    """
    The temperature profile class is responsible for storing temperature profiles
    TODO! What is this?
    """
    def __init__(self,
                 temperature: float,
                 profile: numpy.ndarray):
        self.temperature: float = temperature
        self.profile: numpy.ndarray = profile

    def __repr__(self):
        return f"<TemperatureProfile temperature:{self.temperature} profile:{self.profile}>"
