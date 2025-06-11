import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QListWidget, 
                           QDialog, QTimeEdit, QComboBox, QMessageBox, QScrollArea, QFrame, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QTime, QDateTime, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QImage, QPixmap, QPalette
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
        # 中间：iOS风格开关按钮
        self.toggle_btn = QCheckBox()
        self.toggle_btn.setChecked(self.task.is_enabled)
        self.toggle_btn.setStyleSheet("""
            QCheckBox::indicator {
                width: 52px;
                height: 32px;
                border-radius: 16px;
                background: #393939;
                margin-right: 32px;
                margin-left: 32px;
            }
            QCheckBox::indicator:unchecked {
                background: #393939;
                border: none;
            }
            QCheckBox::indicator:checked {
                background: #393939;
                border: none;
            }
            QCheckBox::indicator:unchecked::before, QCheckBox::indicator:checked::before {
                content: '';
                position: absolute;
                top: 4px;
                width: 24px;
                height: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                transition: left 0.2s, background 0.2s;
            }
            QCheckBox::indicator:unchecked::before {
                left: 4px;
                background: white;
            }
            QCheckBox::indicator:checked::before {
                left: 24px;
                background: #4cd964;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_alarm)
        # 右侧：删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(self.delete_alarm)
        delete_btn.setStyleSheet("background: transparent; color: #ff3b30; font-size: 28px; border: none; margin-right: 16px;")
        # 布局调整
        layout.addLayout(time_layout, 2)
        layout.addStretch(1)
        layout.addWidget(self.toggle_btn, 0, Qt.AlignVCenter)
        layout.addWidget(delete_btn, 0, Qt.AlignVCenter)
        self.setLayout(layout)
        # 分割线
        line = QFrame(self)
        line.setGeometry(24, 79, self.width()-48, 1)
        line.setStyleSheet("background: #222222;")
        line.show()
        
    def toggle_alarm(self):
        try:
            # 获取当前按钮状态
            enable = self.toggle_btn.isChecked()
            
            # 调用toggle_task方法切换任务状态
            self.task_daemon.toggle_task(
                task_id=self.task.id,
                enable=enable
            )
            
            # 更新按钮样式
            self.update_toggle_style()
            
        except Exception as e:
            logging.error(f"切换闹钟状态失败: {str(e)}")
            # 恢复按钮状态
            self.toggle_btn.setChecked(not self.toggle_btn.isChecked())
            self.update_toggle_style()
            
    def update_toggle_style(self):
        if self.toggle_btn.isChecked():
            self.toggle_btn.setStyleSheet("""
                QCheckBox::indicator:checked {
                    border-radius: 16px;
                    background: #ff9500;
                }
                QCheckBox::indicator:checked::before {
                    left: 24px;
                }
            """)
        else:
            self.toggle_btn.setStyleSheet("""
                QCheckBox::indicator:unchecked {
                    border-radius: 16px;
                    background: #393939;
                }
                QCheckBox::indicator:unchecked::before {
                    left: 4px;
                }
            """)
            
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
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(360, 480)
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
        title = QLabel("添加闹钟")
        title.setStyleSheet("color: white; font-size: 18px; font-family: 'PingFang SC'; font-weight: bold;")
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

        # 时间选择（仿iOS滚轮）
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 24, 0, 0)
        time_layout.setSpacing(0)
        self.hour_combo = QComboBox()
        self.minute_combo = QComboBox()
        for i in range(24):
            self.hour_combo.addItem(f"{i:02d}")
        for i in range(60):
            self.minute_combo.addItem(f"{i:02d}")
        self.hour_combo.setCurrentText("08")
        self.minute_combo.setCurrentText("00")
        for c in [self.hour_combo, self.minute_combo]:
            c.setStyleSheet("""
                QComboBox {
                    background: #232325;
                    color: #d1d1d6;
                    font-size: 32px;
                    border: none;
                    min-width: 80px;
                    min-height: 48px;
                    padding: 0 8px;
                    qproperty-alignment: AlignCenter;
                }
                QComboBox QAbstractItemView {
                    background: #232325;
                    color: #d1d1d6;
                    selection-background-color: #393939;
                    selection-color: #ff9500;
                    font-size: 32px;
                }
            """)
        time_layout.addStretch(1)
        time_layout.addWidget(self.hour_combo)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minute_combo)
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
        self.repeat_combo.addItems(["一次", "每日", "每周"])
        self.repeat_combo.setStyleSheet("color: #d1d1d6; background: transparent; font-size: 18px; border: none; padding: 8px 0 8px 0;")
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(["None", "Soft", "Active"])
        self.sound_combo.setStyleSheet("color: #d1d1d6; background: transparent; font-size: 18px; border: none; padding: 8px 0 8px 0;")
        self.light_combo = QComboBox()
        self.light_combo.addItems(["None", "Breathing", "Colorful"])
        self.light_combo.setStyleSheet("color: #d1d1d6; background: transparent; font-size: 18px; border: none; padding: 8px 0 8px 0;")
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(["None", "Sunrise", "Sunset", "Moon"])
        self.screen_combo.setStyleSheet("color: #d1d1d6; background: transparent; font-size: 18px; border: none; padding: 8px 0 8px 0;")
        self.scent_combo = QComboBox()
        self.scent_combo.addItems(["Off", "On"])
        self.scent_combo.setStyleSheet("color: #d1d1d6; background: transparent; font-size: 18px; border: none; padding: 8px 0 8px 0;")
        # 行生成函数
        def add_option_row(label, widget, divider=True):
            row = QHBoxLayout()
            row.setContentsMargins(24, 0, 24, 0)
            row.setSpacing(0)
            lab = QLabel(label)
            lab.setStyleSheet("color: #d1d1d6; font-size: 18px;")
            row.addWidget(lab)
            row.addStretch()
            row.addWidget(widget)
            option_layout.addLayout(row)
            if divider:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setStyleSheet("background: #222222; min-height: 1px; max-height: 1px; border: none;")
                option_layout.addWidget(line)
        add_option_row("重复", self.repeat_combo)
        add_option_row("铃声", self.sound_combo)
        add_option_row("灯光", self.light_combo)
        add_option_row("屏幕", self.screen_combo)
        add_option_row("香氛", self.scent_combo, divider=False)
        option_box.setLayout(option_layout)
        main_layout.addSpacing(24)
        main_layout.addWidget(option_box)
        self.setLayout(main_layout)

    def get_alarm_data(self):
        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        time_str = f"{hour}:{minute}"
        repeat_map = {"一次": "once", "每日": "daily", "每周": "weekly"}
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
        edit_label = QLabel("编辑")
        edit_label.setStyleSheet("color: #ff9500; font-size: 20px; font-weight: 500;")
        title = QLabel("闹钟")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
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
        title_layout.addWidget(edit_label)
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()
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
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_alarms()

def main():
    app = QApplication(sys.argv)
    # TODO: 初始化TaskDaemon
    task_daemon = None
    window = AlarmWidget(task_daemon)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 