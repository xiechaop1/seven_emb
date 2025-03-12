import base64
import time
from base.PIDController import PIDController
import cv2

class Camera:

    PATH = "/tmp/"

    def __init__(self, cv2):
        self.frame_skip = 1  # 每隔3帧处理一次
        self.frame_count = 0
        self.pid_h = PIDController(Kp=1.4, Ki=0, Kd=0.1)  # 水平方向的 PID 控制器
        self.pid_v = PIDController(Kp=0.15, Ki=0, Kd=0.1)  # 竖直方向的 PID 控制器
        self.count = 0
        self.flag_face = False
        self.left = 0.0
        self.top = 0.0
        self.right = 0.0
        self.down = 0.0

        self.video_capture = cv2

        # self.video_capture = cv2.VideoCapture(0)
        self.photo_counter = 0  # Counter for saved images
        self.count_face = 0
        # 原始范围和目标范围
        self.from_min = 45
        self.from_max = 285
        self.to_min = 2000
        self.to_max = 1000
        # 要映射的值（165是示例）
        self.value = 165
        # 调用函数映射值
        # mapped_value = map_value(value, from_min, from_max, to_min, to_max)

    def take_photo(self, file_tag = 1):
        try:
            success, img = self.video_capture.read()
            orin_img = img
            path = self.PATH
            photo_filename = f"{path}{file_tag}.jpg"
            cv2.imwrite(photo_filename, img)
            # 使用cv2.imencode将图像转换为JPEG格式的字节流
            retval, buffer = cv2.imencode('.jpg', img)

            if retval:
                photo_base64 = base64.b64encode(buffer).decode('utf-8')
                return photo_base64
        except Exception as e:
            print(e)
            return

        return

