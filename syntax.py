from PyQt5.QtCore import QFile, QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu,
                             QMessageBox, QTextEdit)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(0xCB772F))
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\bauto\\b", "\\bbreak\\b", "\\bcase\\b", "\\bchar\\b", "\\bconst\\b", "\\bcontinue\\b",
                           "\\bdefault\\b", "\\bdo\\b", "\\bdouble\\b", "\\belse\\b", "\\benum\\b", "\\bextern\\b",
                           "\\bfloat\\b", "\\bfor\\b", "\\bgoto\\b", "\\bif\\b", "\\bint\\b", "\\blong\\b",
                           "\\bregister\\b", "\\breturn\\b", "\\bshort\\b", "\\bsigned\\b", "\\bsizeof\\b",
                           "\\bstatic\\b", "\\bstruct\\b", "\\bswitch\\b", "\\btypedef\\b", "\\bunion\\b",
                           "\\bunsigned\\b", "\\bvoid\\b", "\\bvolatile\\b", "\\bwhile\\b", "\\b#include\\b"]

        self.highlightingRules = []
        for pattern in keywordPatterns:
            self.highlightingRules.append((QRegExp(pattern), keywordFormat))

        classFormat = QTextCharFormat()
        classFormat.setFontWeight(QFont.Bold)
        classFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"),
                                       classFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.green)
        self.highlightingRules.append((QRegExp("//[^\n]*"),
                                       singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.green)

        hashtagFormat = QTextCharFormat()
        hashtagFormat.setForeground(Qt.magenta)
        self.highlightingRules.append((QRegExp("#[^ ]*"), hashtagFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor(165, 194, 92))
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

        includeFormat = QTextCharFormat()
        includeFormat.setForeground(Qt.darkMagenta)
        self.highlightingRules.append((QRegExp("<.*>"), includeFormat))

        functionFormat = QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(QColor(0xCB772F))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
                                       functionFormat))

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
