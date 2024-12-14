import sys

from PyQt5.QtWidgets import *
import PyQt5
from qt_material import apply_stylesheet

class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Hello World")
        label = QLabel("Hello World")
        label.setMargin(10)
        self.setCentralWidget(label)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()

    apply_stylesheet(app, theme='dark_blue.xml')

    win.show()
    sys.exit(app.exec_())
