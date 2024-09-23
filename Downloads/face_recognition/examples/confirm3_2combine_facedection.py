import face_recognition
import cv2
import numpy as np
import matplotlib.pyplot as plt


import serial
import time
import numpy as np
from array import array
import time
import math
import smbus
import threading

import math
# import matplotlib.pyplot as plt
import sys
import os
import math
import numpy as np
import threading
import queue
# from main import switch_flag

# # 将上级目录添加到 sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import Sonar
import os
import sys
import time
import smbus
from smbus2 import SMBus, i2c_msg


last_tt1=0
tt1=0
cycle_time=0



Face_locations = []  # 定义为空列表
cur_t=0
last_t=0
last_pos_0=0
position=[0,0]
current_pulse_width=0
flag_break=False
flag_break2=False

current_pulse_width=0
current_pulse_width2=0
W = 1280  # 摄像头的宽度分辨率
H = 960  # 摄像头的高度分辨率
theta_h = 1500  # 水平舵机的初始角度
theta_v = 900  # 竖直舵机的初始角度

# PID 控制器类
class PIDController:
    def __init__(self, Kp, Ki, Kd,integral_limit=None):
        self.Kp = Kp  # 比例增益
        self.Ki = Ki  # 积分增益
        self.Kd = Kd  # 微分增益
        self.prev_error = 0
        self.integral = 0
        self.integral_limit = integral_limit  # 设置积分上限
        self.last_time = time.time()

    def update(self, error):
        # 计算时间差
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        # 计算积分部分
        self.integral += error * delta_time

        if self.integral_limit is not None:
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)

        # 计算微分部分
        derivative = (error - self.prev_error) / delta_time if delta_time > 0 else 0

        # PID输出: 这里的输出是舵机的“速度”调整量
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # 保存当前误差
        self.prev_error = error

        return output


class PCA9685:
    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(3)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, int(pulse))


def motor_test():
    step1=10
    for j in range(4):
        print("cycle: %d",j)
        for i in range(100):
            pwm.setServoPulse(0,1500-i*step1)  # jaw
            # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
            time.sleep(0.01)
            if i%5==0:
                print(1500-i*step1)


        for i in range(200):
            pwm.setServoPulse(0, 500 + i * step1)  # jaw
            # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
            time.sleep(0.01)
            if 500 + i * step1==1500:
                time.sleep(2)
            if i % 5 == 0:
                print( 500 + i * step1)
        for i in range(100):
            pwm.setServoPulse(0, 2500 - i * step1)  # jaw
            # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
            time.sleep(0.01)
            if i % 5 == 0:
                print(2500 - i * step1)
        time.sleep(2)

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

def speed_control(speed,speed2,step):
    global flag_break,flag_break2,current_pulse_width,current_pulse_width2
    min_pulse = 500
    max_pulse = 2500
    center_pulse = 1500  # 中心位置的脉冲宽度
    center_pulse2=700
    # 设定目标速度（单位：脉冲宽度/秒）
    target_speed = speed  # 你可以根据需要设定这个值，比如50表示每秒脉冲宽度变化50单位
    target_speed2 = speed2
    # 初始化变量
    if current_pulse_width == 0:
        pulse_width = center_pulse     # 从中间位置开始
    else:
        pulse_width = current_pulse_width   #从当前位置开始
    if current_pulse_width2 == 0:
        pulse_width2 = center_pulse2     # 从中间位置开始
    else:
        pulse_width2 = current_pulse_width2  #从当前位置开始
    last_pulse_width = pulse_width
    last_pulse_width2 = pulse_width2
    last_time = time.time()

    ## 计算每次的步长，根据速度控制方向
    current_step = target_speed / 60  # 控制步长与速度成比例
    current_step2 = target_speed2 / 50  # 控制步长与速度成比例

    for i in range(int(step*3)):
        # 计算脉冲宽度
        if flag_break and flag_break2:
            print("Both break flags set, breaking loop!")
            break

        if not flag_break:
            # 设置通道 0 的脉冲宽度
            # print("set channel 0")
            pwm.setServoPulse(0, int(pulse_width))
        else:
            print("Flag_break is set, skipping pwm.setServoPulse for channel 0")

        if not flag_break2:
            # 设置通道 1 的脉冲宽度
            # print("set channel 1")
            pwm.setServoPulse(1, int(pulse_width2))
        else:
            print("Flag_break2 is set, skipping pwm.setServoPulse for channel 1")

        pulse_width += current_step  # 根据速度增加或减少脉冲宽度
        pulse_width2 += current_step2  # 根据速度增加或减少脉冲宽度
        # 确保脉冲宽度在 500 到 2500 之间
        # if pulse_width > max_pulse:
        #     pulse_width = max_pulse
        #     break
        # elif pulse_width < min_pulse:
        #     pulse_width = min_pulse
        #     break
        # if pulse_width2 > max_pulse:
        #     pulse_width2 = max_pulse
        #     break
        # elif pulse_width2 < min_pulse:
        #     pulse_width2 = min_pulse
        #     break

        # 控制时间间隔，以达到指定的速度
        time.sleep(0.006)  # 控制循环速度，值可以调整以匹配实际硬件响应

        # 每隔2个循环计算一次速度
        if i % 2 == 0:
            current_time = time.time()
            delta_time = current_time - last_time
            delta_pulse = pulse_width - last_pulse_width
            delta_pulse2 = pulse_width2 - last_pulse_width2
            speed1 = delta_pulse / delta_time  # 计算当前速度（脉冲宽度/秒）
            speed2 = delta_pulse2 / delta_time
            # 打印当前速度和脉冲宽度变化
            # print(f" Speed: {speed1}")
            # print("pulse_width:", int(pulse_width))
            # print(f" Speed2: {speed2}")
            # print("pulse_width2:", int(pulse_width2))
            current_pulse_width = pulse_width
            current_pulse_width2 = pulse_width2
            # 更新上一次的脉冲宽度和时间
            last_pulse_width = pulse_width
            last_pulse_width2 = pulse_width2
            last_time = current_time


