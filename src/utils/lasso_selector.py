import numpy as np

from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from functools import partial


class GetPath(object):
    """Get the path  indices from a matplotlib collection using `LassoSelector`

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : :class:`~matplotlib.axes.Axes`
        Axes to interact with.

    collection : :class:`matplotlib.collections.Collection` subclass
        Collection you want to select from.

    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to `alpha_other`.
    """

    def __init__(self, oengus, pos):
        self.canvas = oengus.figure.canvas
        self.canvas.mpl_connect('draw_event', self._draw_event)
        self.axes = oengus.SubPlotList[pos[0]][pos[1]].axes
        self.lasso = LassoSelector(
            self.axes,
            #lineprops={'color': 'red', 'linewidth': 4, 'alpha': 0.8},
            onselect=self.onselect#partial(
        )

    def _draw_event(self, evt):
        # after drawing, grab the new background
        self.bg = self.canvas.copy_from_bbox(self.axes.bbox)

    def onselect(self, verts):
        print(f'hello from subplot')
        path = Path(verts)
        #print(path)
        # self.ind = np.nonzero(path.contains_points(self.xys))[0]
        # self.fc[:, -1] = self.alpha_other
        # self.fc[self.ind, -1] = 1
        # self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    # def disconnect(self):
        # self.lasso.disconnect_events()
        # self.fc[:, -1] = 1
        # self.collection.set_facecolors(self.fc)
    #    self.canvas.draw_idle()


"""
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    data = np.random.rand(100, 2)*2

    subplot_kw = dict(xlim=(0, 2), ylim=(0, 2), autoscale_on=False)
    fig, ax = plt.subplots(subplot_kw=subplot_kw)

    pts = ax.scatter(data[:, 0], data[:, 1], s=80)

    selector = SelectFromCollection(ax, pts)

    def accept(event):
        if event.key == "enter":
            print("Selected points:")
            print(selector.xys[selector.ind])
            selector.disconnect()
            ax.set_title("")
            fig.canvas.draw()

    fig.canvas.mpl_connect("key_press_event", accept)
    ax.set_title("Press enter to accept selected points.")

    plt.show()
"""
