from typing import List

from data.experiments.result import Result
from data.mixtures.compound import Compound


class Datapoint:
    def __init__(self,
                 mixture: List[Compound],
                 results: List[Result]):
        self.mixture: List[Compound] = mixture
        self.results: List[Result] = results

