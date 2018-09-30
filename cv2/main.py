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

import matplotlib.pyplot as plt
import types
import pyqtgraph.opengl as gl
from pyqtgraph.opengl.shaders import ShaderProgram, VertexShader, FragmentShader, glEnable, GL_DEPTH_TEST, GL_BLEND, \
    glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glDisable, GL_CULL_FACE

import algorithms
import renderer
import test_functions
import ui_main_window

app = QApplication([])


class Space:
    def __init__(self, sizes):
        self.sizes = sizes

    def gen_uniform_sample(self):
        return np.array([random.uniform(s[0], s[1]) for s in self.sizes])



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.space = Space(2 * [[-6, 6]])
        self.renderers = []

        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        for fn in [getattr(test_functions, fn) for fn in dir(test_functions) if isinstance(getattr(test_functions, fn), types.FunctionType)]:
            self.ui.functions.addItem(fn.__name__, fn)

        self.ui.algorithm.addItem("climbing search", algorithms.ClimbingSearch)
        self.ui.algorithm.addItem("blind", algorithms.BlindSearch)

        self.ui.functions.currentIndexChanged.connect(self.update)
        self.ui.algorithm.currentIndexChanged.connect(self.update_algo)
        self.ui.pushButton.clicked.connect(self.update)

        self.setup_renderers()
        self.update_algo()
        self.update()

    def setup_renderers(self):
        renderer_opengl = renderer.OpenglRenderer()
        self.ui.tab.layout().addWidget(renderer_opengl)
        self.renderers.append(renderer_opengl)

        renderer_matplotlib = renderer.MatplotlibRenderer()
        self.ui.tab_2.layout().addWidget(renderer_matplotlib)
        self.renderers.append(renderer_matplotlib)

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

    def update(self):
        x = np.linspace(self.space.sizes[0][0], self.space.sizes[0][1], 50)
        y = np.linspace(self.space.sizes[1][0], self.space.sizes[1][1], 50)
        X, Y = np.meshgrid(x, y)

        fn = self.ui.functions.currentData()

        Z = fn(np.array([X, Y]))
        algo = self.ui.algorithm.currentData()()

        for w in self.renderers:
            w.update_plane(x, y, Z, self.space)


        options = {opt['name']: opt['transform'](self.option_widgets[opt['name']].text()) for opt in algo.options()}

        for w in self.renderers:
            w.update_points(algo.run(self.space, fn, options))

        self.ui.result.setText("f({arg}) = {val:.4f}".format(
            arg=", ".join(["{:.4f}".format(i) for i in algo.arg]),
            val=algo.min
        ))





ShaderProgram('normalColormy', [
    VertexShader("""
        varying vec3 normal;
        void main() {
            // compute here for use in fragment shader
            normal = normalize(gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
        }
    """),
    FragmentShader("""
        varying vec3 normal;
        void main() {
            vec4 color = gl_Color;
            color.x = (normal.x + 1.0) * 0.5;
            color.y = (normal.y + 1.0) * 0.5;
            color.z = (normal.z + 1.0) * 0.5;
            color.w = 0.7;
            gl_FragColor = color;
        }
    """)
]),

win = MainWindow()
win.setWindowTitle("cv:")
win.show()

app.exec_()