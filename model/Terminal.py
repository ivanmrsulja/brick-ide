"""
    i386ide is lightweight IDE for i386 assembly and C programming language.
    Copyright (C) 2019  Dušan Erdeljan, Marko Njegomir
    Redistributed by: Mršulja Ivan

    This file is part of i386ide.
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

from PyQt5.QtWidgets import QDockWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from controller.TerminalConsole import TerminalConsole


class Terminal(QDockWidget):
    projectSwitchRequested = pyqtSignal()
    tabSwitchRequested = pyqtSignal()

    def __init__(self):
        super(Terminal, self).__init__()
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.titleLabel = QLabel()
        self.titleLabel.setStyleSheet("background-color: #303A3D; color: #D8D8D8")
        self.titleLabel.setText("Terminal")
        self.setTitleBarWidget(self.titleLabel)
        self.setWindowTitle("Terminal")
        self.console = TerminalConsole()
        self.setWidget(self.console)
        self.console.projectSwitchRequested.connect(lambda: self.projectSwitchRequested.emit())
        self.console.tabSwitchRequested.connect(lambda: self.tabSwitchRequested.emit())

    def executeCommand(self, command):
        return self.console.executeCommand(command)

    def getUsername(self):
        return self.console.username