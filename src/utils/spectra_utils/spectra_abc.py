from abc import ABC, abstractmethod


class SpectraABC(ABC):

    @abstractmethod
    def name(self):
        return 0

    @abstractmethod
    def sim(self):
        return 0
    # we need to specify all the inputs required to put in the GUI in a
    # typed manner because TK is typed as well as the fact that the

    @abstractmethod
    def get_line_lvl_params(self):
        # returns a dictionary of all boolean options to pass to the spectrum
        # function will be passed a kwarg to calc_spectra. Must include default
        # e.g. {'normalize': True, 'rest_spec': false, ... }
        return 0

    @abstractmethod
    def get_plot_lvl_params(self):
        # return a dictionary of all float options to pass to spectrum
        # with default values
        # e.g. [{left: {default: -10000, validator: lambda x: float(x)},
        #        right: {default: 0, validator: FUNC}]
        #
        return 0


    @abstractmethod
    def calc_spectra(self):
        # This takes in bool_opts, other things to returns
        # the spectrum at time n
        return 0
