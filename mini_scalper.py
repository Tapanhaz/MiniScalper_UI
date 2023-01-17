import sys,yaml,pyotp,threading,requests,configparser
from NorenRestApiPy.NorenApi import  NorenApi
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QEvent
from time import sleep
import pandas as pd, numpy as np
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime, timedelta

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

        self.var_token = ""
        self.var_ltp = 0

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

        self.load_expirylist()
        self.combo_ticker.addItems(['BANKNIFTY','NIFTY'])
        self.combo_strike.addItems(['ATM', 'ITM','ITM1','ITM2','ITM3','ITM4','OTM','OTM1','OTM2','OTM3','OTM4'])
        self.combo_lots.addItems(['1','2','3','4','5','6','7','8','9','10'])
        self.combo_side.addItems(['CE','PE'])

        self.load_settings()

        ## Get combo values 

        self.combo_ticker.currentTextChanged.connect(self.update_var_token)
        self.combo_strike.currentTextChanged.connect(self.update_var_token)
        self.combo_lots.currentTextChanged.connect(self.update_var_token)
        self.combo_side.currentTextChanged.connect(self.update_var_token)
        self.combo_expiry.currentTextChanged.connect(self.update_var_token)
    
    
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

            self.ui_second_window.username.setText("")
            self.ui_second_window.login_stat.setText("")

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

            self.ui_second_window.btn_login.clicked.connect(self.ShoonyaLogin)

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
        self.sl_window.show()

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
            geo.moveBottom(geo.bottom()+(geo.height()))
            self.sl_window.setGeometry(geo)
        elif self.right_bottom_corner.isChecked() or self.left_bottom_corner.isChecked():
            height = self.sl_window.size().height()
            geo.moveTop(geo.top() - height)
            self.sl_window.setGeometry(geo)
        else:
            geo.moveBottom(geo.bottom()+(geo.height()))
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
        self.combo_ticker.setCurrentText("BANKNIFTY")
        self.combo_strike.setCurrentText("ITM")
        self.combo_lots.setCurrentText("1")
        self.combo_side.setCurrentText("CE")
        expiry_dates = [self.combo_expiry.itemText(i) for i in range(self.combo_expiry.count())]
        current_date = datetime.now().date()
        expiry_dates = [datetime.strptime(date, '%d-%b-%Y').date() for date in expiry_dates]
        closest_expiry_date = min(expiry_dates, key=lambda date: abs(date - current_date) if date >= current_date else timedelta.max)
        self.combo_expiry.setCurrentText(closest_expiry_date.strftime('%d-%b-%Y'))
        self.save_settings()

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {'ticker': self.combo_ticker.currentText(),
                             'strike': self.combo_strike.currentText(),
                             'lots': self.combo_lots.currentText(),
                             'side': self.combo_side.currentText(),
                             'expiry': self.combo_expiry.currentText()}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
    
    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        if 'Settings' in config:
            self.combo_ticker.setCurrentText(config['Settings']['ticker'])
            self.combo_strike.setCurrentText(config['Settings']['strike'])
            self.combo_lots.setCurrentText(config['Settings']['lots'])
            self.combo_side.setCurrentText(config['Settings']['side'])
            #self.combo_expiry.setCurrentText(config['Settings']['expiry'])
    
    def update_var_token(self):
        global ord_qty,nifty_ltp,banknifty_ltp,idx_df,api

        ticker=self.combo_ticker.currentText()
        strikepos=self.combo_strike.currentText()
        lots=self.combo_lots.currentText()
        optype=self.combo_side.currentText()
        expiry=self.combo_expiry.currentText()
        if ticker == 'NIFTY':
            lotsize=50
            strikediff=50
            inst_ltp=float(nifty_ltp)
        elif ticker == 'BANKNIFTY':
            lotsize=25
            strikediff=100
            inst_ltp=float(banknifty_ltp)

        atm_strike = round(inst_ltp/strikediff) * strikediff
        ord_qty=lotsize*int(lots)
        self.lbl_qty.setText(str(ord_qty))

        if strikepos == 'ATM':
            mystrike = atm_strike
        elif strikepos == "ITM" or strikepos == "OTM":
            strikepos += "0"
            pos = int(strikepos[-1]) + 1
            if optype == "CE":
                middle_operand = "-"
            elif optype == "PE":
                middle_operand = "+"
            mystrike = eval(f"atm_strike {middle_operand} pos*strikediff")
            #print(mystrike)
        else:
            pos = int(strikepos[-1]) + 1
            if optype == "CE":
                middle_operand = "-"
            elif optype == "PE":
                middle_operand = "+"
            mystrike = eval(f"atm_strike {middle_operand} pos*strikediff")
            #print(mystrike)
        
        expiry_date = datetime.strptime(expiry, '%d-%b-%Y').strftime("%d%b%y").upper()
        
        trading_symbol=f"{ticker}{expiry_date}{optype[0]}{mystrike}"
        
        
        if float(mystrike) > 10000 :
            self.var_token = idx_df.loc[idx_df['TradingSymbol'] == trading_symbol, 'Token'].values[0]
            self.lbl_strike.setText(str(mystrike))
            #print(self.var_token)
            api.subscribe(f'NFO|{self.var_token}')
        else:
            self.lbl_strike.setText("Error !!")
    
     

    def load_expirylist(self):
        config = configparser.ConfigParser()
        config.read('expiry.ini')
        expiry_dates = config.items('Expiry')
        self.combo_expiry.clear()
        for date in expiry_dates:
            self.combo_expiry.addItem(date[1])
        current_date = datetime.now().date()
        expiry_dates = [datetime.strptime(date[1], '%d-%b-%Y').date() for date in expiry_dates]
        closest_expiry_date = min(expiry_dates, key=lambda date: abs(date - current_date) if date >= current_date else timedelta.max)
        self.combo_expiry.setCurrentText(closest_expiry_date.strftime('%d-%b-%Y'))

    def get_expiry_dates(self):
        global api,idx_df
        nfozip="NFO_symbols.txt.zip"
        instruments_url=f"https://shoonya.finvasia.com/{nfozip}"
        res=requests.get(f"{instruments_url}", allow_redirects=True)
        if res.status_code == 200:
            zfile = BytesIO(res.content)
            with ZipFile(zfile, "r") as zip_ref:
                for file in zip_ref.infolist():
                    with zip_ref.open(file) as f:
                        inst_df = pd.read_csv(f)
                        idx_df= (inst_df.query("Symbol in ['BANKNIFTY', 'NIFTY']")).reset_index(drop=True)
                        idx_df.to_csv("Index.csv")
                        expiry_list =np.sort(pd.to_datetime((inst_df[inst_df['Symbol']=='BANKNIFTY'])['Expiry'],format='%d-%b-%Y', errors='coerce').dt.date.unique())
                        recent_dates = expiry_list[:4]

                        config = configparser.ConfigParser()
                        config.add_section('Expiry')

                        for i, date in enumerate(recent_dates):
                            config.set('Expiry', f'Date{i+1}', date.strftime('%d-%b-%Y'))

                        with open('expiry.ini', 'w') as expiry_ini:
                            config.write(expiry_ini)
                        self.load_expirylist()
        else:
            pass
        
    
    def liveprice(self):
        global api,nifty_ltp,banknifty_ltp
        feed_opened = False
        feedJson = {}
        orderJson={}
        
        banknifty='26009'
        nifty='26000'
        bnftoken=f'NSE|{banknifty}'
        nftoken=f'NSE|{nifty}'
        

        def event_handler_feed_update(message):
            if (('lp' in message)&('tk' in message)):
                feedJson[message['tk']]={'ltp':float(message['lp'])}


        def event_handler_order_update(inmessage):
            if (('norenordno' in inmessage)&('status' in inmessage)):
                orderJson[inmessage['norenordno']]={'status':float(inmessage['status'])} 


        def open_callback():
            global feed_opened
            feed_opened = True

        def setup_websocket():
            global feed_opened,api
            api.start_websocket( order_update_callback=event_handler_order_update,
                                 subscribe_callback=event_handler_feed_update, 
                                 socket_open_callback=open_callback)
            sleep(1)
            while(feed_opened==False):

                pass
            return True

        setup_websocket()
        api.subscribe(bnftoken)
        api.subscribe(nftoken)

        
        
        #api.subscribe(f'NFO|{nfo_token}')
        
        while True:
            
            if banknifty in feedJson:
                self.lbl_banknifty.setText(str(feedJson[banknifty]['ltp']))
                banknifty_ltp = feedJson[banknifty]['ltp']
            if nifty in feedJson:
                self.lbl_nifty.setText(str(feedJson[nifty]['ltp']))
                nifty_ltp = feedJson[nifty]['ltp']
            if str(self.var_token) in feedJson:
                self.lbl_ltp.setText(str(feedJson[str(self.var_token)]['ltp']))
                self.var_ltp=feedJson[str(self.var_token)]['ltp']
            sleep(.5)


    def ShoonyaLogin(self):
        global api, login_status
        with open('cred.yml') as f:
            cred = yaml.load(f, Loader=yaml.FullLoader)
            #print(cred)
        class ShoonyaApiPy(NorenApi):
            def __init__(self):
                NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/', eodhost='https://api.shoonya.com/chartApi/getdata/')
        api = ShoonyaApiPy()
        ret = api.login(userid=cred['user'],
                        password=cred['pwd'],
                        twoFA=pyotp.TOTP(cred['token']).now(),
                        vendor_code=cred['vc'],
                        api_secret=cred['apikey'],
                        imei=cred['imei'])
        login_status=ret['stat']
        thread_liveprice = threading.Thread(target=self.liveprice, daemon=True)

        if ret['stat'] == 'Ok' :
            self.ui_second_window.username.setText(ret['uname'].split()[0])
            self.ui_second_window.login_stat.setText(ret['stat'])
            thread_liveprice.start()
            
        else:
            self.ui_second_window.login_stat.setText('Error!!')
        return api

    

if __name__ == '__main__':
    global login_status, feed_opened, feedJson,api,nifty_ltp,banknifty_ltp,idx_df
    login_status=""
    feed_opened=False
    feedJson={}
    nifty_ltp="0"
    banknifty_ltp="0"
    idx_df=pd.read_csv('Index.csv')
    app = QtWidgets.QApplication(sys.argv)
    window = MiniScalper()
    window.show()
    app.exec_()
