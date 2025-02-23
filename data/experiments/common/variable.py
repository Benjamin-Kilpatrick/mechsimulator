class Variable:
    def __init__(self, name: str, start: float, end: float, increment: float):
        self.name = name
        self.start = start
        self.end = end
        self.increment = increment

        self._curr: float = self.start

    def __iter__(self):
        self._curr = self.start
        return self

    def __next__(self) -> float:
        if self._curr <= self.end:
            out = self._curr
            self._curr += self.increment
            return out
        raise StopIteration
