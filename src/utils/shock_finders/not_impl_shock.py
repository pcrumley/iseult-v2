from shock_abc import ShockFinderABC


class ShockFindingNotImpl(ShockFinderABC):
    def __init__(self, sim):
        self.__sim = sim

    @property
    def sim(self):
        return self.__sim

    def calc_shock_loc(self, n=None):
        return {
            'shock_loc': 0,
            'axes': 'x'}
