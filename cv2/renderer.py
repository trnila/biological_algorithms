import pyqtgraph.opengl as gl
import numpy as np
from PyQt5 import QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib import cm
import colorsys


class OpenglRenderer(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.scale = (1, 1, 1)
        self.setMinimumSize(200, 200)
        self.setCameraPosition(distance=50)

        g = gl.GLGridItem()
        g.scale(1, 1, 1)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.addItem(g)

        self.surface_plot = gl.GLSurfacePlotItem(shader='normalColormy')
        self.surface_plot.setGLOptions('translucent')
        self.addItem(self.surface_plot)

        self.points = gl.GLScatterPlotItem(size=0.5, pxMode=False)
        self.points.hide()
        self.points.setGLOptions('additive')
        self.addItem(self.points)

    def update_plane(self, X, Y, Z, space):
        delta = np.max(Z) - np.min(Z)
        if delta:
            self.scale = (1, 1, 10 / delta)
        else:
            self.scale = (1, 1, 1)

        colors = []
        for x, _ in enumerate(X):
            for y, _ in enumerate(Y):
                delta = np.max(Z)

                val = 0 if delta == 0 else Z[x,y] / delta
                (r, g, b) = colorsys.hsv_to_rgb(val, 1.0, 1.0)
                colors.append((r, g, b, 1))

        self.surface_plot.resetTransform()
        self.surface_plot.scale(*self.scale)
        self.surface_plot.rotate(90, 0, 0, 1)
        self.surface_plot.setData(X, Y, Z, colors=colors)

    def update_points(self, points):
        if len(points) <= 0:
            self.points.hide()
            return

        self.points.show()

        available_colors = [
            (1, 0, 0, 1),
            (0, 1, 0, 1),
            (0, 0, 1, 1),
            (1, 1, 0, 1),
            (0, 1, 1, 1),
            (1, 0, 1, 1),
            (1, 1, 1, 1),
            (0, 0, 0, 1),
        ]
        c = 0
        all_points = []
        colors = []
        for point_group in points:
            for point in point_group.points:
                all_points.append(point.to_vec())
                colors.append(available_colors[c])
            c = (c + 1) % len(available_colors)

        self.points.resetTransform()
        self.points.scale(*self.scale)
        self.points.setData(pos=np.array(all_points), color=np.array(colors))


class MatplotlibRenderer(FigureCanvas):
    position_changed = QtCore.pyqtSignal(float, float)

    def __init__(self):
        super().__init__(Figure())

        self.ax = self.figure.add_subplot(121, projection='3d')
        self.nn = self.figure.add_subplot(122)

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
            self.position_changed.emit(event.xdata, event.ydata)

        self.mpl_connect('button_press_event', onclick)

    def update_plane(self, X, Y, Z, space):
        X, Y = np.meshgrid(X, Y)

        self.ax.clear()
        self.ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.inferno, linewidth=0, antialiased=True, alpha=0.5)

        self.nn.clear()
        self.nn.imshow(Z, extent=np.array(space.sizes).flatten())

        self.draw_idle()

    def update_points(self, points):
        colors = ['red', 'green', 'blue', 'purple', 'yellow']
        color = 0
        for points in points:
            for point in points:
                self.ax.scatter(*point, color=colors[color])
                self.nn.scatter(point[0], point[1], color=colors[color], s=20, edgecolor='black')

            color = (color + 1) % len(colors)

        self.draw_idle()

