import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QDialog, QTimeEdit, QComboBox, QMessageBox, QScrollArea, QFrame, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt, QTime, QDateTime, QSize, QTimer, Signal, QUrl, Property
from PySide6.QtGui import QIcon, QFont, QColor, QPainter, QImage, QPixmap, QPalette
from PySide6.QtQuickWidgets import QQuickWidget
from model.scheduler import TaskDaemon, TaskType, TaskScheduleType, Task
from datetime import time, datetime
import json
import os
import logging
from common.code import Code
from model.task import Task, TaskStatus, TaskScheduleType, TaskType, TaskAction, ActionType, LightCommand, SoundCommand, DisplayCommand

class AlarmItem(QWidget):
    def __init__(self, task, task_daemon, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_daemon = task_daemon
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(80)
        self.setStyleSheet("background: #000000;")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # 左侧：时间和标签
        time_layout = QVBoxLayout()
        time_layout.setSpacing(0)
        time_str = self.task.execution_time.split()[1][:5] if ' ' in self.task.execution_time else self.task.execution_time[:5]
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #d1d1d6; font-size: 48px; font-weight: 300; padding-left: 24px;")
        desc_label = QLabel(self.task.name or "闹钟")
        desc_label.setStyleSheet("color: #8e8e93; font-size: 16px; font-weight: 400; padding-left: 24px;")
        time_layout.addWidget(time_label)
        time_layout.addWidget(desc_label)
        time_layout.addStretch()
        # 中间：iOS风格QML开关
        self.switch_widget = QQuickWidget()
        self.switch_widget.setSource(QUrl.fromLocalFile(os.path.abspath("IosSwitch.qml")))
        self.switch_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.switch_widget.setFixedSize(52, 32)
        root = self.switch_widget.rootObject()
        if root is not None:
            root.setProperty("checked", self.task.is_enabled)
            root.toggled.connect(self.toggle_alarm)
        # 右侧：iOS风格删除按钮
        delete_btn = QPushButton("X")
        delete_btn.setFixedSize(36, 36)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 24px;
                font-family: 'PingFang SC', 'SF Pro Display', Arial, sans-serif;
                font-weight: bold;
                padding: 0;
                margin-right: 20px;
            }
            QPushButton:hover {
                background-color: #ff6259;
            }
            QPushButton:pressed {
                background-color: #d70015;
            }
        """)
        delete_btn.clicked.connect(self.delete_alarm)
        # 布局调整
        layout.addLayout(time_layout, 2)
        layout.addStretch(1)
        layout.addWidget(self.switch_widget, 0, Qt.AlignVCenter)
        layout.addSpacing(16)
        layout.addWidget(delete_btn, 0, Qt.AlignVCenter)
        self.setLayout(layout)
        # 分割线
        line = QFrame(self)
        line.setGeometry(24, 79, self.width()-48, 1)
        line.setStyleSheet("background: #222222;")
        line.show()
        
    def toggle_alarm(self, checked):
        try:
            self.task_daemon.toggle_task(
                task_id=self.task.id,
                enable=checked
            )
        except Exception as e:
            logging.error(f"切换闹钟状态失败: {str(e)}")
            # 恢复按钮状态
            root = self.switch_widget.rootObject()
            if root is not None:
                root.setProperty("checked", not checked)
            
    def delete_alarm(self):
        try:
            self.task_daemon.scheduler.remove_task(self.task.id)
            self.task_daemon.save_tasks()
            self.deleteLater()
        except Exception as e:
            logging.error(f"删除闹钟失败: {str(e)}")

class AddAlarmDialog(QDialog):
    def __init__(self, task_daemon, parent=None):
        super().__init__(parent)
        self.task_daemon = task_daemon
        # 全屏显示
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background: #18181a;")
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部栏
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 16, 16, 0)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("color: #ff9500; font-size: 18px; font-family: 'PingFang SC'; background: transparent; border: none;")
        cancel_btn.clicked.connect(self.reject)
        title = QLabel("Add Alert")
        title.setStyleSheet("color: white; font-size: 20px; font-family: 'PingFang SC'; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        save_btn = QPushButton("存储")
        save_btn.setStyleSheet("color: #ff9500; font-size: 18px; font-family: 'PingFang SC'; background: transparent; border: none;")
        save_btn.clicked.connect(self.save_alarm)
        top_bar.addWidget(cancel_btn)
        top_bar.addStretch()
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(save_btn)
        main_layout.addLayout(top_bar)

        # 时间选择（QML滚轮）
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 24, 0, 0)
        time_layout.setSpacing(0)
        self.qml_widget = QQuickWidget()
        self.qml_widget.setSource(QUrl.fromLocalFile(os.path.abspath("TimePicker.qml")))
        self.qml_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        # 设置QML时间为当前时间
        now = datetime.now()
        root = self.qml_widget.rootObject()
        if root is not None:
            root.setProperty("hour", now.hour)
            root.setProperty("minute", now.minute)
        time_layout.addStretch(1)
        time_layout.addWidget(self.qml_widget)
        time_layout.addStretch(1)
        main_layout.addLayout(time_layout)

        # 选项区块
        option_box = QFrame()
        option_box.setStyleSheet("background: #232325; border-radius: 16px;")
        option_layout = QVBoxLayout()
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setSpacing(0)
        # 选项内容
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["Once", "Daily", "Workday", "Weekend", "Weekly"])
        self.repeat_combo.setStyleSheet("""
            QComboBox {
                color: #d1d1d6;
                background: transparent;
                width: 160px;
                font-size: 18px;
                border: none;
                padding: 8px 0 8px 0;
            }
            QComboBox QAbstractItemView {
                background: #18181a;
                color: white;
                border: none;
                outline: 0;
                margin: 0;
                padding: 0;
                selection-background-color: #ff9500;
                selection-color: white;
            }
            QComboBox QListView {
                background: #18181a;
                border: none;
                outline: 0;
                margin: 0;
                padding: 0;
            }
            QComboBox QScrollBar:vertical {
                background: #18181a;
                width: 0px;
            }
            QComboBox QFrame {
                background: #18181a;
                border: none;
            }
        """)
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(["None", "Soft", "Active"])
        self.sound_combo.setStyleSheet(self.repeat_combo.styleSheet())
        self.light_combo = QComboBox()
        self.light_combo.addItems(["None", "Breathing", "Colorful"])
        self.light_combo.setStyleSheet(self.repeat_combo.styleSheet())
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(["None", "Sunrise", "Sunset", "Moon"])
        self.screen_combo.setStyleSheet(self.repeat_combo.styleSheet())
        self.scent_combo = QComboBox()
        self.scent_combo.addItems(["Off", "On"])
        self.scent_combo.setStyleSheet(self.repeat_combo.styleSheet())
        # 行生成函数
        def add_option_row(label, widget, divider=True):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)
            lab = QLabel(label)
            lab.setStyleSheet("color: #d1d1d6; font-size: 18px; padding-left: 20px;")
            row.addWidget(lab)
            row.addStretch()
            row.addWidget(widget)
            option_layout.addLayout(row)
            if divider:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet("background: #18181a; min-height: 1px; max-height: 1px; border: none;")
                option_layout.addWidget(line)
        add_option_row("Repeat", self.repeat_combo)
        add_option_row("Sound", self.sound_combo)
        add_option_row("Light", self.light_combo)
        add_option_row("Display", self.screen_combo)
        add_option_row("Spray", self.scent_combo, divider=False)
        option_box.setLayout(option_layout)
        main_layout.addSpacing(24)
        main_layout.addWidget(option_box)
        self.setLayout(main_layout)

    def get_alarm_data(self):
        # 从QML获取时间
        root = self.qml_widget.rootObject()
        hour = int(root.property("hour"))
        minute = int(root.property("minute"))
        time_str = f"{hour:02d}:{minute:02d}"
        repeat_map = {"Once": "once", "Daily": "daily", "Workday": "workday", "Weekend": "weekend", "Weekly": "weekly"}
        repeat = repeat_map.get(self.repeat_combo.currentText(), "once")
        actions = []
        # 声音
        sound_map = {"None": None, "Soft": ("gentle.mp3", 80), "Active": ("intense.mp3", 100)}
        sound_effect = sound_map.get(self.sound_combo.currentText())
        if sound_effect:
            file_path, volume = sound_effect
            actions.append({"action_type": ActionType.SOUND, "target": "sound", "parameters": {"file_path": file_path, "volume": volume}})
        # 灯光
        light_map = {"None": None, "Breathing": (Code.LIGHT_MODE_BREATHING, {"r": "128", "g": 128, "b": 0, "steps": 200}), "Colorful": (Code.LIGHT_MODE_SECTOR_FLOWING, {"mode": "colorful"})}
        light_effect = light_map.get(self.light_combo.currentText())
        if light_effect:
            mode, params = light_effect
            actions.append({"action_type": ActionType.LIGHT, "target": "light", "parameters": {"mode": mode, "params": params}})
        # 屏幕
        screen_map = {"None": None, "Sunrise": ("animation", {"type": "sunrise", "duration": 300}), "Sunset": ("animation", {"type": "sunset", "duration": 300}), "Moon": ("animation", {"type": "moon", "duration": 300})}
        screen_effect = screen_map.get(self.screen_combo.currentText())
        if screen_effect:
            mode, params = screen_effect
            actions.append({"action_type": ActionType.DISPLAY, "target": "screen", "parameters": {"mode": mode, "params": params}})
        # 香氛
        scent_map = {"Off": None, "On": ("forest", 5)}
        scent_effect = scent_map.get(self.scent_combo.currentText())
        if scent_effect:
            mode, duration = scent_effect
            actions.append({"action_type": ActionType.SPRAY, "target": "spray", "parameters": {"mode": mode, "duration": duration}})
        return {"time": time_str, "frequency": repeat, "enabled": True, "actions": actions}

    def save_alarm(self):
        try:
            # 获取闹钟数据
            alarm_data = self.get_alarm_data()
            
            # 创建闹钟任务
            execution_time = time(
                hour=int(alarm_data['time'].split(':')[0]),
                minute=int(alarm_data['time'].split(':')[1])
            )
            
            # 使用TaskDaemon的方法创建闹钟
            self.task_daemon.create_alarm_task(
                name=f"闹钟 {alarm_data['time']}",
                execution_time=execution_time,
                parameters=alarm_data['actions'],
                duration=60
            )
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            logging.error(f"保存闹钟失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"保存闹钟失败: {str(e)}")

class AlarmWidget(QWidget):
    def __init__(self, task_daemon, parent=None):
        super().__init__(parent)
        self.task_daemon = task_daemon
        self.setup_ui()
        self.refresh_alarms()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
            QLabel, QCheckBox, QPushButton {
                font-family: 'PingFang SC', 'SF Pro Display', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContent {
                background-color: #000000;
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部栏
        title_bar = QWidget()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet("background: #000000;")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(16, 0, 16, 0)
        title_layout.setSpacing(0)
        # title_layout.addWidget(edit_label)
        # title_layout.addStretch()
        title = QLabel("闹钟")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        title_layout.addStretch()
        title_layout.addWidget(title, 0, Qt.AlignCenter)
        title_layout.addStretch()
        add_btn = QPushButton("")
        add_btn.setFixedSize(36, 36)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9500;
                color: white;
                border: none;
                border-radius: 18px;
            }
            QPushButton::before {
                content: '+';
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        add_btn.setText("+")
        add_btn.setFont(QFont('PingFang SC', 28, QFont.Bold))
        add_btn.clicked.connect(self.show_add_dialog)
        title_layout.addWidget(add_btn)
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)

        # 闹钟列表 - 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        self.alarm_list = QVBoxLayout()
        self.alarm_list.setSpacing(0)
        self.alarm_list.setContentsMargins(0, 0, 0, 0)
        scroll_content.setLayout(self.alarm_list)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
    def refresh_alarms(self):
        # 清除现有闹钟
        while self.alarm_list.count():
            item = self.alarm_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 获取所有闹钟任务
        try:
            tasks = self.task_daemon.get_alarm_tasks()
            if tasks:
                for task in tasks:
                    alarm_item = AlarmItem(task, self.task_daemon)
                    self.alarm_list.addWidget(alarm_item)
            # 添加弹性空间
            self.alarm_list.addStretch()
        except Exception as e:
            logging.error(f"刷新闹钟列表失败: {str(e)}")
            
    def show_add_dialog(self):
        dialog = AddAlarmDialog(self.task_daemon, self)
        dialog.setModal(True)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_alarms() 