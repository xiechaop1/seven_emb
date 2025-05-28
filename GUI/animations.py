from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,  QGraphicsBlurEffect, QLabel, QGraphicsOpacityEffect, QPushButton, QStackedWidget, QFrame
from PyQt5.QtCore import Qt, QRect
import os
os.environ["QT_QPA_PLATFORM"] = "xcb"


class fadeAnimation:
    def __init__(self, duration, callback):
        self.Effect = QGraphicsOpacityEffect()
        self.animation = QPropertyAnimation(self.Effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1) 
        self.animation.finished.connect(callback)