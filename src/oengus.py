import os,sys, subprocess, yaml, time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as cm
import new_cmaps
import numpy as np
from collections import deque
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from scalar_flds_plot import scalarFldsPlot
#from spectra_panel import SpectralPanel
#from mag_panel import BPanel
#from energy_panel import EnergyPanel
#from fft_panel import FFTPanel
#from total_energy_panel import TotEnergyPanel
#from moments_panel import MomentsPanel

from PIL import Image

class Oengus():
    """ We simply derive a new class of Frame as the man frame of our app"""
    def __init__(self, preset_view='Default', interactive = True, tkApp = None):
        self.IseultDir = os.path.join(os.path.dirname(__file__), '..')
        self.sim_name = ''
        self.dirname = ''
        self.tkApp = tkApp
        self.interactive = interactive
        #self.dirname = sim.dir
        try:
            with open(os.path.join(self.IseultDir, '.iseult_configs', preset_view.strip().replace(' ', '_') +'.yml')) as f:
                self.cfgDict = yaml.safe_load(f)
        except:
            print('Cannot find/load ' +  preset_view.strip().replace(' ', '_') +'.yml in .iseult_configs. If the name of view contains whitespace,')
            print('either it must be enclosed in quotation marks or given with whitespace replaced by _.')
            print('Name is case sensitive. Reverting to Default view')
            with open(os.path.join(self.IseultDir, '.iseult_configs', 'Default.yml')) as f:
                self.cfgDict = yaml.safe_load(f)
        self.GenMainParamDict()

        # Clear the figure then add stuff back in
        self.figure = plt.figure(figsize = self.MainParamDict['FigSize'], dpi = self.MainParamDict['dpi'], edgecolor = 'none', facecolor = 'w')

        if self.MainParamDict['HorizontalCbars']:
            self.axes_extent = self.MainParamDict['HAxesExtent']
            self.cbar_extent = self.MainParamDict['HCbarExtent']
            self.SubPlotParams = self.MainParamDict['HSubPlotParams']

        else:
            self.axes_extent = self.MainParamDict['VAxesExtent']
            self.cbar_extent = self.MainParamDict['VCbarExtent']
            self.SubPlotParams = self.MainParamDict['VSubPlotParams']
        self.figure.subplots_adjust( **self.SubPlotParams)
        if self.interactive:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.canvas = FigureCanvasTkAgg(self.figure, master = self.tkApp)
        else:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            self.canvas = FigureCanvasAgg(self.figure)


        # Make the object hold the timestep info
        # Some options to set the way the spectral lines are dashed
        self.spect_plot_counter = 0
        self.dashes_options = [[],[3,1],[5,1],[1,1]]

        # divy up the figure into a bunch of subplots using GridSpec.
        self.gs0 = gridspec.GridSpec(self.MainParamDict['NumOfRows'],self.MainParamDict['NumOfCols'])

        # Create the list of all of subplot wrappers
        self.SubPlotList = [[] for i in range(self.MainParamDict['MaxRows'])]
        self.showingCPUs = False
        self.showingTotEnergy = False
        PlotTypeDict = {
            'ScalarFlds': scalarFldsPlot,
            #'EnergyPlot': EnergyPanel,
            #'FieldsPlot': FieldsPanel,
            #'DensityPlot': DensPanel,
            #'SpectraPlot': SpectralPanel,
            #'MagPlots': BPanel,
            #'FFTPlots': FFTPanel,
            #'TotalEnergyPlot': TotEnergyPanel,
            #'Moments': MomentsPanel
        }
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                tmp_str = f"Chart{i}_{j}"
                if tmp_str in self.cfgDict.keys():
                    tmpchart_type = self.cfgDict[tmp_str]['ChartType']
                    self.SubPlotList[i].append(PlotTypeDict[tmpchart_type](self, (i,j), self.cfgDict[tmp_str]))
                    self.showingTotEnergy += tmpchart_type == 'TotalEnergyPlot'
                    try:
                        self.showingCPUs += self.cfgDict[tmp_str]['show_cpu_domains']
                    except KeyError:
                        pass
                else:
                    # The graph isn't specified in the config file, just set it equal to phase plots
                    self.SubPlotList[i].append(PlotTypeDict['ScalarFlds'](self, (i,j), {}))



        ##
        #
        # Open TristanSim
        #
        ##


        # previous objects
        #if self.showingTotEnergy:
        #    self.calc_total_energy()


        #self.create_graphs()
    def open_sim(self, sim):
        self.sim = sim
    def GenMainParamDict(self, config_file = None):
        ''' The function that reads in a config file and then makes MainParamDict to hold all of the main iseult parameters.
            It also sets all of the plots parameters.'''

        #config = configparser.RawConfigParser()



        # Since configparser reads in strings we have to format the data.
        # First create MainParamDict with the default parameters,
        # the dictionary that will hold the parameters for the program.
        # See ./iseult_configs/Default.cfg for a description of what each parameter does.
        self.MainParamDict = {'zSlice': 0.0, # THIS IS A float WHICH IS THE RELATIVE POSITION OF THE 2D SLICE 0->1
                              '2DSlicePlane': 0, # 0 = x-y plane, 1 == x-z plane
                              'Average1D': 0,
                              'ySlice': 0.5, # THIS IS A FLOAT WHICH IS THE RELATIVE POSITION OF THE 1D SLICE 0->1
                              'WindowSize': '1200x700',
                              'yTop': 100.0,
                              'yBottom': 0.0,
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
                              'FFTRelative': True,
                              'NumOfCols': 2,
                              'VSubPlotParams': {'right': 0.95,
                                                 'bottom': 0.06,
                                                 'top': 0.93,
                                                 'wspace': 0.23,
                                                 'hspace': 0.15,
                                                 'left': 0.06},
                              'HAxesExtent': [18, 92, 0, -1],
                              'SetyLim': False,
                              'HSubPlotParams': {'right': 0.95,
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
                              'Recording': False,
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
                              'legendLabelSize':11}
        for key, val in self.cfgDict['MainParamDict'].items():
            self.MainParamDict[key] = val
        self.electron_color = self.MainParamDict['electron_color']
        self.ion_color = self.MainParamDict['ion_color']
        self.shock_color = self.MainParamDict['shock_color']
        self.ion_fit_color = self.MainParamDict['ion_fit_color']
        self.electron_fit_color = self.MainParamDict['electron_fit_color']
        self.FFT_color = self.MainParamDict['FFT_color']


    #def calc_total_energy(self):
    #    self.TotalEnergyTimes = []
    #    self.TotalElectronEnergy = []
    #    self.TotalIonEnergy = []#
    #    self.TotalMagEnergy = []
    #    self.TotalElectricEnergy =[]
    #    self.TotalBzEnergy = []
    #    for o in self.sim:
    #        self.TotalEnergyTimes.append(o.time)
    #        self.TotalElectronEnergy.append(np.sum(np.sqrt(o.ue*o.ue + o.ve*o.ve + o.we*o.we +1)-1)*o.stride*abs(o.qi)*o.c**2)
    #        self.TotalIonEnergy.append(np.sum(np.sqrt(o.ui*o.ui + o.vi*o.vi + o.wi*o.wi +1)-1)*o.stride*abs(o.qi)*o.mi/o.me*o.c**2)
    #        self.TotalMagEnergy.append(np.sum(o.bz*o.bz+o.bx*o.bx+o.by*o.by)*o.istep**2*.5)
    #        self.TotalElectricEnergy.append(np.sum(o.ez*o.ez+o.ex*o.ex+o.ey*o.ey)*o.istep**2*.5)
    #        self.TotalBzEnergy.append(np.sum(o.bz*o.bz)*o.istep**2*.5)
    #        o.clear()
    #    self.TotalElectronEnergy = np.array(self.TotalElectronEnergy)
    #    self.TotalIonEnergy = np.array(self.TotalIonEnergy)
    #    self.TotalMagEnergy = np.array(self.TotalMagEnergy)
    #    self.TotalElectricEnergy = np.array(self.TotalElectricEnergy)
    #    self.TotalBzEnergy = np.array(self.TotalBzEnergy)

    def create_graphs(self):
        # FIND THE SLICE
        #self.MaxZInd = o.bx.shape[0]-1
        #self.MaxYInd = o.bx.shape[1]-1
        #self.MaxXInd = o.bx.shape[2]-1

        #self.ySlice = int(np.around(self.MainParamDict['ySlice']*self.MaxYInd))
        #self.zSlice = int(np.around(self.MainParamDict['zSlice']*self.MaxZInd))

        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                self.SubPlotList[i][j].draw(self.sim, -1)
        if self.showingCPUs:
            if 'my' in self.sim._h5Key2FileDict.keys():
                cpu_y_locs = np.cumsum(o.my-5)/o.c_omp
            else:
                tmpSize = ((self.MaxYInd+1)*o.istep)//(o.my0-5)
                cpu_y_locs = np.cumsum(np.ones(tmpSize)*(o.my0)-5)/o.c_omp
            if 'mx' in self.sim._h5Key2FileDict.keys():
                cpu_x_locs = np.cumsum(o.mx-5)/o.c_omp
            else:
                tmpSize = ((self.MaxXInd+1)*o.istep)//(o.mx0-5)
                cpu_x_locs = np.cumsum(np.ones(tmpSize)*(o.mx0)-5)/o.c_omp


            for i in range(self.MainParamDict['NumOfRows']):
                for j in range(self.MainParamDict['NumOfCols']):
                    try:
                        if self.SubPlotList[i][j].param_dict['show_cpu_domains']:
                            for k in range(len(self.parent.cpu_x_locs)):
                                self.SubPlotList[i][j].axes.axvline(cpu_x_locs[k], linewidth = 1, linestyle = ':',color = 'w')
                            for k in range(len(self.parent.cpu_y_locs)):
                                self.SubPlotList[i][j].axes.axvline(cpu_y_locs[k], linewidth = 1, linestyle = ':',color = 'w')

                    except KeyError:
                        pass

        #if self.MainParamDict['ShowTitle']:
        #    if len(self.sim_name) == 0:
        #        self.figure.suptitle(os.path.abspath(self.dirname)+ '/*.'+o.fnum+' at time t = %d $\omega_{pe}^{-1}$'  % round(o.time), size = 15)
        #    else:
        #        self.figure.suptitle(self.sim_name +', t = %d $\omega_{pe}^{-1}$'  % round(o.time), size = 15)
        ####
        #
        # Write the lines to the phase plots
        #
        ####

        # first find all the phase plots that need writing to
        self.phase_plot_list = []
        self.spectral_plot_list = []

        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                if self.SubPlotList[i][j].chartType =='PhasePlot' or self.SubPlotList[i][j].chartType =='EnergyPlot':
                    if self.SubPlotList[i][j].GetPlotParam('show_int_region'):
                        self.phase_plot_list.append([i,j])
                if self.SubPlotList[i][j].chartType =='SpectraPlot':
                    self.spectral_plot_list.append([i,j])

        for pos in self.phase_plot_list:
            if self.SubPlotList[pos[0]][pos[1]].GetPlotParam('prtl_type') == 0:
                for spos in self.spectral_plot_list:
                    if self.SubPlotList[spos[0]][spos[1]].GetPlotParam('show_ions'):
                        k = min(self.SubPlotList[spos[0]][spos[1]].spect_num, len(self.dashes_options)-1)
                        # Append the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].axes.axvline(
                        max(self.SubPlotList[spos[0]][spos[1]].i_left_loc, self.SubPlotList[pos[0]][pos[1]].xmin+1),
                        linewidth = 1.5, linestyle = '-', color = self.ion_color))
                        # Choose the left dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines[-1].set_dashes(self.dashes_options[k])

                        # Append the right line to the list
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].axes.axvline(
                        min(self.SubPlotList[spos[0]][spos[1]].i_right_loc, self.SubPlotList[pos[0]][pos[1]].xmax+1),
                        linewidth = 1.5, linestyle = '-', color = self.ion_color))
                        # Choose the right dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines[-1].set_dashes(self.dashes_options[k])
            else:
                for spos in self.spectral_plot_list:
                    if self.SubPlotList[spos[0]][spos[1]].GetPlotParam('show_electrons'):
                        k = min(self.SubPlotList[spos[0]][spos[1]].spect_num, len(self.dashes_options)-1)
                        # Append the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].axes.axvline(
                        max(self.SubPlotList[spos[0]][spos[1]].e_left_loc, self.SubPlotList[pos[0]][pos[1]].xmin+1),
                        linewidth = 1.5, linestyle = '-', color = self.electron_color))
                        # Choose the left dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines[-1].set_dashes(self.dashes_options[k])

                        # Append the right line to the list
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].axes.axvline(
                        min(self.SubPlotList[spos[0]][spos[1]].e_right_loc, self.SubPlotList[pos[0]][pos[1]].xmax+1),
                        linewidth = 1.5, linestyle = '-', color = self.electron_color))
                        # Choose the right dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].IntRegionLines[-1].set_dashes(self.dashes_options[k])
        #self.canvas.draw()

    def draw_output(self, n):
        #for i in range(self.MainParamDict['NumOfRows']):
        #    for j in range(self.MainParamDict['NumOfCols']):
        #        self.SubPlotList[i][j].update_data(o)

        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                self.SubPlotList[i][j].refresh(self.sim, n)
        #if self.showingCPUs:
        #    if 'my' in self.sim._h5Key2FileDict.keys():
        #        cpu_y_locs = np.cumsum(o.my-5)/o.c_omp
        #    else:
        #        tmpSize = ((self.MaxYInd+1)*o.istep)//(o.my0-5)
        #        cpu_y_locs = np.cumsum(np.ones(tmpSize)*(o.my0)-5)/o.c_omp
        #    if 'mx' in self.sim._h5Key2FileDict.keys():
        #        cpu_x_locs = np.cumsum(o.mx-5)/o.c_omp
        #    else:
        #        tmpSize = ((self.MaxXInd+1)*o.istep)//(o.mx0-5)
        #        cpu_x_locs = np.cumsum(np.ones(tmpSize)*(o.mx0)-5)/o.c_omp


        #    for i in range(self.MainParamDict['NumOfRows']):
        #        for j in range(self.MainParamDict['NumOfCols']):
        #            try:
        #                if self.SubPlotList[i][j].param_dict['show_cpu_domains']:
        #                    for k in range(len(self.parent.cpu_x_locs)):
        #                        self.SubPlotList[i][j].axes.axvline(cpu_x_locs[k], linewidth = 1, linestyle = ':',color = 'w')
        #                    for k in range(len(self.parent.cpu_y_locs)):
        #                        self.SubPlotList[i][j].axes.axvline(cpu_y_locs[k], linewidth = 1, linestyle = ':',color = 'w')

        #            except KeyError:
        #                pass

        #if self.MainParamDict['ShowTitle']:
        #    if len(self.sim_name) == 0:
        #        self.figure.suptitle(os.path.abspath(self.dirname)+ '/*.'+o.fnum+' at time t = %d $\omega_{pe}^{-1}$'  % round(o.time), size = 15)
        #    else:
        #        self.figure.suptitle(self.sim_name +', t = %d $\omega_{pe}^{-1}$'  % round(o.time), size = 15)
        ####
        #
        # Write the lines to the phase plots
        #
        ####

        # first find all the phase plots that need writing to
        #self.phase_plot_list = []
        #self.spectral_plot_list = []
        """
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                if self.SubPlotList[i][j].chartType =='PhasePlot' or self.SubPlotList[i][j].chartType =='EnergyPlot':
                    if self.SubPlotList[i][j].GetPlotParam('show_int_region'):
                        self.phase_plot_list.append([i,j])
                if self.SubPlotList[i][j].chartType =='SpectraPlot':
                    self.spectral_plot_list.append([i,j])

        for pos in self.phase_plot_list:
            if self.SubPlotList[pos[0]][pos[1]].GetPlotParam('prtl_type') == 0:
                for spos in self.spectral_plot_list:
                    if self.SubPlotList[spos[0]][spos[1]].GetPlotParam('show_ions'):
                        # Update the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[i].set_xdata(
                        [max(self.SubPlotList[spos[0]][spos[1]].graph.i_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin+1),
                        max(self.SubPlotList[spos[0]][spos[1]].graph.i_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin+1)])
                        i+=1
                        # Append the right line of the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[i].set_xdata(
                        [min(self.SubPlotList[spos[0]][spos[1]].graph.i_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax-1),
                        min(self.SubPlotList[spos[0]][spos[1]].graph.i_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax-1)])
                        i+=1
            else:
                for spos in self.spectral_plot_list:
                    if self.SubPlotList[spos[0]][spos[1]].GetPlotParam('show_electrons'):

                        # Update the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[i].set_xdata(
                        [max(self.SubPlotList[spos[0]][spos[1]].graph.e_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin+1),
                        max(self.SubPlotList[spos[0]][spos[1]].graph.e_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin-1)])
                        i+=1
                        # Update the right line of the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[i].set_xdata(
                        [min(self.SubPlotList[spos[0]][spos[1]].graph.e_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax+1),
                        min(self.SubPlotList[spos[0]][spos[1]].graph.e_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax-1)])
                        i+=1
        """
        self.canvas.draw()
        if not self.interactive:
            s, (width, height) = self.canvas.print_to_buffer()
            return Image.frombytes('RGBA', (width, height), s)
