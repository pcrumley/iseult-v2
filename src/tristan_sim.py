from functools import lru_cache#, #cached_property
import re, sys, os, h5py
import numpy as np

@lru_cache(maxsize = 32)
def get_flist_numbers(outdir = None, sim_type = 'v2'):
    """A function that gets passed a directory and simulation type
    and retuns an ordered list of all the endings of the simulation output files.
    """
    if sim_type == 'v2':
        output_file_names = ['domain.*', 'flds.tot.*', 'spec.tot.*', 'prtl.tot.*']
    else:
        output_file_names = []
    output_file_keys = [key.split('.')[0] for key in output_file_names]
    output_file_regex = [re.compile(elm) for elm in  output_file_names]
    path_dict = {}
    try:
        # Create a dictionary of all the paths to the files
        has_star = 0
        for key, regex in zip(output_file_keys, output_file_regex):
            path_dict[key] = [item for item in filter(regex.match, os.listdir(outdir))]
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

def n_to_fnum(outdir = None, n = -1, sim_type = 'v2'):
    f_list = get_flist_numbers(outdir, sim_type)
    return f_list[n]

data_structure = {
    'prtls': {
        'electrons' : {
            'x' : {
                'h5attr': 'x1',
                'axis_label': r'$x$',
                '1d_label': r'$x$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'y': {
                'h5attr': 'y1',
                'axis_label': r'$y$',
                '1d_label': r'$y$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'z': {
                'h5attr': 'z1',
                'axis_label': r'$z$',
                '1d_label': r'$z$',
                'hist_cbar_label': r'$f_d (p)$'
            },
            'px': {
                'h5attr': 'u1',
                'axis_label': r'$\gamma_e\beta_{e,x}$',
                '1d_label': r'$\gamma_e\beta_{e,x}$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'py': {
                'h5attr': 'v1',
                'axis_label': r'$\gamma_e\beta_{e,y}$',
                '1d_label': r'$\gamma_e\beta_{e,y}$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'pz': {
                'h5attr': 'w1',
                'axis_label': r'$\gamma_e\beta_{e,z}$',
                '1d_label': r'$\gamma_e\beta_{e,z}$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'gamma': {
                'h5attr': None,
                'axis_label': r'$\gamma_e$',
                '1d_label': r'$\gamma_e$',
                'hist_cbar_label': r'$f_e (p)$'
            },
            'proc': {
                'h5attr': 'proc1',
                'axis_label': r'$\mathrm{proc}_i$',
                '1d_label': r'$\mathrm{proc}_i$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'index': {
                'h5attr': 'ind1',
                'axis_label': r'$\mathrm{ind}_i$',
                '1d_label': r'$\mathrm{ind}_i$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'KE': {
                'h5attr': None,
                'axis_label': r'$KE_i$',
                '1d_label': r'$KE_i$',
                'hist_cbar_label': r'$f_i (p)$'
            }
        },
        'ions': {
            'x' : {
                'h5attr': 'x2',
                'axis_label': r'$x$',
                '1d_label': r'$x$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'y': {
                'h5attr': 'y2',
                'axis_label': r'$y$',
                '1d_label': r'$y$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'z': {
                'h5attr': 'z2',
                'axis_label': r'$z$',
                '1d_label': r'$z$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'px': {
                'h5attr': 'u2',
                'axis_label': r'$\gamma_i\beta_{i,x}$',
                '1d_label': r'$\gamma_i\beta_{i,x}$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'py': {
                'h5attr': 'v2',
                'axis_label': r'$\gamma_i\beta_{i,y}$',
                '1d_label': r'$\gamma_i\beta_{i,y}$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'pz': {
                'h5attr': 'w2',
                'axis_label': r'$\gamma_i\beta_{i,z}$',
                '1d_label': r'$\gamma_i\beta_{i,z}$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'gamma': {
                'h5attr': None,
                'axis_label': r'$\gamma_i$',
                '1d_label': r'$\gamma_i$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'proc': {
                'h5attr': 'proc2',
                'axis_label': r'$\mathrm{proc}_i$',
                '1d_label': r'$\mathrm{proc}_i$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'index': {
                'h5attr': 'ind2',
                'axis_label': r'$\mathrm{ind}_i$',
                '1d_label': r'$\mathrm{ind}_i$',
                'hist_cbar_label': r'$f_i (p)$'
            },
            'KE': {
                'h5attr': None,
                'axis_label': r'$KE_i$',
                '1d_label': r'$KE_i$',
                'hist_cbar_label': r'$f_i (p)$'
            }
        }
    },
    'vec_flds': {
        'E': {
            'x': {
                'h5attr': 'ex',
                'axis_label': r'$E$',
                '1d_label': r'$E_x$',
                'cbar_label': r'$E$'
            },
            'y': {
                'h5attr': 'ey',
                'axis_label': r'$E$',
                '1d_label': r'$E_y$',
                'cbar_label': r'$E$'
            },
            'z': {
                'h5attr': 'ez',
                'axis_label': r'$E$',
                '1d_label': r'$E_z$',
                'cbar_label': r'$E$'
            }
        },
        'B' : {
            'x': {
                'h5attr': 'bx',
                'axis_label': r'$B$',
                '1d_label': r'$B_x$',
                'cbar_label': r'$B$'
            },
            'y': {
                'h5attr': 'by',
                'axis_label': r'$B$',
                '1d_label': r'$B_y$',
                'cbar_label': r'$B$'
            },
            'z': {
                'h5attr': 'bz',
                'axis_label': r'$B$',
                '1d_label': r'$B_z$',
                'cbar_label': r'$B$'
            }
        },
        'J' : {
            'x': {
                'h5attr': 'jx',
                'axis_label': r'$J$',
                '1d_label': r'$J_x$',
                'cbar_label': r'$J$'
            },
            'y': {
                'h5attr': 'jy',
                'axis_label': r'$J$',
                '1d_label': r'$J_y$',
                'cbar_label': r'$J$'
            },
            'z': {
                'h5attr': 'jz',
                'axis_label': r'$J$',
                '1d_label': r'$J_z$',
                'cbar_label': r'$J$'
            }
        }
    },
    'scalar_flds': {
        'density': {
            'h5attr': None,
            'axis_label': r'$n$',
            '1d_label': r'$n$',
            'cbar_label': r'$n$'
        },
        'rho': {
            'h5attr': None,
            'axis_label': r'$\rho$',
            '1d_label': r'$\rho$',
            'cbar_label': r'$\rho$'
        },
        'electron_density': {
            'h5attr': 'dens1',
            'axis_label': r'$n_e$',
            '1d_label': r'$n_e$',
            'cbar_label': r'$n_e$'
        },
        'ion_density': {
            'h5attr': 'dens2',
            'axis_label': r'$n_i$',
            '1d_label': r'$n_i$',
            'cbar_label': r'$n_i$'
        },
        'theta_B': {
            'h5attr': None,
            'axis_label': r'$\theta_B$',
            '1d_label': r'$\theta_B$',
            'cbar_label': r'$\theta_B$'
        },
        'B_total': {
            'h5attr': None,
            'axis_label': r'$|B|$',
            '1d_label': r'$|B|$',
            'cbar_label': r'$|B|$'
        }
    },
    'scalars': {
        'Total KE_e',
        'Total KE_i',
        'time'
    },
    'params': {
        'istep': '',
        'stride': '',
        'mi': '',
        'me': '',
        'c_omp': '',
        'time': '',
        'ppc0': '',
        'qi': '',
        'sigma': ''
    }
}
def get_available_quantities(sim_type = 'v2'):
    # Returns a hierachical dictionary structure showing
    # All available data quantities from the simulations

    return data_structure



