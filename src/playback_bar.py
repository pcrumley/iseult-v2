from PyQt5.QtWidgets import (QWidget, QSlider, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton,
                             QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from main_settings_window import SettingsFrame
import numpy as np
import time


class playbackBar(QWidget):

    """
    A Class that will handle the time-stepping in Iseult, and has the
    following, a step left button, a play/pause button, a step right button, a
    playbar, and a settings button.
    """

    def __init__(self, oengus, tstep_param):
        super().__init__()
        self.oengus = oengus
        # This param should be the time-step of the simulation
        self.param = tstep_param

        self._cur_sim = -1  # A way to hold the current simulation

        self._play_debouncer = -np.inf
        self.play_pressed = False
        self.settings_window = None
        self.ignoreChange = False

        self.initUI()

        # attach the parameter to the Playbackbar
        self.param.attach(self)

        # A hack to update the slider
        self._cur_sim = 0

    def initUI(self):

        hbox = QHBoxLayout()

        skip_left_btn = QPushButton(self)
        skip_left_btn.setText("<")
        skip_left_btn.clicked.connect(self.skip_left)

        self.play_btn = QPushButton(self)
        self.play_btn.setText("Play")
        self.play_btn.clicked.connect(self.play_handler)

        skip_right_btn = QPushButton(self)
        skip_right_btn.setText(">")
        skip_right_btn.clicked.connect(self.skip_right)

        self.sim_combo = QComboBox(self)
        self.update_sim_list()
        self.sim_combo.currentIndexChanged.connect(self.simChanged)

        # label for box to change time
        self.label = QLabel('n=', self)
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.label.setMinimumWidth(30)

        # A box to type in a frame num, linked to self.param
        self.edit = QLineEdit(self)
        self.edit.setMaximumWidth(55)
        self.edit.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.edit.setMinimumWidth(30)
        self.edit.setText(str(self.param.value))
        self.edit.returnPressed.connect(self.text_callback)
        self.edit.clearFocus()
        # box to enter time.
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setRange(self.param.minimum, self.param.maximum)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setPageStep(1)

        # update the text box whenever sld is change
        self.sld.valueChanged.connect(self.scale_handler)
        # only update the plot when the user releases the mouse
        self.sld.mouseReleaseEvent = self.update_value

        self.simChanged()

        self.loop_chk = QCheckBox(self)
        self.loop_chk.setText("loop")
        self.loop_chk.setChecked(self.oengus.MainParamDict['LoopPlayback'])
        self.loop_chk.stateChanged.connect(self.loop_changed)

        settings_btn = QPushButton(self)
        settings_btn.setText("Settings")
        settings_btn.clicked.connect(self.open_settings)

        reload_btn = QPushButton(self)
        reload_btn.setText("Reload")
        reload_btn.clicked.connect(self.on_reload)

        clear_btn = QPushButton(self)
        clear_btn.setText("Clear Cache")
        clear_btn.clicked.connect(self.on_refresh)

        ####
        #
        # Add all the objects to the hbox
        #
        ####

        hbox.addWidget(skip_left_btn)
        hbox.addWidget(self.play_btn)
        hbox.addWidget(skip_right_btn)

        hbox.addWidget(self.sim_combo)

        hbox.addWidget(self.label)
        hbox.addWidget(self.edit)
        hbox.addSpacing(5)
        hbox.addWidget(self.sld)
        hbox.addWidget(self.loop_chk)

        hbox.addWidget(settings_btn)
        hbox.addWidget(reload_btn)
        hbox.addWidget(clear_btn)

        hbox.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(30);
        self.setLayout(hbox)

        """
        # a measurement button that should lauch a window to take measurements.
        # self.measuresB = ttk.Button(
        #    self, text='FFT', command=self.open_measures)
        # self.measuresB.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        """

    def update_slider(self):
        self.param.set_max(len(self.oengus.sims[self._cur_sim]))
        self.sld.setRange(self.param.minimum, self.param.maximum)

    @property
    def cur_sim(self):
        return self._cur_sim

    @cur_sim.setter
    def cur_sim(self, val):
        self._cur_sim = val
        self.oengus.cur_sim = val
        self.update_slider()

    def update_sim_list(self):
        self.ignoreChange = True
        self.sim_combo.clear()
        for i in self.oengus.sims_shown:
            self.sim_combo.addItem(self.oengus.sims[i].name)
        index = self.sim_combo.findText(self.oengus.sims[self.cur_sim].name)
        self.ignoreChange = False
        if index >= 0:
            self.sim_combo.setCurrentIndex(index)
        else:
            self.sim_combo.setCurrentIndex(0)

    def simChanged(self):
        if not self.ignoreChange:
            if self.sim_combo.currentText() == self.oengus.sims[self.cur_sim].name:
                pass
            elif self.sim_combo.currentText() in self.oengus.sim_names:
                self.cur_sim = self.oengus.sim_names.index(self.sim_combo.currentText())
                self.oengus.cur_sim = self.cur_sim
        #else:
        #    self.update_sim_list()

    def on_reload(self):
        self.oengus.sims[self.cur_sim].refresh_directory()
        self.update_slider()

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsFrame(self.oengus)
            self.settings_window.show()
        else:
            #self.settings_window.destroy()
            self.settings_window.destroy()
            self.settings_window = SettingsFrame(self.oengus)
            self.settings_window.show()
            #self.settings_window = SettingsFrame(self.oengus)

    def on_refresh(self, *args):
        for sim in self.oengus.sims:
            sim.clear_caches()
        self.update_slider()
        self.oengus.draw_output()

    def loop_changed(self):
        self.oengus.MainParamDict['LoopPlayback'] = self.loop_chk.isChecked()
        self.param.loop = self.oengus.MainParamDict['LoopPlayback']

    def skip_left(self):
        self.param.set(
            self.param.value - self.oengus.MainParamDict['SkipSize'])

    def skip_right(self):
        self.param.set(
            self.param.value + self.oengus.MainParamDict['SkipSize'])

    def play_handler(self, e=None):
        tic = time.time()
        if tic - self._play_debouncer > .05:
            self._play_debouncer = tic
            if not self.play_pressed:
                # Set the value of play pressed to true, change the button name
                # to pause, turn off clear_fig, and start the play loop.
                self.play_pressed = True
                self.play_btn.setText('Pause')
                QTimer.singleShot(
                    int(self.oengus.MainParamDict['WaitTime']*1E3),
                    self.blink)
            else:
                # pause the play loop, turn clear fig back on,
                # and set the button name back to play
                self.play_pressed = False
                self.play_btn.setText('Play')

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
            QTimer.singleShot(
                int(self.oengus.MainParamDict['WaitTime']*1E3),
                self.blink)

    def text_callback(self):
        try:
            # make sure the user types in a int
            if int(self.edit.text()) != self.param.value:
                self.param.set(int(self.edit.text()))
        except ValueError:
            # if they type in random stuff, just set it ot the param value
            self.edit.setText(str(self.param.value))

    def scale_handler(self, e):
        # if changing the scale will change the value of the parameter, do so
        try:
            if int(self.edit.text()) != int(self.sld.value()):
                self.edit.setText(str(int(self.sld.value())))
        except ValueError:
            # if they type in random stuff, just set it to the param value
            self.edit.setText(str(int(self.sld.value())))

    def update_value(self, *args):
        if int(self.sld.value()) != self.param.value:
            self.param.set(int(self.sld.value()))

    def set_knob(self, value):
        self.sld.setValue(value)
        self.edit.setText(str(value))
