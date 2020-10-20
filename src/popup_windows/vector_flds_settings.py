from PyQt5.QtWidgets import (QWidget, QGridLayout,
                             QLabel, QLineEdit,
                             QComboBox, QCheckBox)
import new_cmaps
from base_plot_settings import iseultPlotSettings


class VectorFieldsSettings(iseultPlotSettings):

    def __init__(self, parent, loc):
        super().__init__(parent, loc)
        self.ignoreChange = False

        self.build_ui()

    def build_ui(self):
        self.setWindowTitle(f'Vector Flds Plot {self.loc} Settings')
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
        layout.addWidget(self.sim_combo, 1, 1)

        layout.addWidget(QLabel('Choose Quantity:'), 3, 0)

        self.fld_combo = QComboBox(self)
        self.fld_combo.currentIndexChanged.connect(self.field_type_changed)
        self.update_fld_combo()
        layout.addWidget(self.fld_combo, 4, 0)

        ###
        #
        # Checkboxes. All stander see iseultPlotSettings
        #
        ###

        layout.addWidget(self.show_cbar_cb(), 7, 0)
        layout.addWidget(self.show_shock_cb(), 8, 1)
        layout.addWidget(self.ax_symmetric_cb('y'), 8, 0)
        layout.addWidget(self.show_labels_2d_cb(), 9, 1)
        layout.addWidget(self.is_2d_cb(), 7, 1)
        layout.addWidget(self.div_cmap_cb(), 9, 0)
        # layout.addWidget(self.asym_colorspace_cb(), 10, 0)

        ###
        #
        # Component CBs
        #
        ###
        self.field_cbs = []
        for i, component in enumerate(['x', 'y', 'z']):
            cb = QCheckBox(f'Show {component}')
            cb.param = f'show_{component}'
            cb.setChecked(self.params[cb.param])
            cb.stateChanged.connect(self.component_selector)
            self.field_cbs.append(cb)
            layout.addWidget(cb, 4 + i, 1)

        ###
        #
        # cnorm
        #
        ###

        layout.addWidget(QLabel('Choose Color Norm'), 6, 2)
        layout.addWidget(self.cnorm_QComboBox(), 6, 3)

        layout.addWidget(QLabel('gamma ='), 7, 2)
        layout.addWidget(self.gamma_QLineEdit(), 7, 3)

        layout.addWidget(QLabel('If cnorm is Pow =>'), 8, 2)
        layout.addWidget(QLabel('sign(data)*|data|**gamma'), 9, 3)

        self.v_min_cb = QCheckBox('Set flds min')
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

        self.v_max_cb = QCheckBox('Set flds max')
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

    def sim_changed(self):
        cur_sim_name = self.oengus.sim_names[self.params['sim_num']]
        if self.sim_combo.currentText() == cur_sim_name:
            pass
        else:
            self.params['sim_num'] = self.oengus.sim_names.index(
                self.sim_combo.currentText())
            self.update_fld_combo()

            self.parent.update_all_sim_lists()
            self.subplot.axis_info()
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.oengus.canvas.draw()

    def update_fld_combo(self):
        cur_sim = self.oengus.sims[self.params['sim_num']]
        avail_flds = cur_sim.get_available_quantities()['vec_flds']
        self.ignoreChange = True
        self.fld_combo.clear()
        for fld in avail_flds.keys():
            self.fld_combo.addItem(fld)
        self.fld_combo.setCurrentText(self.params['field_type'])
        self.ignoreChange = False

    def field_type_changed(self):
        if not self.ignoreChange:
            self.params['field_type'] = self.fld_combo.currentText()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()

            self.subplot.draw()
            self.parent.oengus.canvas.draw()

    def v_cb_handler(self):
        cb = self.sender()
        self.params[cb.param_key] = cb.isChecked()
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

    def quantityChanged(self, *args):
        if self.params['field_type'] == self.quantity.get():
            pass
        else:
            self.params['field_type'] = self.quantity.get()
            self.subplot.update_labels_and_colors()
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def twoD_handler(self):
        cb = self.sender()
        self.params['twoD'] = cb.isChecked()

        # Make sure only one dimension checked
        if self.params['twoD']:
            self.ignoreChange = True
            if self.params['show_x']:
                self.params['show_y'] = 0
                self.params['show_z'] = 0
            elif self.params['show_y']:
                self.params['show_z'] = 0
            for cb in self.field_cbs:
                cb.setChecked(self.params[cb.param])
            self.ignoreChange = False

        self.subplot.remove()
        self.subplot.build_axes()
        self.subplot.axis_info()
        self.subplot.draw()
        self.parent.oengus.canvas.draw()

    def component_selector(self):
        # First check if it is 2-D:
        if not self.ignoreChange:
            self.ignoreChange = True
            if self.params['twoD']:
                num_checked = sum([cb.isChecked() for cb in self.field_cbs])

                if num_checked == 0:
                    # All are zero, something must be selected for this plot
                    self.field_cbs[0].setChecked(True)

                if self.params['show_x'] != self.field_cbs[0].isChecked():
                    # set the other plot values to zero in the PlotParams
                    self.params['show_x'] = self.field_cbs[0].isChecked()
                    self.params['show_y'] = 0
                    self.params['show_z'] = 0
                    for cb in self.field_cbs:
                        cb.setChecked(self.params[cb.param])

                elif self.params['show_y'] != self.field_cbs[1].isChecked():
                    # set the other plot values to zero in the PlotParams
                    self.params['show_x'] = 0
                    self.params['show_z'] = 0
                    self.params['show_y'] = self.field_cbs[1].isChecked()
                    for cb in self.field_cbs:
                        cb.setChecked(self.params[cb.param])

                elif self.params['show_z'] != self.field_cbs[2].isChecked():
                    # set the other plot values to zero in the PlotParams
                    self.params['show_x'] = 0
                    self.params['show_y'] = 0
                    self.params['show_z'] = self.field_cbs[2].isChecked()
                    # Uncheck the boxes
                    for cb in self.field_cbs:
                        cb.setChecked(self.params[cb.param])

            else:
                if self.params['show_x'] != self.field_cbs[0].isChecked():
                    show_x = self.field_cbs[0].isChecked()
                    self.subplot.line_x[0].set_visible(show_x)
                    self.subplot.anx.set_visible(show_x)
                    self.params['show_x'] = show_x

                elif self.params['show_y'] != self.field_cbs[1].isChecked():
                    show_y = self.field_cbs[1].isChecked()
                    self.subplot.line_y[0].set_visible(show_y)
                    self.subplot.any.set_visible(show_y)
                    self.params['show_y'] = show_y

                elif self.params['show_z'] != self.field_cbs[2].isChecked():
                    show_z = self.field_cbs[2].isChecked()
                    self.subplot.line_z[0].set_visible(show_z)
                    self.subplot.anz.set_visible(show_z)
                    self.params['show_z'] = show_z
            self.ignoreChange = False
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def OnClosing(self):
        self.destroy()
