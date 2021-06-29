'''
Created on Jun 29, 2021

@author: Duong_Thanh
'''

# from PyQt5 import QtWidgets, uic
# from PyQt5.QtGui import QPixmap, QResizeEvent
# from PyQt5.Qt import QImage, QTimer, QEventLoop, QLabel, QColor
# from PyQt5.QtWidgets import QFileDialog

from PyQt5.Qt import QTimer, QEventLoop

class QT_support_func():
    COLOR_RED_ALARM = "background-color: rgb(255,0,0)"
    COLOR_BUTTON_GRAY = "background-color: rgb(200,200,200)"
    COLOR_BUTTON_BLUE_SLIGHT = "background-color: rgb(100,125,250)"
    COLOR_LINEEDIT_WIDGET_GRAY = "background-color: rgb(239, 239, 239)"

    def delay_ms_loop(self, delay_ms_time):
        loop = QEventLoop()
        QTimer.singleShot(delay_ms_time, loop.quit)
        loop.exec()

    def GUI_ALARM_(self, ui_arg, ORIG_COLOR):
        ui_arg.setStyleSheet(self.COLOR_RED_ALARM); 
        self.delay_ms_loop(80); 
        ui_arg.setStyleSheet(ORIG_COLOR);
        
        
    def GUI_COLOR_CHANGE(self, ui_arg, SET_COLOR):
        ui_arg.setStyleSheet(SET_COLOR);
        
        
    def GUI_COLOR_CHANGE_STATE(self, ui_arg, STATE, TRUE_COLOR, FALSE_COLOR):
        if(STATE):
            ui_arg.setStyleSheet(TRUE_COLOR); 
        else :
            ui_arg.setStyleSheet(FALSE_COLOR);
