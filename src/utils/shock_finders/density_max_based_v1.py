from shock_abc import ShockFinderABC
import numpy as np


class DensMaxShockFinderV1(ShockFinderABC):
    def __init__(self, sim):
        self.__sim = sim

    @property
    def sim(self):
        return self.__sim

    def calc_shock_loc(self, n=None):
        if n is None:
            n = self.sim.get_time()
        response_dict = {
            'shock_loc': 0,
            'axis': 'x'}
        if n < len(self.sim.file_list):
            f_suffix = self.sim.file_list[n]
        else:
            return response_dict

        hash_key = f'd_max_shock_v1{f_suffix}'
        if hash_key not in self.sim._data_dictionary:
            c_omp = self.sim.get_data(data_class='param', attribute='c_omp')
            istep = self.sim.get_data(data_class='param', attribute='istep')
            dens = self.sim.get_data(
                data_class='scalar_flds', fld='density')['data']

            # average along x-axis
            dens_1d = np.average(
                dens.reshape(-1, dens.shape[-1]), axis=0)

            dens_half_max = max(dens_1d)*.5

            # Find the farthest location where the average density is greater
            # than half max
            ishock = np.where(dens_1d >= dens_half_max)[0][-1]

            response_dict['shock_loc'] = ishock * istep / c_omp
            self.sim._data_dictionary[hash_key] = response_dict

        response_dict = self.sim._data_dictionary[hash_key]
        return response_dict


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

    shock_finder = DensMaxShockFinderV1(sim)
    f_suffix = sim.file_list[-1]
    # GET THE DATA
    c_omp = sim.get_data(data_class='param', attribute='c_omp')
    istep = sim.get_data(data_class='param', attribute='istep')
    dens = sim.get_data(data_class='scalar_flds', fld='density')['data']
    print(dens.shape)

    plt.imshow(
        dens[0, :, :],
        extent=(0, dens.shape[2]*istep/c_omp, 0, dens.shape[1]*istep/c_omp))
    shock_finder = DensMaxShockFinderV1(sim)
    shock_dict = shock_finder.calc_shock_loc()
    print(shock_dict)
    plt.axvline(shock_dict['shock_loc'], c='w')
    plt.show()
