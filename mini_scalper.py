import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QEvent

Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")
Ui_SecondWindow, _ = uic.loadUiType("sub.ui")
Ui_ThirdWindow, _ = uic.loadUiType("sl.ui")

class MiniScalper(QtWidgets.QMainWindow, Ui_MainWindow,Ui_SecondWindow,Ui_ThirdWindow):
    def __init__(self):
        super(MiniScalper, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui_second_window = None
        self.ui_third_window = None
        self.always_on_top = False
        self.btn_menu.clicked.connect(self.create_login_window)
        self.btn_exit.clicked.connect(self.close_windows)
        self.btn_minimize.clicked.connect(self.minimize_windows)

        # window position 
        self.login_window = None
        self.sl_window = None 
        self.default_pos = None
        self.right_bottom_corner = None
        self.left_bottom_corner = None
        self.right_top_corner = None
        self.left_bottom_corner = None
        
        # transparency slider
        self.transparency_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.transparency_slider.setRange(0, 100)
        self.transparency_slider.setValue(100)
        self.transparency_slider.setVisible(False)
        self.transparency_slider.valueChanged.connect(self.on_transparency_value_changed)
        self.btn_slider.clicked.connect(self.show_transparency_slider)
        self.transparency_slider.installEventFilter(self)
        
        self.frame_title.installEventFilter(self)
        self.installEventFilter(self)
    
    
    def create_login_window(self):
        #Ui_SecondWindow, _ = uic.loadUiType("sub.ui")
        if self.login_window is None:
            self.login_window = QtWidgets.QMainWindow()
            self.ui_second_window = Ui_SecondWindow()
            self.ui_second_window.setupUi(self.login_window)
            self.login_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.login_window.setWindowOpacity(self.transparency_slider.value() / 100)
            self.login_window.show()
            
            self.login_window.installEventFilter(self)
            self.ui_second_window.btn_menu.setMenu(QtWidgets.QMenu(self.ui_second_window.btn_menu))
            self.ui_second_window.btn_menu.menu().addAction("Always on top", self.toggle_always_on_top).setCheckable(True)
            
            # Window position
            pos_menu = self.ui_second_window.btn_menu.menu().addMenu("Window position")
            self.default_pos = pos_menu.addAction("Default", self.set_default_position)
            self.default_pos.setCheckable(True)
            self.default_pos.setChecked(True)
            self.left_top_corner = pos_menu.addAction("Left Top Corner", self.set_left_top_corner_position)
            self.left_top_corner.setCheckable(True)
            self.right_top_corner = pos_menu.addAction("Right Top Corner", self.set_right_top_corner_position)
            self.right_top_corner.setCheckable(True)
            self.right_bottom_corner = pos_menu.addAction("Right Bottom Corner", self.set_right_bottom_corner_position)
            self.right_bottom_corner.setCheckable(True)
            self.left_bottom_corner = pos_menu.addAction("Left Bottom Corner", self.set_left_bottom_corner_position)
            self.left_bottom_corner.setCheckable(True)

            self.position_login_window()

            self.ui_second_window.btn_menu.menu().addAction("Get Expiry", self.get_expiry_dates)
            self.ui_second_window.btn_menu.menu().addAction("Save Setings", self.save_settings)
            self.ui_second_window.btn_menu.menu().addAction("Restore Defaults", self.default_settings)

            if self.sl_window is None:
                self.sl_window = QtWidgets.QMainWindow()
                self.ui_third_window = Ui_ThirdWindow()
                self.ui_third_window.setupUi(self.sl_window)
                self.sl_window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
                self.sl_window.setWindowOpacity(self.transparency_slider.value() / 100)
                self.sl_window.show()
                self.position_sl_window()
                self.sl_window.installEventFilter(self)
            

        elif self.login_window.isVisible():
            self.login_window.hide()
            self.sl_window.hide()
        else:
            self.login_window.show()
            self.sl_window.show()
   
    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            self.login_window.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
            self.login_window.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
        self.show()
        self.login_window.show()

    def set_default_position(self):
        desktop = QtWidgets.QDesktopWidget()
        x = (desktop.width() - self.frameGeometry().width()) / 2
        y = (desktop.height() - self.frameGeometry().height()) / 2
        self.move(x.__round__(), y.__round__())
        self.default_pos.setChecked(True)
        self.right_top_corner.setChecked(False)
        self.right_bottom_corner.setChecked(False)
        self.left_top_corner.setChecked(False)
        self.left_bottom_corner.setChecked(False)

    def set_right_top_corner_position(self):
        desktop = QtWidgets.QDesktopWidget()
        x = desktop.width() - self.frameGeometry().width()
        y = 0
        self.move(x, y)
        self.default_pos.setChecked(False)
        self.right_top_corner.setChecked(True)
        self.right_bottom_corner.setChecked(False)
        self.left_top_corner.setChecked(False)
        self.left_bottom_corner.setChecked(False)

    def set_left_top_corner_position(self):
        desktop = QtWidgets.QDesktopWidget()
        x = 0 #self.login_window.frameGeometry().width()+2
        y = 0
        self.move(x, y)
        self.default_pos.setChecked(False)
        self.right_top_corner.setChecked(False)
        self.right_bottom_corner.setChecked(False)
        self.left_top_corner.setChecked(True)
        self.left_bottom_corner.setChecked(False)

    def set_right_bottom_corner_position(self):
        desktop = QtWidgets.QDesktopWidget()
        x = desktop.width() - self.frameGeometry().width()
        y = desktop.height() - (self.frameGeometry().height()+50)
        self.move(x, y)
        self.default_pos.setChecked(False)
        self.right_top_corner.setChecked(False)
        self.right_bottom_corner.setChecked(True)
        self.left_top_corner.setChecked(False)
        self.left_bottom_corner.setChecked(False)

    def set_left_bottom_corner_position(self):
        desktop = QtWidgets.QDesktopWidget()
        x=0 #self.login_window.frameGeometry().width()+2
        y = desktop.height() - (self.frameGeometry().height()+50)
        self.move(x, y)
        self.default_pos.setChecked(False)
        self.right_top_corner.setChecked(False)
        self.right_bottom_corner.setChecked(False)
        self.left_top_corner.setChecked(False)
        self.left_bottom_corner.setChecked(True)
        
    def on_transparency_value_changed(self):
        transparency = self.transparency_slider.value()
        self.setWindowOpacity(transparency / 100)
        if self.login_window:
            self.login_window.setWindowOpacity(transparency / 100)
            if self.sl_window:
                self.sl_window.setWindowOpacity(transparency / 100)

    
    def show_transparency_slider(self):
        pos = self.btn_slider.mapToGlobal(QtCore.QPoint(0, 0))
        pos.setY(pos.y() + self.btn_slider.height())
        self.transparency_slider.move(pos)
        self.transparency_slider.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.transparency_slider.setStyleSheet("""
        QSlider{
        border:7px;
        border-color:black;
        border-radius: 50px;
            }
        QSlider::groove:vertical {
            border: 1px solid #999999;
            background: lightblue;
            width: 13px;
            border-radius: 6px;
        }
        QSlider::handle:vertical {
            background: white;
            border: 1px solid #5c5c5c;
            width: 13px;
            height: 50px;
            border-radius: 6px;
            margin: 0 -4px;
        }
        QSlider::sub-page:vertical, QSlider::add-page:vertical{
        border-radius: 6px;
        }
    """)

        self.transparency_slider.setVisible(True)
        
    def eventFilter(self, object, event):
        if object == self.transparency_slider:
            if event.type() == QEvent.Leave:
                self.transparency_slider.setVisible(False)
                return True
        
        #elif event.type() == QEvent.MouseMove and object == self.transparency_slider:
        #    self.transparency_slider.setVisible(True)
        #    self.transparency_slider.raise_()
        #    return True
        
        elif object == self.frame_title:
            if event.type() == QEvent.MouseButtonPress:
                self.offset = event.pos()
            elif event.type() == QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton:
                new_pos = self.mapToParent(event.pos() - self.offset)
                self.move(new_pos)
                       
        elif event.type() == QEvent.WindowStateChange:
            if self.windowState() == QtCore.Qt.WindowNoState:
                self.showNormal()
                if self.login_window is not None:
                    self.login_window.showNormal()
                    if self.sl_window is not None:
                        self.sl_window.showNormal()
                    
            #elif self.login_window.windowState() == QtCore.Qt.WindowNoState:
            #    self.showNormal()
            #    self.login_window.showNormal()
                        
        return super(MiniScalper, self).eventFilter(object, event)

    def position_login_window(self):
        geo = self.geometry()
        #print(self.default_pos.isChecked(),self.right_top_corner.isChecked(),self.right_bottom_corner.isChecked())

        if self.right_top_corner.isChecked() or self.right_bottom_corner.isChecked():
            geo.moveLeft(geo.left() - geo.width() + 1)
            #geo.moveRight(geo.right()+(geo.width()+1))
            self.login_window.setGeometry(geo)
        elif self.left_top_corner.isChecked() or self.left_bottom_corner.isChecked():
            #geo.moveLeft(geo.left() - geo.width() + 1)
            geo.moveRight(geo.right()+geo.width()+1)
            self.login_window.setGeometry(geo)
        else:
            geo.moveRight(geo.right()+(geo.width()+1))
            self.login_window.setGeometry(geo)
        
    
    def position_sl_window(self):
        geo = self.geometry()
        
        if self.right_top_corner.isChecked() or self.left_top_corner.isChecked():
            geo.moveBottom(geo.bottom()+(geo.height()+1))
            self.sl_window.setGeometry(geo)
        elif self.right_bottom_corner.isChecked() or self.left_bottom_corner.isChecked():
            height = self.sl_window.size().height()
            geo.moveTop(geo.top() - height)
            self.sl_window.setGeometry(geo)
        else:
            geo.moveBottom(geo.bottom()+(geo.height()+1))
            self.sl_window.setGeometry(geo)

        
    
    def close_windows(self):
        self.close()
        if self.login_window is not None:
            self.login_window.close()
            if self.sl_window is not None:
                self.sl_window.close()


    def minimize_windows(self):
        self.showMinimized()
        if self.login_window is not None:
            self.login_window.showMinimized()
            if self.sl_window is not None:
                self.sl_window.showMinimized()
    
    def moveEvent(self, event):
        super(MiniScalper, self).moveEvent(event)
        if self.login_window:
            #diff = event.pos() - event.oldPos()
            #geo = self.login_window.geometry()
            #geo.moveTopLeft(geo.topLeft() + diff)
            #self.login_window.setGeometry(geo)
            self.position_login_window()
            if self.sl_window:
                #diff = event.pos() - event.oldPos()
                #geo = self.sl_window.geometry()
                #geo.moveTopLeft(geo.topLeft() + diff)
                #self.sl_window.setGeometry(geo)
                self.position_sl_window()

    def default_settings(self):
        pass

    def save_settings(self):
        pass

    def get_expiry_dates(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MiniScalper()
    window.show()
    app.exec_()
