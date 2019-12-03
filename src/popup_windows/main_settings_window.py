import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
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

        Tk.Toplevel.__init__(self)
        self.wm_title('General Settings')
        self.protocol('WM_DELETE_WINDOW', self.OnClosing)

        self.bind('<Return>', self.SettingsCallback)

        self.oengus = oengus
        self.main_params = self.oengus.MainParamDict
        frm = ttk.Frame(self)
        frm.pack(fill=Tk.BOTH, expand=True)

        # Make an entry to change the skip size
        self.skipSize = Tk.StringVar(self)
        self.skipSize.set(self.main_params['SkipSize']) # default value
        self.skipSize.trace('w', self.SkipSizeChanged)
        ttk.Label(frm, text="Skip Size:").grid(row=0)
        self.skipEnter = ttk.Entry(frm, textvariable=self.skipSize, width = 6)
        self.skipEnter.grid(row =0, column = 1, sticky = Tk.W + Tk.E)

        # Make an button to change the wait time
        self.waitTime = Tk.StringVar(self)
        self.waitTime.set(self.main_params['WaitTime']) # default value
        self.waitTime.trace('w', self.WaitTimeChanged)
        ttk.Label(frm, text="Playback Wait Time:").grid(row=1)
        self.waitEnter = ttk.Entry(frm, textvariable=self.waitTime, width = 6)
        self.waitEnter.grid(row =1, column = 1, sticky = Tk.W + Tk.E)

        # Have a list of the color maps
        self.cmapvar = Tk.StringVar(self)
        self.cmapvar.set(self.main_params['ColorMap']) # default value
        self.cmapvar.trace('w', self.CmapChanged)

        ttk.Label(frm, text="Color map:").grid(row=2)
        cmapChooser = ttk.OptionMenu(frm, self.cmapvar, self.main_params['ColorMap'], *tuple(new_cmaps.sequential))
        cmapChooser.grid(row =2, column = 1, sticky = Tk.W + Tk.E)

        # Have a list of the color maps
        self.divcmapList = new_cmaps.cmaps.keys()
        self.div_cmapvar = Tk.StringVar(self)
        self.div_cmapvar.set(self.main_params['DivColorMap']) # default value
        self.div_cmapvar.trace('w', self.DivCmapChanged)

        ttk.Label(frm, text="Diverging Cmap:").grid(row=3)
        cmapChooser = ttk.OptionMenu(frm, self.div_cmapvar, self.main_params['DivColorMap'], *tuple(new_cmaps.diverging))
        cmapChooser.grid(row =3, column = 1, sticky = Tk.W + Tk.E)


        # Make an entry to change the number of columns
        self.columnNum = Tk.StringVar(self)
        self.columnNum.set(self.main_params['NumOfCols']) # default value
        self.columnNum.trace('w', self.ColumnNumChanged)
        ttk.Label(frm, text="# of columns:").grid(row=4)
        self.ColumnSpin = Spinbox(frm,  from_=1, to=self.main_params['MaxCols'], textvariable=self.columnNum, width = 6)
        self.ColumnSpin.grid(row =4, column = 1, sticky = Tk.W + Tk.E)

        # Make an entry to change the number of columns
        self.rowNum = Tk.StringVar(self)
        self.rowNum.set(self.main_params['NumOfRows']) # default value
        self.rowNum.trace('w', self.RowNumChanged)
        ttk.Label(frm, text="# of rows:").grid(row=5)
        self.RowSpin = Spinbox(frm, from_=1, to=self.main_params['MaxRows'], textvariable=self.rowNum, width = 6)
        self.RowSpin.grid(row =5, column = 1, sticky = Tk.W + Tk.E)

        self.PrtlStrideVar = Tk.StringVar()
        self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
        ttk.Entry(frm, textvariable = self.PrtlStrideVar, width =6).grid(row =6, column =1, sticky = Tk.W +Tk.E)
        ttk.Label(frm, text='Particle stride').grid(row= 6,column =0)

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


        ttk.Label(frm, text = 'min').grid(row= 7, column = 1, sticky = Tk.N)
        ttk.Label(frm, text = 'max').grid(row= 7, column = 2, sticky = Tk.N)
        cb = ttk.Checkbutton(frm, text ='Set xlim',
                        variable = self.LimVar)
        cb.grid(row = 8, sticky = Tk.N)
        ttk.Entry(frm, textvariable=self.xleft, width = 8).grid(row = 8, column =1, sticky = Tk.N)
        ttk.Entry(frm, textvariable=self.xright, width = 8).grid(row = 8, column =2, sticky = Tk.N)



        self.yLimVar = Tk.IntVar()
        self.yLimVar.set(self.main_params['SetyLim'])
        self.yLimVar.trace('w', self.yLimChanged)



        self.yleft = Tk.StringVar()
        self.yleft.set(str(self.main_params['yBottom']))
        self.yright = Tk.StringVar()
        self.yright.set(str(self.main_params['yTop']))


        ttk.Checkbutton(frm, text ='Set ylim',
                        variable = self.yLimVar).grid(row = 9, sticky = Tk.N)
        ttk.Entry(frm, textvariable=self.yleft, width = 8 ).grid(row = 9, column =1, sticky = Tk.N)
        ttk.Entry(frm, textvariable=self.yright, width =8 ).grid(row = 9, column =2, sticky = Tk.N)

        #self.kLimVar = Tk.IntVar()
        #self.kLimVar.set(self.main_params['SetkLim'])
        #self.kLimVar.trace('w', self.kLimChanged)



        #self.kleft = Tk.StringVar()
        #self.kleft.set(str(self.main_params['kLeft']))
        #self.kright = Tk.StringVar()
        #self.kright.set(str(self.main_params['kRight']))


        #ttk.Checkbutton(frm, text ='Set klim', variable = self.kLimVar).grid(row = 10, sticky = Tk.N)
        #ttk.Entry(frm, textvariable=self.kleft, width = 8 ).grid(row = 10, column =1, sticky = Tk.N)
        #ttk.Entry(frm, textvariable=self.kright, width =8 ).grid(row = 10, column =2, sticky = Tk.N)

        #self.xRelVar = Tk.IntVar()
        #self.xRelVar.set(self.main_params['xLimsRelative'])
        #self.xRelVar.trace('w', self.xRelChanged)
        #ttk.Checkbutton(frm, text = "x limits & zooms relative to shock",
        #                variable = self.xRelVar).grid(row = 11, columnspan = 3, sticky = Tk.W)

        """
        framecb = ttk.Frame(frm)

        ttk.Label(framecb, text='Choose 2D plane:').pack(side = Tk.LEFT, expand = 0)
        self.PlaneVar = Tk.IntVar()
        self.PlaneVar.set(self.main_params['2DSlicePlane'])
        self.xybutton = ttk.Radiobutton(framecb,
                            text='x-y',
                            variable=self.PlaneVar,
                            command = self.RadioPlane,
                            value=0)
        self.xybutton.pack(side = Tk.LEFT, expand = 0)
        self.xzbutton = ttk.Radiobutton(framecb,
                            text='x-z',
                            variable=self.PlaneVar,
                            command = self.RadioPlane,
                            value=1)
        self.xzbutton.pack(side = Tk.LEFT, expand = 0)
        framecb.grid(row = 12, columnspan = 4)
        """
        """
        framey = ttk.Frame(frm)
        self.ySliceVar = Tk.IntVar()
        self.ySliceVar.set(self.parent.ySlice)
        self.units_listy = []
        for i in range(self.parent.MaxYInd+1):
            self.units_listy.append(str(i*self.parent.istep/self.parent.c_omp))

        self.ySliceVarC_omp = Tk.StringVar()
        self.ySliceVarC_omp.set(self.units_listy[self.ySliceVar.get()])

        labely = ttk.Label(framey, text='y-slice')#
        labely.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)


        # A slider that will select the 2D slice in the simulation
        self.slidery = ttk.Scale(framey, from_=0, to=self.parent.MaxYInd, command = self.yScaleHandler)
        self.slidery.set(self.ySliceVar.get())
        self.slidery.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)


        self.txtEntery = ttk.Entry(framey, textvariable=self.ySliceVarC_omp, width=6)
        self.txtEntery.pack(side=Tk.LEFT, fill = Tk.BOTH, expand = 0)
        if self.parent.MaxYInd ==0:
            self.txtEntery.state(['disabled'])
            self.slidery.state(['disabled'])
        ttk.Label(framey, text='[c_omp]').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # bind releasing the moust button to updating the plots.
        self.slidery.bind("<ButtonRelease-1>", self.yUpdateValue)


        framey.grid(row = 13, columnspan =4)

        framez = ttk.Frame(frm)
        self.zSliceVar = Tk.IntVar()
        self.zSliceVar.set(int(np.around(self.main_params['zSlice']*self.parent.MaxZInd)))

        self.units_listz = []
        for i in range(self.parent.MaxZInd+1):
            self.units_listz.append(str(i*self.parent.istep/self.parent.c_omp))

        self.zSliceVarC_omp = Tk.StringVar()
        self.zSliceVarC_omp.set(self.units_listz[self.zSliceVar.get()])

        # An entry box that will let us choose the time-step
        ttk.Label(framez, text='z-slice').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)

        # A slider that will select the 2D slice in the simulation
        self.sliderz = ttk.Scale(framez, from_=0, to=self.parent.MaxZInd, command = self.zScaleHandler)
        self.sliderz.set(self.zSliceVar.get())
        self.sliderz.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        self.txtEnterz = ttk.Entry(framez, textvariable=self.zSliceVarC_omp, width=6)
        self.txtEnterz.pack(side=Tk.LEFT, fill = Tk.BOTH, expand = 0)
        ttk.Label(framez, text='[c_omp]').pack(side=Tk.LEFT, fill=Tk.BOTH, expand=0)
        # bind releasing the moust button to updating the plots.
        self.sliderz.bind("<ButtonRelease-1>", self.zUpdateValue)
        if self.parent.MaxZInd ==0:
            self.xzbutton.state(['disabled'])
            self.txtEnterz.state(['disabled'])
            self.sliderz.state(['disabled'])


        framez.grid(row = 14, columnspan =4)
        """
        cb = ttk.Checkbutton(frm, text = "Show Title",
                        variable = self.TitleVar)
        cb.grid(row = 15, sticky = Tk.W)
        # Control whether or not axes are shared with a radio box:
        #self.toLinkList = ['None', 'All spatial', 'All non p-x', 'All 2-D spatial']
        #self.LinkedVar = Tk.IntVar()
        #self.LinkedVar.set(self.main_params['LinkSpatial'])

        #ttk.Label(frm, text='Share spatial axes:').grid(row = 0, column = 2, sticky = Tk.W)

        #for i in range(len(self.toLinkList)):
        #    ttk.Radiobutton(frm,
        #            text=self.toLinkList[i],
        #            variable=self.LinkedVar,
        #            command = self.RadioLinked,
        #            value=i).grid(row = 1+i, column = 2, sticky =Tk.N)

        self.AspectVar = Tk.IntVar()
        self.AspectVar.set(self.main_params['ImageAspect'])
        self.AspectVar.trace('w', self.AspectVarChanged)

        cb = ttk.Checkbutton(frm, text = "Aspect = 1",
                                variable = self.AspectVar)
        cb.grid(row = 15, column = 1, sticky = Tk.W)

        #self.ConstantShockVar = Tk.IntVar()
        #self.ConstantShockVar.set(self.main_params['ConstantShockVel'])
        #self.ConstantShockVar.trace('w', self.ShockSpeedVarChanged)

        #cb = ttk.Checkbutton(frm, text = "Constant Shock v",
        #                        variable = self.ConstantShockVar)
        #cb.grid(row = 15, column = 2, sticky = Tk.W)

        self.Average1DVar = Tk.IntVar()
        self.Average1DVar.set(self.main_params['Average1D'])
        self.Average1DVar.trace('w', self.AverageChanged)
        ttk.Checkbutton(frm, text='1D Average',variable = self.Average1DVar).grid(row = 16, column = 2, sticky = Tk.W)

        self.CbarOrientation = Tk.IntVar()
        self.CbarOrientation.set(self.main_params['HorizontalCbars'])
        self.CbarOrientation.trace('w', self.OrientationChanged)

        cb = ttk.Checkbutton(frm, text = "Horizontal Cbars",
                                variable = self.CbarOrientation)
        cb.grid(row = 16, sticky = Tk.W)


        #self.LinkKVar = Tk.IntVar()
        #self.LinkKVar.set(self.main_params['LinkK'])
        #self.LinkKVar.trace('w', self.LinkKChanged)

        #cb = ttk.Checkbutton(frm, text = "Share k-axes",
        #                        variable = self.LinkKVar)
        #cb.grid(row = 16, column =1, sticky = Tk.W)

    def yScaleHandler(self, e):
        # if changing the scale will change the value of the parameter, do so
        if self.ySliceVar.get() != int(self.slidery.get()):
            self.ySliceVar.set(int(self.slidery.get()))
            self.ySliceVarC_omp.set(self.units_listy[self.ySliceVar.get()])

    def zScaleHandler(self, e):
        # if changing the scale will change the value of the parameter, do so
        if self.zSliceVar.get() != int(self.sliderz.get()):
            self.zSliceVar.set(int(self.sliderz.get()))
            self.zSliceVarC_omp.set(self.units_listz[self.zSliceVar.get()])

    def zUpdateValue(self, e):
        if self.zSliceVar.get() == self.parent.zSlice:
            pass

        else:
            self.main_params['zSlice'] = float(self.zSliceVar.get())/self.parent.MaxZInd
            self.zSliceVarC_omp.set(self.units_listz[self.zSliceVar.get()])
            self.parent.RenewCanvas()

    def yUpdateValue(self, e):
        if self.ySliceVar.get() == self.parent.ySlice:
            pass

        else:
            self.main_params['ySlice'] = float(self.ySliceVar.get())/self.parent.MaxYInd
            self.ySliceVarC_omp.set(self.units_listy[self.ySliceVar.get()])
            self.parent.RenewCanvas()


    def AspectVarChanged(self, *args):
        if self.AspectVar.get() == self.main_params['ImageAspect']:
            pass

        else:
            self.main_params['ImageAspect'] = self.AspectVar.get()
            self.oengus.figure.clf()
            self.oengus.create_graphs()
            self.oengus.canvas.draw()

    def ShockSpeedVarChanged(self, *args):
        if self.main_params['ConstantShockVel'] != self.ConstantShockVar.get():
            self.main_params['ConstantShockVel'] = self.ConstantShockVar.get()
            self.parent.RenewCanvas(ForceRedraw = True)

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

    #def LorentzBoostChanged(self, *args):
    #    if self.LorentzBoostVar.get() == self.main_params['DoLorentzBoost']:
    #        pass

    #    else:
    #        self.main_params['DoLorentzBoost'] = self.LorentzBoostVar.get()
    #        self.parent.RenewCanvas()

    def TitleChanged(self, *args):
        if self.TitleVar.get()==self.main_params['ShowTitle']:
            pass
        else:
            self.main_params['ShowTitle'] = self.TitleVar.get()
            if self.TitleVar.get() == False:
                self.oengus.figure.suptitle('')
            self.oengus.canvas.draw()

    def RadioLinked(self, *args):
        # If the shared axes are changed, the whole plot must be redrawn
        if self.LinkedVar.get() == self.main_params['LinkSpatial']:
            pass
        else:
            self.main_params['LinkSpatial'] = self.LinkedVar.get()
            self.parent.RenewCanvas(ForceRedraw = True)
    def RadioPlane(self, *args):
        # If the shared axes are changed, the whole plot must be redrawn
        if self.PlaneVar.get() == self.main_params['2DSlicePlane']:
            pass
        else:
            self.main_params['2DSlicePlane'] = self.PlaneVar.get()
            self.parent.RenewCanvas()


    def LinkKChanged(self, *args):
        # If the shared axes are changed, the whole plot must be redrawn
        if self.LinkKVar.get() == self.main_params['LinkK']:
            pass
        else:
            self.main_params['LinkK'] = self.LinkKVar.get()
            self.parent.RenewCanvas(ForceRedraw = True)

    def xRelChanged(self, *args):
        # If the shared axes are changed, the whole plot must be redrawn
        if self.xRelVar.get() == self.main_params['xLimsRelative']:
            pass
        else:
            self.main_params['xLimsRelative'] = self.xRelVar.get()
            self.parent.RenewCanvas()


    def CmapChanged(self, *args):
    # Note here that Tkinter passes an event object to onselect()
        if self.cmapvar.get() == self.main_params['ColorMap']:
            pass
        else:
            self.main_params['ColorMap'] = self.cmapvar.get()
            if self.main_params['ColorMap'] in self.oengus.MainParamDict['cmaps_with_green']:

                self.oengus.MainParamDict['ion_color'] = "#{0:02x}{1:02x}{2:02x}".format(int(round(new_cmaps.cmaps['plasma'](0.55)[0]*255)), int(round(new_cmaps.cmaps['plasma'](0.55)[1]*255)), int(round(new_cmaps.cmaps['plasma'](0.55)[2]*255)))
                self.oengus.MainParamDict['electron_color'] ="#{0:02x}{1:02x}{2:02x}".format(int(round(new_cmaps.cmaps['plasma'](0.8)[0]*255)), int(round(new_cmaps.cmaps['plasma'](0.8)[1]*255)), int(round(new_cmaps.cmaps['plasma'](0.8)[2]*255)))

                self.oengus.MainParamDict['ion_fit_color'] = 'r'
                self.oengus.MainParamDict['electron_fit_color'] = 'yellow'

            else:
                self.oengus.MainParamDict['ion_color'] = "#{0:02x}{1:02x}{2:02x}".format(int(round(new_cmaps.cmaps['viridis'](0.45)[0]*255)), int(round(new_cmaps.cmaps['viridis'](0.45)[1]*255)), int(round(new_cmaps.cmaps['viridis'](0.45)[2]*255)))
                self.oengus.MainParamDict['electron_color'] = "#{0:02x}{1:02x}{2:02x}".format(int(round(new_cmaps.cmaps['viridis'](0.75)[0]*255)), int(round(new_cmaps.cmaps['viridis'](0.75)[1]*255)), int(round(new_cmaps.cmaps['viridis'](0.75)[2]*255)))

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
            if int(self.rowNum.get())<1:
                self.rowNum.set(1)
            if int(self.rowNum.get())>self.main_params['MaxRows']:
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
            if int(self.columnNum.get())<1:
                self.columnNum.set(1)
            if int(self.columnNum.get())>self.main_params['MaxCols']:
                self.columnNum.set(self.main_params['MaxCols'])
            if int(self.columnNum.get()) != self.main_params['NumOfCols']:
                self.main_params['NumOfCols'] = int(self.columnNum.get())
                #self.parent.UpdateGridSpec()
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
        tmplist = [self.xleft, self.xright, self.yleft, self.yright]#, self.kleft, self.kright]
        limkeys = ['xLeft', 'xRight', 'yBottom', 'yTop']#, 'kLeft', 'kRight']
        setKeys = ['SetxLim', 'SetyLim']#, 'SetkLim']
        for j in range(len(tmplist)):
            setlims = self.main_params[setKeys[j//2]]
            tmpkey = limkeys[j]

            try:
            #make sure the user types in a a number and that it has changed.
                if abs(float(tmplist[j].get()) - self.main_params[tmpkey]) > 1E-4:
                    self.main_params[tmpkey] = float(tmplist[j].get())
                    to_reload += setlims

            except ValueError:
                #if they type in random stuff, just set it ot the param value
                tmplist[j].set(str(self.main_params[tmpkey]))
        return to_reload

    def CheckIfStrideChanged(self):
        to_reload = False

        try:
            #make sure the user types in a int
            if int(self.PrtlStrideVar.get()) <= 0:
                self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
            if int(self.PrtlStrideVar.get()) != self.main_params['PrtlStride']:
                self.main_params['PrtlStride'] = int(self.PrtlStrideVar.get())
                self.oengus.sims[0].xtra_stride = self.main_params['PrtlStride']
                self.oengus.draw_output()
        except ValueError:
            #if they type in random stuff, just set it to the param value
            self.PrtlStrideVar.set(str(self.main_params['PrtlStride']))
        return to_reload

    def CheckIfSliceChanged(self):
        to_reload = False
        try:
            #make sure the user types in a float
            self.ySliceVar.set(int(np.around(float(self.ySliceVarC_omp.get())*self.parent.c_omp/self.parent.istep)))
            if int(self.ySliceVar.get()) < 0:
                self.ySliceVar.set(0)

            elif int(self.ySliceVar.get()) > self.parent.MaxYInd:
                self.ySliceVar.set(self.parent.MaxYInd)
            self.ySliceVarC_omp.set(self.units_listy[self.ySliceVar.get()])
            if self.ySliceVar.get() != int(np.around(self.main_params['ySlice']*self.parent.MaxYInd)):
                self.main_params['ySlice'] = float(self.ySliceVar.get())/self.parent.MaxYInd
                self.slidery.set(self.ySliceVar.get())
                to_reload += True
        except ValueError:
            #if they type in random stuff, just set it to the param value
            self.ySliceVarC_omp.set(self.units_listy[self.ySliceVar.get()])

        try:
            #make sure the user types in a float
            self.zSliceVar.set(int(np.around(float(self.zSliceVarC_omp.get())*self.parent.c_omp/self.parent.istep)))
            if int(self.zSliceVar.get()) < 0:
                self.zSliceVar.set(0)

            elif int(self.zSliceVar.get()) > self.parent.MaxZInd:
                self.zSliceVar.set(self.parent.MaxZInd)
            self.zSliceVarC_omp.set(self.units_listz[self.zSliceVar.get()])
            if self.zSliceVar.get() != int(np.around(self.main_params['zSlice']*self.parent.MaxZInd)):
                self.main_params['zSlice'] = float(self.OneDSliceVar.get())/self.parent.MaxZInd
                self.sliderz.set(self.zSliceVar.get())
                to_reload += True

        except ValueError:
            #if they type in random stuff, just set it to the param value
            self.TwoDSliceVarC_omp.set(self.units_list2D[self.TwoDSliceVar.get()])
        return to_reload


    def LimChanged(self, *args):
        if self.LimVar.get()==self.main_params['SetxLim']:
            pass
        else:
            self.main_params['SetxLim'] = self.LimVar.get()
            self.oengus.draw_output()

    def yLimChanged(self, *args):
        if self.yLimVar.get()==self.main_params['SetyLim']:
            pass
        else:
            self.main_params['SetyLim'] = self.yLimVar.get()
            self.oengus.draw_output()

    #def kLimChanged(self, *args):
    #    if self.kLimVar.get()==self.main_params['SetkLim']:
    #        pass
    #    else:
    #        self.main_params['SetkLim'] = self.kLimVar.get()
    #        self.parent.RenewCanvas()


    def SettingsCallback(self, e):
        to_reload = self.CheckIfLimsChanged()
        to_reload += self.CheckIfStrideChanged()
        #to_reload += self.CheckIfSliceChanged()
        if to_reload:
            self.oengus.draw_output()



    def OnClosing(self):
        #self.parent.settings_window = None
        self.destroy()
