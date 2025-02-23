from data.common.value import Value
from data.experiments.common.variable import Variable
from data.experiments.measurements.measurement import Measurement



class Lfs(Measurement):
    def __init__(self,
                 value: Value):
        Measurement.__init__(self, value)