def init():
    global switch_flag, old_switch_flag, stop_event, thread3

    pwm.setServoPulse(0, 1500)  # jaw
    pwm.setServoPulse(1, 800)  # jaw
    # pwm.setServoPulse(2, 1500-400-10)  # jaw
    # pwm.setServoPulse(3, 1500-200)  # jaw
    # pwm.setServoPulse(4, 1500-400)  # jaw
    # pwm.setServoPulse(5, 1500+200)  # jaw
    # pwm.setServoPulse(6, 1500+400-100)  # jaw
    # pwm.setServoPulse(7, 1500+200+5)  # jaw
    # pwm.setServoPulse(8, 1500+400+10)  # jaw
    # pwm.setServoPulse(14, 1500+350) #horizon
    # pwm.setServoPulse(15, 1500-100)  #vertical
    # Sonar.sonar_read()
    # ser.write(bytes.fromhex(
    #     "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF00FF49FF0B1205FF00041E010305FF0F594D"))  # 1.发送配置参数
    # time.sleep(0.2)
    # ser.write(bytes.fromhex(
    #     "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF00FF49FF0103034D"))  # 2.唤醒传感器
    # time.sleep(0.2)
    # ser.write(bytes.fromhex(
    #     "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FF00FF49FF0119194D"))  # 3.开启主动上报
    # switch_flag = 9
    # flip_over_with_sensor()
    for i in range(3):
        time.sleep(1)
        print("##################start################")

def map_value(value, from_min, from_max, to_min, to_max):
    # 使用线性映射公式
    return int(to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min))





