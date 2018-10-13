import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from pyqtgraph.opengl.shaders import ShaderProgram, VertexShader, FragmentShader

import renderer
import ui_main_window
import utils
from ipython import ConsoleWidget
from utils import Space, MeasureContext


class Simulation:
    def __init__(self, space, algo, fn, options):
        self.step = 1
        self.algo = algo
        self.fn = fn
        self.options = options
        self.space = space

        cost_fn = utils.CountCallsProxy((lambda X: -fn(X)) if not options['min'] else fn)
        self.steps = list(algo.run(self.space, cost_fn, options))
        self.cost_fn_called = cost_fn.called_count

    @property
    def max_steps(self):
        return len(self.steps) - 1

    def step_by(self, n):
        self.step = max(1, min(self.max_steps, self.step + n))

    def step_forward(self):
        self.step_by(1)

    def step_back(self):
        self.step_by(-1)

    def current_step(self):
        return self.steps[self.step]

    def get_points(self):
        return self.steps[0:self.step]


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.space = Space(2 * [[-6, 6]])
        self.renderers = []
        self.simulation = None

        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        for fn in utils.all_functions():
            self.ui.functions.addItem(fn.__name__, fn)

        for algo in utils.all_algorithms():
            self.ui.algorithm.addItem(algo.__name__, algo)

        self.ui.functions.currentIndexChanged.connect(self.refresh)
        self.ui.algorithm.currentIndexChanged.connect(self.refresh)
        self.ui.startBtn.clicked.connect(self.refresh)
        self.ui.finishBtn.clicked.connect(lambda: self.step_by(sys.maxsize))
        self.ui.stepBtn.clicked.connect(lambda: self.step_by(1))
        self.ui.stepBackBtn.clicked.connect(lambda: self.step_by(-1))

        self.console = ConsoleWidget()
        self.console.execute("%matplotlib inline")
        self.console.push_vars({
            'np': np,
            'plt': plt,
        })
        self.ui.tab_3.layout().addWidget(self.console)

        self.setup_renderers()
        self.refresh()

    def setup_renderers(self):
        renderer_opengl = renderer.OpenglRenderer()
        self.ui.tab.layout().addWidget(renderer_opengl)
        self.renderers.append(renderer_opengl)

        self.renderer_matplotlib = renderer.MatplotlibRenderer()
        self.ui.tab_2.layout().addWidget(self.renderer_matplotlib)
        #self.renderers.append(self.renderer_matplotlib)

    def measure(self, name):
        return MeasureContext(name)

    def remove(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def refresh(self):
        self.update_algo()
        self.update_fn()
        self.start_simulation()
        self.step_by(0)


    @pyqtSlot()
    def update_algo(self):
        algo = self.ui.algorithm.currentData()()
        self.option_widgets = {}
        self.remove(self.ui.gridLayout_2)
        for i, (name, option) in enumerate(algo.options().items()):
            self.ui.gridLayout_2.addWidget(QLabel(name), i / 2, (i % 2)*2, 1, 1)
            widget = option.build_widget(self)
            widget.setObjectName(name)
            self.ui.gridLayout_2.addWidget(widget, i / 2, (i % 2)*2 + 1, 1, 1)
            self.option_widgets[name] = widget

    @pyqtSlot()
    def update_fn(self):
        with self.measure("generate space"):
            x = np.linspace(self.space.sizes[0][0], self.space.sizes[0][1], 50)
            y = np.linspace(self.space.sizes[1][0], self.space.sizes[1][1], 50)
            X, Y = np.meshgrid(x, y)

            fn = self.ui.functions.currentData()
            Z = fn(np.array([X, Y]))

        for w in self.renderers:
            with self.measure(f"update_plane on {w.__class__.__name__}"):
                w.update_plane(x, y, Z, self.space)

    @pyqtSlot()
    def start_simulation(self):
        algo = self.ui.algorithm.currentData()()
        fn = self.ui.functions.currentData()

        options = {name: option.get_value(self.option_widgets[name]) for name, option in algo.options().items()}
        options['min'] = self.ui.minMax.currentText() == 'min'
        self.simulation = Simulation(self.space, algo, fn, options)

    def step_by(self, count=1):
        self.simulation.step_by(count)

        points = self.simulation.get_points()
        for w in self.renderers:
            with self.measure(f"update_points on {w.__class__.__name__}"):
                w.update_points(points)

        self.ui.result.setText("f({arg}) = {val:.4f}; cost fn called {called}x".format(
            arg=", ".join(["{:.4f}".format(i) for i in self.simulation.current_step().best.arg]),
            val=self.simulation.current_step().best.cost,
            called=self.simulation.cost_fn_called,
        ))

        np_points = np.array(points)
        self.console.push_vars({
            'points': np_points,
            #            'values': np_points.reshape(2000, 3)[:, 2],
            'fn': self.simulation.fn,
        })

        self.ui.stepLabel.setText(f"{self.simulation.step}/{self.simulation.max_steps}")

    def fill_z(self, groups, fn):
        for group in groups:
            points_in_group = []
            for point in group:
                points_in_group.append((*point, fn(point)))
            yield points_in_group



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
        
            color.w = 0.7;
            gl_FragColor = color;
        }
    """)
]),

app = QApplication([])

win = MainWindow()
win.setWindowTitle("cv:")
win.show()

app.exec_()