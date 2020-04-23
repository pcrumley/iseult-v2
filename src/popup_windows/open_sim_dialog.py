import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os


class OpenSimDialog(Tk.Toplevel):

    def __init__(self, parent, title='Open Sim'):
        Tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent

        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
#        body.pack(fill=Tk.BOTH)#, expand=True)
        body.pack(fill=Tk.BOTH, anchor=Tk.CENTER, expand=1)

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
        ttk.Label(master, text="Sim #").grid(row=0, column=0)
        ttk.Label(master, text="name").grid(row=0, column=1)
        ttk.Label(master, text="directory").grid(row=0, column=2)
        ttk.Label(master, text="0").grid(row=1, column=0)
        ttk.Label(master, text="1").grid(row=2, column=0)
        ttk.Label(master, text="2").grid(row=3, column=0)
        ttk.Label(master, text="3").grid(row=4, column=0)
        self.names = []
        self.dirs = []
        for i in range(4):
            e_name = ttk.Entry(master, width=17)
            e_name.insert(i, self.parent.oengus.sims[i].name)
            e_name.grid(row=i+1, column=1, sticky=Tk.E)
            self.names.append(e_name)

            e_dir = ttk.Entry(master, width=27)
            if self.parent.oengus.sims[i].outdir is not None:
                e_dir.insert(0, self.parent.oengus.sims[0].outdir)
            e_dir.grid(row=i+1, column=2, sticky=Tk.E)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(
            box, text="Open", width=10,
            command=self.ok, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics

    def ok(self, event=None):
        # if not self.validate():
        #    self.initial_focus.focus_set() # put focus back
        #    return

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

    def apply(self):
        # First change all the names.
        for i, name in enumerate(self.names):
            self.parent.oengus.sims[i].name = str(name.get())
        for i, dir in enumerate(self.dirs):
            if self.parent.oengus.sims[i].outdir != str(dir.get()):
                self.parent.oengus.sims[i].outdir = str(dir.get())
        self.parent.oengus.draw_output()
