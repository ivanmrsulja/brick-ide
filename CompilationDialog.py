from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QIcon
import sys
import os
from PyQt5.QtWidgets import QFileSystemModel
from syntax import Highlighter
from editor import TextEditor
import qdarkstyle
import PyQt5.Qsci
from Terminal import Terminal

clear = lambda: os.system("clear")

class CompilatonDialog(QtWidgets.QDialog):

    def __init__(self, children, parent):
        super(CompilatonDialog, self).__init__(parent)
        self.children = children
        self.window = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Compilation dialog.")
        title_label = QtWidgets.QLabel("You have ASM files in this project, would you like to include them?")
        compile_btn = QtWidgets.QPushButton("Compile")
        compile_btn.clicked.connect(self.compile_c)

        self.buttons = []

        if len(self.children) != 0:
            buttons_layout = QtWidgets.QHBoxLayout()
            counter = 1
            new = QtWidgets.QVBoxLayout()
            for child in self.children:
                if counter < 5:
                    box = QtWidgets.QCheckBox(child)
                    new.addWidget(box)
                    self.buttons.append(box)
                    counter += 1
                else:
                    counter = 1
                    buttons_layout.addLayout(new)
                    new = QtWidgets.QVBoxLayout()
            buttons_layout.addLayout(new)
            final_layout = QtWidgets.QVBoxLayout()
            final_layout.addWidget(title_label)
            final_layout.addLayout(buttons_layout)
            final_layout.addStretch()
            final_layout.addWidget(compile_btn)
            self.setLayout(final_layout)
            self.show()
        else:
            self.compile_c()


    def compile_c(self):
        clear()
        node = self.window.form.tree.currentIndex()
        base_path = os.path.split(self.window.form.save_path)[0]
        full_path = self.window.form.save_path

        if len(self.buttons) != 0:
            for button in self.buttons:
                if button.isChecked():
                    full_path = full_path + " " + os.path.join(base_path, button.text())

        print(full_path)
        self.window.name = os.path.split(self.window.form.save_path)[1]
        command = "gcc -g " + full_path + " -o '" + self.window.name + "'"
        print(command)
        os.system(command)
        self.window.status_label.setText("Compiled successfully !")
        self.close()


