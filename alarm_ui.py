import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QListWidget, 
                           QDialog, QTimeEdit, QComboBox, QMessageBox, QScrollArea, QFrame, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QTime, QDateTime, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QImage, QPixmap, QPalette
from model.scheduler import TaskDaemon, TaskType, TaskScheduleType
from datetime import time
import json
import os
import logging

class AlarmItem(QWidget):
    def __init__(self, task, task_daemon, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_daemon = task_daemon
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 时间标签
        time_label = QLabel(self.task.execution_time)
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
        freq = json.loads(self.task.actions)['frequency']
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
                    background-color: white;
                    border-radius: 13px;
                    margin: 2px;
                }
                QPushButton::indicator:checked {
                    margin-left: 22px;
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
                    background-color: white;
                    border-radius: 13px;
                    margin: 2px;
                }
                QPushButton::indicator:unchecked {
                    margin-left: 2px;
                }
            """)
            
    def toggle_alarm(self):
        try:
            # 调用scheduler的toggle_task方法
            updated_task = self.task_daemon.toggle_task(self.task.id)
            if updated_task:
                self.task = updated_task
                self.update_toggle_style()
                logging.info(f"闹钟状态已切换: ID={self.task.id}, 启用状态={self.task.is_enabled}")
        except Exception as e:
            logging.error(f"切换闹钟状态失败: {str(e)}")
            
    def delete_alarm(self):
        try:
            # 调用scheduler的remove_task方法
            if self.task_daemon.scheduler.remove_task(self.task.id):
                logging.info(f"闹钟已删除: ID={self.task.id}")
                # 通知父窗口刷新列表
                if self.parent():
                    self.parent().refresh_alarms()
        except Exception as e:
            logging.error(f"删除闹钟失败: {str(e)}")

class AddAlarmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
                font-size: 16px;
                margin: 5px 0;
            }
            QTimeEdit {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-family: 'PingFang SC';
                font-size: 16px;
                min-height: 30px;
                text-align: center;
            }
            QComboBox {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-family: 'PingFang SC';
                font-size: 16px;
                min-height: 30px;
                text-align: center;
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
            }
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: 'PingFang SC';
                font-size: 16px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
            QGroupBox {
                color: white;
                font-family: 'PingFang SC';
                font-size: 16px;
                border: 2px solid #303f9f;
                border-radius: 5px;
                margin-top: 20px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#timePicker {
                background-color: #303f9f;
                border-radius: 5px;
            }
            QLabel#timeLabel {
                font-size: 48px;
                font-weight: bold;
                color: white;
                text-align: center;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 时间选择器
        time_group = QGroupBox("提醒时间")
        time_layout = QVBoxLayout()
        
        # 创建时间选择器
        time_picker = QWidget()
        time_picker.setObjectName("timePicker")
        time_picker_layout = QVBoxLayout()
        
        # 小时选择
        hour_label = QLabel("小时")
        hour_label.setAlignment(Qt.AlignCenter)
        self.hour_combo = QComboBox()
        self.hour_combo.addItems([f"{i:02d}" for i in range(24)])
        self.hour_combo.setCurrentText("08")
        
        # 分钟选择
        minute_label = QLabel("分钟")
        minute_label.setAlignment(Qt.AlignCenter)
        self.minute_combo = QComboBox()
        self.minute_combo.addItems([f"{i:02d}" for i in range(60)])
        self.minute_combo.setCurrentText("00")
        
        # 时间显示
        self.time_display = QLabel("08:00")
        self.time_display.setObjectName("timeLabel")
        self.time_display.setAlignment(Qt.AlignCenter)
        
        # 连接信号
        self.hour_combo.currentTextChanged.connect(self.update_time_display)
        self.minute_combo.currentTextChanged.connect(self.update_time_display)
        
        time_picker_layout.addWidget(self.time_display)
        time_picker_layout.addWidget(hour_label)
        time_picker_layout.addWidget(self.hour_combo)
        time_picker_layout.addWidget(minute_label)
        time_picker_layout.addWidget(self.minute_combo)
        time_picker.setLayout(time_picker_layout)
        
        time_layout.addWidget(time_picker)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # 重复方式
        repeat_group = QGroupBox("重复方式")
        repeat_layout = QVBoxLayout()
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["单次", "每天", "工作日", "周末"])
        repeat_layout.addWidget(self.repeat_combo)
        repeat_group.setLayout(repeat_layout)
        layout.addWidget(repeat_group)
        
        # 屏幕效果
        screen_group = QGroupBox("屏幕效果")
        screen_layout = QVBoxLayout()
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(["日出", "日落", "海洋"])
        screen_layout.addWidget(self.screen_combo)
        screen_group.setLayout(screen_layout)
        layout.addWidget(screen_group)
        
        # 声音效果
        sound_group = QGroupBox("声音效果")
        sound_layout = QVBoxLayout()
        self.sound_combo = QComboBox()
        self.sound_combo.addItems(["温柔", "激烈"])
        sound_layout.addWidget(self.sound_combo)
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        # 灯光效果
        light_group = QGroupBox("灯光效果")
        light_layout = QVBoxLayout()
        self.light_combo = QComboBox()
        self.light_combo.addItems(["海洋", "炫彩"])
        light_layout.addWidget(self.light_combo)
        light_group.setLayout(light_layout)
        layout.addWidget(light_group)
        
        # 香氛效果
        scent_group = QGroupBox("香氛效果")
        scent_layout = QVBoxLayout()
        self.scent_combo = QComboBox()
        self.scent_combo.addItems(["树木", "海洋"])
        scent_layout.addWidget(self.scent_combo)
        scent_group.setLayout(scent_layout)
        layout.addWidget(scent_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def update_time_display(self):
        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        self.time_display.setText(f"{hour}:{minute}")
        
    def get_alarm_data(self):
        return {
            'time': f"{self.hour_combo.currentText()}:{self.minute_combo.currentText()}",
            'frequency': ['once', 'daily', 'weekday', 'weekend'][self.repeat_combo.currentIndex()],
            'enabled': True,
            'effects': {
                'screen': ['sunrise', 'sunset', 'ocean'][self.screen_combo.currentIndex()],
                'sound': ['gentle', 'intense'][self.sound_combo.currentIndex()],
                'light': ['ocean', 'colorful'][self.light_combo.currentIndex()],
                'scent': ['forest', 'ocean'][self.scent_combo.currentIndex()]
            }
        }

class AlarmWidget(QWidget):
    def __init__(self, task_daemon, parent=None):
        super().__init__(parent)
        self.task_daemon = task_daemon
        self.setup_ui()
        self.refresh_alarms()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题栏
        title_layout = QHBoxLayout()
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
        layout.addLayout(title_layout)
        
        # 闹钟列表
        self.alarm_list = QVBoxLayout()
        self.alarm_list.setSpacing(10)
        layout.addLayout(self.alarm_list)
        
        self.setLayout(layout)
        
    def refresh_alarms(self):
        # 清除现有闹钟
        while self.alarm_list.count():
            item = self.alarm_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 获取所有闹钟任务
        try:
            tasks = self.task_daemon.get_alarm_tasks()
            for task in tasks:
                alarm_item = AlarmItem(task, self.task_daemon)
                self.alarm_list.addWidget(alarm_item)
        except Exception as e:
            logging.error(f"刷新闹钟列表失败: {str(e)}")
            
    def show_add_dialog(self):
        dialog = AddAlarmDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                # 获取闹钟数据
                alarm_data = dialog.get_alarm_data()
                
                # 创建闹钟任务
                execution_time = time.fromisoformat(alarm_data['time'])
                weekdays = None
                if alarm_data['frequency'] == 'weekday':
                    weekdays = [1, 2, 3, 4, 5]  # 周一到周五
                elif alarm_data['frequency'] == 'weekend':
                    weekdays = [6, 7]  # 周六和周日
                    
                task = self.task_daemon.create_alarm_task(
                    name=f"闹钟 {alarm_data['time']}",
                    execution_time=execution_time,
                    parameters=alarm_data,
                    duration=300,  # 默认持续5分钟
                    weekdays=weekdays
                )
                
                if task:
                    logging.info(f"创建闹钟成功: ID={task.id}, 时间={task.execution_time}")
                    self.refresh_alarms()
                    
            except Exception as e:
                logging.error(f"创建闹钟失败: {str(e)}")

def main():
    app = QApplication(sys.argv)
    # TODO: 初始化TaskDaemon
    task_daemon = None
    window = AlarmWidget(task_daemon)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 