from functools import partial
import os
import sys
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QGridLayout, QFileDialog,
                             QVBoxLayout, QHBoxLayout)


class OpenSimDialog(QDialog):
    def __init__(self, parent, title='Open Sim'):
        super().__init__(parent)
        self.parent = parent
        if title:
            self.setWindowTitle(title)

        self.init_ui()
        self.exec_()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        sim_table = QGridLayout()
        self.build_sim_table(sim_table)
        self.layout.addLayout(sim_table)

        add_remove_btn_box = QHBoxLayout()
        add_remove_btn_box.setSpacing(0)
        # Add btn
        add_btn = QPushButton(self)
        add_btn.setText("Add Sim")
        add_btn.setMaximumWidth(100)
        add_btn.setMinimumWidth(100)
        add_btn.clicked.connect(partial(self.add, sim_table))
        add_remove_btn_box.addWidget(add_btn)

        # Remove Sim
        rm_btn = QPushButton(self)
        rm_btn.setText("Remove Sim")
        rm_btn.setMaximumWidth(100)
        rm_btn.setMinimumWidth(100)
        rm_btn.clicked.connect(self.remove)
        add_remove_btn_box.addWidget(rm_btn)

        self.layout.addLayout(add_remove_btn_box)
        # Cancel & OK buttons (actually... cancel doesn't work. Let's rm it)
        QBtn = QDialogButtonBox.Ok #| QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def build_sim_table(self, grid_layout):
        # create dialog body.  return widget that should have
        # initial focus.
        grid_layout.addWidget(QLabel('Sim #'), 0, 0)
        grid_layout.addWidget(QLabel('name'), 0, 1)
        grid_layout.addWidget(QLabel('directory'), 0, 2)

        self.labels = []
        self.names = []
        self.dirs = []
        self.buttons = []

        for i in range(len(self.parent.oengus.sims)):
            self.labels.append(QLabel(f'{i}'))
            grid_layout.addWidget(self.labels[-1], i+1, 0)
            edit_name = QLineEdit(self)
            edit_name.setText(self.parent.oengus.sims[i].name)
            edit_name.setMaximumWidth(175)
            edit_name.setMinimumWidth(20)

            grid_layout.addWidget(edit_name, i+1, 1)
            self.names.append(edit_name)

            edit_dir = QLineEdit(self)
            edit_dir.setMinimumWidth(175)

            if self.parent.oengus.sims[i].outdir is not None:
                edit_dir.setText(self.parent.oengus.sims[i].outdir)
            grid_layout.addWidget(edit_dir, i+1, 2)
            self.dirs.append(edit_dir)

            open_dir_btn = QPushButton(self)
            open_dir_btn.setText('Open Dir')
            open_dir_btn.clicked.connect(partial(self.open_dir, i))
            grid_layout.addWidget(open_dir_btn, i+1, 3)
            self.buttons.append(open_dir_btn)

    def open_dir(self, i, *args):
        open_dir_dialog = QFileDialog(self)
        open_dir_dialog.setDirectory(os.curdir)
        open_dir_dialog.setFileMode(QFileDialog.Directory)
        if open_dir_dialog.exec_():
            dirNames = open_dir_dialog.selectedFiles()
            if len(dirNames) >0:
                self.dirs[i].setText(dirNames[0])

    # standard button semantics
    def add(self, grid_layout):
        n = len(self.dirs)
        self.parent.oengus.add_sim(f'sim{n}')

        self.labels.append(QLabel(f'{n}'))
        grid_layout.addWidget(self.labels[-1], n+1, 0)
        edit_name = QLineEdit(self)
        edit_name.setText(self.parent.oengus.sims[n].name)
        edit_name.setMaximumWidth(175)
        edit_name.setMinimumWidth(20)

        grid_layout.addWidget(edit_name, n+1, 1)
        self.names.append(edit_name)

        edit_dir = QLineEdit(self)
        edit_dir.setMinimumWidth(175)

        if self.parent.oengus.sims[n].outdir is not None:
            edit_dir.setText(self.parent.oengus.sims[n].outdir)
        grid_layout.addWidget(edit_dir, n+1, 2)
        self.dirs.append(edit_dir)

        open_dir_btn = QPushButton(self)
        open_dir_btn.setText('Open Dir')
        open_dir_btn.clicked.connect(partial(self.open_dir, n))
        grid_layout.addWidget(open_dir_btn, n+1, 3)
        self.buttons.append(open_dir_btn)

    def remove(self, event=None):
        if self.parent.oengus.pop_sim() is not None:
            self.labels[-1].deleteLater()
            self.labels.pop()
            self.names[-1].deleteLater()
            self.names.pop()
            self.dirs[-1].deleteLater()
            self.dirs.pop()
            self.buttons[-1].deleteLater()
            self.buttons.pop()

    def ok(self, event=None):
        if self.validate():
            self.apply()
            self.accept()

    def validate(self):
        ''' Check to make sure the directories are ok '''
        # First change all the names.
        bad = False
        for dir in self.dirs:
            dirname = str(dir.text())
            if not os.path.isdir(dirname):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bad input")
                msg.setInformativeText(
                    f"{dirname} is not a directory")
                msg.exec_()
                bad = True
                break
        return not bad

    def apply(self):
        # First change all the names.
        for i, name in enumerate(self.names):
            self.parent.oengus.sims[i].name = name.text()
        for i, dir in enumerate(self.dirs):
            if self.parent.oengus.sims[i].outdir != dir.text():
                self.parent.oengus.sims[i].outdir = dir.text()
        self.parent.update_all_sim_lists()
        self.parent.oengus.draw_output()