def motor_test_acc():
    step1 = 5  # 初始步长
    acceleration = 0.05 # 加速度调节量
    deceleration = 0.07# 加速度调节量
    acceleration2= 0.08
    deceleration2=0.03
    current_step = step1  # 当前步长
    max_step = 20  # 最大步长，防止加速过快
    min_step =5

    current_step = step1  # 当前步长
    last_pulse_width = 500  # 上一次的脉冲宽度
    last_time = time.time()  # 上一次的时间戳
    pulse_width = 500  # 初始脉冲宽度

    for j in range(3):  # 只循环一次，可以根据需要调整
        time.sleep(0.01)
        # 加速过程
        # pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
        for i in range(300):
            # 计算脉冲宽度，确保在500到2500之间
            pulse_width = 500 + i * current_step
            if pulse_width > 1500:  # 当脉冲宽度超过1500时停止
                pulse_width = 1500
                break
            pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
            pwm.setServoPulse(1, int(pulse_width-1500)/2+1500)  # 设置脉冲宽度
            time.sleep(0.006)

            # 每次迭代后，步长增加，模拟加速
            current_step += acceleration
            if current_step > max_step:
                current_step = max_step

            # 打印当前脉冲宽度和步长以便观察加速过程
            if i % 2== 0:
                current_time = time.time()  # 获取当前时间
                delta_time = current_time - last_time  # 计算时间差
                delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
                speed1 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
                # print(f"Pulse_acc: {int(pulse_width)}, Step: {current_step},Speed:{speed1}")
                print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
                # 更新上一次的脉冲宽度和时间
                last_pulse_width = pulse_width
                last_time = current_time

        # 复位步长，用于减速过程
        current_step = 17
        print("--------------------------")
        time.sleep(0.006)

        # 减速过程
        pulse_width = 1500  # 减速从1500开始
        for i in range(200):
            # 计算脉冲宽度，确保在500到2500之间
            pulse_width = 1500 + i * current_step
            if pulse_width > 2500:  # 当脉冲宽度低于500时停止
                pulse_width = 2500
                break

            pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
            pwm.setServoPulse(1, int(pulse_width - 1500) / 2 + 1500)  # 设置脉冲宽度
            time.sleep(0.006)

            # 每次迭代后，步长减小，模拟减速
            current_step -= deceleration
            if current_step < min_step:
                current_step = min_step

            # 打印当前脉冲宽度和步长以便观察减速过程
            if i % 2 == 0:
                current_time = time.time()  # 获取当前时间
                delta_time = current_time - last_time  # 计算时间差
                delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
                speed2 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
                # print(f"Pulse_dec: {int(pulse_width)}, Step: {current_step},Speed:{speed2}")
                print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
                # 更新上一次的脉冲宽度和时间
                last_pulse_width = pulse_width
                last_time = current_time

        print("==================================")
        time.sleep(0.01)
        pulse_width = 2500  # 减速从1500开始
        for i in range(200):
            # 计算脉冲宽度，确保在500到2500之间
            pulse_width = 2500 -i * current_step
            if pulse_width < 1500:  # 当脉冲宽度低于500时停止
                pulse_width = 5500
                break

            pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
            pwm.setServoPulse(1, int(pulse_width - 1500) / 2 + 1500)  # 设置脉冲宽度
            time.sleep(0.006)

            # 每次迭代后，步长减小，模拟减速
            current_step += acceleration2
            if current_step > max_step:
                current_step = max_step

            # 打印当前脉冲宽度和步长以便观察减速过程
            if i % 2 == 0:
                current_time = time.time()  # 获取当前时间
                delta_time = current_time - last_time  # 计算时间差
                delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
                speed2 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
                # print(f"Pulse_dec: {int(pulse_width)}, Step: {current_step},Speed:{speed2}")
                print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
                # 更新上一次的脉冲宽度和时间
                last_pulse_width = pulse_width
                last_time = current_time
        print("------------------------------------")
        current_step = 17
        time.sleep(0.01)

        for i in range(300):
            # 计算脉冲宽度，确保在500到2500之间
            pulse_width = 1500 -i * current_step
            if pulse_width < 500:  # 当脉冲宽度超过1500时停止
                pulse_width = 500
                break
            pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
            pwm.setServoPulse(1, int(pulse_width-1500)/2+1500)  # 设置脉冲宽度
            time.sleep(0.006)

            # 每次迭代后，步长增加，模拟加速
            current_step -= deceleration2
            if current_step < min_step:
                current_step = min_step

            # 打印当前脉冲宽度和步长以便观察加速过程
            if i % 2== 0:
                current_time = time.time()  # 获取当前时间
                delta_time = current_time - last_time  # 计算时间差
                delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
                speed1 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
                # print(f"Pulse_acc: {int(pulse_width)}, Step: {current_step},Speed:{speed1}")
                print(f"Pulse2_acc: {int(pulse_width-1500)/2+1500}")
                # 更新上一次的脉冲宽度和时间
                last_pulse_width = pulse_width
                last_time = current_time


