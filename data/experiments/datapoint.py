from typing import List

from data.experiments.results import Result
from data.mixtures.compound import Compound


class Datapoint:
    """
    A Datapoint keeps a list of results
    TODO! More detail
    """
    def __init__(self,
                 results: List[Result]):
        self.results: List[Result] = results

    def __repr__(self) -> str:
        return f"<Datapoint results:{self.results}>"

