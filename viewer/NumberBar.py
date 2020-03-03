from PyQt5.Qt import QFrame, QWidget, QHBoxLayout, QPainter, QPlainTextEdit, QFont
from PyQt5 import QtWidgets
import sys



class NumberBar(QWidget):

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.edit = None
        # This is used to update the width of the control.
        # It is the highest line that is currently visibile.
        self.highest_line = 0

    def setTextEdit(self, edit):
        self.edit = edit

    def update(self, *args):
        '''
        Updates the number bar to display the current set of numbers.
        Also, adjusts the width of the number bar if necessary.
        '''
        # The + 4 is used to compensate for the current line being bold.
        width = self.fontMetrics().width(str(self.highest_line)) + 4
        if self.width() != width:
            self.setFixedWidth(width)
        QWidget.update(self, *args)

    def paintEvent(self, event):
        contents_y = self.edit.verticalScrollBar().value()
        page_bottom = contents_y + self.edit.viewport().height()
        font_metrics = self.fontMetrics()
        current_block = self.edit.document().findBlock(self.edit.textCursor().position())

        painter = QPainter(self)

        line_count = 0
        # Iterate over all text blocks in the document.
        block = self.edit.document().begin()
        while block.isValid():
            line_count += 1

            # The top left position of the block in the document
            position = self.edit.document().documentLayout().blockBoundingRect(block).topLeft()

            # Check if the position of the block is out side of the visible
            # area.
            if position.y() > page_bottom:
                break

            # We want the line number for the selected line to be bold.
            bold = False
            if block == current_block:
                bold = True
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)

            # Draw the line number right justified at the y position of the
            # line. 3 is a magic padding number. drawText(x, y, text).
            font = QFont()
            font.setPointSize(self.edit.font().pointSize())
            font.setWordSpacing(20)
            painter.setFont(font)
            if line_count == 1:
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3, 1 + 17 * line_count, str(line_count))
            else:
                painter.drawText(self.width() - font_metrics.width(str(line_count)) - 3,
                                 1 + 17 * line_count + (self.edit.font().pointSize() - 10) * line_count * 2,
                                 str(line_count))
            #print(self.width() - font_metrics.width(str(line_count)) - 3 , " " , round(position.y()) - contents_y + font_metrics.ascent(), str(line_count))

            # Remove the bold style if it was set previously.
            if bold:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            block = block.next()

        self.highest_line = line_count
        painter.end()

        QWidget.paintEvent(self, event)


class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super(TestWidget, self).__init__()
        #window = LineTextWidget()
        self.edit = QPlainTextEdit()
        self.number_bar = NumberBar()
        self.number_bar.setTextEdit(self.edit)
        l = QHBoxLayout()
        l.addWidget(self.number_bar)
        l.addWidget(self.edit)
        self.setLayout(l)
        self.edit.installEventFilter(self)
        self.edit.viewport().installEventFilter(self)
        self.show()

    def eventFilter(self, object, event):
        # Update the line numbers for all events on the text edit and the viewport.
        # This is easier than connecting all necessary singals.
        if object in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QFrame.eventFilter(object, event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wind = TestWidget()
    sys.exit(app.exec_())