if __name__ == "__main__":
    # global flag_break
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(60)

    model_file = "opencv_face_detector_uint8.pb"
    config_file = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_file, config_file)

    threshold = 0.7

    freq = cv2.getTickFrequency()  # 系统频率

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    # obama_image = face_recognition.load_image_file("obama.jpg")
    # obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    #
    # # Load a second sample picture and learn how to recognize it.
    # biden_image = face_recognition.load_image_file("biden.jpg")
    # biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

    # xiaolin_image = face_recognition.load_image_file("xiaolin.jpg")
    # xiaolin_face_encoding = face_recognition.face_encodings(xiaolin_image)[0]
    #
    # # Create arrays of known face encodings and their names
    # known_face_encodings = [
    #     # obama_face_encoding,
    #     # biden_face_encoding,
    #     xiaolin_face_encoding
    # ]
    # known_face_names = [
    #     # "Barack Obama",
    #     # "Joe Biden",
    #     "xiaolin"
    # ]
    #
    # # Initialize some variables
    # face_locations = []
    # face_encodings = []
    # face_names = []
    # process_this_frame = True
    photo_counter = 0  # Counter for saved images

    count_face = 0

    # 原始范围和目标范围
    from_min = 45
    from_max = 285
    to_min =2000
    to_max = 1000
    # 要映射的值（165是示例）
    value = 165
    # 调用函数映射值
    # mapped_value = map_value(value, from_min, from_max, to_min, to_max)
    init()
    frame_skip = 1  # 每隔3帧处理一次
    frame_count = 0
    pid_h = PIDController(Kp=1.4, Ki=0, Kd=0.1)  # 水平方向的 PID 控制器
    pid_v = PIDController(Kp=0.5, Ki=0, Kd=0.1)  # 竖直方向的 PID 控制器
    count=0
    flag_face=False
    left=0.0
    top=0.0
    right=0.0
    down=0.0
    while True:
        count+=1
        t0=time.time()
        flag_break=False
        flag_break2=False
        # Grab a single frame of video
        success, img = video_capture.read()
        img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        if not success:
            break

        blob = cv2.dnn.blobFromImage(img, 1.0, (150, 150), [104, 117, 123], False, False)
        H, W = img.shape[:2]
        tt2 = time.time()
        t1 = cv2.getTickCount()

        net.setInput(blob)

        detections = net.forward()

        t2 = cv2.getTickCount()
        tt3 = time.time()
        fps = freq / (t2 - t1)
        print("fps:",fps)
        ######显示执行速度
        # cv2.putText(img, 'FPS: %.2f' % (fps), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        for i in range(detections.shape[2]):

            ##  获取分数
            score = detections[0, 0, i, 2]
            if score < threshold:
                continue

            ### 获取位置
            left = int(detections[0, 0, i, 3] * W)
            top = int(detections[0, 0, i, 4] * H)
            right = int(detections[0, 0, i, 5] * W)
            down = int(detections[0, 0, i, 6] * H)
            print("left,top,right,down:", left, top, right, down)
            #######画框
            # cv2.rectangle(img, (left, top), (right, down), (0, 255, 0), 3)

            ########写分数
            # cv2.putText(img, '%.4f' % (score), (left, top + 12), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))

            #######显示检测结果
        # cv2.imshow("FACE", img)
        cycle_time = tt1 - last_tt1
        # print("tt1:",tt1)
        # print("last_tt1:",last_tt1)
        print("cycle_time:", cycle_time)
        last_tt1 = tt1
        # Only process every other frame of video to save time
        # if frame_count % frame_skip == 0:
        #     # Resize frame of video to 1/4 size for faster face recognition processing
        #     small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        #
        #     # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        #     rgb_small_frame = small_frame[:, :, ::-1]
        #
        #     # Find all the faces and face encodings in the current frame of video
        #     face_locations = face_recognition.face_locations(rgb_small_frame,model="hog")
        #     print("!!!Face locations:",face_locations)
        #     if face_locations == []:
        #         flag_face=True
        #         print("No face detected!")
        #         position=[165,110]
        #     face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        #
        #     face_names = []
        #     for face_encoding in face_encodings:
        #         # See if the face is a match for the known face(s)
        #         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        #         name = "Unknown"
        #
        #         # # If a match was found in known_face_encodings, just use the first one.
        #         # if True in matches:
        #         #     first_match_index = matches.index(True)
        #         #     name = known_face_names[first_match_index]
        #
        #         # Or instead, use the known face with the smallest distance to the new face
        #         face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        #         best_match_index = np.argmin(face_distances)
        #         if matches[best_match_index]:
        #             name = known_face_names[best_match_index]
        #
        #         face_names.append(name)
        #
        #         # Save the current frame as an image when a face is detected
        #         if name == "Unknown":  # Only save the photo if the face is recognized
        #             count_face+=1
        #             # print("count_face:",count_face)
        #             if count_face==3:
        #                 photo_filename = f"unknown{photo_counter}.jpg"
        #                 cv2.imwrite(photo_filename, frame)
        #                 print("!!!!!!!!!!!!!!!!")
        #                 print(f"Photo saved as {photo_filename}")
        #                 print("!!!!!!!!!!!!!!!!")
        #                 photo_counter += 1  # Increment the counter for each photo saved
        # # process_this_frame = not process_this_frame
        # frame_count += 1
        # Display the results
        t1=time.time()
        # for (top, right, bottom, left), name in zip(face_locations, face_names):
            # print("top:",top)
            # print("right:",right)
            # print("bottom:",bottom)
            # print("left:",left)
        print("count:",count)
        position=[(left+right)//2,(top+down)//2]
        print("position[0]:",position[0])########   x范围45,165,285
        print("position[1]:",position[1])########   x范围45,165,285
        # cur_t=time.time()
        # # print("cur_t:",cur_t)
        # print("!!!position[0]-last_pos_0:",position[0]-last_pos_0)
        # print("cur_t-last_t:",cur_t-last_t)
        # speed=(position[0]-last_pos_0)/(cur_t-last_t)
        # print("!!!speed:",speed)
        # mapped_value = map_value(position[0], from_min, from_max, to_min, to_max)

        x = position[0]
        y = position[1]
        error_x = (position[0] - 165)
        error_y = (position[0] - 110)
        print("!!!error_x,err_y:",error_x,error_y)
        speed_h = pid_h.update(error_x)
        speed_v = pid_v.update(error_y)
        print("!!!speed_h:",speed_h)
        print("!!!speed_v:",speed_v)
        # if abs(position[0]-165)<10:
        #     flag_break = True
        #     print("Center")
        #     speed_control(0,0)
        # if position[0]<=155:
        #     print("Right")
        #     # print("max(abs(position[0]-165)*,100):",max(abs(position[0]-165)*5,120))
        #     # print("max(abs(speed_h)*3,80):",max(abs(speed_h)*3,80))
        #     # speed_control(max(abs(speed_h)*3,80))
        #     speed_control( abs(int(speed_h*2)),40)
        # elif position[0]>=175:
        #     print("Left")
        #     # print("-max(abs(position[0]-165)*,100):",-max(abs(position[0]-165)*5,120))
        #     # print("-max(abs(speed_h) * 3, 80):",-max(abs(speed_h) * 3, 80))
        #     # speed_control(-max(abs(speed_h) * 3, 80))
        #     speed_control( -abs(int(speed_h*2)),40)

        center_x_min = 155
        center_x_max = 175
        center_y_min = 100
        center_y_max = 120
        # center_x_min = 604
        # center_x_max = 644
        # center_y_min = 415
        # center_y_max = 455
        if center_x_min <= x <= center_x_max and center_y_min <= y <= center_y_max:
            # 中心区域
            print("Center-Center")
            flag_break = True
            flag_break2 = True
            speed_control(0, 0,0)

        elif x < center_x_min and center_y_min <= y <= center_y_max:
            # 左边 & 垂直中心
            print("Left-Center")
            flag_break2 = True
            speed_control(abs(int(speed_h*2.5)), 0,20)

        elif x > center_x_max and center_y_min <= y <= center_y_max:
            # 右边 & 垂直中心
            print("Right-Center")
            flag_break2 = True
            speed_control(-abs(int(speed_h*2.5)), 0,20)

        elif center_x_min <= x <= center_x_max and y < center_y_min:
            # 水平中心 & 上
            print("Center-Up")
            flag_break = True
            speed_control(0, abs(int(speed_v*1.2)),20)

        elif center_x_min <= x <= center_x_max and y > center_y_max:
            # 水平中心 & 下
            print("Center-Down")
            flag_break = True
            speed_control(0, -abs(int(speed_v*1.2)),20)

        elif x < center_x_min and y < center_y_min:
            # 左边 & 上
            print("Left-Up")
            speed_control(abs(int(speed_h*2.5)), abs(int(speed_v*1.2)),20)

        elif x < center_x_min and y > center_y_max:
            # 左边 & 下
            print("Left-Down")
            speed_control(abs(int(speed_h*2.5)), -abs(int(speed_v*1.2)),20)

        elif x > center_x_max and y < center_y_min:
            # 右边 & 上
            print("Right-Up")
            speed_control(-abs(int(speed_h*2.5)), abs(int(speed_v*1.2)),20)

        elif x > center_x_max and y > center_y_max:
            # 右边 & 下
            print("Right-Down")
            speed_control(-abs(int(speed_h*2.5)), -abs(int(speed_v*1.2)),20)
        # top *= 4
        # right *= 4
        # down *= 4
        # left *= 4
        # Draw a box around the face
        # cv2.rectangle(frame, (left, top), (right, down), (0, 0, 255), 2)

        # Draw a label with a name below the face
        # cv2.rectangle(frame, (left, down - 35), (right, down), (0, 0, 255), cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # cv2.putText(frame, name, (left + 6, down - 6), font, 1.0, (255, 255, 255), 1)
        # last_t=cur_t
        # # print("last_t:",last_t)
        # last_pos_0=position[0]
        # print("last_pos_0:",last_pos_0)
        # Display the resulting image
        t2=time.time()
        d_t2=t2-t1
        d_t1=t1-t0
        print("d_t1:",d_t1)
        print("d_t2:",d_t2)
        # cv2.imshow('Video', img)
        flag_face = False
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
