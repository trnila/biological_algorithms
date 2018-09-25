import random
import itertools
from PyQt5 import QtCore, Qt, QtWidgets
from PyQt5.QtGui import QPainterPath, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QWidget
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt


import ui_main_window

app = QApplication([])


def sphere(X):
    return X[0] * X[0] + X[1] * X[1]


def plane(X):
    return X[0] * 0 + X[1] * 0


#return A*n + X**2
def rastrigin(Da):
    X = Da[0]
    Y = Da[1]
    n = len(Da)
    A = 10

    return A*n + X**2 - A*np.cos(2 * np.pi * X) + Y**2 - A*np.cos(2 * np.pi * Y)



class BlindSearch:
    def run(self, X, fitness):
        for i in range(100):
            p = np.random.rand(2) * 2 - 1
            z = fitness(p)
            yield (p[0], p[1], z)


class ClimbingSearch:
    def run(self, X, fn):
        start = np.random.rand(2) * 2 - 1
        for i in range(5):
            m = 1000
            arg = None
            points = []
            for x in range(15):
                p = start + np.random.randn(2) * 0.1
                z = fn(p)
                points.append((p[0], p[1], z))
                if z < m:
                    m = z
                    arg = p
            yield points
            start = arg


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.functions.addItem("rastrigin", rastrigin)
        self.ui.functions.addItem("sphere", sphere)
        self.ui.functions.addItem("plane", plane)

        self.ui.algorithm.addItem("climbing search", ClimbingSearch)
        self.ui.algorithm.addItem("blind", BlindSearch)

        self.ui.functions.currentIndexChanged.connect(self.update)
        self.ui.algorithm.currentIndexChanged.connect(self.update)
        self.ui.pushButton.clicked.connect(self.update)

        static_canvas = self.s = FigureCanvas(Figure((5, 4)))
        self.ui.centralwidget.layout().addWidget(static_canvas)

        self.ax = static_canvas.figure.add_subplot(121, projection='3d')
        self.nn = self.s.figure.add_subplot(122)
        self.update()

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        cid = static_canvas.mpl_connect('button_press_event', onclick)

    def update(self):
        X = np.linspace(-6, 6, 50)
        Y = np.linspace(-6, 6, 50)
        X, Y = np.meshgrid(X, Y)

        fn = self.ui.functions.currentData()

        Z = fn([X, Y])
        self.ax.clear()
        self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.inferno, linewidth=0, antialiased=True, alpha=0.5)

        self.nn.clear()
        p = self.nn.imshow(Z, extent=[-6, 6, -6, 6])

        algo = self.ui.algorithm.currentData()()
        colors = ['red', 'green', 'blue', 'purple', 'yellow']
        color = 0
        for points in algo.run([X, Y], fn):
            for point in points:
                self.ax.scatter(*point, color=colors[color])
                self.nn.scatter(point[0], point[1], color=colors[color], s=20, edgecolor='black')
            color += 1

        self.s.draw_idle()



win = MainWindow()
win.setWindowTitle("cv:")
win.show()

app.exec_()