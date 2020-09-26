import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
from new_cmaps import cmap_to_hex
import new_cmaps


class Spinbox(ttk.Entry):
    def __init__(self, master=None, **kw):
        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)

    def current(self, newindex=None):
        return self.tk.call(self._w, 'current', index)

    def set(self, value):
        return self.tk.call(self._w, 'set', value)


class SettingsFrame(Tk.Toplevel):
    def __init__(self, oengus):
        self.oengus = oengus
        self.main_params = self.oengus.MainParamDict

        Tk.Toplevel.__init__(self)
        self.wm_title('Settings')

        nb = ttk.Notebook(self)
        f1 = ttk.Frame(nb)
        f2 = ttk.Frame(nb)

        nb.add(f1, text='General Settings')
        nb.add(f2, text='Sim Settings')

        self.bind('<Return>', self.SettingsCallback)
        self.initial_focus = self.build_settings_panel(f1)
        self.build_sim_settings_panel(f2)
        nb.pack(fill=Tk.BOTH, anchor=Tk.CENTER, expand=True)

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.OnClosing)

        """self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        """
        self.initial_focus.focus_set()

    def build_settings_panel(self, frm):
        # Make an entry to change the skip size
        self.skipSize = Tk.StringVar(self)
        self.skipSize.set(self.main_params['SkipSize'])  # default value
        self.skipSize.trace('w', self.SkipSizeChanged)
        ttk.Label(
            frm, text="Skip Size:").grid(row=0)
        ttk.Entry(
            frm, textvariable=self.skipSize,
            width=6).grid(
                row=0, column=1,
                sticky=Tk.W + Tk.E)
        # Make an button to change the wait time
        self.waitTime = Tk.StringVar(self)
        self.waitTime.set(self.main_params['WaitTime'])  # default value
        self.waitTime.trace('w', self.WaitTimeChanged)

        ttk.Label(
            frm, text="Playback Wait Time:").grid(row=1)
        ttk.Entry(
            frm, textvariable=self.waitTime,
            width=6).grid(
                row=1, column=1,
                sticky=Tk.W + Tk.E)

        # Have a list of the color maps
        self.cmapvar = Tk.StringVar(self)
        self.cmapvar.set(self.main_params['ColorMap'])  # default value
        self.cmapvar.trace('w', self.CmapChanged)

        ttk.Label(
            frm, text="Color map:").grid(
                row=2)
        ttk.OptionMenu(
            frm, self.cmapvar,
            self.main_params['ColorMap'],
            *tuple(new_cmaps.sequential)).grid(
                row=2, column=1,
                sticky=Tk.W + Tk.E)

        # Have a list of the color maps
        self.divcmapList = new_cmaps.cmaps.keys()
        self.div_cmapvar = Tk.StringVar(self)
        self.div_cmapvar.set(self.main_params['DivColorMap'])  # default value
        self.div_cmapvar.trace('w', self.DivCmapChanged)

        ttk.Label(
            frm, text="Diverging Cmap:").grid(
            row=3)
        ttk.OptionMenu(
            frm, self.div_cmapvar,
            self.main_params['DivColorMap'],
            *tuple(new_cmaps.diverging)).grid(
                row=3, column=1,
                sticky=Tk.W + Tk.E)

        # Make an entry to change the number of columns
        self.columnNum = Tk.StringVar(self)
        self.columnNum.set(self.main_params['NumOfCols'])  # default value
        self.columnNum.trace('w', self.ColumnNumChanged)
        ttk.Label(frm, text="# of columns:").grid(row=4)
        Spinbox(
            frm, from_=1, to=self.main_params['MaxCols'],
            textvariable=self.columnNum, width=6).grid(
                row=4, column=1,
                sticky=Tk.W + Tk.E)

        # Make an entry to change the number of columns
        self.rowNum = Tk.StringVar(self)
        self.rowNum.set(self.main_params['NumOfRows'])  # default value
        self.rowNum.trace('w', self.RowNumChanged)
        ttk.Label(
            frm, text="# of rows:").grid(row=5)
        Spinbox(
            frm, from_=1, to=self.main_params['MaxRows'],
            textvariable=self.rowNum, width=6).grid(
                row=5, column=1,
                sticky=Tk.W + Tk.E)

        self.PrtlStrideVar = Tk.StringVar()
        self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
        ttk.Entry(
            frm,
            textvariable=self.PrtlStrideVar,
            width=6).grid(
                row=6, column=1,
                sticky=Tk.W + Tk.E)
        ttk.Label(
            frm, text='Particle stride').grid(
                row=6, column=0)

        # Control whether or not Title is shown
        self.TitleVar = Tk.IntVar()
        self.TitleVar.set(self.main_params['ShowTitle'])
        self.TitleVar.trace('w', self.TitleChanged)

        self.LimVar = Tk.IntVar()
        self.LimVar.set(self.main_params['SetxLim'])
        self.LimVar.trace('w', self.LimChanged)

        self.xleft = Tk.StringVar()
        self.xleft.set(str(self.main_params['xLeft']))
        self.xright = Tk.StringVar()
        self.xright.set(str(self.main_params['xRight']))

        ttk.Label(
            frm, text='min').grid(
                row=7, column=1,
                sticky=Tk.N)
        ttk.Label(
            frm, text='max').grid(
                row=7, column=2,
                sticky=Tk.N)
        ttk.Checkbutton(
            frm, text='Set xlim',
            variable=self.LimVar).grid(
                row=8, sticky=Tk.N)
        ttk.Entry(
            frm, textvariable=self.xleft,
            width=8).grid(
                row=8, column=1,
                sticky=Tk.N)
        ttk.Entry(
            frm, textvariable=self.xright,
            width=8).grid(
                row=8, column=2,
                sticky=Tk.N)

        self.yLimVar = Tk.IntVar()
        self.yLimVar.set(self.main_params['SetyLim'])
        self.yLimVar.trace('w', self.yLimChanged)

        self.yleft = Tk.StringVar()
        self.yleft.set(str(self.main_params['yBottom']))
        self.yright = Tk.StringVar()
        self.yright.set(str(self.main_params['yTop']))

        ttk.Checkbutton(
            frm, text='Set ylim',
            variable=self.yLimVar).grid(
                row=9, sticky=Tk.N)
        ttk.Entry(
            frm, textvariable=self.yleft,
            width=8).grid(
                row=9, column=1,
                sticky=Tk.N)
        ttk.Entry(
            frm, textvariable=self.yright,
            width=8).grid(
                row=9, column=2,
                sticky=Tk.N)

        ttk.Checkbutton(
            frm, text="Show Title",
            variable=self.TitleVar).grid(
                row=15, sticky=Tk.W)
        self.AspectVar = Tk.IntVar()
        self.AspectVar.set(self.main_params['ImageAspect'])
        self.AspectVar.trace('w', self.AspectVarChanged)

        # Control whether or not axes are shared with a radio box:
        self.toLinkList = ['None', 'All spatial', 'All Fields Plots']
        self.LinkedVar = Tk.IntVar()
        self.LinkedVar.set(self.oengus.MainParamDict['LinkSpatial'])

        ttk.Label(
            frm, text='Share spatial axes:').grid(
                row=0, column=2, sticky=Tk.W)

        for i in range(len(self.toLinkList)):
            ttk.Radiobutton(
                frm,
                text=self.toLinkList[i],
                variable=self.LinkedVar,
                command=self.RadioLinked,
                value=i).grid(
                    row=1+i, column=2, sticky=Tk.N)

        ttk.Checkbutton(
            frm, text="Aspect = 1",
            variable=self.AspectVar).grid(
                row=15, column=1,
                sticky=Tk.W)

        self.Average1DVar = Tk.IntVar()
        self.Average1DVar.set(self.main_params['Average1D'])
        self.Average1DVar.trace('w', self.AverageChanged)
        ttk.Checkbutton(
            frm, text='1D Average',
            variable=self.Average1DVar).grid(
                row=16, column=2,
                sticky=Tk.W)

        self.CbarOrientation = Tk.IntVar()
        self.CbarOrientation.set(self.main_params['HorizontalCbars'])
        self.CbarOrientation.trace('w', self.OrientationChanged)

        ttk.Checkbutton(
            frm, text="Horizontal Cbars",
            variable=self.CbarOrientation).grid(
                row=16, sticky=Tk.W)

    def build_sim_settings_panel(self, frm):
        """
        The function that builds out individual simulations settings window.
        For now we will just have it set the shock finder.
        """
        # OptionMenu to choose simulation
        self.cur_sim_name_var = Tk.StringVar(self)
        self.cur_sim_name_var.set(self.oengus.sim_names[0])
        # self.cur_sim_var.trace('w', self.SimChanged)

        ttk.Label(frm, text="Simulation:").grid(row=0, column=0)
        ttk.OptionMenu(
            frm, self.cur_sim_name_var,
            self.oengus.sim_names[0],
            *tuple(self.oengus.sim_names)).grid(
                row=0, column=1, sticky=Tk.W + Tk.E)

        ttk.Label(frm, text="Shock Finder:").grid(row=2, column=0)
        self.cur_sim = self.oengus.sims[
            self.oengus.sim_names.index(self.cur_sim_name_var.get())]

        self.shock_finder_var = Tk.StringVar(self)
        self.shock_finder_var.set(self.cur_sim.shock_finder_name)
        self.shock_finder_var.trace('w', self.shock_finder_changed)

        ttk.OptionMenu(
            frm, self.shock_finder_var,
            self.shock_finder_var.get(),
            *tuple(self.cur_sim.get_shock_finder_opts())).grid(
                row=2, column=1, sticky=Tk.W + Tk.E)

    def shock_finder_changed(self, *args):
        if self.cur_sim.shock_finder_name != self.shock_finder_var.get():
            self.cur_sim.shock_finder = self.shock_finder_var.get()
            self.shock_finder_var.set(self.cur_sim.shock_finder_name)
            # update shock lines
            for i in range(self.oengus.MainParamDict['NumOfRows']):
                for j in range(self.oengus.MainParamDict['NumOfCols']):
                    self.oengus.SubPlotList[i][j].refresh()
            self.oengus.canvas.draw()

    def RadioLinked(self, *args):
        # If the shared axes are changed, we have to call the link
        # handler on every subplot
        if self.LinkedVar.get() == self.oengus.MainParamDict['LinkSpatial']:
            pass
        else:
            self.oengus.MainParamDict['LinkSpatial'] = self.LinkedVar.get()
            for i in range(self.oengus.MainParamDict['NumOfRows']):
                for j in range(self.oengus.MainParamDict['NumOfCols']):
                    self.oengus.SubPlotList[i][j].link_handler()
                    self.oengus.SubPlotList[i][j].refresh()
            self.oengus.canvas.draw()

    def AspectVarChanged(self, *args):
        if self.AspectVar.get() == self.main_params['ImageAspect']:
            pass

        else:
            self.main_params['ImageAspect'] = self.AspectVar.get()
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def AverageChanged(self, *args):
        if self.main_params['Average1D'] != self.Average1DVar.get():
            self.main_params['Average1D'] = self.Average1DVar.get()
            self.oengus.draw_output()

    def OrientationChanged(self, *args):
        if self.CbarOrientation.get() == self.main_params['HorizontalCbars']:
            pass

        else:
            if self.CbarOrientation.get():
                self.oengus.axes_extent = self.main_params['HAxesExtent']
                self.oengus.cbar_extent = self.main_params['HCbarExtent']
                self.oengus.SubPlotParams = self.main_params['HSubPlotParams']

            else:
                self.oengus.axes_extent = self.main_params['VAxesExtent']
                self.oengus.cbar_extent = self.main_params['VCbarExtent']
                self.oengus.SubPlotParams = self.main_params['VSubPlotParams']
            self.main_params['HorizontalCbars'] = self.CbarOrientation.get()
            self.oengus.figure.subplots_adjust(**self.oengus.SubPlotParams)
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def TitleChanged(self, *args):
        if self.TitleVar.get() == self.main_params['ShowTitle']:
            pass
        else:
            self.main_params['ShowTitle'] = self.TitleVar.get()
            if not self.TitleVar.get():
                self.oengus.figure.suptitle('')
            self.oengus.canvas.draw()

    def xRelChanged(self, *args):
        pass
        # If the shared axes are changed, the whole plot must be redrawn
        # if self.xRelVar.get() == self.main_params['xLimsRelative']:
        #    pass
        # else:
        #    self.main_params['xLimsRelative'] = self.xRelVar.get()
        #    self.parent.RenewCanvas()

    def CmapChanged(self, *args):
        # Note here that Tkinter passes an event object to onselect()
        if self.cmapvar.get() == self.main_params['ColorMap']:
            pass
        else:
            self.main_params['ColorMap'] = self.cmapvar.get()
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

    def DivCmapChanged(self, *args):
        # Note here that Tkinter passes an event object to onselect()
        if self.div_cmapvar.get() == self.main_params['DivColorMap']:
            pass
        else:
            self.main_params['DivColorMap'] = self.div_cmapvar.get()
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def SkipSizeChanged(self, *args):
        # Note here that Tkinter passes an event object to SkipSizeChange()
        try:
            if self.skipSize.get() == '':
                pass
            else:
                self.main_params['SkipSize'] = int(self.skipSize.get())
        except ValueError:
            self.skipSize.set(self.main_params['SkipSize'])

    def RowNumChanged(self, *args):
        try:
            if self.rowNum.get() == '':
                pass
            if int(self.rowNum.get()) < 1:
                self.rowNum.set(1)
            if int(self.rowNum.get()) > self.main_params['MaxRows']:
                self.rowNum.set(self.main_params['MaxRows'])
            if int(self.rowNum.get()) != self.main_params['NumOfRows']:
                self.main_params['NumOfRows'] = int(self.rowNum.get())
                self.oengus.figure.clf()
                self.oengus.create_graphs()
                self.oengus.canvas.draw()
        except ValueError:
            self.rowNum.set(self.main_params['NumOfRows'])

    def ColumnNumChanged(self, *args):
        try:
            if self.columnNum.get() == '':
                pass
            if int(self.columnNum.get()) < 1:
                self.columnNum.set(1)
            if int(self.columnNum.get()) > self.main_params['MaxCols']:
                self.columnNum.set(self.main_params['MaxCols'])
            if int(self.columnNum.get()) != self.main_params['NumOfCols']:
                self.main_params['NumOfCols'] = int(self.columnNum.get())
                self.oengus.figure.clf()
                self.oengus.create_graphs()
                self.oengus.canvas.draw()
        except ValueError:
            self.columnNum.set(self.main_params['NumOfCols'])

    def WaitTimeChanged(self, *args):
        # Note here that Tkinter passes an event object to onselect()
        try:
            if self.waitTime.get() == '':
                pass
            else:
                self.main_params['WaitTime'] = float(self.waitTime.get())
        except ValueError:
            self.waitTime.set(self.main_params['WaitTime'])

    def CheckIfLimsChanged(self):
        to_reload = False
        tmplist = [self.xleft, self.xright, self.yleft, self.yright]
        limkeys = ['xLeft', 'xRight', 'yBottom', 'yTop']
        setKeys = ['SetxLim', 'SetyLim']
        for j in range(len(tmplist)):
            setlims = self.main_params[setKeys[j//2]]
            tmpkey = limkeys[j]

            try:
                # make sure the user types in a a number and
                # that it has changed.
                user_num = float(tmplist[j].get())
                if abs(user_num - self.main_params[tmpkey]) > 1E-4:
                    self.main_params[tmpkey] = user_num
                    to_reload += setlims

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                tmplist[j].set(str(self.main_params[tmpkey]))
        return to_reload

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

    def LimChanged(self, *args):
        if self.LimVar.get() == self.main_params['SetxLim']:
            pass
        else:
            self.main_params['SetxLim'] = self.LimVar.get()
            self.oengus.draw_output()

    def yLimChanged(self, *args):
        if self.yLimVar.get() == self.main_params['SetyLim']:
            pass
        else:
            self.main_params['SetyLim'] = self.yLimVar.get()
            self.oengus.draw_output()

    def SettingsCallback(self, e):
        to_reload = self.CheckIfLimsChanged()
        to_reload += self.CheckIfStrideChanged()
        if to_reload:
            self.oengus.draw_output()

    def OnClosing(self):
        self.destroy()
