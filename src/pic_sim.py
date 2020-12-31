import re
import sys
import os
import h5py
import yaml
import numpy as np
from my_parser import ExprParser, AttributeNotFound
from dict_of_spect_methods import _spect_classes

_default_cfg = os.path.join(
    os.path.dirname(__file__), 'code_output_configs', 'tristan_v1.yml')


class picSim(object):
    available_units = ['file', 'c_ompe']  # 'c_ompi']

    def __init__(self,
                 name=None,
                 num=None,
                 dirpath=os.curdir,
                 cfg_file=_default_cfg):
        self.sim_num = num
        self._outdir = dirpath
        self._xtra_stride = 1
        self._data_dictionary = {}
        self._name = name
        self.__cur_n = -1
        self._fnum = []  # An array that holds the suffix of all the files
        self.time_array = []  # An array that holds the times
        self.parser = ExprParser(self)
        self._cfg_file = ''

        if 'iseult_conf.yml' in os.listdir(self.outdir):

            self.cfg_file = os.path.join(self.outdir,  'iseult_conf.yml')
            try:
                self.sim_type = self._cfgDict['name']
            except KeyError:
                self.sim_type = 'Undefined'

            self.clear_caches()
            if len(self) == 0:
                self.outdir = os.path.join(self.outdir, 'output')
        else:
            # can't find the config file, gotta use the default ones
            # first see if v1 works:
            self.try_default_sim_types()

    def get_shock_speed(self):
        if 'shock_speed' not in self._data_dictionary:
            shock_loc = self.get_data(
                data_class='shock_finders',
                shock_method='Density Half Max',
                n=len(self) - 1
            )['shock_loc']
            end_time = self.get_data(
                data_class='param',
                attribute='time',
                n=len(self) - 1
            )
            self._data_dictionary['shock_speed'] = shock_loc/end_time
        return self._data_dictionary['shock_speed']

    def get_domain_size(self):
        response = {}
        for elm in ['x', 'y', 'z']:
            response[elm] = len(
                self.get_data(data_class='axes',
                              attribute=elm)['data']
            )
        return response

    def get_time(self, units=None):
        if units not in self.available_units:
            units = None
        if units is None:
            return self.__cur_n
        elif units == 'file':
            return self.file_list[self.__cur_n]
        elif units == 'c_ompe':
            return self.time_array[self.__cur_n]

    def set_time(self, t_arg, units=None):
        if units is None:
            if t_arg < 0:
                t_arg = self.__len__() - t_arg
            self.__cur_n = min(t_arg, self.__len__() - 1)
        # THIS IS O(N) NEED IMPROVEMENT
        if units == 'file':
            self.__cur_n = self.file_list.index(t_arg)

    def get_f_numbers(self):
        """A function that gets passed a directory and simulation type
        and retuns an ordered list of all the endings of the simulation output
        files."""

        file_names = self._cfgDict['h5_files_list'].keys()
        output_file_names = [name for name in file_names]
        tmp_dict = {}
        for name in output_file_names:
            for h5attr in self._cfgDict['h5_files_list'][name]:
                tmp_dict[h5attr] = os.path.join(self.outdir, name[:-1])

        self.parser.vars = tmp_dict
        output_file_keys = [key.split('.')[0] for key in self._cfgDict['expected_output_files']]
        output_file_regex = [re.compile(elm) for elm in self._cfgDict['expected_output_files']]
        path_dict = {}
        try:
            # Create a dictionary of all the paths to the files
            has_star = 0
            for key, regex in zip(output_file_keys, output_file_regex):
                path_dict[key] = [
                    item for item in
                    filter(regex.match, os.listdir(self.outdir))
                ]

                path_dict[key].sort()
                tmp_list = []
                for i in range(len(path_dict[key])):
                    elm = path_dict[key][i]
                    try:
                        int(elm.split('.')[-1])
                        tmp_list.append(elm)
                    except ValueError:
                        if elm.split('.')[-1] == '***':
                            has_star += 1
                path_dict[key] = tmp_list
            # GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            list_of_files = path_dict[output_file_keys[0]]
            all_there = set(elm.split('.')[-1] for elm in list_of_files)
            for key in path_dict.keys():
                all_there &= set(elm.split('.')[-1] for elm in path_dict[key])
            all_there = list(sorted(all_there, key=lambda x: int(x)))
            if has_star == len(path_dict.keys()):
                all_there.append('***')
            return all_there

        except OSError:
            return []

    def __len__(self):
        return len(self.file_list)

    @property
    def cfg_file(self):
        return self._cfg_file

    @cfg_file.setter
    def cfg_file(self, cfg):
        self._cfg_file = cfg
        with open(self._cfg_file, 'r') as f:
            self._cfgDict = yaml.safe_load(f)
        self.sim_type = self._cfgDict['name']
        try:
            self.SpectralClass = _spect_classes[
                self._cfgDict['spectra']['name_of_spect_class']
            ](self)
        except KeyError:
            self.SpectralClass = None
            print("Cannot load spectral data")
        try:
            self.shock_finder = self._cfgDict['shock_methods']['shock_finder']
        except KeyError:
            pass
        self.refresh_directory()
        self.parser.clear_caches()
        self._data_dictionary = {}

    @property
    def file_list(self):
        return self._fnum

    @file_list.setter
    def file_list(self, val):
        self._fnum = val
        self.time_array = np.empty(len(self._fnum))
        self.parser.string = self._cfgDict['time']
        for i, suffix in enumerate(self._fnum):
            self.parser.string = self._cfgDict['time']
            self.parser.f_suffix = suffix
            self.time_array[i] = self.parser.getValue()

    def clear_caches(self):
        self.cfg_file = self._cfg_file
        # self.refresh_directory()
        # self.parser.clear_caches()
        # self._data_dictionary = {}

    def refresh_directory(self):
        self.file_list = self.get_f_numbers()

    def try_default_sim_types(self):
        default_sim_types = {}
        sim_cfgs_dir = os.path.join(
            os.path.dirname(__file__), 'code_output_configs')

        tmp_list = []
        for cfg_file in os.listdir(sim_cfgs_dir):
            if not cfg_file.startswith('.'):
                elm = os.path.join(sim_cfgs_dir, cfg_file)
                tmp_list.append(os.path.abspath(elm))
        filter(lambda x: x.split[-1] == '.yml', tmp_list)
        for cfg in tmp_list:
            with open(cfg, 'r') as f:
                tmpDict = yaml.safe_load(f)
                if 'name' in tmpDict:
                    default_sim_types[tmpDict['name']] = cfg
        for sim_type, cfg_path in default_sim_types.items():
            self.cfg_file = cfg_path
            if len(self) == 0:
                if 'output' in os.listdir(self.outdir):
                    self.outdir = os.path.join(self.outdir, 'output')
            if len(self) != 0:
                break

    @property
    def name(self):
        return self._name

    # setting the values
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def outdir(self):
        return self._outdir

    # setting the values
    @outdir.setter
    def outdir(self, dirname):
        if os.path.isdir(dirname):
            self._outdir = dirname
            self.clear_caches()
            if 'iseult_conf.yml' in os.listdir(self.outdir):
                self.cfg_file = os.path.join(self.outdir,  'iseult_conf.yml')
                try:
                    self.sim_type = self._cfgDict['name']
                except KeyError:
                    self.sim_type = 'Undefined'
                self.clear_caches()
                if len(self) == 0:
                    if 'output' in os.listdir(self.outdir):
                        self.outdir = os.path.join(self.outdir, 'output')

            else:
                # can't find the config file, gotta use the default ones
                self.try_default_sim_types()
        else:
            print(f'{dirname} is not a directory')

    @property
    def xtra_stride(self):
        return self._xtra_stride

    # setting the values
    @xtra_stride.setter
    def xtra_stride(self, stride):
        self._xtra_stride = stride
        self.parser.prtl_stride = stride
        self.clear_caches()

    def get_available_quantities(self):
        # Returns a hierachical dictionary structure showing
        # All available data quantities from the simulations
        return self._cfgDict

    def get_data(self, n=None, **kwargs):
        """ This function is how you should access data on the hdf5
        files."""

        lookup = {'data_class': None}
        for key, val in kwargs.items():
            lookup[key] = val
        if n is None:
            n = self.__cur_n

        response_dict = {}

        if lookup['data_class'] == 'scalar_v_time':
            self.parser.prtl_stride = 1
            response_dict = {
                'data': np.array([]),
                'times': np.array([]),
                'label': ''
            }
            try:
                if n < len(self.file_list):
                    f_suffix = self.file_list[n]
                else:
                    return response_dict
                if lookup['scalar'] in self._cfgDict['scalars'].keys():
                    expr = self._cfgDict['scalars'][lookup['scalar']]['expr']

                    if expr is not None:
                        hash_key = '{0}_v_time'.format(lookup['scalar'])
                        if hash_key not in self._data_dictionary:
                            self._data_dictionary[hash_key] = response_dict

                        scalar_data = self._data_dictionary[hash_key]

                        # Get the current time:
                        self.parser.string = self._cfgDict['time']
                        self.parser.f_suffix = f_suffix
                        cur_time = self.parser.getValue()

                        time_arr = self._data_dictionary[hash_key]['times']

                        # if time_arr.take(
                        #     time_arr.searchsorted(cur_time),
                        #     mode='clip'
                        # ) != cur_time:

                        time_arr = np.sort(np.append(time_arr, cur_time))
                        self._data_dictionary[hash_key]['times'] = time_arr

                        ind = time_arr.searchsorted(cur_time)[0]
                        data_arr = self._data_dictionary[hash_key]['data']
                        self.parser.string = expr
                        val = self.parser.getValue()

                        data_arr = np.append(
                            np.append(
                                data_arr[0:ind], val),
                            data_arr[ind:])
                        self._data_dictionary[hash_key]['data'] = data_arr

                    response_dict = self._data_dictionary[hash_key]
                    label = self._cfgDict['scalars'][lookup['scalar']]['label']
                    response_dict['label'] = label

            except IndexError:
                pass
            except AttributeNotFound:
                pass
            self.parser.prtl_stride = self.xtra_stride
            return response_dict

        elif lookup['data_class'] == 'prtls':
            response_dict = {
                'data': np.array([]),
                'axis_label': '',
                'hist_cbar_label': ''
            }
            try:

                f_suffix = self.file_list[n]
                if lookup['prtl_type'] in self._cfgDict['prtls'].keys():
                    prtl = self._cfgDict['prtls'][lookup['prtl_type']]
                    if lookup['attribute'] in prtl['attrs'].keys():
                        hash_key = 'prtls' + lookup['prtl_type']
                        hash_key += lookup['attribute'] + f_suffix
                        if hash_key not in self._data_dictionary:
                            expr = prtl['attrs'][lookup['attribute']]['expr']
                            if expr is not None:
                                self.parser.string = expr
                                self.parser.f_suffix = f_suffix
                                val = self.parser.getValue()
                                self._data_dictionary[hash_key] = val
                        response_dict['data'] = self._data_dictionary[hash_key]
                        ax_label = prtl['attrs'][lookup['attribute']]['label']
                        response_dict['axis_label'] = ax_label
                        cbar_label = prtl['hist_cbar_label']
                        response_dict['hist_cbar_label'] = cbar_label
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

        elif lookup['data_class'] == 'param':
            try:
                f_suffix = self.file_list[n]
                expr = self._cfgDict['param'][lookup['attribute']]['expr']
                if expr is not None:
                    hash_key = 'param' + lookup['attribute'] + f_suffix
                    if hash_key not in self._data_dictionary:
                        self.parser.string = expr
                        self.parser.f_suffix = f_suffix
                        self._data_dictionary[hash_key] = np.squeeze(
                            self.parser.getValue())
                    return self._data_dictionary[hash_key]
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return 1.0

        elif lookup['data_class'] == 'scalar_flds':
            response_dict = {
                'data': np.empty((2, 2, 2)),
                'label': ''
            }

            try:
                f_suffix = self.file_list[n]
                if lookup['fld'] in self._cfgDict['scalar_flds'].keys():
                    fld = self._cfgDict['scalar_flds'][lookup['fld']]
                    hash_key = 'scalar_flds' + lookup['fld'] + f_suffix
                    if hash_key not in self._data_dictionary:
                        expr = fld['expr']
                        self.parser.string = expr
                        self.parser.f_suffix = f_suffix
                        val = self.parser.getValue()
                        self._data_dictionary[hash_key] = val
                    response_dict['data'] = self._data_dictionary[hash_key]
                    response_dict['label'] = fld['label']
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

        elif lookup['data_class'] == 'vec_flds':
            response_dict = {
                'data': np.empty((2, 2, 2)),
                'axis_label': '',
                'label': ''
            }
            try:
                f_suffix = self.file_list[n]
                if lookup['fld'] in self._cfgDict['vec_flds'].keys():
                    fld = self._cfgDict['vec_flds'][lookup['fld']]
                    if lookup['component'] in fld.keys():
                        hash_key = 'vec_flds' + lookup['fld']
                        hash_key = hash_key + lookup['component'] + f_suffix
                        if hash_key not in self._data_dictionary:
                            expr = fld[lookup['component']]['expr']
                            self.parser.string = expr
                            self.parser.f_suffix = f_suffix
                            val = self.parser.getValue()
                            self._data_dictionary[hash_key] = val
                        response_dict['data'] = self._data_dictionary[hash_key]
                        response_dict['axis_label'] = fld['axis_label']
                        label = fld[lookup['component']]['label']
                        response_dict['label'] = label
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

        elif lookup['data_class'] == 'axes':
            response_dict = {
                'data': np.arange(1),
                'label': ''
            }
            try:
                f_suffix = self.file_list[n]
                hash_key = 'axes' + lookup['attribute'] + f_suffix
                if hash_key not in self._data_dictionary:
                    expr = self._cfgDict['axes'][lookup['attribute']]['expr']
                    self.parser.string = expr
                    self.parser.f_suffix = f_suffix
                    self._data_dictionary[hash_key] = self.parser.getValue()
                response_dict['data'] = self._data_dictionary[hash_key]
                label = self._cfgDict['axes'][lookup['attribute']]['label']
                response_dict['label'] = label
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

        elif lookup['data_class'] == 'scalar':
            response_dict = {
                'data': np.arange(2),
                'label': ''
            }
            try:
                f_suffix = self.file_list[n]
                hash_key = 'scalar' + lookup['attribute'] + f_suffix
                if hash_key not in self._data_dictionary:
                    expr = self._cfgDict['scalar'][lookup['attribute']]['expr']
                    self.parser.string = expr
                    self.parser.f_suffix = f_suffix
                    self._data_dictionary[hash_key] = self.parser.getValue()
                response_dict['data'] = self._data_dictionary[hash_key]
                label = self._cfgDict['scalar'][lookup['attribute']]['label']
                response_dict['label'] = label
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

        elif lookup['data_class'] == 'shock_finders':
            response_dict = {
                'shock_loc': 0,
                'axis': 'x'
            }
            try:
                f_suffix = self.file_list[n]
                hash_key = 'shock_finders' + lookup['shock_method'] + f_suffix
                shock_finders = self._cfgDict['shock_finders']
                if hash_key not in self._data_dictionary:
                    expr = shock_finders[lookup['shock_method']]['expr']
                    self.parser.string = expr
                    self.parser.f_suffix = f_suffix
                    self._data_dictionary[hash_key] = self.parser.getValue()
                response_dict['shock_loc'] = self._data_dictionary[hash_key]
                label = shock_finders[lookup['shock_method']]['axis']
                response_dict['axis'] = label
            except IndexError:
                pass
            except AttributeNotFound:
                pass
            return response_dict

if __name__ == '__main__':
    sim = picSim(dirpath=os.path.join(os.path.dirname(__file__), '../output'))
    print(len(sim))
    print(
        sim.get_data(
            n=2, data_class='prtls', prtl_type='ions', attribute='KE'))
    print(
        sim.get_data(
            n=2, data_class='prtls', prtl_type='electrons', attribute='z'))
    print(sim.get_data(n=2, data_class='vec_flds', fld='E', component='x'))
    print(sim.get_data(n=2, data_class='scalar_flds', fld='density'))
    print(sim.get_data(n=2, data_class='param', attribute='c_omp'))
    print(sim.get_data(n=2, data_class='scalar_v_time', scalar='Total KE_e'))
    print(sim.get_data(n=0, data_class='scalar_v_time', scalar='Total KE_e'))
    print(sim.get_data(n=1, data_class='scalar_v_time', scalar='Total KE_e'))
