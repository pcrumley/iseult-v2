import matplotlib
import sys
import numpy as np
import numpy.ma as ma
import new_cmaps
from new_cnorms import PowerNormWithNeg
from prtl_hists import Fast2DHist, Fast2DWeightedHist
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects


class phasePlot:
    # A dictionary of all of the parameters for this plot with the
    # default parameters

    plot_param_dict = {
        'twoD': 1,
        'sim_num': 0,
        'masked': 1,
        'cnorm_type': 'Log',  # Colormap normalization. Opts are Log or Linear
        'prtl_type': 'ions',
        'x_val': 'x',
        'y_val': 'px',
        'weights': None,
        'cpow_num': 0.6,
        'show_cbar': True,
        'weighted': False,
        'show_shock': False,
        'show_int_region': True,
        'x_bins': 200,
        'y_bins': 200,
        'v_min': -2.0,
        'v_max': 0,
        'set_v_min': False,
        'set_v_max': False,
        'y_min': -2.0,
        'y_max': 2.0,
        'cmap': 'None',
        'set_y_min': False,
        'set_y_max': False,
        'spatial_x': True,
        'spatial_y': False,
        'interpolation': 'nearest',
        'face_color': 'gainsboro'}

    # A way to make the colorbar display better
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos
        self.parent = parent
        self.chart_type = 'PhasePlot'
        self.figure = self.parent.figure
        self.interpolation_methods = [
            'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

    def norm(self, vmin=None, vmax=None):
        if self.param_dict['cnorm_type'] == 'Log':
            return mcolors.LogNorm(vmin, vmax)

        else:
            return mcolors.Normalize(vmin, vmax)

    def update_labels_and_colors(self):
        if self.param_dict['prtl_type'] == 'ions':  # protons
            self.energy_color = self.parent.ion_color

        else:  # electrons
            self.energy_color = self.parent.electron_color

        self.axes.set_xlabel(
            self.x_values['axis_label'],
            labelpad=self.parent.MainParamDict['xLabelPad'],
            color='black',
            size=self.parent.MainParamDict['AxLabelSize'])

        self.axes.set_ylabel(
            self.y_values['axis_label'],
            labelpad=self.parent.MainParamDict['xLabelPad'],
            color='black',
            size=self.parent.MainParamDict['AxLabelSize'])

    def draw(self, sim=None, n=None):

        self.IntRegionLines = []
        tick_color = 'black'

        self.gs = gridspec.GridSpecFromSubplotSpec(
            100, 100,
            subplot_spec=self.parent.gs0[self.pos])

        self.axes = self.figure.add_subplot(
            self.gs[
                self.parent.axes_extent[0]:self.parent.axes_extent[1],
                self.parent.axes_extent[2]:self.parent.axes_extent[3]])

        self.image = self.axes.imshow(
            [[np.nan, np.nan], [np.nan, np.nan]],
            cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']],
            norm=self.norm(), origin='lower',
            aspect='auto',
            interpolation=self.param_dict['interpolation'])

        self.image.set_extent([0, 1, 0, 1])
        self.image.set_clim([1, 10])

        self.axC = self.figure.add_subplot(
            self.gs[
                self.parent.cbar_extent[0]:self.parent.cbar_extent[1],
                self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])

        # Technically I should use the colorbar class here,
        # but I found it annoying in some of it's limitations.
        if self.parent.MainParamDict['HorizontalCbars']:
            self.cbar = self.axC.imshow(
                self.gradient, aspect='auto',
                cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']])

            # Make the colobar axis more like the real colorbar
            self.axC.tick_params(
                axis='x',
                which='both',  # bothe major and minor ticks
                top=False,  # turn off top ticks
                labelsize=self.parent.MainParamDict['NumFontSize'])

            self.axC.tick_params(
                axis='y',          # changes apply to the y-axis
                which='both',      # both major and minor ticks are affected
                left=False,        # ticks along the bottom edge are off
                right=False,       # ticks along the top edge are off
                labelleft=False)

        else:
            self.cbar = self.axC.imshow(
                np.transpose(self.gradient)[::-1],
                aspect='auto', origin='upper',
                cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']])

            # Make the colobar axis more like the real colorbar
            self.axC.tick_params(
                axis='x',
                which='both',   # both major and minor ticks
                top=False,      # turn off top ticks
                bottom=False,
                labelbottom=False,
                labelsize=self.parent.MainParamDict['NumFontSize'])

            self.axC.tick_params(
                axis='y',           # changes apply to the y-axis
                which='both',       # both major and minor ticks are affected
                left=False,         # ticks along the bottom edge are off
                right=True,         # ticks along the top edge are off
                labelleft=False,
                labelright=True,
                labelsize=self.parent.MainParamDict['NumFontSize'])

        self.cbar.set_extent([0, 1.0, 0, 1.0])

        if not self.param_dict['show_cbar']:
            self.axC.set_visible(False)

        if int(matplotlib.__version__[0]) < 2:
            self.axes.set_axis_bgcolor(self.param_dict['face_color'])
        else:
            self.axes.set_facecolor(self.param_dict['face_color'])

        self.axes.tick_params(
            labelsize=self.parent.MainParamDict['NumFontSize'],
            color=tick_color)

        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        # Generate the X-axis values
        self.x_values = sim.get_data(
            n, data_class='prtls',
            prtl_type=self.param_dict['prtl_type'],
            attribute=self.param_dict['x_val'])
        self.y_values = sim.get_data(
            n, data_class='prtls',
            prtl_type=self.param_dict['prtl_type'],
            attribute=self.param_dict['y_val'])

        self.update_labels_and_colors()
        self.refresh(sim=sim, n=n)

    def refresh(self, sim=None, n=None):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown. If
        hasn't changed, or isn't viewed, don't touch it. The difference
        between this and last time, is that we won't create any mpl objects.
        The plot will be redrawn after all subplots data is changed. '''

        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        c_omp = sim.get_data(
            n, data_class='param',
            attribute='c_omp')

        self.x_values = sim.get_data(
            n, data_class='prtls',
            prtl_type=self.param_dict['prtl_type'],
            attribute=self.param_dict['x_val'])
        self.y_values = sim.get_data(
            n, data_class='prtls',
            prtl_type=self.param_dict['prtl_type'],
            attribute=self.param_dict['y_val'])

        is_good = len(self.y_values['data']) == len(self.x_values['data'])
        is_good &= len(self.y_values['data']) > 0

        if self.param_dict['weighted']:
            self.weights = sim.get_data(
                n, data_class='prtls',
                prtl_type=self.param_dict['prtl_type'],
                attribute=self.param_dict['weights'])

            is_good &= len(self.weights['data']) != 0
            is_good &= len(self.weights['data']) == len(self.y_values['data'])

        if is_good:
            xmin = np.min(self.x_values['data'])
            xmax = np.max(self.x_values['data'])
            xmax = xmax if xmax > xmin else xmin + 1

            ymin = np.min(self.y_values['data'])
            ymax = np.max(self.y_values['data'])
            ymax = ymax if ymax > ymin else ymin + 1

            if self.param_dict['weighted']:
                hist2d = Fast2DWeightedHist(
                    self.y_values['data'],
                    self.x_values['data'],
                    self.weights['data'],
                    ymin, ymax,
                    self.param_dict['y_bins'],
                    xmin, xmax,
                    self.param_dict['x_bins'])
            else:
                hist2d = Fast2DHist(
                    self.y_values['data'],
                    self.x_values['data'],
                    ymin, ymax,
                    self.param_dict['y_bins'],
                    xmin, xmax,
                    self.param_dict['x_bins'])

            hist2d *= float(hist2d.max())**(-1)
            self.clim = [hist2d[hist2d != 0].min(), hist2d.max()]

            # set the colors
            self.image.set_data(hist2d)
            self.image.set_extent([xmin, xmax, ymin, ymax])

            if self.param_dict['set_v_min']:
                self.clim[0] = 10**self.param_dict['v_min']

            if self.param_dict['set_v_max']:
                self.clim[1] = 10**self.param_dict['v_max']

            self.image.set_clim(self.clim)

            if self.param_dict['show_cbar']:
                self.CbarTickFormatter()

            if self.param_dict['show_shock']:
                self.shock_line.set_xdata(
                    [self.parent.shock_loc, self.parent.shock_loc])

            if self.param_dict['set_y_min']:
                ymin = self.param_dict['y_min']

            if self.param_dict['set_y_max']:
                ymax = self.param_dict['y_max']

            self.axes.set_ylim(ymin, ymax)
            self.axes.set_xlim(xmin, xmax)

        else:
            self.image.set_data(np.ones((2, 2))*np.NaN)

    def CbarTickFormatter(self):
        ''' A helper function that sets the cbar ticks & labels. This used to
        be easier, but because I am no longer using the colorbar class i have
        to do stuff manually.'''
        clim = np.copy(self.image.get_clim())
        if self.param_dict['show_cbar']:
            if self.param_dict['cnorm_type'] == 'Log':
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_extent(
                        [np.log10(clim[0]), np.log10(clim[1]), 0, 1])
                    self.axC.set_xlim(
                        np.log10(clim[0]), np.log10(clim[1]))
                    self.axC.xaxis.set_label_position('top')
                    self.axC.set_xlabel(
                        '$\log\ $' + self.x_values['hist_cbar_label'],
                        labelpad=self.parent.MainParamDict['cbarLabelPad'],
                        size=self.parent.MainParamDict['AxLabelSize'])

                else:
                    self.cbar.set_extent(
                        [0, 1, np.log10(clim[0]), np.log10(clim[1])])
                    self.axC.set_ylim(
                        np.log10(clim[0]), np.log10(clim[1]))

                    self.axC.locator_params(axis='y', nbins=6)
                    self.axC.yaxis.set_label_position("right")
                    self.axC.set_ylabel(
                        '$\log\ $' + self.x_values['hist_cbar_label'],
                        labelpad=self.parent.MainParamDict['cbarLabelPad'],
                        rotation=-90,
                        size=self.parent.MainParamDict['AxLabelSize'])

            else:
                if self.parent.MainParamDict['HorizontalCbars']:
                    self.cbar.set_extent([clim[0], clim[1], 0, 1])
                    self.axC.set_xlim(clim[0], clim[1])
                    self.axC.set_xlabel(
                        self.x_values['hist_cbar_label'],
                        labelpad=self.parent.MainParamDict['cbarLabelPad'],
                        size=self.parent.MainParamDict['AxLabelSize'])

                else:
                    self.cbar.set_extent([0, 1, clim[0], clim[1]])
                    self.axC.set_ylim(clim[0], clim[1])
                    self.axC.locator_params(axis='y', nbins=6)
                    self.axC.yaxis.set_label_position("right")
                    self.axC.set_ylabel(
                        self.x_values['hist_cbar_label'],
                        labelpad=self.parent.MainParamDict['cbarLabelPad'],
                        rotation=-90,
                        size=self.parent.MainParamDict['AxLabelSize'])
