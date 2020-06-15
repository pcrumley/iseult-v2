import tkinter as Tk
from tkinter import ttk
import new_cmaps


class ScalarVsTimeSettings(Tk.Toplevel):

    def __init__(self, parent, loc):
        self.parent = parent
        Tk.Toplevel.__init__(self)
        self.loc = loc
        self.wm_title(f'Scalar vs Time Plot {self.loc} Settings')
        self.parent = parent
        frm = ttk.Frame(self)
        frm.pack(fill=Tk.BOTH, expand=True)
        self.protocol('WM_DELETE_WINDOW', self.OnClosing)
        self.bind('<Return>', self.TxtEnter)
        self.subplot = self.parent.oengus.SubPlotList[self.loc[0]][self.loc[1]]
        self.params = self.subplot.param_dict

        # Create the OptionMenu to chooses the Chart Type:
        self.ctypevar = Tk.StringVar(self)
        self.ctypevar.set(self.subplot.chart_type)  # default value
        self.ctypevar.trace('w', self.ctypeChanged)

        ttk.Label(frm, text="Choose Chart Type:").grid(row=0, column=0)
        ctypeChooser = ttk.OptionMenu(
            frm, self.ctypevar, self.subplot.chart_type,
            *tuple(self.parent.oengus.plot_types_dict.keys()))
        ctypeChooser.grid(row=0, column=1, sticky=Tk.W + Tk.E)

    def ShockVarHandler(self, *args):
        if self.params['show_shock'] == self.ShockVar.get():
            pass
        else:
            print('Not Implemented Yet')
            # if self.params['twoD']:
            #    self.subplot.shockline_2d.set_visible(self.ShockVar.get())
            # else:
            #    self.subplot.shock_line.set_visible(self.ShockVar.get())
            self.params['show_shock'] = self.ShockVar.get()
            self.parent.oengus.canvas.draw()

    def CbarHandler(self, *args):
        if self.params['show_cbar'] == self.CbarVar.get():
            pass
        else:
            self.params['show_cbar'] = self.CbarVar.get()
            if self.params['twoD']:
                self.subplot.axC.set_visible(self.CbarVar.get())
                self.parent.oengus.canvas.draw()

    def DivHandler(self, *args):
        if self.params['UseDivCmap'] == self.DivVar.get():
            pass
        else:
            self.params['UseDivCmap'] = self.DivVar.get()
            if self.params['twoD']:
                tmp_cmap = None
                if self.params['UseDivCmap']:
                    tmp_cmap = self.parent.oengus.MainParamDict['DivColorMap']
                else:
                    tmp_cmap = self.parent.oengus.MainParamDict['ColorMap']
                self.subplot.image.set_cmap(new_cmaps.cmaps[tmp_cmap])
                self.subplot.cbar.set_cmap(new_cmaps.cmaps[tmp_cmap])
                self.subplot.set_v_max_min()
                self.parent.oengus.canvas.draw()

    def SimChanged(self, *args):
        sim_names = self.parent.oengus.sim_names
        if self.SimVar.get() == sim_names[self.params['sim_num']]:
            pass
        else:
            self.params['sim_num'] = sim_names.index(self.SimVar.get())
            self.parent.oengus.calc_sims_shown()
            self.parent.playbackbar.update_sim_list()
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def StretchHandler(self, *args):
        if self.params['stretch_colors'] == self.StretchVar.get():
            pass
        else:
            self.params['stretch_colors'] = self.StretchVar.get()
            if self.params['twoD']:
                self.subplot.remove()
                self.subplot.draw()
                self.parent.oengus.canvas.draw()

    def cnormChanged(self, *args):
        if self.params['cnorm_type'] == self.cnormvar.get():
            pass
        else:
            self.params['cnorm_type'] = self.cnormvar.get()
            if self.params['twoD']:
                self.subplot.remove()
                self.subplot.draw()
                self.parent.oengus.canvas.draw()

    def quantityChanged(self, *args):
        if self.params['field_type'] == self.quantity.get():
            pass
        else:
            self.params['field_type'] = self.quantity.get()
            self.subplot.update_labels_and_colors()
            self.subplot.refresh()
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

            # Make sure only one dimension checked
            if self.params['twoD']:
                if self.params['show_x']:
                    self.ShowYVar.set(0)
                    self.params['show_y'] = 0
                    self.ShowZVar.set(0)
                    self.params['show_z'] = 0
                elif self.params['show_y']:
                    self.ShowZVar.set(0)
                    self.params['show_z'] = 0
            self.subplot.remove()
            self.subplot.build_axes()
            self.subplot.axis_info()
            self.subplot.draw()
            self.parent.oengus.canvas.draw()

    def ctypeChanged(self, *args):
        if self.ctypevar.get() == self.subplot.chart_type:
            pass
        else:
            self.parent.changePlotType(self.loc, self.ctypevar.get())
            self.destroy()

    def InterpolChanged(self, *args):
        if self.InterpolVar.get() == self.params['interpolation']:
            pass
        else:
            if self.params['twoD']:
                self.subplot.image.set_interpolation(self.InterpolVar.get())
            self.params['interpolation'] = self.InterpolVar.get()
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
                    self.subplot.remove()
                    self.subplot.draw()
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

    def Selector(self):
        # First check if it is 2-D:
        if self.params['twoD']:
            all_zero = self.ShowXVar.get() == 0
            all_zero = all_zero and self.ShowYVar.get() == 0
            all_zero = all_zero and self.ShowZVar.get() == 0

            if all_zero:
                # All are zero, something must be selected for this plot
                self.ShowXVar.set(1)

            if self.params['show_x'] != self.ShowXVar.get():
                # set the other plot values to zero in the PlotParams
                self.params['show_y'] = 0
                self.params['show_z'] = 0

                # Uncheck the boxes
                self.ShowYVar.set(self.params['show_y'])
                self.ShowZVar.set(self.params['show_z'])
                self.params['show_x'] = self.ShowXVar.get()

            elif self.params['show_y'] != self.ShowYVar.get():
                # set the other plot values to zero in the PlotParams
                self.params['show_x'] = 0
                self.params['show_z'] = 0

                # Uncheck the boxes
                self.ShowXVar.set(self.params['show_x'])
                self.ShowZVar.set(self.params['show_z'])
                self.params['show_y'] = self.ShowYVar.get()

            elif self.params['show_z'] != self.ShowZVar.get():
                # set the other plot values to zero in the PlotParams
                self.params['show_x'] = 0
                self.params['show_y'] = 0

                # Uncheck the boxes
                self.ShowXVar.set(self.params['show_x'])
                self.ShowYVar.set(self.params['show_y'])
                self.params['show_z'] = self.ShowZVar.get()

        else:
            if self.params['show_x'] != self.ShowXVar.get():
                self.subplot.line_x[0].set_visible(self.ShowXVar.get())
                self.subplot.anx.set_visible(self.ShowXVar.get())
                self.params['show_x'] = self.ShowXVar.get()

            elif self.params['show_y'] != self.ShowYVar.get():
                self.subplot.line_y[0].set_visible(self.ShowYVar.get())
                self.subplot.any.set_visible(self.ShowYVar.get())
                self.params['show_y'] = self.ShowYVar.get()

            elif self.params['show_z'] != self.ShowZVar.get():
                self.subplot.line_z[0].set_visible(self.ShowZVar.get())
                self.subplot.anz.set_visible(self.ShowZVar.get())
                self.params['show_z'] = self.ShowZVar.get()
        self.subplot.refresh()
        self.parent.oengus.canvas.draw()

    def OnClosing(self):
        self.destroy()
