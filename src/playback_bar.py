import tkinter as Tk
from tkinter import ttk
from main_settings_window import SettingsFrame
import numpy as np
import time

class playbackBar(Tk.Frame):

    """
    A Class that will handle the time-stepping in Iseult, and has the
    following, a step left button, a play/pause button, a step right button, a
    playbar, and a settings button.
    """

    def __init__(self, oengus, tstep_param):
        Tk.Frame.__init__(self)
        self.oengus = oengus
        # This param should be the time-step of the simulation
        self.param = tstep_param

        self._cur_sim = 0  # A way to hold the current simulation

        self._play_debouncer = -np.inf
        self.play_pressed = False
        self.settings_window = None

        # make a button that skips left
        self.skipLB = ttk.Button(self, text='<', command=self.skip_left)
        self.skipLB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # make the play button
        self.playB = ttk.Button(self, text='Play', command=self.play_handler)
        self.playB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a button that skips right
        self.skipRB = ttk.Button(self, text='>', command=self.skip_right)
        self.skipRB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        self.cur_sim_name = Tk.StringVar(self)
        self.cur_sim_name.set(self.oengus.sims[self.cur_sim].name)
        self.cur_sim_name.trace('w', self.simChanged)

        self.sim_menu = ttk.OptionMenu(
            self,
            self.cur_sim_name,
            self.cur_sim_name.get(),
            *tuple(
                map(lambda x: self.oengus.sims[x].name,
                    self.oengus.sims_shown)))
        self.sim_menu.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # the Check boxes for the dimension
        # An entry box that will let us choose the time-step
        ttk.Label(self, text='n= ').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # A StringVar for a box to type in a frame num, linked to self.param
        self.tstep = Tk.StringVar()
        # set it to the param value
        self.tstep.set(str(self.param.value))

        # the entry box
        self.txt_enter = ttk.Entry(self, textvariable=self.tstep, width=6)
        self.txt_enter.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # A slider that will show the progress in the simulation as well as
        # allow us to select a time. Now the slider just changes the tstep box
        self.slider = ttk.Scale(
            self,
            from_=self.param.minimum,
            to=self.param.maximum,
            command=self.scale_handler)
        self.cur_sim = 0
        self.slider.set(self.param.value)
        self.slider.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        # bind releasing the moust button to updating the plots.
        self.slider.bind("<ButtonRelease-1>", self.update_value)

        new_frame = ttk.Frame(self)
        self.loop_var = Tk.IntVar()
        self.loop_var.set(self.oengus.MainParamDict['LoopPlayback'])
        self.loop_var.trace('w', self.loop_changed)
        self.loop_btn = ttk.Checkbutton(
            new_frame, text='Loop',
            variable=self.loop_var)
        self.loop_btn.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)

        new_frame.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a measurement button that should lauch a window to take measurements.
        # self.measuresB = ttk.Button(
        #    self, text='FFT', command=self.open_measures)
        # self.measuresB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a settings button that should lauch some global settings.
        self.settingsB = ttk.Button(
            self,
            text='Settings',
            command=self.open_settings)
        self.settingsB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a reload button that looks the files and then refreshes the plot
        ttk.Button(
            self, text='Reload',
            command=self.on_reload).pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # a button that clears the cache
        ttk.Button(
            self, text='Clear Cache',
            command=self.on_refresh).pack(
                side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        ttk.Button(
            self, text='Home',
            command=self.oengus.home).pack(
                side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # attach the parameter to the Playbackbar
        self.param.attach(self)

    def update_slider(self):
        self.param.set_max(len(self.oengus.sims[self._cur_sim]))
        self.slider.config(to=self.param.maximum)

    @property
    def cur_sim(self):
        return self._cur_sim

    @cur_sim.setter
    def cur_sim(self, val):
        self._cur_sim = val
        self.oengus.cur_sim = val
        self.update_slider()

    def update_sim_list(self):
        menu = self.sim_menu["menu"]
        menu.delete(0, "end")
        for x in self.oengus.sims_shown:
            name = self.oengus.sims[x].name
            menu.add_command(
                label=name,
                command=lambda value=name: self.cur_sim_name.set(value))

    def simChanged(self, *args):
        if self.cur_sim_name.get() == self.oengus.sims[self.cur_sim].name:
            pass
        else:
            names = [sim.name for sim in self.oengus.sims]
            self.cur_sim = names.index(self.cur_sim_name.get())
            self.oengus.cur_sim = self.cur_sim

    def on_reload(self):
        self.oengus.sims[self.cur_sim].refresh_directory()
        self.update_slider()

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsFrame(self.oengus)
        else:
            self.settings_window.destroy()
            self.settings_window = SettingsFrame(self.oengus)

    def on_refresh(self, *args):
        for sim in self.oengus.sims:
            sim.clear_caches()
        self.update_slider()
        self.oengus.draw_output()

    def loop_changed(self, *args):
        if self.loop_var.get() == self.oengus.MainParamDict['LoopPlayback']:
            pass
        else:
            self.oengus.MainParamDict['LoopPlayback'] = self.loop_var.get()
            self.param.loop = self.oengus.MainParamDict['LoopPlayback']

    def skip_left(self, e=None):
        self.param.set(
            self.param.value - self.oengus.MainParamDict['SkipSize'])

    def skip_right(self, e=None):
        self.param.set(
            self.param.value + self.oengus.MainParamDict['SkipSize'])

    def play_handler(self, e=None):
        tic = time.time()
        if tic - self._play_debouncer > .05:
            self._play_debouncer = tic
            if not self.play_pressed:
                # Set the value of play pressed to true, change the button name to
                # pause, turn off clear_fig, and start the play loop.
                self.play_pressed = True
                self.playB.config(text='Pause')

                self.after(
                    int(self.oengus.MainParamDict['WaitTime']*1E3), self.blink)
            else:
                # pause the play loop, turn clear fig back on,
                # and set the button name back to play
                self.play_pressed = False
                self.playB.config(text='Play')

    def blink(self):
        if self.play_pressed:
            # First check to see if the timestep can get larger
            no_loop = not self.oengus.MainParamDict['LoopPlayback']
            if self.param.value == self.param.maximum and no_loop:
                # push pause button
                self.play_handler()

            # otherwise skip right by size skip size
            else:
                self.param.set(
                    self.param.value + self.oengus.MainParamDict['SkipSize'])

            # start loopin'
            self.after(
                int(self.oengus.MainParamDict['WaitTime']*1E3),
                self.blink)

    def text_callback(self):
        try:
            # make sure the user types in a int
            if int(self.tstep.get()) != self.param.value:
                self.param.set(int(float(self.tstep.get())))
        except ValueError:
            # if they type in random stuff, just set it ot the param value
            self.tstep.set(str(self.param.value))

    def scale_handler(self, e):
        # if changing the scale will change the value of the parameter, do so
        try:
            if int(self.tstep.get()) != int(self.slider.get()):
                self.tstep.set(str(int(self.slider.get())))
        except ValueError:
            # if they type in random stuff, just set it ot the param value
            self.tstep.set(str(int(self.slider.get())))

    def update_value(self, *args):
        if int(self.slider.get()) != self.param.value:
            self.param.set(int(self.slider.get()))

    def set_knob(self, value):
        self.slider.set(value)
        self.tstep.set(str(value))
