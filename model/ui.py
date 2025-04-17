import sys
import os
import vlc
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QStackedWidget, QHBoxLayout, QGraphicsOpacityEffect, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation, QRect, QPoint, QTimer
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
        print("[DEBUG] show_overlay called")
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
            btn.installEventFilter(self)
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
        self.overlay.setGeometry(self.rect())
        self.overlay.raise_()

        # 模拟语音触发
        self.voice_btn = QPushButton("模拟语音触发", self)
        self.voice_btn.raise_()
        self.voice_btn.show()
        self.voice_btn.move(10, 550)
        self.voice_btn.clicked.connect(lambda: print("[DEBUG] button clicked") or self.overlay.show_overlay())

        self.player = None
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        # self.set_video_background("resources/video/main.mp4")
        self.play_video("resource/video/main.mp4")

        # self.showFullScreen()         # 全屏
        self.resize(800, 600)
        self.show()
        self.start_pos = None
        self.end_pos = None

    def play_video(self, video_path):
        self.player = self.media_player
        media = self.vlc_instance.media_new(video_path)
        self.player.stop()
        self.player.set_media(media)
        self.player.play()

        self.stack.setParent(self)
        self.stack.raise_()
        self.overlay.setParent(self)
        self.overlay.raise_()

        self.voice_btn.setParent(self)
        self.voice_btn.raise_()
        self.voice_btn.show()


    def set_video_background(self, path):
        print("[DEBUG] set_video_background called with path:", path)
        if not hasattr(self, 'vlc_instance'):
            self.vlc_instance = vlc.Instance("--aout", "dummy")
            self.vlc_widget = QFrame(self)
            self.vlc_widget.setGeometry(0, 0, self.width(), self.height())
            self.setCentralWidget(self.vlc_widget)
            self.vlc_widget.show()

            self.vlc_player = self.vlc_instance.media_player_new()

            def delayed_bind():
                print("[DEBUG] winId after show:", int(self.vlc_widget.winId()))
                self.vlc_player.set_xwindow(int(self.vlc_widget.winId()))

            QTimer.singleShot(0, delayed_bind)
        else:
            self.vlc_player.stop()

        media = self.vlc_instance.media_new(os.path.abspath(path))
        self.vlc_player.set_media(media)
        def on_media_state_changed(event):
            state = self.vlc_player.get_state()
            print("[VLC STATE] Current state:", state)

        self.vlc_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerMediaChanged, on_media_state_changed
        )
        print("[DEBUG] Media type:", media.get_mrl())
        print("[DEBUG] media set:", os.path.abspath(path))
        print("[DEBUG] player.play() returned:", self.vlc_player.play())
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEncounteredError, lambda e: print("[VLC ERROR] Playback error"))
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, lambda e: print("[VLC STATE] Playing"))
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped, lambda e: print("[VLC STATE] Stopped"))

        self.vlc_player.play()

        self.stack.setParent(self)
        self.stack.raise_()
        self.overlay.setParent(self)
        self.overlay.raise_()

        self.voice_btn.setParent(self)
        self.voice_btn.raise_()
        self.voice_btn.show()

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
            self.play_video("resources/video/main.mp4")
        else:
            self.play_video(f"resources/video/scene{index}.mp4")

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.start_widget = self.stack.currentWidget()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            dx = event.pos().x() - self.start_pos.x()
            current_index = self.stack.currentIndex()

            # Limit drag distance for elasticity
            if abs(dx) > self.width():
                dx = self.width() * (1 if dx > 0 else -1)

            # Determine direction
            if dx > 0 and current_index < self.stack.count() - 1:
                next_index = current_index + 1
            elif dx < 0 and current_index > 0:
                next_index = current_index - 1
            else:
                return

            # Prepare widgets for elastic drag effect
            next_widget = self.stack.widget(next_index)
            next_widget.setGeometry(dx if dx > 0 else dx + self.width(), 0, self.width(), self.height())
            next_widget.show()
            self.start_widget.move(dx, 0)

            # Mark dragging is active
            self.dragging = True
            self.drag_next_index = next_index

    def mouseReleaseEvent(self, event):
        if not self.start_pos:
            return

        dx = event.pos().x() - self.start_pos.x()
        threshold = self.width() // 3
        current_index = self.stack.currentIndex()

        if hasattr(self, 'dragging') and self.dragging and abs(dx) > threshold:
            # If the swipe is enough to switch pages
            self.switch_page(self.drag_next_index)
        elif hasattr(self, 'dragging') and self.dragging:
            # Smooth bounce back animation if the swipe is below threshold
            anim = QPropertyAnimation(self.start_widget, b"pos")
            anim.setDuration(300)
            anim.setStartValue(self.start_widget.pos())
            anim.setEndValue(QPoint(0, 0))
            anim.start()

            # Revert widget positions after bounce back
            self.stack.widget(self.drag_next_index).hide()
            self.start_widget.setGeometry(0, 0, self.width(), self.height())

        self.start_pos = None
        self.end_pos = None
        self.dragging = False

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton):
            if event.type() == event.Enter:
                anim = QPropertyAnimation(obj, b"geometry")
                anim.setDuration(150)
                rect = obj.geometry()
                anim.setStartValue(rect)
                anim.setEndValue(QRect(rect.x() - 5, rect.y() - 5, rect.width() + 10, rect.height() + 10))
                anim.start()
                obj._hover_anim = anim  # prevent garbage collection
            elif event.type() == event.Leave:
                anim = QPropertyAnimation(obj, b"geometry")
                anim.setDuration(150)
                rect = obj.geometry()
                anim.setStartValue(rect)
                anim.setEndValue(QRect(rect.x() + 5, rect.y() + 5, rect.width() - 10, rect.height() - 10))
                anim.start()
                obj._hover_anim = anim
        return super().eventFilter(obj, event)