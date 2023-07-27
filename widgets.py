from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging



class MyButton(QPushButton):
    key_signal = pyqtSignal(str)    # Button捕获到键盘输入发出该信号，参数为输入内容
    def __init__(self, *params):
        super().__init__(*params)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
    def keyPressEvent(self, event) -> None:
        if (event.key() == Qt.Key_1):
            self.log.info('The key 1 has been pressed.')
            # self.setText('1')
            self.key_signal.emit('1')
            self.log.info('The text of the button has been changed to 1.')
        elif (event.key() == Qt.Key_2):
            self.log.info('The key 2 has been pressed.')
            # self.setText('2')
            self.key_signal.emit('2')
            self.log.info('The text of the button has been changed to 2.')
        elif (event.key() == Qt.Key_3):
            self.log.info('The key 3 has been pressed.')
            # self.setText('3')
            self.key_signal.emit('3')
            self.log.info('The text of the button has been changed to 3.')
        elif (event.key() == Qt.Key_4):
            self.log.info('The key 4 has been pressed.')
            # self.setText('4')
            self.key_signal.emit('4')
            self.log.info('The text of the button has been changed to 4.')
        elif (event.key() == Qt.Key_5):
            self.log.info('The key 5 has been pressed.')
            # self.setText('5')
            self.key_signal.emit('5')
            self.log.info('The text of the button has been changed to 5.')
        elif (event.key() == Qt.Key_6):
            self.log.info('The key 6 has been pressed.')
            # self.setText('6')
            self.key_signal.emit('6')
            self.log.info('The text of the button has been changed to 6.')
        elif (event.key() == Qt.Key_7):
            self.log.info('The key 7 has been pressed.')
            # self.setText('7')
            self.key_signal.emit('7')
            self.log.info('The text of the button has been changed to 7.')
        elif (event.key() == Qt.Key_8):
            self.log.info('The key 8 has been pressed.')
            # self.setText('8')
            self.key_signal.emit('8')
            self.log.info('The text of the button has been changed to 8.')
        elif (event.key() == Qt.Key_9):
            self.log.info('The key 9 has been pressed.')
            # self.setText('9')
            self.key_signal.emit('9')
            self.log.info('The text of the button has been changed to 9.')
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            self.log.info('The key Delete/Backspace has been pressed.')
            # self.setText('')
            self.log.info('The text of the button has been erased.')
            
            
class MaskWidget(QWidget):
    def __init__(self, parent=None):
        super(MaskWidget, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRect(self.rect())
            
            
            