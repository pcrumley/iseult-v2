from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
# eventually i need to make a custom toolbar that overides the zoom function


class myCustomToolbar(NavigationToolbar2Tk):
    def __init__(self, plotCanvas, parent):
        # create the default toolbar
        # plotCanvas is the tk Canvas we want to link to the toolbar,
        # parent is the iseult main app
        NavigationToolbar2Tk.__init__(self, plotCanvas, parent)
        # print(self._nav_stack)
        self.parent = parent
