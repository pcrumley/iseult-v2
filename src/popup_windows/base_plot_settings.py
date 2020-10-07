from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QCheckBox

class iseultPlotSettings(QWidget):
    '''
    The base class that all of the subplots settings must be subclasses of.'''

    interpolation_methods = [
        'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
        'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
        'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def __init__(self, parent, loc):
        super().__init__()

        self.parent = parent
        self.oengus = parent.oengus
        self.loc = loc
        # self.main_params = self.oengus.MainParamDict

        self.subplot = self.oengus.SubPlotList[self.loc[0]][self.loc[1]]
        self.params = self.subplot.param_dict

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
            shock_loc = sim.get_shock_loc()
            if shock_loc['shock_loc'] < 0 or shock_loc['axis'] != 'x':
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
