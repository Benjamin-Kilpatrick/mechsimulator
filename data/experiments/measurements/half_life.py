from data.common.value import Value
from data.experiments.measurements.measurement import Measurement



class HalfLife(Measurement):
    def __init__(self,
                 value: Value,
                 end_time: float,
                 target_species: str):
        Measurement.__init__(self, value)
        self.end_time: float = end_time
        self.target_species: str = target_species
