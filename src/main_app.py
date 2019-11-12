#! /usr/bin/env python
import time, string, io
from PIL import Image
import matplotlib
import new_cmaps
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
    from movie_dialog import MovieDialog
from moments import MomentsPanel
from functools import partial
import subprocess, yaml
from oengus import Oengus
from pic_sim import picSim
import tkinter as Tk
from tkinter import ttk, filedialog, messagebox

matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
matplotlib.rcParams['image.resample'] = False
matplotlib.rcParams['image.origin'] = 'upper'

import argparse

def destroy(e):
    sys.exit()

class MyCustomToolbar(NavigationToolbar2Tk):
    def __init__(self, plotCanvas, parent):
        # create the default toolbar
        # plotCanvas is the tk Canvas we want to link to the toolbar,
        # parent is the iseult main app
        NavigationToolbar2Tk.__init__(self, plotCanvas, parent)
        #print(self._nav_stack)
        self.parent = parent

class Spinbox(ttk.Entry):
    def __init__(self, master=None, **kw):
        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)

    def current(self, newindex=None):
        return self.tk.call(self._w, 'current', index)

    def set(self, value):
        return self.tk.call(self._w, 'set', value)


class Knob:
    """
    ---- Taken from the Matplotlib gallery
    Knob - simple class with a "setKnob" method.
    A Knob instance is attached to a Param instance, e.g., param.attach(knob)
    Base class is for documentation purposes.
    """
    def setKnob(self, value):
        pass

class Param:
    """
    ---- Taken from the Matplotlib gallery
    The idea of the "Param" class is that some parameter in the GUI may have
    several knobs that both control it and reflect the parameter's state, e.g.
    a slider, text, and dragging can all change the value of the frequency in
    the waveform of this example.
    The class allows a cleaner way to update/"feedback" to the other knobs when
    one is being changed.  Also, this class handles min/max constraints for all
    the knobs.
    Idea - knob list - in "set" method, knob object is passed as well
      - the other knobs in the knob list have a "set" method which gets
        called for the others.
    """
    def __init__(self, initialValue=None, minimum=0., maximum=1.):
        self.minimum = minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []

    def attach(self, knob):
        self.knobs += [knob]

    def set(self, value, knob=None):
        if self.value != self.constrain(value):
            self.value = self.constrain(value)
            for feedbackKnob in self.knobs:
                if feedbackKnob != knob:
                    feedbackKnob.setKnob(self.value)
        # Adding a new feature that allows one to loop backwards or forwards:
        elif self.maximum != self.minimum:

            if self.value == self.maximum:
                self.value = self.minimum
                for feedbackKnob in self.knobs:
                    if feedbackKnob != knob:
                        feedbackKnob.setKnob(self.value)

            elif self.value == self.minimum:
                self.value = self.maximum
                for feedbackKnob in self.knobs:
                    if feedbackKnob != knob:
                        feedbackKnob.setKnob(self.value)
        return self.value

    def setMax(self, max_arg, knob=None):
        self.maximum = max_arg
        self.value = self.constrain(self.value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value


class PlaybackBar(Tk.Frame):

    """
    A Class that will handle the time-stepping in Iseult, and has the
    following, a step left button, a play/pause button, a step right button, a
    playbar, and a settings button.
    """

    def __init__(self, parent, param, canvas = None):
        Tk.Frame.__init__(self)
        self.parent = parent
        self.playPressed = False

        # This param should be the time-step of the simulation
        self.param = param

        # make a button that skips left
        self.skipLB = ttk.Button(self, text = '<', command = self.SkipLeft)
        self.skipLB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # make the play button
        self.playB = ttk.Button(self, text = 'Play', command = self.PlayHandler)
        self.playB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a button that skips right
        self.skipRB = ttk.Button(self, text = '>', command = self.SkipRight)
        self.skipRB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # An entry box that will let us choose the time-step
        ttk.Label(self, text='n= ').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # A StringVar for a box to type in a frame num, linked to self.param
        self.tstep = Tk.StringVar()
        # set it to the param value
        self.tstep.set(str(self.param.value))

        # the entry box
        self.txtEnter = ttk.Entry(self, textvariable=self.tstep, width=6)
        self.txtEnter.pack(side=Tk.LEFT, fill = Tk.BOTH, expand = 0)

        # A slider that will show the progress in the simulation as well as
        # allow us to select a time. Now the slider just changes the tstep box
        self.slider = ttk.Scale(self, from_=self.param.minimum, to=self.param.maximum, command = self.ScaleHandler)
        self.slider.set(self.param.value)
        self.slider.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        # bind releasing the moust button to updating the plots.
        self.slider.bind("<ButtonRelease-1>", self.UpdateValue)

        new_frame = ttk.Frame(self)
        self.LoopVar = Tk.IntVar()
        self.LoopVar.set(self.parent.MainParamDict['LoopPlayback'])
        self.LoopVar.trace('w', self.LoopChanged)
        self.RecordFrames = ttk.Checkbutton(new_frame, text = 'Loop',
                                            variable = self.LoopVar)
        self.RecordFrames.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)


        self.RecVar = Tk.IntVar()
        self.RecVar.set(self.parent.MainParamDict['Recording'])
        self.RecVar.trace('w', self.RecChanged)
        ttk.Checkbutton(new_frame, text = 'Record',
                        variable = self.RecVar).pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)
        new_frame.pack(side= Tk.LEFT, fill = Tk.BOTH, expand =0)

        # a measurement button that should lauch a window to take measurements.
        self.MeasuresB= ttk.Button(self, text='FFT', command=self.OpenMeasures)
        self.MeasuresB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)


        # a settings button that should lauch some global settings.
        self.SettingsB= ttk.Button(self, text='Settings', command=self.parent.OpenSettings)
        self.SettingsB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a reload button that reloads the files and then refreshes the plot
        ttk.Button(self, text = 'Reload', command = self.OnReload).pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # a refresh button that refreshing the current timestep
        ttk.Button(self, text = 'Refresh', command = self.OnRefresh).pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        #attach the parameter to the Playbackbar
        self.param.attach(self)

    def OnReload(self, *args):
        self.parent.ReloadPath()
        self.parent.RenewCanvas()

    def OnRefresh(self, *args):
        self.parent.RefreshTimeStep()
        self.parent.RenewCanvas()

    def RecChanged(self, *args):
        if self.RecVar.get() == self.parent.MainParamDict['Recording']:
            pass
        else:
            self.parent.MainParamDict['Recording'] = self.RecVar.get()
            if self.parent.MainParamDict['Recording'] == 1:
                self.parent.PrintFig()

    def LoopChanged(self, *args):
        if self.LoopVar.get() == self.parent.MainParamDict['LoopPlayback']:
            pass
        else:
            self.parent.MainParamDict['LoopPlayback'] = self.LoopVar.get()

    def SkipLeft(self, e = None):
        self.param.set(self.param.value - self.parent.MainParamDict['SkipSize'])

    def SkipRight(self, e = None):
        self.param.set(self.param.value + self.parent.MainParamDict['SkipSize'])

    def PlayHandler(self, e = None):
        if not self.playPressed:
            # Set the value of play pressed to true, change the button name to
            # pause, turn off clear_fig, and start the play loop.
            self.playPressed = True
            self.parent.RenewCanvas()

            self.playB.config(text='Pause')

            self.after(int(self.parent.MainParamDict['WaitTime']*1E3), self.blink)
        else:
            self.parent.resizable(1,1)
            # pause the play loop, turn clear fig back on, and set the button name back to play
            self.playPressed = False
            try:
                self.MovieFrame.destroy()
            except AttributeError:
                pass
            self.parent.RenewCanvas()
