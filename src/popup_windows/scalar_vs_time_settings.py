import tkinter as Tk
from tkinter import ttk
import new_cmaps
from functools import partial
from validate_plot_opts import validate_color, validate_ls, \
    validate_marker, validate_marker_size


class ScalarVsTimeSettings(Tk.Toplevel):

    def __init__(self, parent, loc):
        self.parent = parent
        Tk.Toplevel.__init__(self)
        self.loc = loc
        self.plot_opts = ['label', 'color', 'ls', 'marker', 'markersize']
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
        self.line_box = ttk.Frame(master)
        # ttk.Label(box, text="Show Line").grid(row=0, column=0)
        ttk.Label(self.line_box, text="Simulation").grid(row=0, column=1)
        ttk.Label(self.line_box, text="Quantity").grid(row=0, column=2)
        ttk.Label(self.line_box, text="Label").grid(row=0, column=3)
        ttk.Label(self.line_box, text="Color").grid(row=0, column=4)
        ttk.Label(self.line_box, text="Line style").grid(row=0, column=5)
        ttk.Label(self.line_box, text="Marker").grid(row=0, column=6)
        ttk.Label(self.line_box, text="Marker Size").grid(row=0, column=7)

        self.line_var_helpers = []

        for i in range(len(self.lines)):
            self.add_line_options(i)

        self.line_box.pack()
        self.buttonbox(master)

    def gen_plot_args(self, line_num):
        line = self.lines[line_num]
        line['plot_args']['ls'] = ':'
        line['plot_args']['marker'] = next(self.subplot.marker_cycle)
        line['plot_args']['color'] = next(self.subplot.color_cycle)
        line['plot_args']['visible'] = True
        line['plot_args']['markersize'] = 5

    def add_line(self, event=None):
        i = len(self.lines)
        line_dict = {}
        for key in ['sim_num', 'scalar']:
            line_dict[key] = self.lines[i-1][key]
        line_dict['plot_args'] = {
            'label': self.lines[i-1]['plot_args']['label']
        }
        self.lines.append(line_dict)

        self.gen_plot_args(i)
        self.add_line_options(i)
        self.subplot.draw()
        self.parent.oengus.canvas.draw()

    def buttonbox(self, master):
        # add standard button box. override if you don't want the
        # standard buttons
        box = ttk.Frame(master)
        w = ttk.Button(
            box, text='Add line', width=10,
            command=self.add_line, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box, text='Remove line', width=10,
            command=self.remove)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        # w = ttk.Button(box, text="Refresh", width=10, command=self.remove)
        # w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(
            box, text="Ok", width=10,
            command=self.ok)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        # self.bind("<Return>", self.ok)
        # self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics
    def add_line_options(self, line_num=0, event=None):
        i = line_num
        line = self.lines[i]
        tmp_dict = {}
        tmp_dict['show_var'] = Tk.IntVar()
        tmp_dict['show_var'].set(line['plot_args']['visible'])
        tmp_dict['show_var'].trace('w', partial(self.show_line_handler, i))
        tmp_dict['show_cb'] = ttk.Checkbutton(
            self.line_box, text='show line',
            variable=tmp_dict['show_var'])
        tmp_dict['show_cb'].grid(
            row=i+1, column=0
        )
        tmp_dict['sim_var'] = Tk.StringVar(self)
        tmp_dict['sim_var'].set(
            self.parent.oengus.sim_names[line['sim_num']])
        #

        tmp_dict['sim_op'] = ttk.OptionMenu(
            self.line_box, tmp_dict['sim_var'],
            self.parent.oengus.sim_names[line['sim_num']],
            *tuple(self.parent.oengus.sim_names))
        tmp_dict['sim_op'].grid(
            row=i + 1, column=1, sticky=Tk.W + Tk.E)
        tmp_dict['sim_var'].trace('w',  partial(self.sim_handler, i))
        # the Radiobox Control to choose the Field Type
        tmp_dict['quantity'] = Tk.StringVar(self)
        tmp_dict['quantity'].set(line['scalar'])

        cur_sim = self.parent.oengus.sims[line['sim_num']]
        scalars = cur_sim.get_available_quantities()['scalars']

        tmp_dict['quant_op'] = ttk.OptionMenu(
            self.line_box, tmp_dict['quantity'],
            line['scalar'],
            *tuple())

        self.update_quantity_menu(
            tmp_dict['quantity'], list(scalars), tmp_dict['quant_op'])

        tmp_dict['quantity'].trace('w', partial(self.quantity_handler, i))

        tmp_dict['quant_op'].grid(
            row=i+1, column=2,
            sticky=Tk.W + Tk.E)

        for j, elm in enumerate(self.plot_opts):
            tmp_opt_dict = {}
            tmp_dict[elm] = tmp_opt_dict
            tmp_opt_dict['var'] = Tk.StringVar(self)
            tmp_opt_dict['var'].set(line['plot_args'][elm])
            entry_width = 20 if elm == 'label' else 7
            tmp_opt_dict['entry'] = ttk.Entry(
                self.line_box,
                textvariable=tmp_opt_dict['var'],
                width=entry_width)

            tmp_opt_dict['entry'].grid(
                row=i + 1,
                column=3 + j,
                sticky=Tk.W)

        self.line_var_helpers.append(tmp_dict)

    def remove(self, event=None):
        if len(self.lines) > 1:
            tmp_dict = self.line_var_helpers.pop()
            self.lines.pop()
            # First destroy all the tk things
            for key in ['show_cb', 'sim_op', 'quant_op']:
                tmp_dict[key].destroy()
            for elm in self.plot_opts:
                tmp_dict[elm]['entry'].destroy()
            self.subplot.draw()
            self.parent.oengus.canvas.draw()

    def ok(self, event=None):
        if not self.validate():
            # put focus back
            self.initial_focus.focus_set()
            return
        self.update_idletasks()
        self.withdraw()
        self.parent.oengus.canvas.draw()
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
        self.text_callback()
        self.line_plot_options_callback()

        # NEED TO PUT VALIDATION HERE
        if not bad:
            return True

    def ctypeChanged(self, *args):
        if self.ctypevar.get() == self.subplot.chart_type:
            pass
        else:
            self.parent.changePlotType(self.loc, self.ctypevar.get())
            self.destroy()

    def TxtEnter(self, e):
        self.text_callback()
        self.line_plot_options_callback()

    def show_line_handler(self, i, *args):
        if i < len(self.subplot.param_dict['lines']):
            line_opts = self.subplot.param_dict['lines'][i]['plot_args']
            show_tk_var = self.line_var_helpers[i]['show_var']
            if line_opts['visible'] != show_tk_var.get():
                line_opts['visible'] = show_tk_var.get()
                self.subplot.draw()
                self.parent.oengus.canvas.draw()

    def quantity_handler(self, i, *args):
        if i < len(self.subplot.param_dict['lines']):
            line = self.subplot.param_dict['lines'][i]
            tk_var = self.line_var_helpers[i]['quantity']
            label_entry = self.line_var_helpers[i]['label']['entry']
            if line['scalar'] != tk_var.get():
                line['scalar'] = tk_var.get()
                label_entry.delete(0, Tk.END)
                cur_sim = self.parent.oengus.sims[line['sim_num']]
                scalars = cur_sim.get_available_quantities()['scalars']
                new_label = scalars[tk_var.get()]['label']
                line['plot_args']['label'] = new_label
                label_entry.insert(0, new_label)
                self.subplot.draw()
                self.parent.oengus.canvas.draw()

    def sim_handler(self, i, *args):
        if i < len(self.subplot.param_dict['lines']):
            line = self.subplot.param_dict['lines'][i]
            tk_var = self.line_var_helpers[i]['sim_var']
            cur_name = self.parent.oengus.sim_names[line['sim_num']]
            cur_sim = self.parent.oengus.sims[line['sim_num']]
            scalars = cur_sim.get_available_quantities()['scalars']
            if cur_name != tk_var.get():
                line['sim_num'] = self.parent.oengus.sim_names.index(
                    tk_var.get())
                # update available quantities
                self.update_quantity_menu(
                    self.line_var_helpers[i]['quantity'],
                    list(scalars),
                    self.line_var_helpers[i]['quant_op'])
                self.parent.oengus.calc_sims_shown()
                self.parent.playbackbar.update_sim_list()

                self.subplot.refresh()
                self.parent.oengus.canvas.draw()

    def update_quantity_menu(self, tk_var, options, option_menu):
        menu = option_menu['menu']
        menu.delete(0, "end")
        for attr in options:
            menu.add_command(
                label=attr,
                command=lambda value=attr: tk_var.set(value))
        if not (tk_var.get() in options):
            attr_var.set(options[0])

    def line_plot_options_callback(self):
        for line, helper in zip(self.lines, self.line_var_helpers):
            plot_args = line['plot_args']

            # Validate label (no val needed, raw string ok)
            plot_args['label'] = helper['label']['var'].get()

            # line style must be ok
            if validate_ls(helper['ls']['var'].get()):
                plot_args['ls'] = helper['ls']['var'].get()
            else:
                plot_args['ls'] = ':'

            color = helper['color']['var'].get()
            color = color.lower().replace(' ', '')
            if validate_color(color):
                plot_args['color'] = color
            else:
                helper['color']['var'].set(plot_args['color'])

            if validate_marker(helper['marker']['var'].get()):
                plot_args['marker'] = helper['marker']['var'].get()
            else:
                helper['marker']['var'].set(plot_args['marker'])

            try:
                ms = float(helper['markersize']['var'].get())
                if ms >=0:
                    plot_args['markersize'] = ms
                else:
                    helper['markersize']['var'].set(
                        plot_args['markersize'])
            except ValueError:
                helper['markersize']['var'].set(
                    plot_args['markersize'])

        self.subplot.draw()
        self.parent.oengus.canvas.draw()

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
