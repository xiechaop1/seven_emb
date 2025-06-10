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
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a237e;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-family: 'PingFang SC';
            }
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                font-family: 'PingFang SC';
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 时间标签 - 只显示时:分
        time_str = self.task.execution_time.split()[1][:5] if ' ' in self.task.execution_time else self.task.execution_time[:5]
        time_label = QLabel(time_str)
        time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'PingFang SC';
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # 频率标签
        freq_map = {
            'once': '单次',
            'daily': '每天',
            'weekday': '工作日',
            'weekend': '周末'
        }
        try:
            actions = json.loads(self.task.actions)
            freq = actions.get('frequency', 'once')
        except:
            freq = 'once'
            
        freq_label = QLabel(freq_map.get(freq, freq))
        freq_label.setStyleSheet("""
            QLabel {
                color: #b0bec5;
                font-family: 'PingFang SC';
                font-size: 14px;
            }
        """)
        
        # 开关按钮
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedSize(50, 30)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(self.task.is_enabled)
        self.toggle_btn.clicked.connect(self.toggle_alarm)
        self.update_toggle_style()
        
        # 删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(self.delete_alarm)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0bec5;
                font-family: 'PingFang SC';
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                color: #ff5252;
            }
        """)
        
        # 添加组件到布局
        layout.addWidget(time_label)
        layout.addWidget(freq_label)
        layout.addStretch()
        layout.addWidget(self.toggle_btn)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
        
    def toggle_alarm(self):
        try:
            # 更新任务状态
            self.task.is_enabled = self.toggle_btn.isChecked()
            # 保存到文件
            self.task_daemon.save_tasks()
            # 更新按钮样式
            self.update_toggle_style()
            # 重新加载任务
            self.task_daemon.load_tasks()
        except Exception as e:
            logging.error(f"切换闹钟状态失败: {str(e)}")
            # 恢复按钮状态
            self.toggle_btn.setChecked(not self.toggle_btn.isChecked())
            self.update_toggle_style()
            
    def update_toggle_style(self):
        if self.toggle_btn.isChecked():
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    border: none;
                    border-radius: 15px;
                }
                QPushButton::indicator {
                    width: 26px;
                    height: 26px;
                    border-radius: 13px;
                    background-color: white;
                    margin: 2px;
                }
            """)
        else:
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #b0bec5;
                    border: none;
                    border-radius: 15px;
                }
                QPushButton::indicator {
                    width: 26px;
                    height: 26px;
                    border-radius: 13px;
                    background-color: white;
                    margin: 2px;
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
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("添加闹钟")
        self.setFixedSize(400, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a237e;
            }
            QLabel {
                color: white;
                font-family: 'PingFang SC';
                font-size: 12px;
            }
            QComboBox {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 4px;
                font-family: 'PingFang SC';
                font-size: 12px;
                min-height: 40px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #303f9f;
                color: white;
                selection-background-color: #3949ab;
                selection-color: white;
                border: none;
                outline: none;
                font-size: 12px;
            }
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 4px;
                font-family: 'PingFang SC';
                font-size: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
            QTimeEdit {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 4px;
                font-family: 'PingFang SC';
                font-size: 12px;
                min-height: 40px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 时间选择
        time_layout = QVBoxLayout()
        time_label = QLabel("提醒时间")
        time_label.setStyleSheet("font-size: 12px;")
        
        # 使用下拉框选择时间
        time_widget = QWidget()
        time_h_layout = QHBoxLayout()
        time_h_layout.setContentsMargins(0, 0, 0, 0)
        
        self.hour_combo = QComboBox()
        self.minute_combo = QComboBox()
        
        # 添加小时选项
        for i in range(24):
            self.hour_combo.addItem(f"{i:02d}")
            
        # 添加分钟选项
        for i in range(60):
            self.minute_combo.addItem(f"{i:02d}")
            
        # 设置默认时间为08:00
        self.hour_combo.setCurrentText("08")
        self.minute_combo.setCurrentText("00")
        
        time_h_layout.addWidget(self.hour_combo)
        time_h_layout.addWidget(QLabel(":"))
        time_h_layout.addWidget(self.minute_combo)
        time_widget.setLayout(time_h_layout)
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(time_widget)
        layout.addLayout(time_layout)
        
        # 重复选项
        repeat_layout = QVBoxLayout()
        repeat_label = QLabel("重复")
        repeat_label.setStyleSheet("font-size: 12px;")
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["单次", "每天", "工作日", "周末"])
        repeat_layout.addWidget(repeat_label)
        repeat_layout.addWidget(self.repeat_combo)
        layout.addLayout(repeat_layout)
        
        # 屏幕效果
        screen_layout = QVBoxLayout()
        screen_label = QLabel("屏幕效果")
        screen_label.setStyleSheet("font-size: 12px;")
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(["None", "Sunrise", "Sunset", "Ocean"])
        screen_layout.addWidget(screen_label)
        screen_layout.addWidget(self.screen_combo)
        layout.addLayout(screen_layout)
        
        # 声音效果
        sound_layout = QVBoxLayout()
        sound_label = QLabel("声音效果")
        sound_label.setStyleSheet("font-size: 12px;")
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(["None", "Gentle", "Intense"])
        sound_layout.addWidget(sound_label)
        sound_layout.addWidget(self.sound_combo)
        layout.addLayout(sound_layout)
        
        # 灯光效果
        light_layout = QVBoxLayout()
        light_label = QLabel("灯光效果")
        light_label.setStyleSheet("font-size: 12px;")
        self.light_combo = QComboBox()
        self.light_combo.addItems(["None", "Breathing", "Colorful"])
        light_layout.addWidget(light_label)
        light_layout.addWidget(self.light_combo)
        layout.addLayout(light_layout)
        
        # 香薰效果
        scent_layout = QVBoxLayout()
        scent_label = QLabel("香薰效果")
        scent_label.setStyleSheet("font-size: 12px;")
        self.scent_combo = QComboBox()
        self.scent_combo.addItems(["None", "Forest", "Ocean"])
        scent_layout.addWidget(scent_label)
        scent_layout.addWidget(self.scent_combo)
        layout.addLayout(scent_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_alarm)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_alarm_data(self):
        # 获取时间
        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        time_str = f"{hour}:{minute}"
        
        # 获取重复选项
        repeat_map = {
            "单次": "once",
            "每天": "daily",
            "工作日": "weekday",
            "周末": "weekend"
        }
        repeat = repeat_map.get(self.repeat_combo.currentText(), "once")
        
        # 创建动作列表
        actions = []
        
        # 屏幕效果
        screen_map = {
            "None": None,
            "Sunrise": ("animation", {"type": "sunrise", "duration": 300}),
            "Sunset": ("animation", {"type": "sunset", "duration": 300}),
            "Ocean": ("animation", {"type": "ocean", "duration": 300})
        }
        screen_effect = screen_map.get(self.screen_combo.currentText())
        if screen_effect:
            mode, params = screen_effect
            actions.append({
                "action_type": ActionType.DISPLAY,
                "target": "screen",
                "parameters": {
                    "mode": mode,
                    "params": params
                }
            })
            
        # 声音效果
        sound_map = {
            "None": None,
            "Gentle": ("gentle.mp3", 80),
            "Intense": ("intense.mp3", 100)
        }
        sound_effect = sound_map.get(self.sound_combo.currentText())
        if sound_effect:
            file_path, volume = sound_effect
            actions.append({
                "action_type": ActionType.SOUND,
                "target": "sound",
                "parameters": {
                    "file_path": file_path,
                    "volume": volume
                }
            })
            
        # 灯光效果
        light_map = {
            "None": None,
            "Breathing": (Code.LIGHT_MODE_BREATHING, {"r": "128", "g": 128, "b": 0, "steps": 200}),
            "Colorful": (Code.LIGHT_MODE_SECTOR_FLOWING, {"mode": "colorful"}),
        }
        light_effect = light_map.get(self.light_combo.currentText())
        if light_effect:
            mode, params = light_effect
            actions.append({
                "action_type": ActionType.LIGHT,
                "target": "light",
                "parameters": {
                    "mode": mode,
                    "params": params
                }
            })
            
        # 香薰效果
        scent_map = {
            "None": None,
            "Forest": ("forest", 5),
            "Ocean": ("ocean", 5)
        }
        scent_effect = scent_map.get(self.scent_combo.currentText())
        if scent_effect:
            mode, duration = scent_effect
            actions.append({
                "action_type": ActionType.SPRAY,
                "target": "spray",
                "parameters": {
                    "mode": mode,
                    "duration": duration
                }
            })
        
        return {
            "time": time_str,
            "frequency": repeat,
            "enabled": True,
            "actions": actions
        }

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
                parameters=alarm_data,
                duration=300
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
                background-color: #1a237e;
            }
            QLabel {
                color: white;
                font-family: 'PingFang SC';
            }
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                font-family: 'PingFang SC';
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContent {
                background-color: #1a237e;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题栏 - 固定在顶部
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("闹钟")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'PingFang SC';
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        add_btn = QPushButton("+")
        add_btn.setFixedSize(40, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 20px;
                font-family: 'PingFang SC';
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
        """)
        add_btn.clicked.connect(self.show_add_dialog)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(add_btn)
        main_layout.addLayout(title_layout)
        
        # 闹钟列表 - 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建滚动区域的内容容器
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        self.alarm_list = QVBoxLayout()
        self.alarm_list.setSpacing(10)
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