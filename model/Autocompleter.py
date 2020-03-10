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

from PyQt5 import QtGui, QtCore, QtWidgets
from model.syntax import Highlighter
import re
import json

SYSTEM_LIBRARIES = {}


class MyTextEdit(QtWidgets.QPlainTextEdit):

    def __init__(self, *args):
        # *args to set parent
        QtWidgets.QLineEdit.__init__(self, *args)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.completer = None
        self.higlighter = Highlighter(self)

    def setCompleter(self, completer):
        # if self.completer:
        #     self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
        self.completer.insertText.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) -
                 len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtWidgets.QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_BracketLeft:
            self.insertPlainText("[]")
            return
        if event.key() == QtCore.Qt.Key_BraceLeft:
            spaces = ""
            count = 1 / 4
            if self.textCursor().block().text().startswith("    "):
                count = self.textCursor().block().text().count("    ")
                for i in range(count):
                    spaces += "    "
            self.insertPlainText("{\n    " + spaces + "\n" + spaces + "}")
            cursor = self.textCursor()
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, count * 4 + 2)
            self.setTextCursor(cursor)
            return
        if event.key() == QtCore.Qt.Key_Tab:
            self.insertPlainText("    ")
            return
        if self.completer and self.completer.popup() and self.completer.popup().isVisible():
            if event.key() in (
                    QtCore.Qt.Key_Enter,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Escape,
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Backtab):
                event.ignore()
                return
        if event.key() == QtCore.Qt.Key_Return:
            text = self.textCursor().block().text()
            if "#include" in text:
                self.setCompleter(check_for_header_files(self.toPlainText(), None))
            tab_counter = 0
            for char in text:
                if char != " ":
                    break
                else:
                    tab_counter += 1
            line = "\n"
            for i in range(tab_counter):
                line = line + " "
            self.insertPlainText(line)
            return
        if event.modifiers() == QtCore.Qt.ShiftModifier and event.key() == QtCore.Qt.Key_ParenLeft:
            self.insertPlainText("( )")
            cursor = self.textCursor()
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 2)
            self.setTextCursor(cursor)
            return
        # has ctrl-i been pressed??
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_I:
            self.setCompleter(check_for_header_files(self.toPlainText()))
        # has ctrl-Space been pressed??
        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and \
                      event.key() == QtCore.Qt.Key_Space)
        # modifier to complete suggestion inline ctrl-e
        inline = (event.modifiers() == QtCore.Qt.ControlModifier and \
                  event.key() == QtCore.Qt.Key_E)
        # if inline completion has been chosen
        if inline:
            # set completion mode as inline
            self.completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
            completion_prefix = self.textUnderCursor()
            if completion_prefix != self.completer.completionPrefix():
                self.completer.setCompletionPrefix(completion_prefix)
            self.completer.complete()

            self.completer.insertText.emit(self.completer.currentCompletion())

            self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            return
        if (not self.completer or not isShortcut):
            pass
            QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, \
                                            QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text() == '':
            return

        eow = "~!@#$%^&*+{}|:\"<>?,./;'[]\\-="  # end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and \
                       not ctrlOrShift)

        completion_prefix = self.textUnderCursor()
        if completion_prefix == ")":
            self.shift_cursor("l", 1)
            completion_prefix = self.textUnderCursor()
            self.shift_cursor("r", 1)
        elif completion_prefix == "()":
            completion_prefix = ""

        if not isShortcut:
            if self.completer.popup():
                self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(completion_prefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(
            self.completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)  # popup

    def shift_cursor(self, direction, spaces):
        cursor = self.textCursor()
        if direction == "r":
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, spaces)
        elif direction == "l":
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, spaces)
        self.setTextCursor(cursor)


class MyDictionaryCompleter(QtWidgets.QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, my_keywords=None, parent=None):
        global SYSTEM_LIBRARIES
        self.current_parrent = parent
        self.my_keywords = my_keywords
        if len(SYSTEM_LIBRARIES) == 0:
            with open("../model/libraries.json", "r") as libs:
                SYSTEM_LIBRARIES = json.loads(libs.read())
            SYSTEM_LIBRARIES["_natives"] = ["auto", "break", "case", "char", "const", "continue",
                                            "default", "do", "double", "else", "enum", "extern",
                                            "float", "for", "goto", "if", "int", "long",
                                            "register", "return", "short", "signed", "sizeof",
                                            "static", "struct", "switch", "typedef", "union",
                                            "unsigned", "void", "volatile", "while", "include"]
            SYSTEM_LIBRARIES["_others"] = []
        QtWidgets.QCompleter.__init__(self, self.my_keywords, self.current_parrent)
        self.activated.connect(self.changeCompletion)

    def changeCompletion(self, completion):
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        self.insertText.emit(completion)

    def addKeywords(self, keywords):
        for keyword in keywords:
            self.my_keywords.append(keyword)
        QtWidgets.QCompleter.__init__(self, self.my_keywords, self.current_parrent)
        self.activated.connect(self.changeCompletion)


def check_for_header_files(text, keywords: list = None):
    global SYSTEM_LIBRARIES
    if keywords is None:
        keywords = []
    else:
        keywords.clear()
    occurences = re.findall("#include <.+>", text)
    occurences.append("#include <_natives>")
    occurences.append("#include <_others>")
    definitions = re.findall("#define .+", text)
    for definition in definitions:
        SYSTEM_LIBRARIES["_others"].clear()
        SYSTEM_LIBRARIES["_others"].append(definition.split(" ")[1])
    for occurence in occurences:
        if "<" in occurence:
            library = occurence.strip().split(" ")[1].replace("<", "").replace(">", "")
            try:
                for function in SYSTEM_LIBRARIES[library]:
                    keywords.append(function)
            except KeyError:
                print("Nepodrzana biblioteka:", library)
        elif '"' in occurence:
            print(occurence.strip().split(' ')[1].replace('"', '').replace('"', ''))
            pass
    return MyDictionaryCompleter(keywords)


def append_word_to_autocompleter(text, word):
    global SYSTEM_LIBRARIES
    SYSTEM_LIBRARIES["_others"].append(word)
    check_for_header_files(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    completer = MyDictionaryCompleter()
    te = MyTextEdit()
    te.setCompleter(completer)
    te.show()
    app.exec_()
