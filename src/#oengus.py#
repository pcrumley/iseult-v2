import os
import sys
import yaml
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image
from pic_sim import picSim
import new_cmaps
from scalar_flds_plot import scalarFldsPlot
from vector_flds_plot import vectorFldsPlot
from phase_plot import phasePlot


class Oengus():
    """ We simply derive a new class of Frame as the man frame of our app"""
    def __init__(self, preset_view='Default', interactive=True, tkApp=None):
        self.IseultDir = os.path.join(os.path.dirname(__file__), '..')
        self.sim_name = ''
        self.sims = [picSim(name='sim0')]
        self.cur_sim = 0  # the curent sim on the playback bar
        self.sim_names = [sim.name for sim in self.sims]
        self.sims_shown = []
        self.dirname = ''

        self.interactive = interactive
        # Create the figure
        self.figure = plt.figure(edgecolor='none', facecolor='w')
        if self.interactive:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.canvas = FigureCanvasTkAgg(self.figure, master=tkApp)
        else:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            self.canvas = FigureCanvasAgg(self.figure)
        self.load_view(preset_view)

    def GenMainParamDict(self):
        ''' The function that reads in a config file and then makes
            MainParamDict to hold all of the main iseult parameters.
            It also sets all of the plots parameters.'''

        # Since configparser reads in strings we have to format the data.
        # First create MainParamDict with the default parameters,
        # the dictionary that will hold the parameters for the program.
        # See ./iseult_configs/Default.cfg for a description of what each
        # parameter does.

        self.MainParamDict = {
            'zSlice': 0.0,  # THE RELATIVE POSITION OF THE SLICE 0.0 -> 1.0
            '2DSlicePlane': 0,  # 0 = x-y plane, 1 == x-z plane
            'NumberOfSims': 2,
            'Average1D': 0,
            'ySlice': 0.5,  # THE RELATIVE POSITION OF THE SLICE 0.0->1.0
            'WindowSize': '1200x700',
            'yTop': 100.0,
            'yBottom': 0.0,
            'LinkTime': True,
            'TimeUnits': None,
            'Reload2End': True,
            'ColorMap': 'viridis',
            'FFTLeft': 0.0,
            'ShowTitle': True,
            'ImageAspect': 0,
            'WaitTime': 0.01,
            'MaxCols': 8,
            'VAxesExtent': [4, 90, 0, 92],
            'kRight': 1.0,
            'DoLorentzBoost': False,
            'NumOfRows': 3,
            'MaxRows': 8,
            'SetkLim': False,
            'VCbarExtent': [4, 90, 94, 97],
            'SkipSize': 5,
            'xLeft': 0.0,
            'NumFontSize': 11,
            'AxLabelSize': 11,
            'TitleFontSize': 15,
            'FFTRelative': True,
            'NumOfCols': 2,
            'VSubPlotParams': {
                'right': 0.95,
                'bottom': 0.06,
                'top': 0.93,
                'wspace': 0.23,
                'hspace': 0.15,
                'left': 0.06},
            'HAxesExtent': [18, 92, 0, -1],
            'SetyLim': False,
            'cmaps_with_green': [
                'viridis',
                'Rainbow + White',
                'Blue/Green/Red/Yellow',
                'Cube YF',
                'Linear_L'],
            'HSubPlotParams': {
                'right': 0.95,
                'bottom': 0.06,
                'top': 0.91,
                'wspace': 0.15,
                'hspace': 0.3,
                'left': 0.06},
            'yLabelPad': 0,
            'cbarLabelPad': 15,
            'SetxLim': False,
            'xLimsRelative': False,
            'ConstantShockVel': True,
            'xRight': 100.0,
            'LinkSpatial': 2,
            'HCbarExtent': [0, 4, 0, -1],
            # 'Recording': False,
            'xLabelPad': 0,
            'annotateTextSize': 18,
            'FFTRight': 200.0,
            'ClearFig': True,
            'HorizontalCbars': False,
            'DivColorMap': 'BuYlRd',
            'LinkK': True,
            'GammaBoost': 0.0,
            'kLeft': 0.1,
            'LoopPlayback': True,
            'PrtlStride': 5,
            'electron_color': '#fca636',
            'electron_fit_color': 'yellow',
            'ion_color': '#d6556d',
            'ion_fit_color': 'r',
            'shock_color': 'w',
            'FigSize':  [12.0, 6.22],
            'dpi': 100,
            'FFT_color': 'k',
            'legendLabelSize': 11}
        for key, val in self.cfgDict['MainParamDict'].items():
            self.MainParamDict[key] = val
        self.electron_color = self.MainParamDict['electron_color']
        self.ion_color = self.MainParamDict['ion_color']
        self.shock_color = self.MainParamDict['shock_color']
        self.ion_fit_color = self.MainParamDict['ion_fit_color']
        self.electron_fit_color = self.MainParamDict['electron_fit_color']
        self.FFT_color = self.MainParamDict['FFT_color']
        self.MainParamDict['NumberOfSims'] = max(
            1, self.MainParamDict['NumberOfSims'])

        # Loading a config file may change the stride... watch out!
        for sim in self.sims:
            if sim.xtra_stride != self.MainParamDict['PrtlStride']:
                sim.xtra_stride = self.MainParamDict['PrtlStride']

        # Loading a config file may change the number of sims
        if self.MainParamDict['NumberOfSims'] != len(self.sims):
            tmp_num = self.MainParamDict['NumberOfSims']
            while tmp_num > len(self.sims):
                self.add_sim(f'sim{len(self.sims)}')
            while tmp_num < len(self.sims):
                self.pop_sim()

    def calc_slices(self, ax, sim, n):
        # FIND THE SLICE
        attr, param = 'x', 'xSlice'
        if ax == 'y':
            attr, param = 'y', 'ySlice'

        elif ax == 'z':
            attr, param = 'z', 'zSlice'

        maxInd = len(
            sim.get_data(
                n, data_class='axes',
                attribute=attr)['data']
            ) - 1

        slice = int(
            np.around(
                self.MainParamDict[param]*maxInd))

        return slice

    def load_view(self, view_name):
        self.figure.clf()
        view_file = view_name.strip().replace(' ', '_') + '.yml'
        view_file = os.path.join(self.IseultDir, '.iseult_configs', view_file)
        if os.path.exists(view_file) and os.path.isfile(view_file):
            with open(view_file) as f:
                self.cfgDict = yaml.safe_load(f)
        else:
            print(
                'Cannot find/load ' + preset_view.strip().replace(' ', '_') +
                '.yml in .iseult_configs.' +
                ' If the name of view contains whitespace,')
            print(
                'either it must be enclosed in quotation marks' +
                "or given with whitespace replaced with '_'.")
            print('Name is case sensitive.')
            print('Reverting to Default view')

            default_file = os.path.join('.iseult_configs', 'Default.yml')
            with open(os.path.join(self.IseultDir, default_file)) as f:
                self.cfgDict = yaml.safe_load(f)
        self.GenMainParamDict()
        self.figure.dpi = self.MainParamDict['dpi']
        self.figure.figsize = self.MainParamDict['FigSize']

        if self.MainParamDict['HorizontalCbars']:
            self.axes_extent = self.MainParamDict['HAxesExtent']
            self.cbar_extent = self.MainParamDict['HCbarExtent']
            self.SubPlotParams = self.MainParamDict['HSubPlotParams']

        else:
            self.axes_extent = self.MainParamDict['VAxesExtent']
            self.cbar_extent = self.MainParamDict['VCbarExtent']
            self.SubPlotParams = self.MainParamDict['VSubPlotParams']
        self.figure.subplots_adjust(**self.SubPlotParams)

        # Make the object hold the timestep info
        # Some options to set the way the spectral lines are dashed
        self.spect_plot_counter = 0
        self.dashes_options = [[], [3, 1], [5, 1], [1, 1]]

        # Create the list of all of subplot wrappers
        self.SubPlotList = [[] for i in range(self.MainParamDict['MaxRows'])]
        self.showingCPUs = False
        self.showingTotEnergy = False
        self.plot_types_dict = {
            'ScalarFlds': scalarFldsPlot,
            'VectorFlds': vectorFldsPlot,
            'PhasePlot': phasePlot
            # 'FieldsPlot': FieldsPanel,
            # 'DensityPlot': DensPanel,
            # 'SpectraPlot': SpectralPanel,
            # 'MagPlots': BPanel,
            # 'FFTPlots': FFTPanel,
            # 'TotalEnergyPlot': TotEnergyPanel,
            # 'Moments': MomentsPanel
        }
        for i in range(self.MainParamDict['MaxRows']):
            for j in range(self.MainParamDict['MaxCols']):
                tmp_str = f"Chart{i}_{j}"
                if tmp_str in self.cfgDict.keys():
                    tmpchart_type = self.cfgDict[tmp_str]['chart_type']
                    self.SubPlotList[i].append(
                        self.plot_types_dict[tmpchart_type](
                            self, (i, j), self.cfgDict[tmp_str]))
                    self.showingTotEnergy += tmpchart_type == 'TotalEnergyPlot'
                    try:
                        show_cpus = self.cfgDict[tmp_str]['show_cpu_domains']
                        self.showingCPUs += show_cpus
                    except KeyError:
                        pass
                else:
                    # The graph isn't specified in the config file,
                    # just set it equal to scalar field plots
                    self.SubPlotList[i].append(
                        self.plot_types_dict['ScalarFlds'](self, (i, j), {}))

        self.calc_sims_shown()

    def calc_sims_shown(self):
        self.sims_shown = []
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                sim_num = self.SubPlotList[i][j].param_dict['sim_num']
                if sim_num not in self.sims_shown:
                    self.sims_shown.append(sim_num)
        self.sims_shown.sort()

    def add_sim(self, name):
        self.sims.append(picSim(name=name))
        self.sim_names.append(self.sims[-1].name)
        self.sims[-1].xtra_stride = self.MainParamDict['PrtlStride']
        if self.MainParamDict['LinkTime']:
            unit = self.MainParamDict['TimeUnits']
            cur_t = self.sims[self.cur_sim].get_time(units=unit)
            self.sims[-1].set_time(cur_t, units=unit)
        self.MainParamDict['NumberOfSims'] += 1

    def pop_sim(self):
        if len(self.sims) > 1:
            self.sims.pop(-1)
            self.sim_names.pop(-1)
            self.MainParamDict['NumberOfSims'] -= 1

    def create_graphs(self):
        # divy up the figure into a bunch of subplots using GridSpec.
        self.gs0 = gridspec.GridSpec(
            self.MainParamDict['NumOfRows'],
            self.MainParamDict['NumOfCols'])

        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                self.SubPlotList[i][j].draw()  # self.sim, -1)

        if self.MainParamDict['ShowTitle']:
            sim = self.sims[0]
            outname = os.path.abspath(sim.outdir)
            try:
                f_end = sim.file_list[sim.get_time()]
                self.figure.suptitle(
                    f'{outname}/*.{f_end}',
                    size=self.MainParamDict['TitleFontSize'])
            except IndexError:
                self.figure.suptitle(
                    f'{outname} is empty',
                    size=self.MainParamDict['TitleFontSize'])

    def draw_output(self):
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                self.SubPlotList[i][j].refresh()

        if self.MainParamDict['ShowTitle']:
            sim = self.sims[0]
            outname = os.path.abspath(sim.outdir)
            try:
                f_end = sim.file_list[sim.get_time()]
                self.figure.suptitle(f'{outname}/*.{f_end}')
            except IndexError:
                self.figure.suptitle(f'{outname} is empty')

        self.canvas.draw()
        if not self.interactive:
            s, (width, height) = self.canvas.print_to_buffer()
            return Image.frombytes('RGBA', (width, height), s)

    def make_movie(self, fname, start, stop, step, FPS, outdir):
        '''Record a movie'''
        # First find the last frame is stop is -1:
        if stop == -1:
            stop = len(self.sims[self.cur_sim])

        # Now build all the frames we have to visit
        frame_arr = np.arange(start, stop, step)
        if frame_arr[-1] != stop:
            frame_arr = np.append(frame_arr, stop)

        # If total energy plot is showing, we have to
        # loop through everything twice.

        # if self.showing_total_energy_plt:
        #    for k in frame_arr:
        #        self.TimeStep.set(k)

        cmdstring = [
            'ffmpeg',
            # Set framerate to the the user selected option
            '-framerate', str(int(FPS)),
            '-pattern_type', 'glob',
            '-i', '-',
            '-c:v',
            'prores',
            '-pix_fmt',
            'yuv444p10le',
            os.path.join(os.path.join(outdir), fname)
        ]
        pipe = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)
        print(frame_arr)
        for i in frame_arr:

            self.sims[self.cur_sim].set_time(i-1, units=None)
            if self.MainParamDict['LinkTime']:
                unit = self.MainParamDict['TimeUnits']
                cur_t = self.sims[self.cur_sim].get_time(units=None)
                print(cur_t)
                for sim_num in self.sims_shown:
                    self.sims[sim_num].set_time(cur_t, units=None)
            self.draw_output()
            # if self.interactive:
            #    self.canvas.get_tk_widget().update_idletasks()

            s, (width, height) = self.canvas.print_to_buffer()
            im = Image.frombytes('RGBA', (width, height), s)
            # The ffmpeg command we want to call.
            # ffmpeg -framerate [FPS] -i [NAME_***].png -c:v prores -pix_fmt
            # yuv444p10le [OUTPUTNAME].mov
            im.save(pipe.stdin, 'PNG')
            print(f"saving image {i} to pipe")
        pipe.stdin.close()
        pipe.wait()

        # Make sure all went well
        if pipe.returncode != 0:
            raise subprocess.CalledProcessError(pipe.returncode, cmdstring)
