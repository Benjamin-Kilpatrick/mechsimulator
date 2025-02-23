from data.common.value import Value
from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement



class Emission(Measurement):
    def __init__(self,
                 value: Value,
                 timestep: float,
                 end_time: float,
                 wavelength: float,
                 active_species: str):
        Measurement.__init__(self, value)

        self.timestep: float = timestep
        self.end_time: float = end_time
        self.wavelength: float = wavelength
        self.active_species: str = active_species
