from abc import ABC, abstractmethod


class ShockFinderABC(ABC):

    @abstractmethod
    def sim(self):
        return 0
    # we need to specify all the inputs required to put in the GUI in a

    @abstractmethod
    def calc_shock_loc(self, n):
        # This takes in bool_opts, other things to returns
        # the spectrum at time n
        return 0
