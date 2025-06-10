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

class AlarmItem(QFrame):
    def __init__(self, alarm_data, parent=None):
        super().__init__(parent)
        self.alarm_data = alarm_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #1a237e;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: white;
                font-family: 'PingFang SC';
                font-size: 16px;
            }
            QPushButton {
                background-color: #303f9f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: 'PingFang SC';
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
            QPushButton:disabled {
                background-color: #1a237e;
            }
        """)
        
        layout = QHBoxLayout()
        
        # 时间显示
        time_label = QLabel(self.alarm_data['time'])
        time_label.setFont(QFont('PingFang SC', 20))
        layout.addWidget(time_label)
        
        # 频率显示
        freq_text = self.get_frequency_text()
        freq_label = QLabel(freq_text)
        freq_label.setFont(QFont('PingFang SC', 12))
        layout.addWidget(freq_label)
        
        # 开关按钮
        self.toggle_btn = QPushButton("开启" if self.alarm_data['enabled'] else "关闭")
        self.toggle_btn.clicked.connect(self.toggle_alarm)
        layout.addWidget(self.toggle_btn)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_alarm)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
        
    def get_frequency_text(self):
        if self.alarm_data['frequency'] == 'once':
            return "单次"
        elif self.alarm_data['frequency'] == 'daily':
            return "每天"
        elif self.alarm_data['frequency'] == 'weekday':
            return "工作日"
        elif self.alarm_data['frequency'] == 'weekend':
            return "周末"
        return ""
        
    def toggle_alarm(self):
        self.alarm_data['enabled'] = not self.alarm_data['enabled']
        self.toggle_btn.setText("开启" if self.alarm_data['enabled'] else "关闭")
        self.parent().parent().save_alarms()
        
    def delete_alarm(self):
        reply = QMessageBox.question(self, '确认删除', 
                                   '确定要删除这个闹钟吗？',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent().parent().delete_alarm(self.alarm_data)
            self.deleteLater()

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
        self.alarms = []
        self.setup_ui()
        self.load_alarms()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0d47a1;
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
                padding: 10px 20px;
                font-family: 'PingFang SC';
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
            QPushButton#addButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 32px;
                font-weight: bold;
                padding: 0px;
                width: 40px;
                height: 40px;
                text-align: center;
            }
            QPushButton#addButton:hover {
                color: #3949ab;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 顶部布局（标题和添加按钮）
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        
        # 标题
        title = QLabel("闹钟")
        title.setFont(QFont('PingFang SC', 24))
        title.setStyleSheet("color: white;")
        top_layout.addWidget(title)
        
        # 添加按钮
        add_btn = QPushButton("+")
        add_btn.setObjectName("addButton")
        add_btn.setFixedSize(40, 40)
        add_btn.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(add_btn)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # 闹钟列表
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.alarm_list = QWidget()
        self.alarm_layout = QVBoxLayout()
        self.alarm_layout.setSpacing(10)
        self.alarm_list.setLayout(self.alarm_layout)
        self.scroll_area.setWidget(self.alarm_list)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def load_alarms(self):
        # 清空现有闹钟
        while self.alarm_layout.count():
            item = self.alarm_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 加载闹钟
        if os.path.exists('alarms.json'):
            with open('alarms.json', 'r', encoding='utf-8') as f:
                self.alarms = json.load(f)
                
        for alarm in self.alarms:
            self.add_alarm_item(alarm)
            
    def add_alarm_item(self, alarm_data):
        alarm_item = AlarmItem(alarm_data, self.alarm_list)
        self.alarm_layout.addWidget(alarm_item)
        
    def show_add_dialog(self):
        dialog = AddAlarmDialog(self)
        if dialog.exec_():
            alarm_data = dialog.get_alarm_data()
            self.alarms.append(alarm_data)
            self.add_alarm_item(alarm_data)
            self.save_alarms()
            
    def delete_alarm(self, alarm_data):
        self.alarms.remove(alarm_data)
        self.save_alarms()
        
    def save_alarms(self):
        with open('alarms.json', 'w', encoding='utf-8') as f:
            json.dump(self.alarms, f, ensure_ascii=False, indent=2)
            
    def add_alarm_by_voice(self, time, frequency='once'):
        """通过语音添加闹钟"""
        alarm_data = {
            'time': time,
            'frequency': frequency,
            'enabled': True,
            'effects': {
                'screen': 'sunrise',
                'sound': 'gentle',
                'light': 'ocean',
                'scent': 'forest'
            }
        }
        self.alarms.append(alarm_data)
        self.add_alarm_item(alarm_data)
        self.save_alarms()
        
    def delete_alarm_by_voice(self, time):
        """通过语音删除闹钟"""
        for alarm in self.alarms[:]:
            if alarm['time'] == time:
                self.alarms.remove(alarm)
                self.load_alarms()
                self.save_alarms()
                return True
        return False

def main():
    app = QApplication(sys.argv)
    # TODO: 初始化TaskDaemon
    task_daemon = None
    window = AlarmWidget(task_daemon)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 