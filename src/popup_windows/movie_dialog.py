import tkinter as Tk
from tkinter import ttk, messagebox
import os

class MovieDialog(Tk.Toplevel):

    def __init__(self, parent, oengus, title=None):

        Tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.oengus = oengus
        self.result = None

        cur_sim = self.oengus.sims[self.oengus.cur_sim]
        body = ttk.Frame(self)
        self.initial_focus = self.body(
            body, directory=os.path.abspath(
                os.path.join(cur_sim.outdir, '../')
            ))
#        body.pack(fill=Tk.BOTH)#, expand=True)
        body.pack(fill=Tk.BOTH, anchor=Tk.CENTER, expand=1)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self, master, directory='./'):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        master.grid_columnconfigure(1, weight=1)
        ttk.Label(master, text="Name of Movie:").grid(row=0)
        self.e1 = ttk.Entry(master, width=17)
        self.e1.grid(row=0, column=1, sticky=Tk.E + Tk.W)

        ttk.Label(master, text="First Frame:").grid(row=1)
        self.e2 = ttk.Entry(master, width=17)
        self.e2.grid(row=1, column=1, sticky=Tk.E + Tk.W)

        ttk.Label(master, text="Last Frame (-1 for final frame):").grid(row=2)
        self.e3 = ttk.Entry(master, width=17)
        self.e3.grid(row=2, column=1, sticky=Tk.E + Tk.W)

        ttk.Label(master, text="Step Size:").grid(row=3)
        self.e4 = ttk.Entry(master, width=17)
        self.e4.grid(row=3, column=1, sticky=Tk.E + Tk.W)

        ttk.Label(master, text="Frames Per Second:").grid(row=4)
        self.e5 = ttk.Entry(master, width=17)
        self.e5.grid(row=4, column=1, sticky=Tk.E + Tk.W)

        ttk.Label(master, text="Movie Directory:").grid(row=5)
        self.e6 = ttk.Entry(master, width=30)
        self.e6.delete(0, Tk.END)
        self.e6.insert(0, directory)
        self.e6.grid(row=5, column=1, sticky=Tk.E + Tk.W)

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = ttk.Frame(self)

        w = ttk.Button(
            box, text="Save", width=10,
            command=self.ok, default=Tk.ACTIVE)
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
            self.initial_focus.focus_set()  # put focus back
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
        ''' Check to make sure the Movie will work'''
        cur_sim = self.oengus.sims[self.oengus.cur_sim]
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
        self.outdir = str(self.e6.get().strip())

        if self.Name != '':
            self.Name = str(self.e1.get()).strip().replace(' ', '_') + '.mov'

        if self.StartFrame < 0:
            self.StartFrame += len(cur_sim) + 1

        if self.EndFrame < 0:
            self.EndFrame += len(cur_sim) + 1

        bad = False
        if self.Name == '':
            messagebox.showwarning(
                "Bad input",
                "Field must contain a name, please try again"
            )
            bad = True
        if not os.path.isdir(self.outdir):
            messagebox.showwarning(
                "Bad input",
                f"{self.outdir} is not a directory"
            )
            bad = True

        filepath = os.path.join(self.outdir, self.Name)
        try:
            filehandle = open(filepath, 'w')
            filehandle.close()
            if os.path.exists(filepath):
                os.remove(filepath)

        except IOError:
            messagebox.showwarning(
                "Bad input",
                f"You do not have write access to {self.outdir}"
            )
            bad = True

        if not bad:
            if self.StartFrame == '':
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
            elif self.Step <= 0:
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
                return 1

    def apply(self):
        ''' Save the Movie'''
        self.oengus.make_movie(
            fname=self.Name,
            start=self.StartFrame,
            stop=self.EndFrame,
            step=self.Step,
            FPS=self.FPS,
            outdir=self.outdir)