#            self.parent.MainParamDict['ClearFig'] = True
            self.playB.config(text='Play')


    def OpenMeasures(self):
        if self.parent.measure_window is None:
            self.parent.measure_window = MeasureFrame(self.parent)
        else:
            self.parent.measure_window.destroy()
            self.parent.measure_window = MeasureFrame(self.parent)


    def blink(self):
        if self.playPressed:
            # First check to see if the timestep can get larger
            if self.param.value == self.param.maximum and not self.parent.MainParamDict['LoopPlayback']:
                # push pause button
                self.PlayHandler()

            # otherwise skip right by size skip size
            else:
                self.param.set(self.param.value + self.parent.MainParamDict['SkipSize'])

            # start loopin'
            self.after(int(self.parent.MainParamDict['WaitTime']*1E3), self.blink)


    def TextCallback(self):
        try:
            #make sure the user types in a int
            if int(self.tstep.get()) != self.param.value:
                self.param.set(int(float(self.tstep.get())))
        except ValueError:
            #if they type in random stuff, just set it ot the param value
            self.tstep.set(str(self.param.value))

    def ScaleHandler(self, e):
        # if changing the scale will change the value of the parameter, do so
        try:
            if int(self.tstep.get()) != int(self.slider.get()):
                self.tstep.set(str(int(self.slider.get())))
        except ValueError:
            #if they type in random stuff, just set it ot the param value
            self.tstep.set(str(int(self.slider.get())))

    def UpdateValue(self, *args):
        if int(self.slider.get()) != self.param.value:
            self.param.set(int(self.slider.get()))
    def setKnob(self, value):
        pass
#        #set the text entry value
#        self.tstep.set(str(value))
        #set the slider
#        self.slider.set(value)


class MainApp(Tk.Tk):
    """ We simply derive a new class of Frame as the man frame of our app"""
    def __init__(self, name,cmd_args):

        Tk.Tk.__init__(self)
        self.update_idletasks()
        menubar = Tk.Menu(self)
        self.wm_title(name)
        self.settings_window = None
        self.measure_window = None


        self.cmd_args = cmd_args
