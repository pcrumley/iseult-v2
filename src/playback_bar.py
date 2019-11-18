import tkinter as Tk
from tkinter import ttk
from main_settings_window import SettingsFrame

class playbackBar(Tk.Frame):

    """
    A Class that will handle the time-stepping in Iseult, and has the
    following, a step left button, a play/pause button, a step right button, a
    playbar, and a settings button.
    """

    def __init__(self, oengus, tstep_param):
        Tk.Frame.__init__(self)
        self.oengus = oengus
        self.play_pressed = False
        self.settings_window = None
        # This param should be the time-step of the simulation
        self.param = tstep_param

        # make a button that skips left
        self.skipLB = ttk.Button(self, text = '<', command = self.skip_left)
        self.skipLB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # make the play button
        self.playB = ttk.Button(self, text = 'Play', command = self.play_handler)
        self.playB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a button that skips right
        self.skipRB = ttk.Button(self, text = '>', command = self.skip_right)
        self.skipRB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # An entry box that will let us choose the time-step
        ttk.Label(self, text='n= ').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # A StringVar for a box to type in a frame num, linked to self.param
        self.tstep = Tk.StringVar()
        # set it to the param value
        self.tstep.set(str(self.param.value))

        # the entry box
        self.txt_enter = ttk.Entry(self, textvariable=self.tstep, width=6)
        self.txt_enter.pack(side=Tk.LEFT, fill = Tk.BOTH, expand = 0)

        # A slider that will show the progress in the simulation as well as
        # allow us to select a time. Now the slider just changes the tstep box
        self.slider = ttk.Scale(self, from_=self.param.minimum, to=self.param.maximum, command = self.scale_handler)
        self.slider.set(self.param.value)
        self.slider.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        # bind releasing the moust button to updating the plots.
        self.slider.bind("<ButtonRelease-1>", self.update_value)

        new_frame = ttk.Frame(self)
        self.loop_var = Tk.IntVar()
        self.loop_var.set(self.oengus.MainParamDict['LoopPlayback'])
        self.loop_var.trace('w', self.loop_changed)
        self.record_frames = ttk.Checkbutton(new_frame, text = 'Loop',
                                            variable = self.loop_var)
        self.record_frames.pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)


        self.rec_var = Tk.IntVar()
        self.rec_var.set(self.oengus.MainParamDict['Recording'])
        self.rec_var.trace('w', self.rec_changed)
        #ttk.Checkbutton(new_frame, text = 'Record',
        #                variable = self.rec_var).pack(side=Tk.TOP, fill=Tk.BOTH, expand=0)
        new_frame.pack(side= Tk.LEFT, fill = Tk.BOTH, expand =0)

        # a measurement button that should lauch a window to take measurements.
        #self.measuresB= ttk.Button(self, text='FFT', command=self.open_measures)
        #self.measuresB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)


        # a settings button that should lauch some global settings.
        self.settingsB= ttk.Button(self, text='Settings', command=self.open_settings)
        self.settingsB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # a reload button that reloads the files and then refreshes the plot
        #ttk.Button(self, text = 'Reload', command = self.on_reload).pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # a refresh button that refreshing the current timestep
        ttk.Button(self, text = 'Clear Cache', command = self.on_refresh).pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        #attach the parameter to the Playbackbar
        self.param.attach(self)
    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsFrame(self.oengus)
        else:
            self.settings_window.destroy()
            self.settings_window = SettingsFrame(self.oengus)

        #print('open_settings')
    def on_reload(self, *args):
        print('on_reload')
    #    self.parent.ReloadPath()
    #    self.parent.RenewCanvas()

    def on_refresh(self, *args):
        self.parent.sim.clear_caches()
    #    self.parent.RefreshTimeStep()
    #    self.parent.RenewCanvas()

    def rec_changed(self, *args):
        print('rec_changed')
        #if self.RecVar.get() == self.parent.MainParamDict['Recording']:
        #    pass
        #else:
        #    self.parent.MainParamDict['Recording'] = self.RecVar.get()
        #    if self.parent.MainParamDict['Recording'] == 1:
        #        self.parent.PrintFig()

    def loop_changed(self, *args):
        if self.loop_var.get() == self.oengus.MainParamDict['LoopPlayback']:
            pass
        else:
            self.oengus.MainParamDict['LoopPlayback'] = self.loop_var.get()
            self.param.loop = self.oengus.MainParamDict['LoopPlayback']
    def skip_left(self, e = None):
        self.param.set(self.param.value - self.oengus.MainParamDict['SkipSize'])

    def skip_right(self, e = None):
        self.param.set(self.param.value + self.oengus.MainParamDict['SkipSize'])

    def play_handler(self, e = None):
        if not self.play_pressed:
            # Set the value of play pressed to true, change the button name to
            # pause, turn off clear_fig, and start the play loop.
            self.play_pressed = True
            self.playB.config(text='Pause')

            self.after(int(self.oengus.MainParamDict['WaitTime']*1E3), self.blink)
        else:
            #self.parent.resizable(1,1)
            # pause the play loop, turn clear fig back on, and set the button name back to play
            self.play_pressed = False
            #try:
            #    self.MovieFrame.destroy()
            #except AttributeError:
            #    pass
            #self.parent.RenewCanvas()
#            self.parent.MainParamDict['ClearFig'] = True
            self.playB.config(text='Play')


    def open_measures(self):
        print('open_measures')
        """
        if self.parent.measure_window is None:
            self.parent.measure_window = MeasureFrame(self.parent)
        else:
            self.parent.measure_window.destroy()
            self.parent.measure_window = MeasureFrame(self.parent)
        """

    def blink(self):
        if self.play_pressed:
            # First check to see if the timestep can get larger
            if self.param.value == self.param.maximum and not self.oengus.MainParamDict['LoopPlayback']:
                # push pause button
                self.PlayHandler()

            # otherwise skip right by size skip size
            else:
                self.param.set(self.param.value + self.oengus.MainParamDict['SkipSize'])

            # start loopin'
            self.after(int(self.oengus.MainParamDict['WaitTime']*1E3), self.blink)

    def text_callback(self):
        try:
            #make sure the user types in a int
            if int(self.tstep.get()) != self.param.value:
                self.param.set(int(float(self.tstep.get())))
        except ValueError:
            #if they type in random stuff, just set it ot the param value
            self.tstep.set(str(self.param.value))

    def scale_handler(self, e):
        # if changing the scale will change the value of the parameter, do so
        try:
            if int(self.tstep.get()) != int(self.slider.get()):
                self.tstep.set(str(int(self.slider.get())))
        except ValueError:
            #if they type in random stuff, just set it ot the param value
            self.tstep.set(str(int(self.slider.get())))

    def update_value(self, *args):
        if int(self.slider.get()) != self.param.value:
            self.param.set(int(self.slider.get()))
    def set_knob(self, value):
        self.slider.config(to =self.param.maximum)
        self.slider.set(value)
        self.tstep.set(str(value))
