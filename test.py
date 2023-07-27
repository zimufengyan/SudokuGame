from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QApplication, QMainWindow, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QRect, QEvent
from PyQt5.QtGui import QColor, QPainter, QBrush, QPolygon, QRegion


class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint)

        layout = QVBoxLayout()

        self.custom_button1 = QPushButton("Custom Button 1")
        self.custom_button2 = QPushButton("Custom Button 2")

        layout.addWidget(self.custom_button1)
        layout.addWidget(self.custom_button2)

        self.setLayout(layout)

        self.custom_button1.clicked.connect(self.on_custom_button1_clicked)
        self.custom_button2.clicked.connect(self.on_custom_button2_clicked)

        self.result = None

    def on_custom_button1_clicked(self):
        self.result = "Custom Button 1"
        self.close()

    def on_custom_button2_clicked(self):
        self.result = "Custom Button 2"
        self.close()

    def closeEvent(self, event):
        if self.result is None:
            self.result = "Dialog Closed"
        event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and obj == self.parentWidget():
            self.close()
            return True
        return super().eventFilter(obj, event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button = QPushButton("Open Dialog")
        self.button.clicked.connect(self.show_dialog)

        self.setCentralWidget(self.button)

    def show_dialog(self):
        dialog = MyDialog(self)
        dialog.installEventFilter(dialog)
        dialog.exec_()

        result = dialog.result
        if result == "Custom Button 1":
            # 执行自定义按钮1被按下后的操作
            pass
        elif result == "Custom Button 2":
            # 执行自定义按钮2被按下后的操作
            pass
        else:
            # 执行对话框被关闭后的操作
            pass

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
