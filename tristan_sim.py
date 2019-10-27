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

def get_available_quantities(sim_type = 'v2'):
    # Returns a hierachical dictionary structure showing
    # All available data quantities from the simulations
    data_structure = {
        'prtls': [
            { 'electrons' : [
                'x',
                'y',
                'z',
                'px',
                'py',
                'pz',
                'gamma',
                'proc',
                'index',
                'KE'
            ]},
            { 'ions': [
                'x',
                'y',
                'z',
                'px',
                'py',
                'pz',
                'gamma',
                'proc',
                'index',
                #'charge',
                'KE'
            ]}
        ],
        'vec_fields': [
            'E',
            'B',
            'J'
        ],
        'scalar_fields': [
            'density',
            'rho',
            'electron density',
            'ion density',
            'theta_B',
            'B total',
        ],
        'scalars': [
            'Total KE_e',
            'Total KE_i',
            'time'
        ],
        'params': []
    }
    return

@lru_cache()
def get_data(dirpath = None, n = -1, sim_type = 'v2', **kwargs):
    # First fi
    return 0

"""
class TristanSim(object):
    def __init__(self, dirpath=None, xtraStride = 1,

                ):

        # created RegEx for each of the output files
        self._outputFileNames = outputFileNames


        # Open one of the output files and l
        self._outputFileH5Keys = []
        self._pathDict = {}
        self._collisionFixers = collisionFixers
        self.dir = str(dirpath)

        self._name = os.path.split(self.dir)[-1]
        self.xtraStride = xtraStride
        self._h5Key2FileDict = {}

        self._fnum = self.getFileNums()
        self._trackStart = None
        self._trackStop = None
        self.dd = {}

        ### open first file and get all the keys:
        if len(self) != 0:
            for fname in self._outputFileNames:
                tmpStr = ''
                for elm in fname.split('.')[:-1]:
                    tmpStr += elm +'.'
                tmpStr += self._fnum[0]
                with h5py.File(os.path.join(self.dir, tmpStr), 'r') as f:
                    self._outputFileH5Keys.append([key for key in f.keys()])
            # Build an key to h5 file dictionary, and a h5 file to key dictionary
            self._output = [OutputPoint(self, n=x) for x in self.getFileNums()]
            for fkey in self._outputFileKey:
                for key in getattr(self[0], '_'+fkey).keys():
                    if key in self._h5Key2FileDict.keys():
                        if key not in self._collisionFixers.keys():
                            print(f'{key} in {fkey} has collision with {self._h5Key2FileDict[key]}')
                            print(f'Please update self._collisionFixers dictionary in __init__()')
                            print(f'function of TristanSim class')
                        else:
                            self._h5Key2FileDict[key] = self._collisionFixers[key]
                    else:
                        self._h5Key2FileDict[key] = fkey


            self._output[0].setKeys(self._h5Key2FileDict)

    def getFileNums(self):
        try:
            # Create a dictionary of all the paths to the files
            hasStar = 0
            for key, regEx in zip(self._outputFileKey, self._outputFileRegEx):
                self._pathDict[key] = [item for item in filter(regEx.match, os.listdir(self.dir))]
                self._pathDict[key].sort()
                for i in range(len(self._pathDict[key])):
                    elm = self._pathDict[key][i]
                    try:
                        int(elm.split('.')[-1])
                    except ValueError:
                        if elm.split('.')[-1] == '***':
                            hasStar += 1
                        self._pathDict[key].remove(elm)
            ### GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            allThere = set(elm.split('.')[-1] for elm in self._pathDict[self._outputFileKey[0]])
            for key in self._pathDict.keys():
                allThere &= set(elm.split('.')[-1] for elm in self._pathDict[key])
            allThere = list(sorted(allThere, key = lambda x: int(x)))
            if hasStar == len(self._pathDict.keys()):
                allThere.append('***')
            return allThere

        except OSError:
            return []

    def getFields(self):
        return []
    @property
    def trackKeys(self):
        return self._trackKeys

    # setting the values
    @trackKeys.setter
    def trackKeys(self, trackKeys):
        self._trackKeys = trackKeys

    @property
    def name(self):
        return self._name

    # setting the values
    @name.setter
    def name(self, myName):
        self._name = myName

    @property
    def trackStart(self):
        return self._trackStart

    # setting the values
    @trackStart.setter
    def trackStart(self, val):
        self._trackStart = val

    @property
    def trackStop(self):
        return self._trackStop

    # setting the values
    @trackStop.setter
    def trackStop(self, val):
        self._trackStop = val

    def __len__(self):
        #return np.sum(self._mask)
        return len(self._fnum)

    def __getitem__(self, val):
        return self._output[val]

    def loadAllFields(self):
        for out in self:
            for key, val in self._h5Key2FileDict.items():
                if val == 'flds':
                    getattr(out, key)
    def loadAllPrtls(self):
        for out in self:
            for key, val in self._h5Key2FileDict.items():
                if val == 'prtl':
                    getattr(out, key)

class TristanSim(PicSim):
    def __init__(self, dirpath=None, xtraStride = 1):
        super().__init__(dirpath, xtraStride, ['flds.tot.*', 'prtl.tot.*', 'spect.*', 'param.*'])
class TristanV2(PicSim):
    def __init__(self, dirpath=None, xtraStride = 1):
        super().__init__(dirpath, xtraStride, ['domain.*', 'flds.tot.*', 'spec.tot.*', 'prtl.tot.*'])


class ObjectMapper(object):
    '''A base object that holds the info of one type of particle in the simulation
    '''
    __h5Keys = []
    def __init__(self, sim, n=0):
        pass
    @classmethod
    def setKeys(cls, mapdict):
        cls.__h5Keys = [key for key in mapdict.keys()]
    @classmethod
    def mustHave(cls, name):
        return name in ['istep', 'stride', 'mi', 'me', 'c_omp', 'time', 'ppc0', 'qi', 'sigma', 'dens', 'xe']
    @classmethod
    def getKeys(cls):
        return cls.__h5Keys

class OutputPoint(ObjectMapper):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    def __init__(self, sim, n='001'):
        self._sim = sim
        self.__myKeys = []
        self.fnum = n
        for key, fname, h5KeyList in zip(sim._outputFileKey, sim._outputFileNames, sim._outputFileH5Keys):
            self.__myKeys.append(key)
            tmpStr = ''
            for elm in fname.split('.')[:-1]:
                tmpStr += elm +'.'
            tmpStr += n
            setattr(self, '_'+key, h5Wrapper(os.path.join(sim.dir, tmpStr), h5KeyList))

    def __getattribute__(self, name):
        if name in super().getKeys():
            return getattr(getattr(self,'_'+self._sim._h5Key2FileDict[name]), name)
        elif super().mustHave(name):
            if name == 'dens':
                return np.ones((25,25,25))
            if name == 'xe':
                return np.arange(10)
            return 1.0
        else:
            return object.__getattribute__(self, name)
    @cachedProperty
    def tagi(self):
        tmpTags = np.empty(len(self.indi), dtype = 'int64')
        tmpTags[:] = np.abs(self.indi).astype('int64')[:]
        tmpTags[:] += np.abs(self.proci).astype('int64')[:]*2147483648
        return tmpTags

    @cachedProperty
    def tage(self):
        tmpTags = np.empty(len(self.inde), dtype = 'int64')
        tmpTags[:] = np.abs(self.inde).astype('int64')[:]
        tmpTags[:] += np.abs(self.proce).astype('int64')[:]*2147483648
        return tmpTags

    def clear(self):
        for key in self.__myKeys:
            getattr(self, f'_{key}').clear()
        try:
            del self.tagi
        except AttributeError:
            pass
        try:
            del self.tage
        except AttributeError:
            pass

class h5Wrapper(object):
    def __init__(self, fname, h5Keys):
        self._fname = fname
        self.__h5Keys = h5Keys
        self.clear()

    def __getattribute__(self, name):
        if object.__getattribute__(self, name) is None:
            if name in self.__h5Keys:
                with h5py.File(self._fname, 'r') as f:
                    if np.sum([x for x in f[name].shape])!= 1:
                        setattr(self, name, f[name][:])
                    else:
                        setattr(self, name, f[name][0])
        return object.__getattribute__(self, name)

    def keys(self):
        return self.__h5Keys

    def clear(self):
        for key in self.__h5Keys:
            setattr(self, key, None)


class Particles(object):
    '''A base object that holds the info of one type of particle in the
    simulation
    '''
    __prtl_types = []
    def __init__(self, sim, name):
        self.sim = sim
        self.name = name
        self.__prtl_types.append(name)
        self.quantities = []
    def load_saved_quantities(self, key):
        try:
            with h5py.File(os.path.join(self.sim.dir,'prtl.tot.'+self.sim.n),'r') as f:
                return f[key][::self.sim.xtra_stride]
        except IOError:
            return np.array([])


    @classmethod
    def get_prtls(cls):
        return cls.__prtl_types

class Ions(Particles):
    '''The ion subclass'''
    _quantities = [
        'x',
        'y',
        'z',
        'px',
        'py',
        'pz',
        'gamma',
        'proc',
        'index',
        #'charge',
        'KE'
    ]
    _axislabels = [
        r'$x\ [c/\omega_{pe}]$',
        r'$y\ [c/\omega_{pe}]$',
        r'$z\ [c/\omega_{pe}]$',
        r'$\gamma_i\beta_{i,x}$',
        r'$\gamma_i\beta_{i,y}$',
        r'$\gamma_i\beta_{i,z}$',
        r'$\gamma_i$',
        r'$\mathrm{proc_i}$',
        r'$\mathrm{ind_i}$',
        #r'$q_i$',
        r'$\mathrm{KE}_i\ [m_i c^2]$'
    ]

    _oneDlabels = [
        r'$x\ [c/\omega_{pe}]$',
        r'$y\ [c/\omega_{pe}]$',
        r'$z\ [c/\omega_{pe}]$',
        r'$\gamma_i\beta_{i,x}$',
        r'$\gamma_i\beta_{i,y}$',
        r'$\gamma_i\beta_{i,z}$',
        r'$\gamma_i$',
        r'$\mathrm{proc_i}$',
        r'$\mathrm{ind_i}$',
        #r'$q_i$',
        r'$\mathrm{KE}_i\ [m_i c^2]$'
    ]

    _histLabel = r'$f_i (p)$'
    def __init__(self, sim, name='ions'):
        Particles.__init__(self, sim, name)

    @cached_property
    def x(self):
        return self.load_saved_quantities('x_2')/self.sim.comp

    @cached_property
    def y(self):
        return self.load_saved_quantities('y_2')/self.sim.comp

    @cached_property
    def z(self):
        return self.load_saved_quantities('z_2')/self.sim.comp

    @cached_property
    def px(self):
        return self.load_saved_quantities('u_2')

    @cached_property
    def py(self):
        return self.load_saved_quantities('v_2')

    @cached_property
    def pz(self):
        return self.load_saved_quantities('w_2')

    #@cached_property
    #def charge(self):
    #    return self.load_saved_quantities('chi')

    @cached_property
    def gamma(self):
        # an example of a calculated quantity
        #return self.load_saved_quantities('proci')
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cached_property
    def KE(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return (self.gamma-1)

    @cached_property
    def proc(self):
        return self.load_saved_quantities('proc_2')

    @cached_property
    def index(self):
        return self.load_saved_quantities('ind_2')

class Lecs(Particles):
    '''The electron subclass'''
    _quantities = [
        'x',
        'y',
        'z',
        'px',
        'py',
        'pz',
        'gamma',
        'proc',
        'index',
        #'charge',
        'KE'
    ]
    # YOU WRITE AS IF LaTeX BUT YOU MUST DOUBLE ESCAPE '\'  CHARACTER
    _axislabels = [
        r'$x\ [c/\omega_{pe}]$',
        r'$y\ [c/\omega_{pe}]$',
        r'$z\ [c/\omega_{pe}]$',
        r'$\gamma_e\beta_{e,x}$',
        r'$\gamma_e\beta_{e,y}$',
        r'$\gamma_e\beta_{e,z}$',
        r'$\gamma_e$',
        r'$\mathrm{proc_e}$',
        r'$\mathrm{ind_e}$',
        #r'$q_e$',
        r'$\mathrm{KE}_e\ [m_e c^2]$'
    ]

    _oneDlabels = [
        r'$x\ [c/\omega_{pe}]$',
        r'$y\ [c/\omega_{pe}]$',
        r'$z\ [c/\omega_{pe}]$',
        r'$\gamma_e\beta_{e,x}$',
        r'$\gamma_e\beta_{e,y}$',
        r'$\gamma_e\beta_{e,z}$',
        r'$\gamma_e$',
        r'$\mathrm{proc_e}$',
        r'$\mathrm{ind_e}$',
        #r'$q_e$',
        r'$\mathrm{KE}_e\ [m_i c^2]$'
    ]

    self.histLabel = 'f_e (p)'
    def __init__(self, sim, name='electrons'):
        Particles.__init__(self, sim, name)

    @cached_property
    def x(self):
        return self.load_saved_quantities('x_1')/self.sim.comp

    @cached_property
    def y(self):
        return self.load_saved_quantities('y_1')/self.sim.comp

    @cached_property
    def z(self):
        return self.load_saved_quantities('z_1')/self.sim.comp

    @cached_property
    def px(self):
        return self.load_saved_quantities('u_1')

    @cached_property
    def py(self):
        return self.load_saved_quantities('v_1')

    @cached_property
    def pz(self):
        return self.load_saved_quantities('w_1')

    #@cached_property
    #def charge(self):
    #   return self.load_saved_quantities('c')

    @cached_property
    def gamma(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return np.sqrt(self.px**2+self.py**2+self.pz**2+1)

    @cached_property
    def KE(self):
        # an example of a calculated quantity could use
        #return self.load_saved_quantities('proce')
        return (self.gamma-1)*self.params.me/self.sim.mi

    @cached_property
    def proc(self):
        return self.load_saved_quantities('proce')

    @cached_property
    def index(self):
        return self.load_saved_quantities('inde')


class TristanSim(object):
    '''A object that provides an API to access data from Tristan-mp
    particle-in-cell simulations. The specifics of your simulation should be
    defined as a class that extends this object.'''
    params = ['comp','bphi','btheta',]
    def __init__(self, dirpath = None, xtra_stride = 1):
        self.dir = str(dirpath)
        self.xtra_stride = xtra_stride
        # created RegEx for each of the output files
        self._outputFileNames =['domain.*', 'flds.tot.*', 'spec.tot.*', 'prtl.tot.*']

        self._outputFileKey = [key.split('.')[0:-1] for key in self._outputFileNames]
        self._outputFileRegEx = [re.compile(elm) for elm in self._outputFileNames]
        self._pathDict = {}
        visited = {}
        self.n=str(n).zfill(3)
        ### add the ions
        self.ions = Ions(self, name='ions') # NOTE: the name must match the attritube name
        # e.g. self.ions ===> name ='ions'
        ### add the electrons
        self.electrons = Electrons(self, name='electrons')


    def get_file_nums(self):
        try:
            # Create a dictionary of all the paths to the files
            hasStar = 0
            for key, regEx in zip(self._outputFileKey, self._outputFileRegEx):
                self._pathDict[key] = [item for item in filter(regEx.match, os.listdir(self.dir))]
                self._pathDict[key].sort()
                for i in range(len(self._pathDict[key])):
                    elm = self._pathDict[key][i]
                    try:
                        int(elm.split('.')[-1])
                     except ValueError:
                        if elm.split('.')[-1] == '***':
                            hasStar += 1
                        self._pathDict[key].remove(elm)
            ### GET THE NUMBERS THAT HAVE ALL SET OF FILES:
            allThere = set(elm.split('.')[-1] for elm in self._pathDict[self._outputFileKey[0]])
            for key in self._pathDict.keys():
                allThere &= set(elm.split('.')[-1] for elm in self._pathDict[key])
            allThere = list(sorted(allThere, key = lambda x: int(x)))
            if hasStar == len(self._pathDict.keys()):
                allThere.append('***')
            return allThere
            # create a bunch of regular expressions used to search for files
            f_re = re.compile('flds.tot.*')
            prtl_re = re.compile('prtl.tot.*')
            s_re = re.compile('spect.*')
            param_re = re.compile('param.*')

            # Create a dictionary of all the paths to the files
            self.PathDict = {'Flds': [], 'Prtl': [], 'Param': [], 'Spect': []}
            self.PathDict['Flds']= [item for item in filter(f_re.match, os.listdir(self.dir))]
            self.PathDict['Prtl']= [item for item in filter(prtl_re.match, os.listdir(self.dir))]
            self.PathDict['Spect']= [item for item in filter(s_re.match, os.listdir(self.dir))]
            self.PathDict['Param']= [item for item in filter(param_re.match, os.listdir(self.dir))]

            ### iterate through the Paths and just get the .nnn number
            for key in self.PathDict.keys():
                for i in range(len(self.PathDict[key])):
                    try:
                        self.PathDict[key][i] = int(self.PathDict[key][i].split('.')[-1])
                    except ValueError:
                        self.PathDict[key].pop(i)
                    except IndexError:
                        pass

            ### GET THE NUMBERS THAT HAVE ALL 4 FILES:
            allFour = set(self.PathDict['Param'])
            for key in self.PathDict.keys():
                allFour &= set(self.PathDict[key])
            allFour = sorted(allFour)
            return list(allFour)
        except OSError:
            return []
    def get_avail_prtls(self):
        prtl_obj = {}
        prtl_obj['prtls'] = {}
        for prtl in Particles.get_prtls():
            prtl_obj['prtls'][prtl]= {'quantities': getattr(getattr(self,prtl),'quantities'),
                             'axisLabels': getattr(getattr(self,prtl),'axislabels'),
                             'oneDLabels': getattr(getattr(self,prtl),'oneDlabels'),
                             'histLabel': getattr(getattr(self,prtl),'histLabel')}
        return prtl_obj
    def load_param(self, key):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f[key][0]
        except IOError:
            return np.nan

    # SOME SIMULATION WIDE PARAMETERS
    @cached_property
    def comp(self):
        return self.load_param('c_omp')

    @cached_property
    def bphi(self):
        return self.load_param('bphi')

    @cached_property
    def btheta(self):
        return self.load_param('btheta')

    @cached_property
    def sigma(self):
        return self.load_param('sigma')

    @cached_property
    def c(self):
        return self.load_param('c')

    @cached_property
    def delgam(self):
        return self.load_param('delgam')

    @cached_property
    def gamma0(self):
        return self.load_param('gamma0')

    @cached_property
    def istep(self):
        return self.load_param('istep')

    @cached_property
    def me(self):
        return self.load_param('me')

    @cached_property
    def mi(self):
        return self.load_param('mi')

    @cached_property
    def mx(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['mx'][:]
        except IOError:
            return np.array([])

    @cached_property
    def mx0(self):
        return self.load_param('mx0')

    @cached_property
    def my(self):
        try:
            with h5py.File(os.path.join(self.dir,'param.'+self.n),'r') as f:
                return f['my'][:]
        except IOError:
            return np.array([])

    @cached_property
    def my0(self):
        return self.load_param('my0')

    @cached_property
    def mz0(self):
        return self.load_param('mz0')

    @cached_property
    def ntimes(self):
        return self.load_param('ntimes')

    @cached_property
    def ppc0(self):
        return self.load_param('ppc0')

    @cached_property
    def qi(self):
        return self.load_param('qi')

    @cached_property
    def sizex(self):
        return self.load_param('sizex')
    @cached_property
    def sizey(self):
        return self.load_param('sizey')

    @cached_property
    def stride(self):
        return self.load_param('stride')

    @cached_property
    def time(self):
        return self.load_param('time')

    @cached_property
    def walloc(self):
        return self.load_param('walloc')

    @cached_property
    def xinject2(self):
        return self.load_param('xinject2')
"""

if __name__=='__main__':
    print(n_to_fnum('output/',5))
