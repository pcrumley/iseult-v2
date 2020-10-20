from PyQt5.QtWidgets import (QWidget, QComboBox, QLabel, QCheckBox,
                             QLineEdit, QDialog)


class iseultPlotSettings(QDialog):
    '''
    The base class that all of the subplots settings must be subclasses of.'''

    interpolation_methods = [
        'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
        'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
        'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def __init__(self, parent, loc):
        super().__init__(parent)
        self.setModal(0)
        self.parent = parent
        self.oengus = parent.oengus
        self.loc = loc
        # self.main_params = self.oengus.MainParamDict

        self.subplot = self.oengus.SubPlotList[self.loc[0]][self.loc[1]]
        self.params = self.subplot.param_dict
        self.show()

    def closeEvent(self, event):
        self.parent.popups_dict[f'{self.loc[0],self.loc[1]}'] = None

    def interpl_QComboBox(self):
        combo = QComboBox(self)
        for method in self.interpolation_methods:
            combo.addItem(method)
        combo.setCurrentText(self.params['interpolation'])
        combo.currentIndexChanged.connect(self.interp_changed)
        return combo

    def interp_changed(self):
        ''' Only use me in the definition of interpl_combo'''
        combo = self.sender()
        if self.params['interpolation'] == combo.currentText():
            pass
        else:
            self.params['interpolation'] = combo.currentText()
            if self.params['twoD']:
                self.subplot.image.set_interpolation(combo.currentText())
                self.oengus.canvas.draw()

    def chart_type_QComboBox(self):
        combo = QComboBox(self)
        for chart_type in self.oengus.plot_types_dict.keys():
            combo.addItem(chart_type)
        combo.setCurrentText(self.subplot.chart_type)
        combo.currentIndexChanged.connect(self.chart_type_changed)
        return combo

    def chart_type_changed(self):
        combo = self.sender()
        self.parent.changePlotType(self.loc, combo.currentText())
        self.close()

    def show_cbar_cb(self):
        cb = QCheckBox('Show Color Bar')
        cb.setChecked(self.params['show_cbar'])
        cb.stateChanged.connect(self.cbar_handler)
        return cb

    def cbar_handler(self):
        sender = self.sender()
        self.params['show_cbar'] = sender.isChecked()
        if self.params['twoD']:
            self.subplot.axC.set_visible(self.params['show_cbar'])
            self.oengus.canvas.draw()

    def show_shock_cb(self):
        cb = QCheckBox('Show Shock')
        cb.setChecked(self.params['show_shock'])
        cb.stateChanged.connect(self.shock_handler)
        return cb

    def shock_handler(self):
        sender = self.sender()
        self.params['show_shock'] = sender.isChecked()
        if self.params['show_shock']:
            sim = self.oengus.sims[self.params['sim_num']]
            shock_loc = sim.get_data(
                data_class='shock_finders',
                shock_method=self.oengus.MainParamDict['shock_method']
            )
            if shock_loc['axis'] != 'x':
                print('Not Implemented Yet')
                self.ShockVar.set(False)

        self.subplot.shock_line.set_visible(self.params['show_shock'])
        self.subplot.save_axes_pos()
        self.subplot.refresh()
        self.subplot.load_axes_pos()
        self.oengus.canvas.draw()

    def ax_symmetric_cb(self, ax_name):
        cb = QCheckBox(f'symmetric {ax_name}-axis')
        cb.param_arg = f'symmetric_{ax_name}'
        cb.setChecked(self.params[cb.param_arg])
        cb.stateChanged.connect(self.sym_ax_handler)
        return cb

    def sym_ax_handler(self):
        cb = self.sender()
        self.params[cb.param_arg] = cb.isChecked()
        self.subplot.save_axes_pos()
        self.subplot.refresh()
        self.subplot.load_axes_pos()
        self.oengus.canvas.draw()

    def show_labels_2d_cb(self):
        cb = QCheckBox('Show Labels 2D')
        cb.setChecked(self.params['show_labels'])
        cb.stateChanged.connect(self.twoD_label_handler)
        return cb

    def twoD_label_handler(self):
        cb = self.sender()
        self.params['show_labels'] = cb.isChecked()
        if self.params['twoD']:
            self.subplot.an_2d.set_visible(cb.isChecked())
            self.parent.oengus.canvas.draw()

    def is_2d_cb(self):
        cb = QCheckBox('Show in 2D')
        cb.setChecked(self.params['twoD'])
        cb.stateChanged.connect(self.twoD_handler)
        return cb

    def twoD_handler(self):
        cb = self.sender()
        self.params['twoD'] = cb.isChecked()
        self.subplot.remove()
        self.subplot.build_axes()
        self.subplot.axis_info()
        self.subplot.draw()
        self.parent.oengus.canvas.draw()

    def div_cmap_cb(self):
        cb = QCheckBox('Use Diverging cmap')
        cb.setChecked(self.params['UseDivCmap'])
        cb.stateChanged.connect(self.div_cmap_handler)
        return cb

    def div_cmap_handler(self):
        cb = self.sender()
        self.params['UseDivCmap'] = cb.isChecked()
        if self.params['twoD']:
            self.subplot.save_axes_pos()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()
            self.subplot.draw()
            self.subplot.load_axes_pos()
            self.parent.oengus.canvas.draw()

    def asym_colorspace_cb(self):
        cb = QCheckBox('Asymmetric Color Space')
        cb.setChecked(self.params['stretch_colors'])
        cb.stateChanged.connect(self.cspace_handler)
        return cb

    def cspace_handler(self):
        cb = self.sender()
        self.params['stretch_colors'] = cb.isChecked()
        if self.params['twoD']:
            self.subplot.save_axes_pos()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()
            self.subplot.draw()
            self.subplot.load_axes_pos()
            self.parent.oengus.canvas.draw()

    ###
    #
    # cnorm
    #
    ###

    def cnorm_QComboBox(self):
        combo = QComboBox(self)
        for norm in ['Pow', 'Linear']:
            combo.addItem(norm)
        combo.setCurrentText(self.params['cnorm_type'])
        combo.currentIndexChanged.connect(self.cnorm_handler)
        return combo

    def cnorm_handler(self):
        ''' Only use me in the definition of interpl_combo'''
        combo = self.sender()
        self.params['cnorm_type'] = combo.currentText()
        if self.params['twoD']:
            self.subplot.save_axes_pos()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()
            self.subplot.draw()
            self.subplot.load_axes_pos()
            self.parent.oengus.canvas.draw()

    def gamma_QLineEdit(self):
        edit = QLineEdit(self)
        edit.setText(
            str(self.params['cpow_num']))
        edit.returnPressed.connect(self.gamma_changed)
        return edit

    def gamma_changed(self):
        edit = self.sender()
        try:
            user_num = float(edit.text())
            if abs(user_num - self.params['cpow_num']) > 1E-4:
                self.params['cpow_num'] = user_num
                if self.params['twoD'] and self.params['cnorm_type'] == 'Pow':
                    self.subplot.save_axes_pos()
                    self.subplot.remove()
                    self.subplot.build_axes()
                    self.subplot.axis_info()
                    self.subplot.draw()
                    self.subplot.load_axes_pos()

                    self.parent.oengus.canvas.draw()
        except ValueError:
            # if they type in random stuff, just set it ot the param value
            edit.setText(str(self.params['cpow_num']))
