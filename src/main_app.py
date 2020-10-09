#! /usr/bin/env python
import os
import sys
import yaml
from functools import partial
from pic_sim import picSim
from oengus import Oengus
import numpy as np
from mpl_param import Param

from movie_dialog import MovieDialog
from open_sim_dialog import OpenSimDialog
from save_config import SaveDialog
from scalar_flds_settings import ScalarFieldsSettings
from vector_flds_settings import VectorFieldsSettings
from scalar_vs_time_settings import ScalarVsTimeSettings
from phase_settings import phaseSettings
from playback_bar import playbackBar
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from PyQt5.QtGui import QKeySequence
from custom_toolbar import myCustomToolbar
from PyQt5.QtCore import Qt, QFileSystemWatcher
from PyQt5.QtWidgets import QAction, qApp

class MainApp(QtWidgets.QMainWindow):
    """ We simply derive a new class of Frame as the man frame of our app"""
    def __init__(self, name, cmd_args):

        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QtWidgets.QVBoxLayout(self._main)
        self.setWindowTitle(name)


        self.cmd_args = cmd_args

        # A variable that keeps track of the first graph
        # with spatial x & y axes
        self.first_x = None
        self.first_y = None

        # An int that stores the current stride
        self.stride = 0

        self.IseultDir = os.path.join(os.path.dirname(__file__), '..')

        self.oengus = Oengus(
            interactive=True, mainApp=self,
            preset_view=cmd_args.p)
        # open a sim
        if len(self.cmd_args.O[0]) == 0:
            self.oengus.sims[0].outdir = os.curdir
        else:
            for i, outdir in enumerate(self.cmd_args.O):
                if i == len(self.oengus.sims):
                    self.oengus.add_sim(f'sim{i}')
                self.oengus.sims[i].outdir = outdir
        self.oengus.create_graphs()
        """
        self.setGeometry(self.oengus.MainParamDict['WindowSize'])
        self.minsize(780, 280)
        """
        layout.addWidget(self.oengus.canvas)
        self.toolbar = myCustomToolbar(self.oengus.canvas, self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        self.toolbar)
        # self.toolbar.update()
        # self.oengus.canvas._tkcanvas.pack(
        #    side=Tk.RIGHT, fill=Tk.BOTH, expand=1)

        self.oengus.canvas.mpl_connect('button_press_event', self.onclick)

        # Make the object hold the timestep info

        self.time_step = Param(1, minimum=1, maximum=1000)
        self.playbackbar = playbackBar(self.oengus, self.time_step)
        layout.addWidget(self.playbackbar)
        self.time_step.attach(self)
        self.time_step.loop = self.oengus.MainParamDict['LoopPlayback']
        self.time_step.set_max(len(self.oengus.sims[self.playbackbar.cur_sim]))
        self.time_step.set(len(self.oengus.sims[self.playbackbar.cur_sim]))
        self.popups_dict = {}
        self.create_shortcuts()
        self.build_menu()
        #self.config(menu=menubar)
        #self.protocol("WM_DELETE_WINDOW", sys.exit)

        # Overload the close function
        self.closeEvent = self.on_quit

    def build_menu(self):
        exitAct = QAction(' &Quit', self)

        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(qApp.quit)

        # self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        bar = self.menuBar()
        self.views_menu = bar.addMenu("Preset Views")
        self.views_update()
        self.view_dir_watcher = QFileSystemWatcher()
        self.view_dir_watcher.addPath(
            os.path.join(self.IseultDir, '.iseult_configs'))
        self.view_dir_watcher.directoryChanged.connect(self.views_update)

        # file.addAction("New")

        # self.show()
        """
        menubar = Tk.Menu(self)
        self.wm_title()
        fileMenu = Tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)

        fileMenu.add_command(
            label='Save Current State', command=self.OpenSaveDialog)
        fileMenu.add_command(
            label='Open Simulation', command=self.open_sim_dialog)
        fileMenu.add_command(
           label='Make a Movie', command=self.open_movie_dialog)
        fileMenu.add_command(label="Exit", underline=1,
                            command=quit, accelerator="Ctrl+Q")
        # fileMenu.add_command(
        #   label= 'Reset Session', command = self.ResetSession)
        self.preset_menu = Tk.Menu(
            menubar, tearoff=False, postcommand=self.views_update)

        menubar.add_cascade(
            label='Preset Views', underline=0, menu=self.preset_menu)
        """

    def create_shortcuts(self):
        self.settings_acc = QtWidgets.QShortcut(QKeySequence('s'), self)
        self.settings_acc.activated.connect(self.open_settings)

        self.shortcut_play = QtWidgets.QShortcut(
            QKeySequence('space'), self)
        self.shortcut_play.activated.connect(self.playbackbar.play_handler)

        self.shortcut_skip_right = QtWidgets.QShortcut(
            QKeySequence('right'), self)
        self.shortcut_skip_right.activated.connect(self.playbackbar.skip_right)

        self.shortcut_skip_left = QtWidgets.QShortcut(
            QKeySequence('left'), self)
        self.shortcut_skip_left.activated.connect(self.playbackbar.skip_left)

        """
        self.bind_all("<Control-q>", self.quit)
        # self.bind_all("<Command-o>", self.OnOpen)
        self.bind_all("S", self.open_settings)
        self.bind('<Return>', self.txt_enter)
        self.bind('<Left>', self.playbackbar.skip_left)
        self.bind('<Right>', self.playbackbar.skip_right)
        self.bind_all('r', self.playbackbar.on_reload())
        self.bind('<space>', self.playbackbar.play_handler)
        """
    def views_update(self):
        # Clear the menu of all actions
        for act in self.views_menu.actions():
            self.removeAction(act)
        self.views_menu.clear()
        tmpdir = os.listdir(os.path.join(self.IseultDir, '.iseult_configs'))
        tmpdir = [elm for elm in tmpdir]
        tmpdir.sort()
        cfiles = []
        cfg_dir = os.path.join(self.IseultDir, '.iseult_configs')
        for cfile in tmpdir:
            if cfile.split('.')[-1] == 'yml':
                with open(os.path.join(cfg_dir, cfile), 'r') as f:
                    cfgDict = yaml.safe_load(f)
                if 'general' in cfgDict.keys():
                    if 'ConfigName' in cfgDict['general'].keys():
                        tmpstr = cfgDict['general']['ConfigName']
                        cfiles.append((cfile, tmpstr))

        cfiles = sorted(cfiles, key=lambda x: x[1])
        for cfile, name in cfiles:
            load_view_action = QAction(name, self)
            load_view_action.triggered.connect(partial(
                   self.load_config,
                    name))
            self.views_menu.addAction(load_view_action)


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
            fig_size = self.oengus.figure.get_size_inches()
            fig_size *= self.oengus.figure.dpi

            # The relative x position of the mouse in the figure
            x_loc = event.x/fig_size[0]
            # The relative y position of the mouse in the figure
            y_loc = event.y/fig_size[1]

            sub_plots = self.oengus.gs0.get_grid_positions(self.oengus.figure)
            row_array = np.sort(np.append(sub_plots[0], sub_plots[1]))
            col_array = np.sort(np.append(sub_plots[2], sub_plots[3]))
            i = int((len(row_array)-row_array.searchsorted(y_loc))/2)
            j = int(col_array.searchsorted(x_loc)//2)
            if f'{i,j}' in self.popups_dict:
                if self.popups_dict[f'{i,j}'] is not None:
                    self.popups_dict[f'{i,j}'].destroy()
            if self.oengus.SubPlotList[i][j].chart_type == 'ScalarFlds':
                self.popups_dict[f'{i,j}'] = ScalarFieldsSettings(self, (i, j))
                self.popups_dict[f'{i,j}'].show()
            elif self.oengus.SubPlotList[i][j].chart_type == 'VectorFlds':
                self.popups_dict[f'{i,j}'] = VectorFieldsSettings(self, (i, j))
                self.popups_dict[f'{i,j}'].show()
            elif self.oengus.SubPlotList[i][j].chart_type == 'PhasePlot':
                self.popups_dict[f'{i,j}'] = phaseSettings(self, (i, j))
                self.popups_dict[f'{i,j}'].show()
            elif self.oengus.SubPlotList[i][j].chart_type == 'ScalarVsTime':
                self.popups_dict[f'{i,j}'] = ScalarVsTimeSettings(self, (i, j))

    def OpenSaveDialog(self):
        SaveDialog(self)

    def open_sim_dialog(self):
        OpenSimDialog(self)

    def load_config(self, config_name):
        # First get rid of any & all pop up windows:
        if self.playbackbar.settings_window is not None:
            self.playbackbar.settings_window.destroy()
        # if self.measure_window is not None:
        #    self.measure_window.destroy()
        # Go through each sub-plot destroying any pop-up and
        # restoring to default params
        for key, val in self.popups_dict.items():
            if val is not None:
                val.destroy()

        self.oengus.load_view(config_name)

        # There are a few parameters that need to be loaded separately,
        # mainly in the playbackbar.
        self.playbackbar.loop_chk.setChecked(
            self.oengus.MainParamDict['LoopPlayback'])

        self.oengus.create_graphs()
        # self.geometry(self.oengus.MainParamDict['WindowSize'])
        self.oengus.canvas.draw()
        # refresh the geometry
        """
        self.geometry(self.oengus.MainParamDict['WindowSize'])
        """

    def changePlotType(self, pos, new_plot_type):
        self.oengus.SubPlotList[pos[0]][pos[1]] = \
            self.oengus.plot_types_dict[new_plot_type](self.oengus, pos, {})
        self.oengus.figure.clf()
        self.oengus.create_graphs()
        self.oengus.canvas.draw()

    def update_all_sim_lists(self):
        # Calc the current sims shown
        self.oengus.calc_sims_shown()

        # update playbackbar combo
        self.playbackbar.update_sim_list()

    def txt_enter(self, e):
        self.playbackbar.text_callback()

    def open_movie_dialog(self):
        MovieDialog(self, self.oengus)

    def open_settings(self, *evnt_args):
        self.playbackbar.open_settings()

    def set_knob(self, value):
        # self.oengus.sims[self.playbackbar.cur_sim].refresh_directory()
        # self.time_step.set_max(
        #    len(self.oengus.sims[self.playbackbar.cur_sim]))
        self.oengus.sims[self.playbackbar.cur_sim].set_time(value - 1)
        if self.oengus.MainParamDict['LinkTime']:
            unit = self.oengus.MainParamDict['TimeUnits']
            cur_t = self.oengus.sims[self.playbackbar.cur_sim].get_time(
                units=unit)
            for sim in self.oengus.sims:
                sim.set_time(cur_t, units=unit)
        self.oengus.draw_output()

    def on_quit(self, *event):
        if self.playbackbar.settings_window is not None:
            self.playbackbar.settings_window.close()


def runMe(cmd_args):
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)
    app = MainApp('Iseult', cmd_args)
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
