#!/usr/bin/env python3
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
from datetime import datetime
import io
import time
import subprocess
from collections import deque
from threading import Event
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
audio_file_stack_length=0
silent_start_time=0
silent_end_time=0
count2=0
face_detection_switch=False
paizhao_voice_command=False
conversion_success=False

message_id_get=None
data_id_no_send=None
photo_base64=None
generate_photo_base64=False
nihao_detected=False
hello_detected=False
result_detected=False
xiaoqi_detected_count=0
message_id=0
file_counter = 0
no_match_but_valid=False
resp_code_id=0
sleep_detected=False
output_audio_stack = deque()
play_haode=False
is_silent_flag=False

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


# def motor_test():
#     step1=10
#     for j in range(4):
#         print("cycle: %d",j)
#         for i in range(100):
#             pwm.setServoPulse(0,1500-i*step1)  # jaw
#             # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
#             time.sleep(0.01)
#             if i%5==0:
#                 print(1500-i*step1)
#
#
#         for i in range(200):
#             pwm.setServoPulse(0, 500 + i * step1)  # jaw
#             # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
#             time.sleep(0.01)
#             if 500 + i * step1==1500:
#                 time.sleep(2)
#             if i % 5 == 0:
#                 print( 500 + i * step1)
#         for i in range(100):
#             pwm.setServoPulse(0, 2500 - i * step1)  # jaw
#             # pwm.setServoPulse(12, 1500+i*step1 )  # jaw
#             time.sleep(0.01)
#             if i % 5 == 0:
#                 print(2500 - i * step1)
#         time.sleep(2)

def speed_control(speed,speed2,step):
    global flag_break,flag_break2,current_pulse_width,current_pulse_width2
    min_pulse = 500
    max_pulse = 2500
    center_pulse = start_angel1  # 中心位置的脉冲宽度
    center_pulse2=start_angel0
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
            pwm.setServoPulse(1, int(pulse_width))
        else:
            print("Flag_break is set, skipping pwm.setServoPulse for channel 0")

        if not flag_break2:
            # 设置通道 1 的脉冲宽度
            # print("set channel 1")
            pwm.setServoPulse(0, int(pulse_width2))
        else:
            print("Flag_break2 is set, skipping pwm.setServoPulse for channel 1")

        pulse_width += current_step  # 根据速度增加或减少脉冲宽度
        pulse_width2 += current_step2  # 根据速度增加或减少脉冲宽度
        if pulse_width>1700:
            pulse_width =1700
        elif pulse_width<800:
            pulse_width=800
        if pulse_width2 > 1700:
            pulse_width2 = 1700
        elif pulse_width2 < 800:
            pulse_width2 = 800

            # 控制时间间隔，以达到指定的速度
        time.sleep(0.007)  # 控制循环速度，值可以调整以匹配实际硬件响应

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
start_angel1=1500-200
start_angel0=1450-200
def init():
    global switch_flag, old_switch_flag, stop_event, thread3

    pwm.setServoPulse(1, start_angel1)  # jaw
    pwm.setServoPulse(0, start_angel0)  # jaw

    for i in range(1):
        time.sleep(5)
        print("##################start################")

def map_value(value, from_min, from_max, to_min, to_max):
    # 使用线性映射公式
    return int(to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min))


# def motor_test_acc():
#     step1 = 5  # 初始步长
#     acceleration = 0.05 # 加速度调节量
#     deceleration = 0.07# 加速度调节量
#     acceleration2= 0.08
#     deceleration2=0.03
#     current_step = step1  # 当前步长
#     max_step = 20  # 最大步长，防止加速过快
#     min_step =5
#
#     current_step = step1  # 当前步长
#     last_pulse_width = 500  # 上一次的脉冲宽度
#     last_time = time.time()  # 上一次的时间戳
#     pulse_width = 500  # 初始脉冲宽度
#
#     for j in range(3):  # 只循环一次，可以根据需要调整
#         time.sleep(0.01)
#         # 加速过程
#         # pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
#         for i in range(300):
#             # 计算脉冲宽度，确保在500到2500之间
#             pulse_width = 500 + i * current_step
#             if pulse_width > 1500:  # 当脉冲宽度超过1500时停止
#                 pulse_width = 1500
#                 break
#             pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
#             pwm.setServoPulse(1, int(pulse_width-1500)/2+1500)  # 设置脉冲宽度
#             time.sleep(0.006)
#
#             # 每次迭代后，步长增加，模拟加速
#             current_step += acceleration
#             if current_step > max_step:
#                 current_step = max_step
#
#             # 打印当前脉冲宽度和步长以便观察加速过程
#             if i % 2== 0:
#                 current_time = time.time()  # 获取当前时间
#                 delta_time = current_time - last_time  # 计算时间差
#                 delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
#                 speed1 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
#                 # print(f"Pulse_acc: {int(pulse_width)}, Step: {current_step},Speed:{speed1}")
#                 print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
#                 # 更新上一次的脉冲宽度和时间
#                 last_pulse_width = pulse_width
#                 last_time = current_time
#
#         # 复位步长，用于减速过程
#         current_step = 17
#         print("--------------------------")
#         time.sleep(0.006)
#
#         # 减速过程
#         pulse_width = 1500  # 减速从1500开始
#         for i in range(200):
#             # 计算脉冲宽度，确保在500到2500之间
#             pulse_width = 1500 + i * current_step
#             if pulse_width > 2500:  # 当脉冲宽度低于500时停止
#                 pulse_width = 2500
#                 break
#
#             pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
#             pwm.setServoPulse(1, int(pulse_width - 1500) / 2 + 1500)  # 设置脉冲宽度
#             time.sleep(0.006)
#
#             # 每次迭代后，步长减小，模拟减速
#             current_step -= deceleration
#             if current_step < min_step:
#                 current_step = min_step
#
#             # 打印当前脉冲宽度和步长以便观察减速过程
#             if i % 2 == 0:
#                 current_time = time.time()  # 获取当前时间
#                 delta_time = current_time - last_time  # 计算时间差
#                 delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
#                 speed2 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
#                 # print(f"Pulse_dec: {int(pulse_width)}, Step: {current_step},Speed:{speed2}")
#                 print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
#                 # 更新上一次的脉冲宽度和时间
#                 last_pulse_width = pulse_width
#                 last_time = current_time
#
#         print("==================================")
#         time.sleep(0.01)
#         pulse_width = 2500  # 减速从1500开始
#         for i in range(200):
#             # 计算脉冲宽度，确保在500到2500之间
#             pulse_width = 2500 -i * current_step
#             if pulse_width < 1500:  # 当脉冲宽度低于500时停止
#                 pulse_width = 5500
#                 break
#
#             pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
#             pwm.setServoPulse(1, int(pulse_width - 1500) / 2 + 1500)  # 设置脉冲宽度
#             time.sleep(0.006)
#
#             # 每次迭代后，步长减小，模拟减速
#             current_step += acceleration2
#             if current_step > max_step:
#                 current_step = max_step
#
#             # 打印当前脉冲宽度和步长以便观察减速过程
#             if i % 2 == 0:
#                 current_time = time.time()  # 获取当前时间
#                 delta_time = current_time - last_time  # 计算时间差
#                 delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
#                 speed2 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
#                 # print(f"Pulse_dec: {int(pulse_width)}, Step: {current_step},Speed:{speed2}")
#                 print(f"Pulse2_acc: {int(pulse_width - 1500) / 2 + 1500}")
#                 # 更新上一次的脉冲宽度和时间
#                 last_pulse_width = pulse_width
#                 last_time = current_time
#         print("------------------------------------")
#         current_step = 17
#         time.sleep(0.01)
#
#         for i in range(300):
#             # 计算脉冲宽度，确保在500到2500之间
#             pulse_width = 1500 -i * current_step
#             if pulse_width < 500:  # 当脉冲宽度超过1500时停止
#                 pulse_width = 500
#                 break
#             pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
#             pwm.setServoPulse(1, int(pulse_width-1500)/2+1500)  # 设置脉冲宽度
#             time.sleep(0.006)
#
#             # 每次迭代后，步长增加，模拟加速
#             current_step -= deceleration2
#             if current_step < min_step:
#                 current_step = min_step
#
#             # 打印当前脉冲宽度和步长以便观察加速过程
#             if i % 2== 0:
#                 current_time = time.time()  # 获取当前时间
#                 delta_time = current_time - last_time  # 计算时间差
#                 delta_pulse = pulse_width - last_pulse_width  # 计算脉冲宽度差
#                 speed1 = delta_pulse / delta_time  # 计算当前速度（单位：脉冲宽度/秒
#                 # print(f"Pulse_acc: {int(pulse_width)}, Step: {current_step},Speed:{speed1}")
#                 print(f"Pulse2_acc: {int(pulse_width-1500)/2+1500}")
#                 # 更新上一次的脉冲宽度和时间
#                 last_pulse_width = pulse_width
#                 last_time = current_time


