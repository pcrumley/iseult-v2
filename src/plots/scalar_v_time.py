import numpy as np
import new_cmaps
from base_plot import iseultPlot
from itertools import cycle
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D as mlines
from validate_plot_opts import validate_color, validate_ls, \
    validate_marker, validate_marker_size


class scalar_vs_timePlot(iseultPlot):
    # A dictionary of all of the parameters for this plot with the
    # default parameters

    plot_param_dict = {
        'twoD': 0,
        'show_cbar': False,
        'x_min': -2.0,
        'x_max': 0,
        'set_x_min': False,
        'set_x_max': False,
        'lines': [{
            'sim_num': 0,
            'scalar': 'Total KE_e',
            'plot_args': {
                'ls': ':',
                'marker': 'v',
                'color': 'red',
                'markersize': 5,
                'label': r'${\rm KE_e}$',
                'visible': True,
            }
        }],
        'y_axis_label': 'Total Energy',
        'y_min': -2.0,
        'y_max': 2.0,
        'yLog': False,
        'set_y_min': False,
        'set_y_max': False,
        'UseDivCmap': False,
        'face_color': 'gainsboro',
        'show_legend': False,
        'show_cur_time': True}

    def __init__(self, parent, pos, param_dict):
        tmp_dict = {}
        tmp_dict.update(self.plot_param_dict)
        tmp_dict.update(param_dict)
        iseultPlot.__init__(self, parent, pos, tmp_dict)
        self.chart_type = 'ScalarVsTime'
        self.x_axis_info = None
        self.y_axis_info = None
        self.legend_loc = 1
        self.color_cycle = cycle([c for c in mcolors.TABLEAU_COLORS.keys()])
        self.marker_cycle = cycle([m for m in mlines.markers.keys()])
        self.ls_cycle = cycle([':'])
        self.marker_size_cycle = cycle(['.'])
        self.plot_list = []

    def axis_info(self):
        pass

    def link_handler(self):
        iseultPlot.unlink(self.pos)

    def get_sim_nums(self):
        sim_nums = []
        for line in self.shown_lines:
            if line['sim_num'] not in sim_nums:
                sim_nums.append(line['sim_num'])
        return sim_nums

    def clear_lines(self):
        if hasattr(self, 'time_line'):
            self.time_line.remove()
        #if hasattr(self, 'legend'):
        #    self.legend.remove()
        for line_artist in self.plot_list:
            line_artist[0].remove()

    def build_lines(self):
        self.clear_lines()
        self.plot_list = []
        # make sure the line attributes are there...
        kws = ['ls', 'marker', 'color', 'markersize']
        validators = [validate_ls, validate_marker, validate_color, validate_marker_size]
        cycles = [
            self.ls_cycle,
            self.marker_cycle,
            self.color_cycle,
            self.marker_size_cycle]

        for line in self.param_dict['lines']:
            plot_args = line['plot_args']
            if 'visible' not in plot_args.keys():
                plot_args['visible'] = True
            for key, validator, cyc in zip(kws, validators, cycles):
                exists = key in plot_args.keys()
                if not exists or not validator(plot_args[key]):
                    plot_args[key] = next(cyc)

        self.shown_lines = [line for line in filter(
            lambda x: x['plot_args']['visible'],
            self.param_dict['lines'])]

        for line in self.shown_lines:
            self.plot_list.append(
                self.axes.plot(
                    np.arange(2),
                    np.arange(2),
                    markeredgecolor=line['plot_args']['color'],
                    **line['plot_args']))

        self.time_line = self.axes.axvline(
            0,
            linewidth=1.5,
            linestyle='--',
            color='k',
            alpha=0.4,
            visible=self.param_dict['show_cur_time'])

        # See if an legend already exists;
        if hasattr(self, 'legend'):
            # Save its location, checking if _get_loc exists because
            # private method and may go away in matplotlib.
            if hasattr(self.legend, '_get_loc'):
                self.legend_loc = self.legend._get_loc()

        # Build the legend
        legend_handles = [line[0] for line in self.plot_list]
        legend_labels = []
        for line in self.shown_lines:
            legend_labels.append(line['plot_args']['label'])

        self.legend = self.axes.legend(
            legend_handles,
            legend_labels,
            framealpha=.05,
            fontsize=self.parent.MainParamDict['legendLabelSize'])


        self.legend.set_visible(self.param_dict['show_legend'])
        self.legend.get_frame().set_facecolor('k')
        self.legend.get_frame().set_linewidth(0.0)
        self.legend.set_draggable(True, update='loc')
        self.legend._set_loc(self.legend_loc)

    def draw(self):
        self.axC.set_visible(False)
        self.axes.set_ylabel(
            self.param_dict['y_axis_label'],
            labelpad=self.parent.MainParamDict['xLabelPad'],
            color='black',
            size=self.parent.MainParamDict['AxLabelSize'])

        self.axes.set_xlabel(
            r'$t\ [c/\omega_{pe}$]',
            labelpad=self.parent.MainParamDict['xLabelPad'],
            color='black',
            size=self.parent.MainParamDict['AxLabelSize'])

        if self.param_dict['yLog']:
            self.axes.set_yscale('log')

        self.build_lines()

        self.refresh()
        self.link_handler()

    def refresh(self):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown. If
        hasn't changed, or isn't viewed, don't touch it. The difference
        between this and last time, is that we won't create any mpl objects.
        The plot will be redrawn after all subplots data is changed. '''

        if self.param_dict['show_cur_time']:
            sim = self.parent.sims[self.parent.cur_sim]
            t = sim.get_time(units='c_ompe')
            self.time_line.set_xdata([t, t])

        xmin_max = [np.inf, -np.inf]
        ymin_max = [np.inf, -np.inf]

        # self.cur_time.set_xdata([self.time,self.time])

        for plot, line in zip(self.plot_list, self.shown_lines):
            sim = self.parent.sims[line['sim_num']]
            tmp_dict = sim.get_data(
                data_class='scalar_v_time',
                scalar=line['scalar'])
            plot[0].set_data(tmp_dict['times'], tmp_dict['data'])
            xmin_max[0] = min(xmin_max[0], np.min(tmp_dict['times']))
            xmin_max[1] = max(xmin_max[1], np.max(tmp_dict['times']))
            ymin_max[0] = min(ymin_max[0], np.min(tmp_dict['data']))
            ymin_max[1] = max(ymin_max[1], np.max(tmp_dict['data']))

        if np.isinf(xmin_max[0]):
            xmin_max = [None, None]
            ymin_max = [None, None]
        if self.param_dict['yLog']:
            for i in range(2):
                if ymin_max[i] <= 0:
                    ymin_max[i] = None
                if ymin_max[i] is not None:
                    ymin_max[i] = np.log10(ymin_max[i])

        if ymin_max[0] is not None and ymin_max[1] is not None:
            tdist = xmin_max[1]-xmin_max[0]
            xmin_max[0] -= 0.04*tdist
            xmin_max[1] += 0.04*tdist

            dist = ymin_max[1]-ymin_max[0]
            ymin_max[0] -= 0.04*dist
            ymin_max[1] += 0.04*dist
            if self.param_dict['yLog']:
                ymin_max = [10**elm for elm in ymin_max]

        if self.param_dict['set_x_min']:
            xmin_max[0] = self.param_dict['x_min']
        if self.param_dict['set_x_max']:
            xmin_max[1] = self.param_dict['x_max']
        if self.param_dict['set_y_min']:
            ymin_max[0] = self.param_dict['y_min']
        if self.param_dict['set_y_max']:
            ymin_max[1] = self.param_dict['y_max']

        self.axes.set_xlim(xmin_max)
        self.axes.set_ylim(ymin_max)

        self.save_home()
