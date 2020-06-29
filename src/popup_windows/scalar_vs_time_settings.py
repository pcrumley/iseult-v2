import tkinter as Tk
from tkinter import ttk
import new_cmaps


class ScalarVsTimeSettings(Tk.Toplevel):

    def __init__(self, parent, loc):
        self.parent = parent
        Tk.Toplevel.__init__(self)
        self.loc = loc
        self.wm_title(f'Scalar vs Time Plot {self.loc} Settings')
        self.subplot = self.parent.oengus.SubPlotList[self.loc[0]][self.loc[1]]
        self.params = self.subplot.param_dict
        self.lines = self.params['lines']

        nb = ttk.Notebook(self)
        f1 = ttk.Frame(nb)
        f2 = ttk.Frame(nb)

        nb.add(f1, text='Plot Settings')
        nb.add(f2, text='Line Settings')

        self.bind('<Return>', self.TxtEnter)
        self.initial_focus = self.build_settings_panel(f1)
        self.build_line_table(f2)
#        body.pack(fill=Tk.BOTH)#, expand=True)
        nb.pack(fill=Tk.BOTH, anchor=Tk.CENTER, expand=True)

        # self.buttonbox()

        # self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        # self.wait_window(self)

    #
    # construction hooks
    def build_settings_panel(self, master):
        # Create the OptionMenu to chooses the Chart Type:
        self.ctypevar = Tk.StringVar(self)
        self.ctypevar.set(self.subplot.chart_type)  # default value
        self.ctypevar.trace('w', self.ctypeChanged)

        ttk.Label(
            master, text="Choose Chart Type:").grid(
                row=0, column=0)
        ctypeChooser = ttk.OptionMenu(
            master, self.ctypevar,
            self.subplot.chart_type,
            *tuple(self.parent.oengus.plot_types_dict.keys()))
        ctypeChooser.grid(
            row=0, column=1,
            sticky=Tk.W + Tk.E)

        # Add the ability to fix the y or x limits
        self.lims_helper = [
            {
                'label': 'set y min',
                'param_name': 'set_y_min',
                'to_set_var': Tk.IntVar(),
                'val_param': 'y_min',
                'val_var': Tk.StringVar(),
                'entry': None,
            },
            {
                'label': 'set y max',
                'param_name': 'set_y_max',
                'to_set_var': Tk.IntVar(),
                'val_param': 'y_min',
                'val_var': Tk.StringVar(),
                'entry': None,
            },
            {
                'label': 'set t min',
                'param_name': 'set_x_max',
                'to_set_var': Tk.IntVar(),
                'val_param': 'y_min',
                'val_var': Tk.StringVar(),
                'entry': None,
            },
            {
                'label': 'set t max',
                'param_name': 'set_x_max',
                'to_set_var': Tk.IntVar(),
                'val_param': 'y_min',
                'val_var': Tk.StringVar(),
                'entry': None,
            }
        ]

        for i, elm in enumerate(self.lims_helper):
            label, param = elm['label'], elm['param_name']
            var = elm['to_set_var']
            var.set(self.params[param])
            var.trace('w', self.lim_handler)
            cb = ttk.Checkbutton(
                master, text=label,
                variable=var)
            cb.grid(
                row=2 + i,
                column=2,
                sticky=Tk.W)

            lim_val = self.params[elm['val_param']]
            tk_val = elm['val_var']
            tk_val.set(f'{lim_val}')
            elm['entry'] = ttk.Entry(
                master,
                textvariable=tk_val,
                width=7)
            elm['entry'].grid(
                row=2 + i,
                column=3,
                sticky=Tk.W)

        self.bool_opts = [
            {
                'label': 'y-axis logscale',
                'param_name': 'yLog',
                'bool_var': Tk.IntVar()
            },
            {
                'label': 'Show Legend',
                'param_name': 'show_legend',
                'bool_var': Tk.IntVar()
            },
            {
                'label': 'Show Current Time',
                'param_name': 'show_cur_time',
                'bool_var': Tk.IntVar()
            }
        ]

        for i, opt in enumerate(self.bool_opts):
            label = opt['label']
            param_name = opt['param_name']
            var = opt['bool_var']
            var.set(self.params[param_name])
            var.trace('w', self.bool_handler)
            cb = ttk.Checkbutton(
                master, text=label,
                variable=var)
            cb.grid(
                row=2 + i,
                column=0,
                sticky=Tk.W)

    def build_line_table(self, master):
        # create dialog body.  return widget that should have
        # initial focus
        box = ttk.Frame(master)
        ttk.Label(box, text="Simulation").grid(row=0, column=0)
        ttk.Label(box, text="Quantity").grid(row=0, column=1)
        ttk.Label(box, text="Label").grid(row=0, column=2)
        ttk.Label(box, text="Color").grid(row=0, column=3)
        ttk.Label(box, text="Line style").grid(row=0, column=4)
        ttk.Label(box, text="Marker").grid(row=0, column=5)

        self.line_var_helpers = []
        plot_opts = ['label', 'color', 'ls', 'marker']

        for i, line in enumerate(self.lines):
            tmp_dict = {}
            tmp_dict['sim_var'] = Tk.StringVar(self)
            tmp_dict['sim_var'].set(
                self.parent.oengus.sim_names[line['sim_num']])
            # tmp_dict['sim_var'].trace('w', self.SimChanged)

            ttk.OptionMenu(
                box, tmp_dict['sim_var'],
                self.parent.oengus.sim_names[line['sim_num']],
                *tuple(self.parent.oengus.sim_names)).grid(
                row=i + 1, column=0, sticky=Tk.W + Tk.E)

            # the Radiobox Control to choose the Field Type
            tmp_dict['quantity'] = Tk.StringVar(self)
            tmp_dict['quantity'].set(line['scalar'])

            cur_sim = self.parent.oengus.sims[line['sim_num']]
            scalars = cur_sim.get_available_quantities()['scalars']

            ttk.OptionMenu(
                box, tmp_dict['quantity'],
                line['scalar'],
                *tuple(scalars.keys())).grid(
                row=i+1, column=1,
                sticky=Tk.W + Tk.E)
            for j, elm in enumerate(plot_opts):
                tmp_opt_dict = {}
                tmp_opt_dict['var'] = Tk.StringVar(self)
                print(line['plot_args'][elm])
                tmp_opt_dict['var'].set(line['plot_args'][elm])
                print(tmp_opt_dict['var'].get())
                tmp_opt_dict['entry'] = ttk.Entry(
                    box,
                    textvariable=tmp_opt_dict['var'],
                    width=7)
                tmp_opt_dict['entry'].grid(
                    row=i + 1,
                    column=2 + j,
                    sticky=Tk.W)

            """
            self.labels.append(ttk.Label(box, text=f'{i}'))
            self.labels[-1].grid(row=i+1, column=0)
            e_name = ttk.Entry(box, width=17)
            e_name.insert(0, self.parent.oengus.sims[i].name)
            e_name.grid(row=i+1, column=1, sticky=Tk.E)
            self.names.append(e_name)

            e_dir = ttk.Entry(box, width=27)
            if self.parent.oengus.sims[i].outdir is not None:
                e_dir.insert(0, self.parent.oengus.sims[i].outdir)
            e_dir.grid(row=i+1, column=2, sticky=Tk.E)
            self.dirs.append(e_dir)
            """
        box.pack()
        self.buttonbox(master)

    def buttonbox(self, master):
        # add standard button box. override if you don't want the
        # standard buttons
        box = ttk.Frame(master)
        w = ttk.Button(
            box, text='Add Sim', width=10,
            command=self.add, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Remove Sim", width=10, command=self.remove)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box, text="Open", width=10,
            command=self.ok)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        # self.bind("<Return>", self.ok)
        # self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics
    def add(self, event=None):
        n = len(self.dirs)
        self.parent.oengus.add_sim(f'sim{n}')
        self.labels.append(ttk.Label(self.body, text=f'{n}'))
        self.labels[-1].grid(row=n+1, column=0)
        e_name = ttk.Entry(self.body, width=17)
        e_name.insert(0, self.parent.oengus.sims[n].name)
        e_name.grid(row=n+1, column=1, sticky=Tk.E)
        self.names.append(e_name)

        e_dir = ttk.Entry(self.body, width=27)
        if self.parent.oengus.sims[n].outdir is not None:
            e_dir.insert(0, self.parent.oengus.sims[n].outdir)
        e_dir.grid(row=n+1, column=2, sticky=Tk.E)
        self.dirs.append(e_dir)

    def remove(self, event=None):
        if len(self.labels) > 1:
            self.labels[-1].destroy()
            self.labels.pop()
            self.names[-1].destroy()
            self.names.pop()
            self.dirs[-1].destroy()
            self.dirs.pop()
            self.parent.oengus.pop_sim()

    def ok(self, event=None):
        if not self.validate():
            # put focus back
            self.initial_focus.focus_set()
            return
        self.update_idletasks()
        self.withdraw()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks
    def validate(self):
        ''' Check to make sure the directories are ok '''
        # First change all the names.
        bad = False
        for dir in self.dirs:
            dirname = str(dir.get())
            if not os.path.isdir(dirname):
                messagebox.showwarning(
                    "Bad input",
                    f"{dirname} is not a directory"
                )
                bad = True
        if not bad:
            return 1

    def apply(self):
        # First change all the names.
        for i, name in enumerate(self.names):
            self.parent.oengus.sims[i].name = str(name.get())
        for i, dir in enumerate(self.dirs):
            if self.parent.oengus.sims[i].outdir != str(dir.get()):
                self.parent.oengus.sims[i].outdir = str(dir.get())
        self.parent.oengus.draw_output()

    def ctypeChanged(self, *args):
        if self.ctypevar.get() == self.subplot.chart_type:
            pass
        else:
            self.parent.changePlotType(self.loc, self.ctypevar.get())
            self.destroy()

    def TxtEnter(self, e):
        self.text_callback()

    def text_callback(self):
        to_reload = False
        for elm in self.lims_helper:
            p_name = elm['val_param']
            tk_var = elm['val_var']
            entry = elm['entry']
            set_var = elm['to_set_var']
            try:
                # make sure the user types in a number
                user_num = float(entry.get())

                if abs(user_num - self.params[p_name]) > 1E-4:
                    self.params[p_name] = user_num
                    to_reload += True*set_var.get()

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                tk_var.set(str(self.params[p_name]))

        if to_reload:
            self.subplot.refresh()
            self.parent.oengus.canvas.draw()

    def lim_handler(self, *args):
        for elm in self.lims_helper:
            param_name, var = elm['param_name'], elm['to_set_var']
            self.params[param_name] = var.get()
        self.subplot.refresh()
        self.parent.oengus.canvas.draw()

    def bool_handler(self, *args):
        for elm in self.bool_opts:
            param_name, var = elm['param_name'], elm['bool_var']
            self.params[param_name] = var.get()
        if self.params['yLog']:
            self.subplot.axes.set_yscale('log')
        else:
            self.subplot.axes.set_yscale('linear')
        self.subplot.legend.set_visible(self.params['show_legend'])
        self.subplot.time_line.set_visible(self.params['show_cur_time'])
        self.subplot.refresh()
        self.parent.oengus.canvas.draw()
