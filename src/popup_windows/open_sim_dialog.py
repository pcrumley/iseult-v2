import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os
import sys


class OpenSimDialog(Tk.Toplevel):
    def __init__(self, parent, title='Open Sim'):
        Tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent

        self.body = ttk.Frame(self)
        self.initial_focus = self.build_sim_table(self.body)
#        body.pack(fill=Tk.BOTH)#, expand=True)
        self.body.pack(fill=Tk.BOTH, anchor=Tk.CENTER, expand=1)

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

    def build_sim_table(self, master):
        # create dialog body.  return widget that should have
        # initial focus.
        ttk.Label(master, text="Sim #").grid(row=0, column=0)
        ttk.Label(master, text="name").grid(row=0, column=1)
        ttk.Label(master, text="directory").grid(row=0, column=2)
        self.labels = []
        self.names = []
        self.dirs = []
        for i in range(len(self.parent.oengus.sims)):
            self.labels.append(ttk.Label(master, text=f'{i}'))
            self.labels[-1].grid(row=i+1, column=0)
            e_name = ttk.Entry(master, width=17)
            e_name.insert(0, self.parent.oengus.sims[i].name)
            e_name.grid(row=i+1, column=1, sticky=Tk.E)
            self.names.append(e_name)

            e_dir = ttk.Entry(master, width=27)
            if self.parent.oengus.sims[i].outdir is not None:
                e_dir.insert(0, self.parent.oengus.sims[i].outdir)
            e_dir.grid(row=i+1, column=2, sticky=Tk.E)
            self.dirs.append(e_dir)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = ttk.Frame(self)
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

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

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
