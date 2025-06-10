import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QListWidget, 
                           QDialog, QTimeEdit, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QTime, QDateTime
from PyQt5.QtGui import QIcon, QFont
from model.scheduler import TaskDaemon, TaskType, TaskScheduleType
from datetime import time

class AlarmItem(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # 时间显示
        time_str = time.fromisoformat(self.task.execution_time).strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Arial", 16))
        layout.addWidget(time_label)
        
        # 频次显示
        if self.task.schedule_type == TaskScheduleType.ONCE:
            freq_text = "一次"
        elif self.task.schedule_type == TaskScheduleType.DAILY:
            freq_text = "每日"
        else:
            weekdays = [int(d) for d in self.task.weekdays.strip('[]').split(',')]
            freq_text = f"每周 {','.join(map(str, weekdays))}"
        freq_label = QLabel(freq_text)
        layout.addWidget(freq_label)
        
        # 开关按钮
        self.toggle_btn = QPushButton("开启" if self.task.is_enabled else "关闭")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(self.task.is_enabled)
        self.toggle_btn.clicked.connect(self.toggle_alarm)
        layout.addWidget(self.toggle_btn)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_alarm)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
        
    def toggle_alarm(self):
        enabled = self.toggle_btn.isChecked()
        self.toggle_btn.setText("开启" if enabled else "关闭")
        # TODO: 调用TaskDaemon的toggle_task方法
        
    def delete_alarm(self):
        # TODO: 调用TaskDaemon的remove_task方法
        pass

class AddAlarmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("新增闹钟")
        layout = QVBoxLayout()
        
        # 时间选择
        time_layout = QHBoxLayout()
        time_label = QLabel("时间:")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        layout.addLayout(time_layout)
        
        # 频次选择
        freq_layout = QHBoxLayout()
        freq_label = QLabel("频次:")
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["一次", "每日", "每周"])
        self.freq_combo.currentIndexChanged.connect(self.on_freq_changed)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_combo)
        layout.addLayout(freq_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def on_freq_changed(self, index):
        # TODO: 如果选择每周，显示星期选择界面
        pass
        
    def get_alarm_data(self):
        time = self.time_edit.time().toPyTime()
        freq = self.freq_combo.currentText()
        return time, freq

class AlarmWindow(QMainWindow):
    def __init__(self, task_daemon):
        super().__init__()
        self.task_daemon = task_daemon
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("闹钟管理")
        self.setGeometry(100, 100, 400, 600)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("闹钟")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 闹钟列表
        self.alarm_list = QListWidget()
        layout.addWidget(self.alarm_list)
        
        # 添加按钮
        add_btn = QPushButton("+")
        add_btn.setFixedSize(50, 50)
        add_btn.clicked.connect(self.show_add_dialog)
        layout.addWidget(add_btn, alignment=Qt.AlignCenter)
        
        # 加载现有闹钟
        self.load_alarms()
        
    def load_alarms(self):
        self.alarm_list.clear()
        alarms = self.task_daemon.get_alarm_tasks()
        for alarm in alarms:
            item = AlarmItem(alarm)
            self.alarm_list.addItem("")
            self.alarm_list.setItemWidget(self.alarm_list.item(self.alarm_list.count()-1), item)
            
    def show_add_dialog(self):
        dialog = AddAlarmDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            time, freq = dialog.get_alarm_data()
            # TODO: 调用TaskDaemon的create_alarm_task方法创建新闹钟
            self.load_alarms()

def main():
    app = QApplication(sys.argv)
    # TODO: 初始化TaskDaemon
    task_daemon = None
    window = AlarmWindow(task_daemon)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 