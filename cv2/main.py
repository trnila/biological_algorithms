import sys

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
import matplotlib.pyplot as plt
import renderer
import ui_main_window
import utils
from ipython import ConsoleWidget
from simulation import Simulation
from utils import Space, MeasureContext
from widgets import OptionWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.space = Space(2 * [[-6, 6]])
        self.renderers = []
        self.simulation = None
        self.algorithm_option_widgets = {}

        self.ui = ui_main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        for fn in utils.all_functions():
            self.ui.functions.addItem(fn.__name__, fn)

        for algo in utils.all_algorithms():
            self.ui.algorithm.addItem(algo.__name__, algo)
            widget = OptionWidget(self, algo().options())
            widget.hide()
            self.algorithm_option_widgets[algo.__name__] = widget
            self.ui.algorithmOptions.addWidget(widget)

        self.ui.functions.currentIndexChanged.connect(self.refresh)
        self.ui.algorithm.currentIndexChanged.connect(self.refresh)
        self.ui.startBtn.clicked.connect(self.refresh)
        self.ui.finishBtn.clicked.connect(lambda: self.step_by(sys.maxsize))
        self.ui.stepBtn.clicked.connect(lambda: self.step_by(1))
        self.ui.stepBackBtn.clicked.connect(lambda: self.step_by(-1))
        self.ui.autoplay.toggled.connect(self.autoplay_clicked)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.autoplay_next)

        self.console = ConsoleWidget()
        self.console.execute("%matplotlib inline")
        self.console.push_vars({
            'np': np,
            'plt': plt,
        })
        self.ui.tab_3.layout().addWidget(self.console)

        self.setup_renderers()
        self.refresh()

    def autoplay_clicked(self, autoplay):
        if not autoplay:
            self.animation_timer.stop()
        else:
            if self.simulation.is_end():
                self.simulation.set_step(1)
            self.animation_timer.start(100)

    def autoplay_next(self):
        self.step_by()

        if self.simulation.is_end():
            self.animation_timer.stop()
            self.ui.autoplay.setChecked(False)

    def setup_renderers(self):
        renderer_opengl = renderer.OpenglRenderer()
        self.ui.tab.layout().addWidget(renderer_opengl)
        self.renderers.append(renderer_opengl)

        self.renderer_matplotlib = renderer.MatplotlibRenderer()
        self.ui.tab_2.layout().addWidget(self.renderer_matplotlib)
        #self.renderers.append(self.renderer_matplotlib)

    def measure(self, name):
        return MeasureContext(name)

    def refresh(self):
        self.update_algo()
        self.update_fn()
        self.start_simulation()
        self.step_by(0)


    @pyqtSlot()
    def update_algo(self):
        algo = self.ui.algorithm.currentData()()

        for widget in self.algorithm_option_widgets.values():
            widget.hide()

        self.algorithm_option_widgets[type(algo).__name__].show()

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

        options = self.algorithm_option_widgets[type(algo).__name__].get_options()
        options['min'] = self.ui.minMax.currentText() == 'min'
        self.simulation = Simulation(self.space, algo, fn, options)

    def step_by(self, count=1):
        self.simulation.step_by(count)

        points = self.simulation.get_points()
        for w in self.renderers:
            with self.measure(f"update_points on {w.__class__.__name__}"):
                w.update_points(points, self.ui.last_state.isChecked())

        self.ui.result.setText("f({arg}) = {val:.4f}; cost fn called {called}x".format(
            arg=", ".join(["{:.4f}".format(i) for i in self.simulation.current_step().best.arg]),
            val=self.simulation.current_step().best.cost,
            called=self.simulation.current_step().cost_fn_called,
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


app = QApplication([])

win = MainWindow()
win.setWindowTitle("cv:")
win.show()

app.exec_()