def face_detection_run1():
    global running2,face_detection_switch,paizhao_voice_command,photo_base64,generate_photo_base64
    video_capture = cv2.VideoCapture(0)
    photo_counter = 0  # Counter for saved images
    count_face = 0
    # 原始范围和目标范围
    from_min = 45
    from_max = 285
    to_min = 2000
    to_max = 1000
    # 要映射的值（165是示例）
    value = 165
    # 调用函数映射值
    # mapped_value = map_value(value, from_min, from_max, to_min, to_max)

    frame_skip = 1  # 每隔3帧处理一次
    frame_count = 0
    pid_h = PIDController(Kp=1.4, Ki=0, Kd=0.1)  # 水平方向的 PID 控制器
    pid_v = PIDController(Kp=0.35, Ki=0, Kd=0.1)  # 竖直方向的 PID 控制器
    count = 0
    flag_face = False
    left = 0.0
    top = 0.0
    right = 0.0
    down = 0.0
    print("face_detection_switch:",face_detection_switch)
    while running2 and face_detection_switch:
        thread_control_event.wait()

        time.sleep(0.02)
        count += 1
        t0 = time.time()
        flag_break = False
        flag_break2 = False
        # Grab a single frame of video
        success, img = video_capture.read()
        if paizhao_voice_command:
            photo_filename = f"/home/orangepi/vosk-api/python/example/captured_image_{int(tt2)}.jpg"
            cv2.imwrite(photo_filename, img)
            # 使用cv2.imencode将图像转换为JPEG格式的字节流
            retval, buffer = cv2.imencode('.jpg', img)
            if retval:
                # 将字节流转换为Base64字符串
                photo_base64 = base64.b64encode(buffer).decode('utf-8')
                time.sleep(0.02)
                generate_photo_base64=True
                print("send_generate_photo_base64:",generate_photo_base64)
                # send_photo_request(photo_base64)
                send_photo_thread = threading.Thread(target=send_photo_request,args=(photo_base64,))
                send_photo_thread.start()
                # send_photo_thread.join()

        paizhao_voice_command=False


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
        # print("fps:", fps)
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
            # print("left,top,right,down:", left, top, right, down)
            #######画框
            cv2.rectangle(img, (left, top), (right, down), (0, 255, 0), 3)

            ########写分数
            # cv2.putText(img, '%.4f' % (score), (left, top + 12), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))

            #######显示检测结果
        cv2.imshow("FACE", img)
        # cycle_time = tt1 - last_tt1
        # print("tt1:",tt1)
        # print("last_tt1:",last_tt1)
        # print("cycle_time:", cycle_time)
        last_tt1 = tt1

        t1 = time.time()
        # for (top, right, bottom, left), name in zip(face_locations, face_names):
        # print("top:",top)
        # print("right:",right)
        # print("bottom:",bottom)
        # print("left:",left)
        # print("count:", count)
        position = [(left + right) // 2, (top + down) // 2]
        # print("position[0]:", position[0])  ########   x范围45,165,285     ######50, 244   ,438
        # print("position[1]:", position[1])  ########   x范围45,165,285     ######16, 122  ,228

        x = position[0]
        y = position[1]
        # error_x = (position[0] - 165)
        # error_y = (position[0] - 110)
        error_x = (position[0] - 244)
        error_y = (position[0] - 122)
        # print("!!!error_x,err_y:", error_x, error_y)
        speed_h = pid_h.update(error_x)
        speed_v = pid_v.update(error_y)
        # print("!!!speed_h:", speed_h)
        # print("!!!speed_v:", speed_v)

        # center_x_min = 155
        # center_x_max = 175
        # center_y_min = 100
        # center_y_max = 120
        center_x_min = 234 - 2
        center_x_max = 254 + 2
        center_y_min = 112 - 2
        center_y_max = 132 + 2
        # center_x_min = 604
        # center_x_max = 644
        # center_y_min = 415
        # center_y_max = 455
        if center_x_min <= x <= center_x_max and center_y_min <= y <= center_y_max:
            # 中心区域
            print("Center-Center")
            flag_break = True
            flag_break2 = True
            speed_control(0, 0, 0)

        elif x < center_x_min and center_y_min <= y <= center_y_max:
            # 左边 & 垂直中心
            print("Left-Center")
            flag_break2 = True
            speed_control(1.2 * abs(int(speed_h)), 0, 20)

        elif x > center_x_max and center_y_min <= y <= center_y_max:
            # 右边 & 垂直中心
            print("Right-Center")
            flag_break2 = True
            speed_control(-1.2 * abs(int(speed_h)), 0, 20)

        elif center_x_min <= x <= center_x_max and y < center_y_min:
            # 水平中心 & 上
            print("Center-Up")
            flag_break = True
            speed_control(0, -abs(int(speed_v * 1.0)), 20)

        elif center_x_min <= x <= center_x_max and y > center_y_max:
            # 水平中心 & 下
            print("Center-Down")
            flag_break = True
            speed_control(0, abs(int(speed_v * 1.0)), 20)
        #
        elif x < center_x_min and y < center_y_min:
            # 左边 & 上
            print("Left-Up")
            speed_control(1.2 * abs(int(speed_h)), -abs(int(speed_v * 1.0)), 20)

        elif x < center_x_min and y > center_y_max:
            # 左边 & 下
            print("Left-Down")
            speed_control(1.2 * abs(int(speed_h)), abs(int(speed_v * 1.0)), 20)

        elif x > center_x_max and y < center_y_min:
            # 右边 & 上
            print("Right-Up")
            speed_control(-1.2 * abs(int(speed_h)), -abs(int(speed_v * 1.0)), 20)

        elif x > center_x_max and y > center_y_max:
            # 右边 & 下
            print("Right-Down")
            speed_control(-1.2 * abs(int(speed_h)), abs(int(speed_v * 1.0)), 20)
        else:
            print("Something else")

        t2 = time.time()
        d_t2 = t2 - t1
        d_t1 = t1 - t0
        # print("d_t1:", d_t1)
        # print("d_t2:", d_t2)
        # cv2.imshow('Video', img)
        flag_face = False
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Release handle to the webcam
    print("break from face_detection_run1!")
    video_capture.release()
    cv2.destroyAllWindows()





###########################################################
############################################################
############################################################
import webrtcvad
import collections
import argparse
import queue
import sys
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import re
import sys
import librosa
import numpy as np
from multiprocessing import Manager
import time
import threading

# sys.path.append('/home/orangepi/GPT2-chitchat')
# from interact import *
import requests
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderServiceError
import wave
from collections import deque  # 引入环形缓冲区
import asyncio
from scipy import signal


import asyncio
import websockets
import json
import base64
from datetime import datetime
import uuid
from datetime import datetime
import pytz
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import *
import sounddevice as sd
import numpy as np
import wave
from scipy import signal
import time
import subprocess
import asyncio
import websockets
import json
import base64
from datetime import datetime
import uuid
from datetime import datetime
import pytz
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import *
import sounddevice as sd
import numpy as np
import wave
from scipy import signal
import time
import sounddevice as sd
import argparse
from collections import deque  # 引入环形缓冲区
import threading
from vosk import Model, KaldiRecognizer
import re
import sys
import librosa
import webrtcvad
import collections
import argparse
import os
import subprocess
import websocket
import json
import base64
import time
import uuid
import pygame
import sys
import time
import threading
import queue
import cv2
from screeninfo import get_monitors
import subprocess
import pypinyin
###########drawing code
websocket_url = "ws://114.55.90.104:9001/ws"
ws = websocket.create_connection(websocket_url)
ws2 = websocket.create_connection(websocket_url)
# 初始化 pygame
pygame.init()

# 设置窗口模式（800x600）
# screen_width, screen_height = 800, 600
# screen = pygame.display.set_mode((screen_width, screen_height))
# # 设置全屏
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

# 定义颜色
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# 设置笑脸的大小和位置
face_radius = int(min(screen_width, screen_height) * 0.35)  # 占屏幕的 70%
eye_width = int(face_radius * 0.4)
eye_initial_height = int(face_radius * 0.2)  # 初始高度
eye_target_height = int(face_radius * 0.6)  # 目标高度（上部的长方形带椭圆形状）
eye_final_height = int(face_radius * 0.05)  # 第二阶段眯眼高度
eye_glasses_height = int(face_radius * 0.4)  # 最终的眼镜形状高度
initial_eye_radius = 10  # 初始圆角半径
target_eye_radius = eye_width // 2  # 目标圆角半径
final_eye_radius = eye_width // 4  # 眯眼时的圆角半径
glasses_eye_radius = int(face_radius * 0.3)  # 眼镜形状的圆角半径

# 设置眼睛的位置
eye_offset_x = int(face_radius * 0.6)
eye_offset_y = int(face_radius * 0.3)
left_eye_pos = (screen_width // 2 - eye_offset_x, screen_height // 2 - eye_offset_y)
right_eye_pos = (screen_width // 2 + eye_offset_x, screen_height // 2 - eye_offset_y)

# 定义渐变速度
height_step = 2  # 每帧增加或减少的高度
radius_step = 1  # 每帧增加或减少的圆角半径
width_step = 2

# 初始化参数
current_eye_height = eye_initial_height
current_eye_radius = initial_eye_radius
phase = 0  # 动画阶段控制
hold_start_time = None  # 阶段保持时间计时
eye_initial_width = eye_width  # 初始宽度
current_eye_width = eye_initial_width
eye_glasses_width = 220  # 椭圆形的最终宽度
# 创建队列用于线程之间传递用户输入
# phase_queue = queue.Queue()
running=True
running2=True
# 动画绘制初始化
###############
silent_start_time=0
pop_swtich=True
draw_switch=False
# 使用 Event 控制线程的开启和关闭
thread_control_event = threading.Event()
thread_control_event.set()  # 初始状态为允许线程运行
audio_thread_control_event = threading.Event()
audio_thread_control_event.set()  # 初始状态为允许线程运行
start_threads_control = threading.Event()  # 用于控制 start_threads 线程的启动和关闭
websocket_url = "ws://114.55.90.104:9001/ws"
# ws = websocket.create_connection(websocket_url)
ws2 = websocket.create_connection(websocket_url)
xiaoqi_event=Event()
# nihao_event = Event()
# 动画逻辑线程
def animation_logic():
    global phase, current_eye_height, current_eye_radius, hold_start_time, current_eye_width, running,draw_switch
    print("running:",running)
    print("draw_switch:", draw_switch)
    while running and draw_switch:
        thread_control_event.wait()

        if phase == 0:  # phase 0：绘制左眼和右眼
            # 绘制左眼
            left_eye_rect = pygame.Rect(left_eye_pos[0] - current_eye_width // 2,
                                        left_eye_pos[1] - current_eye_height // 2, current_eye_width,
                                        current_eye_height)
            pygame.draw.rect(screen, GREEN, left_eye_rect, border_radius=current_eye_radius)

            # 绘制右眼
            right_eye_rect = pygame.Rect(right_eye_pos[0] - current_eye_width // 2,
                                         right_eye_pos[1] - current_eye_height // 2, current_eye_width,
                                         current_eye_height)
            pygame.draw.rect(screen, GREEN, right_eye_rect, border_radius=current_eye_radius)
            pygame.display.flip()  # 更新屏幕显示


        if phase == 1:
            if current_eye_height < eye_target_height:
                current_eye_height += height_step
            if current_eye_radius < target_eye_radius:
                current_eye_radius += radius_step
            if current_eye_height >= eye_target_height and current_eye_radius >= target_eye_radius:
                phase = 2
        elif phase == 2:
            if current_eye_height > eye_final_height:
                current_eye_height -= height_step
            if current_eye_radius > final_eye_radius:
                current_eye_radius -= radius_step
            if current_eye_height <= eye_final_height and current_eye_radius <= final_eye_radius:
                if hold_start_time is None:
                    hold_start_time = time.time()
                elif time.time() - hold_start_time >= 5:
                    phase = 3
                    hold_start_time = None
        elif phase == 3:
            if current_eye_height < eye_glasses_height:
                current_eye_height += height_step
            if current_eye_radius < glasses_eye_radius:
                current_eye_radius += radius_step
            if current_eye_height >= eye_glasses_height and current_eye_radius >= glasses_eye_radius:
                if hold_start_time is None:
                    hold_start_time = time.time()
                elif time.time() - hold_start_time >= 5:
                    phase = 4
                    hold_start_time = None
        elif phase == 4:
            if current_eye_width < eye_glasses_width:
                current_eye_width += width_step
            if hold_start_time is None:
                hold_start_time = time.time()
            elif time.time() - hold_start_time >= 5:
                phase = 3
                current_eye_height = eye_initial_height
                current_eye_radius = initial_eye_radius
                current_eye_width = eye_initial_width
                hold_start_time = None
        time.sleep(0.02)
video_playing=False
executed_once = False
video_event = threading.Event()
video_path = '/home/orangepi/3.mp4'
pygame.display.set_caption('Eye Animation')
def draw_main():
    global running,executed_once,start_video_playback_flag
    # logic_thread = threading.Thread(target=animation_logic)
    # logic_thread.start()
    st1=time.time()

    while running :
        # print("draw_main is running")
        time.sleep(0.02)  # 控制循环频率
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        screen.fill(BLACK)

        # 绘制左眼
        left_eye_rect = pygame.Rect(left_eye_pos[0] - current_eye_width // 2,
                                    left_eye_pos[1] - current_eye_height // 2, current_eye_width,
                                    current_eye_height)
        pygame.draw.rect(screen, BLUE, left_eye_rect, border_radius=current_eye_radius)

        # 绘制右眼
        right_eye_rect = pygame.Rect(right_eye_pos[0] - current_eye_width // 2,
                                     right_eye_pos[1] - current_eye_height // 2, current_eye_width,
                                     current_eye_height)
        pygame.draw.rect(screen, BLUE, right_eye_rect, border_radius=current_eye_radius)
        pygame.display.flip()

        st2 = time.time()
        # if st2 - st1 > 10 and not pygame.mixer.get_busy():
        if st2 - st1 > 0 and not executed_once and not video_playing:
            start_video_playback_flag=True
            # threading.Thread(target=start_video_playback).start()
            executed_once = True
            # break
            # 在10秒后开始播放视频，确保视频播放只启动一次

            # 如果视频正在播放，暂停pygame绘制
        if video_playing:
            video_event.clear()  # 清除事件，暂停pygame绘制
            video_event.wait()  # 等待视频播放完毕事件

        # if not video_playing and executed_once:
        #     # 视频播放完后，继续绘制
        #     executed_once = False  # 重置标志，确保后续继续绘制
        #     # time.sleep(1)

        pygame.time.delay(40)
    print("break from draw_main!")

    # time.sleep(2)
    pygame.quit()
    print("pygame.quit!")
    sys.exit()


def start_video_playback():
    """ 在后台线程中播放视频 """
    global video_playing
    if video_playing:
        print("Video is already playing.")
        return
    video_playing = True
    # 创建一个 VideoCapture 对象
    cap = cv2.VideoCapture(video_path)

    # 检查视频是否成功打开
    if not cap.isOpened():
        video_playing = False
        print("Error: Could not open video.")
        return

    # 获取屏幕分辨率
    # monitor = get_monitors()[0]
    # print("monitor:",monitor)
    # screen_width = monitor.width
    # screen_height = monitor.height
    # print(f"Screen resolution: {screen_width}x{screen_height}")
    # 创建一个窗口
    # window_name = 'Video Playback'
    # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('Video Playback', screen_width, screen_height)
    # cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, 1)  # 设置全屏
    # remove_window_decor(window_name)  # 去除窗口装饰
    # 循环读取和播放每一帧
    while cap.isOpened():
        ret, frame = cap.read()  # 读取一帧
        if not ret:  # 如果没有读取到帧，视频结束
            print("End of video.")
            break
        # 将 OpenCV 的帧转换为 pygame 可用的格式
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换颜色格式
        frame = pygame.surfarray.make_surface(frame)  # 转换为pygame surface
        # 旋转帧 90 度
        frame = pygame.transform.rotate(frame, -90)
        # 缩放帧以适应屏幕大小
        frame = pygame.transform.scale(frame, (screen_width, screen_height))
        # 在 pygame 窗口中显示视频帧
        screen.blit(frame, (0, 0))
        pygame.display.flip()

        # 每帧等待 40ms，相当于25帧/秒
        pygame.time.delay(40)
        # # 调整帧的大小，适配屏幕分辨率
        # frame_resized = cv2.resize(frame, (screen_width, screen_height))
        #
        # # 显示当前帧
        # cv2.imshow('Video Playback', frame_resized)
        #
        # # 等待 25 毫秒，按 'q' 键退出
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break

    # 释放资源
    video_playing = False
    video_event.set()
    print("Video playback finished.")
    cap.release()
    # cv2.destroyAllWindows()

def remove_window_decor(window_name):
    """ 使用 wmctrl 去除窗口的装饰（无边框） """
    try:
        subprocess.run(['wmctrl', '-r', window_name, '-b', 'remove,decor'], check=True)
    except subprocess.CalledProcessError:
        print(f"Error: Failed to remove window decorations for {window_name}")




no_content_flag=False
xiaoqi_detected = False
first_xiaoqi_detected = False
# xiaoqi_word = ['查询天气', '天气', '小鸡', '小七', '小区', '小气', '消气', '小琴', '小青', '小憩', '效期', '校区',
#                '小觑', '小曲', '小心']
xiaoqi_word=['细胞','七宝','鸡毛','稀薄','七','旗袍','确保','祈祷','去','气']
stop_word = ['停', '停止']
paizhao_word = ['拍', '拍照']
hello_word=['hello','hi','你好','早上好','上午好','好']

websocket_url = "ws://114.55.90.104:9001/ws"
vad = webrtcvad.Vad(1)  # 0-3, 3最灵敏
# 定义帧大小
SAMPLERATE_ORIG = 48000#44100  # 原始采样率（您的麦克风采样率）
# SAMPLERATE_ORIG = 16000
SAMPLERATE_TARGET = 16000  # 目标采样率（VAD支持）
FRAME_DURATION = 30  # ms
# FRAME_SIZE = int(16000 * FRAME_DURATION / 1000)  # assuming 16kHz sample rate
BUFFER_DURATION = 300  # mss
# SAMPLE_RATE = 44100  # 采样率
SAMPLE_RATE = 16000  # 采样率
CHANNELS = 1  # 单声道

SILENCE_THRESHOLD = 700  # 静音阈值
SILENCE_FRAMES = 10  # 静音帧数量阈值
PRE_RECORD_FRAMES = 1  # 预录制帧数
# 定义队列和缓冲区


xiaoqi_detected=False
threads_started = False
video_threads_started=False
first_xiaoqi_detected = False
frames = collections.deque(maxlen=int(BUFFER_DURATION / FRAME_DURATION))

q = queue.Queue()
pre_buffer = deque(maxlen=PRE_RECORD_FRAMES)  # 环形缓冲区，用于保存开头静音
recording = False  # 标志位：是否在录音
recording2=False
silence_counter = 0  # 静音计数器
output_pcm_file = None  # 当前的 .pcm 文件对象
output_wav_file = None  # 当前的 .wav 文件对象
import jieba
noise_break_flag=False #
audio_file_stack = []
flag_append = False
output_file_name = None
audio_file_stack_length=0
data_id1=0
def callback10(indata, frames, time1, status):
    global message_id
    audio_data_dic = (bytes(indata), message_id)
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(audio_data_dic)


######数据格式定义

class VCMethod(str, Enum):
    VOICE_CHAT = "voice-chat"
    TEXT_CHAT = "text-chat"
    PING = "ping"

class ContentType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
# class VCReqData(BaseModel):
#     audio_data: Optional[str] = ""
class VCReqData(BaseModel):
    content_type: Optional[str] = ContentType.AUDIO.value  # audio or image
    content: Optional[str] = "" # base64 encoded data

DataT = TypeVar("DataT")

class Req(BaseModel, Generic[DataT]):
    version: str = "1.0"
    method: VCMethod
    conversation_id: str
    message_id: str
    token: Optional[str] = ""
    timestamp: Optional[str] = ""
    data: Optional[DataT] = None

class VCRespData(BaseModel):
    action: Optional[str] = None
    text: Optional[str] = ""
    audio_format: Optional[str] = "pcm"
    sample_rate: int = 16000
    channels: int = 1
    sample_format: str = "S16LE"
    bitrate: int = 256000
    audio_data: Optional[str] = ""
    stream_seq: int = 0


class Resp(BaseModel, Generic[DataT]):
    version: Optional[str] = ""
    method: Optional[VCMethod] = ""
    conversation_id: Optional[str] = ""
    message_id: Optional[str] = ""
    code: int = 0
    message: str = "success"
    data: Optional[DataT] = None



###id生成

def get_id() -> str:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
    return f"{timestamp}-{uuid.uuid4().hex}"

def get_conversation_id() -> str:
    return uuid.uuid4().hex

def get_message_id() -> str:
    return get_id()


####时间戳生成
def get_rfc3339_with_timezone():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz).isoformat()

last_t1=0
t1=0
def send_photo_request(photo_base64):
    global flag_error, audio_file_stack_length, paizhao_voice_command,\
        generate_photo_base64,nihao_detected,xiaoqi_detected,result_detected,\
        hello_detected,file_counter,message_id,no_match_but_valid,resp_code_id,conversation_id,ws2
    # WebSocket 地址

    # 构建 JSON 请求
    request2 = {
        "version": "1.0",
        "method": "voice-chat",
        "conversation_id": conversation_id,
        "message_id": message_id,
        "token": datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4()),
        # "timestamp": datetime.utcnow().isoformat() + "Z",
        "timestamp": get_rfc3339_with_timezone(),
        "data": {
            "content_type": "image",
            "content": photo_base64
        }
    }

    try:
        # ws.send(json.dumps(request_heartbeat))
        print("json.dumps(request2.message_id):",request2["message_id"])
        print("****************************")
        print("****************************")
        print("****************************")
        print("****************************")
        print("****************************")
        websocket_url = "ws://114.55.90.104:9001/ws"
        ws2 = websocket.create_connection(websocket_url)
        ws2.send(json.dumps(request2))
        print("Photo data sent.")

        file_counter = 1

        # flag_done = False
        # while not flag_done:
        while True:
            time.sleep(0.01)
            if audio_file_stack_length > 1:
                break

            # if nihao_detected:
            #     nihao_detected = False
            #     break

            # if t1 - last_t1 > 3:
            #     # await websocket.send(json.dumps(request_heartbeat))
            #     ws.send(json.dumps(request_heartbeat))
            #     print("Heartbeat sent.")

            # 等待响应
            # response = await websocket.recv()
            try:
                response = ws2.recv()
                response_data = json.loads(response)
                # print("response_data:",response_data)
            except json.JSONDecodeError as e:
                print(f"JSON 解码错误:{e}")
                # print(f"响应内容:{response}")
                continue
            # 检查响应的状态
            if response_data['method'] == 'voice-chat':
                if response_data.get("code") == 0:
                    # 提取并解码音频数据
                    # print("response_data recieived:", response_data["data"])
                    resp_message_id = response_data["message_id"]
                    print("********")
                    print("********")
                    print("!resp_message_id:", resp_message_id)
                    resp_fomat = response_data["data"]["audio_format"]
                    print("resp_fomat:", resp_fomat)

                    audio_base64 = response_data["data"]["audio_data"]
                    audio_bytes = base64.b64decode(audio_base64)
                    seq_li = response_data["data"]["stream_seq"]
                    print("seq_li:", seq_li)
                    response_action = response_data["data"]["action"]
                    print("response_action:", response_action)
                    if response_action == "take_photo":
                        print("web ask to take photo.")
                        paizhao_voice_command = True

                    response_text = response_data["data"]["text"]
                    print("response_text:", response_text)

                    # 将音频数据写入 .pcm 文件
                    # play_audio_data(audio_bytes)

                    file_counter += 1  # 递增文件计数器
                    if str(resp_fomat) == 'mp3':
                        output_file_name = f"2input{file_counter}.mp3"
                        with open(output_file_name, "wb") as pcm_file:
                            pcm_file.write(audio_bytes)
                        print("Saved:", output_file_name)
                        output_wav = f"music0.wav"
                        if os.path.exists(output_wav):
                            # os.remove(output_wav)
                            print(f"Deleted {output_wav}.")
                        subprocess.run(
                            ["ffmpeg", "-i", output_file_name, output_wav]
                        )
                        player = subprocess.Popen(["aplay", "-D", "hw:4,0", output_wav])
                        while player.poll() is None:  # 检查播放器是否仍在运行

                            if nihao_detected or xiaoqi_detected:  # or hello_detected: #or result_detected:  # 检查是否需要停止
                                print("nihao_detected:", nihao_detected)
                                print("Stopping audio playback...")
                                player.terminate()  # 停止播放
                                nihao_detected = False
                                xiaoqi_detected = False
                                # hello_detected=False
                                # result_detected=False
                                break
                            # break

                            time.sleep(0.01)  # 频繁检查是否停止播放

                        # subprocess.run(
                        #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", "16000", "-c", "1", output_file_name])
                    else:
                        audio_buffer = io.BytesIO(audio_bytes)
                        output_audio_stack.append(audio_buffer)
                        output_audio_stack_length = len(output_audio_stack)
                        print("播放栈len:", output_audio_stack_length)
                        # while len(output_file_stack)>0:

                        # output_file_name = output_file_stack.pop(0)
                        # player2 = subprocess.Popen(
                        #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", "16000", "-c", "1", output_file_name])
                        # while player2.poll() is None:  # 检查播放器是否仍在运行
                        #     if nihao_detected or xiaoqi_detected:  # or hello_detected: #or result_detected:  # 检查是否需要停止
                        #         print("nihao_detected:", nihao_detected)
                        #         print("Stopping audio playback...")
                        #         player2.terminate()  # 停止播放
                        #         nihao_detected = False
                        #         xiaoqi_detected = False
                        #         # hello_detected=False
                        #         # result_detected=False
                        #         break
                        #     # break
                        #     time.sleep(0.01)  # 频繁检查是否停止播放
                    # break  # 退出循环????????????????????
                    if nihao_detected or xiaoqi_detected:
                        print("Stopping audio playback due to detection...")
                        break
                    if int(seq_li) == -1:
                        break
                else:
                    # print("Error in response:", response_data.get("message"))
                    flag_done = True
                    break
        generate_photo_base64 = False
    finally:
        # ws2.close()
        print("ws2 closed2!")
###local_output_file_name
is_playing = False
player2 = None  # 初始化播放器变量
haode_file=f"/home/orangepi/vosk-api/python/example/haode.pcm"

play_haode_event = threading.Event()  # 事件对象
def play_haode_function():
    global play_haode,xiaoqi_detected
    while 1:
        time.sleep(0.01)  # 500ms 后执行
        # print("enter play_haode!")
        # print("!!!!!!!!!!!Get_play_haode:",play_haode)
        if play_haode == True and not nihao_detected and not xiaoqi_detected:
            start_time = time.time()  # 记录播放开始时间
            with threading.Lock():
                subprocess.run(
                ["aplay", "-D", "plughw:4,0", "-f", "S16_LE", "-r", "16000", "-c", "1", haode_file])

            play_haode = False
            # time.sleep(1)
            play_haode_event.set()  # 触发事件信号，通知“好”的播放已完成

def playback_thread():
    global nihao_detected, xiaoqi_detected, player2,message_id, \
        no_match_but_valid, output_audio_stack, nihao_event, running2,recording,\
        play_haode,audio_file_stack_length,xiaoqi_event,play_haode_event
    chunk_duration = 0.1  # 每次播放 0.1 秒的音频
    sample_rate = 16000  # 音频采样率
    channels = 1  # 单声道
    bytes_per_sample = 2  # 每个样本 2 字节（16 位 PCM）
    chunk_size = int(sample_rate * bytes_per_sample * channels * chunk_duration)  # 每块音频的大小
    play_haode_event.wait()
    play_haode_event.clear()  # 清除事件信号
  # 清除事件信号
    while running2:
        time.sleep(0.01)
        # if (player2 is not None and player2.poll() is None) or play_haode==True:
        #     # 如果播放器正在运行，等待播放完成
        #     # continue
        # play_haode_event.clear()  # 清除事件信号，准备下一次等待
        # play_haode_event.wait()  # 阻塞直到“好”的播放完成


        if len(output_audio_stack) > 0 :
            # 从栈中取出文件
            audio_buffer = output_audio_stack.popleft()
            audio_buffer.seek(0)  # 确保从缓冲区开头读取
            play_start_time = time.time()
            print("!!!!!!!!!Play_start_time:", play_start_time)
            print("!!!!!!!!!!!Play_message_id:", message_id)

            if no_match_but_valid or nihao_detected or xiaoqi_detected or audio_file_stack_length > 1:
                print("file_name and message_id not match???????????????????????????????????????")
                continue

            # player2 = subprocess.Popen(
            #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", str(sample_rate), "-c", str(channels)],
            #     stdin=subprocess.PIPE
            # )
            with threading.Lock():
                player2 = subprocess.Popen(
                ["aplay", "-D", "plughw:4,0", "-f", "S16_LE", "-r", str(sample_rate), "-c", str(channels)],
                stdin=subprocess.PIPE
            )
            try:
                while True:
                    chunk = audio_buffer.read(chunk_size)  # 读取 0.1 秒的音频块
                    if not chunk:
                        break  # 如果没有更多音频数据，退出播放

                    # 将音频块写入播放器
                    player2.stdin.write(chunk)

                    # 检查中断信号
                    if xiaoqi_event.is_set() or nihao_detected or xiaoqi_detected or no_match_but_valid or audio_file_stack_length > 1:
                        print("$$$$$$$$$$$$$$$$$")
                        print("xiaoqi_event.is_set():",xiaoqi_event.is_set())
                        print("nihao_detected:",nihao_detected)
                        print("xiaoqi_detected:",xiaoqi_detected)
                        print("no_match_but_valid:",no_match_but_valid)
                        print("audio_file_stack_length > 1:",audio_file_stack_length)
                        print("$$$$$$$$$$$$$$$$$")
                    # if nihao_event.is_set() or nihao_detected or xiaoqi_detected or no_match_but_valid or recording==True:
                        print("Stopping audio playback due to detection...")
                        player2.terminate()  # 停止播放
                        output_audio_stack.clear()  # 清空输出缓冲区
                        # nihao_event.clear()
                        xiaoqi_event.clear()
                        nihao_detected = False
                        xiaoqi_detected = False
                        no_match_but_valid = False
                        break

                    # 每次播放 0.1 秒后检查中断信号
                    time.sleep(chunk_duration)

            except Exception as e:
                print(f"Error during playback: {e}")
            finally:
                try:
                    player2.stdin.close()
                    player2.wait()
                except Exception as e:
                    print(f"Error closing player2: {e}")

        else:

            # 如果栈为空，稍微休眠一段时间
            time.sleep(0.01)

    # play_haode_event.clear()

def send_audio_request(audio_file_path):
    global last_t1,t1,last_t2,t2,flag_error,audio_file_stack_length,paizhao_voice_command,\
        photo_base64,generate_photo_base64,nihao_detected,xiaoqi_detected,result_detected,\
        hello_detected,file_counter,message_id,no_match_but_valid,resp_code_id,\
        conversation_id,output_audio_stack,recording,ws
    # WebSocket 地址

    websocket_url = "ws://114.55.90.104:9001/ws"
    ws = websocket.create_connection(websocket_url)
    # 加载音频文件并编码为 base64
    with open(audio_file_path, "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        # audio_data = resample_audio1(audio_data, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
    # 构建 JSON 请求
    request = {
        "version": "1.0",
        "method": "voice-chat",
        "conversation_id": conversation_id,
        "message_id": message_id,
        "token": datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4()),
        # "timestamp": datetime.utcnow().isoformat() + "Z",
        "timestamp":get_rfc3339_with_timezone(),
        "data": {
            "content_type": "audio",
            "content": audio_data
        }
    }
    print("message_id_send_request:",message_id)

    try:
        ws.send(json.dumps(request))
        print("Audio data sent.")
        last_t1 = t1
        # flag_done = False
        # while not flag_done:
        while True:
            # nihao_detected = False
            # xiaoqi_detected = False
            time.sleep(0.01)
            # if nihao_detected or xiaoqi_detected:
            #     print("Stopping audio playback due to detection...")
            #     nihao_detected=False
            #     xiaoqi_detected=False
            #     break
            # nihao_detected = False
            # rewaken_flag=False
            # if nihao_detected:
            #     nihao_detected = False
            #     break
            t1 = time.time()
            # print("@@@@@@SReceive_break_send_audio:", break_send_audio)
            if no_match_but_valid == True or nihao_detected or xiaoqi_detected or audio_file_stack_length > 1:
                print("***************************")
                print("***************************")
                print("no_match_but_valid:",no_match_but_valid)
                print("nihao_detected:", nihao_detected)
                print("xiaoqi_detected:", xiaoqi_detected)
                print("audio_file_stack_length > 1:", audio_file_stack_length > 1)
                print("***************************")
                print("***************************")
                output_audio_stack.clear()
                print("Clear output_file_stack @@SReceive_break_send_audio")
                no_match_but_valid = False
                break_send_audio = False
                nihao_detected = False
                xiaoqi_detected = False
                break

            print("Time_cycle:", t1 - last_t1)
            # 等待响应
            # response = await websocket.recv()
            try:
                response = ws.recv()

                response_data = json.loads(response)
                # print("response_data:",response_data)
            except json.JSONDecodeError as e:
                print(f"JSON 解码错误:{e}")
                # print(f"响应内容:{response}")
                continue
            # 检查响应的状态
            if response_data['method']=='voice-chat':
                if response_data.get("code") == 0 :
                    # 提取并解码音频数据
                    # print("response_data recieived:", response_data["data"])
                    resp_message_id=response_data["message_id"]

                    resp_code_id=response_data["code"]
                    print("********")
                    print("********")
                    print("message_id_get_from_Json:",message_id)
                    print("!!!!!!!!!!!!!Get_resp_message_time:",time.time())
                    print("!!!!!!!!!!!!!!resp_message_id:", resp_message_id)

                    print("!resp_code_id:", resp_code_id,":",type(resp_code_id))
                    if resp_message_id != message_id and int(resp_code_id) == 0:
                        no_match_but_valid = True
                        no_match_but_valid = False
                        print("resp_conversation_id not match !!!!!!!!!!!!!!!!!!!!!???????????????????")
                        break

                    resp_fomat=response_data["data"]["audio_format"]
                    print("resp_fomat:",resp_fomat)
                    audio_base64 = response_data["data"]["audio_data"]
                    audio_bytes = base64.b64decode(audio_base64)
                    seq_li=response_data["data"]["stream_seq"]
                    print("seq_li:",seq_li)
                    response_action=response_data["data"]["action"]
                    print("response_action:", response_action)
                    if response_action=="take_photo":
                        print("web ask to take photo.")
                        paizhao_voice_command=True
                    response_text=response_data["data"]["text"]
                    print("response_text:",response_text)
                    # if audio_file_stack_length>1:
                    #     print("audio_file_stack_length>1 break!!!!!!!!!!!!!!")
                    #     output_audio_stack.clear()
                    #     break
                    # if resp_message_id != message_id:
                    #     no_match_but_valid = True
                    #     print("resp_message_id != message_id break!!!!!!!!!!!!!!")
                    #     no_match_but_valid = False
                    #     output_audio_stack.clear()
                    #     break
                    # if nihao_detected :
                    #     # if recording==True or break_send_audio==True or nihao_detected or xiaoqi_detected or audio_file_stack_length>1:
                    #
                    #     output_audio_stack.clear()
                    #     print("nihao_detected or xiaoqi_detected break!!!!!!.")

                        # nihao_detected = False
                        # xiaoqi_detected = False
                        # break
                    file_counter += 1  # 递增文件计数器
                    if str(resp_fomat) == 'mp3':
                        output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/2input{file_counter}.mp3"
                        with open(output_file_name, "wb") as pcm_file:
                            pcm_file.write(audio_bytes)
                        print("Saved:", output_file_name)
                        output_wav = f"music0.wav"
                        if os.path.exists(output_wav):
                            os.remove(output_wav)
                            print(f"Deleted {output_wav}.")
                        subprocess.run(
                            ["ffmpeg", "-i", output_file_name, output_wav]
                        )
                        print("output_wav1:", output_wav)
                        player = subprocess.Popen(["aplay", "-D", "hw:4,0", output_wav])
                        # player = subprocess.Popen(["aplay", "-D", "hw:0,0", output_wav])
                        while player.poll() is None:  # 检查播放器是否仍在运行
                            if nihao_detected or xiaoqi_detected or audio_file_stack_length > 1: # or hello_detected: #or result_detected:  # 检查是否需要停止
                                print("#################")
                                print("nihao_detected:", nihao_detected)
                                print("xiaoqi_detected:", xiaoqi_detected)
                                print("audio_file_stack_length:", audio_file_stack_length)
                                print("#################")
                                print("Stopping audio playback...")
                                player.terminate()  # 停止播放
                                nihao_detected = False
                                xiaoqi_detected = False
                                # hello_detected=False
                                # result_detected=False
                                break
                            # break
                            time.sleep(0.01)  # 频繁检查是否停止播放

                        # subprocess.run(
                        #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", "16000", "-c", "1", output_file_name])
                    else:
                        # output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/2input{resp_message_id}#{file_counter}.pcm"
                        #
                        # print("!!!!!!!!!!!!!!!Pcm_genarate_time:",time.time())
                        # print("!!!!!!!!!!!!Resp_message_id:",resp_message_id)
                        #
                        # with open(output_file_name, "wb") as pcm_file:
                        #     pcm_file.write(audio_bytes)
                        # print("***********Saved:", output_file_name)
                        audio_buffer = io.BytesIO(audio_bytes)

                        if nihao_detected or xiaoqi_detected or audio_file_stack_length > 1:
                            continue
                        output_audio_stack.append(audio_buffer)
                        output_audio_stack_length = len(output_audio_stack)
                        print("播放栈len:", output_audio_stack_length)
                        # player2=subprocess.Popen(
                        #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", "16000", "-c", "1", output_file_name])
                        # while player2.poll() is None:  # 检查播放器是否仍在运行
                        #     if nihao_detected or xiaoqi_detected: #or hello_detected: #or result_detected:  # 检查是否需要停止
                        #         print("nihao_detected:", nihao_detected)
                        #         print("Stopping audio playback...")
                        #         player2.terminate()  # 停止播放
                        #         nihao_detected = False
                        #         xiaoqi_detected=False
                        #         # hello_detected=False
                        #         # result_detected=False
                        #         break
                        #     # break
                        #     time.sleep(0.01)  # 频繁检查是否停止播放

                    # break  # 退出循环????????????????????
                    if int(seq_li)==-1:
                        break
                else:
                    # print("Error in response:", response_data.get("message"))
                    flag_done = True
                    break

            last_t1 = t1  # 重置最后发送心跳请求的时间
        # generate_photo_base64 = False
            # last_t2 = t2
    finally:
        print("we closed!")
        pass

# 判断是否有语音活动
import webrtcvad

# 初始化 VAD 模块
vad = webrtcvad.Vad()
vad.set_mode(2)  # 设置灵敏度，0 为最低灵敏度，3 为最高灵敏度

def is_speech(data, sample_rate=16000):
    """检测语音活动"""
    # 确保数据长度符合要求（10ms, 20ms 或 30ms）
    frame_duration = 10  # 单位：ms
    frame_size = int(sample_rate * frame_duration / 1000)  # 样本数
    if len(data) != frame_size:
        raise ValueError(f"数据长度不匹配，期望 {frame_size} 样本，实际 {len(data)} 样本")

    # 转换为字节数组
    data_bytes = data.tobytes()

    # 调用 WebRTC VAD 检测语音活动
    return vad.is_speech(data_bytes, sample_rate)

def is_silent(data, threshold=150):
    """检测是否为静音段。"""
    # 将字节数据转换为 numpy 数组
    audio_data = np.frombuffer(data, dtype=np.int16)
    # print("li_audio_data:",audio_data)
    # 检查最大值是否低于阈值
    # print("max:",np.max(np.abs(audio_data)))
    if np.max(np.abs(audio_data)) < threshold:
        # print("检测到静音")
        return True
    else:
        # print("未检测到静音")
        return False

def resample_audio1(audio_data, orig_rate, target_rate):
    """重采样音频数据"""
    # 计算重采样后的长度
    new_length = int(len(audio_data) * target_rate / orig_rate)
    # 执行重采样
    resampled = signal.resample(audio_data, new_length)
    return resampled.astype(np.int16)




def write_variable(value):
    """向共享文件写入变量。"""
    with open(shared_stop_variable_path, "w") as file:
        file.write(value)


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text
start_record_time=0


import numpy as np
from webrtc_audio_processing import AudioProcessingModule as AP
import time
# 加载 PCM 文件
def load_pcm(file_path, dtype=np.int16):
    with open(file_path, 'rb') as f:
        data = np.frombuffer(f.read(), dtype=dtype)
    return data

# 保存 PCM 文件
def save_pcm(file_path, data, dtype=np.int16):
    with open(file_path, 'wb') as f:
        f.write(data.astype(dtype).tobytes())

# 初始化 WebRTC AudioProcessing 模块并处理音频
def process_audio(input_pcm_file, output_pcm_file, sample_rate=16000):
    # 加载原始 PCM 文件
    audio_data = load_pcm(input_pcm_file)
    print(f"Loaded audio data: {len(audio_data)} samples at {sample_rate} Hz")

    # 初始化 WebRTC AudioProcessing 模块
    ap = AP(enable_vad=True, enable_ns=True)
    ap.set_stream_format(sample_rate, 1)  # 设置采样率和单通道

    ap.set_ns_level(3)  # 设置噪声抑制级别（0-3）
    ap.set_vad_level(3)  # 设置语音活动检测级别（0-3）

    # 分块处理音频（10ms 每块）
    frame_size = sample_rate // 100  # 每块 10ms
    processed_audio = []
    for i in range(0, len(audio_data), frame_size):
        audio_chunk = audio_data[i:i+frame_size]
        if len(audio_chunk) < frame_size:
            # 如果最后一块不足 10ms，用 0 填充
            audio_chunk = np.pad(audio_chunk, (0, frame_size - len(audio_chunk)))

        # 处理音频块
        audio_out = ap.process_stream(audio_chunk.tobytes())
        processed_audio.append(np.frombuffer(audio_out, dtype=np.int16))

    # 合并处理后的音频
    processed_audio = np.concatenate(processed_audio)

    # 保存处理后的 PCM 文件
    save_pcm(output_pcm_file, processed_audio)
    print(f"Processed audio saved to {output_pcm_file}")
t_play_haode=time.time()
def callback(indata, frames, time1, status):
    """每次接收音频数据时调用"""
    global t_play_haode,output_file_name, recording, silence_counter, output_pcm_file, pre_buffer, audio_file_stack, \
        noise_break_flag, silent_start_time, silent_end_time, pop_swtich, message_id, start_record_time,play_haode,is_silent_flag
    denoise_output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/denoise_output{message_id}.pcm"
    if status:
        print(status, file=sys.stderr)

    # 计算当前帧的音量能量
    volume = np.abs(indata).mean()
    indata = resample_audio1(indata, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
    current_time = time.time()
    # if current_time-t_play_haode>1:
    #     play_haode_event.set()
    if is_silent_flag==False:
        if volume >= SILENCE_THRESHOLD:
            noise_break_flag = True
            silence_counter = 0  # 重置静音计数器

            if not recording:
                print("开始录音......")
                recording = True
                start_record_time = current_time  # 记录录音开始时间

                message_id_orin = get_message_id()
                message_id = message_id_orin
                print("message_id_born:", message_id)

                output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/output{message_id}.pcm"

                print("output_file_name:", output_file_name)
                output_pcm_file = open(output_file_name, "wb")

                # 写入预缓冲中的静音帧，仅在录音开始时
                for frame in pre_buffer:
                    output_pcm_file.write(frame.tobytes())
                pre_buffer.clear()

            # 写入当前音频帧
            output_pcm_file.write(indata.tobytes())

            # 如果录音时间超过4秒，立即停止录音
            if current_time - start_record_time > 4:
                print("录音时间超过4秒，停止录音")
                recording = False
                output_pcm_file.close()
                # process_audio(output_file_name, denoise_output_file_name)

                if pop_swtich and output_file_name is not None:
                    audio_file_stack.append(output_file_name)
                    print("append_output_file_name:", output_file_name)
                    print("append audio_file_stack:", audio_file_stack)
                output_pcm_file = None

        else:  # 静音帧
            if recording:
                # 写入当前静音帧
                output_pcm_file.write(indata.tobytes())
                silence_counter += 1

                # 如果静音超过指定时间或总录音时长超过4秒，立即停止录音
                if current_time - start_record_time > 1.0 and silence_counter >= 2:
                    print("检测到静音，停止录音")
                    recording = False
                    output_pcm_file.close()
                    # process_audio(output_file_name, denoise_output_file_name)
                    if pop_swtich and output_file_name is not None:
                        play_haode=True
                        t_play_haode=time.time()
                        # print("!!!!!!!!!!!!!!!Send_play_haode:", play_haode)
                        audio_file_stack.append(output_file_name)
                        print("append_output_file_name:", output_file_name)
                        print("append audio_file_stack:", audio_file_stack)
                    output_pcm_file = None
            else:
                # 保存静音帧到预缓冲中，仅在未录音时
                pre_buffer.append(indata.copy())





parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)
# t1 = threading.Thread(main)
# t1.start()
model_path = "/home/orangepi/vosk-model-small-cn-0.22"
text_stack = []
# 定义文件路径
file_path = "/home/orangepi/saved_text.txt"
shared_variable_path = "/home/orangepi/shared_variable.txt"
shared_stop_variable_path = "/home/orangepi/shared_stop_variable.txt"


def write_to_file1(data):
    """将数据写入共享变量文件。"""
    with open(shared_variable_path, "w") as file:
        file.write(str(data))
        # print(f"写入共享变量：{data}")


def read_from_file1():
    """读取共享变量文件中的数据。"""
    with open(shared_variable_path, "r") as file:
        data = file.read().strip()
        # print(f"读取共享变量：{data}")
        return data

def write_to_file(sentence):
    """当共享变量为 0 时写入句子到文件。"""
    while read_from_file1() != "0":
        time.sleep(0.05)  # 如果共享变量不为 0，等待重试

    # 追加写入文件
    with open(file_path, 'a') as file:
        file.write(sentence + "\n")

    # 更新共享变量为 1，表示数据已写入
    write_to_file1(1)


def write_to_file_custom(content):
    """自定义写入函数，根据标志变量决定写入内容。"""
    global first_xiaoqi_detected
    if not first_xiaoqi_detected:
        # 第一次检测到xiaoqi_word时，写入固定内容
        write_to_file("你好，小七")
        first_xiaoqi_detected = True
    else:
        # 后续检测到xiaoqi_word时，写入valid_result
        write_to_file(content)


# device_name = "USB PnP Sound Device"  # 根据实际设备名称进行设置
device_name = "UM10"  # 根据实际设备名称进行设置
# device_name = "SP002Ua"
# device_name='JieLi BR21'
device_index = None
def find_device_index():
    global device_index
    # 遍历设备列表查找设备索引
    for i, device in enumerate(sd.query_devices()):
        print(f"Device {i}: {device['name']}")
        if device_name in device['name'] and device['max_input_channels'] > 0:
            device_index = i
            break
    if device_index is None:
        raise ValueError(f"找不到匹配的设备 '{device_name}'")
    print(f"使用设备: {device_index} - {device_name}")
    return device_index




# def input_stream():
#     global audio_file_stack,device_index
#     device_name = "USB PnP Sound Device"  # 根据实际设备名称进行设置
#
#
#
#
#     with sd.InputStream(samplerate=SAMPLERATE_ORIG, blocksize=FRAME_SIZE,
#                     dtype="int16", channels=1,
#                         callback=callback, device=find_device_index()):
#         print("#" * 80)
#         print("Press Ctrl+C to stop the recording")
#         print("#" * 80)
#         while True:
#             time.sleep(0.05)  # 防止占用过多 CPU
    ######数据格式定义
def main_callback(indata, frames, time1, status):
    global file_counter
    # 调用网络传输的处理函数

    callback(indata, frames, time1, status)
    # 调用本地 Kaldi 处理的处理函数
    callback10(indata, frames, time1, status)
def send_heartbeat():
    global last_t1,t1,last_t2,t2,running2,ws
    # try:
    while running2:
        thread_control_event.wait()
        # 构建 JSON 请求
        request_heartbeat = {
            "version": "1.0",
            "method": "ping",
            # "conversation_id": str(uuid.uuid4()),
            # "message_id": datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4()),
            # "conversation_id": get_conversation_id(),
            # "message_id": get_message_id(),
            # "token": datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4()),
            # # "timestamp": datetime.utcnow().isoformat() + "Z",
            # "timestamp": get_rfc3339_with_timezone(),
            # "data": {}
        }
        # ws = websocket.create_connection(websocket_url)

        ws.send(json.dumps(request_heartbeat))
        # print("heartbeat sent")
        time.sleep(1)
    # finally:
    #     ws.close()

def audio_run():
    global flag_append,audio_file_stack,flag_len,running2,data_id_no_send,generate_photo_base64
    print("audio_run")
    audio_file_stack.clear()
    time.sleep(0.01)  # 保证事件循环可以调度其他任务
    if running2:
        audio_thread_control_event.wait()
        thread_control_event.wait()
        audio_file_stack.append("/home/orangepi/vosk-api/python/example/output_li.pcm")
        time.sleep(0.1)
    # time.sleep(0.1)
    while running2:
        # print("network audio_run!!!")
        audio_thread_control_event.wait()
        thread_control_event.wait()
        flag_len = len(audio_file_stack)

        # print("!!!!!!!!!!!!!!!len(audio_file_stack):",len(audio_file_stack))
        time.sleep(0.03)  # 确保事件循环可以调度其他任务
        # print("Entering while循环")
        # print("发送栈length:", flag_len)
        # if conversion_success==True:
        #     send_audio_request(audio_file_path)
        # if generate_photo_base64:
        #     send_audio_request(audio_file_path)
        if flag_len > 0:
            audio_file_path = audio_file_stack.pop(0)  # 弹出最老的文件
            print(f"audio file: {audio_file_path}")
            # prefix = "output"
            # suffix = ".pcm"
            # audio_file_id = audio_file_path[len(prefix):-len(suffix)]
            # print("audio_file_id:",audio_file_id)
            # print("time_audio_file_id:", time.time())
            # if isinstance(audio_file_id, str) and '_li' not in audio_file_id and data_id_no_send is not None:
            #     data_id_no_send = float(data_id_no_send) if data_id_no_send is not None else 0
            #     if audio_file_id <= data_id_no_send + 1 and audio_file_id >= data_id_no_send - 1:
            #         print("audio_file_id==data_id_no_send, No send")
            #         continue
            audio_file_path = os.path.join("/home/orangepi/vosk-api/python/example", audio_file_path)
            print(f"audio file_full: {audio_file_path}")

            send_audio_request(audio_file_path)
            # run_async(send_audio_request, audio_file_path)
            # success =send_audio_request(audio_file_path)
            # print(f"Send status: {success}")
            # if not success:
            #     # 如果发送失败，继续尝试下一个文件
            #     print("Failed to send audio, retrying with next file.")
            #     continue
        # else:
        #     print("No more audio files to send.")
            # break  # 如果栈空则退出
    print("break from audio_run!")
# def restart_threads():
#     global running2
#     # 将 `running` 设置为 True，允许线程再次运行
#     running2= True
#     # 调用 start_threads() 来启动线程
#     start_threads()

# def stop_threads():
#     global running2, threads_started
#     running2 = False
#     threads_started = False
#     print("Threads stopped.")
def stop_threads():
    print("Threads stopped.")

    thread_control_event.clear()  # 停止子线程的执行
log_file_path = "/home/orangepi/vosk-api/python/example/servo_pulse_log.txt"
def start_threads():
    global threads_started,running,audio_file_stack,running2,start_threads_control,start_video_playback_flag,conversation_id
    # 确保线程只启动一次
    print("enter start_threads")
    # if threads_started:
    #     # print("Threads are already started.")
    #     return
    # recording_thread = threading.Thread(target=input_stream)
    # recording_thread.daemon = True
    # recording_thread.start()
    # 启动音频处理线程
    # thread2 = threading.Thread(target=user_input)
    # thread2.start()
    # current_step = 2
    # for i in range(100):
    #     # 计算脉冲宽度，确保在500到2500之间
    #     pulse_width = 1700 - i * current_step
    #     # if pulse_width > 1500:  # 当脉冲宽度超过1500时停止
    #     #     pulse_width = 1500
    #     #     break
    #     # pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
    #     pwm.setServoPulse(0, int(pulse_width))  # 设置脉冲宽度
    #     time.sleep(0.006)
    # pwm.setServoPulse(1, 400)
    pulse_once = True

    while running2:
        start_threads_control.wait()
        print("enter start_threads")
        conversation_id=get_conversation_id()
        # pwm.setServoPulse(1, start_angel1)  # jaw
        print("Entering")
        # try:
        #     # 读取文件内容
        #     with open(log_file_path, "r") as log_file:
        #         file_value = int(log_file.read().strip())  # 读取并转换为整数
        #         print("file_value:", file_value)
        # except FileNotFoundError:
        #     print(f"Log file {log_file_path} not found. Skipping action.")
        #     file_value = None  # 文件不存在时设置为 None
        # except ValueError:
        #     print(f"Invalid value in {log_file_path}. Skipping action.")
        #     file_value = None  # 文件内容无效时设置为 None
        #
        # # 如果值在范围内，执行舵机动作
        # if file_value is not None and start_angel0-30 <= file_value <= start_angel0+30:
        #     current_step = 2
        #     for i in range(150):
        #         pulse_width = start_angel0
        #         calculated_pulse = int(pulse_width - current_step * i)
        #         pwm.setServoPulse(0, calculated_pulse)
        #         time.sleep(0.006)
        #
        #     # 将最终值写入文件
        #     with open(log_file_path, "w") as log_file:
        #         log_file.write(str(calculated_pulse))  # 将最终值写入文件
        #         print("Final calculated_pulse written:", calculated_pulse)
        #
        #     # 文件关闭检查
        #     print(f"File '{log_file_path}' closed: {log_file.closed}")  # 检查文件是否关闭
        #     pulse_once = False

        # thread_draw=threading.Thread(target=draw_main)
        face_detection_run_thread=threading.Thread(target=face_detection_run1)
        heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        audio_processing_thread = threading.Thread(target=audio_run)
        # logic_thread = threading.Thread(target=animation_logic)

        playback_thread_instance = threading.Thread(target=playback_thread, daemon=True)
        playback_thread_instance.start()
        playhaode_thread_instance = threading.Thread(target=play_haode_function, daemon=True)
        playhaode_thread_instance.start()
        # check_thread = threading.Thread(target=check_audio_file_stack)
        # check_thread.start()
        # thread_draw.start()
        face_detection_run_thread.start()
        heartbeat_thread.start()
        audio_processing_thread.start()
        # logic_thread.start()
        if start_video_playback_flag:
            threading.Thread(target=start_video_playback).start()
        start_threads_control.clear()
    # input_stream()
    # threads_started = True
    # audio_processing_thread.join()
    # heartbeat_thread.join()
    # heartbeat_thread.join()
    # face_detection_run_thread.join()
    # threads_started = False
    # threads_started = True
def timer_check():
    global silent_start_time, xiaoqi_detected,recording,pop_swtich,draw_switch,\
        face_detection_switch,xiaoqi_detected_count,sleep_detected
    pulse_within_range = False
    while running:
        time.sleep(0.02)
        if recording:
            silent_start_time = time.time()  # 重置计时
            # print("计时重置为 0")
            time.sleep(0.02)  # 避免连续触发

        elapsed_time = time.time() - silent_start_time
        current_step = 2

        if elapsed_time > 180 and elapsed_time < 1000000 or sleep_detected==True:  # 超过25秒静音
            print("超过25秒静音，停止线程")
            sleep_detected=False
            pop_swtich = False
            draw_switch = False
            face_detection_switch = False
            stop_threads()  # 停止语音线程
            xiaoqi_detected_count = 0
            time.sleep(0.5)

            # 检查文件中的脉冲值是否在范围内
            # with open(log_file_path, "r") as log_file:
            #     for line in log_file:
            #         pulse_value = int(line)
            #         print("file_pulse_value:", pulse_value)
            #         if start_angel0-300-30 <= pulse_value <= start_angel0-300+30:  # 判断是否在范围内
            #             pulse_within_range = True
            #             print(f"Found pulse within range: {pulse_value}")
            #             break
            #         else:
            #             pulse_within_range = False  # 如果不在范围内，标记为 False
            #
            # print("pulse_within_range:", pulse_within_range)
            #
            # # 如果在范围内，执行舵机动作
            # if pulse_within_range:
            #     pulse_width = start_angel0-300
            #     for i in range(150):
            #         final_pulse = int(pulse_width + current_step * i)
            #         pwm.setServoPulse(0, final_pulse)
            #         time.sleep(0.006)
            #
            #     # 将最终脉冲值写入文件
            #     with open(log_file_path, "w") as log_file:
            #         log_file.write(str(final_pulse))  # 写入最终的脉冲值
            #         print(f"Final pulse width written to file: {final_pulse}")



        #
        # if elapsed_time <50 and xiaoqi_detected==True:
        #     print("没超过50秒，但是重新唤醒,not exceeded 50 seconds, but reawake")
        #     # stop_threads()  # 停止所有线程
        #     # audio_thread_control_event.clear()
        #     # xiaoqi_detected = False
        #     time.sleep(0.1)
        #     # pop_swtich = True
        #     # draw_switch = True
        #     # face_detection_switch = True
        #     # audio_thread_control_event.set()
        #     # silent_start_time = time.time()  # 重置计时
        #     xiaoqi_detected=False
        #     # thread_control_event.set()
        #     # start_threads_control.set()  # 启动 start_threads 线程

        else:
            thread_control_event.set()  # 保持事件激活状态，允许线程运行


def kaldi_run2():
    global xiaoqi_detected,silent_start_time,pop_swtich,draw_switch,face_detection_switch,xiaoqi_detected_count

    while running2:
        time.sleep(0.01)
        if xiaoqi_detected:
            pop_swtich=True
            draw_switch=True
            face_detection_switch=True
            xiaoqi_detected_count += 1
            silent_start_time = time.time()  # 重置计时
            xiaoqi_detected = False
            if xiaoqi_detected_count == 1:
                print("Detected 'xiaoqi' 1st time.")
                thread_control_event.set()
                start_threads_control.set()  # 启动 start_threads 线程
            elif xiaoqi_detected_count >= 2:

                # stop_threads()  # 先停止所有子线程
                print("Detected 'xiaoqi' keyword, restarting threads...")
                # thread_control_event.set()
                # start_threads_control.set()  # 启动 start_threads 线程



def text_to_phonemes(text):
    phonemes = pypinyin.lazy_pinyin(text, style=pypinyin.Style.TONE3)  # 带音调拼音
    return phonemes
# 将关键词转换为音素
qibao_phonemes = {word: text_to_phonemes(word) for word in xiaoqi_word}
print("qibao_phonemes:", qibao_phonemes)
stop_phonemes = {word: text_to_phonemes(word) for word in stop_word}
print("stop_phonemes:", stop_phonemes)
hello_phonemes = {word: text_to_phonemes(word) for word in hello_word}
print("hello_phonemes:", hello_phonemes)


target_keywords = ["播放音乐", "七宝", "停止", "抬头","拍照","睡觉"]
def detect_keywords(transcription):
    """从转录文本中检测关键词"""

    for word in target_keywords:
        if word in transcription:
            print(f"Keyword detected: {word}")

keywords = '["播放音乐", "七宝", "停止", "抬头", "拍照","睡觉","[unk]"]'##########关键词必须完全一样才行
def kaldi_listener():
    global count2, silent_start_time, silent_end_time, xiaoqi_detected, running2, running,paizhao_voice_command,\
        message_id_get,data_id_no_send,nihao_detected,result_detected,hello_detected,keywords,sleep_detected,\
        nihao_event,is_silent_flag,xiaoqi_event
    args.samplerate = SAMPLERATE_ORIG

    rec = KaldiRecognizer(model, SAMPLERATE_ORIG, keywords)
    # rec2 = KaldiRecognizer(model, 44100)
    with sd.InputStream(samplerate=args.samplerate, blocksize=8000, device=find_device_index(),
                        dtype="int16", channels=1, callback=main_callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording1")
        print("#" * 80)
        # rec = KaldiRecognizer(model, args.samplerate,'["播放音乐","七宝", "停止", "停", "[unk]"]')
        # print("args.samplerate:", args.samplerate)
        # start_threads()
        count2 = 0
        xiaoqi_detected_count=0
        while True:
            time.sleep(0.01)
            count2 += 1
            is_silent_flag=False
            # print("count2:",count2)
            # if count2 == 2:
            #     silent_start_time = time.time()
            # silent_end_time = time.time()
            # print("silent_end_time-slient_start_time:", silent_end_time - silent_start_time)
            # if count2 > 2 and silent_end_time - silent_start_time > 30:
            #     print("morre than 10s break!!!!!")
            #     running2 = False
            #     time.sleep(0.1)
            # running2 = True
            # print("running2:", running2)
            # time.sleep(0.01)
            audio_data_get = q.get()
            data, message_id_get = audio_data_get
            if is_silent(data):
                print("检测到静音，跳过此段音频")
                is_silent_flag=True
                continue  # 跳过静音段，进入下一个循环
            # frames.append(data)
            # print("data_id_get:", data_id_get)
            # if rec2.AcceptWaveform(data):
            #     # print(rec.Result())
            #     result2 = json.loads(rec2.Result())
            #     print("LI_Result_dict_flow:2", result2)
            #     if result2:
            #         result_detected=True
            # else:
            #     partial2 = json.loads(rec2.PartialResult())
            #     print("LI_Result_dict:partial2", partial2)
            #     partial_text2 = partial2.get("partial2", "")
            #     print(f"Partial Transcription2: {partial_text2}")
                # detect_keywords(partial_text2)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("LI_Result_dict_keyword:", result)
                transcription = result.get("text", "")
                print(f"Transcription@@: {transcription}")
                # detect_keywords(transcription)
                # print("keywords[1]:",target_keywords[1])
                # 检测关键词
                # for word, phonemes in qibao_phonemes.items():
                #     if any(phoneme in recognized_phonemes for phoneme in phonemes):
                if target_keywords[1] in str(transcription):
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")
                    xiaoqi_event.set()
                    xiaoqi_detected = True
                    continue
                else:
                    # print("未检测到qibao关键词，xiaoqi_event.clear")
                    xiaoqi_event.clear()
                    # continue
                # if target_keywords[5] in str(transcription):
                #     print(f"检测到sleep关键词: {target_keywords[5]}")
                #     # print(f"检测到qibao关键词: {phonemes}")
                #     sleep_detected = True
                # if target_keywords[2] in str(transcription) :
                #     print(f"检测到stop_phonemes关键词: {target_keywords[2] }")
                #     # print(f"检测到stop_phonemes关键词: {phonemes}")
                #     nihao_detected=True
                #     nihao_event.set()
                #     continue
                # if target_keywords[3] in str(transcription):
                #     print(f"检测到stop_phonemes关键词: {target_keywords[3]}")
                #     # print(f"检测到stop_phonemes关键词: {phonemes}")
                #     nihao_detected = True
                # if target_keywords[4] in str(transcription):
                #     print(f"识别到paizhao_word: {target_keywords[4]}")
                #     paizhao_voice_command=True
                #     data_id_no_send=int(data_id_get)
                #     print("time_data_id_no_send:", time.time())
                #     print("data_id_no_send:",data_id_no_send)
                    # write_variable("1")
                    # print("共享变量已改为 1")
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "")
                print(f"Partial Transcription: {partial_text}")
                if target_keywords[1] in str(partial_text):
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")
                    xiaoqi_event.set()
                    xiaoqi_detected = True
                    continue
                else:
                    xiaoqi_event.clear()
                    # print("partial未检测到qibao关键词，xiaoqi_event.clear")
                # if target_keywords[5] in str(partial_text):
                #     print(f"检测到sleep关键词: {target_keywords[5]}")
                #     # print(f"检测到qibao关键词: {phonemes}")
                #     sleep_detected = True
                # if target_keywords[2] in str(partial_text):
                #     print(f"检测到stop_phonemes关键词: {target_keywords[2]}")
                #     nihao_event.set()
                #     # print(f"检测到stop_phonemes关键词: {phonemes}")
                #     nihao_detected = True
                #     continue

            if dump_fn is not None:
                dump_fn.write(data)
        print("final:",rec.FinalResult())
if __name__ == "__main__":
    # shape_change2()
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(60)
    model_file = "opencv_face_detector_uint8.pb"
    config_file = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
    threshold = 0.7
    freq = cv2.getTickFrequency()  # 系统频率
    # face_detection_run1()
    init()
    # time.sleep(10)
    try:
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, "input")
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info["default_samplerate"])
        if args.model is None:
            # model = Model(lang="en-us")
            model = Model(model_path)
        else:
            # model = Model(lang=args.model)
            model = Model(model_path)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None
        # kaldi_thread=threading.Thread(target=kaldi_run)
        # kaldi_thread.start()
        start_threads_thread = threading.Thread(target=start_threads)
        start_threads_thread.start()

        kaldi2_thread = threading.Thread(target=kaldi_run2)
        kaldi2_thread.start()

        kaldi_listener_thread = threading.Thread(target=kaldi_listener)
        kaldi_listener_thread.start()

        timer_thread = threading.Thread(target=timer_check)
        timer_thread.start()
        draw_main()
        # start_threads()

        # running2=True
                # xiaoqi_detected = False
            # print("break from while loop")
        # time.sleep(1)
        # with 块结束，关闭当前流，重新启动一个带有 callback1 的 InputStream
        # print("Switching to callback1")
        # with sd.InputStream(samplerate=SAMPLERATE_ORIG2, blocksize=FRAME_SIZE,
        #                     device=find_device_index(), dtype="int16", channels=1,
        #                     callback=callback):
        #     print("#" * 80)
        #     print("Press Ctrl+C to stop the recording2")
        #     print("#" * 80)

    except KeyboardInterrupt:
        print("\nDone")
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ": " + str(e))






