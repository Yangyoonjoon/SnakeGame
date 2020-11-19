from PyQt5.QtWidgets import QWidget, QApplication
import sys
from game import *

class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 600)
        self.game = Game(self)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.game.draw(qp)
        qp.end()

    def keyPressEvent(self, e):
        self.game.keyDown(e.key())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())