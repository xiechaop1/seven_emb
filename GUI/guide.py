import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QRectF, QRect, QEasingCurve, QPoint, QTimer, QTime, QDate, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QFont, QFontDatabase, QPalette, QMouseEvent, QIcon, QMovie
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsBlurEffect, QLabel, 
                           QGraphicsOpacityEffect, QPushButton, QStackedWidget, QFrame, 
                           QGraphicsView, QGraphicsScene, QGraphicsRectItem, QComboBox,
                           QSlider, QCheckBox, QRadioButton, QButtonGroup, QVBoxLayout,
                           QHBoxLayout, QScrollArea)
from GUI.buttons import CustomButton, ImageButton

WINDOW_W = 1080
WINDOW_H = 1080

class GuidePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, WINDOW_W, WINDOW_H)
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
        
        # 设置初始页面
        self.stack.setCurrentIndex(0)
        
    def finish_guide(self):
        # 完成引导流程，返回主界面
        self.parent().show_main_interface()

class BaseGuidePage(QWidget):
    next_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # 创建背景
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, WINDOW_W, WINDOW_H)
        self.background.setStyleSheet("background-color: #1a1a1a;")
        
        # 创建标题
        self.title = QLabel(self)
        self.title.setGeometry(0, 100, WINDOW_W, 60)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-size: 32px;")
        
        # 创建内容区域
        self.content = QLabel(self)
        self.content.setGeometry(100, 200, WINDOW_W-200, 400)
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setStyleSheet("color: white; font-size: 24px;")
        
        # 创建下一步按钮
        self.next_btn = CustomButton(200, 60, self)
        self.next_btn.setText("下一步")
        self.next_btn.setGeometry((WINDOW_W-200)//2, WINDOW_H-200, 200, 60)
        self.next_btn.clicked.connect(self.next_clicked.emit)

class WelcomePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("欢迎来到Mindora的世界")
        self.content.setText("在最开始的时候，请选择一些必要的信息，\n以便Mindora带给你关于冥想和助眠的更好体验")

class LanguagePage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您的语言")
        self.content.setText("")
        
        # 创建语言选择按钮组
        self.language_group = QButtonGroup(self)
        languages = ["英语", "中文", "日语", "法语"]
        
        for i, lang in enumerate(languages):
            radio = QRadioButton(lang, self)
            radio.setGeometry((WINDOW_W-200)//2, 300+i*60, 200, 50)
            radio.setStyleSheet("color: white; font-size: 24px;")
            self.language_group.addButton(radio, i)
            radio.show()

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

class ReligionPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您所在的宗教")
        
        # 创建宗教选择按钮组
        self.religion_group = QButtonGroup(self)
        religions = ["无宗教信仰", "佛教", "基督教", "伊斯兰教", "印度教", "道教", "其他"]
        
        # 创建滚动区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-400)//2, 300, 400, 400)
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
        
        # 创建单选按钮
        for i, religion in enumerate(religions):
            radio = QRadioButton(religion, self.container)
            radio.setGeometry(0, i*60, 400, 50)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 24px;
                    padding: 10px;
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
            self.religion_group.addButton(radio, i)
            radio.show()

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

class ProblemsPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("请选择您希望通过Mindora帮助您解决的问题")
        
        # 创建问题选择区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-600)//2, 300, 600, 400)
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
        for i, problem in enumerate(problems):
            checkbox = QCheckBox(problem, self.container)
            checkbox.setGeometry(0, i*50, 600, 40)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 20px;
                    padding: 5px;
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
            checkbox.show()
            
        # 修改下一步按钮的启用状态
        self.next_btn.setEnabled(False)
        
        # 连接信号
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.update_next_button)
            
    def update_next_button(self):
        """更新下一步按钮状态"""
        checked = any(checkbox.isChecked() for checkbox in self.checkboxes)
        self.next_btn.setEnabled(checked)

class MentorPage(BaseGuidePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title.setText("重要的一步：请选择您喜爱的流派和导师")
        self.content.setText("每个导师有独特的特长和独在的世界，您可以试听导师的自我介绍以便选择。\n当您希望更换导师时，您随时可以通过设置页面进行更换")
        
        # 创建导师选择区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry((WINDOW_W-800)//2, 300, 800, 500)
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
        self.mentor_cards = []
        for i, mentor in enumerate(self.mentors):
            # 创建卡片容器
            card = QWidget(self.container)
            card.setGeometry(0, i*250, 800, 200)
            card.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 10px;
                }
            """)
            
            # 创建头像
            avatar = QLabel(card)
            avatar.setGeometry(20, 20, 160, 160)
            avatar_pixmap = QPixmap(mentor["avatar"])
            avatar.setPixmap(avatar_pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            avatar.setStyleSheet("border-radius: 80px;")
            
            # 创建名称
            name = QLabel(mentor["name"], card)
            name.setGeometry(200, 30, 400, 40)
            name.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            
            # 创建描述
            desc = QLabel(mentor["description"], card)
            desc.setGeometry(200, 80, 400, 40)
            desc.setStyleSheet("color: #cccccc; font-size: 18px;")
            
            # 创建试听按钮
            listen_btn = CustomButton(120, 40, card)
            listen_btn.setText("试听")
            listen_btn.setGeometry(200, 140, 120, 40)
            listen_btn.clicked.connect(lambda checked, m=mentor: self.play_audio(m["audio"]))
            
            # 创建选择按钮
            select_btn = QRadioButton(card)
            select_btn.setGeometry(700, 80, 40, 40)
            select_btn.setStyleSheet("""
                QRadioButton {
                    color: white;
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
            self.mentor_group.addButton(select_btn, i)
            
            self.mentor_cards.append(card)
            card.show()
            
        # 修改下一步按钮的启用状态
        self.next_btn.setEnabled(False)
        
        # 连接信号
        self.mentor_group.buttonClicked.connect(self.update_next_button)
        
    def play_audio(self, audio_path):
        """播放导师介绍音频"""
        # TODO: 实现音频播放功能
        pass
        
    def update_next_button(self):
        """更新下一步按钮状态"""
        self.next_btn.setEnabled(True)

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