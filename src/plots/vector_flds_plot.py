import matplotlib
import numpy as np
import sys
sys.path.append('../utils')

import new_cmaps
from new_cnorms import PowerNormWithNeg, PowerNormFunc
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import FuncFormatter
import matplotlib.transforms as mtransforms

class vectorFldsPlot:
    # A dictionary of all of the parameters for this plot with the default parameters

    plot_param_dict = {'twoD': 0,
                       'field_type': 'B',
                       'sim_num': 0,
                       'show_x': 1,
                       'show_y' : 1,
                       'show_z' : 1,
                       'show_cbar': True,
                       'v_min': 0,
                       'v_max' : 10,
                       'set_v_min': False,
                       'set_v_max': False,
                       'show_shock' : False,
                       'show_FFT_region': False,
                       'OutlineText': True,
                       'spatial_x': True,
                       'spatial_y': False,
                       'show_labels': True,
                       'normalize_fields': True, # Normalize fields to their upstream values
                       'cnorm_type': 'Linear', # Colormap norm;  options are Log, Pow or Linear
                       'cpow_num': 1.0, # Used in the PowerNorm
                       'div_midpoint': 0.0, # The cpow color norm normalizes data to [0,1] using np.sign(x-midpoint)*np.abs(x-midpoint)**(-cpow_num) -> [0,midpoint,1] if it is a divering cmap or [0,1] if it is not a divering cmap
                       'interpolation': 'none',
                       'cmap': 'None', # If cmap is none, the plot will inherit the parent's cmap
                       'UseDivCmap': True, # Use a diverging cmap for the 2d plots
                       'stretch_colors': False, # If stretch colors is false, then for a diverging cmap the plot ensures -b and b are the same distance from the midpoint of the cmap.
                       'show_cpu_domains': False, # plots lines showing how the CPUs are divvying up the computational region
                       'face_color': 'gainsboro'}

    gradient =  np.linspace(0, 1, 256)# A way to make the colorbar display better
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos

        self.chart_type = 'VectorFlds'
        self.changedD = False
        self.parent = parent
        self.figure = self.parent.figure
        self.interpolation_methods = ['none','nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def norm(self, vmin=None, vmax=None):
        if self.param_dict['cnorm_type'] == "Linear":
            if self.param_dict['UseDivCmap']:
                return PowerNormWithNeg(1.0, vmin, vmax, midpoint = self.param_dict['div_midpoint'], stretch_colors = self.param_dict['stretch_colors'])
            else:
                return mcolors.Normalize(vmin, vmax)
        elif self.param_dict['cnorm_type'] == "Log":
            return  mcolors.LogNorm(vmin, vmax)
        else:
            return PowerNormWithNeg(self.param_dict['cpow_num'], vmin, vmax, div_cmap = self.param_dict['UseDivCmap'], midpoint = self.param_dict['div_midpoint'], stretch_colors = self.param_dict['stretch_colors'])


    def draw(self, sim = None, n = None):
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]
        # if n is None:
        #     n = self.parent.cur_times[self.param_dict['sim_num']]

                # get c_omp and istep to convert cells to physical units

        # FIND THE SLICE
        MaxYInd = len(sim.get_data(n, data_class='axes', attribute='y')['data']) - 1
        MaxZInd = len(sim.get_data(n, data_class='axes', attribute='z')['data']) - 1


        self.ySlice = int(np.around(self.parent.MainParamDict['ySlice']*MaxYInd))
        self.zSlice = int(np.around(self.parent.MainParamDict['zSlice']*MaxZInd))



        self.c_omp = sim.get_data(n, data_class = 'param', attribute = 'c_omp')
        self.istep = sim.get_data(n, data_class = 'param', attribute = 'istep')

        if self.param_dict['OutlineText']:
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
        if self.param_dict['twoD']:
            self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])

            self.image = self.axes.imshow(np.array([[1,1],[1,1]]), norm = self.norm(), origin = 'lower')

            if self.parent.MainParamDict['ImageAspect']:
                self.image = self.axes.imshow(np.array([[1,1],[1,1]]), norm = self.norm(), origin = 'lower')
            else:
                self.image = self.axes.imshow(np.array([[1,1],[1,1]]), norm = self.norm(), origin = 'lower', aspect='auto')

            self.image.set_interpolation(self.param_dict['interpolation'])



            #self.shockline_2d = self.axes.axvline(self.parent.shock_loc,
            #                                        linewidth = 1.5,
            #                                        linestyle = '--',

            #                                        color = self.parent.shock_color,
            #                                        path_effects=[PathEffects.Stroke(linewidth=2, foreground='k'),
            #                                        PathEffects.Normal()])
            #self.shockline_2d.set_visible(self.GetPlotParam('show_shock'))

            #self.an_2d = self.axes.annotate(self.vec_2d['cbar_label'],
            self.an_2d = self.axes.annotate('',
                                            xy = (0.9,.9),
                                            xycoords= 'axes fraction',
                                            color = 'white',
                                            **self.annotate_kwargs)
            self.an_2d.set_visible(self.param_dict['show_labels'])


            self.axC = self.figure.add_subplot(self.gs[self.parent.cbar_extent[0]:self.parent.cbar_extent[1], self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])

            if self.parent.MainParamDict['HorizontalCbars']:
                self.cbar = self.axC.imshow(self.gradient, aspect='auto')
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
                                            origin='upper')
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

            if not self.param_dict['show_cbar']:
                self.axC.set_visible(False)
            #else:
            #    self.CbarTickFormatter()

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.param_dict['face_color'])
            else:
                self.axes.set_facecolor(self.param_dict['face_color'])

            self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=tick_color)


            #self.axes.set_xlabel(r'$x\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            self.axes.set_xlabel(r'$x$', labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                #self.axes.set_ylabel(r'$y\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
                self.axes.set_ylabel(r'$y$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                #self.axes.set_ylabel(r'$z\ [c/\omega_{\rm pe}]$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
                self.axes.set_ylabel(r'$z$', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])


        else:
            self.xaxis =  sim.get_data(n, data_class = 'axes', attribute = 'x')
            if self.param_dict['show_x']:
                self.vec_x = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'x')
            if self.param_dict['show_y']:
                self.vec_y = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'y')
            if self.param_dict['show_z']:
                self.vec_z = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'z')

            self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])

            # Make the 1-D plots
            self.line_x = self.axes.plot([1,1], [-.5,.5])

            self.line_y = self.axes.plot([1,1], [-.5,.5])
            self.line_z = self.axes.plot([1,1], [-.5,.5])

            self.line_x[0].set_visible(self.param_dict['show_x'])
            self.line_y[0].set_visible(self.param_dict['show_y'])
            self.line_z[0].set_visible(self.param_dict['show_z'])
            # fancy code to make sure that matplotlib sets its limits
            # only based on visible lines
            self.key_list = ['show_x', 'show_y', 'show_z']
            self.line_list = [self.line_x[0], self.line_y[0], self.line_z[0]]

            self.annotate_pos = [0.8,0.9]
            self.anx = self.axes.annotate('', xy = self.annotate_pos,
                        xycoords= 'axes fraction',
                        **self.annotate_kwargs)
            self.annotate_pos[0] += .08
            self.any = self.axes.annotate('', xy = self.annotate_pos,
                        xycoords= 'axes fraction',
                        **self.annotate_kwargs)
            self.annotate_pos[0] += .08
            self.anz = self.axes.annotate('', xy = self.annotate_pos,
                        xycoords= 'axes fraction',
                        **self.annotate_kwargs)

            self.anx.set_visible(self.param_dict['show_x'])
            self.any.set_visible(self.param_dict['show_y'])
            self.anz.set_visible(self.param_dict['show_z'])
            #### Set the ylims... there is a problem where it scales the ylims for the invisible lines:

            #self.shock_line =self.axes.axvline(self.parent.shock_loc, linewidth = 1.5, linestyle = '--', color = self.parent.shock_color, path_effects=[PathEffects.Stroke(linewidth=2, foreground='k'),
            #        PathEffects.Normal()])
            #self.shock_line.set_visible(self.GetPlotParam('show_shock'))

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.param_dict['face_color'])
            else:
                self.axes.set_facecolor(self.param_dict['face_color'])

            self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=tick_color)

            #if self.parent.MainParamDict['SetxLim']:
            #    if self.parent.MainParamDict['xLimsRelative']:
            #        self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
            #                           self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
            #    else:
            #        self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            #else:
            self.axes.set_xlim(self.xaxis['data'][0],self.xaxis['data'][-1])

            if self.param_dict['set_v_min']:
                self.axes.set_ylim(bottom = self.param_dict['v_min'])
            if self.param_dict['set_v_max']:
                self.axes.set_ylim(top = self.param_dict['v_max'])

            # Handle the axes labeling


            #if self.GetPlotParam('normalize_density'):
            #    tmp_str += r'$\ [n_0]$'
            self.axes.set_xlabel(self.xaxis['label'], labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
            #self.axes.set_ylabel(self.scalar_fld['1d_label'], labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black', size = self.parent.MainParamDict['AxLabelSize'])
        self.update_labels_and_colors(sim, n)
        self.refresh(sim = sim, n = n)
        #if self.GetPlotParam('show_cpu_domains'):
        #    self.parent.SetCpuDomainLines()

    def CbarTickFormatter(self):
        ''' A helper function that sets the cbar ticks & labels. This used to be
        easier, but because I am no longer using the colorbar class i have to do
        stuff manually.'''
        clim = np.copy(self.image.get_clim())
        if self.param_dict['show_cbar']:
            if self.param_dict['cnorm_type'] == "Log":
                self.cbar.set_extent([np.log10(clim[0]),np.log10(clim[1]),0,1])
                self.axC.set_xlim(np.log10(clim[0]),np.log10(clim[1]))

            elif self.param_dict['cnorm_type'] == "Pow":
                # re-create the gradient with the data values
                # First make a colorbar in the negative region that is linear in the pow_space
                data_range = np.linspace(clim[0],clim[1],512)

                cbardata = PowerNormFunc(data_range, vmin = data_range[0], vmax = data_range[-1], gamma = self.param_dict['cpow_num'], midpoint = self.param_dict['div_midpoint'], div_cmap = self.param_dict['UseDivCmap'], stretch_colors = self.param_dict['stretch_colors'])
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

            elif self.param_dict['cnorm_type'] == "Linear" and self.param_dict['UseDivCmap']:
                # re-create the gradient with the data values
                # First make a colorbar in the negative region that is linear in the pow_space
                data_range = np.linspace(clim[0],clim[1],512)

                cbardata = PowerNormFunc(data_range, vmin = data_range[0], vmax = data_range[-1], gamma = 1.0, div_cmap = self.param_dict['UseDivCmap'], midpoint = self.param_dict['div_midpoint'], stretch_colors = self.param_dict['stretch_colors'])
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
    def refresh(self, sim = None, n = None):

        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown.  If
        hasn't changed, or isn't viewed, don't touch it. The difference between this and last
        time, is that we won't actually do any drawing in the plot. The plot
        will be redrawn after all subplots data is changed. '''
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]
        # if n is None:
        #    n = self.parent.cur_times[self.param_dict['sim_num']]
        # FIND THE SLICE
        MaxYInd = len(sim.get_data(n, data_class='axes', attribute='y')['data']) - 1
        MaxZInd = len(sim.get_data(n, data_class='axes', attribute='z')['data']) - 1


        self.ySlice = int(np.around(self.parent.MainParamDict['ySlice']*MaxYInd))
        self.zSlice = int(np.around(self.parent.MainParamDict['zSlice']*MaxZInd))
        self.c_omp = sim.get_data(n, data_class = 'param', attribute = 'c_omp')
        self.istep = sim.get_data(n, data_class = 'param', attribute = 'istep')


        # Now that the data is loaded, start making the plots
        if self.param_dict['twoD']:
            if self.param_dict['show_x']:
                self.vec_2d = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'x')
            elif self.param_dict['show_y']:
                self.vec_2d = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'y')
            else:
                self.vec_2d = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'z')            # Link up the spatial axes if desired
            self.an_2d.set_text(self.vec_2d['cbar_label'])
            if self.parent.MainParamDict['2DSlicePlane'] == 0: # x-y plane
                self.image.set_data(self.vec_2d['data'][self.zSlice,:,:])
            elif self.parent.MainParamDict['2DSlicePlane'] == 1: # x-z plane
                self.image.set_data(self.vec_2d['data'][:,self.ySlice,:])

            self.ymin = 0
            self.ymax =  self.image.get_array().shape[0]#/self.c_omp*self.istep

            self.xmin = 0
            self.xmax =  self.image.get_array().shape[1]#/self.c_omp*self.istep

            #self.image.set_interpolation(self.param_dict['interpolation'])
            #self.image.set_cmap(new_cmaps.cmaps[self.cmap])
            self.image.set_extent([self.xmin, self.xmax, self.ymin, self.ymax])

        # Main goal, only change what is showing..
        # First do the 1D plots, because it is simpler
        else:
            self.xaxis =  sim.get_data(n, data_class = 'axes', attribute = 'x')
            if self.param_dict['show_x']:
                self.vec_x = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'x')
            if self.param_dict['show_y']:
                self.vec_y = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'y')
            if self.param_dict['show_z']:
                self.vec_z = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'z')
            if self.parent.MainParamDict['Average1D']:
                if self.param_dict['show_x']:
                    self.line_x[0].set_data(self.xaxis['data'], np.average(self.vec_x['data'].reshape(-1, self.vec_x['data'].shape[-1]), axis = 0))
                if self.param_dict['show_y']:
                    self.line_y[0].set_data(self.xaxis['data'], np.average(self.vec_y['data'].reshape(-1, self.vec_y['data'].shape[-1]), axis = 0))
                if self.param_dict['show_z']:
                    self.line_z[0].set_data(self.xaxis['data'], np.average(self.vec_z['data'].reshape(-1, self.vec_z['data'].shape[-1]), axis = 0))
            else: # x-y plane
                if self.param_dict['show_x']:
                    self.line_x[0].set_data(self.xaxis['data'], self.vec_x['data'][self.zSlice,self.ySlice,:])
                if self.param_dict['show_y']:
                    self.line_y[0].set_data(self.xaxis['data'], self.vec_y['data'][self.zSlice,self.ySlice,:])
                if self.param_dict['show_z']:
                    self.line_z[0].set_data(self.xaxis['data'], self.vec_z['data'][self.zSlice,self.ySlice,:])

        self.set_v_max_min()


    def update_labels_and_colors(self, sim = None, n = None):
        if sim is None:
            sim = self.parent.sim[self.param_dict['sim_num']]
        #if n is None:
        #    n = self.parent.cur_times[self.param_dict['sim_num']]

        if self.param_dict['cmap'] == 'None':
            if self.param_dict['UseDivCmap']:
                cmap = self.parent.MainParamDict['DivColorMap']
            else:
                cmap = self.parent.MainParamDict['ColorMap']

        else:
            cmap = self.param_dict['cmap']


        if self.param_dict['twoD']:
            self.image.set_cmap(new_cmaps.cmaps[cmap])
            self.cbar.set_cmap(new_cmaps.cmaps[cmap])
        else:
            x_color = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.2)
            y_color = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.5)
            z_color = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.8)
            if self.param_dict['show_x']:
                self.vec_x = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'x')
                self.anx.set_text(self.vec_x['1d_label'])
                self.line_x[0].set_color(x_color)
                self.anx.set_color(x_color)
            if self.param_dict['show_y']:
                self.vec_y = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'y')
                self.any.set_text(self.vec_y['1d_label'])
                self.line_y[0].set_color(y_color)
                self.any.set_color(y_color)

            if self.param_dict['show_z']:
                self.vec_z = sim.get_data(n, data_class = 'vec_flds', fld = self.param_dict['field_type'], component= 'z')
                self.anz.set_text(self.vec_z['1d_label'])
                self.line_z[0].set_color(z_color)
                self.anz.set_color(z_color)

    def set_v_max_min(self):
        if not self.param_dict['twoD']:
            self.axes.dataLim = mtransforms.Bbox.unit()
            self.axes.dataLim.update_from_data_xy(xy = np.vstack(self.line_list[0].get_data()).T, ignore=True)
            for line, key in zip(self.line_list, self.key_list):

                if self.param_dict[key]:

                    xy = np.vstack(line.get_data()).T
                    self.axes.dataLim.update_from_data_xy(xy, ignore=False)
            self.axes.autoscale('y')
            if self.param_dict['set_v_min']:
                self.axes.set_ylim(bottom=self.param_dict['v_min'])
            if self.param_dict['set_v_max']:
                self.axes.set_ylim(top=self.param_dict['v_max'])
            if self.parent.MainParamDict['SetxLim']:
                #if self.parent.MainParamDict['xLimsRelative']:
                #    self.axes.set_xlim(self.parent.MainParamDict['xLeft'] + self.parent.shock_loc,
                #                       self.parent.MainParamDict['xRight'] + self.parent.shock_loc)
                #else:
                self.axes.set_xlim(self.parent.MainParamDict['xLeft'], self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(self.xaxis['data'][0], self.xaxis['data'][-1])

        else:
            self.vmin = self.image.get_array().min()
            if self.param_dict['set_v_min']:
                self.vmin = self.param_dict['v_min']
            self.vmax = self.image.get_array().max()
            if self.param_dict['set_v_max']:
                self.vmax = self.param_dict['v_max']
            if self.param_dict['UseDivCmap'] and not self.param_dict['stretch_colors']:
                self.vmax = max(np.abs(self.vmin), self.vmax)
                self.vmin = -self.vmax
            self.image.norm.vmin = self.vmin
            self.image.norm.vmax = self.vmax
            if self.param_dict['show_cbar']:
                self.CbarTickFormatter()
    def remove(self):
        try:
            self.axC.remove()
        except AttributeError:
            pass
        except KeyError:
            pass
        self.axes.remove()


if __name__== '__main__':
    import os
    from oengus import Oengus
    from pic_sim import picSim
    import matplotlib.pyplot as plt
    oengus = Oengus(interactive=False,preset_view='test')


    oengus.open_sim(picSim(os.path.join(os.path.dirname(__file__),'../output')))
    oengus.create_graphs()
    plt.savefig('test.png')
