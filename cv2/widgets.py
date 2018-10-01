from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


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

    def text(self):
        return self.value