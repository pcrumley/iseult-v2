import os, yaml
import tkinter as Tk
from tkinter import ttk, messagebox

def save_iseult_cfg(oengus, window_size, cfgfile, cfgname):
    # When adding sections or items, add them in the reverse order of
    # how you want them to be displayed in the actual file.
    # In addition, please note that using RawConfigParser's and the raw
    # mode of ConfigParser's respective set functions, you can assign
    # non-string values to keys internally, but will receive an error
    # when attempting to write to a file or when you get it in non-raw
    # mode. SafeConfigParser does not allow such assignments to take place.
    #config.add_section('general')
    cfgDict = {}
    #config.set('general', 'ConfigName', cfgname)

    #config.add_section('main')
    cfgDict['general'] = {'ConfigName': cfgname}
    #DictList = ['HSubPlotParams', 'VSubPlotParams']
    #IntListsList = ['HAxesExtent', 'HCbarExtent', 'VAxesExtent', 'VCbarExtent']

    # Update the 'WindowSize' attribute to the current window size
    oengus.MainParamDict['WindowSize'] = window_size #str(self.winfo_width())+'x'+str(self.winfo_height())
    # Get figsize and dpi

    oengus.MainParamDict['FigSize'] = [float(oengus.figure.get_size_inches()[0]),float(oengus.figure.get_size_inches()[1])]

    #print(self.MainParamDict['FigSize'], type(self.MainParamDict['FigSize']))
    oengus.MainParamDict['dpi'] = oengus.figure.dpi
    #print(self.MainParamDict['FigSize'], self.MainParamDict['dpi'] )
    # Update the current subplot params


    tmp_param_str = 'HSubPlotParams' if oengus.MainParamDict['HorizontalCbars'] else 'VSubPlotParams'
    try:
        oengus.MainParamDict[tmp_param_str]['left']=float(oengus.figure.subplotpars.left)
        oengus.MainParamDict[tmp_param_str]['right']=float(oengus.figure.subplotpars.right)
        oengus.MainParamDict[tmp_param_str]['top']=float(oengus.figure.subplotpars.top)
        oengus.MainParamDict[tmp_param_str]['bottom']=float(oengus.figure.subplotpars.bottom)
        oengus.MainParamDict[tmp_param_str]['wspace']=float(oengus.figure.subplotpars.wspace)
        oengus.MainParamDict[tmp_param_str]['hspace']=float(oengus.figure.subplotpars.hspace)

    except:
        pass
    for i in range(oengus.MainParamDict['NumOfRows']):
        for j in range(oengus.MainParamDict['NumOfCols']):
            tmp_str = f"Chart{i}_{j}"
            #config.add_section(tmp_str)

            cfgDict[tmp_str] = oengus.SubPlotList[i][j].param_dict
            cfgDict[tmp_str]['chart_type'] = oengus.SubPlotList[i][j].chart_type
    cfgDict['MainParamDict'] = oengus.MainParamDict
    #print(yaml.dump(cfgDict))
    # Writing our configuration file to 'example.cfg'

    with open(cfgfile, 'w') as cfgFile:
        cfgFile.write(yaml.safe_dump(cfgDict))


class SaveDialog(Tk.Toplevel):

    def __init__(self, parent, title = None):

        Tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
#        body.pack(fill=Tk.BOTH)#, expand=True)
        body.pack(fill = Tk.BOTH, anchor = Tk.CENTER, expand=1)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        ttk.Label(master, text="Name of View:").grid(row=0)
        self.e1 = ttk.Entry(master, width=17)
        self.e1.grid(row=0, column=1, sticky = Tk.E)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(box, text="Save", width=10, command=self.ok, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        ''' Check to make sure the config file doesn't already exist'''
        Name = str(self.e1.get())
#        AlreadyExists = False
#        os.listdir(os.path.join(self.parent.IseultDir, '.iseult_configs'))
        if Name == '':
            messagebox.showwarning(
                "Bad input",
                "Field must contain a name, please try again"
            )
        else:
            return 1 # override

    def apply(self):
        ''' Save the config file'''
        w_size = f'{self.parent.winfo_width()}x{self.parent.winfo_height()}'
        new_cfg_file = os.path.join(self.parent.IseultDir, '.iseult_configs', str(self.e1.get()).strip().replace(' ', '_') +'.yml')
        save_iseult_cfg(self.parent.oengus, w_size,
            new_cfg_file, str(self.e1.get()).strip())
