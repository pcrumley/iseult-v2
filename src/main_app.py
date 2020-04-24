#! /usr/bin/env python
import time, os, sys, yaml
sys.path.append(os.path.join(os.path.dirname(__file__), 'popup_windows'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from custom_toolbar import myCustomToolbar
from matplotlib.figure import Figure
from movie_dialog import MovieDialog
from open_sim_dialog import OpenSimDialog
from save_config import SaveDialog
from oengus import Oengus
from pic_sim import picSim
from functools import partial
import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
from mpl_param import Param
import numpy as np
from scalar_flds_settings import ScalarFieldsSettings
from vector_flds_settings import VectorFieldsSettings
from phase_settings import phaseSettings
from playback_bar import playbackBar

def destroy(e):
    sys.exit()


class MainApp(Tk.Tk):
    """ We simply derive a new class of Frame as the man frame of our app"""
    def __init__(self, name,cmd_args):

        Tk.Tk.__init__(self)
        #self.update_idletasks()
        menubar = Tk.Menu(self)
        self.wm_title(name)


        self.cmd_args = cmd_args
#        if self.cmd_args.r:
#            self.iconify()
        # A variable that keeps track of the first graph with spatial x & y axes
        self.first_x = None
        self.first_y = None


        # An int that stores the current stride
        self.stride = 0

        self.IseultDir = os.path.join(os.path.dirname(__file__),'..')

        fileMenu = Tk.Menu(menubar, tearoff=False)
        #self.presetMenu = Tk.Menu(menubar, tearoff=False, postcommand=self.ViewUpdate)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        #fileMenu.add_command(label= 'Open Directory', command = self.OnOpen, accelerator='Command+o')

        fileMenu.add_command(label="Exit", underline=1,
                             command=quit, accelerator="Ctrl+Q")
        fileMenu.add_command(label= 'Save Current State', command = self.OpenSaveDialog)
        fileMenu.add_command(label= 'Open Simulation', command = self.open_sim_dialog)
        #fileMenu.add_command(label= 'Make a Movie', command = self.OpenMovieDialog)
        #fileMenu.add_command(label= 'Reset Session', command = self.ResetSession)
        self.preset_menu = Tk.Menu(menubar, tearoff=False, postcommand=self.viewsUpdate)
        menubar.add_cascade(label='Preset Views', underline=0, menu = self.preset_menu)

        self.bind_all("<Control-q>", self.quit)
        #self.bind_all("<Command-o>", self.OnOpen)
        #self.bind_all("S", self.OpenSettings)
        self.oengus = Oengus(interactive=True, tkApp = self)
        # open a sim


        self.oengus.sims[0].outdir = self.cmd_args.O[0] if len(self.cmd_args.O[0])>0 else os.curdir

        self.oengus.create_graphs()
        self.geometry(self.oengus.MainParamDict['WindowSize'])
        self.minsize(780, 280)

        self.toolbar = myCustomToolbar(self.oengus.canvas, self)
        self.toolbar.update()
        self.oengus.canvas._tkcanvas.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
        self.oengus.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.oengus.canvas.mpl_connect('button_press_event', self.onclick)
        # Make the object hold the timestep info
        self.time_step = Param(1, minimum=1, maximum=1000)
        self.playbackbar = playbackBar(self.oengus, self.time_step)
        self.playbackbar.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)
        self.time_step.attach(self)
        self.time_step.loop = self.oengus.MainParamDict['LoopPlayback']
        self.time_step.set_max(len(self.oengus.sims[self.playbackbar.cur_sim]))
        self.time_step.set(len(self.oengus.sims[self.playbackbar.cur_sim]))

        #menubar.add_cascade(label='Preset Views', underline=0, menu = self.presetMenu)


        self.popups_dict = {}

        self.config(menu=menubar)
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.bind('<Return>', self.txt_enter)
        self.bind('<Left>', self.playbackbar.skip_left)
        self.bind('<Right>', self.playbackbar.skip_right)
        #self.bind('r', self.playbackbar.OnReload)
        self.bind('<space>', self.playbackbar.play_handler)
        self.update()
    def viewsUpdate(self):
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
                                self.preset_menu.delete(tmpstr)
                            except:
                                pass
                            self.preset_menu.add_command(label = tmpstr, command = partial(self.LoadConfig, str(os.path.join(self.IseultDir,'.iseult_configs', cfile))))
                except:
                    pass
    def GetPlotParam(self, val):
        return 1
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
            fig_size = self.oengus.figure.get_size_inches()*self.oengus.figure.dpi # Fig size in px

            x_loc = event.x/fig_size[0] # The relative x position of the mouse in the figure
            y_loc = event.y/fig_size[1] # The relative y position of the mouse in the figure

            sub_plots = self.oengus.gs0.get_grid_positions(self.oengus.figure)
            row_array = np.sort(np.append(sub_plots[0], sub_plots[1]))
            col_array = np.sort(np.append(sub_plots[2], sub_plots[3]))
            i = int((len(row_array)-row_array.searchsorted(y_loc))/2)
            j = int(col_array.searchsorted(x_loc)//2)
            if f'{i,j}' in self.popups_dict:
                if self.popups_dict[f'{i,j}'] is not None:
                    self.popups_dict[f'{i,j}'].destroy()
            if self.oengus.SubPlotList[i][j].chart_type == 'ScalarFlds':
                self.popups_dict[f'{i,j}'] = ScalarFieldsSettings(self,(i,j))
            elif self.oengus.SubPlotList[i][j].chart_type == 'VectorFlds':
                self.popups_dict[f'{i,j}'] = VectorFieldsSettings(self,(i,j))
            elif self.oengus.SubPlotList[i][j].chart_type == 'PhasePlot':
                self.popups_dict[f'{i,j}'] = phaseSettings(self,(i,j))

    def OpenSaveDialog(self):
        SaveDialog(self)

    def open_sim_dialog(self):
        OpenSimDialog(self)

    def LoadConfig(self, config_file):
        # First get rid of any & all pop up windows:
        if self.playbackbar.settings_window is not None:
            self.playbackbar.settings_window.destroy()
        #if self.measure_window is not None:
        #    self.measure_window.destroy()
        # Go through each sub-plot destroying any pop-up and
        # restoring to default params
        for key, val in self.popups_dict.items():
            try:
                val.destroy()
            except:
                pass
        # Read in the config file
        #config = configparser.RawConfigParser()
        #config.read(config_file)
        cfgDict = {}
        with open(config_file, 'r') as f:
            cfgDict = yaml.safe_load(f)
        # Generate the Main Param Dict
        self.oengus.cfgDict = cfgDict
        self.oengus.GenMainParamDict()
        # Loading a config file may change the stride... watch out!
        for sim in self.oengus.sims:
            if sim.xtra_stride != self.oengus.MainParamDict['PrtlStride']:
                sim.xtra_stride = self.oengus.MainParamDict['PrtlStride']

        # There are a few parameters that need to be loaded separately, mainly in the playbackbar.
        self.playbackbar.rec_var.set(self.oengus.MainParamDict['Recording'])
        self.playbackbar.loop_var.set(self.oengus.MainParamDict['LoopPlayback'])

        self.oengus.figure.clf()

        self.oengus.create_graphs()
        self.geometry(self.oengus.MainParamDict['WindowSize'])
        self.oengus.canvas.draw()
        # refresh the geometry

        self.geometry(self.oengus.MainParamDict['WindowSize'])

    def changePlotType(self, pos, new_plot_type):
        self.oengus.SubPlotList[pos[0]][pos[1]] = self.oengus.plot_types_dict[new_plot_type](self.oengus, pos, {})
        self.oengus.figure.clf()

        self.oengus.create_graphs()
        self.oengus.canvas.draw()
    def txt_enter(self, e):
        self.playbackbar.text_callback()
    def set_knob(self, value):
        self.oengus.sims[self.playbackbar.cur_sim].refresh_directory()
        self.time_step.set_max(len(self.oengus.sims[self.playbackbar.cur_sim]))
        self.oengus.cur_times[self.playbackbar.cur_sim] = value - 1
        self.oengus.draw_output()
        self.oengus.canvas.get_tk_widget().update_idletasks()

def runMe(cmd_args):
    app = MainApp('Iseult', cmd_args)
    app.mainloop()