def h5_getter(filepath, attribute):
    with h5py.File(filepath, 'r') as f:
        return f[attribute][:]

@lru_cache()
def get_data(dirpath = None, n = -1, sim_type = 'v2',  **kwargs):
    """ This function is how you should access data on the hdf5
    files."""

    lookup = {
        'data_class': 'prtls',
        'prtl_type': 'ions',
        'attribute': 'x'
    }
    response_dir = {}
    for key, val in kwargs.items():
        lookup[key] = val

    if sim_type == 'v2':
        f_end = n_to_fnum(dirpath, n)
        if lookup['data_class'] == 'prtls':
            fpath = os.path.join(dirpath, 'prtl.tot.') + f_end
            if lookup['prtl_type'] in data_structure['prtls'].keys():
                if lookup['attribute'] in data_structure['prtls'][lookup['prtl_type']].keys():
                    if data_structure['prtls'][lookup['prtl_type']][lookup['attribute']]['h5attr'] is not None:
                        response_dir['data'] = h5_getter(fpath,
                            data_structure['prtls'][lookup['prtl_type']][lookup['attribute']]['h5attr'])

                    elif lookup['attribute'] == 'gamma':
                        response_dir['data'] = np.sqrt(
                            get_data(dirpath, n, sim_type,
                                data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                attribute = 'px')['data']**2
                            + get_data(dirpath, n, sim_type,
                                data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                attribute = 'py')['data']**2
                            + get_data(dirpath, n, sim_type,
                                data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                attribute = 'pz')['data']**2
                             + 1)
                    elif lookup['attribute'] == 'KE':
                        response_dir['data'] = get_data(dirpath, n, sim_type,
                                        data_class = 'prtls', prtl_type = lookup['prtl_type'],
                                        attribute = 'gamma')['data'] - 1

                    response_dir['axis_label'] = data_structure['prtls'][lookup['prtl_type']][lookup['attribute']]['axis_label']
                    response_dir['1d_label'] =  data_structure['prtls'][lookup['prtl_type']][lookup['attribute']]['1d_label']
                    response_dir['hist_cbar_label'] =  data_structure['prtls'][lookup['prtl_type']][lookup['attribute']]['hist_cbar_label']
                    return response_dir

        elif lookup['data_class'] == 'vec_flds':
            fpath = os.path.join(dirpath, 'flds.tot.') + f_end
            if lookup['fld'] in data_structure['vec_flds'].keys():
                if lookup['component'] in data_structure['vec_flds'][lookup['fld']].keys():
                    if data_structure['vec_flds'][lookup['fld']][lookup['component']]['h5attr'] is not None:
                        response_dir['data'] = h5_getter(fpath,
                            data_structure['vec_flds'][lookup['fld']][lookup['component']]['h5attr'])
                    response_dir['axis_label'] = data_structure['vec_flds'][lookup['fld']][lookup['component']]['axis_label']
                    response_dir['1d_label'] = data_structure['vec_flds'][lookup['fld']][lookup['component']]['1d_label']
                    response_dir['cbar_label'] = data_structure['vec_flds'][lookup['fld']][lookup['component']]['cbar_label']
                    return response_dir
        elif lookup['data_class'] == 'scalar_flds':
            fpath = os.path.join(dirpath, 'flds.tot.') + f_end
            if lookup['fld'] in data_structure['scalar_flds'].keys():
                if data_structure['scalar_flds'][lookup['fld']]['h5attr'] is not None:
                    response_dir['data'] = h5_getter(fpath,
                        data_structure['scalar_flds'][lookup['fld']]['h5attr'])
                elif lookup['fld'] == 'density':
                    response_dir['data'] = get_data(dirpath, n, sim_type,
                                    data_class = 'scalar_flds',
                                    fld = 'electron_density')['data'] + get_data(dirpath, n, sim_type,
                                    data_class = 'scalar_flds',
                                    fld = 'ion_density')['data']

                response_dir['axis_label'] = data_structure['scalar_flds'][lookup['fld']]['axis_label']
                response_dir['1d_label'] = data_structure['scalar_flds'][lookup['fld']]['1d_label']
                response_dir['cbar_label'] = data_structure['scalar_flds'][lookup['fld']]['cbar_label']
                return response_dir
        elif lookup['data_class'] == 'param':
            return 1.0
    else:
        return {}

if __name__=='__main__':
    print(n_to_fnum('output/',-1))
    print(get_data('output/', n = 15, data_class='prtls', prtl_type = 'ions', attribute = 'KE'))
    print(get_data('output/', n = 15, data_class='prtls', prtl_type = 'electrons', attribute = 'z'))
    print(get_data('output/', n = 15, data_class='vec_flds', fld = 'E', component = 'x'))
    print(get_data('output/', n = 15, data_class='scalar_flds', fld = 'density'))
    print(get_data('output/', n = 15, data_class='param', fld = 'c_omp'))
