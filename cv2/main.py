import random
import itertools
from PyQt5 import QtCore, Qt, QtWidgets
from PyQt5.QtGui import QPainterPath, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QWidget, QLineEdit, QLabel, \
    QSpinBox, QDoubleSpinBox
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import types

import test_functions
import ui_main_window

app = QApplication([])


class Space:
    def __init__(self, sizes):
        self.sizes = sizes

    def gen_uniform_sample(self):
        return np.array([random.randrange(s[0], s[1]) for s in self.sizes])


class BlindSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 10}
        ]

    def run(self, space, fitness, options):
        for i in range(options['iterations']):
            p = space.gen_uniform_sample()
            z = fitness(p)
            yield [(p[0], p[1], z)]


class ClimbingSearch:
    def options(self):
        return [
            {'name': 'iterations', 'transform': int, 'default': 5},
            {'name': 'population', 'transform': int, 'default': 5},
            {'name': 'sigma', 'transform': float, 'default': 0.1, 'type': QDoubleSpinBox},
        ]

    def run(self, space, fn, options):
        start = space.gen_uniform_sample()
        for i in range(options['iterations']):
            m = np.Infinity
            arg = None
            points = []
            for x in range(options['population']):
                p = start + np.random.randn(2) * options['sigma']
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

        for fn in [getattr(test_functions, fn) for fn in dir(test_functions) if isinstance(getattr(test_functions, fn), types.FunctionType)]:
            self.ui.functions.addItem(fn.__name__, fn)

        self.ui.algorithm.addItem("climbing search", ClimbingSearch)
        self.ui.algorithm.addItem("blind", BlindSearch)

        self.ui.functions.currentIndexChanged.connect(self.update)
        self.ui.algorithm.currentIndexChanged.connect(self.update_algo)
        self.ui.pushButton.clicked.connect(self.update)

        self.space = Space(2 * [[-6, 6]])

        static_canvas = self.s = FigureCanvas(Figure())
        self.ui.centralwidget.layout().addWidget(static_canvas)

        self.ax = static_canvas.figure.add_subplot(121, projection='3d')
        self.nn = self.s.figure.add_subplot(122)
        self.update_algo()

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        cid = static_canvas.mpl_connect('button_press_event', onclick)

    def remove(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_algo(self):
        algo = self.ui.algorithm.currentData()()

        row = 0
        self.option_widgets = {}
        self.remove(self.ui.gridLayout_2)
        for option in algo.options():
            self.ui.gridLayout_2.addWidget(QLabel(option['name']), row, 0, 1, 1)
            btn = QSpinBox() if not 'type' in option else option['type']()
            btn.setValue(10)
            btn.setObjectName(option['name'])
            btn.setValue(option['default'])
            btn.setMaximum(1000)
            self.option_widgets[option['name']] = btn
            self.ui.gridLayout_2.addWidget(btn, row, 1, 1, 1)
            row += 1

        self.update()

    def update(self):
        X = np.linspace(self.space.sizes[0][0], self.space.sizes[0][1], 50)
        Y = np.linspace(self.space.sizes[1][0], self.space.sizes[1][1], 50)
        X, Y = np.meshgrid(X, Y)

        fn = self.ui.functions.currentData()

        print(fn)
        Z = fn(np.array([X, Y]))
        self.ax.clear()
        self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.inferno, linewidth=0, antialiased=True, alpha=0.5)

        self.nn.clear()
        self.nn.imshow(Z, extent=np.array(self.space.sizes).flatten())

        algo = self.ui.algorithm.currentData()()


        options = {opt['name']: opt['transform'](self.option_widgets[opt['name']].text()) for opt in algo.options()}

        colors = ['red', 'green', 'blue', 'purple', 'yellow']
        color = 0
        for points in algo.run(self.space, fn, options):
            for point in points:
                self.ax.scatter(*point, color=colors[color])
                self.nn.scatter(point[0], point[1], color=colors[color], s=20, edgecolor='black')
            color = (color + 1) % len(colors)

        self.s.draw_idle()



win = MainWindow()
win.setWindowTitle("cv:")
win.show()

app.exec_()