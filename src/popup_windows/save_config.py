import os
import yaml
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit,
                             QLabel, QMessageBox)

def save_iseult_cfg(oengus, window_size, cfgfile, cfgname):
    # When adding sections or items, add them in the reverse order of
    # how you want them to be displayed in the actual file.
    # In addition, please note that using RawConfigParser's and the raw
    # mode of ConfigParser's respective set functions, you can assign
    # non-string values to keys internally, but will receive an error
    # when attempting to write to a file or when you get it in non-raw
    # mode. SafeConfigParser does not allow such assignments to take place.

    cfgDict = {}

    cfgDict['general'] = {'ConfigName': cfgname}

    # Update the 'WindowSize' attribute to the current window size
    oengus.MainParamDict['WindowSize'] = window_size

    # Get figsize and dpi
    fig_size = oengus.figure.get_size_inches()
    oengus.MainParamDict['FigSize'] = [float(elm) for elm in fig_size]
    oengus.MainParamDict['dpi'] = oengus.figure.dpi
    if oengus.MainParamDict['HorizontalCbars']:
        subplot_cfg = oengus.MainParamDict['HSubPlotParams']
    else:
        subplot_cfg = oengus.MainParamDict['VSubPlotParams']
    try:
        subplot_params = oengus.figure.subplotpars
        for key in subplot_cfg.keys():
            subplot_cfg[key] = float(getattr(subplot_params, key))
    except KeyError:
        pass
    for i in range(oengus.MainParamDict['NumOfRows']):
        for j in range(oengus.MainParamDict['NumOfCols']):
            tmp_str = f"Chart{i}_{j}"
            subplot = oengus.SubPlotList[i][j]
            cfgDict[tmp_str] = subplot.param_dict
            cfgDict[tmp_str]['chart_type'] = subplot.chart_type
    cfgDict['MainParamDict'] = oengus.MainParamDict

    # Writing our configuration file to 'example.cfg'
    with open(cfgfile, 'w') as cfgFile:
        cfgFile.write(yaml.safe_dump(cfgDict))


class SaveDialog(QDialog):
    def __init__(self, parent, title=None):
        super().__init__(parent)
        self.parent = parent
        if title:
            self.setWindowTitle(title)
        self.init_ui()
        self.exec_()

    def init_ui(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.reject)

        self.name_QLineEdit = QLineEdit(self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Name of View:"))
        self.layout.addWidget(self.name_QLineEdit)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    # standard button semantics
    def ok(self, event=None):
        if self.validate():
            self.apply()
            self.accept()

    # command hooks
    def validate(self):
        ''' Check to make sure the config file doesn't already exist'''
        Name = str(self.name_QLineEdit.text()).strip()
        ok_special_chars = ['.', '_', ' ']
        for char in ok_special_chars:
            Name = Name.replace(char, '')
        if Name == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bad input")
            msg.setInformativeText("Field cannot be empty, please try again")
            msg.exec_()
        elif not Name.isalnum():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bad input")
            msg.setInformativeText(
                "Name must be alpha numeric (whitespace, '_', or '.' are ok).")
            msg.exec_()
        else:
            return True

    def apply(self):
        ''' Save the config file'''
        w_size = f'{self.parent.width()}x{self.parent.height()}'
        cfg_dir = os.path.join(self.parent.IseultDir, '.iseult_configs')
        new_cfg_file = str(self.name_QLineEdit.text()).strip().replace(' ', '_') + '.yml'
        new_cfg_file = os.path.join(cfg_dir, new_cfg_file)
        save_iseult_cfg(
            self.parent.oengus, w_size,
            new_cfg_file, str(self.name_QLineEdit.text()).strip())
