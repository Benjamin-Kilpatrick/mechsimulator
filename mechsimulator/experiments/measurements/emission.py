from experiments.common.variable import Variable
from experiments.measurements.measurement import Measurement



class Emission(Measurement):
    def __init__(self,
                 variable: Variable,
                 timestep: float,
                 end_time: float,
                 wavelength: float,
                 active_species: str):
        Measurement.__init__(self, variable)

        self.timestep: float = timestep
        self.end_time: float = end_time
        self.wavelength: float = wavelength
        self.active_species: str = active_species
