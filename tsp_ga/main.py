import time

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainterPath, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from collections import namedtuple
import random

import ui_main_window

from genetic import Trajectory, Genetic

City = namedtuple('City', ['x', 'y', 'name', 'id'])
cities = [
    City(60,200, 'A',0),
    City(80,200,'B',1),
    City(80,180,'C',2),
    City(140,180,'D',3),
    City(20,160,'E',4),
    City(100,160,'F',5),
    City(200,160,'G',6),
    City(140,140,'H',7),
    City(40,120,'I',8),
    City(100,120,'J',9),
    City(180,100, 'K',10),
    City(60,80, 'L',11),
    City(120,80, 'M',12),
    City(180,60,'N',13),
    City(20,40,'O',14),
    City(100,40,'P',15),
    City(200,40,'Q',16),
    City(20,20,'R',17),
    City(60,20,'S',18),
    City(160,20,'T',19),
]


class Test:
    def __init__(self, _, __):
        pass

    def run(self):
        import tsp
        c = [(x.x, x.y) for x in cities]
        t = tsp.tsp(c)

        yield Trajectory(t[1], t[0]), Trajectory(t[1], t[0])


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.autoplay = False
        self._zoom = 1
        self.genetic = None
        self.paths = []
        self.last = None

        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

        self.ui.algorithm.addItem('genetic', Genetic)
        self.ui.algorithm.addItem('solver', Test)

        self.ui.playBtn.clicked.connect(self.on_play_click)
        self.ui.nextBtn.clicked.connect(self.next)
        self.ui.restartBtn.clicked.connect(self.start)
        self.ui.showCur.stateChanged.connect(self.redraw)

        self.timer = QTimer()
        self.timer.timeout.connect(self.gen_next)
        self.timer.start(1)

        for city in cities:
            self.scene.addEllipse(city.x, city.y, 5, 5, QPen(), QBrush(QColor(255, 0, 0)))
            self.scene.addSimpleText(city.name).setPos(city.x + 5, city.y + 5)

        self.start()

    def start(self):
        try:
            seed = int(self.ui.seed.text())
        except ValueError as e:
            seed = -1

        if seed <= -1:
            seed = random.randint(0, 1000)

        print(seed)
        random.seed(seed)
        np.random.seed(seed)

        self.clear_paths()
        self.ui.distance.setText("")
        clazz = self.ui.algorithm.currentData()
        self.genetic = clazz(cities, int(self.ui.popSize.text())).run()

    def on_play_click(self, play):
        self.autoplay = play

    def gen_next(self):
        if self.autoplay:
            self.next()

    @QtCore.pyqtSlot()
    def next(self):
        try:
            trajectories = next(self.genetic)
        except StopIteration:
            self.ui.playBtn.setChecked(False)
            self.autoplay = False
            return

        self.ui.distance.setText(f"{trajectories[0].distance:.2f} units")

        self.last = trajectories
        self.draw_trajectories(trajectories)

    def redraw(self):
        self.draw_trajectories(self.last)

    def draw_trajectories(self, trajectories):
        self.clear_paths()

        pens = [
            QPen(QColor(255, 0, 0)),
            QPen(QColor(0, 0, 0))
        ]

        for i, trajectory in enumerate(trajectories):
            if i != 0 and not self.ui.showCur.isChecked():
                break

            path = QPainterPath()
            path.moveTo(cities[trajectory.path[0]].x, cities[trajectory.path[0]].y)
            for hop in trajectory.path:
                city = cities[hop]
                path.lineTo(city.x, city.y)
            path.lineTo(cities[trajectory.path[0]].x, cities[trajectory.path[0]].y)

            self.paths.append(
                self.scene.addPath(path, pen=pens[i])
            )

    def clear_paths(self):
        for path in self.paths:
            self.scene.removeItem(path)
        self.paths = []


app = QApplication([])

win = MainWindow()
win.setWindowTitle("cv: ")
win.show()

app.exec_()