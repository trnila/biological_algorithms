from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, \
    QSpinBox, QDoubleSpinBox
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

import types
from pyqtgraph.opengl.shaders import ShaderProgram, VertexShader, FragmentShader

import algorithms
import renderer
import test_functions
import ui_main_window
from utils import Space, MeasureContext


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.space = Space(2 * [[-6, 6]])
        self.renderers = []

        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        for fn in [getattr(test_functions, fn) for fn in dir(test_functions) if isinstance(getattr(test_functions, fn), types.FunctionType)]:
            self.ui.functions.addItem(fn.__name__, fn)

        self.ui.algorithm.addItem("blind", algorithms.BlindSearch)
        self.ui.algorithm.addItem("simulated anneling", algorithms.Anneling)
        self.ui.algorithm.addItem("climbing search", algorithms.ClimbingSearch)
        #self.ui.algorithm.addItem("test grid", algorithms.GridAlgorithm)

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

        self.renderer_matplotlib = renderer.MatplotlibRenderer()
        self.ui.tab_2.layout().addWidget(self.renderer_matplotlib)
        self.renderers.append(self.renderer_matplotlib)

    def measure(self, name):
        return MeasureContext(name)

    def remove(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

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

    def update(self):
        with self.measure("generate space"):
            x = np.linspace(self.space.sizes[0][0], self.space.sizes[0][1], 50)
            y = np.linspace(self.space.sizes[1][0], self.space.sizes[1][1], 50)
            X, Y = np.meshgrid(x, y)

            fn = self.ui.functions.currentData()
            Z = fn(np.array([X, Y]))

        algo = self.ui.algorithm.currentData()()

        for w in self.renderers:
            with self.measure(f"update_plane on {w.__class__.__name__}"):
                w.update_plane(x, y, Z, self.space)

        options = {name: option.get_value(self.option_widgets[name]) for name, option in algo.options().items()}
        cost_fn = (lambda X: -fn(X)) if self.ui.minMax.currentText() == 'max' else fn
        points = list(self.fill_z(algo.run(self.space, cost_fn, options), fn))

        for w in self.renderers:
            with self.measure(f"update_points on {w.__class__.__name__}"):
                w.update_points(points)

        self.ui.result.setText("f({arg}) = {val:.4f}".format(
            arg=", ".join(["{:.4f}".format(i) for i in algo.arg]),
            val=fn(algo.arg)
        ))

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