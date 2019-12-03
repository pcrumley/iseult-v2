import re, sys, os, h5py, yaml
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))


def h5_getter(filepath, attribute, prtl_stride = None):
    with h5py.File(filepath, 'r') as f:
        #if prtl_stride is not None:
        #    return f[attribute][::prtl_stride]
        #else:
        return f[attribute][:]

class picSim(object):
    def __init__(self, dirpath=None, cfg_file ='tristan_v2.yml'):
        self._outdir = dirpath
        cfg_file = os.path.join(os.path.join(os.path.dirname(__file__), 'code_output_configs', cfg_file))
        with open(cfg_file, 'r') as f:
            self._cfgDict=yaml.safe_load(f)
        self.sim_type = self._cfgDict['name']
        self._xtra_stride = 1
        self._fnum = self.get_f_numbers()
        self._data_dictionary = {}

    def get_f_numbers(self):
        """A function that gets passed a directory and simulation type
        and retuns an ordered list of all the endings of the simulation output files.
        """
        output_file_names = self._cfgDict['h5_files_list']
        output_file_keys = [key.split('.')[0] for key in output_file_names]
        output_file_regex = [re.compile(elm) for elm in  output_file_names]
        path_dict = {}
        try:
            # Create a dictionary of all the paths to the files
            has_star = 0
            for key, regex in zip(output_file_keys, output_file_regex):
                path_dict[key] = [item for item in filter(regex.match, os.listdir(self.outdir))]
                path_dict[key].sort()
                for i in range(len(path_dict[key])):
                    elm = path_dict[key][i]
                    try:
                        int(elm.split('.')[-1])
                    except ValueError:
                        if elm.split('.')[-1] == '***':
                            has_star += 1
                        path_dict[key].remove(elm)
            ### GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            all_there = set(elm.split('.')[-1] for elm in path_dict[output_file_keys[0]])
            for key in path_dict.keys():
                all_there &= set(elm.split('.')[-1] for elm in path_dict[key])
            all_there = list(sorted(all_there, key = lambda x: int(x)))
            if has_star == len(path_dict.keys()):
                all_there.append('***')
            return all_there

        except OSError:
            return []
    def __len__(self):
        return len(self._fnum)

    @property
    def file_list(self):
        return self._fnum

    def clear_caches(self):
        self._fnum = self.get_f_numbers()
        self._data_dictionary = {}

    def refresh_directory(self):
        self._fnum = self.get_f_numbers()

    @property
    def outdir(self):
        return self._outdir

    # setting the values
    @outdir.setter
    def outdir(self, dirname):
        self._outdir = dirname
        self.clear_caches()

    @property
    def xtra_stride(self):
        return self._xtra_stride

    # setting the values
    @xtra_stride.setter
    def xtra_stride(self, stride):
        self._xtra_stride = stride
        self._data_dictionary = {}

    def get_available_quantities(self):
        # Returns a hierachical dictionary structure showing
        # All available data quantities from the simulations
        return self._cfgDict

    def get_data(self, n = -1, **kwargs):
        """ This function is how you should access data on the hdf5
        files."""

        lookup = {'data_class': None}
        for key, val in kwargs.items():
            lookup[key] = val

        f_end = self.file_list[n]
        response_dir = {}
        try:
            if lookup['data_class'] == 'prtls':
                if lookup['prtl_type'] in self._cfgDict['prtls'].keys():
                    if lookup['attribute'] in self._cfgDict['prtls'][lookup['prtl_type']].keys():
                        hash_key = lookup['data_class']  + lookup['prtl_type']
                        hash_key += lookup['attribute'] + f_end
                        if hash_key not in self._data_dictionary:
                            if self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['h5attr'] is not None:
                                fpath = self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['h5file']
                                fpath = os.path.join(self.outdir, fpath) + f_end
                                self._data_dictionary[hash_key] = h5_getter(fpath,
                                    self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['h5attr'])
                            elif lookup['attribute'] == 'gamma':
                                self._data_dictionary[hash_key] = np.sqrt(
                                    self.get_data(n,
                                        data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                        attribute = 'px')['data']**2
                                    + self.get_data(n,
                                        data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                        attribute = 'py')['data']**2
                                    + self.get_data(n,
                                        data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                        attribute = 'pz')['data']**2
                                     + 1)
                            elif lookup['attribute'] == 'KE':
                                self._data_dictionary[hash_key] = self.get_data(n,
                                                data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                                attribute = 'gamma')['data'] - 1
                        if self.xtra_stride > 1:
                            fpath = self._cfgDict['prtls'][lookup['prtl_type']]['index']['h5file']
                            fpath = os.path.join(self.outdir, fpath) + f_end
                            indices = h5_getter(fpath, self._cfgDict['prtls'][lookup['prtl_type']]['index']['h5attr'])
                            if self.sim_type == 'Tristan_MP':
                                indices = indices//2

                            response_dir['data'] = self._data_dictionary[hash_key][np.mod(indices,self.xtra_stride) == 0]
                        else:
                            response_dir['data'] = self._data_dictionary[hash_key]
                        response_dir['axis_label'] = self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['axis_label']
                        response_dir['1d_label'] =  self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['1d_label']
                        response_dir['hist_cbar_label'] =  self._cfgDict['prtls'][lookup['prtl_type']][lookup['attribute']]['hist_cbar_label']
                        return response_dir

            elif lookup['data_class'] == 'vec_flds':
                if lookup['fld'] in self._cfgDict['vec_flds'].keys():
                    if lookup['component'] in self._cfgDict['vec_flds'][lookup['fld']].keys():
                        hash_key = 'vec_flds' + lookup['fld'] + lookup['component'] + f_end
                        if hash_key not in self._data_dictionary:
                            if self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['h5attr'] is not None:
                                fpath = self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['h5file']
                                fpath = os.path.join(self.outdir, fpath) + f_end
                            self._data_dictionary[hash_key] = h5_getter(fpath,
                                self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['h5attr'])
                        response_dir['data'] = self._data_dictionary[hash_key]
                        response_dir['axis_label'] = self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['axis_label']
                        response_dir['1d_label'] = self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['1d_label']
                        response_dir['cbar_label'] = self._cfgDict['vec_flds'][lookup['fld']][lookup['component']]['cbar_label']
                        return response_dir
            elif lookup['data_class'] == 'scalar_flds':
                fpath = os.path.join(self.outdir, 'flds.tot.') + f_end
                if lookup['fld'] in self._cfgDict['scalar_flds'].keys():
                    hash_key = 'scalar_flds' + lookup['fld'] + f_end
                    if hash_key not in self._data_dictionary:
                        if self._cfgDict['scalar_flds'][lookup['fld']]['h5attr'] is not None:
                            self._data_dictionary[hash_key] = h5_getter(fpath,
                                self._cfgDict['scalar_flds'][lookup['fld']]['h5attr'])

                        elif lookup['fld'] == 'rho':
                                self._data_dictionary[hash_key] = self.get_data(n,
                                            data_class = 'scalar_flds',
                                            fld = 'ion_density')['data'] - self.get_data(n,
                                            data_class = 'scalar_flds',
                                            fld = 'electron_density')['data']
                        elif lookup['fld'] == 'electron_density':
                            self._data_dictionary[hash_key] = -self.get_data(n,
                                        data_class = 'scalar_flds',
                                        fld = 'ion_density')['data'] + self.get_data(n,
                                        data_class = 'scalar_flds',
                                        fld = 'density')['data']
                        elif lookup['fld'] == 'B_total':

                            tmp = self.get_data(n, data_class='vec_flds', fld = 'B', component = 'x')['data']**2
                            tmp += self.get_data(n, data_class='vec_flds', fld = 'B', component = 'y')['data']**2
                            tmp += self.get_data(n, data_class='vec_flds', fld = 'B', component = 'z')['data']**2

                            self._data_dictionary[hash_key] = np.sqrt(tmp)
                        elif lookup['fld'] == 'theta_B':
                            bx = self.get_data(n, data_class='vec_flds', fld = 'B', component = 'x')['data']
                            bperp = self.get_data(n, data_class='vec_flds', fld = 'B', component = 'y')['data']**2
                            bperp += self.get_data(n, data_class='vec_flds', fld = 'B', component = 'z')['data']**2
                            self._data_dictionary[hash_key] = np.arctan2(np.sqrt(bperp), bx)
                        elif lookup['fld'] == 'density':
                            self._data_dictionary[hash_key] = self.get_data(n,
                                        data_class = 'scalar_flds',
                                        fld = 'electron_density')['data'] + self.get_data(n,
                                        data_class = 'scalar_flds',
                                        fld = 'ion_density')['data']
                    response_dir['data'] = self._data_dictionary[hash_key]
                    response_dir['axis_label'] = self._cfgDict['scalar_flds'][lookup['fld']]['axis_label']
                    response_dir['1d_label'] = self._cfgDict['scalar_flds'][lookup['fld']]['1d_label']
                    response_dir['cbar_label'] = self._cfgDict['scalar_flds'][lookup['fld']]['cbar_label']
                    return response_dir
            elif lookup['data_class'] == 'scalars':
                hash_key = 'scalars' + lookup['attribute'] + f_end
                if hash_key not in self._data_dictionary:
                    if lookup['attribute'] == 'shock_loc':
                        dens_avg1D = np.average(self.get_data(n, data_class='scalar_flds', fld = 'density')['data'], axis =2)
                        x_ax = self.get_data(n, data_class='axes', attribute= 'x')['data']
                        istep = self.get_data(n, data_class='param', attribute = 'istep')
                        c_omp = self.get_data(n, data_class='param', attribute = 'c_omp')

                        # Find out where the shock is at the last time step.
                        jstart = int(min(10*c_omp/istep, len(x_ax)))

                        dens_half_max = max(dens_avg1D[jstart:])*.5

                        # Find the farthest location where the average density is greater
                        # than half max
                        ishock = np.where(dens_avg1D[jstart:]>=dens_half_max)[0][-1]
                        self._data_dictionary[hash_key] = x_ax[ishock_final]

                    if lookup['attribute'] == 'const_shock_speed':
                        vel_shock = self.get_data(-1, data_class='scalars', attribute='shock_loc')['data']
                        vel_shock /= self.get_data(-1, data_class='scalars', attribute='time')['data']
                        return {'data': vel_shock, 'label': self._cfgDict[lookup['data_class']][lookup['attribute']]['label']}
                    else:
                        return {'data': 1.0, 'label': ''}
                return {'data': self._data_dictionary[hash_key], 'label': self._cfgDict[lookup['data_class']][lookup['attribute']]['label']}

            elif lookup['data_class'] == 'axes':
                hash_key = 'axes' + lookup['attribute'] + f_end
                if hash_key not in self._data_dictionary:
                    if lookup['attribute'] == 'x':
                        ans = np.arange(self.get_data(n, data_class='vec_flds', fld = 'B', component = 'x')['data'].shape[2])
                        ans = ans * self.get_data(n, data_class='param', attribute = 'istep')
                        ans = ans / self.get_data(n, data_class='param', attribute = 'c_omp')
                        self._data_dictionary[hash_key] = ans
                    elif lookup['attribute'] == 'y':
                        ans = np.arange(self.get_data(n, data_class='vec_flds', fld = 'B', component = 'x')['data'].shape[1])
                        ans = ans * self.get_data(n, data_class='param', attribute = 'istep')
                        ans = ans / self.get_data(n, data_class='param', attribute = 'c_omp')
                        self._data_dictionary[hash_key] = ans
                    elif lookup['attribute'] == 'z':
                        ans = np.arange(self.get_data(n, data_class='vec_flds', fld = 'B', component = 'x')['data'].shape[0])
                        ans = ans * self.get_data(n, data_class='param', attribute = 'istep')
                        ans = ans / self.get_data(n,data_class='param', attribute = 'c_omp')
                        self._data_dictionary[hash_key] = ans

                return {'data': self._data_dictionary[hash_key], 'label': self._cfgDict['axes'][lookup['attribute']]['axis_label']}
            elif lookup['data_class'] == 'param':
                if self._cfgDict['param'][lookup['attribute']]['h5attr'] is not None:
                    fpath = self._cfgDict['param'][lookup['attribute']]['h5file']
                    fpath = os.path.join(self.outdir, fpath) + f_end
                    return h5_getter(fpath,
                        self._cfgDict['param'][lookup['attribute']]['h5attr'])[0]
                else:
                    return 1.0
            else:
                return response_dir
        except KeyError:
            return response_dir
if __name__=='__main__':
    sim =picSim(os.path.join(os.path.dirname(__file__),'../output'))
    print(sim.get_data(n = 15, data_class='prtls', prtl_type = 'ions', attribute = 'KE'))
    print(sim.get_data(n = 15, data_class='prtls', prtl_type = 'electrons', attribute = 'z'))
    print(sim.get_data(n = 15, data_class='vec_flds', fld = 'E', component = 'x'))
    print(sim.get_data(n = 15, data_class='scalar_flds', fld = 'density'))
    print(sim.get_data(n = 15, data_class='param', attribute = 'c_omp'))
