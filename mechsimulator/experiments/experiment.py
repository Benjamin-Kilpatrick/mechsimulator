from experiments.measurements.measurement import Measurement
from experiments.reactions.reaction import Reaction


class Experiment:
    def __init__(self,
                 reaction: Reaction,
                 measurement: Measurement):
        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement
