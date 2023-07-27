import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QApplication
from PyQt5.QtWidgets import QMainWindow, QUndoCommand, QUndoStack, QDialog
from PyQt5.QtCore import *
import logging
from copy import deepcopy
from collections import deque

from basic import *
from generator import SudokuGenerator
from solver import SudokuSolver
from config import Config
from widgets import MaskWidget
from Ui_Sudoku_v1 import Ui_Sudoku
from dialogs import *


class Window(QMainWindow):
    over = pyqtSignal(int)    # whether the current game is over, 0 representing lose, and 1 representing victory.
    
    def __init__(self):
        super().__init__()
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
        self.config = Config()
        self.level = 'easy' # easy, normal, hard, perfessional, extreme
        self.time_sonsumed = 0  
        self.target_loc = (1, 1)  # location of the currently selected grid, starts from 1, with a default value of (1, 1) 
        self.errors = 0
        self.errors_set = []
        self.hint_limitation = self.config.hint_limitation    # limitations on the number of hints.
        self.mode = 'normal' # normal or hint
        self.is_pause = True       # Whether the game is paused.
        
        self.sudoku = None
        self.initial_sudoku = None      # a copy of initial sudoku
        self.sudoku_generator = None
        self.answer = None
        
        self.timer = QTimer(self)
        self.undoStack = QUndoStack()
        self.undoStack.setUndoLimit(10)  # sets the limit of undo operations to 10.
        self.stack = deque()    # record the process of filling grids.
        
        self.confirm_query = True      # Whether to stop the query when the level will be changed.
        
        self.ui = Ui_Sudoku()
        self.ui.setupUi(self)
        
        self.mask_widget = MaskWidget(self) 
        self.mask_widget.setGeometry(self.geometry())
        self.hide_mask()
        
        self.connect()
        self.get_sudoku()
        self.showGame()
        
    def get_sudoku(self):
        self.sudoku_generator = SudokuGenerator()
        self.sudoku = self.sudoku_generator.generate(level=self.level)
        self.initial_sudoku = deepcopy(self.sudoku)
        self.answer = SudokuSolver(sudoku=self.sudoku).solve()
        
    def showGame(self):
        # initialize and show the sudoku game.
        for i in range(1, 10):
            for j in range(1, 10):
                btn = self.find_target_btn((i, j))
                value = self.sudoku[i-1, j-1]
                if value == 0:
                    btn.setText('')
                else:
                    btn.setText(str(value))
        self.log.info("The game has been initialized.")
        
        # start the timer 
        self.timer.start(1000)  # send signal of timeout per 1000 ms (i.e., 1 second).
        self.initUi() 
        
    def initUi(self):
        # initialize the value of certain widgets.
        self.time_sonsumed = 0
        self.errors = 0
        self.errors_set.clear()
        self.hint_limitation = self.config.hint_limitation
        self.ui.label_hint_limitation.setText(str(self.hint_limitation))
        self.is_pause = True
        self.update_errors()
        
        self.ui.label_hint_limitation.setText(str(self.hint_limitation))
        
        # simulate a click on button gird_btn_1 and let it get a focus.
        self.ui.gird_btn_1.click()
        self.ui.gird_btn_1.setFocus()
        # simulate a click on StartPauseBtn
        self.ui.StartPauseBtn.click() 
        
    def update_errors(self):
        error_text = self.config.error_platfrom.format(self.errors, self.config.errors_limitation)
        self.ui.label_error.setText(error_text)
        # Determines whether the number of errors has reached the upper limit, and handle. 
        if self.errors == self.config.errors_limitation:
            self.over.emit(0)
        
    def connect(self):
        self.timer.timeout.connect(self.show_time)
        for i in range(1, 10):
            btn = self.ui.centralwidget.findChild(QPushButton, f'Btn_{i}')
            btn.clicked.connect(self.btn_number_clicked)
        for i in range(1, 82):
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{i}')
            btn.clicked.connect(self.btn_grid_clicked)
            btn.key_signal.connect(self.fill_operation)
        self.ui.ClearBtn.clicked.connect(self.erase)
        self.ui.BackBtn.clicked.connect(self.undo_operation)
        self.ui.HintBtn.clicked.connect(self.hint)
        self.ui.NewBtn.clicked.connect(self.new_game)
        self.ui.StartPauseBtn.clicked.connect(self.btn_pause_clicked)
        self.ui.BtnBigStart.clicked.connect(self.btn_pause_clicked)
        self.ui.btn_easy.clicked.connect(self.set_level)
        self.ui.btn_normal.clicked.connect(self.set_level)
        self.ui.btn_hard.clicked.connect(self.set_level)
        self.ui.btn_perfessional.clicked.connect(self.set_level)
        self.ui.btn_extreme.clicked.connect(self.set_level)
        
        self.over.connect(self.handle_over)
        
    def undo_operation(self):
        self.log.info(f"sudoku before undo:\n {self.sudoku}")
        self.undoStack.undo()
        self.log.info(f"sudoku after undo:\n {self.sudoku}")
        
    def fill_operation(self, value):
        if self.target_loc is not None:
            # if existing a grid was chose.
            r, c = self.target_loc
            target_idx = (r - 1) * 9 + (c - 1) + 1
            target_btn  = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{target_idx}')
            self.undoStack.push(FillGrid(target_btn, value, self.log, self.stack, r, c, self.sudoku))
            self.log.info(f'The value of button located in {(r, c)} has been changed to {value}.')
            is_valid = self.validation(r, c, value)
            if is_valid:
                target_btn.setStyleSheet(self.config.valid_target_btn_style)
                # determine whether this game is over, and handle.
                if np.array_equal(self.sudoku, self.answer):
                    self.over.emit(1)
            else:
                target_btn.setStyleSheet(self.config.error_target_btn_style)
                self.errors += 1
                self.errors_set.append(target_btn)
                self.update_errors()
                self.sudoku[r-1, c-1] = 0
        
    def hint(self):
        self.mode = 'hint'
        self.timer.stop()
        # give a hint if player clicked the hint button.
        # TODO: implement the hint function, pointing out the least remaining grid. 
        self.hint_limitation -= 1
        if self.hint_limitation >= 0:
            self.log.info(f"The hint button has been clicked, and {self.hint_limitation} hints left.")
            self.ui.label_hint_limitation.setText(str(self.hint_limitation))
            target_btn = self.find_target_btn()
            if target_btn in self.errors_set:
                # correct the error.
                r, c = self.target_loc
                val = self.answer[r-1, c-1]
                self.sudoku[r-1, c-1] = val
                target_btn.setText(str(val))
                self.errors_set.remove(target_btn)
                self.log.info("The error has been corrected.")
            else:
                solver = SudokuSolver(sudoku=self.sudoku)
                state = solver.update_state()
                r, c, remaining = solver.get_least_remaining(state)
                self.log.info(f"The least remaining grid located in {(r+1, c+1)} has been found and its remaining is {remaining}.")
                val = remaining[0]
                # focus on the least remaining grid.
                target_btn = self.find_target_btn((r+1, c+1))
                if target_btn: target_btn.click()
                
                dialog = HintDialog(val, self)
                dialog.exec_()
                target_btn.setText(str(val))
                self.sudoku[r, c] = int(val)
                
            target_btn.setStyleSheet(self.config.valid_target_btn_style)
                
            if np.array_equal(self.sudoku, self.answer):
                self.over.emit(1)
        else:
            self.log.info(f"no hints left.")    
        
        self.timer.start()
        
    def erase(self):
        # erase the text of target button.
        if self.target_loc is not None:
            r, c = self.target_loc
            target_btn = self.find_target_btn()
            if target_btn is not None:
                self.undoStack.push(FillGrid(target_btn, '', self.log, self.stack))
                self.log.info(f'The value of button located in {(r, c)} has been erased.')
                self.sudoku[r-1, c-1] = 0
                
    def is_over(self) -> bool:
        # Determines if the game is over.
        # TODO: implements this
        pass
            
    def validation(self, row ,col, content: str) -> bool:
        # TODO: complete the validation for valid input in sudoku.  
        ans = self.answer[row-1, col-1]
        if content == str(ans):
            self.log.info('The input is valid.')
            return True
        else:
            self.log.warning('The input is invalid.')
            return False
            
    def btn_grid_clicked(self):
        sender = self.sender()
        name = str(sender.objectName())
        index = int(name.split(sep='_')[-1])
        self.log.info(f'The button {name} hase been clicked.')
        
        row, col = calculate_row_column(index)
        self.target_loc = (row, col)
        self.log.info(f'The button clicked is located in ({row}, {col}).')
        self.change_style()
        
    def change_style(self):
        if self.target_loc is None:
            return
        row, col = self.target_loc
        
        # firstly, clear all style
        for i in range(1, 82):
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{i}')
            if btn is not None:
                btn.setStyleSheet(self.config.btn_style)
            
        # Secondly, change the style of wrong grid.
        for btn in self.errors_set:
            btn.setStyleSheet(self.config.error_btn_style)
            
        # Changes the style of the entire row, column, and nine-cell grid in which the selected grid is located.
        start = (row - 1) * 9 + 1
        for i in range(start, start + 9):
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{i}')
            if btn in self.errors_set:
                btn.setStyleSheet(self.config.error_part_btn_style)
            elif btn is not None:
                btn.setStyleSheet(self.config.part_btn_style)
        for i in range(col, 82, 9):
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{i}')
            if btn in self.errors_set:
                btn.setStyleSheet(self.config.error_part_btn_style)
            elif btn is not None:
                btn.setStyleSheet(self.config.part_btn_style)
        subgrid_indices = get_subgrid_indices(row, col)
        for i, j in subgrid_indices:
            idx = (i - 1) * 9 + j
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{idx}')
            if btn in self.errors_set:
                btn.setStyleSheet(self.config.error_part_btn_style)
            elif btn is not None:
                btn.setStyleSheet(self.config.part_btn_style)
        target_btn = self.find_target_btn()
        if self.mode == 'hint':
            self.log.info("change style of the target button under the mode of hint.")
            target_btn.setStyleSheet(self.config.hint_target_btn_style)
            self.mode = 'normal'
        elif target_btn in self.errors_set:
            target_btn.setStyleSheet(self.config.error_target_btn_style)
        elif target_btn is not None:
            target_btn.setStyleSheet(self.config.target_btn_style)
        
    def new_game(self, is_center=False):
        # when the NewBtn has benn clicked.
        self.timer.stop()
        dialog = NewGameDialog(self, is_center=is_center)
        self.show_mask()
        dialog.installEventFilter(dialog)
        dialog.exec_()
        self.hide_mask()
        
        result = dialog.result
        if result in self.config.level_set:
            # start a new game 
            self.confirm_query = False
            target_btn = self.ui.centralwidget.findChild(QPushButton, f'btn_{result}')
            target_btn.click()
            self.confirm_query = True
            self.log.debug(f"Start a new game with level of '{result}'.")
        elif result == 'restart':
            # reset this game
            self.sudoku = deepcopy(self.initial_sudoku)
            self.showGame()
            self.log.debug("The current game has been reseted.")
        else:
            # continue this game
            self.timer.start()
    
    def handle_over(self, val):
        self.timer.stop()
        if val == 0:
            # lose
            dialog = GameOverDialog(self)
            self.show_mask()
            dialog.ui.errorLabel.setText(f"你出现了{self.errors}个错误，游戏失败")
            dialog.exec_()
            self.hide_mask()
            
            if dialog.result == 'restore':
                # second change
                self.config.errors_limitation += 1
                self.timer.start()
            else:
                # start a new game
                self.new_game(is_center=True)
            self.update_errors()
        else:
            # vectory
            level = self.config.level_dict.get(self.level)
            timer = time_conversion(self.time_sonsumed)
            dialog = VectoryDialog(self, timer=timer, level=level)
            self.show_mask()
            dialog.exec_()
            self.hide_mask()
            
            # start a new game
            self.new_game(is_center=True)
            
    def find_target_btn(self, target_loc=None):
        if target_loc is not None:
            row, col = target_loc
        elif self.target_loc is not None:
            row, col = self.target_loc
        else:
            return None
        target_idx = (row - 1) * 9 + (col - 1) + 1
        target_btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{target_idx}')
        return target_btn
        
    def btn_number_clicked(self):
        sender = self.sender()
        name = str(sender.objectName())
        value = str(name.split('_')[-1])
        self.log.info(f"Button {name} has been clicked.")
        self.fill_operation(value)
        
    def btn_pause_clicked(self):
        self.is_pause = not self.is_pause
        if self.is_pause is True:
            # pause the game.
            self.log.info("The pause button has been clicked and then the game will be paused.")
            # modify the button's icon
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/res/start_grey.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.StartPauseBtn.setIcon(icon)
            # show the big start button
            self.ui.BtnBigStart.setVisible(True)
            # lock other widgets
            self.lock(is_lock=True)
            # pause the timer
            self.timer.stop()
            pass
        else:
            self.log.info("The start button has been clicked and then the game will be started.")
            # when the game is not paused.
            # modify the button's icon
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/res/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.StartPauseBtn.setIcon(icon)
            # hide the big start button
            self.ui.BtnBigStart.setVisible(False)
            # unlock other widgets
            self.lock(is_lock=False)
            # start the timer
            self.timer.start()
        
    def lock(self, is_lock=True):
        for i in range(1, 10):
            btn = self.ui.centralwidget.findChild(QPushButton, f'Btn_{i}')
            btn.setEnabled(not is_lock)
        for i in range(1, 82):
            btn = self.ui.centralwidget.findChild(QPushButton, f'gird_btn_{i}')
            btn.setEnabled(not is_lock)
        self.ui.BackBtn.setEnabled(not is_lock)
        self.ui.ClearBtn.setEnabled(not is_lock)
        self.ui.HintBtn.setEnabled(not is_lock)
        self.ui.NewBtn.setEnabled(not is_lock)
        self.ui.btn_easy.setEnabled(not is_lock)
        self.ui.btn_normal.setEnabled(not is_lock)
        self.ui.btn_hard.setEnabled(not is_lock)
        self.ui.btn_perfessional.setEnabled(not is_lock)
        self.ui.btn_extreme.setEnabled(not is_lock)
        
    def show_mask(self):
        self.mask_widget.show()
        opacity_effect = QGraphicsOpacityEffect(self.mask_widget)
        opacity_effect.setOpacity(0.8)
        self.mask_widget.setGraphicsEffect(opacity_effect)
        self.log.debug("show the mask widget.")

        mask_position = QPoint(0, 0)
        self.mask_widget.move(mask_position)
        
    def hide_mask(self):
        self.mask_widget.hide()
        self.log.debug("hide the mask widget.")
        
    def set_level(self):
        sender = self.sender()
        name = sender.objectName()
        
        if self.confirm_query == True:
            self.log.info(f"The button of {name} has been clicked and the property of 'confirm_query' is {self.confirm_query}, "
                          "so show the confirming dialog.")
            # show the confirm dialog.
            dialog = NewGameConfirmDialog(self)
            self.timer.stop()
            self.show_mask()
            
            if dialog.exec_() == QDialog.Accepted:
                self.level = name.split('_')[-1] 
                self.log.info(f"The OK button has been clicked. And then switches to {self.level} lrvel.")
                
                self.ui.btn_easy.setStyleSheet(self.config.level_btn_style)
                self.ui.btn_normal.setStyleSheet(self.config.level_btn_style)
                self.ui.btn_hard.setStyleSheet(self.config.level_btn_style)
                self.ui.btn_perfessional.setStyleSheet(self.config.level_btn_style)
                self.ui.btn_extreme.setStyleSheet(self.config.level_btn_style)
                
                # update the property of confirm_query
                self.confirm_query = dialog.result
                self.log.debug(f'Now, the new value of property of "confirm_query" is {self.confirm_query}.')
                
                # restart and reshow a new game.
                self.get_sudoku()
                self.showGame()
                sender.setStyleSheet(self.config.level_target_btn_style)
            else:
                self.log.info(f"The Cancel button has been clicked. And then cancel this operation.")
                self.timer.start()
            
            self.hide_mask()
        else:
            self.level = name.split('_')[-1]
            self.log.info(f"The property of 'confirm_query' is {self.confirm_query}, so switches to {self.level} level directly.")
            
            self.ui.btn_easy.setStyleSheet(self.config.level_btn_style)
            self.ui.btn_normal.setStyleSheet(self.config.level_btn_style)
            self.ui.btn_hard.setStyleSheet(self.config.level_btn_style)
            self.ui.btn_perfessional.setStyleSheet(self.config.level_btn_style)
            self.ui.btn_extreme.setStyleSheet(self.config.level_btn_style)
            
            # restart and reshow a new game.
            self.get_sudoku()
            self.showGame()
            sender.setStyleSheet(self.config.level_target_btn_style)
        
    def show_time(self):
        self.time_sonsumed += 1
        time_text = time_conversion(self.time_sonsumed)
        self.ui.label_time.setText(time_text)
        # self.log.info(f'The timer has triggered, and time ({time_text}) has been updated.')
        
    
class FillGrid(QUndoCommand):
    # a class that implements the function of undo and redo for filling grid.
    def __init__(self, target: QPushButton, value: str, log, stack: deque, row, col, sudoku):
        super().__init__()
        self.target = target
        self.value = value
        self.log = log
        self.stack = stack
        self.row = row
        self.col = col
        self.sudoku = sudoku
        
    def redo(self) -> None:
        self.log.info('A redo operation has been performed.')
        prev = self.target.text()
        self.target.setText(self.value)
        self.stack.append((self.target, prev, self.row, self.col))
        self.log.info(f'The value of {self.target.objectName()} has been changed to {self.value}.')
        
    def undo(self) -> None:
        self.log.info('An undo operation has been performed.')
        if len(self.stack) > 0:
            target, prev, row, col = self.stack.pop()
            target.setText(prev)
            self.sudoku[row-1, col-1] = 0 if prev == '' else int(prev)
            self.log.info(f'The value of {self.target.objectName()} has been changed back to {prev}.')
        else:
            self.log.info(f'The stack is empty, so the undo cannot be performed.')
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())
