from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QComboBox, QCheckBox, QTabWidget, QSpinBox,
                             QRadioButton)
from PyQt5.QtCore import Qt, QTimer
import new_cmaps
from base_plot_settings import iseultPlotSettings


class ScalarFieldsSettings(iseultPlotSettings):

    def __init__(self, parent, loc):
        super().__init__(parent, loc)
        self.ignoreChange = False

        self.build_ui()

    def build_ui(self):
        self.setWindowTitle(f'Scalar Flds Plot {self.loc} Settings')

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

        layout.addWidget(QLabel('Choose Quantity:'), 3, 0)

        self.fld_combo = QComboBox(self)
        self.fld_combo.currentIndexChanged.connect(self.fld_type_changed)
        self.update_fld_combo()
        layout.addWidget(self.fld_combo, 4, 0)

        """
        # Create a var to track whether or not to plot in 2-D
        self.TwoDVar = Tk.IntVar(self)
        self.TwoDVar.set(self.params['twoD'])
        ttk.Checkbutton(
            frm, text="Show in 2-D",
            variable=self.TwoDVar,
            command=self.Change2d).grid(
                row=1, column=2,
                sticky=Tk.W)
        # the Radiobox Control to choose the Field Type
        self.quantity = Tk.StringVar(self)
        self.quantity.set(self.params['flds_type'])
        self.quantity.trace('w', self.quantityChanged)

        ttk.Label(
            frm, text="Choose Quantity:").grid(
                row=2, sticky=Tk.W)
        cur_sim = self.parent.oengus.sims[self.params['sim_num']]
        quantChooser = ttk.OptionMenu(
            frm, self.quantity,
            self.params['flds_type'],
            *tuple(cur_sim.get_available_quantities()['scalar_flds'].keys()))
        quantChooser.grid(
            row=3, column=0,
            sticky=Tk.W + Tk.E)

        # Control whether or not Cbar is shown
        self.CbarVar = Tk.IntVar()
        self.CbarVar.set(self.params['show_cbar'])
        cb = ttk.Checkbutton(
            frm, text="Show Color bar",
            variable=self.CbarVar,
            command=self.CbarHandler)
        cb.grid(
            row=6, sticky=Tk.W)

        # show shock
        self.ShockVar = Tk.IntVar()
        self.ShockVar.set(self.params['show_shock'])
        cb = ttk.Checkbutton(
            frm, text="Show Shock",
            variable=self.ShockVar,
            command=self.ShockVarHandler)
        cb.grid(
            row=6, column=1,
            sticky=Tk.W)

        # show labels
        self.ShowLabels = Tk.IntVar()
        self.ShowLabels.set(self.params['show_labels'])
        ttk.Checkbutton(
            frm, text="Show Labels 2D",
            variable=self.ShowLabels,
            command=self.LabelHandler).grid(
                row=7, column=1,
                sticky=Tk.W)
        # Control whether or not diverging cmap is used
        self.DivVar = Tk.IntVar()
        self.DivVar.set(self.params['UseDivCmap'])
        ttk.Checkbutton(
            frm, text="Use Diverging Cmap",
            variable=self.DivVar,
            command=self.DivHandler).grid(
                row=8, sticky=Tk.W)

        # Use full div cmap
        self.StretchVar = Tk.IntVar()
        self.StretchVar.set(self.params['stretch_colors'])
        ttk.Checkbutton(
            frm, text="Asymmetric Color Space",
            variable=self.StretchVar,
            command=self.StretchHandler).grid(
                row=9, column=0,
                columnspan=2, sticky=Tk.W)

        self.cnormvar = Tk.StringVar(self)
        self.cnormvar.set(self.params['cnorm_type'])  # default value
        self.cnormvar.trace('w', self.cnormChanged)

        ttk.Label(
            frm, text="Choose Color Norm:").grid(
                row=6, column=2)
        cnormChooser = ttk.OptionMenu(
            frm, self.cnormvar,
            self.params['cnorm_type'],
            *tuple(['Pow', 'Linear']))
        cnormChooser.grid(
            row=6, column=3,
            sticky=Tk.W + Tk.E)

        # Now the gamma of the pow norm
        self.powGamma = Tk.StringVar()
        self.powGamma.set(str(self.params['cpow_num']))
        ttk.Label(
            frm, text='gamma =').grid(
                row=7, column=2,
                sticky=Tk.E)
        ttk.Label(
            frm, text='If cnorm is Pow =>').grid(
                row=8, column=2,
                columnspan=2,
                sticky=Tk.W)
        ttk.Label(
            frm, text='sign(data)*|data|**gamma').grid(
                row=9, column=2,
                columnspan=2,
                sticky=Tk.E)

        self.GammaEnter = ttk.Entry(
            frm, textvariable=self.powGamma,
            width=7)
        self.GammaEnter.grid(
            row=7, column=3)

        # Now the field lim
        self.setZminVar = Tk.IntVar()
        self.setZminVar.set(self.params['set_v_min'])
        self.setZminVar.trace('w', self.setZminChanged)

        self.setZmaxVar = Tk.IntVar()
        self.setZmaxVar.set(self.params['set_v_max'])
        self.setZmaxVar.trace('w', self.setZmaxChanged)

        self.Zmin = Tk.StringVar()
        self.Zmin.set(str(self.params['v_min']))

        self.Zmax = Tk.StringVar()
        self.Zmax.set(str(self.params['v_max']))

        ttk.Checkbutton(
            frm, text='Set flds min',
            variable=self.setZminVar).grid(
                row=3, column=2,
                sticky=Tk.W)
        self.ZminEnter = ttk.Entry(
            frm, textvariable=self.Zmin,
            width=7)
        self.ZminEnter.grid(
            row=3, column=3)

        ttk.Checkbutton(
            frm, text='Set flds max',
            variable=self.setZmaxVar).grid(
                row=4, column=2,
                sticky=Tk.W)

        self.ZmaxEnter = ttk.Entry(
            frm, textvariable=self.Zmax,
            width=7).grid(
                row=4, column=3)
        """
        self.setLayout(layout)

    def DivHandler(self, *args):
        if self.params['UseDivCmap'] == self.DivVar.get():
            pass
        else:
            self.params['UseDivCmap'] = self.DivVar.get()
            if self.params['twoD']:
                self.subplot.save_axes_pos()
                self.subplot.remove()
                self.subplot.build_axes()
                self.subplot.axis_info()
                self.subplot.draw()
                self.subplot.load_axes_pos()
                self.parent.oengus.canvas.draw()

    def sim_changed(self):
        cur_sim_name = self.oengus.sim_names[self.params['sim_num']]
        if self.sim_combo.currentText() == cur_sim_name:
            pass
        else:
            self.params['sim_num'] = self.oengus.sim_names.index(
                self.sim_combo.currentText())
            self.update_fld_combo()

            self.parent.update_all_sim_lists()
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.oengus.canvas.draw()

    def update_fld_combo(self):
        cur_sim = self.oengus.sims[self.params['sim_num']]
        avail_flds = cur_sim.get_available_quantities()['scalar_flds']
        self.ignoreChange = True
        self.fld_combo.clear()
        for fld in avail_flds.keys():
            self.fld_combo.addItem(fld)
        self.fld_combo.setCurrentText(self.params['flds_type'])
        self.ignoreChange = False

    def StretchHandler(self, *args):
        if self.params['stretch_colors'] == self.StretchVar.get():
            pass
        else:
            self.params['stretch_colors'] = self.StretchVar.get()
            if self.params['twoD']:
                self.subplot.save_axes_pos()
                self.subplot.remove()
                self.subplot.build_axes()
                self.subplot.axis_info()
                self.subplot.draw()
                self.subplot.load_axes_pos()
                self.parent.oengus.canvas.draw()

    def cnormChanged(self, *args):
        if self.params['cnorm_type'] == self.cnormvar.get():
            pass
        else:
            self.params['cnorm_type'] = self.cnormvar.get()
            if self.params['twoD']:
                self.subplot.save_axes_pos()
                self.subplot.remove()
                self.subplot.build_axes()
                self.subplot.axis_info()
                self.subplot.draw()
                self.subplot.load_axes_pos()
                self.parent.oengus.canvas.draw()

    def fld_type_changed(self):
        if not self.ignoreChange:
            self.params['flds_type'] = self.fld_combo.currentText()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()

            self.subplot.draw()
            self.parent.oengus.canvas.draw()

    def LabelHandler(self, *args):
        if self.params['show_labels'] == self.ShowLabels.get():
            pass
        else:
            self.params['show_labels'] = self.ShowLabels.get()
            if self.params['twoD']:
                self.subplot.an_2d.set_visible(self.ShowLabels.get())
                self.parent.oengus.canvas.draw()

    def Change2d(self):
        if self.TwoDVar.get() == self.params['twoD']:
            pass
        else:
            self.params['twoD'] = self.TwoDVar.get()
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()
            self.subplot.draw()
            self.parent.oengus.canvas.draw()

    def setZminChanged(self, *args):
        if self.setZminVar.get() == self.params['set_v_min']:
            pass
        else:
            self.params['set_v_min'] = self.setZminVar.get()
            self.subplot.set_v_max_min()
            self.parent.oengus.canvas.draw()

    def setZmaxChanged(self, *args):
        if self.setZmaxVar.get() == self.params['set_v_max']:
            pass
        else:
            self.params['set_v_max'] = self.setZmaxVar.get()
            self.subplot.set_v_max_min()
            self.parent.oengus.canvas.draw()

    def TxtEnter(self, e):
        self.FieldsCallback()
        self.GammaCallback()

    def GammaCallback(self):
        try:
            # make sure the user types in a float
            user_num = float(self.powGamma.get())
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
            self.powGamma.set(str(self.params['cpow_num']))

    def FieldsCallback(self):
        tkvarLimList = [self.Zmin, self.Zmax]
        plot_param_List = ['v_min', 'v_max']
        tkvarSetList = [self.setZminVar, self.setZmaxVar]
        to_reload = False
        for j in range(len(tkvarLimList)):
            try:
                # make sure the user types in a number
                user_num = float(tkvarLimList[j].get())
                if abs(user_num - self.params[plot_param_List[j]]) > 1E-4:
                    self.params[plot_param_List[j]] = user_num
                    to_reload += True*tkvarSetList[j].get()

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                tkvarLimList[j].set(str(self.params[plot_param_List[j]]))
        if to_reload:
            self.subplot.set_v_max_min()
            self.parent.oengus.canvas.draw()

    def OnClosing(self):
        self.destroy()
