from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGridLayout


class StartPosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.label = QLabel()
        self.layout().addWidget(self.label)
        self.value = None

    def mouseReleaseEvent(self, evt):
        self.value = None
        self.label.setText("")


    def on_change(self, x, y):
        self.value = (x, y)
        self.label.setText(f"{x:.3f},{y:.3f}")

    def get_position(self):
        return self.value


class OptionWidget(QWidget):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.options = options
        self.option_widgets = {}
        self.setLayout(QGridLayout())

        for i, (name, option) in enumerate(options.items()):
            self.layout().addWidget(QLabel(name), i / 2, (i % 2)*2, 1, 1)
            widget = option.build_widget(self)
            widget.setObjectName(name)
            self.layout().addWidget(widget, i / 2, (i % 2)*2 + 1, 1, 1)
            self.option_widgets[name] = widget

    def get_options(self):
        return {name: option.get_value(self.option_widgets[name]) for name, option in self.options.items()}