import tkinter as Tk
from tkinter import ttk
import new_cmaps


class phaseSettings(Tk.Toplevel):
    interpolation_methods = [
        'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
        'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
        'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def __init__(self, parent, loc):
        self.parent = parent
        Tk.Toplevel.__init__(self)
        self.loc = loc
        self.wm_title(f'Phase Plot {self.loc} Settings')
        self.parent = parent
        frm = ttk.Frame(self)
        frm.pack(fill=Tk.BOTH, expand=True)
        self.protocol('WM_DELETE_WINDOW', self.OnClosing)
        self.bind('<Return>', self.TxtEnter)
        self.subplot = self.parent.oengus.SubPlotList[self.loc[0]][self.loc[1]]
        self.params = self.subplot.param_dict

        # Create the OptionMenu to chooses the image interpolation:
        self.InterpolVar = Tk.StringVar(self)
        self.InterpolVar.set(self.params['interpolation'])  # default value
        self.InterpolVar.trace('w', self.InterpolChanged)
        ttk.Label(frm, text="Interpolation Method:").grid(
            row=0, column=2)
        ttk.OptionMenu(
            frm, self.InterpolVar,
            self.params['interpolation'],
            *tuple(self.interpolation_methods)).grid(
                row=0, column=3,
                sticky=Tk.W + Tk.E)

        # OptionMenu to choose simulation
        self.SimVar = Tk.StringVar(self)
        self.SimVar.set(self.parent.oengus.sim_names[self.params['sim_num']])
        self.SimVar.trace('w', self.SimChanged)

        ttk.Label(frm, text="simulation:").grid(row=1, column=0)
        ttk.OptionMenu(
            frm, self.SimVar,
            self.parent.oengus.sim_names[self.params['sim_num']],
            *tuple(self.parent.oengus.sim_names)).grid(
            row=1, column=1, sticky=Tk.W + Tk.E)

        # Create the OptionMenu to chooses the Chart Type:
        self.ctypevar = Tk.StringVar(self)
        self.ctypevar.set(self.subplot.chart_type)  # default value
        self.ctypevar.trace('w', self.ctypeChanged)

        ttk.Label(frm, text="Choose Chart Type:").grid(row=0, column=0)
        ttk.OptionMenu(
            frm, self.ctypevar,
            self.subplot.chart_type,
            *tuple(self.parent.oengus.plot_types_dict.keys())).grid(
                row=0, column=1,
                sticky=Tk.W + Tk.E)

        # the Radiobox Control to choose the Field Type
        self.quantity = Tk.StringVar(self)
        self.quantity.set(self.params['prtl_type'])
        self.quantity.trace('w', self.quantityChanged)

        cur_sim = self.parent.oengus.sims[self.params['sim_num']]
        avail_prtls = cur_sim.get_available_quantities()['prtls']
        ttk.Label(frm, text="Choose Particle:").grid(
            row=2, sticky=Tk.W)
        ttk.OptionMenu(
            frm, self.quantity,
            self.params['prtl_type'],
            *tuple(avail_prtls.keys())).grid(
                row=3, column=0,
                sticky=Tk.W + Tk.E)

        # choose the prtl quantity on the x-axis
        ttk.Label(
            frm, text='x_val:').grid(
                row=4, column=0, sticky=Tk.W)
        self.xval_var = Tk.StringVar(self)
        self.xval_var.set(self.params['x_val'])
        self.xval_var.trace('w', self.x_valChanged)

        avail_attrs = avail_prtls[self.params['prtl_type']]['attrs'].keys()
        ttk.OptionMenu(
            frm, self.xval_var,
            self.params['x_val'],
            *tuple(avail_attrs)).grid(
                row=5, column=0,
                sticky=Tk.W + Tk.E)

        ttk.Label(
            frm, text='y_val:').grid(
                row=4, column=1,
                sticky=Tk.W)

        self.yval_var = Tk.StringVar(self)
        self.yval_var.set(self.params['y_val'])
        self.yval_var.trace('w', self.y_valChanged)

        ttk.OptionMenu(
            frm, self.yval_var,
            self.params['y_val'],
            *tuple(avail_attrs)).grid(
                row=5, column=1,
                sticky=Tk.W + Tk.E)

        # the Check boxes for the dimension

        # Control whether or not Cbar is shown
        self.CbarVar = Tk.IntVar()
        self.CbarVar.set(self.params['show_cbar'])
        ttk.Checkbutton(
            frm, text="Show Color bar",
            variable=self.CbarVar,
            command=self.CbarHandler).grid(
                row=6, sticky=Tk.W)

        # show shock
        self.ShockVar = Tk.IntVar()
        self.ShockVar.set(self.params['show_shock'])
        ttk.Checkbutton(
            frm, text="Show Shock",
            variable=self.ShockVar,
            command=self.ShockVarHandler).grid(
                row=6, column=1,
                sticky=Tk.W)

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
            frm, text='Set v min',
            variable=self.setZminVar).grid(
                row=3, column=2, sticky=Tk.W)
        ttk.Entry(
            frm, textvariable=self.Zmin,
            width=7).grid(
                row=3, column=3)

        ttk.Checkbutton(
            frm, text='Set flds max',
            variable=self.setZmaxVar).grid(
                row=4, column=2, sticky=Tk.W)

        ttk.Entry(
            frm, textvariable=self.Zmax,
            width=7).grid(
                row=4, column=3)

    def ShockVarHandler(self, *args):
        if self.params['show_shock'] == self.ShockVar.get():
            pass
        else:
            print('Not Implemented Yet')
            # if self.params['twoD']:
            #     self.subplot.shockline_2d.set_visible(self.ShockVar.get())
            # else:
            #     self.subplot.shock_line.set_visible(self.ShockVar.get())
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
        if self.params['prtl_type'] == self.quantity.get():
            pass
        else:
            self.params['prtl_type'] = self.quantity.get()
            self.subplot.refresh()
            self.subplot.update_labels_and_colors()
            self.parent.oengus.canvas.draw()

    def y_valChanged(self, *args):
        if self.params['y_val'] == self.yval_var.get():
            pass
        else:
            self.params['y_val'] = self.yval_var.get()
            self.subplot.refresh()
            self.subplot.update_labels_and_colors()
            self.parent.oengus.canvas.draw()

    def x_valChanged(self, *args):
        if self.params['x_val'] == self.xval_var.get():
            pass
        else:
            self.params['x_val'] = self.xval_var.get()

            self.subplot.refresh()
            self.subplot.update_labels_and_colors()
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

    def SimChanged(self, *args):
        cur_sim_name = self.parent.oengus.sim_names[self.params['sim_num']]
        if self.SimVar.get() == cur_sim_name:
            pass
        else:
            self.params['sim_num'] = self.parent.oengus.sim_names.index(
                self.SimVar.get())
            self.parent.oengus.calc_sims_shown()
            self.parent.playbackbar.update_sim_list()
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def setZminChanged(self, *args):
        if self.setZminVar.get() == self.params['set_v_min']:
            pass
        else:
            self.params['set_v_min'] = self.setZminVar.get()
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def setZmaxChanged(self, *args):
        if self.setZmaxVar.get() == self.params['set_v_max']:
            pass
        else:
            self.params['set_v_max'] = self.setZmaxVar.get()
            self.subplot.refresh()
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
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def OnClosing(self):
        self.destroy()
