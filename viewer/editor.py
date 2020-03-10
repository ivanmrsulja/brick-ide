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

import shutil
from model.SaveNode import *
from PyQt5.QtCore import Qt, pyqtRemoveInputHook
from PyQt5.Qt import QFrame
import os
import qdarkstyle
from model.Terminal import Terminal
from model.Autocompleter import *
from viewer.NumberBar import NumberBar


class TextEditor(QtWidgets.QWidget):

    def __init__(self):
        super(TextEditor, self).__init__()
        self.save_path = None
        self.open_path = None
        self.local_data = {}
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("QWidget { background-color: #2B2B2B ; color: #A9B7C6}")

        self.terminal = Terminal()

        self.tree = QtWidgets.QTreeView()
        self.tree.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.model = QtWidgets.QFileSystemModel()
        self.index_model = QtCore.QModelIndex()
        self.model.setRootPath("")

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)

        self.tree.setAnimated(True)
        self.tree.setIndentation(15)
        self.tree.setSortingEnabled(True)
        self.tree.setWindowTitle("Dir View")
        self.tree.doubleClicked.connect(self.tree_clk)
        self.get_open_path()
        self.init_text_edit()
        self.text_edit_layout = QtWidgets.QHBoxLayout()
        self.text_edit_layout.addWidget(self.number_bar)
        self.text_edit_layout.addWidget(self.text)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addLayout(self.text_edit_layout, 0, 2, 4, 6)
        self.grid.addWidget(self.tree, 0, 0, 4, 2)
        self.grid.addWidget(self.terminal, 4, 0, 2, 8)

        self.setLayout(self.grid)

    def open_menu(self, position):
        self.contextMenu = QtWidgets.QMenu()

        actionNewFolder = QtWidgets.QAction("New Folder", None)
        actionNewFolder.triggered.connect(self.make_new_folder)

        actionNewFile = QtWidgets.QAction("New File", None)
        actionNewFile.triggered.connect(self.make_new_c_file)

        action_delete = QtWidgets.QAction("Delete", None)
        action_delete.triggered.connect(self.delete_node)

        action_refresh = QtWidgets.QAction("Refresh", None)
        action_refresh.triggered.connect(self.refresh_table)

        action_rename = QtWidgets.QAction("Rename", None)
        action_rename.triggered.connect(self.rename_node)

        if self.open_path is not None:
            self.contextMenu.addAction(actionNewFolder)
            self.contextMenu.addAction(actionNewFile)
            self.contextMenu.addAction(action_delete)
            if self.tree.currentIndex().internalPointer() is not None:
                self.contextMenu.addAction(action_rename)
            self.contextMenu.addAction(action_refresh)


        self.contextMenu.exec_(self.tree.viewport().mapToGlobal(position))

    def refresh_table(self):
        self.tree.repaint()

    def delete_node(self):
        name = str(self.tree.currentIndex().data())
        message = name + " will be deleted permanently !"
        flags = QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        button = QtWidgets.QMessageBox.question(self, "Are you sure ?", message, flags)

        if (button == QtWidgets.QMessageBox.Yes):

            base_path = self.open_path
            if self.tree.currentIndex().parent() != self.tree.rootIndex():
                base_path = os.path.split(self.get_path_for_making(base_path))[0]

            del_path = os.path.join(base_path, name)
            try:
                shutil.rmtree(del_path)
            except NotADirectoryError:
                os.remove(del_path)
            self.refresh_table()
            if del_path == self.save_path:
                self.save_path = None

    def rename_node(self):
        ret_text, ok_button = QtWidgets.QInputDialog.getText(self, "Rename", "Insert new name: ")
        if ok_button:
            if ret_text.strip() == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Empty directory name! ")
                return
            path = self.get_path_for_making(self.open_path)
            os.rename(path, os.path.join(os.path.split(path)[0], ret_text))
            self.tree.repaint()

    def make_new_folder(self):
        base_path = self.open_path
        if self.tree.currentIndex().parent() != self.tree.rootIndex() or not "." in self.tree.currentIndex().data():
            base_path = self.get_path_for_making(self.open_path)
            if "." in base_path:
                base_path = os.path.split(base_path)[0]

        ret_text, ok_button = QtWidgets.QInputDialog.getText(self, "Directory name", "Insert directory name: ")
        if ok_button:
            if ret_text.strip() == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Empty directory name! ")
                return
            final_path = os.path.join(base_path, ret_text.split(".")[0])
            os.mkdir(final_path)
            self.tree.repaint()

    def make_new_c_file(self):
        base_path = self.open_path
        if self.tree.currentIndex().parent() != self.tree.rootIndex() or not "." in self.tree.currentIndex().data():
            base_path = self.get_path_for_making(self.open_path)
            if "." in base_path:
                base_path = os.path.split(base_path)[0]

        ret_text, ok_button = QtWidgets.QInputDialog.getText(self, "File name", "Insert file name: ")
        if ok_button:
            if ret_text.strip() == "":
                QtWidgets.QMessageBox.critical(self, "Error", "Empty file name! ")
                return
            if "." not in ret_text:
                ret_text = ret_text + ".c"
            final_path = os.path.join(base_path, ret_text)
            with open(final_path, "w") as new_file:
                pass
            self.refresh_table()
            return final_path
        return None

    def init_text_edit(self):
        self.completer = MyDictionaryCompleter()
        self.text = MyTextEdit(self)
        self.text.setCompleter(self.completer)
        self.text.setStyleSheet("QPlainTextEdit { color: rgb(169, 183, 198) }")

        self.number_bar = NumberBar()
        self.number_bar.setTextEdit(self.text)

        self.font = QtGui.QFont()
        self.font.setFamily('Ariel')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)

        self.text.setFont(self.font)
        self.highlighter = Highlighter(self.text.document())
        self.text.textChanged.connect(self.save_locally)

        with open("../viewer/local_data.txt", "r") as f:
            lines = f.read()
            self.text.setPlainText(lines)

        if lines.strip() == "" and self.save_path is not None:
            with open(self.save_path, "r") as f:
                lines = f.read()
                self.text.setPlainText(lines)

        new_completer = check_for_header_files(self.text.toPlainText(), self.completer.my_keywords)
        self.text.setCompleter(new_completer)

        self.text.installEventFilter(self)
        self.text.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.text, self.text.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)

    def set_font(self, value):
        if int(value) >= 8 and int(value) <= 50:
            self.font.setPointSize(int(value))
            self.text.setFont(self.font)
        else:
            self.font.setPointSize(10)
            self.text.setFont(self.font)

    def save_locally(self):
        if self.save_path is None:
            return
        text = self.text.toPlainText()
        with open("../viewer/local_data.txt", "w") as f:
            f.write(text)
        if self.save_path not in self.local_data.keys():
            new_save = SaveNode(self.save_path)
            new_save.data = text
            self.local_data[self.save_path] = new_save
        else:
            if text != self.local_data[self.save_path].data:
                self.local_data[self.save_path].data = text
                self.local_data[self.save_path].saved = False
        #print(self.local_data[self.save_path].data)

    def save_file(self):
        if self.save_path is None:
            QtWidgets.QMessageBox.information(self, "Specify location",
                                              "Please specify a location where you would like to save.")
            if self.open_path is None or self.open_path == "":
                self.open_file()

            path = self.make_new_c_file()
            if path is None:
                return
            else:
                self.save_path = path
                self.tree.setCurrentIndex(self.model.index(self.save_path))
                self.save_locally()
        try:
            with open(self.save_path, "w") as file:
                text = self.text.toPlainText()
                file.write(text)
            self.local_data[self.save_path].saved = True
        except:
            QtWidgets.QMessageBox.information(self, "Error", "You can't save if you don't specify location!")
            self.save_path = None

    def open_file(self):
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open directory")
        if file_path == "":
            return
        self.save_path = None
        if self.open_path is None:
            self.tree.setModel(self.model)
            for i in range(1, 4):
                self.tree.hideColumn(i)
        self.open_path = file_path
        self.write_path()
        self.tree.setRootIndex(self.model.index(self.open_path))

        self.update_hints()

    def write_path(self):
        with open("../viewer/temp.txt", "w") as f:
            f.write(self.open_path + "|" + str(self.save_path))

    def get_open_path(self):
        with open("../viewer/temp.txt", "r") as f:
            path = f.read()
        if path == "":
            return
        paths = path.split("|")
        self.open_path = paths[0]
        self.save_path = paths[1]

        if self.open_path != "None":
            self.tree.setModel(self.model)

            for i in range(1,4):
                self.tree.hideColumn(i)

            self.tree.setRootIndex(self.model.index(self.open_path))
        else:
            self.open_path = None
        if self.save_path != "None":
            self.tree.setCurrentIndex(self.model.index(self.save_path))
        else:
            self.save_path = None

    def get_path_for_making(self, base_path):
        if self.tree.currentIndex().data() is None:
            return self.open_path
        current = self.tree.currentIndex()
        path = []
        while current != self.tree.rootIndex():
            print(self.tree.currentIndex().data())
            path.append(current.data())
            current = current.parent()
        path.reverse()
        final_path = ""
        for node in path:
            final_path = final_path + "/" + node

        final_path = base_path + final_path

        return  final_path


    def tree_clk(self):
        if self.tree.currentIndex().data().endswith(".c") or self.tree.currentIndex().data().endswith(".h"):
            base_path = os.path.join(self.open_path, self.tree.currentIndex().data())
            if self.tree.currentIndex().parent() != self.tree.rootIndex():
                base_path = self.get_path_for_making(self.open_path)
            self.save_path = base_path

            if self.save_path not in self.local_data.keys():
                with open(self.save_path, "r") as file:
                    text = file.read()
                    new_save = SaveNode(self.save_path)
                    new_save.data = text
                    self.local_data[self.save_path] = new_save
                    self.text.setPlainText(text)
            else:
                self.text.setPlainText(self.local_data[self.save_path].data)

            self.write_path()
            self.update_hints()

    def update_hints(self):
        new_completer = check_for_header_files(self.text.toPlainText(), self.completer.my_keywords)
        self.text.setCompleter(new_completer)

    def safe_to_close(self):
        for file in self.local_data.values():
            if not file.saved:
                return False
        return True

    def get_unsaved_files(self):
        for_ret = []
        for path in self.local_data.keys():
            if not self.local_data[path].saved:
                for_ret.append(path.split("/")[-1])
        return for_ret