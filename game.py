from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QRectF, QPoint, pyqtSignal, QObject
from threading import Thread
import time
import random

class Game(QObject):

    update_signal = pyqtSignal()
    gameover_signal = pyqtSignal()

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

        # 뱀 먹이
        self.bFood = False
        self.fx = 0
        self.fy = 0

        # 키보드 2중 방지
        self.bMoved = False

        # 시그널 처리
        self.update_signal.connect(self.parent.update)
        self.gameover_signal.connect(self.parent.gameOver)

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
        for i, m in enumerate(self.snake):
            if i == 0:
                qp.setBrush(hb)
            else:
                qp.setBrush(bb)
            qp.drawRect(self.rects[m.y()][m.x()])
            if i == 0:
                qp.drawText(self.rects[m.y()][m.x()], Qt.AlignCenter, str(len(self.snake)))

        # 밥 그리기
        if self.bFood:
            b = QBrush(QColor(255,100,0))
            qp.setBrush(b)
            qp.drawEllipse(self.rects[self.fy][self.fx])

    def keyDown(self, key):
        if not self.bMoved:
            # 뱀 방향 0:L, 1:U, 2:R, 3:D
            if key == Qt.Key_Left and self.dir != 2:
                self.dir = 0
            elif key == Qt.Key_Up and self.dir != 3:
                self.dir = 1
            elif key == Qt.Key_Right and self.dir != 0:
                self.dir = 2
            elif key == Qt.Key_Down and self.dir != 1:
                self.dir = 3

            self.bMoved = True

    def makeFood(self):
        while True:
            x = random.randint(0, self.line-2)
            y = random.randint(0, self.line-2)

            # 뱀 마디와 밥 좌표 비교
            bOverlap = False
            for m in self.snake:
                if m.x() == x and m.y() == y:
                    bOverlap = True
                    break

            if bOverlap == False:
                self.fx = x
                self.fy = y
                self.bFood = True
                break
            else:
                continue

    def isEat(self, hx, hy):
        if hx == self.fx and hy == self.fy:
            return True
        else:
            return False

    def isEatMyBody(self, hx, hy):
        minLen = 4
        if len(self.snake) > minLen:
            for i, m in enumerate(self.snake):
                if i > minLen-1:
                    if hx == m.x() and hy == m.y():
                        return True
        return False


    def threadFunc(self):
        while self.bRun:
            # 밥 생성
            if self.bFood == False:
                self.makeFood()

            # 기존 머리
            head = QPoint(self.snake[0])
            x = head.x()
            y = head.y()

            # 밥 먹었는지
            eat = self.isEat(x, y)

            # 이동방향에 따른 새 머리
            # 뱀이동 0:L, 1:U, 2:R, 3:D
            if self.dir == 0:
                head.setX(x-1)
            elif self.dir == 1:
                head.setY(y-1)
            elif self.dir == 2:
                head.setX(x+1)
            else:
                head.setY(y+1)

            # 뱀 머리, 마디 충돌검사
            if self.isEatMyBody(x, y):
                break

            # 밖으로 나갔는지
            if (head.x() < 0 or head.x() >= self.line-1) or (head.y() < 0 or head.y() >= self.line-1):
                break
            else:
                # 새 머리 추가
                self.snake.insert(0, head)
                # 꼬리 삭제
                if not eat:
                    del(self.snake[-1])
                else:
                    self.bFood = False

            # 키보드 락 풀기
            self.bMoved = False

            self.update_signal.emit()
            time.sleep(0.2)

        # main으로 게임종료 시그널 보내기
        self.gameover_signal.emit()