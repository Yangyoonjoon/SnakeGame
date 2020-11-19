from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QRectF, QPoint, pyqtSignal, QObject
from threading import Thread
import time

class Game(QObject):

    update_signal = pyqtSignal()

    def __init__(self, w):
        super().__init__()
        self.parent = w
        self.rect = w.rect()
        self.inrect = QRectF(self.rect)
        gap = 20
        self.inrect.adjust(gap, gap, -gap, -gap)

        # 게임판 라인 수, 게임판 한칸 크기
        self.line = 20
        self.size = self.inrect.width() / (self.line-1)

        # 게임판 개수 초기화
        x = self.inrect.left()
        y = self.inrect.top()
        gap = 2
        self.rects = []

        for r in range(self.line):
            temp = []
            for c in range(self.line):
                rect = QRectF(x+(c*self.size), y+(r*self.size), self.size, self.size)
                rect.adjust(gap, gap, -gap, -gap)
                temp.append(rect)
            self.rects.append(temp)

        # 초기뱀 생성
        head = QPoint(self.line//2, self.line//2)
        self.snake = []
        self.snake.append(head)
        self.snake.append(QPoint(head.x()-1, head.y()))
        self.snake.append(QPoint(head.x()-2, head.y()))

        # 뱀 방향 0:L, 1:U, 2:R, 3:D
        self.dir = 2

        # 시그널 처리
        self.update_signal.connect(self.parent.update)

        # 쓰레드 생성
        self.t = Thread(target=self.threadFunc)
        self.bRun = True
        self.t.start()


    def draw(self, qp):
        # 게임판 그리기
        x = self.inrect.left()
        y = self.inrect.top()

        x1 = self.inrect.right()
        y1 = self.inrect.top()

        x2 = self.inrect.left()
        y2 = self.inrect.bottom()

        for i in range(self.line):
            qp.drawLine(x, y+(i*self.size), x1, y1+(i*self.size))
            qp.drawLine(x+(i*self.size), y, x2+(i*self.size), y2)

        # 뱀 그리기
        hb = QBrush(QColor(255,165,0))
        bb = QBrush(QColor(255,215,0))
        qp.setBrush(hb)
        for m in self.snake:
            qp.drawRect(self.rects[m.y()][m.x()])
            qp.setBrush(bb)

    def keyDown(self, key):
        # 뱀 방향 0:L, 1:U, 2:R, 3:D
        if key == Qt.Key_Left:
            self.dir = 0
        elif key == Qt.Key_Up:
            self.dir = 1
        elif key == Qt.Key_Right:
            self.dir = 2
        elif key == Qt.Key_Down:
            self.dir = 3


    def threadFunc(self):
        while self.bRun:
            # 뱀이동 0:L, 1:U, 2:R, 3:D

            # 기존 머리
            head = QPoint(self.snake[0])
            x = head.x()
            y = head.y()

            # 이동방향에 따른 새 머리
            if self.dir == 0:
                head.setX(x-1)
            elif self.dir == 1:
                head.setY(y-1)
            elif self.dir == 2:
                head.setX(x+1)
            else:
                head.setY(y+1)

            # 새 머리 추가
            self.snake.insert(0, head)
            # 꼬리 삭제
            del(self.snake[-1])

            self.update_signal.emit()
            time.sleep(0.1)