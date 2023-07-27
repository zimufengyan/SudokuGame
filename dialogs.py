import sys
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QDialog, QWidget
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QPainter, QBrush, QPolygon, QRegion

from Ui_new_game_confirm import Ui_NewGameConfirmDialog
from Ui_new_game import Ui_NewGameDialog
from Ui_gameover import Ui_GameOverDialog
from Ui_hint import Ui_HintDialog
from Ui_vectory import Ui_vectoryDialog
      
        
class NewGameConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.ui = Ui_NewGameConfirmDialog()
        self.ui.setupUi(self)
                
        self.result = True
        
        self.ui.okButton.clicked.connect(self.confirm)
        self.ui.cancelButton.clicked.connect(self.cancel)
                
    def confirm(self):
        self.log.debug('The OK button has been clicked, so accept.')
        if self.ui.checkBox.isChecked():
            self.log.debug('The checkbox has been checked.')
            self.result = False
        self.accept()
        
    def cancel(self):
        self.log.debug('The Cancel button has been clicked, so reject.')
        if self.ui.checkBox.isChecked():
            self.log.debug('The checkbox has been checked.')
            self.result = False
        self.reject()
             

class NewGameDialog(QDialog):
    def __init__(self, parent=None, is_center=False):
        super().__init__(parent, flags=Qt.FramelessWindowHint)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.ui = Ui_NewGameDialog()
        self.ui.setupUi(self)
        
        self.setModal(True)  # 设置为模态对话框
        self.setWindowModality(Qt.ApplicationModal)  
        
        if is_center is False:
            self.setDialogPosition()
        
        self.result = None
        
        self.ui.easyBtn.clicked.connect(self.close)
        self.ui.normalBtn.clicked.connect(self.close)
        self.ui.hardBtn.clicked.connect(self.close)
        self.ui.perfessionalBtn.clicked.connect(self.close)
        self.ui.extremeBtn.clicked.connect(self.close)
        self.ui.restartBtn.clicked.connect(self.close)
        self.ui.cancelBtn.clicked.connect(self.close)
        
    def setDialogPosition(self):
        parent_size = self.parent().geometry()
        dialog_size = self.geometry()
        x = parent_size.x() + 620
        y = parent_size.y() + 35
        self.setGeometry(x, y, dialog_size.width(), dialog_size.height())
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and obj == self.parentWidget():
            self.close()
            return True
        return super().eventFilter(obj, event)
        
    def closeEvent(self, event):
        sender = self.sender()
        if sender:
            name = sender.objectName()
            self.log.debug(f"The button of {name} has been clicked.")
            self.result = name[:-3]
        self.accept()
        
        
class GameOverDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.ui = Ui_GameOverDialog()
        self.ui.setupUi(self)
        
        self.setModal(True)  # 设置为模态对话框
        self.setWindowModality(Qt.ApplicationModal)  
        
        self.result = None
        
        self.ui.restoreBtn.clicked.connect(self.close)
        self.ui.newBtn.clicked.connect(self.close)
        
    def closeEvent(self, event) -> None:
        sender = self.sender()
        name = sender.objectName()
        self.log.debug(f"The button of {name} has been clicked.")
        self.result = name[:-3]
        self.accept()
        
        
class HintDialog(QDialog):
    onStyle = "border-radius:5px;background-color:#0072E3"
    offStyle = "border-radius:5px;background-color:#a8a8a8"
    def __init__(self, hint_content, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.ui = Ui_HintDialog()
        self.ui.setupUi(self)
        self.ui.progressLabel_1.setStyleSheet(self.onStyle)
        self.ui.progressLabel_2.setStyleSheet(self.offStyle)
        
        self.setDialogPosition()
        
        self.hint_content = hint_content
        
        self.setModal(True)  # 设置为模态对话框
        self.setWindowModality(Qt.ApplicationModal)  
        
        self.ui.okToolButton.setVisible(False)
        self.ui.leftToolButton.setVisible(False)
        self.ui.rightToolButton.clicked.connect(self.next_page)
        
    def setDialogPosition(self):
        parent_size = self.parent().geometry()
        dialog_size = self.geometry()
        x = parent_size.x() + 635
        y = parent_size.y() + 70
        self.setGeometry(x, y, dialog_size.width(), dialog_size.height())
        
    def next_page(self):
        # when rightToolButton has been clicked.
        self.ui.hintLabel.setText(f"此单元格只剩一个选项{self.hint_content}, \n因此只能填{self.hint_content}")
        self.ui.progressLabel_2.setStyleSheet(self.onStyle)
        self.ui.progressLabel_1.setStyleSheet(self.offStyle)
        self.ui.leftToolButton.setVisible(True)
        self.ui.okToolButton.setVisible(True)
        self.ui.leftToolButton.clicked.connect(self.last_page)
        self.ui.okToolButton.clicked.connect(self.close)
        
    def last_page(self):
        self.ui.hintLabel.setText('留意这个单元格及突出显示区域')
        self.ui.progressLabel_1.setStyleSheet(self.onStyle)
        self.ui.progressLabel_2.setStyleSheet(self.offStyle)
        self.ui.okToolButton.setVisible(False)
        self.ui.leftToolButton.setVisible(False)
        
        
class VectoryDialog(QDialog):
    def __init__(self, parent=None, **params):
        super().__init__(parent, flags=Qt.FramelessWindowHint)
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.ui = Ui_vectoryDialog()
        self.ui.setupUi(self)
        
        self.ui.levelLabel.setText(params.get('level', '简单'))
        self.ui.timerLabel.setText(params.get('timer'))
        
        self.ui.NewBtn.clicked.connect(self.close)
        