from experiments.common.variable import Variable
from experiments.measurements.measurement import Measurement



class Lfs(Measurement):
    def __init__(self,
                 variable: Variable):
        Measurement.__init__(self, variable)
