from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement


class Abs(Measurement):
    def __init__(self,
                 variable: Variable,
                 timestep: float,
                 end_time: float,
                 wavelength: float,
                 active_species: str,
                 abs_coefficient: float = 0.0,
                 path_length: float = 0.0):
        Measurement.__init__(self, variable)

        self.timestep: float = timestep
        self.end_time: float = end_time
        self.wavelength: float = wavelength
        self.active_species: str = active_species
        self.abs_coefficient: float = abs_coefficient
        self.path_length: float = path_length
