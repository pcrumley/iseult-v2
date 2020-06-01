import numpy as np
import new_cmaps
import matplotlib.transforms as mtransforms
from base_plot import iseultPlot


class vectorFldsPlot(iseultPlot):
    # A dictionary of all of the parameters for this plot
    # with the default values

    plot_param_dict = {
        'twoD': 0,
        'field_type': 'B',
        'sim_num': 0,
        'show_x': 1,
        'show_y': 1,
        'show_z': 1,
        'show_cbar': True,
        'v_min': 0,
        'v_max': 10,
        'set_v_min': False,
        'set_v_max': False,
        'show_shock': False,
        'show_FFT_region': False,
        'OutlineText': True,
        'spatial_x': True,
        'spatial_y': False,
        'show_labels': True,
        'normalize_fields': True,  # Normalize fields to their upstream values
        'cnorm_type': 'Linear',  # Colormap norm: Log, Pow or Linear
        'cpow_num': 1.0,  # Used in the PowerNorm
        # The cpow color norm normalizes data to [0,1] using
        # np.sign(x-midpoint)*np.abs(x-midpoint)**(-cpow_num) -> [0,midpoint,1]
        # if it is a divering cmap or [0,1] if it is not a divering cmap
        'div_midpoint': 0.0,
        'interpolation': 'none',
        # If cmap is none, the plot will inherit the parent's cmap
        'cmap': 'None',
        'UseDivCmap': True,  # Use a diverging cmap for the 2d plots
        # plots lines showing how the CPUs are divvying up
        # the computational region
        'show_cpu_domains': False,
        # If stretch colors is false, then for a diverging cmap the plot
        # ensures -b and b are the same distance from the midpoint of the cmap.
        'stretch_colors': False,
        'face_color': 'gainsboro'}

    # A way to make the colorbar display better. I'm not sure this is necessary
    # anymore.
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(super().plot_param_dict)
        self.param_dict.update(self.plot_param_dict)
        self.param_dict.update(param_dict)
        self.pos = pos

        self.chart_type = 'VectorFlds'
        self.changedD = False
        self.parent = parent
        self.figure = self.parent.figure

    def draw(self, sim=None, n=None):
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        self.c_omp = sim.get_data(n, data_class='param', attribute='c_omp')
        self.istep = sim.get_data(n, data_class='param', attribute='istep')

        # Make the plots
        self.build_axes()
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

        else:
            self.axC.set_visible(False)
            self.xaxis = sim.get_data(
                n, data_class='axes',
                attribute='x')

            if self.param_dict['show_x']:
                self.vec_x = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='x')

            if self.param_dict['show_y']:
                self.vec_y = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='y')

            if self.param_dict['show_z']:
                self.vec_z = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='z')


            # Make the 1-D plots
            self.line_x = self.axes.plot([1, 1], [-0.5, 0.5])
            self.line_y = self.axes.plot([1, 1], [-0.5, 0.5])
            self.line_z = self.axes.plot([1, 1], [-0.5, 0.5])

            self.line_x[0].set_visible(self.param_dict['show_x'])
            self.line_y[0].set_visible(self.param_dict['show_y'])
            self.line_z[0].set_visible(self.param_dict['show_z'])

            self.annotate_pos = [0.8, 0.9]
            self.anx = self.axes.annotate(
                '',
                xy=self.annotate_pos,
                xycoords='axes fraction',
                **self.annotate_kwargs)
            self.annotate_pos[0] += .08
            self.any = self.axes.annotate(
                '',
                xy=self.annotate_pos,
                xycoords='axes fraction',
                **self.annotate_kwargs)
            self.annotate_pos[0] += .08
            self.anz = self.axes.annotate(
                '',
                xy=self.annotate_pos,
                xycoords='axes fraction',
                **self.annotate_kwargs)

            self.anx.set_visible(self.param_dict['show_x'])
            self.any.set_visible(self.param_dict['show_y'])
            self.anz.set_visible(self.param_dict['show_z'])

            # Build some iterables for going over the lines
            self.key_list = ['show_x', 'show_y', 'show_z']
            self.line_list = [self.line_x[0], self.line_y[0], self.line_z[0]]

            self.axes.set_xlim(self.xaxis['data'][0], self.xaxis['data'][-1])

            if self.param_dict['set_v_min']:
                self.axes.set_ylim(bottom=self.param_dict['v_min'])
            if self.param_dict['set_v_max']:
                self.axes.set_ylim(top=self.param_dict['v_max'])

            # Handle the axes labeling
            self.axes.set_xlabel(
                self.xaxis['label'],
                labelpad=self.parent.MainParamDict['xLabelPad'],
                color='black',
                size=self.parent.MainParamDict['AxLabelSize'])

        self.update_labels_and_colors(sim, n)
        self.refresh(sim=sim, n=n)

    def refresh(self, sim=None, n=None):
        '''This is a function that will be called only if self.axes already
        holds a density type plot. We only update things that have shown.  If
        hasn't changed, or isn't viewed, don't touch it. The difference
        between this and draw function, is that we won't create any new
        matplotlib objects, instead just update their data. the plot
        will be redrawn after all subplots data are changed.'''

        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        self.ySlice = self.parent.calc_slices('y', sim, n)
        self.zSlice = self.parent.calc_slices('z', sim, n)
        self.c_omp = sim.get_data(n, data_class='param', attribute='c_omp')
        self.istep = sim.get_data(n, data_class='param', attribute='istep')

        # Now that the data is loaded, start making the plots
        if self.param_dict['twoD']:
            if self.param_dict['show_x']:
                self.vec_2d = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='x')

            elif self.param_dict['show_y']:
                self.vec_2d = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='y')
            else:
                self.vec_2d = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='z')

            self.an_2d.set_text(self.vec_2d['label'])

            if self.parent.MainParamDict['2DSlicePlane'] == 0:   # x-y plane
                self.image.set_data(self.vec_2d['data'][self.zSlice, :, :])
            elif self.parent.MainParamDict['2DSlicePlane'] == 1:  # x-z plane
                self.image.set_data(self.vec_2d['data'][:, self.ySlice, :])

            self.ymin = 0
            self.ymax = self.image.get_array().shape[0]/self.c_omp*self.istep

            self.xmin = 0
            self.xmax = self.image.get_array().shape[1]/self.c_omp*self.istep
            self.image.set_extent([self.xmin, self.xmax, self.ymin, self.ymax])

        # Main goal, only change what is showing..
        # First do the 1D plots, because it is simpler
        else:
            self.xaxis = sim.get_data(
                n, data_class='axes',
                attribute='x')

            if self.param_dict['show_x']:
                self.vec_x = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='x')

            if self.param_dict['show_y']:
                self.vec_y = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='y')

            if self.param_dict['show_z']:
                self.vec_z = sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='z')

            if self.parent.MainParamDict['Average1D']:

                if self.param_dict['show_x']:
                    self.line_x[0].set_data(
                        self.xaxis['data'],
                        np.average(
                            self.vec_x['data'].reshape(
                                -1, self.vec_x['data'].shape[-1]), axis=0))

                if self.param_dict['show_y']:
                    self.line_y[0].set_data(
                        self.xaxis['data'],
                        np.average(
                            self.vec_y['data'].reshape(
                                -1, self.vec_y['data'].shape[-1]), axis=0))

                if self.param_dict['show_z']:
                    self.line_z[0].set_data(
                        self.xaxis['data'],
                        np.average(
                            self.vec_z['data'].reshape(
                                -1, self.vec_z['data'].shape[-1]), axis=0))

            else:  # x-y plane
                if self.param_dict['show_x']:
                    self.line_x[0].set_data(
                        self.xaxis['data'],
                        self.vec_x['data'][self.zSlice, self.ySlice, :])

                if self.param_dict['show_y']:
                    self.line_y[0].set_data(
                        self.xaxis['data'],
                        self.vec_y['data'][self.zSlice, self.ySlice, :])
                if self.param_dict['show_z']:
                    self.line_z[0].set_data(
                        self.xaxis['data'],
                        self.vec_z['data'][self.zSlice, self.ySlice, :])

        self.set_v_max_min()
        self.save_home()

    def update_labels_and_colors(self, sim=None, n=None):
        if sim is None:
            sim = self.parent.sims[self.param_dict['sim_num']]

        if self.param_dict['cmap'] == 'None':
            cmap = self.parent.MainParamDict['ColorMap']
            x_color = new_cmaps.cmap_to_hex(0.2, cmap)
            y_color = new_cmaps.cmap_to_hex(0.5, cmap)
            z_color = new_cmaps.cmap_to_hex(0.8, cmap)

            if self.param_dict['UseDivCmap']:
                cmap = self.parent.MainParamDict['DivColorMap']

        else:
            cmap = self.param_dict['cmap']
            x_color = new_cmaps.cmap_to_hex(0.2, cmap)
            y_color = new_cmaps.cmap_to_hex(0.5, cmap)
            z_color = new_cmaps.cmap_to_hex(0.8, cmap)

        if self.param_dict['twoD']:
            self.image.set_cmap(new_cmaps.cmaps[cmap])
            self.cbar.set_cmap(new_cmaps.cmaps[cmap])

        else:

            self.axes.set_ylabel(
                sim.get_data(
                    n, data_class='vec_flds',
                    fld=self.param_dict['field_type'],
                    component='x')['axis_label'])

            self.vec_x = sim.get_data(
                n, data_class='vec_flds',
                fld=self.param_dict['field_type'],
                component='x')
            self.anx.set_text(self.vec_x['label'])
            self.line_x[0].set_color(x_color)
            self.anx.set_color(x_color)

            self.vec_y = sim.get_data(
                n, data_class='vec_flds',
                fld=self.param_dict['field_type'],
                component='y')
            self.any.set_text(self.vec_y['label'])
            self.line_y[0].set_color(y_color)
            self.any.set_color(y_color)

            self.vec_z = sim.get_data(
                n, data_class='vec_flds',
                fld=self.param_dict['field_type'],
                component='z')

            self.anz.set_text(self.vec_z['label'])
            self.line_z[0].set_color(z_color)
            self.anz.set_color(z_color)

    def set_v_max_min(self):
        # NOTE THIS SHOULD BE CHANGED TO SET THE MIN AND MAX
        # MANUALLY, WILL BE MORE EFFICIENT!

        if not self.param_dict['twoD']:
            self.axes.dataLim = mtransforms.Bbox.unit()
            self.axes.dataLim.update_from_data_xy(
                xy=np.vstack(
                    self.line_list[0].get_data()).T,
                ignore=True)

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
                self.axes.set_xlim(
                    self.parent.MainParamDict['xLeft'],
                    self.parent.MainParamDict['xRight'])
            else:
                self.axes.set_xlim(
                    self.xaxis['data'][0],
                    self.xaxis['data'][-1])

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
    oengus = Oengus(interactive=False, preset_view='test')
    oengus.open_sim(
        picSim(os.path.join(os.path.dirname(__file__), '../output')))
    oengus.create_graphs()
    plt.savefig('test.png')
