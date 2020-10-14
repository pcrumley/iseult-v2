from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLineEdit,
                             QLabel, QMessageBox, QGridLayout)
import os


class MovieDialog(QDialog):
    def __init__(self, parent, oengus, title=None):
        super().__init__(parent)
        self.parent = parent
        self.oengus = oengus
        if title:
            self.setWindowTitle(title)
        self.init_ui()
        self.exec_()

    def init_ui(self):

        self.labels = [
            "Name of Movie:",
            "First Frame:",
            "Last Frame (-1 for final frame):",
            "Step Size:",
            "Frames Per Second:",
            "Movie Directory:"]
        self.labels = [QLabel(label) for label in self.labels]
        self.movie_opts_edits = [QLineEdit(self) for _ in self.labels]

        # get movie directory:
        cur_sim = self.oengus.sims[self.oengus.cur_sim]
        movie_dir = os.path.abspath(os.path.join(cur_sim.outdir, '../'))

        self.movie_opts_edits[-1].setText(movie_dir)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        for i, (label, line_edit) in enumerate(zip(self.labels,
                                                   self.movie_opts_edits)):
            self.layout.addWidget(label, i, 0)
            self.layout.addWidget(line_edit, i, 1)

        self.layout.addWidget(self.buttonBox, len(self.labels), 0, 1, 2)

        self.setLayout(self.layout)

    # standard button semantics
    def ok(self, event=None):
        if self.validate():
            self.apply()
            self.accept()

    def validate(self):
        ''' Check to make sure the Movie will work'''
        cur_sim = self.oengus.sims[self.oengus.cur_sim]
        self.Name = self.movie_opts_edits[0].text()
        try:
            self.StartFrame = int(self.movie_opts_edits[1].text())

        except ValueError:
            self.StartFrame = ''
        try:
            self.EndFrame = int(self.movie_opts_edits[2].text())
        except ValueError:
            self.EndFrame = ''
        try:
            self.Step = int(self.movie_opts_edits[3].text())
        except ValueError:
            self.Step = ''
        try:
            self.FPS = int(self.movie_opts_edits[4].text())
        except ValueError:
            self.FPS = ''
        self.outdir = str(self.movie_opts_edits[5].text().strip())

        if self.Name != '':
            self.Name = self.Name.strip().replace(' ', '_')
            try:
                if self.Name[-4:] != '.mov':
                    self.Name = self.Name + '.mov'
            except IndexError:
                pass

        if self.StartFrame < 0:
            self.StartFrame += len(cur_sim) + 1

        if self.EndFrame < 0:
            self.EndFrame += len(cur_sim) + 1

        bad = False
        if self.Name == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bad input")
            msg.setInformativeText(
                "Field must contain a name, please try again")
            msg.exec_()
            bad = True

        if not bad and not os.path.isdir(self.outdir):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bad input")
            msg.setInformativeText(f"{self.outdir} is not a directory")
            msg.exec_()
            bad = True

        if not bad:
            filepath = os.path.join(self.outdir, self.Name)
            try:
                filehandle = open(filepath, 'w')
                filehandle.close()
                if os.path.exists(filepath):
                    os.remove(filepath)

            except IOError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    f"You do not have write access to {self.outdir}")
                bad = True

        if not bad:
            if self.StartFrame == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "StartFrame must contain an int, please try again"
                )
            elif self.EndFrame == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "EndFrame must contain an int, please try again"
                )
            elif self.StartFrame == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "Starting frame cannot be zero"
                )
            elif self.EndFrame == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "Ending frame cannot be zero"
                )
            elif self.Step == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "Step must contain an int, please try again"
                )
            elif self.Step <= 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "Step must be an integer >0, please try again"
                )
            elif self.FPS == '':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "FPS must contain an int >0, please try again"
                )
            elif self.FPS <= 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    "FPS must contain an int >0, please try again"
                )
            else:
                return True

    def apply(self):
        ''' Save the Movie'''
        self.oengus.make_movie(
            fname=self.Name,
            start=self.StartFrame,
            stop=self.EndFrame,
            step=self.Step,
            FPS=self.FPS,
            outdir=self.outdir)
