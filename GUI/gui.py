import sys
from turtle import isvisible
import vlc
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRectF, QRect, QEasingCurve, QPoint
from PyQt5.QtCore import Qt, QRectF, QTimer, QTime, QDate, QPropertyAnimation, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QFont, QFontDatabase, QPalette, QMouseEvent, QIcon, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,  QGraphicsBlurEffect, QLabel, QGraphicsOpacityEffect, QPushButton, QStackedWidget, QFrame, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from GUI.buttons import CustomButton , ImageButton
# from buttons import CustomButton , ImageButton
# from GUI.animations import fadeAnimation

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

WINDOW_W = 1080
WINDOW_H = 1080
FIRST_ICON_R = 150
FIRST_CONTAINER_W = 200
FIRST_CONTAINER_H = 400
FIRST_TXT_W = 150
FIRST_TXT_H = 40
FIRST_TOPRTC_W = 50
FIRST_TOPRTC_H = 25
FIRST_STATUS_W = 100
FIRST_STATUS_H = 25
FIRST_BOTDATE_W = 360
FIRST_BOTDATE_H = 36
FIRST_BOTRTC_W = 360
FIRST_BOTRTC_H = 108
FIRST_BOT_DRSPACE = 0
FIRST_BOTGAP = FIRST_BOTRTC_H
FIRST_BTN_W = 150
FIRST_BTN_H = 50

SECOND_HEAD_TOPGAP = 120
SECOND_HEAD_R = 190
SECOND_NAME_TOPGAP = 30
SECOND_NAME_W = 160
SECOND_NAME_H = 50
SECOND_GUIDE_W = 828
SECOND_GUIDE_H = 274


BOTBAR_BTN_R = 100

GUIDE_BTN_W = 50
GUIDE_BTN_H = 120

VOICE_DETECTING_ICON_R = 100
VOICE_DETECTING_ICON_BOTGAP = 100



coacher = ["Guruji", "Guruji"]
coacherHead = ["resources/images/secondhead_guruji.png", 
               "resources/images/secondhead_guruji.png"]
coacherBackground = ["resources/images/secondback_guruji.jpg", 
                     "resources/images/zeroback_sun.jpg"]
coacherGuideTxt = ["    As the day comes to an end, release yourself\nfrom the busyness and allow your body and mind\nto fully relax. Close your eyes, gently bid farewell\nto today, and drift into a peaceful dream.",
                   "    As the day comes to an end, release yourself\nfrom the busyness and allow your body and mind\nto fully relax. Close your eyes, gently bid farewell\nto today, and drift into a peaceful dream."]
coacherSleepFlashDict = [
{
    "0":"resources/images/third_wave.gif",
    "1":"resources/images/third_starsky.gif",
    "2":"resources/images/third_breath.gif",
    "3":"resources/images/third_shuimu.gif",
    "4":"resources/images/third_shuimu.gif", 
    "5":"resources/images/third_wave.gif",
    "6":"resources/images/third_starsky.gif"
},
{
    "0":"resources/images/third_wave.gif",
    "1":"resources/images/third_starsky.gif",
    "2":"resources/images/third_breath.gif",
    "3":"resources/images/third_shuimu.gif",
    "4":"resources/images/third_shuimu.gif", 
    "5":"resources/images/third_wave.gif",
    "6":"resources/images/third_starsky.gif"
}]
# coacherMovie = [["resources/images/third_breath.gif", "resources/images/third_starsky.gif"],
#                 ["resources/images/third_starsky.gif", "resources/images/third_breath.gif"]]

class FirstWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)  # 不自动填充背景，保持透明
        
        #跑道衬底
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        
        #icon图标按钮
        self.iconBTN = [ImageButton(FIRST_ICON_R, FIRST_ICON_R, "resources/images/firstmenu_Meditation.png", self),
                        ImageButton(FIRST_ICON_R, FIRST_ICON_R, "resources/images/firstmenu_Hypnotise.png", self),
                        ImageButton(FIRST_ICON_R, FIRST_ICON_R, "resources/images/firstmenu_Tools.png", self)]
        #icon名称
        self.txtQLabel = [QLabel(self),
                          QLabel(self),
                          QLabel(self)]
        #Enter按钮
        self.btn = [CustomButton(FIRST_BTN_W, FIRST_BTN_H, self),
                    CustomButton(FIRST_BTN_W, FIRST_BTN_H, self),
                    CustomButton(FIRST_BTN_W, FIRST_BTN_H, self)] 
        self.btn[0].clicked.connect(self.MeditationClicked)
        self.layout()
        
    def layout(self):
        spacing = (WINDOW_W - FIRST_CONTAINER_W * 3)//6
        ContainerPos_W = (WINDOW_H - FIRST_CONTAINER_H)//2        
        TXTVerPos_W = (FIRST_CONTAINER_W - FIRST_TXT_W)//2
        TXTVerPos_H = (FIRST_CONTAINER_H - FIRST_TXT_H)//2
        BTNPos_W = (FIRST_CONTAINER_W - FIRST_BTN_W)//2
        BTNPos_H = FIRST_CONTAINER_H - FIRST_CONTAINER_W//2
        
        # 设置绘制颜色（跑道的颜色）
        runway_color = QColor(255, 255, 255, 100)  # 半透明的白色
        runway_image = QImage(WINDOW_W, WINDOW_H, QImage.Format_ARGB32_Premultiplied)
        runway_image.fill(Qt.transparent)  # 设置透明背景
        
        # 使用 QPainter 绘制跑道形状到 QImage 上
        painter = QPainter(runway_image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)     
        for i in range(3):
            x = (i * (FIRST_CONTAINER_W + spacing)) + spacing*2
            y = ContainerPos_W  # 固定跑道的垂直位置
            painter.setBrush(runway_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, FIRST_CONTAINER_W, FIRST_CONTAINER_H, FIRST_CONTAINER_W//2, FIRST_CONTAINER_W//2)  # 绘制跑道形状
        painter.end()
        
        # 将绘制的图像转换为 QPixmap 显示在 QLabel 中
        self.pixmap = QPixmap.fromImage(runway_image)
        self.label.setPixmap(self.pixmap)
        
        #加载icon
        for i in range(3):
            x = (i * (FIRST_CONTAINER_W + spacing)) + spacing*2
            y = ContainerPos_W  # 固定跑道的垂直位置           
            self.iconBTN[i].move(x+(FIRST_CONTAINER_W-FIRST_ICON_R)//2, y+(FIRST_CONTAINER_W-FIRST_ICON_R)//2)
            
        #加载文字
        text = ["Meditation",
                "Hypnotise",
                "Tools" ]
        palette = QPalette()
        palette.setColor(QPalette.Foreground, QColor(255, 255, 255))  # 设置字体颜色为红色
        current_font = QFont("Source Han Serif CN", 20)
        for i in range(3):
            x = (i * (FIRST_CONTAINER_W + spacing)) + spacing*2
            y = ContainerPos_W  # 固定跑道的垂直位置
            self.txtQLabel[i].setGeometry(x+TXTVerPos_W, y+TXTVerPos_H, FIRST_TXT_W, FIRST_TXT_H)
            self.txtQLabel[i].setAlignment(Qt.AlignCenter)
            self.txtQLabel[i].setText(text[i])
            self.txtQLabel[i].setFont(current_font)
            self.txtQLabel[i].setPalette(palette)
        
        current_font = QFont("PingFang SC Regular", 15)
        #绘制按钮    
        for i in range(3):
            x = (i * (FIRST_CONTAINER_W + spacing)) + spacing*2
            y = ContainerPos_W  # 固定跑道的垂直位置
            self.btn[i].setText("Enter")
            self.btn[i].setFont(current_font)
            self.btn[i].move(x+BTNPos_W, y+BTNPos_H)
            
    def MeditationClicked(self):
        # print(f"Mouse clicked")
        if self.parent().menu_flag == 1:
           self.parent().SecondMenuGrp[0].fade_in()
        else:
           print('illegal click\n')
           return
        

        
class SecondWidget(QWidget):
    global coacher
    global coacherHead
    global coacherGuideTxt
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)  # 不自动填充背景，保持透明
        #助眠师编号
        self.number = number
        #设置位置和大小
        self.setGeometry(self.number*WINDOW_W, 0, WINDOW_W, WINDOW_H)
        #背景图
        self.backLabel = QLabel(self)
        self.backLabel.setGeometry(0, 0, WINDOW_W, WINDOW_H)          
        #引导语衬底
        self.guideLabel = QLabel(self)
        self.guideLabel.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        #头像
        self.headBTN = ImageButton(SECOND_HEAD_R, SECOND_HEAD_R, coacherHead[self.number], self)
        #名字
        self.nameQLabel = QLabel(self)
        #引导语
        self.coacherGuideTxtQLabel = QLabel(self)
        
        self.layout()
        
    def layout(self):
        self.image = QPixmap(coacherBackground[self.number])
        self.image = self.image.scaled(self.backLabel.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.backLabel.setPixmap(self.image)
        self.backLabel.setScaledContents(True)
        
        # 设置绘制颜色（跑道的颜色）
        runway_color = QColor(255, 255, 255, 100)  # 半透明的白色
        runway_image = QImage(WINDOW_W, WINDOW_H, QImage.Format_ARGB32_Premultiplied)
        runway_image.fill(Qt.transparent)  # 设置透明背景
        
        # 使用 QPainter 绘制跑道形状到 QImage 上
        painter = QPainter(runway_image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setBrush(runway_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect((WINDOW_W - SECOND_GUIDE_W)//2, WINDOW_H//2, SECOND_GUIDE_W, SECOND_GUIDE_H, SECOND_GUIDE_H//2, SECOND_GUIDE_H//2)  # 绘制跑道形状
        painter.end()
        
        # 将绘制的图像转换为 QPixmap 显示在 QLabel 中
        self.pixmap = QPixmap.fromImage(runway_image)

        # 设置高斯模糊效果
        # blur_effect = QGraphicsBlurEffect()
        # blur_effect.setBlurRadius(10)  # 设置模糊半径
        # self.guideLabel.setGraphicsEffect(blur_effect)
        self.guideLabel.setPixmap(self.pixmap)
        
        palette = QPalette()
        palette.setColor(QPalette.Foreground, QColor(255, 255, 255))
        self.headBTN.move((WINDOW_W-SECOND_HEAD_R)//2, SECOND_HEAD_TOPGAP)
        self.nameQLabel.setGeometry((WINDOW_W-SECOND_NAME_W)//2, SECOND_HEAD_TOPGAP+SECOND_HEAD_R+SECOND_NAME_TOPGAP, SECOND_NAME_W, SECOND_NAME_H)
        self.nameQLabel.setAlignment(Qt.AlignCenter)
        self.nameQLabel.setText(coacher[self.number])
        self.nameQLabel.setFont(QFont("Source Han Serif CN", 26))
        self.nameQLabel.setPalette(palette)
        
        self.coacherGuideTxtQLabel.setGeometry((WINDOW_W - SECOND_GUIDE_W)//2, WINDOW_H//2, SECOND_GUIDE_W, SECOND_GUIDE_H)
        self.coacherGuideTxtQLabel.setAlignment(Qt.AlignCenter)
        self.coacherGuideTxtQLabel.setText(coacherGuideTxt[self.number])
        self.coacherGuideTxtQLabel.setFont(QFont("PingFang SC Light", 20))
        palette.setColor(QPalette.Foreground, QColor(0, 0, 0))
        self.coacherGuideTxtQLabel.setPalette(palette)
        
        # 设置透明度动画
        # self.opacity_effect = QGraphicsOpacityEffect()
        # self.setGraphicsEffect(self.opacity_effect)
        # self.opacity_effect.setOpacity(0)

        # self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        # self.animation.setDuration(1000)
        # self.animation.setStartValue(0)
        # self.animation.setEndValue(1)
        # self.animation.finished.connect(self.parent().First2Second_finish_switch)
    def fade_in(self):
        # self.raise_()
        # self.parent().afterRaise()
        for i in range(len(coacher)):
            self.parent().SecondMenuGrp[i].raise_()
        self.parent().afterRaise()
        self.show()
        self.parent().animation_second.start()
             
class TopBarDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)  # 不自动填充背景，保持透明

        # 设置界面大小
        self.setGeometry(0, 0, WINDOW_W, WINDOW_H//10)
        
        current_font = QFont("PingFang SC Bold", 12)
        # 创建一个 QLabel 用于显示时间
        self.time_label = QLabel(self)
        # self.time_label.setFixedSize(FIRST_TOPRTC_W, FIRST_TOPRTC_H)
        self.time_label.setStyleSheet("color: white;")
        self.time_label.setFont(current_font)
        self.time_label.setGeometry(WINDOW_W//2-FIRST_TOPRTC_W*2, WINDOW_W//120, FIRST_TOPRTC_W, FIRST_TOPRTC_H)
        self.time_label.hide()

        # 设置 QTimer 来每秒更新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)  # 每次定时器超时，调用 update_time 方法
        self.timer.start(1000)  # 1000ms = 1秒

        # 初始化时钟显示
        self.update_time()
        
        #状态栏显示
        self.status_label = QLabel(self)
        self.status_pixmap = QPixmap("resources/images/topbar_wifiConnected.png")
        self.status_label.setGeometry(WINDOW_W//2+FIRST_TOPRTC_W*2, WINDOW_W//120, FIRST_STATUS_W, FIRST_STATUS_H)
        self.status_pixmap = self.status_pixmap.scaled(FIRST_STATUS_H, FIRST_STATUS_H*2//3, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.status_label.setPixmap(self.status_pixmap)  

    def update_time(self):
        # 获取当前时间并更新到 QLabel 中
        # print("time")
        current_time = QTime.currentTime().toString("hh:mm")
        self.time_label.setText(current_time)  # 设置 QLabel 显示当前时间

class BottomBarDisplayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)  # 不自动填充背景，保持透明

        # 设置界面大小
        self.setGeometry(0, WINDOW_H - (FIRST_BOTDATE_H + FIRST_BOT_DRSPACE + FIRST_BOTRTC_H + FIRST_BOTGAP), WINDOW_W, FIRST_BOTDATE_H + FIRST_BOT_DRSPACE + FIRST_BOTRTC_H)
        # self.setGeometry(0, 0, WINDOW_W, FIRST_BOTDATE_H + FIRST_BOT_DRSPACE + FIRST_BOTRTC_H)
        
        current_font = QFont("PingFang SC Light")
        current_font.setPixelSize(FIRST_BOTDATE_H)
        # 创建一个 QLabel 用于显示时间
        self.date_label = QLabel(self)
        # self.time_label.setFixedSize(FIRST_TOPRTC_W, FIRST_TOPRTC_H)
        self.date_label.setStyleSheet("color: white;")
        self.date_label.setFont(current_font)
        self.date_label.setGeometry((WINDOW_W - FIRST_BOTRTC_W)//2, 0, FIRST_BOTDATE_W, FIRST_BOTDATE_H)
        self.date_label.setAlignment(Qt.AlignCenter)
        # self.date_label.hide()
        
        current_font = QFont("PingFang SC Regular")
        current_font.setPixelSize(FIRST_BOTRTC_H)
        # 创建一个 QLabel 用于显示时间
        self.time_label = QLabel(self)
        # self.time_label.setFixedSize(FIRST_TOPRTC_W, FIRST_TOPRTC_H)
        self.time_label.setStyleSheet("color: white;")
        self.time_label.setFont(current_font)
        self.time_label.setGeometry((WINDOW_W - FIRST_BOTRTC_W)//2, FIRST_BOTDATE_H + FIRST_BOT_DRSPACE, FIRST_BOTRTC_W, FIRST_BOTRTC_H)
        self.time_label.setAlignment(Qt.AlignCenter)
        # self.time_label.hide()

        # 设置 QTimer 来每秒更新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)  # 每次定时器超时，调用 update_time 方法
        self.timer.start(1000)  # 1000ms = 1秒

        # 初始化时钟显示
        self.update_time()  
        
        # 绘制播放按钮
        self.playbutton = ImageButton(BOTBAR_BTN_R, BOTBAR_BTN_R, "resources/images/bottombar_playButton.png", self)
        self.playbutton.setGeometry((self.size().width()-BOTBAR_BTN_R)//2, (self.size().height() - BOTBAR_BTN_R)//2, BOTBAR_BTN_R, BOTBAR_BTN_R)  # 设置按钮位置和大小
        self.playbutton.clicked.connect(self.playClicked)
        self.playbutton.hide()
        # 绘制停止按钮
        self.stopbutton = ImageButton(BOTBAR_BTN_R, BOTBAR_BTN_R, "resources/images/bottombar_stop.png", self)
        self.stopbutton.setGeometry((self.size().width()-BOTBAR_BTN_R)//2, (self.size().height() - BOTBAR_BTN_R)//2, BOTBAR_BTN_R, BOTBAR_BTN_R)  # 设置按钮位置和大小
        self.stopbutton.clicked.connect(self.stopClicked)
        self.stopbutton.hide()

    def playClicked(self):
        # print(f"Mouse clicked")
        if self.parent().menu_flag == 2:
           self.parent().comm.message.emit("enter sleep")
        #    self.parent().thirdBGMovie = QMovie(coacherSleepFlashDict[self.parent().SecondMenuIndex][self.parent().sleep_seq])
        #    self.parent().thirdBG.setMovie(self.parent().thirdBGMovie)
        #    self.parent().thirdBGMovie.start()
        # #    self.parent().thirdBG.hide()
        #    self.parent().thirdBG.raise_()
        #    self.parent().afterRaise()
        #    self.parent().thirdBG.show()
        #    self.parent().animation_third.start()
        else:
           print('illegal click\n')
           return
       
    def stopClicked(self):
        if self.parent().menu_flag == 3:
           self.parent().thirdBGMovie.stop()
        else:
           print('illegal click\n')
           return
        
    def update_time(self):
        # 获取当前时间并更新到 QLabel 中
        # print("time")
        current_date = QDate.currentDate().toString("MMM dd  ddd")        
        current_time = QTime.currentTime().toString("hh:mm")
        self.date_label.setText(current_date)  # 设置 QLabel 显示当前日期
        self.time_label.setText(current_time)  # 设置 QLabel 显示当前时间  
        
class VoiceDetectingWidget(QWidget):
    def __init__(self, image_folder, interval=100, parent=None):
        super().__init__(parent)
        self.image_folder = image_folder
        self.image_files = sorted([
            os.path.join(image_folder, f)
            for f in os.listdir(image_folder)
            if f.lower().endswith('.png')
        ])
        self.total_images = len(self.image_files)
        self.current_index = 0
        self.interval = interval  # 单位：毫秒

        # self.setWindowTitle("PNG 序列动画")
        self.setGeometry(0, 0, 1080, 1080)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.backScene = QLabel(self)
        self.backScene.setGeometry(0, 0, self.width(), self.height())        
        backScene_color = QColor(0, 0, 0, 200)  # 半透明的黑色
        backScene_image = QImage(WINDOW_W, WINDOW_H, QImage.Format_ARGB32_Premultiplied)
        backScene_image.fill(Qt.transparent)  # 设置透明背景
        # 使用 QPainter 绘制跑道形状到 QImage 上
        painter = QPainter(backScene_image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setBrush(backScene_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, WINDOW_W, WINDOW_H)  # 绘制跑道形状
        painter.end()
        # 将绘制的图像转换为 QPixmap 显示在 QLabel 中
        self.pixmap = QPixmap.fromImage(backScene_image)
        self.backScene.setPixmap(self.pixmap)

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 1080, 1080)
        # 定时器用于播放动画
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.interval)

        self.update_frame()

    def update_frame(self):
        pixmap = QPixmap(self.image_files[self.current_index])
        self.label.setPixmap(pixmap)
        self.current_index = (self.current_index + 1) % self.total_images              
        
class MainWindow(QMainWindow):
    def __init__(self, communicator):
        super().__init__()
        self.setFixedSize(WINDOW_W, WINDOW_H) #设置主窗口固定大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint) #把窗口设置为“无边框且总在最前面”的窗口
        self.setCursor(Qt.BlankCursor)
        
        self.ClickStartPos = None
        self.DraggingFlag = False
        #加载字体
        font_db = QFontDatabase()
        font_db.addApplicationFont("resources/fonts/PingFang_Regular.ttf")#"PingFang SC Regular"
        font_db.addApplicationFont("resources/fonts/PingFang_Bold.ttf")#"PingFang SC Bold"
        font_db.addApplicationFont("resources/fonts/PingFang_Light.ttf")#"PingFang SC Light"
        font_db.addApplicationFont("resources/fonts/SourceHanSerifCN-Heavy-4.otf")#"Source Han Serif CN"
        font_db.addApplicationFont("resources/fonts/SourceHanSerifCN-Bold-2.otf")#"Source Han Serif CN"
        #菜单级数标识
        self.menu_flag = 0  
        #睡眠流程阶段序号
        self.sleep_seq = "1" 
        self.comm = communicator
        
        # self.Container = QStackedWidget(self)
        # self.Container.setGeometry(0,0,WINDOW_W, WINDOW_H)
        # self.scene = QGraphicsScene()
        # self.setScene(self.scene)
        # 创建初始界面
        self.initBG = QLabel(self)
        self.initBG.setPixmap(QPixmap("resources/images/zeroback_sun.jpg").scaled(self.size(), Qt.IgnoreAspectRatio))
        self.initBG.setGeometry(0, 0, self.width(), self.height())
        # self.initRect = QGraphicsRectItem(self.initBG)
        # self.initBG.hide()
             
        # 创建一级界面
        self.firstBG = QLabel(self)
        self.firstBG.setGeometry(0, 0, self.width(), self.height())
        self.firstBG.setScaledContents(True)
        self.firstBGMovie = QMovie("resources/images/firstback_fire.gif")
        self.firstBG.setMovie(self.firstBGMovie)
        self.firstBGMovie.start()
        self.firstBG.hide()         
        self.firstMenu = FirstWidget(self)
        self.firstMenu.setGeometry(self.width(), 0, self.width(), self.height()) 
        # self.firstMenu.hide() 

        # 创建二级界面 
        self.SecondMenuIndex = 0 #当前二级菜单页序数     
        self.SecondMenuGrp = [] #二级菜单子项列表
        for i in range(len(coacher)):
            self.SecondMenuGrp.append(SecondWidget(i,self))
            if i == 0:
                self.SecondMenuGrp[i].hide()
        self.curr_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex]
        self.next_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex+1]
        
        # #创建三级场景界面
        self.thirdBG = QLabel(self)
        self.thirdBG.setGeometry(0, 0, self.width(), self.height())
        self.thirdBG.setScaledContents(True)
        # self.thirdBGMovie = QMovie("resources/images/third_starsky.gif")
        # self.thirdBG.setMovie(self.thirdBGMovie)
        # self.thirdBGMovie.start()
        self.thirdBG.hide()
        
        # 创建topBar
        self.TopBar = TopBarDisplayWidget(self) 
        # self.TopBar.hide()       
        # 创建BottomBar
        self.BottomBar = BottomBarDisplayWidget(self)
        # 创建左右按钮
        self.leftBtn = ImageButton(GUIDE_BTN_W,GUIDE_BTN_H,"resources/images/leftSingleArrow.png",self)
        self.leftBtn.clicked.connect(self.leftArrowClicked)
        self.leftBtn.move(GUIDE_BTN_W//2, (WINDOW_H - GUIDE_BTN_H)//2)
        self.leftBtn.hide()
        self.rightBtn = ImageButton(GUIDE_BTN_W,GUIDE_BTN_H,"resources/images/rightSingleArrow.png",self)
        self.rightBtn.clicked.connect(self.rightArrowClicked)
        self.rightBtn.move(WINDOW_W - GUIDE_BTN_W - GUIDE_BTN_W//2, (WINDOW_H - GUIDE_BTN_H)//2) 
        self.rightBtn.hide()
        # 创建语音交互图层       
        self.voiceDetectingPage = VoiceDetectingWidget("resources/images/voiceDynamicImage", 100, self)
        self.voiceDetectingPage.hide()
        
        #添加动画效果
        self.AnimationFlash()
        
    def messageHandler(self, text):
        if text == "voice appear":
            print(f"voice appear Received")
            self.voiceDetectingPage.raise_()
            self.voiceDetectingPage.show()   
        elif text == "voice disappear":
            print(f"voice disappear Received")
            self.voiceDetectingPage.hide()
        elif text == "enter sleep":
            print(f"enter sleep Received")
            if self.menu_flag != 3:
                self.sleep_seq = "1"
                self.thirdBGMovie = QMovie(coacherSleepFlashDict[self.SecondMenuIndex][self.sleep_seq])
                self.thirdBG.setMovie(self.thirdBGMovie)
                self.thirdBGMovie.start()
                self.thirdBG.raise_()
                self.afterRaise()
                self.thirdBG.show()
                self.animation_third.start()
        elif text.split(' ')[0] == "sleepAssisting":
            print(f"sleepAssisting")
            if self.menu_flag == 3:
                self.sleep_seq = text.split(' ')[1]
                self.thirdBGMovie = QMovie(coacherSleepFlashDict[self.SecondMenuIndex][self.sleep_seq])
                self.thirdBG.setMovie(self.thirdBGMovie)
                self.thirdBGMovie.start()
                # self.thirdBG.raise_()
                # self.afterRaise()
                # self.thirdBG.show()
                # self.animation_third.start()

    def mousePressEvent(self, event: QMouseEvent):
        # print(f"Mouse clicked")
        super().mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.initBG.show()
            self.animation_init.start() 
            return 
        if self.menu_flag == 0:
            self.firstBG.raise_()
            self.firstMenu.raise_()
            self.afterRaise()
            self.firstBG.show()
            self.animation_first.start() 
        elif self.menu_flag == 1:
            self.ClickStartPos = event.globalPos()
            self.DraggingFlag = True
            self.curr_start = self.firstMenu.pos()
        elif self.menu_flag == 2:
            print("normal clicked")
            # clicked_widget = self.childAt(event.pos())
            # if isinstance(clicked_widget, QPushButton):
            #     return
            self.ClickStartPos = event.globalPos()
            self.DraggingFlag = True
            self.curr_start = self.curr_SecondMenu.pos()
            self.zero_start = self.SecondMenuGrp[0].pos()
        else:
            return
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.DraggingFlag:
            offset = event.globalPos() - self.ClickStartPos
            delta_x = offset.x()
            if self.menu_flag == 1 and (self.curr_start.x() + delta_x) > 0 and (self.curr_start.x() + delta_x) < self.width():
                self.firstMenu.move(self.curr_start.x() + delta_x, 0)
            elif self.menu_flag == 2:
                if delta_x < 0 and self.SecondMenuIndex < len(coacher)-1:
                    # 向左滑 -> 下一张
                    self.curr_SecondMenu.move(self.curr_start.x() + delta_x, 0)
                    self.next_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex+1]
                    self.next_SecondMenu.move(self.curr_start.x() + delta_x + self.width(), 0)
                elif delta_x > 0 and self.SecondMenuIndex > 0:
                    # 向右滑 -> 上一张
                    self.curr_SecondMenu.move(self.curr_start.x() + delta_x, 0)
                    self.next_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex-1]
                    self.next_SecondMenu.move(self.curr_start.x() + delta_x - self.width(), 0)
            
            # else: 
            #     self.DraggingFlag = False
            #     return
                
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if not self.DraggingFlag:
            return
        self.DraggingFlag = False 

        if self.menu_flag == 1:
            end_x = event.globalPos()
            moved_p = end_x - self.ClickStartPos
            moved_x = moved_p.x()
            threshold = self.width() // 4
            if moved_x < 0:
                self.animation_firstMenuIn.setStartValue(self.firstMenu.pos())
                if moved_x < -threshold:
                    self.animation_firstMenuIn.setEndValue(QPoint(0, 0))
                    self.animation_firstMenuIn.setDuration(self.firstMenu.pos().x()//2)#动画时间跟滑动距离成比例，确保速度相同
                    self.animation_firstMenuIn.start()
                else:
                    self.animation_firstMenuIn.setEndValue(QPoint(self.width(), 0))
                    self.animation_firstMenuIn.setDuration(200)#动画时间跟滑动距离成比例，确保速度相同
                    self.animation_firstMenuIn.start()
                    
            elif moved_x > 0:
                self.animation_firstMenuOut.setStartValue(self.firstMenu.pos())
                if moved_x > threshold:
                    self.animation_firstMenuOut.setEndValue(QPoint(self.width(), 0))
                    self.animation_firstMenuOut.setDuration((self.width()-self.firstMenu.pos().x())//2)#动画时间跟滑动距离成比例，确保速度相同
                    self.animation_firstMenuOut.start()
                else:
                    self.animation_firstMenuOut.setEndValue(QPoint(0, 0))
                    self.animation_firstMenuOut.setDuration(200)#动画时间跟滑动距离成比例，确保速度相同
                    self.animation_firstMenuOut.start()
                    
            # elif moved_x == 0:
            #     if self.voiceDetectingPage.isVisible():
            #         self.voiceDetectingPage.hide()   
            #     else:
            #         self.voiceDetectingPage.raise_()
            #         self.voiceDetectingPage.show()           
                
        elif self.menu_flag == 2:
            end_x = self.curr_SecondMenu.pos().x()
            moved_x = end_x - self.curr_start.x()
            threshold = self.width() // 4
            if moved_x < 0:
                if moved_x < -threshold and self.SecondMenuIndex < len(coacher) - 1:
                    self.animate_transition(self.SecondMenuIndex + 1)
                else:
                    self.animate_transition(self.SecondMenuIndex + 1, reset=True) 
            elif moved_x > 0:
                if moved_x > threshold and self.SecondMenuIndex > 0:
                    self.animate_transition(self.SecondMenuIndex - 1)
                else:
                    self.animate_transition(self.SecondMenuIndex - 1, reset=True)
            
    def leftArrowClicked(self):
        if(self.menu_flag == 1):
            self.animation_firstMenuOut.setStartValue(self.firstMenu.pos())
            self.animation_firstMenuOut.setDuration((self.width()-self.firstMenu.pos().x())//2)#动画时间跟滑动距离成比例，确保速度相同
            self.animation_firstMenuOut.start()
            return
        elif(self.menu_flag == 2):
            if(self.SecondMenuIndex > 0):
                self.curr_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex]
                self.next_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex-1]
                self.animate_transition(self.SecondMenuIndex - 1)
            else:
                self.firstBG.raise_()
                self.firstMenu.raise_()
                self.afterRaise()
                self.firstBG.show()
                self.animation_first.start()
                return
        

    def rightArrowClicked(self):
        if(self.menu_flag == 1):
            return
        elif(self.menu_flag == 2 and self.SecondMenuIndex < len(coacher) - 1):
            print("start move")
            self.curr_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex]
            self.next_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex+1]
            self.animate_transition(self.SecondMenuIndex + 1)
            return
        
    def animate_transition(self, new_index, reset=False):
        duration = 300
        if reset:
            # 回弹动画
            self.anim_current = QPropertyAnimation(self.curr_SecondMenu, b"pos")
            self.anim_current.setDuration(duration)
            self.anim_current.setEasingCurve(QEasingCurve.InOutCubic)
            self.anim_current.setStartValue(self.curr_SecondMenu.pos())
            self.anim_current.setEndValue(QPoint(0, 0))
            self.anim_current.start()

            self.anim_next = QPropertyAnimation(self.next_SecondMenu, b"pos")
            self.anim_next.setDuration(duration)
            self.anim_next.setEasingCurve(QEasingCurve.InOutCubic)
            self.anim_next.setStartValue(self.next_SecondMenu.pos())
            self.anim_next.setEndValue(QPoint(self.curr_start.x()+self.width() if new_index > self.SecondMenuIndex else self.curr_start.x()-self.width(), 0))
            self.anim_next.start()
        else:
            # 动画滑动切换
            print(self.curr_SecondMenu.pos())
            self.anim_current = QPropertyAnimation(self.curr_SecondMenu, b"pos")
            self.anim_current.setEasingCurve(QEasingCurve.InOutCubic)
            self.anim_current.setStartValue(self.curr_SecondMenu.pos())
            self.anim_current.setEndValue(QPoint(-self.width() if new_index > self.SecondMenuIndex else self.width(), 0))
            self.anim_current.setDuration(abs(abs(self.curr_SecondMenu.pos().x())-self.width())//2)#动画时间跟滑动距离成比例，确保速度相同
            self.anim_current.start()

            self.anim_next = QPropertyAnimation(self.next_SecondMenu, b"pos")  
            self.anim_next.setEasingCurve(QEasingCurve.InOutCubic)
            self.anim_next.setStartValue(self.next_SecondMenu.pos())
            self.anim_next.setEndValue(QPoint(0, 0))
            self.anim_next.setDuration(abs(self.next_SecondMenu.pos().x())//2)#动画时间跟滑动距离成比例，确保速度相同
            self.anim_next.start()

            self.anim_next.finished.connect(lambda: self.finalize_transition(new_index))

    def finalize_transition(self, new_index):
        print("finished")
        for i in range(len(coacher)):
            if i == self.SecondMenuIndex or i == new_index:
                continue
            self.SecondMenuGrp[i].move(self.zero_start.x() + self.width()*i*(self.SecondMenuIndex - new_index), 0)
        self.SecondMenuIndex = new_index
        self.curr_SecondMenu = self.SecondMenuGrp[self.SecondMenuIndex]
        if self.SecondMenuIndex == len(coacher) - 1:
            if self.SecondMenuIndex == 0:
                self.leftBtn.image = QPixmap("resources/images/leftSingleArrow.png")
            else:
                self.leftBtn.image = QPixmap("resources/images/leftDoubleArrow.png")
            self.leftBtn.show()
            self.rightBtn.hide()
        elif self.SecondMenuIndex == 0:
            self.leftBtn.image = QPixmap("resources/images/leftSingleArrow.png")
            self.leftBtn.show()
            self.rightBtn.image = QPixmap("resources/images/rightDoubleArrow.png")
            self.rightBtn.show()
        else:
            self.leftBtn.image = QPixmap("resources/images/leftDoubleArrow.png")
            self.leftBtn.show()
            self.rightBtn.image = QPixmap("resources/images/rightDoubleArrow.png")
            self.rightBtn.show()
        
    
    def AnimationFlash(self):
        #锁屏背景淡入动画
        self.initEffect = QGraphicsOpacityEffect()
        self.animation_init = QPropertyAnimation(self.initEffect, b"opacity")
        self.animation_init.setDuration(1000)  # 1秒淡入
        self.animation_init.setStartValue(0)
        self.animation_init.setEndValue(1) 
        self.animation_init.finished.connect(self.init_finish_switch) 
        self.initBG.setGraphicsEffect(self.initEffect)      
        #一级菜单背景淡入动画
        self.effect = QGraphicsOpacityEffect()
        self.firstBG.setGraphicsEffect(self.effect)
        self.animation_first = QPropertyAnimation(self.effect, b"opacity")
        self.animation_first.setDuration(1000)  # 1秒淡入
        self.animation_first.setStartValue(0)
        self.animation_first.setEndValue(1)
        self.animation_first.finished.connect(self.First_finish_switch)
        #一级菜单组件滑动入场动画       
        self.animation_firstMenuIn = QPropertyAnimation(self.firstMenu, b"pos")
        self.animation_firstMenuIn.setDuration(300)
        self.animation_firstMenuIn.setEasingCurve(QEasingCurve.InOutCubic)
        # self.animation_firstMenuIn.setStartValue(self.firstMenu.pos())
        self.animation_firstMenuIn.setEndValue(QPoint(0, 0))
        self.animation_firstMenuIn.finished.connect(self.FirstMenu_finish_switch)
        #一级菜单组件滑动出场动画
        self.animation_firstMenuOut = QPropertyAnimation(self.firstMenu, b"pos")
        self.animation_firstMenuOut.setDuration(300)
        self.animation_firstMenuOut.setEasingCurve(QEasingCurve.InOutCubic)
        # self.animation_firstMenuOut.setStartValue(self.firstMenu.pos())
        self.animation_firstMenuOut.setEndValue(QPoint(self.width(), 0))
        self.animation_firstMenuOut.finished.connect(self.FirstMenu_finish_switch)
        #二级页面淡入动画
        self.secondEffect = QGraphicsOpacityEffect()
        self.SecondMenuGrp[0].setGraphicsEffect(self.secondEffect)
        self.animation_second = QPropertyAnimation(self.secondEffect, b"opacity")
        self.animation_second.setDuration(1000)  # 1秒淡入
        self.animation_second.setStartValue(0)
        self.animation_second.setEndValue(1)
        self.animation_second.finished.connect(self.Second_finish_switch)
        #三级场景淡入动画
        self.thirdEffect = QGraphicsOpacityEffect()
        self.animation_third = QPropertyAnimation(self.thirdEffect, b"opacity")
        self.animation_third.setDuration(1000)  # 1秒淡入
        self.animation_third.setStartValue(0)
        self.animation_third.setEndValue(1) 
        self.animation_third.finished.connect(self.Third_finish_switch) 
        self.thirdBG.setGraphicsEffect(self.thirdEffect)
                
    
    def init_finish_switch(self):
        if self.menu_flag == 1:
            self.firstBG.hide()
            self.firstMenu.hide()
            self.TopBar.time_label.hide()
            self.leftBtn.hide()
            self.rightBtn.hide()
            self.BottomBar.date_label.show()
            self.BottomBar.time_label.show()
            # self.BottomBar.playbutton.hide()
            self.BottomBar.show()
        self.menu_flag = 0
        
    def First_finish_switch(self):
        if self.menu_flag == 0:
            self.initBG.hide()
            self.firstMenu.show()
        elif self.menu_flag == 2:
            self.leftBtn.show()
            self.BottomBar.hide()
            self.BottomBar.date_label.show()
            self.BottomBar.time_label.show()
            self.BottomBar.playbutton.hide()
            self.rightBtn.hide()
            self.curr_SecondMenu.hide()
        self.menu_flag = 1
        
    def FirstMenu_finish_switch(self):
        if self.firstMenu.pos().x() == 0:
            # print(self.firstMenu.pos().x())
            self.BottomBar.hide()
            self.TopBar.time_label.show()
            self.leftBtn.image = QPixmap("resources/images/leftSingleArrow.png")
            self.leftBtn.show()
        else:
            self.leftBtn.hide()
            self.TopBar.time_label.hide()
            self.BottomBar.show()
        
    def Second_finish_switch(self):
        if self.menu_flag == 1:
            self.BottomBar.date_label.hide()
            self.BottomBar.time_label.hide()
            self.BottomBar.playbutton.show()
            self.BottomBar.show()
            self.leftBtn.image = QPixmap("resources/images/leftSingleArrow.png")
            self.leftBtn.show()
            self.rightBtn.image = QPixmap("resources/images/rightDoubleArrow.png")
            self.rightBtn.show()
            self.menu_flag = 2
            
    def Third_finish_switch(self):
        # if self.menu_flag != 2:
        self.TopBar.time_label.show()
        self.TopBar.status_label.show()
        self.BottomBar.date_label.hide()
        self.BottomBar.time_label.hide()
        self.BottomBar.playbutton.hide()
        self.BottomBar.stopbutton.show()
        self.leftBtn.hide()
        self.rightBtn.hide()
        self.curr_SecondMenu.hide()
        self.menu_flag = 3      
        
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            QApplication.quit()
            
    def afterRaise(self):
        self.TopBar.raise_()
        self.BottomBar.raise_()
        self.leftBtn.raise_()
        self.rightBtn.raise_()
            
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    
    
