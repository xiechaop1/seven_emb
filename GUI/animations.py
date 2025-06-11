from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,  QGraphicsBlurEffect, QLabel, QGraphicsOpacityEffect, QPushButton, QStackedWidget, QFrame
from PySide6.QtCore import Qt, QRect
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