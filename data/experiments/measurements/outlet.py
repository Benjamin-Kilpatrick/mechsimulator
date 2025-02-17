from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement



class Outlet(Measurement):
    def __init__(self,
                 variable: Variable,):
        Measurement.__init__(self, variable)
