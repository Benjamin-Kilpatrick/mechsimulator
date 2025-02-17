from data.experiments.measurements.measurement import Measurement
from data.experiments.reactions.reaction import Reaction


class Experiment:
    def __init__(self,
                 reaction: Reaction,
                 measurement: Measurement):
        self.reaction: Reaction = reaction
        self.measurement: Measurement = measurement
