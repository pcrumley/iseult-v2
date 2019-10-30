import matplotlib
import numpy as np
import numpy.ma as ma
import sys
sys.path.append('../')

import new_cmaps
from new_cnorms import PowerNormWithNeg, PowerNormFunc
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import FuncFormatter

class ScalarFldsPlot:
    # A dictionary of all of the parameters for this plot with the default parameters

    plot_param_dict = {'twoD': 0,
                       'flds_type': 'density',
                       'show_cbar': True,
                       'set_color_limits': False,
                       'v_min': 0,
                       'v_max' : 10,
                       'set_v_min': False,
                       'set_v_max': False,
                       'show_labels' : True,
                       'show_shock' : False,
                       'OutlineText': True,
                       'spatial_x': True,
                       'spatial_y': False,
                       'interpolation': 'none',
                       'normalize_density': True, # Normalize density to it's upstream values
                       'cnorm_type': 'Linear', # Colormap norm;  options are Pow or Linear
                       'cpow_num': 0.6, # Used in the PowerNorm
                       'UseDivCmap': False,
                       'div_midpoint': 0.0,
                       'stretch_colors': False,
                       'cmap': 'None', # If cmap is none, the plot will inherit the parent's cmap
                       'show_cpu_domains': False, # plots lines showing how the CPUs are divvying up the computational region
                       'face_color': 'gainsboro'}

    gradient =  np.linspace(0, 1, 256)# A way to make the colorbar display better
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict, sim):
        self.sim = sim
        self.param_dict = {}
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos
        self.chartType = 'ScalarFldsPlot'
        self.parent = parent
        self.figure = self.parent.figure
        self.InterpolationMethods = ['none','nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def norm(self, vmin=None, vmax=None):
        if self.GetPlotParam('cnorm_type') =="Linear":
            if self.GetPlotParam('UseDivCmap'):
                return PowerNormWithNeg(1.0, vmin, vmax, midpoint = self.GetPlotParam('div_midpoint'), stretch_colors = self.GetPlotParam('stretch_colors'))
            else:
                return mcolors.Normalize(vmin, vmax)
        elif self.GetPlotParam('cnorm_type') == "Log":
            return  mcolors.LogNorm(vmin, vmax)
        else:
            return PowerNormWithNeg(self.GetPlotParam('cpow_num'), vmin, vmax, div_cmap = self.GetPlotParam('UseDivCmap'),midpoint = self.GetPlotParam('div_midpoint'), stretch_colors = self.GetPlotParam('stretch_colors'))

    def update_data(self, n):
        ''' A Helper function that loads the data for the plot'''


    def draw(self, n):
        if self.GetPlotParam('cmap') == 'None':
            if self.GetPlotParam('UseDivCmap'):
                self.cmap = self.parent.MainParamDict['DivColorMap']
            else:
                self.cmap = self.parent.MainParamDict['ColorMap']

        else:
            self.cmap = self.GetPlotParam('cmap')

        self.dens_color = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.5)
                # get c_omp and istep to convert cells to physical units

        # FIND THE SLICE
        MaxZInd = len(self.sim.get_data(n, data_type='axes', attribute='z')['data']) - 1
        MaxYInd = len(self.sim.get_data(n, data_type='axes', attribute='y')['data']) - 1

        self.ySlice = int(np.around(self.MainParamDict['ySlice']*self.MaxYInd))
        self.zSlice = int(np.around(self.MainParamDict['zSlice']*self.MaxZInd))
        self.scalar_fld = self.sim.get_data(n, data_type = 'scalar_flds', fld = self.GetPlotParam('flds_type'))


        self.c_omp = self.sim.get_data(n, data_type = 'param', attribute = 'c_omp')
        self.istep = self.sim.get_data(n, data_type = 'param', attribute = 'istep')
        if self.GetPlotParam('OutlineText'):
            self.annotate_kwargs = {'horizontalalignment': 'right',
            'verticalalignment': 'top',
            'size' : self.parent.MainParamDict['annotateTextSize'],
            'path_effects' : [PathEffects.withStroke(linewidth=1.5,foreground="k")]
            }
        else:
            self.annotate_kwargs = {'horizontalalignment' : 'right',
            'verticalalignment' : 'top',
            'size' : self.parent.MainParamDict['annotateTextSize']}

        # Set the tick color
        tick_color = 'black'

        # Create a gridspec to handle spacing better
        self.gs = gridspec.GridSpecFromSubplotSpec(100,100, subplot_spec = self.parent.gs0[self.pos])#, bottom=0.2,left=0.1,right=0.95, top = 0.95)

        # Now that the data is loaded, start making the plots
        if self.GetPlotParam('twoD'):
            # Link up the spatial axes if desired
            self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])



            if self.parent.MainParamDict['2DSlicePlane'] ==0: # x-y plane
                if self.parent.MainParamDict['ImageAspect']:
                    self.cax = self.axes.imshow(self.scalar_fld['data'][self.parent.zSlice,:,:], norm = self.norm(), origin = 'lower')
                else:
                    self.cax = self.axes.imshow(self.scalar_fld['data'][self.parent.zSlice,:,:], norm = self.norm(), origin = 'lower',
                                                aspect = 'auto')
            elif self.parent.MainParamDict['2DSlicePlane'] ==1: # x-z plane
                if self.parent.MainParamDict['ImageAspect']:
                    self.cax = self.axes.imshow(self.scalar_fld['data'][:,self.parent.ySlice,:], norm = self.norm(), origin = 'lower')
                else:
                    self.cax = self.axes.imshow(self.scalar_fld['data'][:,self.parent.ySlice,:], norm = self.norm(), origin = 'lower',
                                                aspect = 'auto')


            self.ymin = 0
            self.ymax =  self.cax.get_array().shape[0]/self.c_omp*self.istep
            self.xmin = 0
            self.xmax =  self.cax.get_array().shape[1]/self.c_omp*self.istep

            self.vmin = self.cax.get_array().min()
            if self.GetPlotParam('set_v_min'):
                self.vmin = self.GetPlotParam('v_min')
            self.vmax = self.cax.get_array().max()
            if self.GetPlotParam('set_v_max'):
                self.vmax = self.GetPlotParam('v_max')
            if self.GetPlotParam('UseDivCmap') and not self.GetPlotParam('stretch_colors'):
                self.vmax = max(np.abs(self.vmin), self.vmax)
                self.vmin = -self.vmax
            self.cax.norm.vmin = self.vmin
            self.cax.norm.vmax = self.vmax
            self.cax.set_interpolation(self.GetPlotParam('interpolation'))
            self.cax.set_cmap(new_cmaps.cmaps[self.cmap])
            self.cax.set_extent([self.xmin, self.xmax, self.ymin, self.ymax])

            self.shockline_2d = self.axes.axvline(self.parent.shock_loc,
                                                    linewidth = 1.5,
                                                    linestyle = '--',
                                                    color = self.parent.shock_color,
                                                    path_effects=[PathEffects.Stroke(linewidth=2, foreground='k'),
                                                    PathEffects.Normal()])
            self.shockline_2d.set_visible(self.GetPlotParam('show_shock'))

            self.an_2d = self.axes.annotate(self.two_d_label,
                                            xy = (0.9,.9),
                                            xycoords= 'axes fraction',
                                            color = 'white',
                                            **self.annotate_kwargs)
            self.an_2d.set_visible(self.GetPlotParam('show_labels'))


            self.axC = self.figure.add_subplot(self.gs[self.parent.cbar_extent[0]:self.parent.cbar_extent[1], self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])

            if self.parent.MainParamDict['HorizontalCbars']:
                self.cbar = self.axC.imshow(self.gradient, aspect='auto',
                                            cmap=new_cmaps.cmaps[self.cmap])
                # Make the colobar axis more like the real colorbar
                self.cbar.set_extent([0, 1.0, 0, 1.0])
                self.axC.tick_params(axis='x',
                                which = 'both', # bothe major and minor ticks
                                top = False, # turn off top ticks
                                labelsize=self.parent.MainParamDict['NumFontSize'])

                self.axC.tick_params(axis='y',          # changes apply to the y-axis
                                which='both',      # both major and minor ticks are affected
                                left=False,      # ticks along the bottom edge are off
                                right=False,         # ticks along the top edge are off
                                labelleft=False)
            else: #Cbar is on the vertical
                self.cbar = self.axC.imshow(np.transpose(self.gradient)[::-1], aspect='auto',
                                            cmap=new_cmaps.cmaps[self.cmap], origin='upper')
                # Make the colobar axis more like the real colorbar
                self.cbar.set_extent([0, 1.0, 0, 1.0])
                self.axC.tick_params(axis='x',
                                which = 'both', # bothe major and minor ticks
                                top = False, # turn off top ticks
                                bottom = False, # turn off top ticks
                                labelbottom = False, # turn off top ticks
                                labelsize=self.parent.MainParamDict['NumFontSize'])

                self.axC.tick_params(axis='y',          # changes apply to the y-axis
                                which='both',      # both major and minor ticks are affected
                                left=False,      # ticks along the bottom edge are off
                                right=True,         # ticks along the top edge are off
                                labelleft=False,
                                labelright = True,
                                labelsize = self.parent.MainParamDict['NumFontSize'])

            if not self.GetPlotParam('show_cbar'):
                self.axC.set_visible(False)
            else:
                self.CbarTickFormatter()

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.GetPlotParam('face_color'))
            else:
                self.axes.set_facecolor(self.GetPlotParam('face_color'))

            self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=tick_color)

            if self.parent.MainParamDict['SetxLim']:
                if self.parent.MainParamDict['xLimsRelative']:
                    self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
                                       self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
                else:
                    self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(self.xmin,self.xmax)

            if self.parent.MainParamDict['SetyLim']:
                self.axes.set_ylim(self.parent.MainParamDict['yBottom']*self.c_omp/self.istep, self.parent.MainParamDict['yTop']*self.c_omp/self.istep)
            else:
                self.axes.set_ylim(self.ymin, self.ymax)
            self.axes.set_xlabel(r'$x\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                self.axes.set_ylabel(r'$y\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(r'$z\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])


        else:
            self.xaxis =  self.sim.get_data(n, data_type = 'axes', attribute = 'x')
            # Do the 1D Plots
            self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])

            # Make the 1-D plots
            if self.parent.MainParamDict['Average1D']:
                self.linedens = self.axes.plot(self.xaxis['data'], np.average(self.scalar_fld['data'].reshape(-1,self.scalar_fld['data'].shape[-1]), axis = 0), color = self.dens_color)
            else:
                self.linedens = self.axes.plot(self.xaxis['data'], self.scalar_fld['data'][self.zSlice,self.ySlice,:], color = self.dens_color)

            #if self.GetPlotParam('normalize_density'):
            #    self.linedens[0].set_data(self.linedens[0].get_data()[0], self.linedens[0].get_data()[1]*self.ppc0**(-1))

            #### Set the ylims... there is a problem where it scales the ylims for the invisible lines:
            min_max = [self.linedens[0].get_data()[1].min(), self.linedens[0].get_data()[1].max()]
            dist = min_max[1]-min_max[0]
            min_max[0] -= 0.04*dist
            min_max[1] += 0.04*dist
            self.axes.set_ylim(min_max)
            #self.shock_line =self.axes.axvline(self.parent.shock_loc, linewidth = 1.5, linestyle = '--', color = self.parent.shock_color, path_effects=[PathEffects.Stroke(linewidth=2, foreground='k'),
            #        PathEffects.Normal()])
            #self.shock_line.set_visible(self.GetPlotParam('show_shock'))

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.GetPlotParam('face_color'))
            else:
                self.axes.set_facecolor(self.GetPlotParam('face_color'))

            self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=tick_color)

            #if self.parent.MainParamDict['SetxLim']:
            #    if self.parent.MainParamDict['xLimsRelative']:
            #        self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
            #                           self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
            #    else:
            #        self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            #else:
            self.axes.set_xlim(self.xaxis['data'][0],self.xaxis['data'][-1])

            if self.GetPlotParam('set_v_min'):
                self.axes.set_ylim(bottom = self.GetPlotParam('v_min'))
            if self.GetPlotParam('set_v_max'):
                self.axes.set_ylim(top = self.GetPlotParam('v_max'))

            # Handle the axes labeling


            #if self.GetPlotParam('normalize_density'):
            #    tmp_str += r'$\ [n_0]$'
            self.axes.set_xlabel(self.xaxis['label'], labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            self.axes.set_ylabel(self.scalar_fld['1d_label'], labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])


        #if self.GetPlotParam('show_cpu_domains'):
        #    self.parent.SetCpuDomainLines()

    def CbarTickFormatter(self):
        ''' A helper function that sets the cbar ticks & labels. This used to be
        easier, but because I am no longer using the colorbar class i have to do
        stuff manually.'''
        clim = np.copy(self.cax.get_clim())
        if self.GetPlotParam('show_cbar'):
            if self.GetPlotParam('cnorm_type') == "Log":
                self.cbar.set_extent([np.log10(clim[0]),np.log10(clim[1]),0,1])
                self.axC.set_xlim(np.log10(clim[0]),np.log10(clim[1]))

            elif self.GetPlotParam('cnorm_type') == "Pow":
                # re-create the gradient with the data values
                # First make a colorbar in the negative region that is linear in the pow_space
                data_range = np.linspace(clim[0],clim[1],512)

                cbardata = PowerNormFunc(data_range, vmin = data_range[0], vmax = data_range[-1], gamma = self.GetPlotParam('cpow_num'), midpoint = self.GetPlotParam('div_midpoint'), div_cmap = self.GetPlotParam('UseDivCmap'), stretch_colors = self.GetPlotParam('stretch_colors'))
                cbardata = np.vstack((cbardata,cbardata))
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_data(cbardata)
                    self.cbar.set_extent([clim[0],clim[1],0,1])
                    self.axC.set_xlim(clim[0],clim[1])
                else:
                    self.cbar.set_data(np.transpose(cbardata)[::-1])
                    self.cbar.set_extent([0,1,clim[0],clim[1]])
                    self.axC.set_ylim(clim[0],clim[1])
                    self.axC.locator_params(axis='y',nbins=6)

            elif self.GetPlotParam('cnorm_type') == "Linear" and self.GetPlotParam('UseDivCmap'):
                # re-create the gradient with the data values
                # First make a colorbar in the negative region that is linear in the pow_space
                data_range = np.linspace(clim[0],clim[1],512)

                cbardata = PowerNormFunc(data_range, vmin = data_range[0], vmax = data_range[-1], gamma = 1.0, div_cmap = self.GetPlotParam('UseDivCmap'), midpoint = self.GetPlotParam('div_midpoint'), stretch_colors = self.GetPlotParam('stretch_colors'))
                cbardata = np.vstack((cbardata,cbardata))
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_data(cbardata)
                    self.cbar.set_extent([clim[0],clim[1],0,1])
                    self.axC.set_xlim(clim[0],clim[1])
                else:
                    self.cbar.set_data(np.transpose(cbardata)[::-1])
                    self.cbar.set_extent([0,1,clim[0],clim[1]])
                    self.axC.set_ylim(clim[0],clim[1])
                    self.axC.locator_params(axis='y',nbins=6)

            else:# self.GetPlotParam('cnorm_type') == "Linear":
                if self.parent.MainParamDict['HorizontalCbars']:
