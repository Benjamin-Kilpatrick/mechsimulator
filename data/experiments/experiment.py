from data.experiments.common.variable_set import VariableSet
from data.experiments.measurement import Measurement
from data.experiments.reaction import Reaction


class Experiment:
    def __init__(self,
                 reaction: Reaction,
                 measurement: Measurement,
                 variables: VariableSet):
        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement
        self.variables: VariableSet = variables

