import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os

class OpenSimDialog(Tk.Toplevel):

    def __init__(self, parent, title = 'Open Sim'):
        Tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent

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
        ttk.Label(master, text="Sim #").grid(row=0, column = 0)
        ttk.Label(master, text="name").grid(row=0, column = 1)
        ttk.Label(master, text="directory").grid(row=0, column = 2)
        ttk.Label(master, text="0").grid(row=1, column = 0)
        ttk.Label(master, text="1").grid(row=2, column = 0)
        ttk.Label(master, text="2").grid(row=3, column = 0)
        ttk.Label(master, text="3").grid(row=4, column = 0)

        self.e0name = ttk.Entry(master, width=17)
        self.e0name.insert(0,self.parent.oengus.sims[0].name)
        self.e0name.grid(row=1, column=1, sticky = Tk.E)
        self.e0dir = ttk.Entry(master, width=27)
        if self.parent.oengus.sims[0].outdir is not None:
            self.e0dir.insert(0,self.parent.oengus.sims[0].outdir)
        self.e0dir.grid(row=1, column=2, sticky = Tk.E)

        self.e1name = ttk.Entry(master, width=17)
        self.e1name.insert(0,self.parent.oengus.sims[1].name)
        self.e1name.grid(row=2, column=1, sticky = Tk.E)

        self.e1dir = ttk.Entry(master, width=27)
        if self.parent.oengus.sims[1].outdir is not None:
            self.e1dir.insert(0,self.parent.oengus.sims[1].outdir)
        self.e1dir.grid(row=2, column=2, sticky = Tk.E)

        self.e2name = ttk.Entry(master, width=17)
        self.e2name.insert(0,self.parent.oengus.sims[2].name)
        self.e2name.grid(row=3, column=1, sticky = Tk.E)
        self.e2dir = ttk.Entry(master, width=27)
        if self.parent.oengus.sims[2].outdir is not None:
            self.e2dir.insert(0,self.parent.oengus.sims[2].outdir)
        self.e2dir.grid(row=3, column=2, sticky = Tk.E)

        self.e3name = ttk.Entry(master, width=17)
        self.e3name.insert(0,self.parent.oengus.sims[3].name)
        self.e3name.grid(row=4, column=1, sticky = Tk.E)

        self.e3dir = ttk.Entry(master, width=27)
        if self.parent.oengus.sims[3].outdir is not None:
            self.e3dir.insert(0,self.parent.oengus.sims[3].outdir)
        #self.e3dir.insert(0,self.parent.oengus.sims[3].outdir)
        self.e3dir.grid(row=4, column=2, sticky = Tk.E)

        """
        ttk.Label(master, text="First Frame:").grid(row=1)
        self.e2 = ttk.Entry(master, width=17)
        self.e2.grid(row=1, column=1, sticky = Tk.E)

        ttk.Label(master, text="Last Frame (-1 for final frame):").grid(row=2)
        self.e3 = ttk.Entry(master, width=17)
        self.e3.grid(row=2, column=1, sticky = Tk.E)

        ttk.Label(master, text="Step Size:").grid(row=3)
        self.e4 = ttk.Entry(master, width=17)
        self.e4.grid(row=3, column=1, sticky = Tk.E)

        ttk.Label(master, text="Frames Per Second:").grid(row=4)
        self.e5 = ttk.Entry(master, width=17)
        self.e5.grid(row=4, column=1, sticky = Tk.E)
        """
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(box, text="Open", width=10, command=self.ok, default=Tk.ACTIVE)
        w.pack(side=Tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=Tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        #if not self.validate():
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

    def validate(self):
        ''' Check to make sure the Movie will work'''
        self.Name = str(self.e1.get())
        try:
            self.StartFrame = int(self.e2.get())
        except ValueError:
            self.StartFrame = ''
        try:
            self.EndFrame = int(self.e3.get())
        except ValueError:
            self.EndFrame = ''
        try:
            self.Step = int(self.e4.get())
        except ValueError:
            self.Step = ''
        try:
            self.FPS = int(self.e5.get())
        except ValueError:
            self.FPS = ''

        if self.Name != '':
            self.Name = str(self.e1.get()).strip().replace(' ', '_') +'.mov'
        if self.StartFrame <0:
            self.StartFrame = 0#len(self.parent.PathDict['Param'])+self.StartFrame + 1
        if self.EndFrame <0:
            self.EndFrame = 0#len(self.parent.PathDict['Param'])+self.EndFrame + 1

        if self.Name == '':
            messagebox.showwarning(
                "Bad input",
                "Field must contain a name, please try again"
            )

        elif self.StartFrame == '':
            messagebox.showwarning(
                "Bad input",
                "StartFrame must contain an int, please try again"
            )
        elif self.EndFrame == '':
            messagebox.showwarning(
                "Bad input",
                "EndFrame must contain an int, please try again"
            )
        elif self.StartFrame == 0:
            messagebox.showwarning(
                "Bad input",
                "Starting frame cannot be zero"
            )
        elif self.EndFrame == 0:
            messagebox.showwarning(
                "Bad input",
                "Ending frame cannot be zero"
            )


        elif self.Step == '':
            messagebox.showwarning(
                "Bad input",
                "Step must contain an int, please try again"
            )
        elif self.Step <=0:
            messagebox.showwarning(
                "Bad input",
                "Step must be an integer >0, please try again"
            )
        elif self.FPS == '':
            messagebox.showwarning(
                "Bad input",
                "FPS must contain an int >0, please try again"
            )
        elif self.FPS <= 0:
            messagebox.showwarning(
                "Bad input",
                "FPS must contain an int >0, please try again"
            )
        else:
            return 1 # override

    def apply(self):
        # First change all the names.
        for i, name in enumerate([self.e0name, self.e1name, self.e2name, self.e3name]):
            self.parent.oengus.sims[i].name = str(name.get())
        for i, dir in enumerate([self.e0dir, self.e1dir, self.e2dir, self.e3dir]):
            if self.parent.oengus.sims[i].outdir != str(dir.get()):
                for sim_type, cfg_path in self.parent.oengus.avail_sim_types.items():
                    self.parent.oengus.sims[i].cfg_file = cfg_path
                    self.parent.oengus.sims[i].outdir = str(dir.get())
                    if len(self.parent.oengus.sims[i]) == 0:
                        self.parent.oengus.sims[i].outdir = os.path.join(self.parent.oengus.sims[i].outdir, 'output')
                    if len(self.parent.oengus.sims[i]) != 0:
                        break
        self.parenet.oengus.draw_output()
