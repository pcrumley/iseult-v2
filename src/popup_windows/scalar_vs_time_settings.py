from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QComboBox, QCheckBox, QTabWidget, QSpinBox,
                             QRadioButton)
from PyQt5.QtCore import Qt, QTimer
import new_cmaps
from functools import partial
from validate_plot_opts import validate_color, validate_ls, \
    validate_marker, validate_marker_size
from base_plot_settings import iseultPlotSettings


class ScalarVsTimeSettings(iseultPlotSettings):

    def __init__(self, parent, loc):
        super().__init__(parent, loc)
        self.ignoreChange = False
        self.plot_opts = ['label', 'color', 'ls', 'marker', 'markersize']
        self.lines = self.params['lines']

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'Scalar vs Time Plot {self.loc} Settings')

        layout = QGridLayout()
        tabwidget = QTabWidget()
        tabwidget.addTab(self.settings_tab(), "Plot Settings")
        tabwidget.addTab(self.lines_tab(), "Line Settings")
        layout.addWidget(tabwidget, 0, 0)
        self.setLayout(layout)

    #
    # construction hooks
    def settings_tab(self):
        SettingsTabWidget = QWidget(self)
        # Create the OptionMenu to chooses the Chart Type:
        settings_grid = QGridLayout(SettingsTabWidget)
        settings_grid.addWidget(QLabel('Choose Chart Type:'), 0, 0)
        settings_grid.addWidget(self.chart_type_QComboBox(), 0, 1)

        # Add the ability to fix the y or x limits
        self.lims_helper = [
            {
                'param_name': 'set_y_min',
                'to_set_cb': QCheckBox('set y min'),
                'val_param': 'y_min',
                'entry': None,
            },
            {
                'param_name': 'set_y_max',
                'to_set_cb': QCheckBox('set y max'),
                'val_param': 'y_max',
                'entry': None,
            },
            {
                'param_name': 'set_x_min',
                'to_set_cb': QCheckBox('set t min'),
                'val_param': 'x_min',
                'entry': None,
            },
            {
                'param_name': 'set_x_max',
                'to_set_cb':  QCheckBox('set t max'),
                'val_param': 'x_max',
                'entry': None,
            }
        ]

        for i, elm in enumerate(self.lims_helper):
            param = elm['param_name']
            cb = elm['to_set_cb']
            cb.setChecked(self.params[param])
            cb.stateChanged.connect(self.lim_handler)
            settings_grid.addWidget(cb, 2+i, 2)

            lim_val = self.params[elm['val_param']]

            elm['entry'] = QLineEdit(SettingsTabWidget)
            elm['entry'].setText(f'{lim_val}')
            settings_grid.addWidget(elm['entry'], 2+i, 3)

        self.bool_opts = [

            {
                'param_name': 'yLog',
                'cb': QCheckBox('y-axis logscale')
            },
            {
                'param_name': 'show_legend',
                'cb': QCheckBox('Show Legend')
            },
            {
                'param_name': 'show_cur_time',
                'cb': QCheckBox('Show Current Time')
            }
        ]

        for i, opt in enumerate(self.bool_opts):
            param_name = opt['param_name']
            cb = opt['cb']
            cb.setChecked(self.params[param_name])
            cb.stateChanged.connect(partial(self.bool_handler, param_name))
            settings_grid.addWidget(cb, 2+i, 0)

        SettingsTabWidget.setLayout(settings_grid)
        return SettingsTabWidget

    def lines_tab(self):
        LinesTabWidget = QWidget(self)
        # Create the OptionMenu to chooses the Chart Type:
        self.lines_grid = QGridLayout(LinesTabWidget)
        for i, label in enumerate(['Simulation', 'Quantity', 'Label',
                                   'Color', 'Line Style', 'Marker',
                                   'Marker Size']):
            self.lines_grid.addWidget(QLabel(label), 0, 1 + i)
        self.line_var_helpers = []


        for i in range(len(self.lines)):
            self.add_line_options(i)

        LinesTabWidget.setLayout(self.lines_grid)

        #self.buttonbox(master)
        return LinesTabWidget

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
        self.subplot.save_axes_pos()
        self.subplot.draw()
        self.subplot.load_axes_pos()
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
        tmp_dict['show_cb'] = QCheckBox('show line')
        tmp_dict['show_cb'].setChecked(line['plot_args']['visible'])
        tmp_dict['show_cb'].stateChanged.connect(
            partial(self.show_line_handler, i))
        self.lines_grid.addWidget(tmp_dict['show_cb'], i+1, 0)

        tmp_dict['sim_combo'] = QComboBox(self)
        for name in self.parent.oengus.sim_names:
            tmp_dict['sim_combo'].addItem(name)

        cur_name = self.parent.oengus.sim_names[line['sim_num']]
        tmp_dict['sim_combo'].setCurrentText(cur_name)

        tmp_dict['sim_combo'].currentIndexChanged.connect(
            partial(self.sim_handler, i))
        self.lines_grid.addWidget(tmp_dict['sim_combo'], i+1, 1)

        # the ComboBox to choose the scalar

        cur_sim = self.parent.oengus.sims[line['sim_num']]
        scalars = cur_sim.get_available_quantities()['scalars']

        tmp_dict['quant_combo'] = QComboBox(self)
        for quant in scalars:
            tmp_dict['quant_combo'].addItem(quant)

        tmp_dict['quant_combo'].setCurrentText(line['scalar'])

        # self.update_quantity_menu(
        #    tmp_dict['quantity'], list(scalars), tmp_dict['quant_op'])

        # tmp_dict['quantity'].trace('w', partial(self.quantity_handler, i))

        self.lines_grid.addWidget(tmp_dict['quant_combo'], i+1, 2)

        for j, elm in enumerate(self.plot_opts):
            tmp_opt_dict = {}
            tmp_dict[elm] = tmp_opt_dict
            # entry_width = 20 if elm == 'label' else 7
            tmp_opt_dict['entry'] = QLineEdit(self)
            tmp_opt_dict['entry'].setText(f"{line['plot_args'][elm]}")
            self.lines_grid.addWidget(tmp_opt_dict['entry'], i+1, 3+j)


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
                self.subplot.save_axes_pos()
                self.subplot.refresh()
                self.subplot.load_axes_pos()
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
        self.subplot.save_axes_pos()
        self.subplot.draw()
        self.subplot.load_axes_pos()
        self.parent.oengus.canvas.draw()

    def text_callback(self):
        to_reload = False
        for elm in self.lims_helper:
            p_name = elm['val_param']
            entry = elm['entry']
            set_cb = elm['to_set_cb']
            try:
                # make sure the user types in a number
                user_num = float(entry.text())

                if abs(user_num - self.params[p_name]) > 1E-4:
                    self.params[p_name] = user_num
                    to_reload += set_cb.isChecked()

            except ValueError:
                # if they type in random stuff, just set it ot the param value
                entry.setText(str(self.params[p_name]))

        if to_reload:
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()
            self.parent.oengus.canvas.draw()

    def lim_handler(self, *args):
        for elm in self.lims_helper:
            param_name, cb = elm['param_name'], elm['to_set_cb']
            self.params[param_name] = cb.isChecked()
        self.subplot.save_axes_pos()
        self.subplot.refresh()
        self.subplot.load_axes_pos()
        self.parent.oengus.canvas.draw()

    def bool_handler(self, bool_name, *args):
        for elm in self.bool_opts:
            param_name, cb = elm['param_name'], elm['cb']
            self.params[param_name] = cb.isChecked()
        if self.params['yLog']:
            self.subplot.axes.set_yscale('log')
        else:
            self.subplot.axes.set_yscale('linear')
        self.subplot.legend.set_visible(self.params['show_legend'])
        self.subplot.time_line.set_visible(self.params['show_cur_time'])
        if bool_name == 'yLog':
            self.subplot.refresh()
        else:
            self.subplot.save_axes_pos()
            self.subplot.refresh()
            self.subplot.load_axes_pos()

        self.parent.oengus.canvas.draw()
