import shutil

from PyQt5.QtCore import Qt
import os
import qdarkstyle
from model.Terminal import Terminal
from model.Autocompleter import *


class TextEditor(QtWidgets.QWidget):

    def __init__(self):
        super(TextEditor, self).__init__()
        self.save_path = None
        self.open_path = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("QWidget { background-color: #2B2B2B ; color: #A9B7C6}")
        self.init_text_edit()

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

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.text, 0, 2, 4, 6)
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

        if self.tree.currentIndex().internalPointer() is not None:
            self.contextMenu.addAction(actionNewFolder)
            self.contextMenu.addAction(actionNewFile)
            self.contextMenu.addAction(action_delete)
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

    def init_text_edit(self):
        self.completer = MyDictionaryCompleter()
        self.text = MyTextEdit(self)
        self.text.setCompleter(self.completer)
        self.text.setStyleSheet("QPlainTextEdit { color: rgb(169, 183, 198) }")

        self.font = QtGui.QFont()
        self.font.setFamily('Ariel')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)

        self.text.setFont(self.font)
        self.highlighter = Highlighter(self.text.document())
        self.text.textChanged.connect(self.save_locally)

        with open("viewer/local_data.txt", "r") as f:
            lines = f.read()
            self.text.setPlainText(lines)

        new_completer = check_for_header_files(self.text.toPlainText(), self.completer.my_keywords)
        self.text.setCompleter(new_completer)

    def set_font(self, value):
        if int(value) >= 8 and int(value) <= 50:
            self.font.setPointSize(int(value))
            self.text.setFont(self.font)
        else:
            self.font.setPointSize(10)
            self.text.setFont(self.font)

    def save_locally(self):
        text = self.text.toPlainText()
        with open("viewer/local_data.txt", "w") as f:
            f.write(text)

    def save_file(self):
        if self.save_path is None:
            QtWidgets.QMessageBox.information(self, "Error",
                                              "Open directory first, then select file by double clicking on it to enable this option.")
            if self.open_path is None or self.open_path == "":
                self.open_file()
            return
        try:
            with open(self.save_path, "w") as file:
                text = self.text.toPlainText()
                file.write(text)
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
        with open("viewer/temp.txt", "w") as f:
            f.write(self.open_path + "|" + str(self.save_path))

    def get_open_path(self):
        with open("viewer/temp.txt", "r") as f:
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
        current = self.tree.currentIndex()
        path = []
        while current != self.tree.rootIndex():
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

            with open(self.save_path, "r") as file:
                text = file.read()
                self.text.setPlainText(text)
            self.write_path()

            self.update_hints()

    def update_hints(self):
        new_completer = check_for_header_files(self.text.toPlainText(), self.completer.my_keywords)
        self.text.setCompleter(new_completer)