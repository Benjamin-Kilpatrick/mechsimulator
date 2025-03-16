from typing import List

from data.experiments.results import Result
from data.mixtures.compound import Compound


class Datapoint:
    def __init__(self,
                 results: List[Result]):
        self.results: List[Result] = results

