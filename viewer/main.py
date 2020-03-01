#!/usr/bin/env python3

from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
import sys
import os
from viewer.editor import TextEditor
from viewer.CompilationDialog import CompilatonDialog

clear = lambda: os.system("clear")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.form = TextEditor()
        self.setCentralWidget(self.form)
        self.windows = []
        self.windows.append(self)
        clear()
        self.name = None
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 1024, 720)
        self.setWindowTitle("Brick")
        self.setWindowIcon(QIcon(QtGui.QPixmap("../images/window_icon.png")))
        self.setStyleSheet("QMainWindow { background-color: #3d4345 }")

        self.status_label = QtWidgets.QLabel()
        self.status_label.setStyleSheet("QLabel { color: #A9B7C6}")
        self.statusBar().addWidget(self.status_label)

        self.font_sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.font_sl.setStyleSheet("QSlider { color: #A9B7C6}")
        self.font_sl.setMinimum(8)
        self.font_sl.setMaximum(24)
        self.font_sl.setSingleStep(2)
        self.font_sl.setValue(10)
        self.font_sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.font_sl.setTickInterval(2)
        self.font_sl.setFixedWidth(200)

        self.font_label = QtWidgets.QLabel("Font Size: ")
        self.font_label.setStyleSheet("QLabel { color: #A9B7C6}")

        self.c_label = QtWidgets.QLabel("C: ")
        self.c_label.setStyleSheet("QLabel { color: #A9B7C6}")

        self.compile_btn = QtWidgets.QPushButton("Compile")
        self.compile_btn.setShortcut("Ctrl+C")
        self.compile_btn.setStyleSheet("QPushButton { background-color: #2B2B2B ; color: #A9B7C6}")

        self.build_btn = QtWidgets.QPushButton("Build")
        self.build_btn.setStyleSheet("QPushButton { background-color: #2B2B2B ; color: #A9B7C6}")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.setStyleSheet("QPushButton { background-color: #2B2B2B ; color: #A9B7C6}")
        debug_btn = QtWidgets.QPushButton("Debug")
        debug_btn.setStyleSheet("QPushButton { background-color: #2B2B2B ; color: #A9B7C6}")
        debug_btn.setIcon(QtGui.QIcon(QtGui.QPixmap("../images/debug.png")))

        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar.setStyleSheet("QToolBar { background-color: #3d4345 }")
        self.tool_bar.addWidget(self.font_label)
        self.tool_bar.addWidget(self.font_sl)
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(self.c_label)
        self.tool_bar.addWidget(self.compile_btn)
        self.tool_bar.addWidget(self.build_btn)
        self.tool_bar.addWidget(self.clear_btn)
        self.tool_bar.addSeparator()
        self.tool_bar.addSeparator()
        self.tool_bar.addWidget(debug_btn)
        self.addToolBar(self.tool_bar)

        self.font_sl.valueChanged.connect(lambda: self.change_font(self.font_sl.value()))
        self.compile_btn.clicked.connect(self.compile_c)
        self.build_btn.clicked.connect(self.build_c)
        self.clear_btn.clicked.connect(self.clear_c)
        debug_btn.clicked.connect(self.debug_c)

        self.bar = self.menuBar()
        self.bar.setStyleSheet("QMenuBar { background-color: #3d4345 ; color: #A9B7C6}")
        self.file = self.bar.addMenu("File")
        self.file.setStyleSheet("QMenu { background-color: #3d4345 ; color: #A9B7C6}")
        self.edit = self.bar.addMenu("Edit")
        self.edit.setStyleSheet("QMenu { background-color: #3d4345 ; color: #A9B7C6}")

        self.new = QtWidgets.QAction("New")
        self.new.setShortcut("Ctrl+n")
        self.save = QtWidgets.QAction("Save")
        self.save.setShortcut("Ctrl+s")
        self.open = QtWidgets.QAction("Open")
        self.open.setShortcut("Ctrl+o")
        self.file.addAction(self.new)
        self.file.addAction(self.save)
        self.file.addAction(self.open)
        self.save.triggered.connect(self.form.save_file)
        self.open.triggered.connect(self.form.open_file)
        self.new.triggered.connect(self.new_file)

        self.show()

    def change_font(self, value):
        self.form.set_font(value)
        self.status_label.setText("Font set on size {}.".format(value))

    def compile_c(self):
        if self.form.tree.currentIndex().data() is None:
            self.status_label.setText("Save first, compile later.")
            return

        if self.name is not None:
            QtWidgets.QMessageBox.information(self, "You have some leftover files", "Please clear previously compiled files to avoid cluttering.")
            return
        dialog = CompilatonDialog(self.get_children(), self)
        self.windows.append(dialog)

    def get_children(self):
        node = self.form.tree.currentIndex()
        for_ret = []
        if "." in node.data():
            i = 0
            while node.parent().child(i,0).data() is not None:
                if node.parent().child(i,0).data().endswith(".S"):
                    for_ret.append(node.parent().child(i,0).data())
                i +=1
            return for_ret

    def build_c(self):
        if self.name is None:
            QtWidgets.QMessageBox.critical(self, "Error", "You have to compile first ! ")
            return
        clear()
        command = "./" + self.name
        phrase = '"Press_any_key_to_continue..."'
        os.system("gnome-terminal -e 'bash -c \"" + command + "; read -n1 -r -p " + phrase + " key; exec exit \"'")


    def clear_c(self):
        if self.name is None:
            QtWidgets.QMessageBox.critical(self, "Error", "You have to compile first ! ")
            return
        clear()
        command = "rm '" + self.name + "'"
        os.system(command)
        self.status_label.setText("Local data cleared successfully.")
        self.name = None

    def new_file(self):
        newest = MainWindow()

    def debug_c(self):
        if self.name is None:
            QtWidgets.QMessageBox.critical(self, "Error", "You have to compile first ! ")
            return
        clear()
        command = "ddd " + self.name
        os.system(command)

    def closeEvent(self, event):
        # do stuff
        if self.form.safe_to_close():
            event.accept()
        else:
            message = "You have unsaved changes in: "
            for filename in self.form.get_unsaved_files():
                message += filename + ", "
            flags = QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            button = QtWidgets.QMessageBox.question(self, "Exit without saving?",  message[0: -2] + ".", flags)

            if (button == QtWidgets.QMessageBox.No):
                event.ignore()
            else:
                event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
