import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QStackedWidget, QHBoxLayout, QGraphicsOpacityEffect, QLabel
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation, QRect, QPoint
from PyQt5.QtGui import QMovie

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.setGeometry(parent.rect())
        self.hide()

        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.opacity_anim = QPropertyAnimation(self.effect, b"opacity")
        parent.installEventFilter(self)

        self.floating = QWidget(self)
        self.floating.setStyleSheet("background-color: rgba(255, 255, 255, 180); border-radius: 15px;")
        self.floating.setGeometry(0, self.height(), self.width(), 200)
        self.floating.hide()

    def show_overlay(self):
        self.show()
        self.floating.show()
        self.floating.raise_()
        self.opacity_anim.stop()
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()

        anim = QPropertyAnimation(self.floating, b"geometry")
        anim.setDuration(300)
        anim.setStartValue(QRect(0, self.height(), self.width(), 200))
        anim.setEndValue(QRect(0, self.height() - 200, self.width(), 200))
        anim.start()
        self.anim = anim

    def hide_overlay(self):
        self.opacity_anim.stop()
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(1)
        self.opacity_anim.setEndValue(0)
        self.opacity_anim.start()

        anim = QPropertyAnimation(self.floating, b"geometry")
        anim.setDuration(300)
        anim.setStartValue(QRect(0, self.height() - 200, self.width(), 200))
        anim.setEndValue(QRect(0, self.height(), self.width(), 200))
        anim.finished.connect(self._finalize_hide)
        anim.start()
        self.anim = anim

    def _finalize_hide(self):
        self.hide()
        self.floating.hide()

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress and self.isVisible():
            if not self.floating.geometry().contains(event.pos()):
                self.hide_overlay()
        return super().eventFilter(obj, event)

class HomePage(QWidget):
    def __init__(self, switch_page_func):
        super().__init__()
        layout = QVBoxLayout()
        for i in range(3):
            btn = QPushButton()
            btn.setFixedSize(150, 100)
            btn.setStyleSheet(f"border-image: url(resources/images/button_{i+1}.png);")
            btn.clicked.connect(lambda _, idx=i: switch_page_func(idx + 1))
            layout.addWidget(btn)
        self.setLayout(layout)

class ScenePage(QWidget):
    def __init__(self, index, go_back_func):
        super().__init__()
        layout = QVBoxLayout()
        label = QPushButton(f"这是场景 {index}")
        back_btn = QPushButton("返回")
        back_btn.clicked.connect(go_back_func)
        layout.addWidget(label)
        layout.addWidget(back_btn)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt 动态界面 Demo")
        self.setGeometry(100, 100, 800, 600)

        # 页面容器
        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 800, 600)
        self.home_page = HomePage(self.switch_page)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(ScenePage(1, lambda: self.switch_page(0)))
        self.stack.addWidget(ScenePage(2, lambda: self.switch_page(0)))
        self.stack.addWidget(ScenePage(3, lambda: self.switch_page(0)))
        self.stack.raise_()

        # 浮层遮罩
        self.overlay = OverlayWidget(self)
        self.overlay.raise_()

        # 模拟语音触发
        voice_btn = QPushButton("模拟语音触发", self)
        voice_btn.move(10, 550)
        voice_btn.clicked.connect(self.overlay.show_overlay)
        voice_btn.raise_()

        self.set_video_background("resources/video/main.mp4")
        self.showFullScreen()

    def set_video_background(self, path):
        if hasattr(self, 'player'):
            self.player.stop()
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(path))))
            self.player.play()
        else:
            self.video_widget = QVideoWidget(self)
            self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            self.player.setVideoOutput(self.video_widget)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(path))))
            self.video_widget.setGeometry(0, 0, self.width(), self.height())
            self.setCentralWidget(self.video_widget)
            self.player.play()

    def switch_page(self, index):
        current_index = self.stack.currentIndex()
        if current_index == index:
            return

        current_widget = self.stack.currentWidget()
        next_widget = self.stack.widget(index)

        direction = -1 if index > current_index else 1
        offset_x = direction * self.stack.width()

        next_widget.setGeometry(offset_x, 0, self.stack.width(), self.stack.height())
        next_widget.show()

        anim_current = QPropertyAnimation(current_widget, b"pos")
        anim_current.setDuration(300)
        anim_current.setStartValue(QPoint(0, 0))
        anim_current.setEndValue(QPoint(-offset_x, 0))

        anim_next = QPropertyAnimation(next_widget, b"pos")
        anim_next.setDuration(300)
        anim_next.setStartValue(QPoint(offset_x, 0))
        anim_next.setEndValue(QPoint(0, 0))

        anim_current.start()
        anim_next.start()

        self.anim_current = anim_current
        self.anim_next = anim_next

        self.stack.setCurrentIndex(index)

        if index == 0:
            self.set_video_background("resources/video/main.mp4")
        else:
            self.set_video_background(f"resources/video/scene{index}.mp4")