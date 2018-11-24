import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QPainterPath, QBrush, QColor, QPen, QPixmap
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem
import random
import ui_main_window
from antcolony import AntColony
from cities import cities
from genetic import Genetic
from common import Trajectory

np.set_printoptions(threshold=np.nan, linewidth=10000)


class Test:
    def __init__(self, cities, __):
        self.cities = cities

    def run(self):
        import tsp
        c = [(x.x, x.y) for x in self.cities]
        t = tsp.tsp(c)

        yield Trajectory(t[1], t[0]), Trajectory(t[1], t[0])


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.cities = cities

        self.autoplay = False
        self._zoom = 1
        self.genetic = None
        self.paths = []
        self.last = None

        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

        self.ui.popSize.setValue(20)
        self.ui.algorithm.addItem('ant', AntColony)
        self.ui.algorithm.addItem('genetic', Genetic)
        self.ui.algorithm.addItem('solver', Test)

        self.ui.playBtn.clicked.connect(self.on_play_click)
        self.ui.nextBtn.clicked.connect(self.next)
        self.ui.restartBtn.clicked.connect(self.start)
        self.ui.showCur.stateChanged.connect(self.redraw)

        self.timer = QTimer()
        self.timer.timeout.connect(self.gen_next)
        self.timer.start(1)

        for city in self.cities:
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

        seed = 100
        print(seed)
        random.seed(seed)
        np.random.seed(seed)

        self.clear_paths()
        self.ui.distance.setText("")
        clazz = self.ui.algorithm.currentData()
        self.genetic = clazz(self.cities, int(self.ui.popSize.text())).run({})

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
            path.moveTo(self.cities[trajectory.path[0]].x, self.cities[trajectory.path[0]].y)
            for hop in trajectory.path:
                city = self.cities[hop]
                path.lineTo(city.x, city.y)
            path.lineTo(self.cities[trajectory.path[0]].x, self.cities[trajectory.path[0]].y)

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