def runMe(cmd_args):
    tic = time.time()
    cmdout = ['ffmpeg',
                '-y', '-f', 'image2pipe', # overwrite, image2 is a colorspace thing.
                '-framerate', str(int(cmd_args.framerate)), # Set framerate to the the user selected option
                 '-pattern_type', 'glob', '-i', '-', # Not sure what this does... I am going to get rid of it
                 '-codec', 'copy',  # save as a *.mov
                 cmd_args.outmovie]#, '&']#, # output name,

    pipe = subprocess.Popen(cmdout, stdin=subprocess.PIPE)
    sims = []
    iseult_figs = []
    iseultDir = os.path.join(os.path.dirname(__file__), '..')
    try:
        with open(os.path.join(iseultDir, '.iseult_configs', cmd_args.p.strip().replace(' ', '_') +'.yml')) as f:
            cfgDict = yaml.safe_load(f)
    except:
        print('Cannot find/load ' +  preset_view.strip().replace(' ', '_') +'.yml in .iseult_configs. If the name of view contains whitespace,')
        print('either it must be enclosed in quotation marks or given with whitespace replaced by _.')
        print('Name is case sensitive. Reverting to Default view')
        with open(os.path.join(iseultDir, '.iseult_configs', 'Default.yml')) as f:
            cfgDict = yaml.safe_load(f)


    for i in range(len(cmd_args.O)):
        dirname= os.curdir
        dirlist = os.listdir(dirname)
        if len(cmd_args.O[i])>0:
            dirname = os.path.join(dirname, cmd_args.O[i])
        elif 'output' in dirlist:
            dirname = os.path.join(dirname, 'output')
        curname = ''
        if i<len(cmd_args.name):
            curname = cmd_args.name[i]
        curSim = TristanSim(dirname, xtraStride = cfgDict['MainParamDict']['PrtlStride'])

        cntxt = {'preset_view':cmd_args.p,
            'sim': curSim,
            'name':curname
            }
        sims.append(curSim)
        iseult_figs.append(Oengus(**cntxt))
    for s in sims:
        s.tlist = np.array([o.time for o in s])
    tSteps= []
    for s in sims:
        if len(tSteps) < len(s.tlist):
            # list(s.tlist) instead of s.tlist here is to force a deep copy. quirk of python.
            tSteps = list(s.tlist)


    for t in tSteps:
        imgs = []
        for s, ifig in zip(sims, iseult_figs):
            n = np.where(np.min(np.abs(s.tlist-t)) == np.abs(s.tlist-t))[0][0]
            imgs.append(ifig.draw_output(n))

        imgs_comb = np.vstack(list(np.asarray(i) for i in imgs))

        # save that beautiful picture
        imgs_comb = Image.fromarray(imgs_comb)
        imgs_comb.save(pipe.stdin, 'PNG')
        print(f"saving image {n} to pipe")
    pipe.stdin.close()
    pipe.wait()

    # Make sure all went well
    if pipe.returncode != 0:
        raise sp.CalledProcessError(pipe.returncode, cmd_out)
