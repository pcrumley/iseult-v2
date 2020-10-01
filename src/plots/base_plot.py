import matplotlib
import numpy as np
import sys
import new_cmaps
from new_cnorms import PowerNormWithNeg, PowerNormFunc
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from functools import partial


class iseultPlot:
    '''The base class that all of the subplots must be subclasses of.
    Will elaborate documentation more later.'''
    # A way to make the colorbar display better
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    plot_param_dict = {
        'twoD': 0,
        'cnorm_type': 'Log',  # Colormap normalization. Opts are Log or Linear
        'cpow_num': 0.6,
        'show_cbar': True,
        'cmap': 'None',
        'UseDivCmap': False,
        'OutlineText': True,
        'interpolation': 'bicubic',
        'face_color': 'gainsboro'}

    _linked_axes = []

    def __init__(self, parent, pos, param_dict):
        self.param_dict = {}
        self.param_dict.update(param_dict)
        self.pos = pos
        self.parent = parent
        self.figure = self.parent.figure
        self._zoom_x_min = None
        self._zoom_x_max = None
        self._zoom_y_min = None
        self._zoom_y_max = None
        self.home_x = None
        self.home_y = None
        self.x_axis_info = None
        self.y_axis_info = None

    @property
    def annotate_kwargs(self):
        if self.param_dict['OutlineText']:
            return {
                'horizontalalignment': 'right',
                'verticalalignment': 'top',
                'size': self.parent.MainParamDict['annotateTextSize'],
                'path_effects': [
                    PathEffects.withStroke(linewidth=1.5, foreground="k")]
            }
        else:
            return {
                'horizontalalignment': 'right',
                'verticalalignment': 'top',
                'size': self.parent.MainParamDict['annotateTextSize']}

    def draw(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError

    def get_sim_nums(self):
        if 'sim_num' in self.param_dict.keys():
            return [self.param_dict['sim_num']]
        else:
            return []
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

    def build_axes(self):
        self.gs = gridspec.GridSpecFromSubplotSpec(
            100, 100,
            subplot_spec=self.parent.gs0[self.pos])

        self.axes = self.figure.add_subplot(
            self.gs[
                self.parent.axes_extent[0]:self.parent.axes_extent[1],
                self.parent.axes_extent[2]:self.parent.axes_extent[3]])

        self.axes.callbacks.connect(
            'xlim_changed',
            partial(
                self.parent.link_axes,
                ax_type='x',
                subplot=self))
        self.axes.callbacks.connect(
            'ylim_changed',
            partial(
                self.parent.link_axes,
                ax_type='y',
                subplot=self))
        self.axC = self.figure.add_subplot(
            self.gs[
                self.parent.cbar_extent[0]:self.parent.cbar_extent[1],
                self.parent.cbar_extent[2]:self.parent.cbar_extent[3]])
        self.axC.set_navigate(False)

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

        if int(matplotlib.__version__[0]) < 2:
            self.axes.set_axis_bgcolor(self.param_dict['face_color'])
        else:
            self.axes.set_facecolor(self.param_dict['face_color'])

        self.axes.tick_params(
            labelsize=self.parent.MainParamDict['NumFontSize'],
            color='black')

    def CbarTickFormatter(self, label=''):
        ''' A helper function that sets the cbar ticks & labels. This used to
        be easier, but because I am no longer using the colorbar class i have
        to do stuff manually.'''
        clim = np.copy(self.image.get_clim())
        if self.param_dict['cnorm_type'] == "Log":
            clim = np.log10(clim[0]), np.log10(clim[1])
        if self.param_dict['show_cbar']:
            if self.param_dict['cnorm_type'] == "Pow":
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

                else:
                    self.cbar.set_data(np.transpose(cbardata)[::-1])

            if self.parent.MainParamDict['HorizontalCbars']:
                self.cbar.set_extent([clim[0], clim[1], 0, 1])
                self.axC.set_xlim(clim[0], clim[1])
                self.axC.set_xlabel(
                    label,
                    labelpad=self.parent.MainParamDict['cbarLabelPad'],
                    size=self.parent.MainParamDict['AxLabelSize'])
            else:
                self.cbar.set_extent([0, 1, clim[0], clim[1]])
                self.axC.set_ylim(clim[0], clim[1])
                self.axC.locator_params(axis='y', nbins=6)
                self.axC.yaxis.set_label_position("right")
                self.axC.set_ylabel(
                    label,
                    labelpad=self.parent.MainParamDict['cbarLabelPad'],
                    rotation=-90,
                    size=self.parent.MainParamDict['AxLabelSize'])

    def save_axes_pos(self):
        xmin, xmax = self.axes.get_xlim()
        self._zoom_x_min = xmin if xmin != self.home_x[0] else None
        self._zoom_x_max = xmax if xmax != self.home_x[1] else None

        ymin, ymax = self.axes.get_ylim()
        self._zoom_y_min = ymin if ymin != self.home_y[0] else None
        self._zoom_y_max = ymax if ymax != self.home_y[1] else None

    def save_home(self):
        self.home_x = self.axes.get_xlim()
        self.home_y = self.axes.get_ylim()

    def go_home(self):
        self.axes.set_xlim(self.home_x)
        self.axes.set_ylim(self.home_y)

    def load_axes_pos(self):
        if self._zoom_x_min is not None:
            self.axes.set_xlim(left=self._zoom_x_min)

        if self._zoom_x_max is not None:
            self.axes.set_xlim(right=self._zoom_x_max)

        if self._zoom_y_min is not None:
            self.axes.set_ylim(bottom=self._zoom_y_min)

        if self._zoom_y_max is not None:
            self.axes.set_ylim(top=self._zoom_y_max)

    @classmethod
    def link_up(cls, payload):
        if payload is not None:
            cls._linked_axes.append(payload)

    @classmethod
    def unlink(cls, pos):
        tmpList = []
        for elm in cls._linked_axes:
            if elm['pos'][0] == pos[0] and elm['pos'][1] == pos[1]:
                pass
            else:
                tmpList.append(elm)
        cls._linked_axes = tmpList

    @classmethod
    def get_linked_ax(cls):
        return cls._linked_axes

    def link_handler(self):
        raise NotImplementedError

    def axis_info(self):
        # A function that should return None if the x-axis are not spatial
        # otherwise it should set x_axis_info to
        # {'data_ax': val, 'pos': self.pos, 'axes': 'x'}
        raise NotImplementedError

    def remove(self):
        try:
            self.axC.remove()

        except AttributeError:
            pass

        except KeyError:
            pass

        self.axes.remove()
