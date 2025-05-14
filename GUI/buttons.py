from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QRect
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

class CustomButton(QPushButton):
    def __init__(self, btn_w, btn_h, parent=None):
        super().__init__(parent)
        self.resize(btn_w, btn_h)  # 设置按钮的大小
        self.setStyleSheet("border: none;")  # 移除默认的边框
        self.btn_w = btn_w
        self.btn_h = btn_h
        # self.enterCnt = 0
        # self.leaveCnt = 0
        
       # 创建缩放动画
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # 动画持续时间 300ms
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # 缓动效果

        # 默认的大小和位置
        self.normal_size = self.geometry()
        self.animating = False  # 动画状态标志

        # 连接动画的finished信号来恢复动画状态
        self.animation.finished.connect(self.animation_finished)

    def enterEvent(self, event):
        """鼠标悬停事件触发时，启动缩放动画"""
        if self.animating:
            # self.enterCnt = self.enterCnt + 1
            print('test1')
            return  # 如果正在进行动画，忽略本次事件

        # 修改按钮大小
        g = self.geometry()
        # self.animation.stop()
        self.animation.setStartValue(g)
        self.animation.setEndValue(g.adjusted(-self.btn_w//10, -self.btn_h//10, self.btn_w//10, self.btn_h//10))
        self.animation.start()
        # super().enterEvent(event)
        self.animating = True  # 标记动画正在进行中

    def leaveEvent(self, event):
        """鼠标离开事件触发时，恢复原来的大小"""
        if self.animating:
            # self.leaveCnt = self.leaveCnt + 1
            print('test2')
            return  # 如果正在进行动画，忽略本次事件

        g = self.geometry()
        # self.animation.stop()
        self.animation.setStartValue(g)
        self.animation.setEndValue(g.adjusted(self.btn_w//10, self.btn_h//10, -self.btn_w//10, -self.btn_h//10))
        self.animation.start()
        # super().leaveEvent(event)
        self.animating = True  # 标记动画正在进行中

    def animation_finished(self):
        """动画结束时恢复状态"""
        g = self.geometry()
        # print(g.width())
        if g.width() == self.btn_w:
            # if (self.enterCnt - self.leaveCnt) == 1:
            if self.underMouse():
                print('ani_test1')
                self.animation.setStartValue(g)
                self.animation.setEndValue(g.adjusted(-self.btn_w//10, -self.btn_h//10, self.btn_w//10, self.btn_h//10))
                self.animation.start()
                # self.enterCnt = 0
                # self.leaveCnt = 0
                return
        elif g.width() == self.btn_w*1.2:
            # if (self.enterCnt - self.leaveCnt) == -1:
            if not self.underMouse():
                print('ani_test2')
                self.animation.setStartValue(g)
                self.animation.setEndValue(g.adjusted(self.btn_w//10, self.btn_h//10, -self.btn_w//10, -self.btn_h//10))
                self.animation.start()
                # self.enterCnt = 0
                # self.leaveCnt = 0
                return
        self.animating = False  # 结束动画，恢复为可触发状态

    def paintEvent(self, event):
        # 获取 QPainter 对象
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿

        # 设置按钮颜色
        normal_color = QColor(0, 0, 0)  # 按钮的正常颜色
        hover_color = QColor(100, 149, 237)  # 悬停时的颜色
        press_color = QColor(30, 144, 255)   # 按下时的颜色
        color = normal_color
        self.font = QFont("PingFang SC Regular")
        self.font.setPointSize(self.height()//3)
        
        # 设置背景颜色，根据按钮的状态
        if self.isDown():  # 按钮按下时
            color = press_color
        elif self.underMouse():  # 鼠标悬停时
            color = hover_color
        else:
            color = normal_color
        
        # 绘制圆形背景
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)  # 去掉边框
        painter.drawRoundedRect(0,0,self.width(), self.height(), self.height()//2, self.height()//2)
        # 设置按钮文本
        painter.setPen(QPen(Qt.white))  # 设置文本颜色为白色
        painter.setFont(self.font)  # 使用默认字体
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())  # 绘制按钮文本

        painter.end()
        
class ImageButton(QPushButton):
    def __init__(self, btn_w, btn_h, imagePath, parent=None):
        super().__init__(parent)
        self.resize(btn_w, btn_h)  # 设置按钮的大小
        self.setStyleSheet("border: none;")  # 移除默认的边框
        self.btn_w = btn_w
        self.btn_h = btn_h
        self.image = QPixmap(imagePath)
        self.image = self.image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        
       # 创建缩放动画
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # 动画持续时间 300ms
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # 缓动效果

        # 默认的大小和位置
        self.normal_size = self.geometry()
        self.animating = False  # 动画状态标志

        # 连接动画的finished信号来恢复动画状态
        self.animation.finished.connect(self.animation_finished)

    def enterEvent(self, event):
        """鼠标悬停事件触发时，启动缩放动画"""
        if self.animating:
            # self.enterCnt = self.enterCnt + 1
            print('enter ignored')
            return  # 如果正在进行动画，忽略本次事件

        # 修改按钮大小
        g = self.geometry()
        # self.animation.stop()
        self.animation.setStartValue(g)
        self.animation.setEndValue(g.adjusted(-self.btn_w//10, -self.btn_h//10, self.btn_w//10, self.btn_h//10))
        self.animation.start()
        print('enter animation start')
        # super().enterEvent(event)
        self.animating = True  # 标记动画正在进行中

    def leaveEvent(self, event):
        """鼠标离开事件触发时，恢复原来的大小"""
        if self.animating:
            # self.leaveCnt = self.leaveCnt + 1
            print('leave ignored')
            return  # 如果正在进行动画，忽略本次事件

        g = self.geometry()
        # self.animation.stop()
        self.animation.setStartValue(g)
        self.animation.setEndValue(g.adjusted(self.btn_w//10, self.btn_h//10, -self.btn_w//10, -self.btn_h//10))
        self.animation.start()
        print('leave animation start')
        # super().leaveEvent(event)
        self.animating = True  # 标记动画正在进行中

    def animation_finished(self):
        """动画结束时恢复状态"""
        g = self.geometry()
        print("animation finished")
        print(g.width())
        if g.width() == self.btn_w:
            # if (self.enterCnt - self.leaveCnt) == 1:
            print("ready to calib")
            if self.underMouse():
                # print('ani_test1')
                self.animation.setStartValue(g)
                self.animation.setEndValue(g.adjusted(-self.btn_w//10, -self.btn_h//10, self.btn_w//10, self.btn_h//10))
                self.animation.start()
                print('enter calib start')
                # self.enterCnt = 0
                # self.leaveCnt = 0
                return
        elif g.width() == self.btn_w*1.2:
            # if (self.enterCnt - self.leaveCnt) == -1:
            print("ready to calib")
            if not self.underMouse():
                # print('ani_test2')
                self.animation.setStartValue(g)
                self.animation.setEndValue(g.adjusted(self.btn_w//10, self.btn_h//10, -self.btn_w//10, -self.btn_h//10))
                self.animation.start()
                print('leave calib start')
                # self.enterCnt = 0
                # self.leaveCnt = 0
                return
        self.animating = False  # 结束动画，恢复为可触发状态

    def paintEvent(self, event):
        # 获取 QPainter 对象
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        self.scaledimage = self.image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, self.scaledimage)

        painter.end()