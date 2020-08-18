from shock_abc import ShockFinderABC
import numpy as np


class ConstVelShockFinderV1(ShockFinderABC):
    def __init__(self, sim):
        self.__sim = sim

    @property
    def sim(self):
        return self.__sim

    def calc_shock_loc(self, n=None):
        if n is None:
            n = self.sim.get_time()
        time = self.sim.get_data(
            data_class='param', attribute='time')
        response_dict = {
            'shock_loc': self.calc_shock_speed() * time,
            'axis': 'x'}
        return response_dict

    def calc_shock_speed(self):
        hash_key = f'shock_speed'
        shock_tup = self.sim._data_dictionary.get(hash_key, (1, -np.inf))
        t = len(self.sim.file_list) - 1
        if t != shock_tup[1]:
            c_omp = self.sim.get_data(
                data_class='param', attribute='c_omp', n=t)
            istep = self.sim.get_data(
                data_class='param', attribute='istep', n=t)
            dens = self.sim.get_data(
                data_class='scalar_flds', fld='density', n=t)['data']

            # average along x-axis
            dens_1d = np.average(
                dens.reshape(-1, dens.shape[-1]), axis=0)

            dens_half_max = max(dens_1d)*.5

            # Find the farthest location where the average density is greater
            # than half max
            ishock = np.where(dens_1d >= dens_half_max)[0][-1]
            time = self.sim.get_data(
                data_class='param', attribute='time', n=t)
            shock_tup = (ishock * istep / c_omp / time, t)
            self.sim._data_dictionary[hash_key] = shock_tup

        shock_tup = self.sim._data_dictionary[hash_key]
        return shock_tup[0]


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(
        os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(
        os.path.join(os.path.dirname(__file__), '..', 'spectra_utils'))
    sys.path.append(
        os.path.join(os.path.dirname(__file__), '..', '..'))
    from pic_sim import picSim
    from matplotlib import pyplot as plt

    sim = picSim(
        dirpath=os.path.join(
            os.path.dirname(__file__),  # shock finders folder
            '..',  # utils folder
            '..',  # src folder
            '..',  # iseult-v2 folder
            'output'),
        cfg_file=os.path.join(
            os.path.dirname(__file__),  # shock finders folder
            '..',  # utils folder
            '..',  # src folder
            'code_output_configs',  # iseult-v2 folder
            'tristan_v1.yml'))
    sim.set_time(0)
    shock_finder = ConstVelShockFinderV1(sim)
    # GET THE DATA
    c_omp = sim.get_data(data_class='param', attribute='c_omp')
    istep = sim.get_data(data_class='param', attribute='istep')
    dens = sim.get_data(data_class='scalar_flds', fld='density')['data']

    plt.imshow(
        dens[0, :, :],
        extent=(0, dens.shape[2]*istep/c_omp, 0, dens.shape[1]*istep/c_omp))
    shock_finder = ConstVelShockFinderV1(sim)
    shock_dict = shock_finder.calc_shock_loc()
    plt.axvline(shock_dict['shock_loc'], c='w')
    plt.show()
