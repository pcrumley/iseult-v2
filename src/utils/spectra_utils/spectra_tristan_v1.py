from spectra_abc import SpectraABC
import numpy as np


class TristanV1Spect(SpectraABC):
    def __init__(self, sim):
        self.__name = 'tristan-v1-spec'
        self.__sim = sim

    @property
    def name(self):
        return self.__name

    @property
    def sim(self):
        return self.__sim

    def get_line_lvl_params(self):
        # returns a list of all boolean options to pass to the spectrum
        # function will be passed a kwarg to calc_spectra. Must includ
        # e.g. ['normalize', 'rest spec', ...]..
        return [
            {
                'param': 'x_left',
                'type': 'float_entry',
                'default_val': -10000.,
                'parser': lambda x: float(x)
            },
            {
                'param': 'x_right',
                'type': 'float_entry',
                'default_val': -0.,
                'parser': lambda x: float(x)
            },
            {
                'param': 'prtl_type',
                'type': 'option_box',
                'default_val': 'lec',
                'opts': ['ion', 'lec']
            }
        ]

    def get_plot_lvl_params(self):
        return [
            {
                'param': 'spect_type',
                'level': 'option_box',
                'default_val': 'energy',
                'opts': ['energy', 'momentum'],
            },
            {
                'param': 'rest_frame',
                'type': 'bool',
                'default_val': False
            },
            {
                'param': 'normed',
                'type': 'bool',
                'default_val': False
            },
            {
                'param': 'rel_to_shock',
                'type': 'bool',
                'default_val': False
            }
        ]

    def calc_spectra(
            self, n=None, spect_type='energy',
            rest_frame=False, normed=False, rel_to_shock=False,
            x_left=-100000., x_right=50.0, prtl_type='lec'):

        if n is None:
            n = self.sim.get_time()

        response_dict = {
            'ndarrays': (np.array([]),np.array([]))
        }
        if n < len(self.sim.file_list):
            f_suffix = self.sim.file_list[n]
        else:
            return response_dict
        hash_key = '{0}{1}{2}{3}{4}{5}{6}{7}'.format(
            spect_type, rest_frame, normed, rel_to_shock,
            x_left, x_right, prtl_type, f_suffix)
        if hash_key not in self.sim._data_dictionary:
            self.sim.parser.string = "c_omp"
            self.sim.parser.f_suffix = f_suffix
            c_omp = self.sim.parser.getValue()

            self.sim.parser.string = "istep"
            self.sim.parser.f_suffix = f_suffix
            istep = self.sim.parser.getValue()

            self.sim.parser.string = "xsl"
            self.sim.parser.f_suffix = f_suffix
            xsl = self.sim.parser.getValue()/c_omp

            self.sim.parser.string = "gamma"
            self.sim.parser.f_suffix = f_suffix
            gamma = self.sim.parser.getValue()

            # massRatio = o.mi/o.me
            momentum = np.sqrt((gamma+1)**2-1.)
            spect_key = 'spec'
            if prtl_type == 'lec':
                spect_key += 'e'
            else:
                spect_key += 'p'
            if rest_frame:
                spect_key += 'rest'

            self.sim.parser.string = spect_key
            self.sim.parser.f_suffix = f_suffix
            spec = np.copy(self.sim.parser.getValue())

            for i in range(len(xsl)):
                spec[:, i] *= gamma

            ###############################
            # energy spectra, f=(dN/dE)/N
            ###############################

            dgamma = np.empty(len(gamma))
            delta = np.log10(gamma[-1]/gamma[0])/len(gamma)
            for i in range(len(dgamma)):
                dgamma[i] = gamma[i]*(10**delta-1.)

            indLeft = xsl.searchsorted(x_left)
            indRight = xsl.searchsorted(x_right, side='right')

            if indLeft >= indRight:
                indLeft = indRight
                indRight += 1

            # energy distribution, f(E)=(dn/dE)/N
            fE = np.empty(len(gamma))
            norm = np.ones(len(xsl))

            # total particles in each linear x bin
            for i in range(len(norm)):
                norm[i] = sum(spec[:, i])

            for k in range(len(fE)):
                fE[k] = sum(spec[k][indLeft:indRight])

            if sum(norm[indLeft:indRight]) > 0:
                if normed:
                    fE *= 1.0/sum(norm[indLeft:indRight])

                eDist = np.copy(fE)
                fE *= dgamma**(-1)
                fmom = fE/(4*np.pi*momentum)/(gamma+1)
                momDist = fmom*momentum**4

            if spect_type == 'energy':
                self.sim._data_dictionary[hash_key] = (gamma, eDist)
            else:  # spect_type == 'momentum':
                self.sim._data_dictionary[hash_key] = (momentum, momDist)

        response_dict['ndarrays'] = self.sim._data_dictionary[hash_key]
        if spect_type == 'energy':
            response_dict['x_label'] = r'$\gamma - 1$'
            response_dict['y_label'] = r'$E(dn/dE)$'
        else:  # spect_type == 'momentum':
            response_dict['x_label'] = r'$\gamma \beta$'
            response_dict['y_label'] = r'$p^4 f(p)$'

        return response_dict
