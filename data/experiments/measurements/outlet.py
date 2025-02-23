from data.common.value import Value
from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement



class Outlet(Measurement):
    def __init__(self,
                 value: Value):
        Measurement.__init__(self, value)
