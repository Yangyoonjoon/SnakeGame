from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
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

    def closeEvent(self, e):
        self.game.bRun = False

    def gameOver(self):
        result = QMessageBox.information(self, '게임오버', '다시하겠습니까?', QMessageBox.Yes | QMessageBox.No)

        if result == QMessageBox.Yes:
            del (self.game)
            self.game = Game(self)
        else:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())