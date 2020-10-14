import numpy as np


def dens_half_max_shock(dens, c_omp, istep):
    # average along x-axis
    dens_1d = np.average(
        dens.reshape(-1, dens.shape[-1]), axis=0)

    dens_half_max = max(dens_1d)*.5

    # Find the farthest location where the average density is greater
    # than half max
    ishock = np.where(dens_1d >= dens_half_max)[0][-1]
    return ishock * istep / c_omp


def const_vel_shock(sim):
    cur_time = sim.get_data(
        data_class='param',
        attribute='time'
    )
    return sim.get_shock_speed()*cur_time
