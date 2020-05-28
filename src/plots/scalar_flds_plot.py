import matplotlib
import numpy as np
import sys
import new_cmaps
from new_cnorms import PowerNormWithNeg, PowerNormFunc
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import FuncFormatter


class scalarFldsPlot:
    # A dictionary of all of the parameters for this plot with the
    # default parameters

    plot_param_dict = {
        'twoD': 0,
        'sim_num': 0,
        'flds_type': 'density',
        'show_cbar': True,
        'set_color_limits': False,
        'v_min': 0,
        'v_max': 10,
        'set_v_min': False,
        'set_v_max': False,
        'show_labels': True,
        'show_shock': False,
        'OutlineText': True,
        'spatial_x': True,
        'spatial_y': False,
        'interpolation': 'none',
        'normalize_density': True,  # Normalize dens to it's upstream values
        'cnorm_type': 'Linear',  # Colormap norm;  options are Pow or Linear
        'cpow_num': 0.6,  # Used in the PowerNorm
        'UseDivCmap': False,
        'div_midpoint': 0.0,
        'stretch_colors': False,
        'cmap': 'None',  # If cmap is none, the plot inherits the parent's cmap
        'face_color': 'gainsboro'}

    # A way to make the colorbar display better
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos

        self.chart_type = 'ScalarFlds'
        self.changedD = False
        self.parent = parent
        self.figure = self.parent.figure
        self.interpolation_methods = [
            'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def norm(self, vmin=None, vmax=None):
        if self.param_dict['cnorm_type'] == "Linear":
            if self.param_dict['UseDivCmap']:
                return PowerNormWithNeg(
                    1.0, vmin, vmax,
                    midpoint=self.param_dict['div_midpoint'],
                    stretch_colors=self.param_dict['stretch_colors'])

            else:
                return mcolors.Normalize(vmin, vmax)

        elif self.param_dict['cnorm_type'] == "Log":
            return mcolors.LogNorm(vmin, vmax)

        else:

            return PowerNormWithNeg(
                self.param_dict['cpow_num'],
                vmin, vmax,
                div_cmap=self.param_dict['UseDivCmap'],
                midpoint=self.param_dict['div_midpoint'],
                stretch_colors=self.param_dict['stretch_colors'])

    def draw(self, sim=None, n=None):
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        if self.param_dict['cmap'] == 'None':
            if self.param_dict['UseDivCmap']:
                self.cmap = self.parent.MainParamDict['DivColorMap']

            else:
                self.cmap = self.parent.MainParamDict['ColorMap']

        else:
            self.cmap = self.param_dict['cmap']

        self.dens_color = new_cmaps.cmap_to_hex(0.5, self.cmap)

        # get c_omp and istep to convert cells to physical units
        self.c_omp = sim.get_data(n, data_class='param', attribute='c_omp')
        self.istep = sim.get_data(n, data_class='param', attribute='istep')

        # FIND THE SLICE
        self.ySlice = self.parent.calc_slices('y', sim, n)
        self.zSlice = self.parent.calc_slices('z', sim, n)

        self.scalar_fld = sim.get_data(
            n, data_class='scalar_flds',
            fld=self.param_dict['flds_type'])

        if self.param_dict['OutlineText']:
            self.annotate_kwargs = {
                'horizontalalignment': 'right',
                'verticalalignment': 'top',
                'size': self.parent.MainParamDict['annotateTextSize'],
                'path_effects': [
                    PathEffects.withStroke(linewidth=1.5, foreground="k")]
            }

        else:
            self.annotate_kwargs = {
                'horizontalalignment': 'right',
                'verticalalignment': 'top',
                'size': self.parent.MainParamDict['annotateTextSize']}

        # Set the tick color
        tick_color = 'black'

        # Create a gridspec to handle spacing better
        self.gs = gridspec.GridSpecFromSubplotSpec(
            100, 100,
            subplot_spec=self.parent.gs0[self.pos])

        # Now that the data is loaded, start making the plots
        # Make the plots
        if self.param_dict['twoD']:
            self.axes = self.figure.add_subplot(
                self.gs[
                    self.parent.axes_extent[0]:self.parent.axes_extent[1],
                    self.parent.axes_extent[2]:self.parent.axes_extent[3]])

            self.image = self.axes.imshow(
                np.array([[1, 1], [1, 1]]),
                norm=self.norm(),
                origin='lower')

            if not self.parent.MainParamDict['ImageAspect']:
                self.image = self.axes.imshow(
                    np.array([[1, 1], [1, 1]]),
                    norm=self.norm(),
                    origin='lower',
                    aspect='auto')

            self.image.set_interpolation(
                self.param_dict['interpolation'])

            self.an_2d = self.axes.annotate(
                '',
                xy=(0.9, 0.9),
                xycoords='axes fraction',
                color='white',
                **self.annotate_kwargs)

            self.an_2d.set_visible(
                self.param_dict['show_labels'])

            self.axC = self.figure.add_subplot(
                self.gs[
                    self.parent.cbar_extent[0]:self.parent.cbar_extent[1],
                    self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])

            if self.parent.MainParamDict['HorizontalCbars']:
                self.cbar = self.axC.imshow(
                    self.gradient, aspect='auto')

                # Make the colobar axis more like the real colorbar
                self.cbar.set_extent([0, 1.0, 0, 1.0])
                self.axC.tick_params(
                    axis='x',
                    which='both',  # bothe major and minor ticks
                    top=False,  # turn off top ticks
                    labelsize=self.parent.MainParamDict['NumFontSize'])

                self.axC.tick_params(
                    axis='y',       # changes apply to the y-axis
                    which='both',   # both major and minor ticks are affected
                    left=False,     # ticks along the bottom edge are off
                    right=False,    # ticks along the top edge are off
                    labelleft=False)

            else:  # Cbar is on the vertical
                self.cbar = self.axC.imshow(
                    np.transpose(self.gradient)[::-1],
                    aspect='auto',
                    origin='upper')
                # Make the colobar axis more like the real colorbar
                self.cbar.set_extent([0, 1.0, 0, 1.0])

                self.axC.tick_params(
                    axis='x',
                    which='both',  # both the major and minor ticks
                    top=False,  # turn off top ticks
                    bottom=False,  # turn off top ticks
                    labelbottom=False,  # turn off top ticks
                    labelsize=self.parent.MainParamDict['NumFontSize'])

                self.axC.tick_params(
                    axis='y',        # changes apply to the y-axis
                    which='both',    # both major and minor ticks are affected
                    left=False,      # ticks along the bottom edge are off
                    right=True,      # ticks along the top edge are off
                    labelleft=False,
                    labelright=True,
                    labelsize=self.parent.MainParamDict['NumFontSize'])

            if not self.param_dict['show_cbar']:
                self.axC.set_visible(False)

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.param_dict['face_color'])
            else:
                self.axes.set_facecolor(self.param_dict['face_color'])

            self.axes.tick_params(
                labelsize=self.parent.MainParamDict['NumFontSize'],
                color=tick_color)

            self.axes.set_xlabel(
                r'$x$',
                labelpad=self.parent.MainParamDict['xLabelPad'],
                color='black',
                size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                self.axes.set_ylabel(
                    r'$y$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(
                    r'$z$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

        # 1D simulations
        else:
            self.xaxis = sim.get_data(
                n, data_class='axes',
                attribute='x')

            # Do the 1D Plots
            self.axes = self.figure.add_subplot(
                self.gs[
                    self.parent.axes_extent[0]:self.parent.axes_extent[1],
                    self.parent.axes_extent[2]:self.parent.axes_extent[3]])

            self.linedens = self.axes.plot(
                [1, 1], [-0.5, 0.5],
                color=self.dens_color)

            if int(matplotlib.__version__[0]) < 2:
                self.axes.set_axis_bgcolor(self.param_dict['face_color'])
            else:
                self.axes.set_facecolor(self.param_dict['face_color'])

            self.axes.tick_params(
                labelsize=self.parent.MainParamDict['NumFontSize'],
                color=tick_color)

            self.axes.set_xlim(
                self.xaxis['data'][0],
                self.xaxis['data'][-1])

            # Handle the axes labeling
            self.axes.set_xlabel(
                self.xaxis['label'],
                labelpad=self.parent.MainParamDict['xLabelPad'],
                color='black',
                size=self.parent.MainParamDict['AxLabelSize'])

            self.axes.set_ylabel(
                self.scalar_fld['label'],
                labelpad=self.parent.MainParamDict['yLabelPad'],
                color='black',
                size=self.parent.MainParamDict['AxLabelSize'])

        self.refresh(sim=sim, n=n)

    def CbarTickFormatter(self):
        ''' A helper function that sets the cbar ticks & labels. This used to
        be easier, but because I am no longer using the colorbar class i have
        to do stuff manually.'''
        clim = np.copy(self.image.get_clim())
        if self.param_dict['show_cbar']:
            if self.param_dict['cnorm_type'] == "Log":
                self.cbar.set_extent(
                    [np.log10(clim[0]), np.log10(clim[1]), 0, 1])
                self.axC.set_xlim(
                    np.log10(clim[0]),
                    np.log10(clim[1]))

            elif self.param_dict['cnorm_type'] == "Pow":
                # re-create the gradient with the data values
                # First make a colorbar in the negative region that
                # is linear in the pow_space
                data_range = np.linspace(clim[0], clim[1], 512)

                cbardata = PowerNormFunc(
                    data_range,
                    vmin=data_range[0],
                    vmax=data_range[-1],
                    gamma=self.param_dict['cpow_num'],
                    midpoint=self.param_dict['div_midpoint'],
                    div_cmap=self.param_dict['UseDivCmap'],
                    stretch_colors=self.param_dict['stretch_colors'])
                cbardata = np.vstack((cbardata, cbardata))

                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_data(cbardata)
                    self.cbar.set_extent([clim[0], clim[1], 0, 1])
                    self.axC.set_xlim(clim[0], clim[1])

                else:
                    self.cbar.set_data(np.transpose(cbardata)[::-1])
                    self.cbar.set_extent([0, 1, clim[0], clim[1]])
                    self.axC.set_ylim(clim[0], clim[1])
                    self.axC.locator_params(axis='y', nbins=6)

            elif self.param_dict['UseDivCmap']:
                # re-create the gradient with the data values
                # First make a colorbar in the negative region
                # that is linear in the pow_space
                data_range = np.linspace(clim[0], clim[1], 512)

                cbardata = PowerNormFunc(
                    data_range,
                    vmin=data_range[0],
                    vmax=data_range[-1],
                    gamma=1.0,
                    div_cmap=True,
                    midpoint=self.param_dict['div_midpoint'],
                    stretch_colors=self.param_dict['stretch_colors'])
                cbardata = np.vstack((cbardata, cbardata))

                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_data(cbardata)
                    self.cbar.set_extent([clim[0], clim[1], 0, 1])
                    self.axC.set_xlim(clim[0], clim[1])

                else:
                    self.cbar.set_data(np.transpose(cbardata)[::-1])
                    self.cbar.set_extent([0, 1, clim[0], clim[1]])
                    self.axC.set_ylim(clim[0], clim[1])
                    self.axC.locator_params(axis='y', nbins=6)

            else:
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_extent([clim[0], clim[1], 0, 1])
                    self.axC.set_xlim(clim[0], clim[1])
                else:

                    self.cbar.set_extent([0, 1, clim[0], clim[1]])
                    self.axC.set_ylim(clim[0], clim[1])
                    self.axC.locator_params(axis='y', nbins=6)

    def refresh(self, sim=None, n=None):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown.  If
        hasn't changed, or isn't viewed, don't touch it. The difference between
        this and last time, is that we won't actually do any drawing in the
        plot. The plot will be redrawn after all subplots data is changed. '''
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        self.scalar_fld = sim.get_data(
            n, data_class='scalar_flds',
            fld=self.param_dict['flds_type'])
        self.xaxis = sim.get_data(
            n, data_class='axes',
            attribute='x')
        self.c_omp = sim.get_data(
            n, data_class='param',
            attribute='c_omp')
        self.istep = sim.get_data(
            n, data_class='param',
            attribute='istep')

        # FIND THE SLICE

        self.ySlice = self.parent.calc_slices('y', sim, n)
        self.zSlice = self.parent.calc_slices('z', sim, n)

        # Main goal, only change what is showing..
        # First do the 1D plots, because it is simpler
        if self.param_dict['twoD'] == 0:
            print(self.xaxis['data'],self.scalar_fld['data'][self.zSlice, self.ySlice, :])
            if self.parent.MainParamDict['Average1D']:
                self.linedens[0].set_data(
                    self.xaxis['data'],
                    np.average(
                        self.scalar_fld['data'].reshape(
                            -1, self.scalar_fld['data'].shape[-1]), axis=0))

            else:  #
                self.linedens[0].set_data(
                    self.xaxis['data'],
                    self.scalar_fld['data'][self.zSlice, self.ySlice, :])

            if self.parent.MainParamDict['SetxLim']:
                self.axes.set_xlim(
                    self.parent.MainParamDict['xLeft'],
                    self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(
                    self.xaxis['data'][0],
                    self.xaxis['data'][-1])

        else:  # Now refresh the plot if it is 2D
            if self.parent.MainParamDict['2DSlicePlane'] == 0:  # x-y plane
                self.image.set_data(
                    self.scalar_fld['data'][self.zSlice, :, :])
            elif self.parent.MainParamDict['2DSlicePlane'] == 1:  # x-z plane
                self.image.set_data(
                    self.scalar_fld['data'][:, self.ySlice, :])

            self.ymin = 0
            self.ymax = self.image.get_array().shape[0]/self.c_omp*self.istep
            self.xmin = 0
            self.xmax = self.xaxis['data'][-1]
            self.image.set_extent([
                self.xmin, self.xmax, self.ymin, self.ymax])
            if self.parent.MainParamDict['SetxLim']:
                self.axes.set_xlim(
                    self.parent.MainParamDict['xLeft'],
                    self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(self.xmin, self.xmax)

            if self.parent.MainParamDict['SetyLim']:
                self.axes.set_ylim(
                    self.parent.MainParamDict['yBottom'],
                    self.parent.MainParamDict['yTop'])
            else:
                self.axes.set_ylim(self.ymin, self.ymax)

            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                self.axes.set_ylabel(
                    r'$y$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(
                    r'$z$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

        self.set_v_max_min()

    def set_v_max_min(self):
        if not self.param_dict['twoD']:
            min_max = [
                self.linedens[0].get_data()[1].min(),
                self.linedens[0].get_data()[1].max()]
            dist = min_max[1]-min_max[0]
            min_max[0] -= 0.04*dist
            min_max[1] += 0.04*dist
            self.axes.set_ylim(min_max)
            if self.param_dict['set_v_min']:
                self.axes.set_ylim(bottom=self.param_dict['v_min'])
            if self.param_dict['set_v_max']:
                self.axes.set_ylim(top=self.param_dict['v_max'])
        else:
            self.vmin = self.image.get_array().min()
            if self.param_dict['set_v_min']:
                self.vmin = self.param_dict['v_min']
            self.vmax = self.image.get_array().max()
            if self.param_dict['set_v_max']:
                self.vmax = self.param_dict['v_max']
            if self.param_dict['UseDivCmap']:
                if not self.param_dict['stretch_colors']:
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


if __name__ == '__main__':
    import os
    from oengus import Oengus
    from pic_sim import picSim
    import matplotlib.pyplot as plt
    oengus = Oengus(interactive=False)
    oengus.open_sim(
        picSim(
            os.path.join(os.path.dirname(__file__), '../output')))

    oengus.create_graphs()
    plt.savefig('test.png')
