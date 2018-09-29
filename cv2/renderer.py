import pyqtgraph.opengl as gl
import numpy as np
from PyQt5.QtWidgets import QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib import cm


class OpenglRenderer(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        
        self.setMinimumSize(200, 200)
        self.setCameraPosition(distance=50)


        ## Add a grid to the view
        g = gl.GLGridItem()
        g.scale(1, 1, 1)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.addItem(g)


        p2 = gl.GLSurfacePlotItem(shader='normalColormy')
        p2.setGLOptions('translucent')
        self.addItem(p2)
        self.p2 = p2

        sp1 = gl.GLScatterPlotItem(pos=np.array([]), size=0.1, pxMode=False, color=(1, 1, 1, 1))
        #sp1.setGLOptions('translucent')
        sp1.setGLOptions('additive')
        self.addItem(sp1)
        self.sp1 = sp1

    def update_plane(self, X, Y, Z, space):
        self.p2.setData(X, Y, Z)

    def update_points(self, points):
        all_points = []
        for point_group in points:
            for point in point_group:
                all_points.append(point)


        self.sp1.setData(pos=np.array(all_points))


class MatplotlibRenderer(FigureCanvas):
    def __init__(self):
        super().__init__(Figure())

        self.ax = self.figure.add_subplot(121, projection='3d')
        self.nn = self.figure.add_subplot(122)

        def onclick(event):
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

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

