#! /usr/bin/env python
import time, os, sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from movie_dialog import MovieDialog
from oengus import Oengus
from pic_sim import picSim
import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
from mpl_param import Param
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

        fileMenu = Tk.Menu(menubar, tearoff=False)
        #self.presetMenu = Tk.Menu(menubar, tearoff=False, postcommand=self.ViewUpdate)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        #fileMenu.add_command(label= 'Open Directory', command = self.OnOpen, accelerator='Command+o')

        fileMenu.add_command(label="Exit", underline=1,
                             command=quit, accelerator="Ctrl+Q")
        #fileMenu.add_command(label= 'Save Current State', command = self.OpenSaveDialog)
        #fileMenu.add_command(label= 'Make a Movie', command = self.OpenMovieDialog)
        #fileMenu.add_command(label= 'Reset Session', command = self.ResetSession)


        self.bind_all("<Control-q>", self.quit)
        #self.bind_all("<Command-o>", self.OnOpen)
        #self.bind_all("S", self.OpenSettings)
        self.oengus = Oengus(interactive=True, tkApp = self)
        print(len(picSim()))

        self.oengus.open_sim(picSim())#os.path.join(os.path.dirname(__file__),'../output')))
        self.oengus.create_graphs()
        self.geometry(self.oengus.MainParamDict['WindowSize'])

        self.oengus.canvas._tkcanvas.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
        self.oengus.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        # Make the object hold the timestep info
        self.time_step = Param(1, minimum=1, maximum=1000)
        self.playbackbar = playbackBar(self.oengus, self.time_step, canvas = self.oengus.canvas)
        self.playbackbar.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)
        self.time_step.attach(self)
        #menubar.add_cascade(label='Preset Views', underline=0, menu = self.presetMenu)
        self.update()


        self.config(menu=menubar)
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.bind('<Return>', self.txt_enter)
        self.bind('<Left>', self.playbackbar.skip_left)
        self.bind('<Right>', self.playbackbar.skip_right)
        #self.bind('r', self.playbackbar.OnReload)
        #self.bind('<space>', self.playbackbar.PlayHandler)
        #self.update()

    def txt_enter(self, e):
        self.playbackbar.text_callback()
    def set_knob(self, value):
        self.oengus.draw_output(value-1)
        self.oengus.canvas.get_tk_widget().update_idletasks()

def runMe(cmd_args):
    app = MainApp('Iseult', cmd_args)
    app.mainloop()
