#!/usr/bin/env pythonw
import matplotlib, sys
sys.path.append('../utils')

import numpy as np
import numpy.ma as ma
import new_cmaps
from new_cnorms import PowerNormWithNeg
from Numba2DHist import Fast2DHist, Fast2DWeightedHist
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects

class PhasePanel:
    # A dictionary of all of the parameters for this plot with the default parameters

    plot_param_dict = {'twoD' : 1,
                       'mom_dim': 0,
                       'masked': 1,
                       'cnorm_type': 'Log', #Colormap normalization. Opts are Log or Linear
                       'prtl_type': 'ions',
                       'x_val': 'x',
                       'y_val': 'px',
                       'weights': None,
                       'cpow_num': 0.6,
                       'show_cbar': True,
                       'weighted': False,
                       'show_shock': False,
                       'show_int_region': True,
                       'x_bins' : 200,
                       'y_bins' : 200,
                       'v_min': -2.0,
                       'v_max' : 0,
                       'set_v_min': False,
                       'set_v_max': False,
                       'p_min': -2.0,
                       'p_max' : 2,
                       'set_E_min' : False,
                       'E_min': 1.0,
                       'set_E_max': False,
                       'E_max': 200.0,
                       'set_p_min': False,
                       'set_p_max': False,
                       'spatial_x': True,
                       'spatial_y': False,
                       'interpolation': 'nearest',
                       'face_color': 'gainsboro'}


    gradient =  np.linspace(0, 1, 256)# A way to make the colorbar display better
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos
        self.chartType = 'PhasePlot'
        self.figure = self.parent.figure
        self.InterpolationMethods = ['none','nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']


    def norm(self, vmin=None, vmax=None):
        if self.GetPlotParam('cnorm_type') == "Log":
            return  mcolors.LogNorm(vmin, vmax)

        else:
            return mcolors.Normalize(vmin, vmax)


    def update_labels_and_colors(self):
        # set the colors
        if self.GetPlotParam('prtl_type') == 0: #protons
            self.energy_color = self.parent.ion_color
        else: #electons
            self.energy_color = self.parent.electron_color

        for line in self.IntRegionLines:
            line.set_color(self.energy_color)
        #set the xlabels
        if self.parent.MainParamDict['DoLorentzBoost'] and np.abs(self.parent.MainParamDict['GammaBoost'])>1E-8:
            self.x_label = r'$x\prime\ [c/\omega_{\rm pe}]$'
        else:
            self.x_label = r'$x\ [c/\omega_{\rm pe}]$'
        #set the ylabel
        self.y_label  = self.ylabel_list[self.parent.MainParamDict['DoLorentzBoost']][self.GetPlotParam('prtl_type')][self.GetPlotParam('mom_dim')]

    def draw(self):
        # In order to speed up the plotting, we only recalculate everything
        # if necessary.
        self.IntRegionLines = []
        # Figure out the color and ylabel
        # Choose the particle type and px, py, or pz
        self.UpdateLabelsandColors()

        self.xmin = self.hist2d[2][0]
        self.xmax = self.hist2d[2][-1]

        self.ymin = self.hist2d[1][0]
        self.ymax = self.hist2d[1][-1]


        if self.GetPlotParam('masked'):
            self.tick_color = 'k'
        else:
            self.tick_color = 'white'


        self.clim = list(self.hist2d[3])

        if self.GetPlotParam('set_v_min'):
            self.clim[0] = 10**self.GetPlotParam('v_min')
        if self.GetPlotParam('set_v_max'):
            self.clim[1] = 10**self.GetPlotParam('v_max')


        self.gs = gridspec.GridSpecFromSubplotSpec(100,100, subplot_spec = self.parent.gs0[self.pos])#, bottom=0.2,left=0.1,right=0.95, top = 0.95)

        self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])

        self.cax = self.axes.imshow(self.hist2d[0],
                                    cmap = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']],
                                    norm = self.norm(), origin = 'lower',
                                    aspect = 'auto',
                                    interpolation=self.GetPlotParam('interpolation'))

        self.cax.set_extent([self.xmin, self.xmax, self.ymin, self.ymax])

        self.cax.set_clim(self.clim)

        self.shock_line = self.axes.axvline(self.parent.shock_loc, linewidth = 1.5, linestyle = '--', color = self.parent.shock_color, path_effects=[PathEffects.Stroke(linewidth=2, foreground='k'),
                   PathEffects.Normal()])
        if not self.GetPlotParam('show_shock'):
            self.shock_line.set_visible(False)




        self.axC = self.figure.add_subplot(self.gs[self.parent.cbar_extent[0]:self.parent.cbar_extent[1], self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])


        # Technically I should use the colorbar class here,
        # but I found it annoying in some of it's limitations.
        if self.parent.MainParamDict['HorizontalCbars']:
            self.cbar = self.axC.imshow(self.gradient, aspect='auto',
                                    cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']])
            # Make the colobar axis more like the real colorbar
            self.axC.tick_params(axis='x',
                                which = 'both', # bothe major and minor ticks
                                top = False, # turn off top ticks
                                labelsize=self.parent.MainParamDict['NumFontSize'])

            self.axC.tick_params(axis='y',          # changes apply to the y-axis
                                which='both',      # both major and minor ticks are affected
                                left=False,      # ticks along the bottom edge are off
                                right=False,         # ticks along the top edge are off
                                labelleft=False)

        else:
            self.cbar = self.axC.imshow(np.transpose(self.gradient)[::-1], aspect='auto', origin='upper',
                                    cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']])
            # Make the colobar axis more like the real colorbar
            self.axC.tick_params(axis='x',
                                which = 'both', # bothe major and minor ticks
                                top = False, # turn off top ticks
                                bottom = False,
                                labelbottom = False,
                                labelsize=self.parent.MainParamDict['NumFontSize'])

            self.axC.tick_params(axis='y',          # changes apply to the y-axis
                                which='both',      # both major and minor ticks are affected
                                left=False,      # ticks along the bottom edge are off
                                right=True,         # ticks along the top edge are off
                                labelleft=False,
                                labelright=True,
                                labelsize=self.parent.MainParamDict['NumFontSize'])

        self.cbar.set_extent([0, 1.0, 0, 1.0])

        if not self.GetPlotParam('show_cbar'):
            self.axC.set_visible(False)

        if int(matplotlib.__version__[0]) < 2:
            self.axes.set_axis_bgcolor(self.GetPlotParam('face_color'))
        else:
            self.axes.set_facecolor(self.GetPlotParam('face_color'))
        self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=self.tick_color)
        self.axes.set_xlabel(self.x_label, labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
        self.axes.set_ylabel(self.y_label, labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])

        self.refresh()

    def refresh(self):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown. If
        hasn't changed, or isn't viewed, don't touch it. The difference between this and last
        time, is that we won't actually do any drawing in the plot. The plot
        will be redrawn after all subplots data is changed. '''

        if sim is None:
            sim = self.parent.sim
        if n is None:
            n = self.parent.cur_time
        # Generate the X-axis values
        c_omp = sim.get_data(n, data_class = 'param', attribute = 'c_omp')

        x_values = sim.get_data(n, data_class = 'prtls',
                prtl_type = self.param_dict['prtl_type'],
                attribute = self.param_dict['x_val'])
        y_values = sim.get_data(n, data_class = 'prtls',
                prtl_type = self.param_dict['prtl_type'],
                attribute = self.param_dict['y_val'])
        if self.param_dict['weighted']:
            weights = sim.get_data(n, data_class = 'prtls',
                    prtl_type = self.param_dict['prtl_type'],
                    attribute = self.param_dict['weights'])
        xmin = np.min(x_values['data'])
        xmax = np.max(x_values['data'])
        xmax = xmax if xmax > xmin else xmin + 1

        ymin = np.min(y_values['data'])
        ymax = np.max(y_values['data'])
        ymax = ymax if ymax > ymin else ymin + 1

        if self.param_dict['weighted']:
            hist2d = Fast2DWeightedHist(sy_values['data'], x_values['data'], weights['data'], ymin, ymax, self.param_dict['pbins'], xmin, xmax, self.param_dict['xbins'])
        else:
            hist2d = Fast2DHist(y_values['data'], x_values['data'], ymin, ymax, self.param_dict['pbins'], xmin, xmax, self.param_dict['xbins'])
        # Main goal, only change what is showing..
        self.xmin = self.hist2d[2][0]
        self.xmax = self.hist2d[2][-1]
        self.ymin = self.hist2d[1][0]
        self.ymax = self.hist2d[1][-1]
        self.clim = list(self.hist2d[3])

        self.cax.set_data(self.hist2d[0])

        self.cax.set_extent([self.xmin,self.xmax, self.ymin, self.ymax])


        if self.GetPlotParam('set_v_min'):
            self.clim[0] =  10**self.GetPlotParam('v_min')
        if self.GetPlotParam('set_v_max'):
            self.clim[1] =  10**self.GetPlotParam('v_max')

        self.cax.set_clim(self.clim)
        if self.GetPlotParam('show_cbar'):
            self.CbarTickFormatter()


        if self.GetPlotParam('show_shock'):
            self.shock_line.set_xdata([self.parent.shock_loc,self.parent.shock_loc])

        self.UpdateLabelsandColors()
        self.axes.set_xlabel(self.x_label, labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
        self.axes.set_ylabel(self.y_label, labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])

        if self.GetPlotParam('set_p_min'):
            self.ymin = self.GetPlotParam('p_min')
        if self.GetPlotParam('set_p_max'):
            self.ymax = self.GetPlotParam('p_max')
        self.axes.set_ylim(self.ymin, self.ymax)

        if self.parent.MainParamDict['SetxLim'] and self.parent.MainParamDict['LinkSpatial'] == 1:
            if self.parent.MainParamDict['xLimsRelative']:
                self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
                                   self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
            else:
                self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])

        else:
            self.axes.set_xlim(self.xmin,self.xmax)

    def CbarTickFormatter(self):
        ''' A helper function that sets the cbar ticks & labels. This used to be
        easier, but because I am no longer using the colorbar class i have to do
        stuff manually.'''
        clim = np.copy(self.cax.get_clim())
        if self.GetPlotParam('show_cbar'):
            if self.GetPlotParam('cnorm_type') == "Log":
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_extent([np.log10(clim[0]),np.log10(clim[1]),0,1])
                    self.axC.set_xlim(np.log10(clim[0]),np.log10(clim[1]))
                    self.axC.xaxis.set_label_position("top")
                    if self.GetPlotParam('prtl_type') ==0:
                        self.axC.set_xlabel(r'$\log{\ \ f_i(p)}$', size = self.parent.MainParamDict['AxLabelSize'])#, labelpad =15, rotation = -90)
                    else:
                        self.axC.set_xlabel(r'$\log{\ \ f_e(p)}$', size = self.parent.MainParamDict['AxLabelSize'])#, size = 12,labelpad =15, rotation = -90)

                else:
                    self.cbar.set_extent([0,1,np.log10(clim[0]),np.log10(clim[1])])
                    self.axC.set_ylim(np.log10(clim[0]),np.log10(clim[1]))
                    self.axC.locator_params(axis='y',nbins=6)
                    self.axC.yaxis.set_label_position("right")
                    if self.GetPlotParam('prtl_type') ==0:
                        self.axC.set_ylabel(r'$\log{\ \ f_i(p)}$', labelpad = self.parent.MainParamDict['cbarLabelPad'], rotation = -90, size = self.parent.MainParamDict['AxLabelSize'])
                    else:
                        self.axC.set_ylabel(r'$\log{\ \ f_e(p)}$', labelpad = self.parent.MainParamDict['cbarLabelPad'], rotation = -90, size = self.parent.MainParamDict['AxLabelSize'])

            else:# self.GetPlotParam('cnorm_type') == "Linear":
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_extent([clim[0], clim[1], 0, 1])
                    self.axC.set_xlim(clim[0], clim[1])
                    if self.GetPlotParam('prtl_type') ==0:
                        self.axC.set_xlabel(r'$f_i(p)$', size = self.parent.MainParamDict['AxLabelSize'])
                    else:
                        self.axC.set_xlabel(r'$f_e(p)$', size = self.parent.MainParamDict['AxLabelSize'])

                else:
                    self.cbar.set_extent([0, 1, clim[0], clim[1]])
                    self.axC.set_ylim(clim[0], clim[1])
                    self.axC.locator_params(axis='y', nbins=6)
                    self.axC.yaxis.set_label_position("right")
                    if self.GetPlotParam('prtl_type') ==0:
                        self.axC.set_ylabel(r'$f_i(p)$', labelpad = self.parent.MainParamDict['cbarLabelPad'], rotation = -90, size = self.parent.MainParamDict['AxLabelSize'])
                    else:
                        self.axC.set_ylabel(r'$f_e(p)$', labelpad = self.parent.MainParamDict['cbarLabelPad'], rotation = -90, size = self.parent.MainParamDict['AxLabelSize'])

    def calc_hist_2D(self, sim = None, n = None):


        # Choose the particle type and px, py, or pz
        if self.GetPlotParam('prtl_type') == 0: #protons
            self.x_values = getattr(output,'xi')/self.c_omp
                    self.weights = getattr(output,'che')
                if self.GetPlotParam('mom_dim') == 0:
                    self.y_values = getattr(output,'ue')
                if self.GetPlotParam('mom_dim') == 1:
                    self.y_values = getattr(output,'ve')
                if self.GetPlotParam('mom_dim') == 2:
                    self.y_values = getattr(output,'we')

            pmin = 0.0 if len(self.y_values) == 0 else min(self.y_values)
            self.pmax = 0.0 if len(self.y_values) == 0 else max(self.y_values)
            self.pmax = self.pmax if (self.pmax != self.pmin) else self.pmin + 1

            self.xmax = self.xmax if (self.xmax != self.xmin) else self.xmin + 1

            if self.GetPlotParam('set_E_min') or self.GetPlotParam('set_E_max'):
                # We need to calculate the total energy of each particle in
                # units m_e c^2

                # First load the data. We require all 3 dimensions of momentum
                # to determine the energy in the downstream frame
                if self.GetPlotParam('prtl_type') == 0:
                    u = getattr(output,'ui')
                    v = getattr(output,'vi')
                    w = getattr(output,'wi')

                if self.GetPlotParam('prtl_type') == 1: #electons
                    self.x_values = getattr(output,'xe')/self.c_omp
                    u = getattr(output,'ue')
                    v = getattr(output,'ve')
                    w = getattr(output,'we')

                # Now calculate LF of the particles in downstream restframe
                energy = np.sqrt(u**2+v**2+w**2+1)
                # If they are electrons this already the energy in units m_e c^2.
                # Otherwise...
                if self.GetPlotParam('prtl_type')==0:
                    energy *= getattr(output,'mi')/getattr(output,'me')

                # Now find the particles that fall in our range
                if self.GetPlotParam('set_E_min'):
                    inRange = energy >= self.GetPlotParam('E_min')
                    if self.GetPlotParam('set_E_max'):
                        inRange *= energy <= self.GetPlotParam('E_max')
                elif self.GetPlotParam('set_E_max'):
                    inRange = energy <= self.GetPlotParam('E_max')
                if self.GetPlotParam('weighted'):
                    self.hist2d = Fast2DWeightedHist(self.y_values[inRange], self.x_values[inRange], self.weights[inRange], self.pmin,self.pmax, self.GetPlotParam('pbins'), self.xmin,self.xmax, self.GetPlotParam('xbins')), [self.pmin, self.pmax], [self.xmin, self.xmax]
                else:
                    self.hist2d = Fast2DHist(self.y_values[inRange], self.x_values[inRange], self.pmin,self.pmax, self.GetPlotParam('pbins'), self.xmin,self.xmax, self.GetPlotParam('xbins')), [self.pmin, self.pmax], [self.xmin, self.xmax]
            else:
                if self.GetPlotParam('weighted'):
                    self.hist2d = Fast2DWeightedHist(self.y_values, self.x_values, self.weights, self.pmin,self.pmax, self.GetPlotParam('pbins'), self.xmin,self.xmax, self.GetPlotParam('xbins')), [self.pmin, self.pmax], [self.xmin, self.xmax]
                else:
                    self.hist2d = Fast2DHist(self.y_values, self.x_values, self.pmin,self.pmax, self.GetPlotParam('pbins'), self.xmin,self.xmax, self.GetPlotParam('xbins')), [self.pmin, self.pmax], [self.xmin, self.xmax]

            try:
                if self.GetPlotParam('masked'):
                    zval = ma.masked_array(self.hist2d[0])
                    zval[zval == 0] = ma.masked
                    zval *= float(zval.max())**(-1)
                    tmplist = [zval[~zval.mask].min(), zval.max()]
                else:
                    zval = np.copy(self.hist2d[0])
                    zval[zval==0] = 0.5
                    zval *= float(zval.max())**(-1)
                    tmplist = [zval.min(), zval.max()]
            except ValueError:
                tmplist = [0.1,1]
            self.hist2d = zval, self.hist2d[1], self.hist2d[2], tmplist

    def GetPlotParam(self, keyname):
        return self.param_dict[keyname]
