from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QComboBox, QCheckBox, QTabWidget, QSpinBox,
                             QRadioButton, QDialog)
from PyQt5.QtCore import Qt, QTimer
from new_cmaps import cmap_to_hex
import new_cmaps
from functools import partial


class SettingsFrame(QDialog):
    def __init__(self, main_app):
        super().__init__(main_app)
        self.setModal(0)
        self.main_app = main_app
        self.oengus = self.main_app.oengus
        # self.main_params = self.oengus.MainParamDict
        self.setWindowTitle('Settings')
        self.build_ui()
        self.ignoreChange = False
        self.show()

    def closeEvent(self, event):
        self.main_app.playbackbar.settings_window = None

    def update_slice_info(self):
        self.sim_tab.update_slice_widgets()

    def build_ui(self):
        layout = QGridLayout()
        tabwidget = QTabWidget()
        self.settings_tab = SettingsTab(self.main_app)
        self.sim_tab = SimTab(self.main_app)
        tabwidget.addTab(self.settings_tab, "General Settings")
        tabwidget.addTab(self.sim_tab, "Sim Settings")
        layout.addWidget(tabwidget, 0, 0)
        self.setLayout(layout)

    def AverageChanged(self, *args):
        if self.main_params['Average1D'] != self.Average1DVar.get():
            self.main_params['Average1D'] = self.Average1DVar.get()
            self.oengus.draw_output()

    def xRelChanged(self, *args):
        pass
        # If the shared axes are changed, the whole plot must be redrawn
        # if self.xRelVar.get() == self.main_params['xLimsRelative']:
        #    pass
        # else:
        #    self.main_params['xLimsRelative'] = self.xRelVar.get()
        #    self.parent.RenewCanvas()

    def CheckIfStrideChanged(self):
        to_reload = False
        try:
            # make sure the user types in a int
            if int(self.PrtlStrideVar.get()) <= 0:
                self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
            if int(self.PrtlStrideVar.get()) != self.main_params['PrtlStride']:
                self.main_params['PrtlStride'] = int(self.PrtlStrideVar.get())
                for sim in self.oengus.sims:
                    if len(sim) > 0:
                        sim.xtra_stride = self.main_params['PrtlStride']
                self.oengus.draw_output()
        except ValueError:
            # if they type in random stuff, just set it to the param value
            self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
        return to_reload


class SettingsTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.oengus = main_app.oengus
        self.main_params = self.oengus.MainParamDict
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        ###
        #
        # Upper left rows
        #
        # | tstep     | 10   |
        # | wait_time | 0.01 |
        # | cmap |  ComboBox |
        # | DivCmap | Combo  |
        # | col       | Spin |
        # | row       | Spin |
        #
        ###

        # Row 1
        upp_grid = QGridLayout()
        upp_left_min_width = 150
        upp_left_max_width = 200

        upp_grid.addWidget(QLabel('Skip Size:'), 0, 0)
        self.tstep = QLineEdit(self)
        self.tstep.setMaximumWidth(upp_left_max_width)
        self.tstep.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tstep.setMinimumWidth(upp_left_min_width)
        self.tstep.setText(str(self.main_params['SkipSize']))
        self.tstep.returnPressed.connect(self.skip_size_changed)
        self.tstep.clearFocus()
        upp_grid.addWidget(self.tstep, 0, 1)

        # Row 2
        upp_grid.addWidget(QLabel('Playback Wait Time:'), 1, 0)
        self.wait_time = QLineEdit(self)
        self.wait_time.setMaximumWidth(upp_left_max_width)
        self.wait_time.setMinimumWidth(upp_left_min_width)
        self.wait_time.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.wait_time.setText(str(self.main_params['WaitTime']))
        self.wait_time.returnPressed.connect(self.wait_time_changed)
        upp_grid.addWidget(self.wait_time, 1, 1)

        # Row 3
        upp_grid.addWidget(QLabel('Color map:'), 2, 0)
        self.cmap_combo = QComboBox(self)
        for cmap in new_cmaps.sequential:
            self.cmap_combo.addItem(cmap)
        self.cmap_combo.setCurrentText(self.main_params['ColorMap'])
        self.cmap_combo.currentIndexChanged.connect(self.cmap_changed)
        self.cmap_combo.setMaximumWidth(upp_left_max_width)
        self.cmap_combo.setMinimumWidth(upp_left_min_width)
        upp_grid.addWidget(self.cmap_combo, 2, 1)

        # Row 4
        upp_grid.addWidget(QLabel('Diverging cmap:'), 3, 0)
        self.div_cmap_combo = QComboBox(self)
        for cmap in new_cmaps.diverging:
            self.div_cmap_combo.addItem(cmap)
        self.div_cmap_combo.setCurrentText(self.main_params['DivColorMap'])
        self.div_cmap_combo.currentIndexChanged.connect(self.div_cmap_changed)
        self.div_cmap_combo.setMaximumWidth(upp_left_max_width)
        self.div_cmap_combo.setMinimumWidth(upp_left_min_width)
        upp_grid.addWidget(self.div_cmap_combo, 3, 1)

        # Row 5
        upp_grid.addWidget(QLabel('# of Columns:'), 4, 0)
        self.col_sb = QSpinBox(self)
        self.col_sb.setRange(1, self.main_params['MaxCols'])
        self.col_sb.setValue(self.main_params['NumOfCols'])

        self.col_sb.valueChanged.connect(self.col_changed)
        self.col_sb.setMaximumWidth(upp_left_max_width)
        self.col_sb.setMinimumWidth(upp_left_min_width)
        upp_grid.addWidget(self.col_sb, 4, 1)

        # Row 6
        upp_grid.addWidget(QLabel('# of rows:'), 5, 0)
        self.row_sb = QSpinBox(self)
        self.row_sb.setRange(1, self.main_params['MaxRows'])
        self.row_sb.setValue(self.main_params['NumOfRows'])

        self.row_sb.valueChanged.connect(self.row_changed)
        self.row_sb.setMaximumWidth(upp_left_max_width)
        self.row_sb.setMinimumWidth(upp_left_min_width)
        upp_grid.addWidget(self.row_sb, 5, 1)

        ###
        #
        # Upper Right radio
        #  Link Axes
        # | | None
        # | | All spatial
        # | | All fields
        # | cmap |  ComboBox |
        # | DivCmap | Combo  |
        # | col       | Spin |
        # | row       | Spin |
        #
        ###

        upp_grid.addWidget(QLabel('Share Spatial Axes:'), 0, 2)
        radiobutton = QRadioButton("None")
        if self.main_params['LinkSpatial'] == 0:
            radiobutton.setChecked(True)
        radiobutton.shared_axes = 0
        radiobutton.toggled.connect(self.radio_clicked)
        upp_grid.addWidget(radiobutton, 1, 2)

        radiobutton = QRadioButton("All Spatial")
        if self.main_params['LinkSpatial'] == 1:
            radiobutton.setChecked(True)

        radiobutton.shared_axes = 1
        radiobutton.toggled.connect(self.radio_clicked)
        upp_grid.addWidget(radiobutton, 2, 2)

        radiobutton = QRadioButton("All Fields")
        if self.main_params['LinkSpatial'] == 2:
            radiobutton.setChecked(True)
        radiobutton.shared_axes = 2
        radiobutton.toggled.connect(self.radio_clicked)
        upp_grid.addWidget(radiobutton, 3, 2)

        main_layout.addLayout(upp_grid)

        ###
        #
        # add layout for limits
        #
        #                 Min     Max
        # |x| set xlim |       |       |
        # |x| set ylim |       |       |
        #
        ###

        mid = QGridLayout()
        mid.addWidget(QLabel("Min"), 0, 1)
        mid.addWidget(QLabel("Max"), 0, 2)
        self.xlims_cb = QCheckBox("Set xlims")
        self.xlims_cb.setChecked(self.main_params['SetxLim'])
        self.xlims_cb.stateChanged.connect(self.xlims_changed)
        mid.addWidget(self.xlims_cb, 1, 0)

        self.xleft = QLineEdit(self)
        self.xleft.setMaximumWidth(upp_left_max_width - 80)
        self.xleft.setMinimumWidth(upp_left_min_width - 80)
        self.xleft.setText(str(self.main_params['xLeft']))
        self.xleft.returnPressed.connect(self.check_if_limval_changed)
        mid.addWidget(self.xleft, 1, 1)

        self.xright = QLineEdit(self)
        self.xright.setMaximumWidth(upp_left_max_width - 80)
        self.xright.setMinimumWidth(upp_left_min_width - 80)
        self.xright.setText(str(self.main_params['xRight']))
        self.xright.returnPressed.connect(self.check_if_limval_changed)
        mid.addWidget(self.xright, 1, 2)

        self.ylims_cb = QCheckBox("Set ylims")
        self.ylims_cb.setChecked(self.main_params['SetyLim'])
        self.ylims_cb.stateChanged.connect(self.ylims_changed)
        mid.addWidget(self.ylims_cb, 2, 0)

        self.ybottom = QLineEdit(self)
        self.ybottom.setMaximumWidth(upp_left_max_width - 80)
        self.ybottom.setMinimumWidth(upp_left_min_width - 80)
        self.ybottom.setText(str(self.main_params['yBottom']))
        self.ybottom.returnPressed.connect(self.check_if_limval_changed)
        mid.addWidget(self.ybottom, 2, 1)

        self.ytop = QLineEdit(self)
        self.ytop.setMaximumWidth(upp_left_max_width - 80)
        self.ytop.setMinimumWidth(upp_left_min_width - 80)
        self.ytop.setText(str(self.main_params['yTop']))
        self.ytop.returnPressed.connect(self.check_if_limval_changed)
        mid.addWidget(self.ytop, 2, 2)
        main_layout.addLayout(mid)

        ##
        #
        # bottom checkpanel
        #
        # |x| show title |x| aspect = 1 |x| horizontal Cbars
        #
        ##

        cbs = [
            ('show title', 'ShowTitle'),
            ('aspect = 1', 'ImageAspect'),
            ('Horizontal cbars', 'HorizontalCbars')]
        row = QHBoxLayout()
        for i, tup in enumerate(cbs):
            cb = QCheckBox(tup[0])
            cb.param_name = tup[1]
            cb.setChecked(self.main_params[tup[1]])
            cb.stateChanged.connect(self.cb_handler)
            row.addWidget(cb)
        main_layout.addLayout(row)

    def skip_size_changed(self):
        # Note here that Tkinter passes an event object to SkipSizeChange()
        try:
            self.main_params['SkipSize'] = int(self.tstep.text())
        except ValueError:
            self.skipSize.setText(self.main_params['SkipSize'])

    def wait_time_changed(self, *args):
        # Note here that Tkinter passes an event object to onselect()
        try:
            self.main_params['WaitTime'] = float(self.wait_time.text())
        except ValueError:
            self.wait_time.setText(self.main_params['WaitTime'])

    def cmap_changed(self):
        if self.cmap_combo.currentText() == self.main_params['ColorMap']:
            pass
        else:
            self.main_params['ColorMap'] = self.cmap_combo.currentText()
            cmaps_with_green = self.oengus.MainParamDict['cmaps_with_green']
            if self.main_params['ColorMap'] in cmaps_with_green:

                self.oengus.MainParamDict['ion_color'] = cmap_to_hex(
                    0.55, 'plasma')
                self.oengus.MainParamDict['electron_color'] = cmap_to_hex(
                    0.8, 'plasma')

                self.oengus.MainParamDict['ion_fit_color'] = 'r'
                self.oengus.MainParamDict['electron_fit_color'] = 'yellow'

            else:
                self.oengus.MainParamDict['ion_color'] = cmap_to_hex(
                    0.45, 'viridis')
                self.oengus.MainParamDict['electron_color'] = cmap_to_hex(
                    0.75, 'viridis')

                self.oengus.MainParamDict['ion_fit_color'] = 'mediumturquoise'
                self.oengus.MainParamDict['electron_fit_color'] = 'lime'

            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def div_cmap_changed(self, *args):
        # Note here that Tkinter passes an event object to onselect()
        div_cmap_name = self.div_cmap_combo.currentText()
        if div_cmap_name == self.main_params['DivColorMap']:
            pass
        else:
            self.main_params['DivColorMap'] = div_cmap_name
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def col_changed(self):
        self.main_params['NumOfCols'] = int(self.col_sb.value())
        self.clean_up_pop_ups()
        self.oengus.figure.clf()
        self.oengus.create_graphs()
        self.oengus.canvas.draw()

    def row_changed(self):
        self.main_params['NumOfRows'] = int(self.row_sb.value())
        self.clean_up_pop_ups()
        self.oengus.figure.clf()
        self.oengus.create_graphs()
        self.oengus.canvas.draw()

    def clean_up_pop_ups(self):
        for i in range(self.main_params['MaxRows']):
            for j in range(self.main_params['MaxCols']):
                if i >= self.main_params['NumOfRows']:
                    if f'{i,j}' in self.main_app.popups_dict:
                        if self.main_app.popups_dict[f'{i,j}'] is not None:
                            self.main_app.popups_dict[f'{i,j}'].deleteLater()
                elif j >= self.main_params['NumOfCols']:
                    if f'{i,j}' in self.main_app.popups_dict:
                        if self.main_app.popups_dict[f'{i,j}'] is not None:
                            self.main_app.popups_dict[f'{i,j}'].deleteLater()

    def radio_clicked(self):
        # If the shared axes are changed, we have to call the link
        # handler on every subplot
        radioButton = self.sender()
        if radioButton.isChecked():
            self.oengus.MainParamDict['LinkSpatial'] = radioButton.shared_axes
            for i in range(self.oengus.MainParamDict['NumOfRows']):
                for j in range(self.oengus.MainParamDict['NumOfCols']):
                    self.oengus.SubPlotList[i][j].link_handler()
                    # self.oengus.SubPlotList[i][j].save_axes_pos()
                    self.oengus.SubPlotList[i][j].refresh()
                    # self.oengus.SubPlotList[i][j].load_axes_pos()
            self.oengus.canvas.draw()

    def xlims_changed(self):
        self.main_params['SetxLim'] = self.xlims_cb.isChecked()
        self.oengus.draw_output()

    def ylims_changed(self):
        self.main_params['SetyLim'] = self.ylims_cb.isChecked()
        self.oengus.draw_output()

    def check_if_limval_changed(self):
        to_reload = False
        tmplist = [self.xleft, self.xright, self.ybottom, self.ytop]
        limkeys = ['xLeft', 'xRight', 'yBottom', 'yTop']
        setKeys = ['SetxLim', 'SetyLim']
        for j in range(len(tmplist)):
            setlims = self.main_params[setKeys[j//2]]
            tmpkey = limkeys[j]

            try:
                # make sure the user types in a a number and
                # that it has changed.
                user_num = float(tmplist[j].text())
                if abs(user_num - self.main_params[tmpkey]) > 1E-4:
                    self.main_params[tmpkey] = user_num
                    to_reload += setlims

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                tmplist[j].setText(str(self.main_params[tmpkey]))
        return to_reload

    def cb_handler(self):
        cb = self.sender()
        if cb.param_name == 'ImageAspect':
            self.main_params['ImageAspect'] = cb.isChecked()
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

        if cb.param_name == 'ShowTitle':
            self.main_params['ShowTitle'] = cb.isChecked()
            if not self.main_params['ShowTitle']:
                self.oengus.figure.suptitle('')
            else:
                self.oengus.make_title()

            self.oengus.canvas.draw()

        if cb.param_name == 'HorizontalCbars':
            if cb.isChecked():
                self.oengus.axes_extent = self.main_params['HAxesExtent']
                self.oengus.cbar_extent = self.main_params['HCbarExtent']
                self.oengus.SubPlotParams = self.main_params['HSubPlotParams']

            else:
                self.oengus.axes_extent = self.main_params['VAxesExtent']
                self.oengus.cbar_extent = self.main_params['VCbarExtent']
                self.oengus.SubPlotParams = self.main_params['VSubPlotParams']
            self.main_params['HorizontalCbars'] = cb.isChecked()
            self.oengus.figure.subplots_adjust(**self.oengus.SubPlotParams)
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()


class SimTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.oengus = main_app.oengus
        self.main_params = self.oengus.MainParamDict
        self.sim_selected = self.oengus.sims[0]
        self.build_ui()

    def build_ui(self):
        min_width = 150
        max_width = 200

        layout = QGridLayout()
        self.setLayout(layout)

        ####
        #
        # Build up the sim settings tab
        #
        #  Choose Sim: | ComboBox |
        #  Choose shock finder: | ComboBox |
        #
        ####
        layout.addWidget(QLabel('Choose sim'), 0, 0)
        self.sim_combo = QComboBox(self)
        self.update_sim_list()
        self.sim_combo.currentIndexChanged.connect(self.sim_selection_changed)
        layout.addWidget(self.sim_combo, 0, 1)

        layout.addWidget(QLabel('Choose Shock Finder'), 1, 0)
        self.shock_combo = QComboBox(self)
        self.update_shock_opts()
        self.shock_combo.currentIndexChanged.connect(self.shock_finder_changed)
        layout.addWidget(self.shock_combo, 1, 1)

        ####
        #
        #  prtl stride:
        #  | QLineEdit | | x | average 1D |
        #
        ####

        sim_ind = self.sim_selected.sim_num
        sim_params = self.main_params['sim_params'][sim_ind]

        layout.addWidget(QLabel('Prtl Stride'), 2, 0)

        self.prtl_stride_edit = QLineEdit(self)
        self.prtl_stride_edit.setText(str(sim_params['PrtlStride']))
        self.prtl_stride_edit.setMaximumWidth(max_width)
        self.prtl_stride_edit.setMinimumWidth(min_width)
        self.prtl_stride_edit.returnPressed.connect(self.stride_changed)
        layout.addWidget(self.prtl_stride_edit, 2, 1)
        self.average1D_cb = QCheckBox("Average1D")
        self.average1D_cb.setChecked(sim_params['Average1D'])
        self.average1D_cb.stateChanged.connect(self.avg_changed)

        layout.addWidget(self.average1D_cb, 3, 0)



        # radio buttons to choose plane.
        row = QHBoxLayout()
        row.addWidget(QLabel('Choose 2D-plane:'))

        self.slice_radio_btns = []
        radiobutton = QRadioButton("x-y")
        radiobutton.plane = 0
        radiobutton.toggled.connect(self.radio_clicked)
        self.slice_radio_btns.append(radiobutton)
        row.addWidget(radiobutton)

        radiobutton = QRadioButton("x-z")
        radiobutton.plane = 1
        radiobutton.toggled.connect(self.radio_clicked)
        self.slice_radio_btns.append(radiobutton)

        row.addWidget(radiobutton)

        radiobutton = QRadioButton("y-z")
        radiobutton.plane = 2
        radiobutton.toggled.connect(self.radio_clicked)
        self.slice_radio_btns.append(radiobutton)

        row.addWidget(radiobutton)
        layout.addLayout(row, 4, 0, 1, 2)

        # Now do the sliders

        self.sliders_dict = {}
        for i, ax in enumerate(['x', 'y', 'z']):
            row = QHBoxLayout()
            sld_obj = {}
            sld_obj['label'] = QLabel(self)
            #sld_obj['edit'] = QLineEdit(self)
            #sld_obj['edit'].setMaximumWidth(55)
            #sld_obj['edit'].setMinimumWidth(30)
            #self.edit.setText(str(self.param.value))
            #sld_obj['edit'].clearFocus()
            # box to enter time.
            sld_obj['sld'] = QSlider(Qt.Horizontal, self)
            sld_obj['sld'].ax = ax
            # update the text box whenever sld is change
            sld_obj['sld'].valueChanged.connect(self.scale_handler)
            # only update the plot when the user releases the mouse
            sld_obj['sld'].mouseReleaseEvent = partial(self.update_slice_val, ax)

            # self.sld.setRange(self.param.minimum, self.param.maximum)
            sld_obj['sld'].setFocusPolicy(Qt.NoFocus)
            sld_obj['sld'].setPageStep(1)

            row.addWidget(QLabel(f'{ax}-slice'))
            row.addWidget(sld_obj['sld'])
            row.addWidget(sld_obj['label'])
            self.sliders_dict[ax] = sld_obj

            layout.addLayout(row, 5 + i, 0, 1, 2)

        self.update_slice_widgets()

    def scale_handler(self, e):
        # if changing the scale will change the value of the parameter, do so
        sld = self.sender()
        ax = self.sim_selected.get_data(
            data_class='axes',
            attribute=sld.ax)['data']

        self.sliders_dict[sld.ax]['label'].setText(
            f'{round(ax[int(sld.value())], 2)}'
        )

    def update_slice_val(self, ax_name, e):
        sim_ind = self.sim_selected.sim_num
        sim_params = self.main_params['sim_params'][sim_ind]

        sld = self.sliders_dict[ax_name]['sld']
        ax = self.sim_selected.get_data(
            data_class='axes',
            attribute=ax_name)['data']
        next_sld_val = float(sld.value())/(len(ax)-1.0)
        if next_sld_val != sim_params[f'{ax_name}Slice']:
            sim_params[f'{ax_name}Slice'] = next_sld_val
            if not sim_params['Average1D']:
                for i in range(self.oengus.MainParamDict['NumOfRows']):
                    for j in range(self.oengus.MainParamDict['NumOfCols']):
                        self.oengus.SubPlotList[i][j].save_axes_pos()
                        self.oengus.SubPlotList[i][j].refresh()
                        self.oengus.SubPlotList[i][j].load_axes_pos()
                self.oengus.canvas.draw()

    def update_slice_widgets(self):
        sim_ind = self.sim_selected.sim_num
        sim_params = self.main_params['sim_params'][sim_ind]

        for btn in self.slice_radio_btns:
            btn.setChecked(btn.plane == sim_params['2DSlicePlane'])

        sim_sizes = self.sim_selected.get_domain_size()
        x_ax = self.sim_selected.get_data(
            data_class='axes',
            attribute='x')['data']
        y_ax = self.sim_selected.get_data(
            data_class='axes',
            attribute='y')['data']
        z_ax = self.sim_selected.get_data(
            data_class='axes',
            attribute='z')['data']

        self.slice_radio_btns[1].setEnabled(len(z_ax) > 1)
        self.slice_radio_btns[2].setEnabled( # False)
            (len(y_ax) > 1) and (len(z_ax) > 1))

        # enable or disable sliders
        # for key in ['edit', 'sld']:
        self.sliders_dict['x']['sld'].setEnabled(
            sim_params['2DSlicePlane'] == 2
        )

        self.sliders_dict['y']['sld'].setEnabled(
            (sim_params['2DSlicePlane'] != 2) and
            (len(y_ax) > 1)
        )

        self.sliders_dict['z']['sld'].setEnabled(
            (sim_params['2DSlicePlane'] != 2) and
            (len(z_ax) > 1)
        )
        self.update_slider_vals()

    def update_slider_vals(self):
        for key in ['x', 'y', 'z']:
            ax = self.sim_selected.get_data(
                data_class='axes',
                attribute=key)['data']
            if len(ax) > 1:
                self.sliders_dict[key]['sld'].setRange(0, len(ax)-1)

                self.sliders_dict[key]['sld'].setValue(
                    self.oengus.calc_slices(
                        key, self.sim_selected
                    )
                )
    def radio_clicked(self):
        # If the shared axes are changed, we have to call the link
        # handler on every subplot
        radioButton = self.sender()
        sim_ind = self.sim_selected.sim_num
        sim_params = self.main_params['sim_params'][sim_ind]

        if radioButton.isChecked():
            if sim_params['2DSlicePlane'] != radioButton.plane:
                 sim_params['2DSlicePlane'] = radioButton.plane
                 self.oengus.figure.clf()
                 self.oengus.create_graphs()
                 self.oengus.canvas.draw()

    def avg_changed(self):
        ind = self.sim_selected.sim_num
        sim_params = self.main_params['sim_params'][ind]

        if sim_params['Average1D'] != self.average1D_cb.isChecked():
            sim_params['Average1D'] = self.average1D_cb.isChecked()
            for i in range(self.oengus.MainParamDict['NumOfRows']):
                for j in range(self.oengus.MainParamDict['NumOfCols']):
                    self.oengus.SubPlotList[i][j].save_axes_pos()
                    self.oengus.SubPlotList[i][j].refresh()
                    self.oengus.SubPlotList[i][j].load_axes_pos()
            self.oengus.canvas.draw()

    def stride_changed(self):
        # Note here that Tkinter passes an event object to SkipSizeChange()
        if not self.ignoreChange:
            ind = self.sim_selected.sim_num
            sim_params = self.main_params['sim_params'][ind]
            try:
                sim_params['PrtlStride'] = int(self.prtl_stride_edit.text())
                self.sim_selected.xtra_stride = sim_params['PrtlStride']
                for i in range(self.oengus.MainParamDict['NumOfRows']):
                    for j in range(self.oengus.MainParamDict['NumOfCols']):
                        self.oengus.SubPlotList[i][j].save_axes_pos()
                        self.oengus.SubPlotList[i][j].refresh()
                        self.oengus.SubPlotList[i][j].load_axes_pos()
                self.oengus.canvas.draw()
            except ValueError:
                self.prtl_stride_edit.setText(str(sim_params['PrtlStride']))

    def update_sim_list(self):
        self.ignoreChange = True
        self.sim_combo.clear()
        for name in self.oengus.sim_names:
            self.sim_combo.addItem(name)
        index = self.sim_combo.findText(self.sim_selected.name)
        if index >= 0:
            self.sim_combo.setCurrentIndex(index)
        self.ignoreChange = False

    def sim_selection_changed(self):
        if not self.ignoreChange:
            if self.sim_combo.currentText() != self.sim_selected.name:
                try:
                    ind = self.oengus.sim_names.index(
                        self.sim_combo.currentText())
                except ValueError:
                    ind = 0

                self.sim_selected = self.oengus.sims[ind]
                sim_params = self.oengus.MainParamDict['sim_params'][ind]
                self.prtl_stride_edit.setText(str(sim_params['PrtlStride']))
                self.average1D_cb.setChecked(sim_params['Average1D'])
                self.update_shock_opts()
                self.update_slice_widgets()

    def update_shock_opts(self):
        self.ignoreChange = True
        self.shock_combo.clear()

        avail_opts = self.sim_selected.get_available_quantities()
        for method_name in avail_opts['shock_finders']:
            self.shock_combo.addItem(method_name)
        sim_params = self.oengus.MainParamDict[
            'sim_params'][self.sim_selected.sim_num]
        index = self.shock_combo.findText(sim_params['shock_method'])
        self.ignoreChange = False
        if index >= 0:
            self.shock_combo.setCurrentIndex(index)
        else:
            self.shock_combo.setCurrentIndex(0)

    def shock_finder_changed(self, *args):
        if not self.ignoreChange:
            combo_name = self.shock_combo.currentText()
            sim_params = self.oengus.MainParamDict[
                'sim_params'][self.sim_selected.sim_num]
            if sim_params['shock_method'] != combo_name:
                sim_params['shock_method'] = combo_name
                # self.shock_finder_var.set(self.sim_selected.shock_finder_name)
                # update shock lines
                for i in range(self.oengus.MainParamDict['NumOfRows']):
                    for j in range(self.oengus.MainParamDict['NumOfCols']):
                        self.oengus.SubPlotList[i][j].save_axes_pos()
                        self.oengus.SubPlotList[i][j].refresh()
                        self.oengus.SubPlotList[i][j].load_axes_pos()
                self.oengus.canvas.draw()
