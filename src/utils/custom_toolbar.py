from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT


class myCustomToolbar(NavigationToolbar2QT):
    def __init__(self, plotCanvas, parent):
        # create the default toolbar
        # plotCanvas is the tk Canvas we want to link to the toolbar,
        # parent is the iseult main app
        NavigationToolbar2QT.__init__(self, plotCanvas, parent)
        # print(self._nav_stack)
        self.parent = parent

    def home(self):
        self.parent.oengus.home()