#        if self.cmd_args.r:
#            self.iconify()
        # A variable that keeps track of the first graph with spatial x & y axes
        self.first_x = None
        self.first_y = None

        # An int that stores the current stride
        self.stride = 0

        self.IseultDir = os.path.join(os.path.dirname(__file__),'..')

        # a list of cmaps with orange prtl colors
        self.cmaps_with_green = ['viridis', 'Rainbow + White', 'Blue/Green/Red/Yellow', 'Cube YF', 'Linear_L']



        fileMenu = Tk.Menu(menubar, tearoff=False)
        self.presetMenu = Tk.Menu(menubar, tearoff=False, postcommand=self.ViewUpdate)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label= 'Open Directory', command = self.OnOpen, accelerator='Command+o')

        fileMenu.add_command(label="Exit", underline=1,
                             command=quit, accelerator="Ctrl+Q")
        fileMenu.add_command(label= 'Save Current State', command = self.OpenSaveDialog)
        fileMenu.add_command(label= 'Make a Movie', command = self.OpenMovieDialog)
        fileMenu.add_command(label= 'Reset Session', command = self.ResetSession)


        self.bind_all("<Control-q>", self.quit)
        self.bind_all("<Command-o>", self.OnOpen)
        self.bind_all("S", self.OpenSettings)
        oengus = Oengus(interactive=True)


        oengus.open_sim(picSim('../output/'))
        oengus.create_graphs()
        self.geometry(self.oengus.MainParamDict['WindowSize'])

        if self.MainParamDict['HorizontalCbars']:
            self.axes_extent = self.MainParamDict['HAxesExtent']
            self.cbar_extent = self.MainParamDict['HCbarExtent']
            self.SubPlotParams = self.MainParamDict['HSubPlotParams']

        else:
            self.axes_extent = self.MainParamDict['VAxesExtent']
            self.cbar_extent = self.MainParamDict['VCbarExtent']
            self.SubPlotParams = self.MainParamDict['VSubPlotParams']
        self.f.subplots_adjust( **self.SubPlotParams)

        # Make the object hold the timestep info
        self.TimeStep = Param(1, minimum=1, maximum=1000)
        self.playbackbar = PlaybackBar(self, self.TimeStep, canvas = self.canvas)

        # Add the toolbar
        self.toolbar =  MyCustomToolbar(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)

        # Some options to set the way the spectral lines are dashed
        self.dashes_options = [[],[3,1],[5,1],[1,1]]
        # Look for the tristan output files and load the file paths into
        # previous objects
        self.dirname = os.curdir
        if len(self.cmd_args.O[0])>0:
            self.dirname = os.path.join(self.dirname, self.cmd_args.O[0])

        self.findDir()


        self.TimeStep.attach(self)
        self.InitializeCanvas()

        menubar.add_cascade(label='Preset Views', underline=0, menu = self.presetMenu)
        self.playbackbar.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)
        self.update()


        self.config(menu=menubar)

        self.bind('<Return>', self.TxtEnter)
        self.bind('<Left>', self.playbackbar.SkipLeft)
        self.bind('<Right>', self.playbackbar.SkipRight)
        self.bind('r', self.playbackbar.OnReload)
        self.bind('<space>', self.playbackbar.PlayHandler)
        if self.cmd_args.b :
            self.after(0,self.MakeAMovie('out.mov', 1, -1, 1, 10))
            self.after(1, self.quit())
        self.update()
    def ViewUpdate(self):
        tmpdir = list(os.listdir(os.path.join(self.IseultDir, '.iseult_configs')))
        tmpdir.sort()
        for cfile in tmpdir:
            if cfile.split('.')[-1]=='yml':
                with open(os.path.join(os.path.join(self.IseultDir, '.iseult_configs'), cfile), 'r') as f:
                    cfgDict=yaml.safe_load(f)
                try:
                    if 'general' in cfgDict.keys():
                        if 'ConfigName'  in cfgDict['general'].keys():
                            tmpstr = cfgDict['general']['ConfigName']
                            try:
                                self.presetMenu.delete(tmpstr)
                            except:
                                pass
                            self.presetMenu.add_command(label = tmpstr, command = partial(self.LoadConfig, str(os.path.join(self.IseultDir,'.iseult_configs', cfile))))
                except:
                    pass
    def StrideChanged(self):
        # first we have to remove the calculated energy time steps
        self.TotalEnergyTimeSteps = []
        self.TotalEnergyTimes = np.array([])
        self.TotalIonEnergy = np.array([])
        self.TotalElectronEnergy = np.array([])

        self.TotalMagEnergy = np.array([])
        self.TotalBzEnergy = np.array([])
        self.TotalElectricEnergy = np.array([])

        # figure out all keys that have 'Prtl'
        # now we have to go through the data dictionary and remove the particle info
        for DataDict in self.ListOfDataDict:
            for k in self.prtl_keys:
                DataDict.pop(k, None)


    def quit(self, event):
        print("quitting...")
        sys.exit(0)


    def LoadConfig(self, config_file):
        # First get rid of any & all pop up windows:
        if self.settings_window is not None:
            self.settings_window.destroy()
        if self.measure_window is not None:
            self.measure_window.destroy()
        # Go through each sub-plot destroying any pop-up and
        # restoring to default params
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                self.SubPlotList[i][j].RestoreDefaultPlotParams()
                try:
                    self.SubPlotList[i][j].graph.settings_window.destroy()
                except:
                    pass
        # Read in the config file
        #config = configparser.RawConfigParser()
        #config.read(config_file)
        cfgDict = {}
        with open(config_file, 'r') as f:
            cfgDict = yaml.safe_load(f)
        # Generate the Main Param Dict
        self.GenMainParamDict(config_file)

        #Loading a config file may change the stride... watch out!
        if self.stride != self.MainParamDict['PrtlStride']:
            self.stride = self.MainParamDict['PrtlStride']
            self.StrideChanged()
        # Load in all the subplot params
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                tmp_str = 'Chart' + str(i) + '_' + str(j)

                if tmp_str in cfgDict.keys():

                    tmpchart_type = cfgDict[tmp_str]['ChartType']
                    self.SubPlotList[i][j].SetGraph(tmpchart_type)
                    for key, val in cfgDict[tmp_str].items():
                        self.SubPlotList[i][j].PlotParamsDict[tmpchart_type][key] = val
                else:
                    # The graph isn't specified in the config file, just set it equal to a phase plot
                    self.SubPlotList[i][j].SetGraph('PhasePlot')
        # There are a few parameters that need to be loaded separately, mainly in the playbackbar.
        self.playbackbar.RecVar.set(self.MainParamDict['Recording'])
        self.playbackbar.LoopVar.set(self.MainParamDict['LoopPlayback'])

        # refresh the geometry
        print(self.MainParamDict['WindowSize'])
        self.geometry(self.MainParamDict['WindowSize'])
        if self.MainParamDict['HorizontalCbars']:
            self.axes_extent = self.MainParamDict['HAxesExtent']
            self.cbar_extent = self.MainParamDict['HCbarExtent']
            self.SubPlotParams = self.MainParamDict['HSubPlotParams']

        else:
            self.axes_extent = self.MainParamDict['VAxesExtent']
            self.cbar_extent = self.MainParamDict['VCbarExtent']
            self.SubPlotParams = self.MainParamDict['VSubPlotParams']
        self.f.subplots_adjust( **self.SubPlotParams)
        # refresh the gridspec and re-draw all of the subplots
        self.UpdateGridSpec()

    def UpdateGridSpec(self, *args):
        '''A function that handles updates the gridspec that divides up of the
        plot into X x Y subplots'''
        # To prevent orphaned windows, we have to kill all of the windows of the
        # subplots that are no longer shown.

        for i in range(self.MainParamDict['MaxRows']):
            for j in range(self.MainParamDict['MaxCols']):
                if i < self.MainParamDict['NumOfRows'] and j < self.MainParamDict['NumOfCols']:
                    pass
                elif self.SubPlotList[i][j].graph.settings_window is not None:
                    self.SubPlotList[i][j].graph.settings_window.destroy()

        self.gs0 = gridspec.GridSpec(self.MainParamDict['NumOfRows'],self.MainParamDict['NumOfCols'])
        self.RenewCanvas(keep_view = False, ForceRedraw = True)


    def RefreshTimeStep(self):
        ''' A function that will find out will arrays need to be loaded for
        to draw the graphs. Then it will save all the data necessaru to
        If the time hasn't changed, it will only load new keys.'''
        if self.TimeStep.value in self.timestep_visited:
            cur_ind = self.timestep_visited.index(self.TimeStep.value)
            self.timestep_visited.pop(cur_ind)
            self.ListOfDataDict.pop(cur_ind)
            self.timestep_queue.remove(self.TimeStep.value)

        if self.TimeStep.value in self.TotalEnergyTimeSteps:
            self.TotalEnergyTimeSteps.remove(self.TimeStep.value)
            ind = self.TotalEnergyTimes.searchsorted(self.DataDict['time'][0])
            if ind < len(self.TotalEnergyTimes)-1:
                self.TotalEnergyTimes = np.append(self.TotalEnergyTimes[0:ind],self.TotalEnergyTimes[ind+1:])
                self.TotalElectronEnergy = np.append(self.TotalElectronEnergy[0:ind],self.TotalElectronEnergy[ind+1:])
                self.TotalIonEnergy = np.append(self.TotalIonEnergy[0:ind],self.TotalIonEnergy[ind+1:])
                self.TotalMagEnergy = np.append(self.TotalMagEnergy[0:ind], self.TotalMagEnergy[ind+1:])
                self.TotalBzEnergy = np.append(self.TotalBzEnergy[0:ind], self.TotalBzEnergy[ind+1:])
                self.TotalElectricEnergy = np.append(self.TotalElectricEnergy[0:ind], self.TotalElectricEnergy[ind+1:])
            else:
                self.TotalEnergyTimes = self.TotalEnergyTimes[0:ind]
                self.TotalElectronEnergy = self.TotalElectronEnergy[0:ind]
                self.TotalIonEnergy = self.TotalIonEnergy[0:ind]
                self.TotalMagEnergy = self.TotalMagEnergy[0:ind]
                self.TotalBzEnergy = self.TotalBzEnergy[0:ind]
                self.TotalElectricEnergy = self.TotalElectricEnergy[0:ind]

    def MakePrevCtypeList(self):
        self.prev_ctype_list = []
        for i in range(self.MainParamDict['NumOfRows']):
            tmp_ctype_l = []
            for j in range(self.MainParamDict['NumOfCols']):
                tmp_ctype_l.append(str(self.SubPlotList[i][j].chartType))
            self.prev_ctype_list.append(tmp_ctype_l)

    def SaveLLoc(self):
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                subplot = self.SubPlotList[i][j]
                if subplot.chartType == 'Moments' or subplot.chartType == 'TotalEnergyPlot':
                    try:
                        if subplot.graph.legend._get_loc() != 1:
                            subplot.SetPlotParam('legend_loc', ' '.join(str(x) for x in subplot.graph.legend._get_loc()), update_plot = False)
                    except:
                        pass
                if subplot.chartType == 'SpectraPlot':
                    try:
                        if subplot.graph.legDelta._get_loc() != 1:
                            subplot.SetPlotParam('PL_legend_loc', ' '.join(str(x) for x in subplot.graph.legDelta._get_loc()), update_plot = False)
                    except:
                        pass
                    try:
                        if subplot.graph.legT._get_loc() != 2:
                            subplot.SetPlotParam('T_legend_loc', ' '.join(str(x) for x in subplot.graph.legT._get_loc()), update_plot = False)
                    except:
                        pass
    def SetLLoc(self):
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):
                subplot = self.SubPlotList[i][j]
                if subplot.chartType == 'Moments' or subplot.chartType == 'TotalEnergyPlot':
                    if subplot.GetPlotParam('legend_loc') != 'N/A':
                        tmp_tup = float(subplot.GetPlotParam('legend_loc').split()[0]),float(subplot.GetPlotParam('legend_loc').split()[1])
                        subplot.graph.legend._set_loc(tmp_tup)
                if subplot.chartType == 'SpectraPlot':
                    if subplot.GetPlotParam('T_legend_loc') != 'N/A':
                        tmp_tup = float(subplot.GetPlotParam('T_legend_loc').split()[0]),float(subplot.GetPlotParam('T_legend_loc').split()[1])
                        try:
                            subplot.graph.legT._set_loc(tmp_tup)
                        except:
                            pass
                    if subplot.GetPlotParam('PL_legend_loc') != 'N/A':
                        tmp_tup = float(subplot.GetPlotParam('PL_legend_loc').split()[0]),float(subplot.GetPlotParam('PL_legend_loc').split()[1])
                        try:
                            subplot.graph.legDelta._set_loc(tmp_tup)
                        except:
                            pass

    def SaveView(self):
        # A function that will make sure our view will stay the same as the
        # plot updates.

        cur_view = []
        for ax, (view, (pos_orig, pos_active)) in self.toolbar._nav_stack().items():
            #print(type(ax))
            if ax in self.cbarList:
                continue
            cur_view.append(view)
        #    Go to the home view
        self.toolbar._nav_stack.home()
        #self.toolbar.home()
        home_view = []
        for ax, (view, (pos_orig, pos_active)) in self.toolbar._nav_stack().items():
            #print(type(ax))
            if ax in self.cbarList:
                continue
            home_view.append(view)
        #home_view =  list(self.toolbar._nav_stack.__call__())

            #print(view, pos_orig)
            # Find cbars
            #self.FindCbars(prev=True)
            # Filter out the colorbar axes
            #print(self.IsCbarList)
        try:
            self.is_changed_list = []
            self.diff_from_home = []
            self.old_views = []
            if cur_view is not None:
                for i in range(len(cur_view)):
                    is_changed =[]
                    diff_list = []
                    for j in range(4):
                        num_changed = home_view[i][j]-cur_view[i][j] != 0.0
                        is_changed.append(num_changed)
                        if num_changed:
                            if self.MainParamDict['xLimsRelative'] and j < 2:
                                #define the difference relative to the shock loc
                                diff_list.append(cur_view[i][j]-self.shock_loc)
                            else:
                                # define the difference relative to the home loc
                                diff_list.append(cur_view[i][j])

                        else:
                            # They haven't zoomed in, diff should be zero,
                            # but I'm making it a string so cur_view-shock_loc can be
                            # equal to zero and the hash still distinguish between the two cases.
                            diff_list.append('n/a')


                    self.is_changed_list.append(is_changed)
                    self.old_views.append(cur_view[i])
                    self.diff_from_home.append(diff_list)

        except IndexError:
            pass

    def LoadView(self):

        self.toolbar.push_current()

        cur_view = []
        tmpList = []
        for ax, (view, (pos_orig, pos_active)) in self.toolbar._nav_stack().items():
            tmpList.append(view)
            if ax in self.cbarList:
                continue
            cur_view.append(view)
        # Find the cbars in the current plot
        #self.FindCbars()
        try:
            # put the parts that have changed from the old view
            # into the proper place in the next view
            m = 0 # a counter that allows us to go from labeling the plots in [i][j] to 1d
            k = 0 # a counter that skips over the colorbars
            for i in range(self.MainParamDict['NumOfRows']):
                for j in range(self.MainParamDict['NumOfCols']):
                    tmp_old_view = list(self.old_views.pop(0))
                    tmp_new_view = list(cur_view[k])
                    self.SubPlotList[i][j].graph.axes._set_view(cur_view[k])
                    if self.prev_ctype_list[i][j] == self.SubPlotList[i][j].chartType:
                        # see if the view has changed from the home view
                        is_changed = self.is_changed_list[m]
                        if self.SubPlotList[i][j].Changedto2D or self.SubPlotList[i][j].Changedto1D:
                            # only keep the x values if they have changed
                            for n in range(2):
                                if is_changed[n]:
                                    if self.SubPlotList[i][j].PlotParamsDict[self.SubPlotList[i][j].chartType]['spatial_x']:
                                        tmp_new_view[n] = tmp_old_view[n]+self.MainParamDict['xLimsRelative']*(self.shock_loc-self.prev_shock_loc)
                                    else:
                                        tmp_new_view[n] = tmp_old_view[n]
                        else:
                            # Keep any y or x that is changed
                            for n in range(4):
                                if is_changed[n]:
                                    tmp_new_view[n] = tmp_old_view[n]
                                    if n < 2:
                                        if self.SubPlotList[i][j].PlotParamsDict[self.SubPlotList[i][j].chartType]['spatial_x']:
                                            tmp_new_view[n] = tmp_old_view[n]+self.MainParamDict['xLimsRelative']*(self.shock_loc-self.prev_shock_loc)
                                        else:
                                            tmp_new_view[n] = tmp_old_view[n]

                    cur_view[k] = tmp_new_view

                    self.SubPlotList[i][j].graph.axes._set_view(cur_view[k])

                    # Handle the counting of the 'views' array in matplotlib
                    #skip over colorbar axes
                    m += 1
                    k += 1
                    self.SubPlotList[i][j].Changedto1D = False
                    self.SubPlotList[i][j].Changedto2D = False
            self.toolbar.push_current()
            #self.toolbar._nav_stack.push(cur_view)
            #print(len(self.toolbar._nav_stack._elements))
            #self.toolbar.set_history_buttons()
            #self.toolbar._update_view()
        except IndexError:
            pass

    def RenewCanvas(self, keep_view = True, ForceRedraw = False):

        '''We have two way of updated the graphs: 1) by refreshing them using
        self.RefreshCanvas, we don't recreate all of the artists that matplotlib
        needs to make the plot work. self.RefreshCanvas should be fast. Two we
        can ReDraw the canvas using self.ReDrawCanvas. This recreates all the
        artists and will be slow. Sometimes the graph must be redrawn however,
        if the GridSpec changed, more plots are added, the chartype changed, if
        the plot went from 2d to 1D, etc.. If any change occurs that requires a
        redraw, renewcanvas must be called with ForceRedraw = True. '''

        self.SaveLLoc()
        if ForceRedraw:
            self.ReDrawCanvas(keep_view = keep_view)
        else:
            self.RefreshCanvas(keep_view = keep_view)
        # Record the current ctypes for later
        self.MakePrevCtypeList()
        for elm in tmp_list:
            self.DataDict.pop(elm, None)
        self.SetLLoc()
        # Save the image for quick playback later
        #self.SaveTmpFig()


    def ReDrawCanvas(self, keep_view = True):
        #  We need to see if the user has moved around the zoom level in python.
        # First we see if there are any views in the toolbar
        cur_view =  self.toolbar._nav_stack.__call__()
        if cur_view is None:
            keep_view = False
        if self.NewDirectory:
            keep_view = False
        if keep_view:
            self.SaveView()

        self.f.clf()
        #
        if self.MainParamDict['ClearFig']:
            self.canvas.draw()

        self.LoadAllKeys()


        # Calculate the new xmin, and xmax

        # Find the first position with a physical x,y & k axis:
        self.first_x = None
        self.first_y = None
        self.first_k = None
        k = 0
        # find the first spatial x and y
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):

                # First handle the axes sharing
                if self.SubPlotList[i][j].chartType == 'FFTPlots':
                    # The plot type is a spectral plot, which has no spatial dim
                    if self.first_k is None:
                        self.first_k = (i,j)
                elif self.SubPlotList[i][j].chartType == 'SpectraPlot':
                    # The plot type is a spectral plot, which has no spatial dim
                    pass
                elif self.MainParamDict['LinkSpatial'] != 1 and self.SubPlotList[i][j].chartType == 'PhasePlot':
                    # If this is the case we don't care about the phase plots
                    # as we don't want to share the axes
                    pass
                elif self.MainParamDict['LinkSpatial'] != 1 and self.SubPlotList[i][j].chartType == 'EnergyPlot':
                    # If this is the case we don't care about the phase plots
                    # as we don't want to share the axes
                    pass
                elif self.MainParamDict['LinkSpatial'] == 3 and self.SubPlotList[i][j].GetPlotParam('twoD'):
                    # If the plot is twoD share the axes
                    if self.first_x is None and self.SubPlotList[i][j].GetPlotParam('spatial_x'):
                        self.first_x = (i,j)
                    if self.first_y is None and self.SubPlotList[i][j].GetPlotParam('spatial_y'):
                        self.first_y = (i,j)

                else:
                    # Just find the first spatial x and y direction.
                    if self.first_x is None and self.SubPlotList[i][j].GetPlotParam('spatial_x'):
                        self.first_x = (i,j)
                    if self.first_y is None and self.SubPlotList[i][j].GetPlotParam('spatial_y'):
                        self.first_y = (i,j)

                # Now... We can draw the graph.
                self.SubPlotList[i][j].DrawGraph()

        if self.MainParamDict['ShowTitle']:
            tmpstr = get_flist_numbers(self.dirname)[self.TimeStep.value-1]
            self.f.suptitle(os.path.abspath(self.dirname)+ '/*.'+tmpstr+' at time t = %d $\omega_{pe}^{-1}$'  % round(self.DataDict['time'][0]), size = 15)
        if keep_view:
            self.LoadView()


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
                        k = min(self.SubPlotList[spos[0]][spos[1]].graph.spect_num, len(self.dashes_options)-1)
                        # Append the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].graph.axes.axvline(
                        max(self.SubPlotList[spos[0]][spos[1]].graph.i_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin+1),
                        linewidth = 1.5, linestyle = '-', color = self.ion_color))
                        # Choose the left dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[-1].set_dashes(self.dashes_options[k])

                        # Append the right line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].graph.axes.axvline(
                        min(self.SubPlotList[spos[0]][spos[1]].graph.i_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax+1),
                        linewidth = 1.5, linestyle = '-', color = self.ion_color))
                        # Choose the right dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[-1].set_dashes(self.dashes_options[k])
            else:
                for spos in self.spectral_plot_list:
                    if self.SubPlotList[spos[0]][spos[1]].GetPlotParam('show_electrons'):
                        k = min(self.SubPlotList[spos[0]][spos[1]].graph.spect_num, len(self.dashes_options)-1)
                        # Append the left line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].graph.axes.axvline(
                        max(self.SubPlotList[spos[0]][spos[1]].graph.e_left_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmin+1),
                        linewidth = 1.5, linestyle = '-', color = self.electron_color))
                        # Choose the left dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[-1].set_dashes(self.dashes_options[k])

                        # Append the right line to the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines.append(self.SubPlotList[pos[0]][pos[1]].graph.axes.axvline(
                        min(self.SubPlotList[spos[0]][spos[1]].graph.e_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax+1),
                        linewidth = 1.5, linestyle = '-', color = self.electron_color))
                        # Choose the right dashes pattern
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[-1].set_dashes(self.dashes_options[k])

        self.canvas.draw()
        self.canvas.get_tk_widget().update_idletasks()


        if self.MainParamDict['Recording']:
            self.PrintFig()


    def RefreshCanvas(self, keep_view = True):
        #  We need to see if the user has moved around the zoom level in python.
        # First we see if there are any views in the toolbar
        cur_view =  self.toolbar._nav_stack.__call__()
        if cur_view is None:

            keep_view = False

            self.diff_from_home = []
            for i in range(self.MainParamDict['NumOfRows']*self.MainParamDict['NumOfCols']):
                self.diff_from_home.append(['n/a', 'n/a', 'n/a', 'n/a'])


        if self.NewDirectory:
            keep_view = False
        if keep_view:
            self.SaveView()


        self.toolbar._nav_stack.clear()

        self.LoadAllKeys()


        # By design, the first_x and first_y cannot change if the graph is
        # being refreshed. Any call that would require this needs a redraw
        # Now we refresh the graph.
        for i in range(self.MainParamDict['NumOfRows']):
            for j in range(self.MainParamDict['NumOfCols']):

                self.SubPlotList[i][j].RefreshGraph()

        if self.MainParamDict['ShowTitle']:
            tmpstr = self.PathDict['Prtl'][self.TimeStep.value-1].split('.')[-1]
            self.f.suptitle(os.path.abspath(self.dirname)+ '/*.'+tmpstr+' at time t = %d $\omega_{pe}^{-1}$'  % round(self.DataDict['time'][0]), size = 15)

        if keep_view:
            self.LoadView()


        for pos in self.phase_plot_list:
            i = 0
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
                        # Append the right line of the list
                        self.SubPlotList[pos[0]][pos[1]].graph.IntRegionLines[i].set_xdata(
                        [min(self.SubPlotList[spos[0]][spos[1]].graph.e_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax+1),
                        min(self.SubPlotList[spos[0]][spos[1]].graph.e_right_loc, self.SubPlotList[pos[0]][pos[1]].graph.xmax-1)])
                        i+=1
        self.canvas.draw()
        self.canvas.get_tk_widget().update_idletasks()

        if self.MainParamDict['Recording']:
            self.PrintFig()


    def MakeAMovie(self, fname, start, stop, step, FPS):
        '''Record a movie'''
        # Where-ever you are create a hidden file and then delete that directory:
        self.PrintFig(MakingMovie= True)
        # Delete all the images in that subdirectory
        if os.path.isdir(os.path.join(self.movie_dir, '../tmp_erase')):
            for name in os.listdir(os.path.join(self.movie_dir, '../tmp_erase')):
                os.remove(os.path.join(self.movie_dir, '../tmp_erase', name))

            # First find the last frame is stop is -1:

            if stop == -1:
                stop = len(self.PathDict['Param'])

            # Now build all the frames we have to visit
            frame_arr = np.arange(start, stop, step)
            if frame_arr[-1] != stop:
                frame_arr = np.append(frame_arr, stop)

            # If total energy plot is showing, we have to loop through everything twice.

            if self.showing_total_energy_plt:
                for k in frame_arr:
                    self.TimeStep.set(k)

            for i in frame_arr:
                self.TimeStep.set(i)
                self.PrintFig(MakingMovie  = True)

            # The ffmpeg command we want to call.
            # ffmpeg -y -f image2 -framerate 8 -pattern_type glob -i '*.png' -codec copy out.mov

            cmdstring = ['xterm', '-e','ffmpeg',
                        '-y', '-f', 'image2', # overwrite, image2 is a colorspace thing.
                        '-framerate', str(int(FPS)), # Set framerate to the the user selected option
                        '-pattern_type', 'glob', '-i', os.path.join(self.movie_dir, '../tmp_erase','*.png'), # Not sure what this does... I am going to get rid of it
                        '-codec', 'copy',  # save as a *.mov
                        os.path.join(os.path.join(self.movie_dir,'..'),fname)]#, '&']#, # output name,
                        #'<dev/null', '>dev/null', '2>/var/log/ffmpeg.log', '&'] # run in background
            try:
                subprocess.call(cmdstring)
            except OSError:
                try:
                    subprocess.call(cmdstring[2:])
                except OSError:
                    messagebox.showwarning(
                        "Problems saving a movie",
                        "Please make sure that ffmpeg is installedgg on your machine."
                        )

            for name in os.listdir(os.path.join(self.movie_dir, '../tmp_erase')):
                os.remove(os.path.join(self.movie_dir, '../tmp_erase', name))
            os.rmdir(os.path.join(self.movie_dir, '../tmp_erase'))

    def OpenSaveDialog(self):
        SaveDialog(self)
    def OpenMovieDialog(self):
        MovieDialog(self)

    def onclick(self, event):
        '''After being clicked, we should use the x and y of the cursor to
        determine what subplot was clicked'''

        # Since the location of the cursor is returned in pixels and gs0 is
        # given as a relative value, we must first convert the value into a
        # relative x and y
        if not event.inaxes:
            pass
        if event.button == 1:
            pass
        else:
            fig_size = self.f.get_size_inches()*self.f.dpi # Fig size in px

            x_loc = event.x/fig_size[0] # The relative x position of the mouse in the figure
            y_loc = event.y/fig_size[1] # The relative y position of the mouse in the figure

            sub_plots = self.gs0.get_grid_positions(self.f)
            row_array = np.sort(np.append(sub_plots[0], sub_plots[1]))
            col_array = np.sort(np.append(sub_plots[2], sub_plots[3]))
            i = int((len(row_array)-row_array.searchsorted(y_loc))/2)
            j = int(col_array.searchsorted(x_loc)//2)

            self.SubPlotList[i][j].OpenSubplotSettings()

    def setKnob(self, value):
        # If the time parameter changes update the plots
        self.RenewCanvas()

        self.playbackbar.tstep.set(str(value))
        #set the slider
        self.playbackbar.slider.set(value)

    def OpenSettings(self, *args):
        if self.settings_window is None:
            self.settings_window = SettingsFrame(self)
        else:
            self.settings_window.destroy()
            self.settings_window = SettingsFrame(self)

    def TxtEnter(self, e):
        self.playbackbar.TextCallback()

def runMe(cmd_args):
    app = MainApp('Iseult', cmd_args)
    app.mainloop()
