from PyQt5.QtWidgets import (QWidget, QGridLayout,
                             QLabel, QLineEdit,
                             QComboBox, QCheckBox)
import new_cmaps
from base_plot_settings import iseultPlotSettings


class phaseSettings(iseultPlotSettings):

    def __init__(self, parent, loc):
        super().__init__(parent, loc)
        self.ignoreChange = False

        self.build_ui()

    def build_ui(self):
        self.setWindowTitle(f'Phase Plot {self.loc} Settings')
        layout = QGridLayout()
        ###
        #
        #  Do everything in 1 qridlayout        #
        #
        ##

        layout.addWidget(QLabel('Choose Chart Type:'), 0, 0)
        layout.addWidget(self.chart_type_QComboBox(), 0, 1)

        layout.addWidget(QLabel('Interpolation Method:'), 0, 2)
        layout.addWidget(self.interpl_QComboBox(), 0, 3)

        layout.addWidget(QLabel('Simulation:'), 1, 0)
        self.sim_combo = QComboBox(self)
        for sim_name in self.oengus.sim_names:
            self.sim_combo.addItem(sim_name)
        self.sim_combo.setCurrentIndex(self.params['sim_num'])
        self.sim_combo.currentIndexChanged.connect(self.sim_changed)
        layout.addWidget(self.sim_combo, 2, 0)

        ###
        #
        # Particle quantities
        #
        ###

        layout.addWidget(QLabel('Choose Particle:'), 3, 0)

        self.prtl_combo = QComboBox(self)
        self.prtl_combo.currentIndexChanged.connect(self.prtl_type_changed)
        layout.addWidget(self.prtl_combo, 4, 0)

        layout.addWidget(QLabel('x_val:'), 5, 0)
        self.xval_combo = QComboBox(self)
        self.xval_combo.param_arg = 'x_val'
        self.xval_combo.currentIndexChanged.connect(self.prtl_attr_handler)
        layout.addWidget(self.xval_combo, 6, 0)

        layout.addWidget(QLabel('y_val:'), 5, 1)
        self.yval_combo = QComboBox(self)
        self.yval_combo.param_arg = 'y_val'
        self.yval_combo.currentIndexChanged.connect(self.prtl_attr_handler)
        layout.addWidget(self.yval_combo, 6, 1)

        self.update_prtl_combo()
        self.update_attr_combos()

        ###
        #
        # Check buttons
        #
        ###

        layout.addWidget(self.show_cbar_cb(), 7, 0)
        layout.addWidget(self.show_shock_cb(), 7, 1)
        layout.addWidget(self.ax_symmetric_cb('x'), 8, 0)
        layout.addWidget(self.ax_symmetric_cb('y'), 8, 1)
        cb = QCheckBox('Aspect = 1')
        cb.setChecked(self.params['aspect_one'])
        cb.stateChanged.connect(self.aspect_handler)
        layout.addWidget(cb, 9, 0)

        ###
        #
        # # of bins
        #
        ###

        # ybins
        layout.addWidget(QLabel('# of ybins'), 10, 0)
        self.edit_ybins = QLineEdit(self)
        self.edit_ybins.param_arg = 'y_bins'
        self.edit_ybins.setText(
            str(self.params[self.edit_ybins.param_arg]))
        self.edit_ybins.returnPressed.connect(self.bins_changed)
        layout.addWidget(self.edit_ybins, 10, 1)

        # xbins
        layout.addWidget(QLabel('# of xbins'), 11, 0)
        self.edit_xbins = QLineEdit(self)
        self.edit_xbins.param_arg = 'x_bins'
        self.edit_xbins.setText(
            str(self.params[self.edit_xbins.param_arg]))
        self.edit_xbins.returnPressed.connect(self.bins_changed)
        layout.addWidget(self.edit_xbins, 11, 1)

        self.v_min_cb = QCheckBox('Set log f min')
        self.v_min_cb.param_key = 'set_v_min'
        self.v_min_cb.setChecked(self.params['set_v_min'])
        self.v_min_cb.stateChanged.connect(self.v_cb_handler)
        layout.addWidget(self.v_min_cb, 3, 2)

        self.edit_vmin = QLineEdit(self)
        self.edit_vmin.param_arg = 'v_min'
        self.edit_vmin.setText(
            str(self.params['v_min']))
        self.edit_vmin.returnPressed.connect(self.lims_changed)
        layout.addWidget(self.edit_vmin, 3, 3)

        self.v_max_cb = QCheckBox('Set log f max')
        self.v_max_cb.param_key = 'set_v_max'
        self.v_max_cb.setChecked(self.params['set_v_max'])
        self.v_max_cb.stateChanged.connect(self.v_cb_handler)
        layout.addWidget(self.v_max_cb, 4, 2)

        self.edit_vmax = QLineEdit(self)
        self.edit_vmax.param_arg = 'v_max'
        self.edit_vmax.setText(
            str(self.params['v_max']))
        self.edit_vmax.returnPressed.connect(self.lims_changed)
        layout.addWidget(self.edit_vmax, 4, 3)

        self.setLayout(layout)

    def prtl_type_changed(self, *args):
        if not self.ignoreChange:
            if self.params['prtl_type'] != self.prtl_combo.currentText():
                self.params['prtl_type'] = self.prtl_combo.currentText()
                self.update_attr_combos()
                self.subplot.refresh()
                self.subplot.update_labels_and_colors()
                self.oengus.canvas.draw()

    def prtl_attr_handler(self):
        if not self.ignoreChange:
            sender = self.sender()
            if self.params[sender.param_arg] != sender.currentText():
                self.params[sender.param_arg] = sender.currentText()
                self.subplot.axis_info()
                self.subplot.refresh()
                self.subplot.update_labels_and_colors()
                self.oengus.canvas.draw()

    def sim_changed(self):
        cur_sim_name = self.oengus.sim_names[self.params['sim_num']]
        if self.sim_combo.currentText() == cur_sim_name:
            pass
        else:
            self.params['sim_num'] = self.oengus.sim_names.index(
                self.sim_combo.currentText())
            self.update_prtl_combo()
            self.update_attr_combos()

            self.parent.update_all_sim_lists()
            self.subplot.axis_info()
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.oengus.canvas.draw()

    def aspect_handler(self):
        sender = self.sender()
        self.params['aspect_one'] = sender.isChecked()
        if self.params['aspect_one']:
            self.subplot.axes.set_aspect('equal')
        else:
            self.subplot.axes.set_aspect('auto')
        self.oengus.canvas.draw()

    def v_cb_handler(self):
        cb = self.sender()
        self.params[cb.param_key] = cb.isChecked()
        self.subplot.save_axes_pos()
        self.subplot.refresh()
        self.subplot.load_axes_pos()
        self.oengus.canvas.draw()

    def bins_changed(self):
        to_reload = False
        line_edit = self.sender()
        try:
            #make sure the user types in a float
            user_num = int(line_edit.text())
            if user_num - int(self.params[line_edit.param_arg]) != 0:
                self.params[line_edit.param_arg] = user_num
                to_reload += True

        except ValueError:
            # if they type in random stuff, just set it ot the param value
            line_edit.setText(str(self.params[line_edit.param_arg]))

        if to_reload:
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.oengus.canvas.draw()

    def lims_changed(self):
        edit_list = [self.edit_vmin, self.edit_vmax]
        plot_param_List = ['v_min', 'v_max']
        cb_list = [self.v_min_cb, self.v_max_cb]
        to_reload = False
        for j in range(len(cb_list)):
            try:
                # make sure the user types in a number
                user_num = float(edit_list[j].text())
                if abs(user_num - self.params[plot_param_List[j]]) > 1E-4:
                    self.params[plot_param_List[j]] = user_num
                    to_reload += True * cb_list[j].isChecked()

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                edit_list[j].setText(str(self.params[plot_param_List[j]]))

        if to_reload:
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.oengus.canvas.draw()

    def update_prtl_combo(self):
        cur_sim = self.oengus.sims[self.params['sim_num']]
        avail_prtls = cur_sim.get_available_quantities()['prtls']
        self.ignoreChange = True
        self.prtl_combo.clear()
        for prtl in avail_prtls.keys():
            self.prtl_combo.addItem(prtl)
        self.prtl_combo.setCurrentText(self.params['prtl_type'])
        self.ignoreChange = False

    def update_attr_combos(self):
        cur_sim = self.oengus.sims[self.params['sim_num']]
        avail_prtls = cur_sim.get_available_quantities()['prtls']

        self.ignoreChange = True

        if self.params['prtl_type'] in avail_prtls.keys():
            avail_attrs = list(
                avail_prtls[self.params['prtl_type']]['attrs'].keys())
        else:
            avail_attrs = []

        if len(avail_attrs) > 0:

            self.xval_combo.clear()
            self.yval_combo.clear()
            for attr in avail_attrs:
                self.xval_combo.addItem(attr)
                self.yval_combo.addItem(attr)

            self.xval_combo.setCurrentText(self.params['x_val'])
            self.yval_combo.setCurrentText(self.params['y_val'])

            if not (self.xval_combo.currentText() in avail_attrs):
                self.params['x_val'] = avail_attrs[0]
                self.xval_combo.setCurrentText(avail_attrs[0])

            if not (self.yval_combo.currentText() in avail_attrs):
                self.params['y_val'] = avail_attrs[0]
                self.yval_combo.setCurrentText(avail_attrs[0])

        self.ignoreChange = False
