"""
    Brick is lightweight IDE for C programming language.
    Copyright (C) 2020 : Mršulja Ivan

    This file is part of Brick IDE.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

from PyQt5 import QtWidgets
import os

clear = lambda: os.system("clear")

start_directory = os.getcwd()

class CompilatonDialog(QtWidgets.QDialog):

    def __init__(self, children, parent, settings):
        super(CompilatonDialog, self).__init__(parent)
        self.children = children
        self.window = parent
        self.base_option = settings
        print(self.base_option)
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
            flags = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            button = QtWidgets.QMessageBox.question(self, "Compilation type", "Do you want to compile as 32-bit program?", flags)

            if (button == QtWidgets.QMessageBox.Yes):
                self.base_option += "-m32 "

        self.window.name = os.path.split(self.window.form.save_path)[1]
        self.window.name = "_object_file_" + self.window.name
        command = self.base_option + full_path + " -o '" + self.window.name + "'"
        if self.window.form.terminal.executeCommand(command):
            self.window.status_label.setText("Compiled successfully !")
        else:
            self.window.status_label.setText("Compilation terminated.")
            self.window.name = None
        self.close()


