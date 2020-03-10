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

from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu,
                             QMessageBox, QTextEdit)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0xCB772F))
        keyword_format.setFontWeight(QFont.Bold)

        keyword_patterns = ["\\bauto\\b", "\\bbreak\\b", "\\bcase\\b", "\\bchar\\b", "\\bconst\\b", "\\bcontinue\\b",
                           "\\bdefault\\b", "\\bdo\\b", "\\bdouble\\b", "\\belse\\b", "\\benum\\b", "\\bextern\\b",
                           "\\bfloat\\b", "\\bfor\\b", "\\bgoto\\b", "\\bif\\b", "\\bint\\b", "\\blong\\b",
                           "\\bregister\\b", "\\breturn\\b", "\\bshort\\b", "\\bsigned\\b", "\\bsizeof\\b",
                           "\\bstatic\\b", "\\bstruct\\b", "\\bswitch\\b", "\\btypedef\\b", "\\bunion\\b",
                           "\\bunsigned\\b", "\\bvoid\\b", "\\bvolatile\\b", "\\bwhile\\b", "\\b#include\\b"]

        self.highlightingRules = []
        for pattern in keyword_patterns:
            self.highlightingRules.append((QRegExp(pattern), keyword_format))

        constant_format = QTextCharFormat()
        constant_format.setFontWeight(QFont.Bold)
        constant_format.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\b([A-Z]+\_*)+\\b"),
                                       constant_format))

        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(Qt.green)
        self.highlightingRules.append((QRegExp("//[^\n]*"),
                                       single_line_comment_format))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.green)

        hashtag_format = QTextCharFormat()
        hashtag_format.setForeground(Qt.magenta)
        self.highlightingRules.append((QRegExp("#[^ ]*"), hashtag_format))

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(QColor(165, 194, 92))
        self.highlightingRules.append((QRegExp("\".*\""), quotation_format))

        include_format = QTextCharFormat()
        include_format.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("<.*>"), include_format))

        function_format = QTextCharFormat()
        function_format.setFontItalic(True)
        function_format.setForeground(QColor(0xCB772F))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                                       function_format))

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                           self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                                                             startIndex + commentLength);
