import sys

from socketIO_client import SocketIO, BaseNamespace
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot


def update(data):
    print(data)

# my socket
socketIO = SocketIO('127.0.0.1', 3409, BaseNamespace)
socketIO.define(BaseNamespace, '/ns') # it doesn't work
socketIO.on('update', update)


# GUI
class App(QWidget):
    global socketIO

    def __init__(self):
        super().__init__()

        self.font = QFont()
        self.title = 'Equation input'
        self.left = 50
        self.top = 100
        self.width = 600
        self.height = 400

        self.font.setPointSize(15)

        self.gene_edit = QLineEdit(self)
        self.gene_edit.setFont(self.font)

        self.initUI(self.font, self.gene_edit)

    def initUI(self, font, gene_edit):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.size())

        label = QLabel("Enter equation :")
        label.setFont(font)

        send_equation = QPushButton('Submit', self)
        send_equation.setFixedHeight(50)
        send_equation.clicked.connect(self.on_click)

        h_box = QHBoxLayout()
        h_box.addWidget(label)
        h_box.addWidget(gene_edit)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(send_equation)

        self.setLayout(v_box)
        self.show()

    @pyqtSlot()
    def on_click(self):
        try:
            equation = self.gene_edit.text()
            if equation != '':
                socketIO.emit('equation', equation)
                socketIO.wait(seconds=1)
                print("Sent to server : ", equation)
            else:
                QMessageBox.about(self, 'Error', 'Wrong input')
        except Exception:
            QMessageBox.about(self, 'Error', 'Wrong input')

    def closeEvent(self, QCloseEvent):
        socketIO.disconnect()
        socketIO._close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
