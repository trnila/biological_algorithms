from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
import numpy as np

from widgets import StartPosWidget


class AlgorihmOption:
    def build_widget(self, app):
        raise NotImplementedError

    def get_value(self, widget):
        raise NotImplementedError


class IntOption(AlgorihmOption):
    def __init__(self, default=0, min=0, max=100):
        self.default = default
        self.min = min
        self.max = max

    def build_widget(self, app):
        widget = QSpinBox()
        widget.setMinimum(self.min)
        widget.setMaximum(self.max)
        widget.setValue(self.default)
        return widget

    def get_value(self, widget):
        return int(widget.text())


class FloatOption(AlgorihmOption):
    def __init__(self, default=0, min=0, max=100):
        self.default = default
        self.min = min
        self.max = max

    def build_widget(self, app):
        widget = QDoubleSpinBox()
        widget.setMinimum(self.min)
        widget.setMaximum(self.max)
        widget.setDecimals(10)
        widget.setValue(self.default)
        return widget

    def get_value(self, widget):
        return float(widget.text())


class StartPositionOption(AlgorihmOption):
    def build_widget(self, app):
        widget = StartPosWidget()
        app.renderer_matplotlib.position_changed.connect(widget.on_change)
        return widget

    def get_value(self, widget):
        return widget.get_position()