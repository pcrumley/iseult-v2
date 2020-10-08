import numpy as np
import new_cmaps
from base_plot import iseultPlot
import matplotlib.patheffects as PathEffects


class scalarFldsPlot(iseultPlot):
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
        'interpolation': 'bicubic',
        'normalize_density': True,  # Normalize dens to it's upstream values
        'cnorm_type': 'Linear',  # Colormap norm;  options are Pow or Linear
        'cpow_num': 0.6,  # Used in the PowerNorm
        'UseDivCmap': False,
        'div_midpoint': 0.0,
        'stretch_colors': False,
        'symmetric_y': False,
        'cmap': 'None',  # If cmap is none, the plot inherits the parent's cmap
        'face_color': 'gainsboro'}

    def __init__(self, parent, pos, param_dict):
        tmp_dict = {}
        tmp_dict.update(self.plot_param_dict)
        tmp_dict.update(param_dict)
        iseultPlot.__init__(self, parent, pos, tmp_dict)
        self.chart_type = 'ScalarFlds'

    def axis_info(self):
        if self.parent.MainParamDict['LinkSpatial'] != 0:
            self.x_axis_info = {'data_ax': 'x', 'pos': self.pos, 'axes': 'x'}

            if self.param_dict['twoD']:
                if self.parent.MainParamDict['2DSlicePlane'] == 0:  # x-y plane
                    self.y_axis_info = {
                        'data_ax': 'y',
                        'pos': self.pos,
                        'axes': 'y'
                    }
                elif self.parent.MainParamDict['2DSlicePlane'] == 1:  # x-z
                    self.y_axis_info = {
                        'data_ax': 'z',
                        'pos': self.pos,
                        'axes': 'y'
                    }
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

    def draw(self):
        sim = self.parent.sims[self.param_dict['sim_num']]
        shock_loc = sim.get_shock_loc()
        # at some point we may need to support
        # shocks along different axes but for now
        if shock_loc['axis'] != 'x' or shock_loc['shock_loc'] == 0:
            print("Shock must be defined along x axis.")
            self.param_dict['show_shock'] = False

        self.shock_line = self.axes.axvline(
            shock_loc['shock_loc'], linewidth=1.5,
            linestyle='--', color='w',
            path_effects=[
                PathEffects.Stroke(linewidth=2, foreground='k'),
                PathEffects.Normal()])

        self.shock_line.set_visible(
            self.param_dict['show_shock'])

        if self.param_dict['cmap'] == 'None':
            if self.param_dict['UseDivCmap']:
                self.cmap = self.parent.MainParamDict['DivColorMap']

            else:
                self.cmap = self.parent.MainParamDict['ColorMap']

        else:
            self.cmap = self.param_dict['cmap']

        self.dens_color = new_cmaps.cmap_to_hex(0.5, self.cmap)

        # get c_omp and istep to convert cells to physical units
        self.c_omp = sim.get_data(data_class='param', attribute='c_omp')
        self.istep = sim.get_data(data_class='param', attribute='istep')

        # FIND THE SLICE
        self.ySlice = self.parent.calc_slices('y', sim)
        self.zSlice = self.parent.calc_slices('z', sim)

        self.scalar_fld = sim.get_data(
            data_class='scalar_flds',
            fld=self.param_dict['flds_type'])

        # Now that the data is loaded, start making the plots
        # Make the plots
        if self.param_dict['twoD']:
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

            self.image.set_cmap(new_cmaps.cmaps[self.cmap])
            self.cbar.set_cmap(new_cmaps.cmaps[self.cmap])

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

            if not self.param_dict['show_cbar']:
                self.axC.set_visible(False)

            self.axes.set_xlabel(
                r'$x\ [c/\omega_{pe}]$',
                labelpad=self.parent.MainParamDict['xLabelPad'],
                color='black',
                size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 0:
                self.axes.set_ylabel(
                    r'$y\ [c/\omega_{pe}]$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(
                    r'$z\ [c/\omega_{pe}]$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

        # 1D simulations
        else:
            self.axC.set_visible(False)
            self.xaxis = sim.get_data(
                data_class='axes',
                attribute='x')

            self.linedens = self.axes.plot(
                [1, 1], [-0.5, 0.5],
                color=self.dens_color)

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

        self.refresh()
        self.link_handler()

    def refresh(self):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown.  If
        hasn't changed, or isn't viewed, don't touch it. The difference between
        this and last time, is that we won't actually do any drawing in the
        plot. The plot will be redrawn after all subplots data is changed. '''
        sim = self.parent.sims[self.param_dict['sim_num']]

        self.scalar_fld = sim.get_data(
            data_class='scalar_flds',
            fld=self.param_dict['flds_type'])
        self.xaxis = sim.get_data(
            data_class='axes',
            attribute='x')
        self.c_omp = sim.get_data(
            data_class='param',
            attribute='c_omp')
        self.istep = sim.get_data(
            data_class='param',
            attribute='istep')

        # FIND THE SLICE

        self.ySlice = self.parent.calc_slices('y', sim)
        self.zSlice = self.parent.calc_slices('z', sim)

        # Main goal, only change what is showing..
        # First do the 1D plots, because it is simpler
        if self.param_dict['twoD'] == 0:
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
            self.an_2d.set_text(self.scalar_fld['label'])
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
                    r'$y\ [c/\omega_{pe}]$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])

            if self.parent.MainParamDict['2DSlicePlane'] == 1:
                self.axes.set_ylabel(
                    r'$z\ [c/\omega_{pe}]$',
                    labelpad=self.parent.MainParamDict['yLabelPad'],
                    color='black',
                    size=self.parent.MainParamDict['AxLabelSize'])
        if self.param_dict['show_shock']:
            tmp = sim.get_shock_loc()
            if tmp['axis'] == 'x':
                self.shock_line.set_xdata([tmp['shock_loc'], tmp['shock_loc']])
        self.set_v_max_min()
        self.save_home()

    def set_v_max_min(self):
        if not self.param_dict['twoD']:
            min_max = [
                self.linedens[0].get_data()[1].min(),
                self.linedens[0].get_data()[1].max()]
            dist = min_max[1]-min_max[0]
            min_max[0] -= 0.04*dist
            min_max[1] += 0.04*dist
            if self.param_dict['set_v_min']:
                min_max[0] = self.param_dict['v_min']
            if self.param_dict['set_v_max']:
                min_max[0] = self.param_dict['v_max']
            if self.param_dict['symmetric_y']:
                tmp = max(abs(min_max[0]), abs(min_max[1]))
                min_max[0] = -tmp
                min_max[1] = tmp

            self.axes.set_ylim(min_max)

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
