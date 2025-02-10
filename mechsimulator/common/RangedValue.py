from common.UnitValue import UnitValue


class RangedValue:
    def __init__(self,
                 start: UnitValue,
                 end: UnitValue,
                 step: UnitValue
                 ):
        self.start: UnitValue = start
        self.end: UnitValue = end
        self.step: UnitValue = step

        self.curr: UnitValue = self.start

    def __iter__(self):
        self.curr = self.start

    def __next__(self):
        if self.curr <= self.end:
            x: UnitValue = self.curr
            self.curr += self.step
            return x
        raise StopIteration