#                    self.cbar.set_data(self.gradient)
                    self.cbar.set_extent([clim[0],clim[1],0,1])
                    self.axC.set_xlim(clim[0],clim[1])
                else:
#                    self.cbar.set_data(np.transpose(self.gradient)[::-1])
                    self.cbar.set_extent([0,1,clim[0],clim[1]])
                    self.axC.set_ylim(clim[0],clim[1])
                    self.axC.locator_params(axis='y',nbins=6)
    def refresh(self, n):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown.  If
        hasn't changed, or isn't viewed, don't touch it. The difference between this and last
        time, is that we won't actually do any drawing in the plot. The plot
        will be redrawn after all subplots data is changed. '''
        self.scalar_fld = self.sim.get_data(n, data_type = 'scalar_flds', fld = self.GetPlotParam('flds_type'))
        self.xaxis =  self.sim.get_data(n, data_type = 'axes', attribute = 'x')
        self.c_omp = self.sim.get_data(n, data_type = 'param', attribute = 'c_omp')
        self.istep = self.sim.get_data(n, data_type = 'param', attribute = 'istep')
        # Main goal, only change what is showing..
        # First do the 1D plots, because it is simpler
        if self.GetPlotParam('twoD') == 0:

            if self.parent.MainParamDict['Average1D']:
                self.linedens[0].set_data(self.xaxis['data'], np.average(self.scalar_fld['data'].reshape(-1,self.scalar_fld['data'].shape[-1]), axis = 0))
            else: # x-y plane
                self.linedens[0].set_data(self.xaxis['data'], self.scalar_fld['data'][self.parent.zSlice,self.parent.ySlice,:])

            #### Set the ylims...
            min_max = [self.linedens[0].get_data()[1].min(),self.linedens[0].get_data()[1].max()]
            dist = min_max[1]-min_max[0]
            min_max[0] -= 0.04*dist
            min_max[1] += 0.04*dist
            self.axes.set_ylim(min_max)
            if self.GetPlotParam('set_v_min'):
                self.axes.set_ylim(bottom = self.GetPlotParam('v_min'))
            if self.GetPlotParam('set_v_max'):
                self.axes.set_ylim(top = self.GetPlotParam('v_max'))
            #if self.GetPlotParam('show_shock'):
            #    self.shock_line.set_xdata([self.parent.shock_loc,self.parent.shock_loc])

            if self.parent.MainParamDict['SetxLim']:
                #if self.parent.MainParamDict['xLimsRelative']:
                #    self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
                #                       self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
                #else:
                self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(self.xaxis_values[0], self.xaxis_values[-1])


        else: # Now refresh the plot if it is 2D
            if self.parent.MainParamDict['2DSlicePlane'] == 0: # x-y plane
                self.cax.set_data(self.scalar_fld['data'][self.parent.zSlice,:,:])
            elif self.parent.MainParamDict['2DSlicePlane'] == 1: # x-z plane
                self.cax.set_data(self.scalar_fld['data'][:,self.parent.ySlice,:])

            #if self.GetPlotParam('normalize_density'):
            #    self.cax.set_data(self.cax.get_array()/self.ppc0)


            self.ymin = 0
            self.ymax =  self.cax.get_array().shape[0]/self.c_omp*self.istep
            self.xmin = 0
            self.xmax =  self.xaxis['data'][-1]
            self.cax.set_extent([self.xmin,self.xmax, self.ymin, self.ymax])
            if self.parent.MainParamDict['SetxLim']:
                #if self.parent.MainParamDict['xLimsRelative']:
                #    self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
                #                       self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
                #else:
                self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(self.xmin,self.xmax)

            if self.parent.MainParamDict['SetyLim']:
                self.axes.set_ylim(self.parent.MainParamDict['yBottom'],self.parent.MainParamDict['yTop'])
            else:
                self.axes.set_ylim(self.ymin,self.ymax)

            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                self.axes.set_ylabel(r'$y\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(r'$z\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            self.vmin = self.cax.get_array().min()
            if self.GetPlotParam('set_v_min'):
                self.vmin = self.GetPlotParam('v_min')
            self.vmax = self.cax.get_array().max()
            if self.GetPlotParam('set_v_max'):
                self.vmax = self.GetPlotParam('v_max')
            if self.GetPlotParam('UseDivCmap') and not self.GetPlotParam('stretch_colors'):
                self.vmax = max(np.abs(self.vmin), self.vmax)
                self.vmin = -self.vmax
            self.cax.norm.vmin = self.vmin
            self.cax.norm.vmax = self.vmax
            if self.GetPlotParam('show_cbar'):
                self.CbarTickFormatter()
            #if self.GetPlotParam('show_shock'):
            #    self.shockline_2d.set_xdata([self.parent.shock_loc,self.parent.shock_loc])

    def GetPlotParam(self, keyname):
        return self.param_dict[keyname]
