import re
import sys
import os
import h5py
import yaml
import numpy as np
# sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from my_parser import ExprParser


def h5_getter(filepath, attribute, prtl_stride=None):
    with h5py.File(filepath, 'r') as f:
        if prtl_stride is not None:
            return f[attribute][::prtl_stride]
        else:
            return f[attribute][:]


default_cfg = os.path.join(
    os.path.dirname(__file__), 'code_output_configs', 'tristan_v1.yml')


class picSim(object):
    available_units = ['file']  # ['c_ompe', 'file', 'c_ompi']

    def __init__(self,
                 name=None, dirpath=os.curdir, cfg_file=default_cfg):

        self._outdir = dirpath
        self._xtra_stride = 1
        self._data_dictionary = {}
        self._name = name
        self.__cur_n = -1
        self._fnum = 0
        self.parser = ExprParser()
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

    def get_time(self, units=None):
        if units not in self.available_units:
            units = None
        if units is None:
            return self.__cur_n
        elif units == 'file':
            return self.file_list[self.__cur_n]
        # elif self.units == 'lap':
        #    self.__units = 'lap'
        # elif self.units == 'c_ompe':
        #    self.__units = 'c_ompe'
        # elif self.units == 'c_ompi':
        #    self.__units = 'c_ompi'

    def set_time(self, t_arg, units=None):
        if units is None:
            if t_arg < 0:
                t_arg = self.__len__() - t_arg
            self.__cur_n = min(t_arg, self.__len__() - 1)
        # THIS IS O(N) NEED IMPROVEMENT
        if units == 'file':
            self.__cur_n = self.file_list.index(t_arg)
        #    self.__units = 'lap'
        # elif units == 'c_ompe':
        #    self.__unit = 'c_ompe'
        # elif units_str == 'c_ompi':
    #    self.__units = 'c_ompi'

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
        output_file_keys = [key.split('.')[0] for key in output_file_names]
        output_file_regex = [re.compile(elm) for elm in output_file_names]
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
                for i in range(len(path_dict[key])):
                    elm = path_dict[key][i]
                    try:
                        int(elm.split('.')[-1])
                    except ValueError:
                        if elm.split('.')[-1] == '***':
                            has_star += 1
                        path_dict[key].remove(elm)

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
        return len(self._fnum)

    @property
    def cfg_file(self):
        return self._cfg_file

    @cfg_file.setter
    def cfg_file(self, cfg):
        self._cfg_file = cfg
        with open(self._cfg_file, 'r') as f:
            self._cfgDict = yaml.safe_load(f)
        self.sim_type = self._cfgDict['name']
        self.clear_caches()

    @property
    def file_list(self):
        return self._fnum

    def clear_caches(self):
        self._fnum = self.get_f_numbers()
        self._data_dictionary = {}

    def refresh_directory(self):
        self._fnum = self.get_f_numbers()

    def try_default_sim_types(self):
        default_sim_types = {}
        sim_cfgs_dir = os.path.join(
            os.path.dirname(__file__), 'code_output_configs')

        tmp_list = []
        for cfg_file in os.listdir(sim_cfgs_dir):
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

        if lookup['data_class'] == 'prtls':
            response_dict = {
                'data': np.array([]),
                'axis_label': '',
                'hist_cbar_label': ''
            }
            try:
                f_end = self._fnum[n]
                if lookup['prtl_type'] in self._cfgDict['prtls'].keys():
                    prtl = self._cfgDict['prtls'][lookup['prtl_type']]
                    if lookup['attribute'] in prtl['attrs'].keys():
                        hash_key = 'prtls' + lookup['prtl_type']
                        hash_key += lookup['attribute'] + f_end
                        if hash_key not in self._data_dictionary:
                            expr = prtl['attrs'][lookup['attribute']]['expr']
                            if expr is not None:
                                self.parser.string = expr
                                self.parser.f_end = f_end
                                val = self.parser.getValue()
                                self._data_dictionary[hash_key] = val
                        response_dict['data'] = self._data_dictionary[hash_key]
                        ax_label = prtl['attrs'][lookup['attribute']]['label']
                        response_dict['axis_label'] = ax_label
                        cbar_label = prtl['hist_cbar_label']
                        response_dict['hist_cbar_label'] = cbar_label
            except IndexError:
                pass
            return response_dict

        elif lookup['data_class'] == 'param':
            try:
                f_end = self._fnum[n]
                expr = self._cfgDict['param'][lookup['attribute']]['expr']
                if expr is not None:
                    hash_key = 'param' + lookup['attribute']
                    if hash_key not in self._data_dictionary:
                        self.parser.string = expr
                        self.parser.f_end = f_end
                        self._data_dictionary[hash_key] = np.squeeze(
                            self.parser.getValue())
                    return self._data_dictionary[hash_key]
            except IndexError:
                pass
            return 1.0

        elif lookup['data_class'] == 'scalar_flds':
            response_dict = {
                'data': np.empty((1, 1, 1)),
                'label': ''
            }

            try:
                f_end = self._fnum[n]
                if lookup['fld'] in self._cfgDict['scalar_flds'].keys():
                    fld = self._cfgDict['scalar_flds'][lookup['fld']]
                    hash_key = 'scalar_flds' + lookup['fld'] + f_end
                    if hash_key not in self._data_dictionary:
                        expr = fld['expr']
                        self.parser.string = expr
                        self.parser.f_end = f_end
                        val = self.parser.getValue()
                        self._data_dictionary[hash_key] = val
                    response_dict['data'] = self._data_dictionary[hash_key]
                    response_dict['label'] = fld['label']
            except IndexError:
                pass
            return response_dict

        elif lookup['data_class'] == 'vec_flds':
            response_dict = {
                'data': np.empty((1, 1, 1)),
                'axis_label': '',
                'label': ''
            }
            try:
                f_end = self._fnum[n]
                if lookup['fld'] in self._cfgDict['vec_flds'].keys():
                    fld = self._cfgDict['vec_flds'][lookup['fld']]
                    if lookup['component'] in fld.keys():
                        hash_key = 'vec_flds' + lookup['fld']
                        hash_key = hash_key + lookup['component'] + f_end
                        if hash_key not in self._data_dictionary:
                            expr = fld[lookup['component']]['expr']
                            self.parser.string = expr
                            self.parser.f_end = f_end
                            val = self.parser.getValue()
                            self._data_dictionary[hash_key] = val
                        response_dict['data'] = self._data_dictionary[hash_key]
                        response_dict['axis_label'] = fld['axis_label']
                        label = fld[lookup['component']]['label']
                        response_dict['label'] = label
            except IndexError:
                pass
            return response_dict

        elif lookup['data_class'] == 'axes':
            response_dict = {
                'data': np.empty(1),
                'label': ''
            }
            try:
                f_end = self._fnum[n]
                hash_key = 'axes' + lookup['attribute'] + f_end
                if hash_key not in self._data_dictionary:
                    expr = self._cfgDict['axes'][lookup['attribute']]['expr']
                    self.parser.string = expr
                    self.parser.f_end = f_end
                    self._data_dictionary[hash_key] = self.parser.getValue()
                response_dict['data'] = self._data_dictionary[hash_key]
                label = self._cfgDict['axes'][lookup['attribute']]['label']
                response_dict['label'] = label
            except IndexError:
                pass
            return response_dict


if __name__ == '__main__':
    sim = picSim(os.path.join(os.path.dirname(__file__), '../output'))
    print(
        sim.get_data(
            n=15, data_class='prtls', prtl_type='ions', attribute='KE'))
    print(
        sim.get_data(
            n=15, data_class='prtls', prtl_type='electrons', attribute='z'))
    print(sim.get_data(n=15, data_class='vec_flds', fld='E', component='x'))
    print(sim.get_data(n=15, data_class='scalar_flds', fld='density'))
    print(sim.get_data(n=15, data_class='param', attribute='c_omp'))
