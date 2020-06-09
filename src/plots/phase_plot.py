import numpy as np
import new_cmaps
from prtl_hists import Fast2DHist, Fast2DWeightedHist
from base_plot import iseultPlot


class phasePlot(iseultPlot):
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
        'UseDivCmap': False,
        'interpolation': 'nearest',
        'face_color': 'gainsboro'}

    # A way to make the colorbar display better
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        tmp_dict = {}
        tmp_dict.update(self.plot_param_dict)
        tmp_dict.update(param_dict)
        iseultPlot.__init__(self, parent, pos, tmp_dict)
        self.chart_type = 'PhasePlot'

    def axis_info(self):
        if self.parent.MainParamDict['LinkSpatial'] == 1:
            for val in ['x', 'y', 'z']:
                if self.param_dict['x_val'] == val:
                    self.x_axis_info = {
                        'data_ax': val,
                        'pos': self.pos,
                        'axes': 'x'
                    }
                    break
            else:
                self.x_axis_info = None

            for val in ['x', 'y', 'z']:
                if self.param_dict['y_val'] == val:
                    self.x_axis_info = {
                        'data_ax': val,
                        'pos': self.pos,
                        'axes': 'y'
                    }
                    break
            else:
                self.y_axis_info = None
        else:
            self.x_axis_info = None
            self.y_axis_info = None

    def link_handler(self):
        # First unlink this plot
        iseultPlot.unlink(self.pos)
        self.axis_info()

        iseultPlot.link_up(self.x_axis_info)
        iseultPlot.link_up(self.y_axis_info)

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

        self.image = self.axes.imshow(
            [[np.nan, np.nan], [np.nan, np.nan]],
            cmap=new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']],
            norm=self.norm(), origin='lower',
            aspect='auto',
            interpolation=self.param_dict['interpolation'])

        self.image.set_extent([0, 1, 0, 1])
        self.image.set_clim([1, 10])

        if not self.param_dict['show_cbar']:
            self.axC.set_visible(False)

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
        self.link_handler()

    def refresh(self, sim=None, n=None):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown. If
        hasn't changed, or isn't viewed, don't touch it. The difference
        between this and last time, is that we won't create any mpl objects.
        The plot will be redrawn after all subplots data is changed. '''

        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

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
                label = self.x_values['hist_cbar_label']
                if self.param_dict['cnorm_type'] == 'Log':
                    label = '$\log\ $' + label
                self.CbarTickFormatter(label)

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
            self.image.set_data(
                np.ones((2, 2))*np.NaN)

        self.save_home()
