import sys
import json
import os
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRectF, QRect, QEasingCurve, QPoint, QTimer, QTime, QDate, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QFont, QFontDatabase, QPalette, QMouseEvent, QIcon, QMovie
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsBlurEffect, QLabel, 
                           QGraphicsOpacityEffect, QPushButton, QStackedWidget, QFrame, 
                           QGraphicsView, QGraphicsScene, QGraphicsRectItem, QComboBox,
                           QSlider, QCheckBox, QRadioButton, QButtonGroup, QVBoxLayout,
                           QHBoxLayout, QScrollArea)
from GUI.buttons import CustomButton, ImageButton
# from .main import MainWindow  # 添加这行导入语句

WINDOW_W = 1280
WINDOW_H = 800

class InitManager:
    def __init__(self):
        self.init_file = "init.json"
        self.data = None
        
    def load_init_data(self):
        """加载初始化数据"""
        if os.path.exists(self.init_file):
            try:
                with open(self.init_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                return True
            except Exception as e:
                print(f"Error loading init data: {e}")
                return False
        return False
        
    def save_init_data(self, data):
        """保存初始化数据"""
        try:
            with open(self.init_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving init data: {e}")
            return False

class GuidePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_manager = InitManager()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建堆叠窗口用于管理多个引导页面
        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        
        # 创建各个引导页面
        self.welcome_page = WelcomePage(self)
        self.language_page = LanguagePage(self)
        self.date_page = DatePage(self)
        self.time_page = TimePage(self)
        self.religion_page = ReligionPage(self)
        self.stress_page = StressPage(self)
        self.sleep_page = SleepPage(self)
        self.problems_page = ProblemsPage(self)
        self.mentor_page = MentorPage(self)
        self.final_page = FinalPage(self)
        
        # 添加页面到堆叠窗口
        self.stack.addWidget(self.welcome_page)
        self.stack.addWidget(self.language_page)
        self.stack.addWidget(self.date_page)
        self.stack.addWidget(self.time_page)
        self.stack.addWidget(self.religion_page)
        self.stack.addWidget(self.stress_page)
        self.stack.addWidget(self.sleep_page)
        self.stack.addWidget(self.problems_page)
        self.stack.addWidget(self.mentor_page)
        self.stack.addWidget(self.final_page)
        
        # 连接信号
        self.welcome_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.language_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.date_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.time_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.religion_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.stress_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(6))
        self.sleep_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(7))
        self.problems_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(8))
        self.mentor_page.next_clicked.connect(lambda: self.stack.setCurrentIndex(9))
        self.final_page.finish_clicked.connect(self.finish_guide)
        
        # 连接返回按钮信号
        self.language_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.date_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.time_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.religion_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.stress_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.sleep_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.problems_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(6))
        self.mentor_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(7))
        self.final_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(8))
        
        # 设置初始页面
        self.stack.setCurrentIndex(0)
        
    def finish_guide(self):
        """完成引导，收集所有数据并传递给主界面"""
        # 收集所有数据
        init_data = {
            'language': self.language_page.get_selected_language(),
            'date': self.date_page.get_selected_date(),
            'time': self.time_page.get_selected_time(),
            'religion': self.religion_page.get_selected_religion(),
            'stress_level': self.stress_page.get_stress_level(),
            'sleep_quality': self.sleep_page.get_sleep_quality(),
            'problems': self.problems_page.get_selected_problems(),
            'mentor': self.mentor_page.get_selected_mentor()
        }
        
        print("Initialization data:", init_data)  # 调试信息
        
        # 创建并显示主界面
        # self.main_window = MainWindow(init_data)
        # self.main_window.show()
        self.close()

class BaseGuidePage(QWidget):
    next_clicked = pyqtSignal()
    back_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 创建背景
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        self.background.setStyleSheet("background-color: #1a1a1a;")
        
        # 创建按钮容器 - 移到顶部
        self.button_container = QWidget(self)
        self.button_container.setGeometry(0, 20, WINDOW_W, 80)
        self.button_container.setStyleSheet("background-color: transparent;")
        
        # 创建返回按钮
        self.back_btn = QPushButton(self.button_container)
        self.back_btn.setText("返回")
        self.back_btn.setGeometry(20, 0, 200, 60)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #FFD700;
                border: 1px solid #FFD700;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #FFA500;
                color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
                border: 1px solid #FF8C00;
                color: #FF8C00;
            }
        """)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        
        # 创建下一步按钮
        self.next_btn = QPushButton(self.button_container)
        self.next_btn.setText("下一步")
        self.next_btn.setGeometry(WINDOW_W-220, 0, 200, 60)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #FFD700;
                border: 1px solid #FFD700;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #FFA500;
                color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
                border: 1px solid #FF8C00;
                color: #FF8C00;
            }
        """)
        self.next_btn.clicked.connect(self.next_clicked.emit)
        
        # 创建标题
        self.title = QLabel(self)
        self.title.setGeometry(0, 120, WINDOW_W, 60)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-size: 32px;")
        
        # 创建内容区域
        self.content = QLabel(self)
        self.content.setGeometry(100, 200, WINDOW_W-200, 400)
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setStyleSheet("color: white; font-size: 24px;")
        
        # 确保按钮容器和按钮都可见
        self.button_container.raise_()
        self.button_container.show()
        self.back_btn.show()
        self.next_btn.show()

class WelcomePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("欢迎来到Mindora的世界")
        self.content.setText("在最开始的时候，请选择一些必要的信息，\n以便Mindora带给你关于冥想和助眠的更好体验")
        
        # 在欢迎页面隐藏返回按钮
        self.back_btn.hide()
        
        # 修改下一步按钮样式，使其更加显眼
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #FFD700;
                border: 4px solid #FFD700;
                border-radius: 30px;
                font-size: 28px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 4px solid #FFA500;
                color: #FFA500;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
                border: 4px solid #FF8C00;
                color: #FF8C00;
            }
        """)
        self.next_btn.setText("开始体验")
        self.next_btn.setGeometry((WINDOW_W-300)//2, 0, 300, 60)  # 欢迎页面按钮居中

class LanguagePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您的语言")
        self.content.setText("")
        
        # 创建语言选择按钮组
        self.language_group = QButtonGroup(self)
        self.languages = ["英语", "中文", "日语", "法语"]
        
        # 创建语言选择容器
        self.language_container = QWidget(self)
        self.language_container.setGeometry((WINDOW_W-400)//2, 300, 400, 300)
        
        # 创建单选按钮
        for i, lang in enumerate(self.languages):
            radio = QRadioButton(lang, self.language_container)
            radio.setGeometry(0, i*60, 400, 50)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 24px;
                    padding: 10px;
                }
                QRadioButton::indicator {
                    width: 30px;
                    height: 30px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #4a4a4a;
                    border-radius: 15px;
                    background-color: #2a2a2a;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4a4a4a;
                    border-radius: 15px;
                    background-color: #4a4a4a;
                }
            """)
            self.language_group.addButton(radio, i)
            radio.show()
            
        # 连接信号
        self.language_group.buttonClicked.connect(self.on_language_selected)
        
    def on_language_selected(self):
        """当选择语言时直接进入下一个页面"""
        self.next_clicked.emit()

    def get_selected_language(self):
        """获取选中的语言"""
        button = self.language_group.checkedButton()
        if button:
            return self.languages[self.language_group.id(button)]
        return None

class DatePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您当前所在地的日期")
        
        # 创建日期选择器
        self.date_widget = QWidget(self)
        self.date_widget.setGeometry((WINDOW_W-400)//2, 300, 400, 200)
        
        # 创建年月日选择器
        self.year_combo = QComboBox(self.date_widget)
        self.year_combo.setGeometry(0, 0, 120, 50)
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 5px;
                font-size: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/images/down_arrow.png);
                width: 20px;
                height: 20px;
            }
        """)
        
        self.month_combo = QComboBox(self.date_widget)
        self.month_combo.setGeometry(140, 0, 120, 50)
        self.month_combo.setStyleSheet(self.year_combo.styleSheet())
        
        self.day_combo = QComboBox(self.date_widget)
        self.day_combo.setGeometry(280, 0, 120, 50)
        self.day_combo.setStyleSheet(self.year_combo.styleSheet())
        
        # 填充年份选项（当前年份前后10年）
        current_year = QDate.currentDate().year()
        for year in range(current_year-10, current_year+11):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        
        # 填充月份选项
        for month in range(1, 13):
            self.month_combo.addItem(str(month).zfill(2))
        self.month_combo.setCurrentText(str(QDate.currentDate().month()).zfill(2))
        
        # 更新日期选项
        self.update_days()
        
        # 连接信号
        self.year_combo.currentTextChanged.connect(self.update_days)
        self.month_combo.currentTextChanged.connect(self.update_days)
        
    def update_days(self):
        """更新日期选项"""
        year = int(self.year_combo.currentText())
        month = int(self.month_combo.currentText())
        days_in_month = QDate(year, month, 1).daysInMonth()
        
        self.day_combo.clear()
        for day in range(1, days_in_month + 1):
            self.day_combo.addItem(str(day).zfill(2))
        
        current_day = QDate.currentDate().day()
        if current_day <= days_in_month:
            self.day_combo.setCurrentText(str(current_day).zfill(2))
        else:
            self.day_combo.setCurrentText("01")
            
    def get_selected_date(self):
        """获取选择的日期"""
        year = self.year_combo.currentText()
        month = self.month_combo.currentText()
        day = self.day_combo.currentText()
        return f"{year}-{month}-{day}"

class TimePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您当前所在地的时间")
        
        # 创建时间选择器
        self.time_widget = QWidget(self)
        self.time_widget.setGeometry((WINDOW_W-400)//2, 300, 400, 200)
        
        # 创建时分选择器
        self.hour_combo = QComboBox(self.time_widget)
        self.hour_combo.setGeometry(0, 0, 120, 50)
        self.hour_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 5px;
                font-size: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/images/down_arrow.png);
                width: 20px;
                height: 20px;
            }
        """)
        
        self.minute_combo = QComboBox(self.time_widget)
        self.minute_combo.setGeometry(140, 0, 120, 50)
        self.minute_combo.setStyleSheet(self.hour_combo.styleSheet())
        
        # 创建分隔符标签
        self.separator = QLabel(":", self.time_widget)
        self.separator.setGeometry(120, 0, 20, 50)
        self.separator.setStyleSheet("color: white; font-size: 30px;")
        self.separator.setAlignment(Qt.AlignCenter)
        
        # 填充小时选项
        for hour in range(24):
            self.hour_combo.addItem(str(hour).zfill(2))
        self.hour_combo.setCurrentText(str(QTime.currentTime().hour()).zfill(2))
        
        # 填充分钟选项
        for minute in range(60):
            self.minute_combo.addItem(str(minute).zfill(2))
        self.minute_combo.setCurrentText(str(QTime.currentTime().minute()).zfill(2))
        
    def get_selected_time(self):
        """获取选择的时间"""
        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        return f"{hour}:{minute}"

class ReligionPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您所在的宗教")
        
        # 创建宗教选择按钮组
        self.religion_group = QButtonGroup(self)
        self.religions = ["无宗教信仰", "佛教", "基督教", "伊斯兰教", "印度教", "道教", "其他"]
        
        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-400)//2, 300, 400, 400)
        self.scroll_area.setWidgetResizable(True)  # 允许widget调整大小
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建容器widget
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.container)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建单选按钮
        for religion in self.religions:
            radio = QRadioButton(religion)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 24px;
                    padding: 10px;
                    min-height: 50px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #4a4a4a;
                    border-radius: 10px;
                    background-color: #2a2a2a;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #4a4a4a;
                    border-radius: 10px;
                    background-color: #4a4a4a;
                }
            """)
            self.religion_group.addButton(radio)
            layout.addWidget(radio)
        
        # 确保滚动区域在最上层
        self.scroll_area.raise_()
        self.scroll_area.show()

    def get_selected_religion(self):
        """获取选中的宗教"""
        button = self.religion_group.checkedButton()
        if button:
            return self.religions[self.religion_group.id(button)]
        return None

class StressPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您近1周的压力水平")
        
        # 创建压力水平滑块
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry((WINDOW_W-600)//2, 300, 600, 50)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0000, stop:0.33 #ffff00,
                    stop:0.66 #0000ff, stop:1 #00ff00);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # 创建标签
        self.labels = []
        labels_text = ["压力非常大", "压力较大", "压力一般", "压力较小", "非常轻松"]
        for i, text in enumerate(labels_text):
            label = QLabel(text, self)
            label.setGeometry((WINDOW_W-600)//2 + i*150, 360, 150, 30)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-size: 18px;")
            self.labels.append(label)
            
        # 创建当前值显示标签
        self.value_label = QLabel("50%", self)
        self.value_label.setGeometry((WINDOW_W-100)//2, 400, 100, 40)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: white; font-size: 24px;")
        
        # 连接信号
        self.slider.valueChanged.connect(self.update_value_label)
        
    def update_value_label(self, value):
        """更新值显示标签"""
        self.value_label.setText(f"{value}%")
        # 根据值更新标签颜色
        if value <= 20:
            self.labels[0].setStyleSheet("color: #ff0000; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 40:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: #ffff00; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 60:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: #0000ff; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 80:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: #00ff00; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        else:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: #00ff00; font-size: 18px;")
            
    def get_stress_level(self):
        """获取压力水平值"""
        return self.slider.value()

class SleepPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您近1周的睡眠质量")
        
        # 创建睡眠质量滑块
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry((WINDOW_W-600)//2, 300, 600, 50)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0000, stop:0.33 #ffff00,
                    stop:0.66 #0000ff, stop:1 #00ff00);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # 创建标签
        self.labels = []
        labels_text = ["非常不好", "不太好", "一般", "较好", "非常好"]
        for i, text in enumerate(labels_text):
            label = QLabel(text, self)
            label.setGeometry((WINDOW_W-600)//2 + i*150, 360, 150, 30)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-size: 18px;")
            self.labels.append(label)
            
        # 创建当前值显示标签
        self.value_label = QLabel("50%", self)
        self.value_label.setGeometry((WINDOW_W-100)//2, 400, 100, 40)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("color: white; font-size: 24px;")
        
        # 连接信号
        self.slider.valueChanged.connect(self.update_value_label)
        
    def update_value_label(self, value):
        """更新值显示标签"""
        self.value_label.setText(f"{value}%")
        # 根据值更新标签颜色
        if value <= 20:
            self.labels[0].setStyleSheet("color: #ff0000; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 40:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: #ffff00; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 60:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: #0000ff; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        elif value <= 80:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: #00ff00; font-size: 18px;")
            self.labels[4].setStyleSheet("color: white; font-size: 18px;")
        else:
            self.labels[0].setStyleSheet("color: white; font-size: 18px;")
            self.labels[1].setStyleSheet("color: white; font-size: 18px;")
            self.labels[2].setStyleSheet("color: white; font-size: 18px;")
            self.labels[3].setStyleSheet("color: white; font-size: 18px;")
            self.labels[4].setStyleSheet("color: #00ff00; font-size: 18px;")
            
    def get_sleep_quality(self):
        """获取睡眠质量值"""
        return self.slider.value()

class ProblemsPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您希望通过Mindora帮助您解决的问题")
        
        # 创建问题选择区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-600)//2, 300, 600, 400)
        self.scroll_area.setWidgetResizable(True)  # 允许widget调整大小
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建容器widget
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.container)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.container)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建复选框
        problems = [
            "改善睡眠质量",
            "减轻压力和焦虑",
            "提高专注力",
            "改善情绪管理",
            "增强自我意识",
            "提高冥想效果",
            "改善心理健康",
            "增强身心平衡",
            "提高生活质量",
            "改善人际关系"
        ]
        
        self.checkboxes = []
        for problem in problems:
            checkbox = QCheckBox(problem)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 20px;
                    padding: 5px;
                    min-height: 40px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #4a4a4a;
                    border-radius: 4px;
                    background-color: #2a2a2a;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #4a4a4a;
                    border-radius: 4px;
                    background-color: #4a4a4a;
                }
            """)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
            checkbox.stateChanged.connect(self.update_next_button)
            
        # 修改下一步按钮的启用状态
        self.next_btn.setEnabled(False)
        
        # 确保滚动区域在最上层
        self.scroll_area.raise_()
        self.scroll_area.show()
            
    def update_next_button(self):
        """更新下一步按钮状态"""
        checked = any(checkbox.isChecked() for checkbox in self.checkboxes)
        self.next_btn.setEnabled(checked)
        print(f"Checkbox state changed. Next button enabled: {checked}")  # 添加调试信息

    def get_selected_problems(self):
        """获取选中的问题列表"""
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]

class MentorPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("重要的一步：请选择您喜爱的流派和导师")
        self.content.setText("每个导师有独特的特长和独在的世界，您可以试听导师的自我介绍以便选择。\n当您希望更换导师时，您随时可以通过设置页面进行更换")
        
        # 调整标题和内容区域的位置
        self.title.setGeometry(0, 80, WINDOW_W, 40)  # 减小标题高度
        self.content.setGeometry(100, 130, WINDOW_W-200, 60)  # 减小内容区域高度
        
        # 创建导师选择区域 - 调整位置
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-400)//2, 200, 400, 300)  # 上移滚动区域
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建容器widget
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(self.container)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.container)
        layout.setSpacing(10)  # 减小间距
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建导师选择按钮组
        self.mentor_group = QButtonGroup(self)
        
        # 导师数据
        self.mentors = [
            {
                "name": "Guruji",
                "avatar": "resources/images/secondhead_guruji.png",
                "background": "resources/images/secondback_guruji.jpg",
                "description": "专注于冥想和心灵平静的导师",
                "audio": "resources/audio/guruji_intro.mp3"
            },
            {
                "name": "Master Sun",
                "avatar": "resources/images/secondhead_sun.png",
                "background": "resources/images/zeroback_sun.jpg",
                "description": "专注于睡眠和放松的导师",
                "audio": "resources/audio/sun_intro.mp3"
            }
        ]
        
        # 创建导师卡片
        for mentor in self.mentors:
            # 创建卡片容器
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 5px;
                    min-height: 40px;  /* 减小最小高度 */
                }
            """)
            
            # 创建卡片布局
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
            card_layout.setSpacing(5)  # 减小间距
            
            # 创建左侧区域（头像）
            left_widget = QWidget()
            left_widget.setFixedSize(32, 32)  # 缩小头像尺寸
            left_layout = QVBoxLayout(left_widget)
            left_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建头像
            avatar = QLabel()
            avatar.setFixedSize(32, 32)  # 缩小头像尺寸
            avatar_pixmap = QPixmap(mentor["avatar"])
            avatar.setPixmap(avatar_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            avatar.setStyleSheet("border-radius: 16px;")  # 调整圆角
            left_layout.addWidget(avatar)
            
            # 创建右侧区域（信息）
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(2)  # 减小间距
            
            # 创建名称
            name = QLabel(mentor["name"])
            name.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")  # 减小字体
            right_layout.addWidget(name)
            
            # 创建描述
            desc = QLabel(mentor["description"])
            desc.setStyleSheet("color: #cccccc; font-size: 12px;")  # 减小字体
            right_layout.addWidget(desc)
            
            # 创建按钮区域
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(5)  # 减小间距
            
            # 创建试听按钮
            listen_btn = QPushButton("试听")
            listen_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    color: #FFD700;
                    border: 1px solid #FFD700;
                    border-radius: 10px;
                    font-size: 12px;
                    padding: 2px 8px;
                    min-width: 50px;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            listen_btn.clicked.connect(lambda checked, m=mentor: self.play_audio(m["audio"]))
            button_layout.addWidget(listen_btn)
            
            # 创建选择按钮
            select_btn = QRadioButton()
            select_btn.setStyleSheet("""
                QRadioButton {
                    color: white;
                }
                QRadioButton::indicator {
                    width: 15px;
                    height: 15px;
                }
                QRadioButton::indicator:unchecked {
                    border: 1px solid #4a4a4a;
                    border-radius: 7px;
                    background-color: #2a2a2a;
                }
                QRadioButton::indicator:checked {
                    border: 1px solid #4a4a4a;
                    border-radius: 7px;
                    background-color: #4a4a4a;
                }
            """)
            self.mentor_group.addButton(select_btn)
            button_layout.addWidget(select_btn)
            
            right_layout.addWidget(button_widget)
            
            # 添加左右区域到卡片
            card_layout.addWidget(left_widget)
            card_layout.addWidget(right_widget)
            
            # 添加卡片到主布局
            layout.addWidget(card)
        
        # 修改下一步按钮的启用状态
        self.next_btn.setEnabled(False)
        
        # 连接信号
        self.mentor_group.buttonClicked.connect(self.update_next_button)
        
        # 确保滚动区域在最上层
        self.scroll_area.raise_()
        self.scroll_area.show()
        
    def play_audio(self, audio_path):
        """播放导师介绍音频"""
        # TODO: 实现音频播放功能
        print(f"Playing audio: {audio_path}")
        
    def update_next_button(self):
        """更新下一步按钮状态"""
        self.next_btn.setEnabled(True)
        print("Mentor selected. Next button enabled.")

    def get_selected_mentor(self):
        """获取选中的导师"""
        button = self.mentor_group.checkedButton()
        if button:
            # 获取导师卡片
            card = button.parent().parent()
            # 获取导师名称
            name_label = card.findChild(QLabel)
            if name_label:
                return name_label.text()
        return None

class FinalPage(BaseGuidePage):
    finish_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("Great！您已经完成了初始的设置")
        self.content.setText("在开始我们的旅程之前，请允许我再次向您保证，Mindora极其注重您的隐私，\n"
                           "可以在不联网的时候使用所有能力。并提供了物理按键以一键关闭系统的声音、灯光、香氛。\n"
                           "您可以通过Mindora来唤醒他，也可以用触屏完成整个操作。\n"
                           "当您希望更新内容时，您可以链接WIFI，完成系统及更多新内容的下载")
        self.next_btn.setText("开始体验")
        self.next_btn.clicked.disconnect()
        self.next_btn.clicked.connect(self.finish_clicked.emit) 