


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import json
# from PyQt5.QtCore import *
import sys
import pandas as pd
from eeg_modules import DataOperations


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.f = QFont("Arial", 15)
        self.vbox = QVBoxLayout()
        self.widget = QWidget()
        self.data = pd.DataFrame()
        self.windowed_data = pd.DataFrame()
        self.baselined_data = pd.DataFrame()
        self.fill_empty_cells_data = pd.DataFrame()
        self.operations_menu = None
        self.config_data = None
        self.filename = ()
        self.column_name = []
        self.csv_file_details = []
        self.area = QScrollArea()
        self.time_duration = None
        self.mol = None
        self.dialog_box = None
        self.init_ui()

    def read_config_data(self):
        with open('config.json', 'r') as f:
            self.config_data = json.load(f)

    def write_config_data(self, file_path):
        self.config_data["recently opened file path"] = file_path
        print(self.config_data["recently opened file path"])
        with open('config.json', 'w') as f:
            json.dump(self.config_data, f, indent=3)

    def getDetails(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data.sort_values(by="TimeStamp", ascending=True, inplace=True)
        self.column_name = self.data.columns.values.tolist()
        self.data['TimeStamp'] = pd.to_datetime(self.data['TimeStamp'])
        self.time_duration = self.data['TimeStamp'].max() - self.data['TimeStamp'].min()
        self.time_duration = self.time_duration.components
        self.data = self.data.filter(regex="Time|RAW|Element")
        lis = []
        for j in self.column_name:
            if "RAW" in j:
                lis.append({
                    "Column Name": j,
                    "Mean": round(self.data[j].mean(), 4),
                    "Standard Deviation": round(self.data[j].std(), 4),
                    "Maximum": round(self.data[j].max(), 4),
                    "Minimum": round(self.data[j].min(), 4),
                    "Blank Values": len(self.data.index) - self.data[j].count()
                })
        self.csv_file_details.append({
            "File Name": self.filename[0].split("/")[-1],
            "File Location": self.filename[0],
            "Time Duration": str(self.time_duration[1]) + " hour(s) " + str(
                self.time_duration[2]) + " minute(s) and " + str(
                self.time_duration[3]) + "." + str(self.time_duration[4]) + " seconds",
            "Number of rows": len(self.data.index),
            "Number of columns": len(self.column_name),
            "Data points": int(
                len(self.data.index) / (
                        self.time_duration[1] * 60 * 60 + self.time_duration[2] * 60 + self.time_duration[3])),
            "Column Details": lis
        })
        for i in self.csv_file_details:
            label_file_name = QLabel("File Name : " + str(i["File Name"]))
            label_file_location = QLabel("File Location : " + str(i["File Location"]))
            label_time_duration = QLabel("Time Duration : " + str(i["Time Duration"]))
            label_number_of_rows = QLabel("Number of Rows : " + str(i["Number of rows"]))
            label_number_of_columns = QLabel("Number of Columns : " + str(i["Number of columns"]))
            label_data_points = QLabel("Data Points per second(approx.) : " + str(i["Data points"]))

            label_file_name.setFont(self.f)
            label_file_location.setFont(self.f)
            label_time_duration.setFont(self.f)
            label_number_of_rows.setFont(self.f)
            label_number_of_columns.setFont(self.f)
            label_data_points.setFont(self.f)

            self.vbox.addWidget(label_file_name)
            self.vbox.addWidget(label_file_location)
            self.vbox.addWidget(label_time_duration)
            self.vbox.addWidget(label_number_of_rows)
            self.vbox.addWidget(label_number_of_columns)
            self.vbox.addWidget(label_data_points)
            self.vbox.addSpacing(10)
            for j in i["Column Details"]:
                self.vbox.addSpacing(1)
                name = QLabel("Column name ; " + str(j["Column Name"]))
                name.setFont(self.f)
                min = QLabel("Minimum value ; " + str(j["Minimum"]))
                max = QLabel("Maximum value ; " + str(j["Maximum"]))
                mean = QLabel("Mean  ; " + str(j["Mean"]))
                SD = QLabel("Standard Deviation ; " + str(j["Standard Deviation"]))
                blank = QLabel("Blank value ; " + str(j["Blank Values"]))
                self.vbox.addWidget(name)
                self.vbox.addWidget(min)
                self.vbox.addWidget(max)
                self.vbox.addWidget(mean)
                self.vbox.addWidget(SD)
                self.vbox.addWidget(blank)
                self.vbox.addSpacing(15)

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.filename = QFileDialog.getOpenFileName(self, "File Explorer",
                                                    self.config_data["recently opened file path"], "csv(*.csv)")
        if self.filename[0] != '':
            if self.config_data["recently opened file path"] != self.filename[0]:
                self.write_config_data(self.filename[0])
            self.getDetails(self.filename[0])

    def settings(self):
        print("settings file will be opened")

    def windowing(self):
        if not self.data.empty:
            item = [str(x) for x in range(1, 11)]
            value, ok = QInputDialog.getItem(self, "Input Dialog", "Select Window Size", item, 0, False)
            if ok:
                self.windowed_data = do.windowing(int(value), self.time_duration, self.data)
                self.message_box('Operation Completed', 1, 'Windowing operation has been completed successfully')
                self.save_message_box(0)
            else:
                self.message_box('Operation Failed', 3, 'Window size not selected')
        else:
            self.message_box('Operation Failed', 3, 'File not selected for performing windowing operation')

    def baseline(self):
        if not self.data.empty:
            filename = QFileDialog.getOpenFileName(self, "File Explorer", "/home/winston/Desktop", "csv(*.csv)")
            if filename[0] != '':
                self.baselined_data = do.baseline(filename[0], self.data)
                self.save_message_box(1)
        else:
            self.message_box('Operation Failed', 3, 'File not selected for baseline removal')

    def fill_empty_cells(self, ):
        if not self.data.empty:
            self.fill_empty_cells_data = do.fill_empty_cells(self.data)
            print(self.fill_empty_cells_data)
            self.save_message_box(2)
        else:
            self.message_box('Operation Failed', 3, 'File not selected for filling empty cells')

    def message_box(self, status, code, message):
        self.dialog_box = QMessageBox()
        if code == 0:
            self.dialog_box.setIcon(QMessageBox.Question)
        elif code == 1:
            self.dialog_box.setIcon(QMessageBox.Information)
        elif code == 2:
            self.dialog_box.setIcon(QMessageBox.Warning)
        else:
            self.dialog_box.setIcon(QMessageBox.Critical)
        self.dialog_box.setWindowTitle(status)
        self.dialog_box.setText(message)
        self.dialog_box.exec_()

    def save_message_box(self, operation):
        self.dialog_box = QMessageBox()
        self.dialog_box.setIcon(QMessageBox.Question)
        self.dialog_box.setWindowTitle("Save")
        self.dialog_box.setText('Would you like to save output data?')
        self.dialog_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = self.dialog_box.exec_()
        if result == 16384:
            options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
            filename = QFileDialog.getSaveFileName(self, "Save File", filter="csv", options=options)
            if filename[0] != '':
                if operation == 0:
                    self.windowed_data.to_csv(path_or_buf=filename[0] + '.' + filename[1], index=None)
                    self.message_box('Successful', 1, "File saved successfully")
                elif operation == 1:
                    self.baselined_data.to_csv(path_or_buf=filename[0] + '.' + filename[1], index=None)
                    self.message_box('Successful', 1, "File saved successfully")
                elif operation == 2:
                    self.fill_empty_cells_data.to_csv(path_or_buf=filename[0] + '.' + filename[1], index=None)
                    self.message_box('Successful', 1, "File saved successfully")
                else:
                    pass

            else:
                self.message_box('Warning', 2, "The result of operation has not been saved")
        else:
            self.message_box('Warning', 2, "The result of operation has not been saved")

    def init_ui(self):
        self.setWindowTitle("For-EEG-Preprocessing")
        self.read_config_data()
        menubar = self.menuBar()

        # Adding menu objects to menubar
        filemenu = menubar.addMenu("File")
        self.operations_menu = menubar.addMenu("Operations")
        log_menu = menubar.addMenu("Log")
        help_menu = menubar.addMenu("Help")

        # Adding actions to filemenu

        openFile = QAction("Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Load an existing csv file')
        openFile.triggered.connect(self.open_file)
        filemenu.addAction(openFile)

        recent = filemenu.addMenu("Recent")

        setting = QAction("Settings", self)
        setting.setShortcut("Ctrl+Alt+S")
        setting.triggered.connect(self.settings)
        filemenu.addAction(setting)

        exit_file = QAction("Exit", self)
        exit_file.setShortcut("Ctrl+Q")
        exit_file.setStatusTip('Exit Application')
        exit_file.triggered.connect(self.close)
        filemenu.addAction(exit_file)

        # Adding actions to Operations Menu

        fill_empty_cells = QAction("Fill Empty Cells", self)
        fill_empty_cells.setShortcut("Ctrl+E")
        fill_empty_cells.triggered.connect(self.fill_empty_cells)
        self.operations_menu.addAction(fill_empty_cells)

        windowing = QAction("Windowing", self)
        windowing.setShortcut("Ctrl+W")
        windowing.setStatusTip("Performs windowing operation on the selected data")
        windowing.triggered.connect(self.windowing)
        self.operations_menu.addAction(windowing)

        baseline = QAction("Baseline Removal", self)
        baseline.setShortcut("Ctrl+B")
        baseline.triggered.connect(self.baseline)
        self.operations_menu.addAction(baseline)

        segmentation = QAction("Segmentation", self)
        interpolation = QAction("Interpolation", self)
        extrapolation = QAction("Extrapolation", self)

        self.operations_menu.addAction(segmentation)
        self.operations_menu.addAction(interpolation)
        self.operations_menu.addAction(extrapolation)

        self.area.setStyleSheet("background-color:#474444;color:#ffffff")
        self.setCentralWidget(self.area)
        self.vbox.setContentsMargins(100, 50, 50, 0)
        self.area.setLayout(self.vbox)
        self.setStyleSheet(
            "QMenuBar {font-size: 15px;background-color:#676565;padding:3px 4px;} QMenuBar::item{"
            "color:#ffffff;background-color:#676565;} QMenu{font-size: 15px;background-color:#676565;padding:3px "
            "4px;color:#ffffff} QMenu::item::selected{color:#ffffff;background-color:#3a9fbf;}")
        self.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    do = DataOperations()
    sys.exit(app.exec_())
