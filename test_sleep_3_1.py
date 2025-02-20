#!/usr/bin/env python3
from asyncio import shield

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
from websocket import WebSocketException, WebSocketConnectionClosedException
from datetime import datetime
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

file_counter = 0
# no_match_but_valid=False
resp_code_id=0
sleep_detected=False
output_audio_stack = deque()
play_haode=False
play_qibaozaina=False
is_silent_flag=False
old_message_id=0
last_message_id=0
continue_shot_and_record=False

sleep_voice_list=[["PREPARE_0e4469908950edf80d00d50388e22b72.mp3","PREPARE_fb554feefb09a53a8bb55c6320e7cdb1.mp3","PREPARE_b28c329834ff637ff3a73c5e01bd7d52.mp3","PREPARE_2e60034d42489d4b7b411366b9295356.mp3"],
                  ["POSTURE_b929bab873c406f9fcecc3abdd324ec1.mp3","POSTURE_c08908db7c842e01fbd8f965dfa85d89.mp3","POSTURE_06d311023745d1a866490c0d0ce42f44.mp3","POSTURE_080ed47b54f21a0b6709de6484d1dc1e.mp3","POSTURE_e444af1a781082ba399ff9eaebb507eb.mp3"],
                  ["BREATHING_a291d037d81ddc94e0fc33bcf729dea9.mp3","BREATHING_4dc3129193b03d217cddf651ba366fe6.mp3","BREATHING_a7c0c188a373ea0a69c1f46f17eaeb31.mp3","BREATHING_36c798c145115acc2b01ca8339fa4981.mp3","BREATHING_9685385b968f6512da7ee169fe861b9c.mp3","BREATHING_7663c2e11fd2cc1179d6850a99db75aa.mp3","BREATHING_d460b7c6cb07b406dcdbde371afca1bc.mp3","BREATHING_bb6957ab273cbdf11a4aae3244e3f5cc.mp3","BREATHING_7941fd6f49d176f0dd2ee7bb0a93afcd.mp3","BREATHING_bd7ce9ce5e10201cdfe0b9bd4f634a5e.mp3","BREATHING_b361ddc8c2ca77b5493c7469c6e9b3d6.mp3",
                   "BREATHING_9dce53484234ed669c45bcd4edb04d22.mp3","BREATHING_5049ad4ccc4a737f2361b13a47090613.mp3","BREATHING_6e8fe98a2b2102f12ced5ea46aea85af.mp3","BREATHING_e55fb3e213cba1408e0ef40c547ae640.mp3","BREATHING_4cb6818bd595b5516cc6e7b4757809cd.mp3","BREATHING_b270ed55b5b4dc2123ec0797ef450cb5.mp3","BREATHING_91003bd2e4ec5844b6c9f5d1c5da573f.mp3","BREATHING_7585a88baebd17e29d5c36a74a2f2bd8.mp3"],
                  ["RELAX_1_f493e41a829211386884d7e1ae27abdf.mp3","RELAX_1_1c8f90b4f914a54f9e8b0ce67fc0952b.mp3","RELAX_1_274cce17599bfbe6d9a887aa46cbe2b8.mp3","RELAX_1_c49ec684c3c07d6a15f0f234bb0b0251.mp3","RELAX_1_225bebee5a4a2dfa4ed8cb756f13f99e.mp3","RELAX_1_55e1498701aa227d2fd8d5ac46ef5d2d.mp3","RELAX_1_ad1e671152487bb40daede8cc38eaf9a.mp3","RELAX_1_11e6a3fa3caa2c265564202c09a2164f.mp3","RELAX_1_0e56b97ebb717c43c9edbbd4a876742e.mp3","RELAX_1_3b2a13dc2c6f2ecbf02a52b8adaf1908.mp3","RELAX_1_1230b134033f975c74a4c63d45ea6d12.mp3"],
                  ["RELAX_2_06728bad68a989b8f735dac2b86102c0.mp3","RELAX_2_02971319602ea73cb3309270c2ca5be3.mp3"],
                  ["SLEEP_READY_af5dbd5a079133dd483b998db2ea2c73.mp3","SLEEP_READY_88a2a7c12cb7637af4df21ff704ee849.mp3"],
                  ]

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
        self.bus = smbus.SMBus(1)
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
        if pulse_width>1800:
            pulse_width =1800
        elif pulse_width<800:
            pulse_width=800
        if pulse_width2 > 1300:
            pulse_width2 = 1300
        elif pulse_width2 < 900:
            pulse_width2 = 900

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
start_angel1=1300
start_angel0=1100
def init():
    global switch_flag, old_switch_flag, stop_event, thread3

    pwm.setServoPulse(1, start_angel1)  # jaw
    pwm.setServoPulse(0, start_angel0)  # jaw

    for i in range(1):
        time.sleep(0.2)
        print("##################start################")

def map_value(value, from_min, from_max, to_min, to_max):
    # 使用线性映射公式
    return int(to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min))


last_x=0
last_y=0
under_score_count=0
photo_base64_list = []
reconnect_flag=False
old_cant_connect_flag=False
def face_detection_run1():
    global under_score_count,running2,face_detection_switch,paizhao_voice_command,photo_base64,generate_photo_base64,last_x,last_y,\
        continue_shot_and_record,photo_base64_list,cant_connect_flag,reconnect_flag,old_cant_connect_flag,li_wait_time
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
    pid_v = PIDController(Kp=0.15, Ki=0, Kd=0.1)  # 竖直方向的 PID 控制器
    count = 0
    flag_face = False
    left = 0.0
    top = 0.0
    right = 0.0
    down = 0.0
    print("face_detection_switch:",face_detection_switch)
    # under_score_count=0
    # local_image_path="/home/li/vosk-api/python/example/guan1.jpg"
    max_photo=0
    while running2 and face_detection_switch:
        thread_control_event.wait()
        tt2 = time.time()
        time.sleep(0.005)
        count += 1
        t0 = time.time()
        flag_break = False
        flag_break2 = False
        # Grab a single frame of video
        success, img = video_capture.read()
        orin_img=img
        print("!!!continue_shot_and_record:",continue_shot_and_record)
        print("!!!count:",count)

        if paizhao_voice_command:
            photo_filename = f"/home/li/vosk-api/python/example/shot_and_recording/captured_image_{int(tt2)}.jpg"
            cv2.imwrite(photo_filename, img)
            # 使用cv2.imencode将图像转换为JPEG格式的字节流
            retval, buffer = cv2.imencode('.jpg', img)
            if retval:
                # 将字节流转换为Base64字符串
                photo_base64 = base64.b64encode(buffer).decode('utf-8')
                time.sleep(0.1)
                generate_photo_base64 = True
                print("send_generate_photo_base64:", generate_photo_base64)
                # send_photo_request(photo_base64)
                send_photo_thread = threading.Thread(target=send_photo_request, args=(photo_base64,))
                send_photo_thread.start()

                # device = get_usb_device()
                # print(f"!!!!!!找到音频设备: {device}")
                with threading.Lock():
                    subprocess.run(
                        ["aplay", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "16000", "-c", "1", take_photo_file])
                # send_photo_thread.join()
        paizhao_voice_command = False

        # if continue_shot_and_record and count%2==1:
        if continue_shot_and_record:
            if count==1:
                max_photo=1
            elif count>1:
                max_photo = 2
            print("shot!")
            photo_filename = f"/home/li/vosk-api/python/example/shot_and_recording/continued_image_{int(tt2)}.jpg"
            cv2.imwrite(photo_filename, img)
            # 使用cv2.imencode将图像转换为JPEG格式的字节流
            retval, buffer = cv2.imencode('.jpg', img)
            if retval:
                # 将字节流转换为Base64字符串
                photo_base64 = base64.b64encode(buffer).decode('utf-8')
                photo_base64_list.append(photo_base64)
                time.sleep(0.01)
                generate_photo_base64=True
                if len(photo_base64_list)>10:
                    print("len(photo_base64_list)>10!!!")
                    cant_connect_flag =True


                    print("cant_connect_flag:",cant_connect_flag)
                    file_path = "/home/li/vosk-api/python/example/sleep_config.json"
                    with open(file_path, 'r', encoding='utf-8') as file:
                        try:
                            data_local = json.load(file)  # 使用 json.load() 来解析文件内容
                            print(data_local)  # 打印读取的 JSON 数据
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                    # find_file_index
                    result = find_file_index(sleep_voice_list, li_filename)

                    if result:
                        p, q = result
                        print(f"File '{li_filename}' found at p={p}, q={q}")
                        if p==0:
                            li_wait_time=1.5
                        if p == 1:
                            li_wait_time = 2
                        if p == 2 and (0<=q<=6 or 9<=q<=12):
                            li_wait_time = 3
                        if p == 2 and (7 <= q <= 8 ):
                            li_wait_time = 8
                        if p == 2 and (13 <= q):
                            li_wait_time = 6
                        if p==3 and (0<= q<=2 or q==5 or q>9):
                            li_wait_time = 8
                        if p == 3 and (3 <= q <= 4 or 6<=q<=8):
                            li_wait_time = 4
                        if p == 4 or 5 :
                            li_wait_time = 8


                        add_files_to_stack(sleep_voice_list, p, q)
                        with open("li_scene_seq.txt", "w") as file_scene:
                            file_scene.write(str(p+1))
                elif len(photo_base64_list)<=max_photo:
                    print("len(photo_base64_list)<=3>!!!")
                    cant_connect_flag = False
                    if old_cant_connect_flag==True:
                        reconnect_flag = True

                print(f"Captured {len(photo_base64_list)} photo(s)")
                print("send_generate_photo_base64:",generate_photo_base64)
                old_cant_connect_flag = cant_connect_flag

                # with threading.Lock():
                #     subprocess.run(
                #         ["aplay", "-D", "plughw:3,0", "-f", "S16_LE", "-r", "16000", "-c", "1", qibaozaine_file])
                # send_photo_request(photo_base64)
                # if len(photo_base64_list) >= 4:
                #     print("Sending 4 photos...")
                #     print("photo_base64_list:",photo_base64_list)
                #     send_photo_thread = threading.Thread(target=send_photo_request,args=(photo_base64_list,))
                #     send_photo_thread.start()
                #     photo_base64_list = []
                # with threading.Lock():
                #     subprocess.run(
                #         ["aplay", "-D", "plughw:4,0", "-f", "S16_LE", "-r", "16000", "-c", "1", take_photo_file])
                # send_photo_thread.join()

        # paizhao_voice_command=False

        img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        if not success:
            break
        photo_filename_contiune=f"/home/li/vosk-api/python/example/continue_image_{int(count)}.jpg"
        blob = cv2.dnn.blobFromImage(img, 1.0, (150, 150), [104, 117, 123], False, False)
        H, W = img.shape[:2]

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
            # print("@@@@@@score:", score)
            if score < threshold:

                if count%10==1:
                    under_score_count+=1
                    # print("under_score_count:", under_score_count)
                    left=244
                    right=244
                    top=62
                    down=62
                    position = [(left + right) // 2, (top + down) // 2]
                    error_x = (position[0] - 244)
                    error_y = (position[1] - 122 -35)
                    under_score = True
                    # print("error_x,error_y:", error_x, error_y)

                else:
                    continue

            ### 获取位置
            if score>=threshold:
                under_score_count=0
                left = int(detections[0, 0, i, 3] * W)
                top = int(detections[0, 0, i, 4] * H)
                right = int(detections[0, 0, i, 5] * W)
                down = int(detections[0, 0, i, 6] * H)
                if count % 2 == 1:
                    print("拍照continue")
                    cv2.imwrite(photo_filename_contiune, orin_img)
            # print("left,top,right,down:", left, top, right, down)
            ######画框
            # cv2.rectangle(img, (left, top), (right, down), (0, 255, 0), 3)



            ########写分数
            # cv2.putText(img, '%.4f' % (score), (left, top + 12), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))

            #######显示检测结果
        # cv2.imshow("FACE", img)
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
        # print("!!!x,y:", x, y)
        if count>300 and (abs(x - last_x) > 50 or abs(y - last_y) > 50):
            print("!!!!!Moved too much, ignore this frame.!!!")
            continue
        # error_x = (position[0] - 165)
        # error_y = (position[0] - 110)
        error_x = (position[0] - 244)
        error_y = (position[1] - 122-35)
        print("under_score_count2:",under_score_count)
        if under_score_count>5:
            error_x=0
            error_y=0
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
        center_y_min = 112 - 2-35
        center_y_max = 132 + 2-35
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
            speed_control(1.4 * abs(int(speed_h)), 0, 20)

        elif x > center_x_max and center_y_min <= y <= center_y_max:
            # 右边 & 垂直中心
            print("Right-Center")
            flag_break2 = True
            speed_control(-1.4 * abs(int(speed_h)), 0, 20)

        elif center_x_min <= x <= center_x_max and y < center_y_min:
            # 水平中心 & 上
            print("Center-Up")
            flag_break = True
            speed_control(0, -abs(int(speed_v * 1.2)), 20)

        elif center_x_min <= x <= center_x_max and y > center_y_max:
            # 水平中心 & 下
            print("Center-Down")
            flag_break = True
            speed_control(0, abs(int(speed_v * 1.2)), 20)
        #
        elif x < center_x_min and y < center_y_min:
            # 左边 & 上
            print("Left-Up")
            speed_control(1.4 * abs(int(speed_h)), -abs(int(speed_v * 1.2)), 20)

        elif x < center_x_min and y > center_y_max:
            # 左边 & 下
            print("Left-Down")
            speed_control(1.4 * abs(int(speed_h)), abs(int(speed_v * 1.2)), 20)

        elif x > center_x_max and y < center_y_min:
            # 右边 & 上
            print("Right-Up")
            speed_control(-1.4 * abs(int(speed_h)), -abs(int(speed_v * 1.2)), 20)

        elif x > center_x_max and y > center_y_max:
            # 右边 & 下
            print("Right-Down")
            speed_control(-1.4 * abs(int(speed_h)), abs(int(speed_v * 1.2)), 20)
        else:
            print("Something else")
        t2 = time.time()
        d_t2 = t2 - t1
        d_t1 = t1 - t0
        last_x=x
        last_y=y
        print("!!!last_x,last_y:", last_x, last_y)
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



# 录音的全局变量
recording2 = False
start_record_time2 = time.time()
audio_memory2 = io.BytesIO()
message_id2 = 0
pre_buffer2 =  deque(maxlen=1)

# 假设的音频数据队列
audio_data_queue2 = []





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
from vosk import Model, KaldiRecognizer, SpkModel
import re
import sys
import librosa
import webrtcvad
import collections
import argparse
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
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

print("AAA")

websocket_url = "ws://114.55.90.104:9001/ws"
# ws=None
ws = websocket.create_connection(websocket_url)
def create_connection_with_retries(url, max_retries=10000, retry_interval=0.3):
    global ws
    """尝试建立 WebSocket 连接，如果断开则重试"""
    retries = 0
    while retries < max_retries:
        try:
            print(f"Trying to connect to {url} (Attempt {retries + 1} / {max_retries})")
            ws = websocket.create_connection(url)

            # remote_host, remote_port = ws.sock.getpeername()
            # print(f"Connected to host: {remote_host}, port: {remote_port}")


            print("Connection successful!")
            return ws
        except (websocket.WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
            print(f"Connection failed: {e}")
            retries += 1
            if retries < max_retries:
                print(f"Waiting for {retry_interval} seconds before retrying...")
                time.sleep(retry_interval)
            else:
                print("Max retry attempts reached. Unable to connect to WebSocket.")
                raise e
    return None



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
print("CCC")

print("DDD")
xiaoqi_event=Event()
recording_event=Event()
output_file_stack=[]

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
video_path = '/home/li/blink2.mp4'
video_path2 = '/home/li/think.mp4'
video_path3 = '/home/li/loading.mp4'
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
        # print("st2 - st1 > 0:",st2 - st1 > 0)
        # print("executed_once:",executed_once)
        # print("video_playing:",video_playing)
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
    global video_playing,flag_think,video_path,video_path2,flag_think2,video_path3
    if video_playing:
        print("Video is already playing.")
        return
    video_playing = True
    # 根据 flag_think 判断播放哪个视频路径
    # current_video_path = video_path2 if flag_think else video_path
    if flag_think and not flag_think2:
        current_video_path = video_path2
    if flag_think2 and not flag_think:
        current_video_path = video_path3
    elif not flag_think and not flag_think2:
        current_video_path = video_path

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
    while video_playing:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 每次视频播放开始时将帧重置到 0
        while cap.isOpened():
            if flag_think and not flag_think2 and current_video_path != video_path2:
                print("Flag think is True, switching to video_path2.")
                cap.release()  # 释放当前视频资源
                current_video_path = video_path2  # 切换到 video_path2
                cap = cv2.VideoCapture(current_video_path)  # 打开新的视频

            if flag_think2 and not flag_think and current_video_path != video_path3:
                print("Flag think is True, switching to video_path2.")
                cap.release()  # 释放当前视频资源
                current_video_path = video_path3  # 切换到 video_path2
                cap = cv2.VideoCapture(current_video_path)  # 打开新的视频

            elif not flag_think and not flag_think2 and current_video_path != video_path:
                print("Flag think is False, switching to video_path.")
                cap.release()  # 释放当前视频资源
                current_video_path = video_path  # 切换到 video_path
                cap = cv2.VideoCapture(current_video_path)  # 打开新的视频



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
            pygame.time.delay(18)
            # # 调整帧的大小，适配屏幕分辨率
            # frame_resized = cv2.resize(frame, (screen_width, screen_height))
            #
            # # 显示当前帧
            # cv2.imshow('Video Playback', frame_resized)
            #
            # # 等待 25 毫秒，按 'q' 键退出
            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break
        # cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置到视频的开头
        # # 判断是否需要切换视频路径
        # if flag_think:  # 如果 flag_think 为 True
        #     print("Flag think is True, played video_path2 once.")
        #
        #     print("Flag think is True, switching to video 2.")
        #     cap.release()  # 释放当前视频资源
        #     current_video_path = video_path2  # 切换到 video_path2
        #     cap = cv2.VideoCapture(current_video_path)  # 打开新的视频
        #     # flag_think=False
        # else:  # 如果 flag_think 为 False
        #     print("Flag think is False, playing video 1.")
        #     cap.release()  # 释放当前视频资源
        #     current_video_path = video_path  # 切换到 video_path
        #     cap = cv2.VideoCapture(current_video_path)  # 打开新的视频
        # # 如果视频播放结束，继续循环
        # print("Video finished, restarting...")

    # 释放资源
    video_playing = False
    video_event.set()
    print("Video playback finished.")
    cap.release()

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

vad = webrtcvad.Vad(1)  # 0-3, 3最灵敏
# 定义帧大小
# SAMPLERATE_ORIG = 48000#44100  # 原始采样率（您的麦克风采样率）
SAMPLERATE_ORIG = 16000
SAMPLERATE_TARGET = 16000  # 目标采样率（VAD支持）
FRAME_DURATION = 30  # ms
# FRAME_SIZE = int(16000 * FRAME_DURATION / 1000)  # assuming 16kHz sample rate
BUFFER_DURATION = 300  # mss
# SAMPLE_RATE = 44100  # 采样率
SAMPLE_RATE = 16000  # 采样率
CHANNELS = 1  # 单声道

SILENCE_THRESHOLD = 800  # 静音阈值
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

print("EEE")
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
def send_photo_request(photo_base64_list):
    global flag_error, audio_file_stack_length, paizhao_voice_command,\
        generate_photo_base64,nihao_detected,xiaoqi_detected,result_detected,\
        hello_detected,file_counter,message_id,resp_code_id,conversation_id,ws,shield_after_send,flag_think2,old_message_id
    # WebSocket 地址
    print("$$$$$$$$$$$$$$$$message_id_send:",message_id)
    # print("sned2_photo_base64_list:",photo_base64_list)
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
            "images": {
                "format": "jpeg",
                "data":
                    photo_base64_list
            }

        }
    }
    retries = 0
    max_retries = 10000
    retry_interval = 0.3
    while True:  # 无限重连直到成功
        try:
            if ws is None or not ws.connected:
                print("WebSocket not connected. Attempting to reconnect...")
                ws = websocket.create_connection(websocket_url)

                # remote_host, remote_port = ws.sock.getpeername()
                # print(f"Connected to host: {remote_host}, port: {remote_port}")
                print("WebSocket reconnected successfully!")

            # 发送照片数据
            ws.send(json.dumps(request2))
            print("Photo data sent successfully.")
            break  # 成功后退出无限重连循环

        except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
            print(f"WebSocket connection failed: {e}")
            print(f"Retrying1 in {retry_interval} seconds...")
            time.sleep(retry_interval)

        except Exception as e:
            print(f"Unexpected error: {e}")
            print(f"Retrying2 in {retry_interval} seconds...")
            time.sleep(retry_interval)

def continue_send_photo():
    global flag_error, audio_file_stack_length, paizhao_voice_command, \
        generate_photo_base64, nihao_detected, xiaoqi_detected, result_detected, \
        hello_detected, file_counter, message_id, resp_code_id, conversation_id, ws, \
        shield_after_send, flag_think2, old_message_id, photo_base64_list,message_id2
    # WebSocket 地址
    retries = 0
    max_retries = 10000
    retry_interval = 0.3
    c_count=0
    while True:
        c_count+=1
        time.sleep(0.01)
        if c_count==1:
            max_photo=1
        elif c_count>1:
            max_photo = 2
        if len(photo_base64_list) >= max_photo:
            with open("li_scene_seq.txt", "r") as file_scene:
                content = file_scene.read().strip()  # 读取并去除空白字符
                if content == 'None' or content == '':
                    print("content is empty or None")
                    li_scene_seq2 = None  # 如果文件为空，可以设置默认值，或者根据需求处理
                else:  # 如果文件内容不是空的
                    li_scene_seq2 = int(content)  # 转换为整数
                    print("li_scene_seq2:", li_scene_seq2)  # 打印读取的值



                # 读取play_status.txt中的字符串
            with open("play_status.txt", "r") as file_status:
                content2 = file_status.read().strip()  # 读取并去除任何多余的空白字符
                if content2 == 'None' or content2 == '':
                    print("content2 is empty or None")
                    play_status2 = ""  # 如果文件为空，可以设置默认值，或者根据需求处理
                else:
                    play_status2 = content2

            with open("play_status.txt", "w") as file_status:
                file_status.write(str("None"))  # 将play_status写入文件，确保是字符串格式（"IN_PROGRESS" 或 "COMPLETED"）

            message_id_orin2 = get_message_id()
            message_id2 = message_id_orin2
            print("Sending 3 photos...")
            print("message_id2:",message_id2)
            print("continue_send_photo conversation_id:",conversation_id)
            request2 = {
                "version": "1.0",
                "method": "report-state",  # 始终使用 "report-state"
                "conversation_id": conversation_id,
                "message_id": message_id2,
                "token": datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4()),
                "timestamp": get_rfc3339_with_timezone(),
                "data": {
                    "images": {
                        "format": "jpeg",
                        "data": photo_base64_list
                    },
                    "scene_exec_status": {
                        "scene_seq": li_scene_seq2,
                        "status": play_status2
                    }
                }

            }
            # print("request2:",request2)
            print("li_scene_seq2:",li_scene_seq2)
            print("play_status2:", play_status2)
            while True:  # 无限重连直到成功
                try:
                    if ws is None or not ws.connected:
                        print("WebSocket not connected. Attempting to reconnect...")
                        ws = websocket.create_connection(websocket_url)
                        # remote_host, remote_port = ws.sock.getpeername()
                        # print(f"Connected to host: {remote_host}, port: {remote_port}")
                        print("WebSocket reconnected successfully!")

                    # 发送照片数据
                    ws.send(json.dumps(request2))
                    print("Photo data sent successfully.")
                    break  # 成功后退出无限重连循环

                except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                    print(f"WebSocket connection failed: {e}")
                    print(f"Retrying3 in {retry_interval} seconds...")
                    time.sleep(retry_interval)

                except Exception as e:
                    print(f"Unexpected error: {e}")
                    print(f"Retrying4 in {retry_interval} seconds...")
                    time.sleep(retry_interval)

            # 清空照片队列
            photo_base64_list.clear()
        # file_counter = 1


###local_output_file_name
is_playing = False
player2 = None  # 初始化播放器变量
import random
qibaozaine_file=f"/home/li/vosk-api/python/example/qibaozaine.pcm"
take_photo_file=f"/home/li/vosk-api/python/example/take_photo.pcm"
play_haode_event = threading.Event()
play_qibaozaina_event= threading.Event()
def play_haode_function():
    global play_haode,xiaoqi_detected
    while 1:
        time.sleep(0.01)  # 500ms 后执行
        # print("enter play_haode!")
        # print("!!!!!!!!!!!Get_play_haode:",play_haode)
        if play_haode == True and not nihao_detected and not xiaoqi_detected:
            start_time = time.time()  # 记录播放开始时间

            pcm_files = [
                "/home/li/vosk-api/python/example/zhegema.pcm",
                "/home/li/vosk-api/python/example/zheyangya.pcm",
                "/home/li/vosk-api/python/example/qibaozaine.pcm",
                "/home/li/vosk-api/python/example/qibaozaiting.pcm",
                "/home/li/vosk-api/python/example/haode.pcm"
            ]

            random_number = random.randint(0, 10000)
            index = random_number % 4
            with threading.Lock():
                subprocess.run(
                ["aplay", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "16000", "-c", "1", pcm_files[index]])

            play_haode = False
            # time.sleep(1)
            play_haode_event.set()  # 触发事件信号，通知“好”的播放已完成

def play_qibaozaine_function():
    global play_qibaozaina, xiaoqi_detected
    while 1:
        time.sleep(0.01)  # 500ms 后执行
        # print("enter play_haode!")
        # print("!!!!!!!!!!!Get_play_haode:",play_haode)
        if play_qibaozaina == True and not nihao_detected and not xiaoqi_detected:
            start_time = time.time()  # 记录播放开始时间

            with threading.Lock():
                subprocess.run(
                    ["aplay", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "16000", "-c", "1", qibaozaine_file])

            play_qibaozaina = False
            # time.sleep(1)
            play_qibaozaina_event.set()  # 触发事件信号，通知“好”的播放已完成

play_queue = queue.Queue()
local_output_file_name_list=[]
# local_output_file_name='/home/li/vosk-api/python/example/A13_4.wav'
bmg_file_name='/home/li/vosk-api/python/example/sleep2.mp3'
bmg_file_name_list = [
    "/home/li/vosk-api/python/example/sleep1.mp3",
    "/home/li/vosk-api/python/example/sleep2.mp3",
    "/home/li/vosk-api/python/example/sleep3.mp3"
]

li_scene_seq=None
play_status=None
# status_queue=queue.Queue()
interrupt_flag=False

garbage_content_event = threading.Event()
add_once_list_flag_with_sleep = False

def mix_play():
    global recording_event,nihao_detected,xiaoqi_detected,local_output_file_name_list,standup_flag,\
        li_voices_list_len,play_status,interrupt_flag,li_wait_time,is_garbage_content,garbage_flag,resp_message_id,message_id

    global qibao_sentence_complete,add_once_list_flag_with_sleep

    while True:
        try:
            # if standup_flag==False:
            #     continue

            if interrupt_flag:
                print("Interrupt skipping")
                time.sleep(0.1)
                continue

            command2,j2,local_output_file_name = play_queue.get()
            old_command2=command2
            old_j2=j2
            old_local_output_file_name=local_output_file_name
            print(f"get from queue: {local_output_file_name}")
            print("command2,j2,local_output_file_name:",command2,j2,local_output_file_name)
            # if command2=="voice-chat":
            #     print("li_voices_list_len:",li_voices_list_len)
            #     if j2<li_voices_list_len-1:
            #         play_status="IN_PROGRESS"
            #     elif j2==li_voices_list_len-1:
            #         play_status = "COMPLETED"
            #     print("li_scene_seq,play_status:",li_scene_seq,play_status)
            #     with open("li_scene_seq.txt", "w") as file_scene:
            #         file_scene.write(str(li_scene_seq))  # 将li_scene_seq写入文件，确保是数字序号的字符串格式
            #     with open("play_status.txt", "w") as file_status:
            #         file_status.write(str(play_status))  # 将play_status写入文件，确保是字符串格式（"IN_PROGRESS" 或 "COMPLETED"）
            # play_status = "IN_PROGRESS"
            if command2=="execute-command":
                if j2<li_voices_list_len-1:
                    play_status="IN_PROGRESS"
                elif j2==li_voices_list_len-1:
                    play_status = "COMPLETED"
                print("play_status:",play_status)

                with open("play_status.txt", "w") as file_status:
                    file_status.write(str(play_status))  # 将play_status写入文件，确保是字符串格式（"IN_PROGRESS" 或 "COMPLETED"）

        except queue.Empty:
            print("队列为空，等待新的音频文件...")
            time.sleep(0.1)
            continue

        if os.path.exists(local_output_file_name):
            print(f"start playing: {local_output_file_name}")
            try:
                voice = pygame.mixer.Sound(local_output_file_name)
                voice_channel = pygame.mixer.Channel(1)
                while standup_flag:
                    print("standup_flag detected, stopping voice playback")
                    voice_channel.stop()
                    time.sleep(0.1)
                    standup_flag=False
                    break

                print("garbage_flag2:", garbage_flag)
                if garbage_flag == 1:
                    print("is garbage")
                    # play_queue.put((old_command2, old_j2, old_local_output_file_name))
                    # print("reput:",old_local_output_file_name)
                    # pygame.mixer.init()
                    # voice2 = pygame.mixer.Sound(local_output_file_name)
                    # print(f"start again playing: {local_output_file_name}")
                    # voice_channel = pygame.mixer.find_channel()
                    # print("voice_channel:",voice_channel)
                    # if not voice_channel:  # 如果没有空闲通道，就分配一个新的
                    #     voice_channel = pygame.mixer.Channel(1)
                    resp_message_id = message_id
                    voice_channel.play(temp_voice)
                    while voice_channel.get_busy():  # 如果音频正在播放
                        pygame.time.wait(20)

                    garbage_content_event.clear()
                    garbage_flag = 0
                    # break
                # elif garbage_flag == 0:
                    # interrupt_flag = True
                    # print("not garbage content")
                    # play_queue.queue.clear()
                    # output_file_stack.clear()
                    # print("2 clear play_queue")
                    # print("2 clear output_file_stack")
                    # with open("play_status.txt", "w") as file_status:
                    #     file_status.write(str(play_status))  # 更新文件
                    # break


                voice_channel.play(voice)

                temp_voice = voice

                print("################")
                print("command and j2",command2,j2)
                print("####################")
                if command2 == "voice-chat":
                    if j2 == -1:
                        qibao_sentence_complete = True
                        interrupt_flag = False
                        add_once_list_flag_with_sleep = True
                if command2 == "execute-command" and (local_output_file_name == "/home/li/vosk-api/python/example/enter_sleep_mode.mp3" or local_output_file_name == "/home/li/vosk-api/python/example/lahuisixu2.mp3"):
                    qibao_sentence_complete = True
                    interrupt_flag = False
                    add_once_list_flag_with_sleep = True


                if li_wait_time is None:
                    li_wait_time=1
                print("li_wait_time2:", li_wait_time)
                print("wait start!!!")
                # time.sleep(li_wait_time*2)

                total_duration = voice.get_length()
                print("total duration:", total_duration)

                start_time = pygame.time.get_ticks()
                print("start time:", start_time)
                interrupted_position = 0

                print("wait end!!!")
                while voice_channel.get_busy() :
                    if command2 == "execute-command":
                        time.sleep(li_wait_time)
                        # (pygame.time.get_ticks() - start_time < li_wait_time * 1000)
                    #current_position = (pygame.time.get_ticks() - start_time) / 1000.0
                    #print("current position:", current_position)
                    # if resp_message_id != message_id:
                    #     print("!resp_message_id != message_id break!")
                    #     voice_channel.stop()  # 停止语音播放
                    #     play_status = "IN_PROGRESS"  # 播放状态更改为IN_PROGRESS
                    #     interrupt_flag = True
                    #     play_queue.queue.clear()
                    #     output_file_stack.clear()
                    #     print("2 clear play_queue")
                    #     print("2 clear output_file_stack")
                    #     with open("play_status.txt", "w") as file_status:
                    #         file_status.write(str(play_status))  # 更新文件
                    #
                    #     break
                    print("resp_message_id:",resp_message_id)
                    print("message_id:",message_id)
                    if resp_message_id != message_id :
                        print("!resp_message_id != message_id break!")
                        voice_channel.stop()  # 停止语音播放
                        interrupt_flag = True
                        garbage_flag=0
                        # print('voice garbage', garbage_flag)
                        time.sleep(0.1)
                        #interrupted_position = current_position
                        #print("interrupted_position:",interrupted_position)
                        play_status = "IN_PROGRESS"  # 播放状态更改为IN_PROGRESS

                        # if current_position >= total_duration:
                        #     print("Audio playback completed.")
                        #     break
                        # if is_garbage_content==True:
                        # print("garbage_flag2:",garbage_flag)
                        # if garbage_flag==1:
                        #     print("is garbage")
                        #     # play_queue.put((old_command2, old_j2, old_local_output_file_name))
                        #     # print("reput:",old_local_output_file_name)
                        #     # pygame.mixer.init()
                        #     # voice2 = pygame.mixer.Sound(local_output_file_name)
                        #     # print(f"start again playing: {local_output_file_name}")
                        #     # voice_channel = pygame.mixer.find_channel()
                        #     # print("voice_channel:",voice_channel)
                        #     # if not voice_channel:  # 如果没有空闲通道，就分配一个新的
                        #     #     voice_channel = pygame.mixer.Channel(1)
                        #     resp_message_id=message_id
                        #     voice_channel.play(voice)
                        #     while voice_channel.get_busy():  # 如果音频正在播放
                        #         pygame.time.wait(20)
                        #
                        #     garbage_content_event.clear()
                        #     garbage_flag=0
                        #     break
                        # elif garbage_flag == 0:
                        #     interrupt_flag = True
                        #     print("not garbage content")
                        #     # play_queue.queue.clear()
                        #     # output_file_stack.clear()
                        #     # print("2 clear play_queue")
                        #     # print("2 clear output_file_stack")
                        #     with open("play_status.txt", "w") as file_status:
                        #         file_status.write(str(play_status))  # 更新文件
                        #     break
                    if standup_flag:
                        print("standup_flag detected, breaking playback")
                        voice_channel.stop()  # 停止语音播放
                        time.sleep(0.1)
                        play_status = "IN_PROGRESS"  # 播放状态更改为IN_PROGRESS
                        with open("play_status.txt", "w") as file_status:
                            file_status.write(str(play_status))  # 更新文件
                        standup_flag = False
                        break
                    if recording_event.is_set() or nihao_detected or xiaoqi_detected :
                        print("!xiaoqi_detected break!")
                        voice_channel.stop()  # 停止语音播放
                        time.sleep(0.1)
                        # 重置打断标志
                        nihao_detected = False
                        xiaoqi_detected = False
                        play_status = "IN_PROGRESS"  # 播放状态更改为IN_PROGRESS
                        with open("play_status.txt", "w") as file_status:
                            file_status.write(str(play_status))  # 更新文件
                        break
                    print(f"语音 {local_output_file_name} 播放完毕")
                    pygame.time.Clock().tick(10)




            except pygame.error as e:
                print(f"播放失败: {e}")
        else:
            print(f"语音文件未找到: {local_output_file_name}")
last_bgm_num=0
def combine_bgm_sound():
    global bmg_file_name_list,bmg_file_name,bgm_num,last_bgm_num,standup_flag
    os.environ["SDL_AUDIODRIVER"] = "alsa"
    os.environ["AUDIODEV"] = "hw:1,0"
    while 1:
        thread_control_event.wait()
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(1.0)

            # 加载并播放背景音乐
            # if os.path.exists(bmg_file_name):
            #     pygame.mixer.music.load(bmg_file_name)
            #     pygame.mixer.music.play(-1)
            #     print(f"bgm {bmg_file_name} is playing")
            # else:
            #     print(f"bgm can't find: {bmg_file_name}")
            #     exit()
            mix_play_thread = threading.Thread(target=mix_play)
            mix_play_thread.start()
            playback_thread_instance = threading.Thread(target=playback_thread, daemon=True)
            playback_thread_instance.start()

            while True:
                time.sleep(0.1)
                # print("bgm_num:",bgm_num)
                if standup_flag:
                    print("standup_flag detected, stopping bgm and voice")
                    pygame.mixer.music.stop()  # 停止背景音乐
                    standup_flag=False
                    break  # 跳出while循环，重新初始化和播放新的背景音乐
                if bgm_num==last_bgm_num:
                    continue
                if bgm_num == 1:
                    bmg_file_name = bmg_file_name_list[2]
                    pygame.mixer.music.load(bmg_file_name)
                    pygame.mixer.music.play(-1)
                    print(f"swtich to bgm {bmg_file_name}")
                if bgm_num == 2:
                    bmg_file_name = bmg_file_name_list[1]
                    pygame.mixer.music.load(bmg_file_name)
                    pygame.mixer.music.play(-1)
                    print(f"swtich to bgm {bmg_file_name}")
                if bgm_num == 3:
                    bmg_file_name = bmg_file_name_list[0]
                    pygame.mixer.music.load(bmg_file_name)
                    pygame.mixer.music.play(-1)
                    print(f"swtich to bgm {bmg_file_name}")
                last_bgm_num=bgm_num

        except pygame.error as e:
            print(f"pygame 初始化失败: {e}")


def playback_thread():
    global nihao_detected, xiaoqi_detected, player2,message_id, output_file_stack, nihao_event, running2,recording,\
        play_haode,audio_file_stack_length,xiaoqi_event,play_haode_event,play_qibaozaina_event,recording_event,\
        shield_after_send,flag_think,resp_message_id,local_output_file_name_list,li_wait_time,standup_flag
  # 清除事件信号
    while running2:
        time.sleep(0.01)
        # if (player2 is not None and player2.poll() is None) or play_haode==True:
        #     # 如果播放器正在运行，等待播放完成
        #     # continue
        # play_haode_event.clear()  # 清除事件信号，准备下一次等待
        # play_haode_event.wait()  # 阻塞直到“好”的播放完成

        if len(output_file_stack) > 0 :
            # 从栈中取出文件
            command1,j1,local_output_file_name = output_file_stack.pop(0)
            print(" command1,j1,local_output_file_name:", command1,j1,local_output_file_name)
            # print(f"***Playing***: {local_output_file_name}")


            # flag_think=False
            print("li_resp_message_id:",resp_message_id)
            print("li_message_id:", message_id)
            if standup_flag:
                print("playback_thread standup_flag:",standup_flag)
                continue
            if  recording_event.is_set() or nihao_detected or xiaoqi_detected or  audio_file_stack_length > 1:
                print("file_name and message_id not match???????????????????????????????????????")
                recording_event.clear()
                continue
            #if resp_message_id != message_id:
                #print("playback_thread resp_message_id!= message_id break!!!!!!!!!!!!!!")
                # continue

            # player2 = subprocess.Popen(
            #     ["aplay", "-D", "hw:0,0", "-f", "S16_LE", "-r", str(sample_rate), "-c", str(channels)],
            #     stdin=subprocess.PIPE
            # )
            # player2 = subprocess.Popen(
            #     ["aplay", "-D", "plughw:3,0", "-f", "S16_LE", "-r", "16000", "-c", "1", local_output_file_name]
            # )
            # player2 = subprocess.Popen(["mpg123", "-o", "alsa:plughw:3,0", local_output_file_name])

            play_queue.put((command1,j1,local_output_file_name))
        else:

            # 如果栈为空，稍微休眠一段时间
            time.sleep(0.005)

    # play_haode_event.clear()
flag_think=False
flag_think2=False
shield_after_send=False
retries=0
retry_interval = 0.3
max_retries=10000
def send_audio_request(audio_data):
    global last_t1,t1,last_t2,t2,flag_error,audio_file_stack_length,paizhao_voice_command,\
        photo_base64,generate_photo_base64,nihao_detected,xiaoqi_detected,result_detected,\
        hello_detected,file_counter,message_id,resp_code_id,\
        conversation_id,output_audio_stack,recording,ws,shield_after_send,flag_think,flag_think2,old_message_id,retries ,max_retries

    global garbage_flag
    # WebSocket 地址


    # 加载音频文件并编码为 base64
    # with open(audio_file_path, "rb") as audio_file:
    #     audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
    audio_data = base64.b64encode(audio_data).decode('utf-8')
        # audio_data = resample_audio1(audio_data, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
    # 构建 JSON 请求
    print("$$$$$$$$$$$$$$$$message_id_send:",message_id)
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
    retries = 0
    max_retries = 10000
    retry_interval = 0.3
    while True:  # 无限重连直到成功
        try:
            if ws is None or not ws.connected:
                print("WebSocket not connected. Attempting to reconnect...")
                ws = websocket.create_connection(websocket_url)
                print("WebSocket reconnected successfully!")
                # remote_host, remote_port = ws.sock.getpeername()
                # print(f"Connected to host: {remote_host}, port: {remote_port}")

            # 发送照片数据
            qibao_sentence_complete = False
            garbage_flag = 2

            ws.send(json.dumps(request))
            # remote_host, remote_port = ws.sock.getpeername()
            # print(f"Connected to host: {remote_host}, port: {remote_port}")
            print("Photo data sent successfully.")
            break  # 成功后退出无限重连循环

        except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
            print(f"WebSocket connection failed: {e}")
            print(f"Retrying5 in {retry_interval} seconds...")
            time.sleep(retry_interval)

        except Exception as e:
            print(f"Unexpected error: {e}")
            print(f"Retrying6 in {retry_interval} seconds...")
            time.sleep(retry_interval)


        # flag_think=True
        # flag_done = False
        # while not flag_done:



        # generate_photo_base64 = False
            # last_t2 = t2
        finally:
            print("we closed!")
            pass





audio_data_queue = queue.Queue()

is_garbage_content=False
old_msg_id = None
cant_connect_flag=False
sleep_mode=False
def receive_audio_request():
    global last_t1, t1, last_t2, t2, flag_error, audio_file_stack_length, paizhao_voice_command, \
        photo_base64, generate_photo_base64, nihao_detected, xiaoqi_detected, result_detected, \
        hello_detected, file_counter, message_id, resp_code_id, \
        conversation_id, output_audio_stack, recording, ws, shield_after_send, flag_think, flag_think2,\
        old_message_id,retries,max_retries,old_msg_id,cant_connect_flag,reconnect_flag,sleep_mode,is_garbage_content

    retry_interval = 0.3
    mes2_id=None
    count_j=0
    while True:
        print("receive_audio_request!")
        current_time_loop = datetime.now()
        print("current time loop：", current_time_loop.strftime("%Y-%m-%d %H:%M:%S"))
        print("print receive_audio_request")

        time.sleep(0.005)

        t1 = time.time()
        # print("@@@@@@SReceive_break_send_audio:", break_send_audio)
        if  nihao_detected or xiaoqi_detected or audio_file_stack_length > 1:
            print("***************************")
            print("***************************")

            print("nihao_detected:", nihao_detected)
            print("xiaoqi_detected:", xiaoqi_detected)
            print("audio_file_stack_length > 1:", audio_file_stack_length > 1)
            print("***************************")
            print("***************************")
            output_audio_stack.clear()
            print("Clear output_file_stack @@SReceive_break_send_audio")

            break_send_audio = False
            nihao_detected = False
            xiaoqi_detected = False
            break
        print("Time_cycle:", t1 - last_t1)
        # 等待响应
        # response = await websocket.recv()
        try:
            try:
                print("reconnect_flag!!:",reconnect_flag)
                if reconnect_flag==True:
                    print("write COMPLETED to play_status.txt")
                    play_queue.queue.clear()
                    output_file_stack.clear()
                    with open("play_status.txt", "w") as file_status:
                        file_status.write(str("COMPLETED"))
                    reconnect_flag=False
                t1=time.time()
                response = ws.recv()
                t2=time.time()
                print("Time_diff2:", t2 - t1)
                # remote_host, remote_port = ws.sock.getpeername()
                # print(f"Connected to host: {remote_host}, port: {remote_port}")
                #print("recv_message_id2:",message_id)
            except (websocket.WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                print(f"Connection failed: {e}")
                retries += 1

                if retries < max_retries:
                    print(f"Waiting for {retry_interval} seconds before retrying...")
                    time.sleep(retry_interval)
                    try:
                        ws = websocket.create_connection(websocket_url)  # 尝试重新连接
                        print("Reconnected to WebSocket.")
                        cant_connect_flag=False
                        print("cant_connect_flag1:", cant_connect_flag)
                        # remote_host, remote_port = ws.sock.getpeername()
                        # print(f"Connected to host: {remote_host}, port: {remote_port}")
                    except Exception as reconnect_error:
                        print(f"Reconnection failed: {reconnect_error}")
                else:
                    print("Max retry attempts reached. Unable to connect to WebSocket.")
                    raise e

            if response is not None:
                cant_connect_flag =False
                print("receive_audio_request.....")
                response_data = json.loads(response)
                if response_data is not None:
                    print("response_data.getcode:",response_data.get("code"))
                    if response_data.get("code")==400:
                        is_garbage_content=True
                        garbage_content_event.set()
                        print("is_garbage_content:",is_garbage_content)

                    else:
                        
                        is_garbage_content=False
                #if response_data is not None:
                    if response_data['method'] == 'voice-chat':
                        resp_message_id = response_data["message_id"]
                        if response_data.get("code") == 0:
                            # sleep_mode=False
                            # print("set sleep_mode False!")
                            # 提取并解码音频数据
                            print("response_data recieived:......")
                            print("response_data time:", time.time())
                            # resp_message_id = response_data["message_id"]
                            if resp_message_id != message_id or recording_event.is_set():  # and resp_message_id != old_message_id:
                                print("resp_message_id!= message_id break2!!!!!!!!!!!!!!")
                                recording_event.clear()
                                continue
                            interrupt_flag = True
                # print("response_data:",response_data)
                #if response_data is not None:
                    if response_data['method'] == 'execute-command':
                        if response_data["data"]["scene_seq"] is not None and response_data["data"]["scene_seq"] > 100:
                            audio_data_queue.queue.clear()
                            print("len(audio_data_queue.queue):", len(audio_data_queue.queue))
                        if response_data.get("code") == 0:
                            sleep_mode=True
                            print("set sleep_mode True!")
                            mes2_id=response_data["message_id"]
                            print("mes2_id:", mes2_id)
                            print("message_id:",message_id)
                            print("old_msg_id:", old_msg_id)
                            if message_id == mes2_id:
                                print("continue audio_data_queue")
                                #continue

                    audio_data_queue.put(response_data)
                    print("len(audio_data_queue.queue)2:", len(audio_data_queue.queue))
                    if mes2_id is not None:
                        print("put queue sucess:", mes2_id)
                    old_msg_id = message_id
                    #response_data = None
        except json.JSONDecodeError as e:
            print(f"JSON 解码错误:{e}")
            # print(f"响应内容:{response}")
            continue
        #######检查响应的状态


        last_t1 = t1  # 重置最后发送心跳请求的时间

from datetime import datetime

resp_message_id=0
fix_counter=0

li_wait_time=0
scent_spray_flag=False
last_scent_spray_flag=False
bgm_num=0
standup_string="站起"
standup_flag=False
seq_queue=queue.Queue()
li_voices_list_len=0
qibao_sentence_complete=True
li_voice=None
li_filename=None
play_enter_sleep_mode=False
has_added_sleep_mode_command=False
old_light_mode = ""
def deal_received_audio_request():
    global last_t1, t1, last_t2, t2, flag_error, audio_file_stack_length, paizhao_voice_command, \
        photo_base64, generate_photo_base64, nihao_detected, xiaoqi_detected, result_detected, \
        hello_detected, file_counter, message_id, resp_code_id, \
        conversation_id, output_audio_stack, recording, ws, shield_after_send, flag_think, flag_think2, \
        old_message_id,resp_message_id,xiaoqi_event,recording_event,continue_shot_and_record,output_file_stack,fix_counter\
        ,li_wait_time,scent_spray_flag,bgm_num,standup_flag,li_voices_list_len,li_scene_seq,\
        qibao_sentence_complete,li_voice,interrupt_flag,cant_connect_flag,li_filename,sleep_mode,play_enter_sleep_mode,has_added_sleep_mode_command

    global add_once_list_flag_with_sleep
    li_voices_list=[]

    while True:
        print("deal_received_audio_request!")
        time.sleep(0.003)
        print("audio_data_queue:",audio_data_queue)
        try:
            response_data = audio_data_queue.get()
            print("wait response_data")
        except queue.Empty:
            print("audio_data_queue is empty, continue...")

        if response_data is not None:
            if response_data['method'] == 'execute-command':
                # print("response_data_from_execute-command:", response_data)
                print("response_data_conversation_id:",response_data['conversation_id'])
                print("cant_connect_flag3:",cant_connect_flag)
                if cant_connect_flag == True:
                    print("!!!!!!!!!!!!!!!!!")
                    print("local broadcast!!!!!!")
                    print("!!!!!!!!!!!!!!!!!")



                elif cant_connect_flag == False:
                    if response_data.get("code") == 0:
                        print("mes_id:",response_data["message_id"])

                        li_action_feature=response_data["data"]["actions"]["action_feature"]
                        print("li_action_feature:", li_action_feature)
                        # if standup_string in li_action_feature:
                        #     print("standup_string:",standup_string)
                        #     standup_flag=True

                        li_bgm = response_data["data"]["actions"]["bgm"]
                        print("li_bgm:", li_bgm)
                        if li_bgm is not None:
                            li_bgm_audio_data=li_bgm["audio_data"]
                            print("li_bgm_audio_data:",li_bgm_audio_data)
                            li_bgm_audio_format = li_bgm["audio_format"]
                            print("li_bgm_audio_format:", li_bgm_audio_format)
                            li_bgm_filename = li_bgm["filename"]
                            print("li_bgm_filename:", li_bgm_filename)
                            if li_bgm_filename is not None:
                                if "bo_1036" in li_bgm_filename:
                                    print("enter bgm_num 1")
                                    bgm_num=1
                                if "bo_asmr" in li_bgm_filename:
                                    print("enter bgm_num 2")
                                    bgm_num = 2

                        li_scene=response_data["data"]["scene"]
                        print("li_scene:", li_scene)
                        li_scene_seq = response_data["data"]["scene_seq"]
                        print("***************************************")
                        print("***************************************")

                        print("li_scene_seq:", li_scene_seq)
                        now2 = datetime.now()
                        print(now2.strftime("%Y-%m-%d %H:%M:%S"))
                        print("***************************************")
                        print("***************************************")

                        with open("li_scene_seq.txt", "r") as file_scene:
                            content = file_scene.read().strip()  # 读取并去除空白字符
                            if content == 'None' or content == '':
                                print("content is empty or None")
                                old_seq = None  # 如果文件为空，可以设置默认值，或者根据需求处理
                            else:  # 如果文件内容不是空的clea
                                old_seq = int(content)  # 转换为整数
                                print("old_seq:", old_seq)
                        print("interrupt_flag:",interrupt_flag)
                        print("li_scene_seq==old_seq:",li_scene_seq==old_seq)
                        print("li_scene_seq > old_seq:",li_scene_seq > old_seq)
                        print("qibao_sentence_complete_2:", qibao_sentence_complete)
                        if li_scene_seq is not None:
                            print("old_seq<100 and (li_scene_seq > old_seq or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq)) and qibao_sentence_complete:",old_seq<100 and (li_scene_seq > old_seq or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq and qibao_sentence_complete)))
                            print("(old_seq>100 and li_scene_seq!=old_seq) or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq and qibao_sentence_complete):",(old_seq>100 and li_scene_seq!=old_seq and qibao_sentence_complete) or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq and qibao_sentence_complete))

                            if (old_seq<100 and (li_scene_seq > old_seq or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq)) and qibao_sentence_complete) or ((old_seq>100 and li_scene_seq!=old_seq and qibao_sentence_complete) or (add_once_list_flag_with_sleep==True and li_scene_seq==old_seq and qibao_sentence_complete)):
                                with open("li_scene_seq.txt", "w") as file_scene:
                                    file_scene.write(str(li_scene_seq))  # 将li_scene_seq写入文件，确保是数字序号的字符串格式
                            # if 1 >= 0:
                                print("yes")
                                add_once_list_flag_with_sleep = False

                                if li_scene_seq>100:
                                    print("queue.clear", li_scene_seq)
                                    play_queue.queue.clear()
                                    print("clear play_queue")
                                    output_file_stack.clear()
                                    print("clear output_file_stack")
                                li_voice = response_data["data"]["actions"]["voice"]
                                if li_voice is not None:
                                    # print("li_voice:", li_voice)

                                    li_voices_list=li_voice["voices"]
                                    # print("li_voices_list:",li_voices_list)
                                    print("len(li_voices_list):",len(li_voices_list))
                                    # if li_audio_base64 != None:
                                    #     audio_data_list = [voice["audio_data"] for voice in response_data["voices"]]
                                    #     audio_text_list = [voice["text"] for voice in response_data["voices"]]
                                    #     for text_i in audio_text_list:
                                    #         print("text_i:", text_i)
                                    #
                                    #     for audio_data_i in audio_data_list:
                                    #         print("audio_data_i:", audio_data_i)
                                    #         audio_bytes = base64.b64decode(audio_data_i)
                                    #         # audio_text = li_voice["text"]
                                    #         # print("audio_text:", audio_text)
                                    #         if str(li_voice["audio_format"]) =='mp3':
                                    #             fixed_audio_file_name = f"/home/li/vosk-api/python/example/fix_audio/fixed_{fix_counter}.mp3"
                                    #             with open(fixed_audio_file_name, "wb") as mp3_file:
                                    #                 mp3_file.write(audio_bytes)
                                    #             print("Saved_fix:", fixed_audio_file_name)
                                    #             # time.sleep(1)
                                    #             output_file_stack.append(fixed_audio_file_name)
                                    #             fix_counter+=1
                                    li_voices_list_len=len(li_voices_list)
                                    print("li_voices_list_len:",li_voices_list_len)
                                    for i in range (li_voices_list_len):
                                        print("i:", i)
                                        # li_audio_base64 = li_voices_list[i]["audio_data"]
                                        li_audio_fomat = li_voices_list[i]["audio_format"]
                                        print("li_audio_fomat:", li_audio_fomat)
                                        # if li_audio_base64 != None:
                                        li_action = li_voices_list[i]["action"]
                                        print("li_action:", li_action)
                                        li_wait_time = li_voices_list[i]["wait_time"]
                                        print("li_wait_time:", li_wait_time)
                                        if li_wait_time is None:
                                            li_wait_time = 1
                                        # li_audio_base64_len = len(li_voices_list[i]["audio_data"])
                                        # print("li_audio_base64_len:", li_audio_base64_len)
                                        # audio_bytes = base64.b64decode(li_audio_base64)
                                        li_audio_text = li_voices_list[i]["text"]
                                        print("li_audio_text:", li_audio_text)
                                        # if str(li_audio_fomat) == 'mp3':
                                        #     fixed_audio_file_name = f"/home/li/vosk-api/python/example/fix_audio/fixed_{i}.mp3"
                                        #     with open(fixed_audio_file_name, "wb") as mp3_file:
                                        #         mp3_file.write(audio_bytes)
                                        #     print("Saved_fix:", fixed_audio_file_name)
                                            # time.sleep(li_wait_time)
                                            # time.sleep(5)
                                        li_filename = li_voices_list[i]["filename"]
                                        print("li_filename:", li_filename, "appended!")



                                        output_file_stack.append(("execute-command",i,"/home/li/vosk-api/python/example/sound/"+str(li_filename)))

                                        print("!!!output_file_stack:",output_file_stack)
                                        output_file_stack_length = len(output_file_stack)
                                        print("播放栈len:", output_file_stack_length)
                                interrupt_flag = False
                                # qibao_sentence_complete=False
                        # if qibao_sentence_complete==True:
                        #     print("replay unfinished sentence!")
                        #     if li_voice is not None:
                        #         li_voices_list = li_voice["voices"]
                        #         li_voices_list_len = len(li_voices_list)
                        #         print("li_voices_list_len:", li_voices_list_len)
                        #
                        #         for i in range(li_voices_list_len):
                        #             fixed_audio_file_name = f"/home/li/vosk-api/python/example/fix_audio/fixed_{i}.mp3"
                        #             print("append fixed_audio_file_name:",fixed_audio_file_name)
                        #             output_file_stack.append(("execute-command", i, fixed_audio_file_name))
                        #         qibao_sentence_complete =False
                        else:
                            print("i_scene_seq!=last_li_scene_seq+1!!")

                        light = response_data["data"]["actions"]["light"]
                        print("light:", light)
                        if light is not None:
                            light_rgb = light["rgb"]

                            print("light_rgb:", light_rgb)
                            if light_rgb is not None:
                                r, g, b = map(int, light_rgb.split(','))

                                print("r, g, b:",r,g,b)
                            light_mode = light["mode"]
                            print("light_mode:", light_mode)
                            if light_mode is not None:
                                if old_light_mode != light_mode:
                                    if str(light_mode) == "Off":
                                        print("Off!!!")
                                        turn_off()
                                        # time.sleep(2)
                                    if str(light_mode) == "Shadowing":
                                        print("Shadowing!!!")
                                        turn_off()
                                        time.sleep(0.1)
                                        # theaterChaseRainbow(strip, wait_ms=50)
                                        theaterChaseRainbow_thread=threading.Thread(target=theaterChaseRainbow,args=(strip,50))
                                        theaterChaseRainbow_thread.start()
                                        # time.sleep(1)
                                    if str(light_mode) == "Breathing":
                                        print("Breathing!!!")
                                        turn_off()
                                        time.sleep(0.1)
                                        # wheel(100)
                                        wheel_thread = threading.Thread(target=wheel, args=(100,))
                                        wheel_thread.start()
                                        # time.sleep(1)
                                    if str(light_mode) == "Gradient":
                                        print("Gradient!!!")
                                        turn_off()
                                        time.sleep(0.1)
                                        # colorWipe_single(strip,  color=Color(0, 255, 0),wait_ms=50)
                                        colorWipe_single_thread = threading.Thread(target=breath, args(r, g, b))
                                        colorWipe_single_thread.start()
                                        # time.sleep(1)
                                    if str(light_mode) == "Static":
                                        print("Static!!!")
                                        turn_off()
                                        time.sleep(0.1)
                                        # rainbow(strip, wait_ms=30)
                                        rainbow_thread = threading.Thread(target=const_color,args=(r, g, b,))
                                        rainbow_thread.start()
                                        # time.sleep(1)
                                    old_light_mode = light_mode

                        fragrance = response_data["data"]["actions"]["fragrance"]
                        print("fragrance:",fragrance)
                        if fragrance is not None:
                            fragrance_status = fragrance["status"]
                            fragrance_level = fragrance["level"]
                            fragrance_count = fragrance["count"]
                            print("fragrance_status:", fragrance_status)
                            if fragrance_status is not None:
                                if fragrance_status=="on":
                                    scent_spray_flag=True
                                if fragrance_status == "off":
                                    scent_spray_flag = False
                            if fragrance_level is not None:
                                print("fragrance_level:", fragrance_level)
                            if fragrance_count is not None:
                                print("fragrance_count:", fragrance_count)

            if response_data['method'] == 'voice-chat':
                if is_garbage_content==False:
                    if response_data['data']['text'] is not None and response_data["data"]["stream_seq"] is not None and response_data["data"]["stream_seq"] == 1 :
                        print("garbage")
                        response_text = response_data['message_id']
                        print("gar response_text:", response_text)
                        play_queue.queue.clear()
                        print("clear play_queue")
                        output_file_stack.clear()
                        print("clear output_file_stack")
                        #interrupt_flag = False
                        qibao_sentence_complete = False

                if response_data.get("code") == 0:
                    seq_li = response_data["data"]["stream_seq"]
                    print("seq_li:", seq_li)
                    if seq_li == -1:
                        #qibao_sentence_complete = True
                        #print("qibao_sentence_complete:", qibao_sentence_complete)
                        print("sleep_mode:",sleep_mode)
                        if sleep_mode==True:
                            time.sleep(10)
                            output_file_stack.append(
                                ("execute-command", 1, f"/home/li/vosk-api/python/example/lahuisixu2.mp3"))
                            time.sleep(3)
                        sleep_mode = False

                        # play_qibaozaine_function()
                        # with open("li_scene_seq.txt", "r") as file_scene:
                        #     content = file_scene.read().strip()  # 读取并去除空白字符
                        #     if content == 'None' or content == '':
                        #         print("content is empty or None")
                        #         old_seq= None  # 如果文件为空，可以设置默认值，或者根据需求处理
                        #     else:  # 如果文件内容不是空的
                        #         old_seq = int(content)  # 转换为整数
                        #         print("old_seq2:",old_seq)
                        #
                        # with open("li_scene_seq.txt", "w") as file_scene:
                        #     file_scene.write(str(old_seq))  # 将li_scene_seq写入文件，确保是数字序号的字符串格式
                        with open("play_status.txt", "w") as file_status:
                            file_status.write(str("IN_PROGRESS"))
                        # qibao_sentence_complete = False
                    #else:
                        #qibao_sentence_complete = False
                    # 提取并解码音频数据
                    print("response_data recieived:voice-chat")
                    print("response_data time:",time.time())
                    resp_message_id = response_data["message_id"]

                    resp_code_id = response_data["code"]
                    print("********")
                    print("********")
                    print("message_id_get_from_Json:", message_id)
                    print("!!!!!!!!!!!!!Get_resp_message_time:", time.time())
                    print("!!!!!!!!!!!!!!resp_message_id:", resp_message_id)

                    print("!resp_code_id:", resp_code_id, ":", type(resp_code_id))
                    print("old_message_id:", old_message_id)
                    # if resp_message_id != message_id and int(resp_code_id) == 0:
                    # if resp_message_id != old_message_id and int(resp_code_id) == 0:

                    #     print("resp_conversation_id not match !!!!!!!!!!!!!!!!!!!!!???????????????????")
                        # break

                    resp_fomat = response_data["data"]["audio_format"]
                    print("resp_fomat:", resp_fomat)
                    audio_base64 = response_data["data"]["audio_data"]
                    # print("audio_base64:", audio_base64)

                    response_action = response_data["data"]["action"]
                    print("response_action:", response_action)
                    if response_action == "take_photo":
                        print("web ask to take photo.")
                        paizhao_voice_command = True

                    elif response_action == "sleep_assistant":
                        print("sleep_assistant")
                        response_text = response_data['message_id']
                        print("sleep_assistant response_text:", response_text)
                        play_queue.queue.clear()
                        print("sleep_assistant clear play_queue")
                        output_file_stack.clear()
                        print("sleep_assistant clear output_file_stack")
                        #interrupt_flag = False

                        print("web ask to sleep assistant.")
                        continue_shot_and_record = True
                        play_enter_sleep_mode=True
                        if play_enter_sleep_mode and not has_added_sleep_mode_command:
                            output_file_stack.append(
                                ("execute-command", 1, f"/home/li/vosk-api/python/example/enter_sleep_mode.mp3"))
                            has_added_sleep_mode_command = True
                        play_enter_sleep_mode = False
                        # pygame.mixer.music.load("/home/li/vosk-api/python/example/enter_sleep_mode.mp3")
                        # # 播放音频
                        # pygame.mixer.music.play()
                        # print("playing enter_sleep_mode.mp3")
                        # # 等待音频播放完成
                        # while pygame.mixer.music.get_busy():
                        #     pygame.time.Clock().tick(10)

                    if audio_base64 != None:
                        audio_bytes = base64.b64decode(audio_base64)

                        # seq_li = response_data["data"]["stream_seq"]
                        # print("seq_li:", seq_li)

                        response_action = response_data["data"]["action"]
                        print("response_action:", response_action)


                        response_text = response_data["data"]["text"]
                        print("response_text:", response_text)
                        # if audio_file_stack_length>1:
                        #     print("audio_file_stack_length>1 break!!!!!!!!!!!!!!")
                        #     output_audio_stack.clear()
                        #     break
                        # if resp_message_id != message_id:

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
                        flag_think2 = False
                        if str(resp_fomat) == 'mp3':
                            if resp_message_id != message_id or recording_event.is_set():  # and resp_message_id != old_message_id:
                                print("resp_message_id!= message_id break1!!!!!!!!!!!!!!")

                                recording_event.clear()
                                continue

                            if nihao_detected or xiaoqi_detected or audio_file_stack_length > 1:
                                continue



                            output_file_name = f"/home/li/vosk-api/python/example/send_pcm_folder/2input{file_counter}.mp3"
                            with open(output_file_name, "wb") as pcm_file:
                                pcm_file.write(audio_bytes)
                            print("Saved:", output_file_name)
                            output_file_stack.append(("voice-chat",seq_li,output_file_name))
                            output_file_stack_length = len(output_file_stack)
                            print("播放栈len:", output_file_stack_length)



                        else:
                            print("no mp3")

            interrupt_flag = False





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
# from webrtc_audio_processing import AudioProcessingModule as AP
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

audio_memory = None


def callback(indata, frames, time1, status):
    """每次接收音频数据时调用"""
    global t_play_haode,output_file_name, recording, silence_counter, output_pcm_file, pre_buffer, audio_file_stack, \
        noise_break_flag, silent_start_time, silent_end_time, pop_swtich, message_id, start_record_time,play_haode,\
        is_silent_flag,recording_event,flag_think,old_message_id,last_message_id,not_send_flag,play_qibaozaina,audio_memory
    denoise_output_file_name = f"/home/li/vosk-api/python/example/send_pcm_folder/denoise_output{message_id}.pcm"
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
            flag_think=True
            noise_break_flag = True
            silence_counter = 0  # 重置静音计数器

            if not recording:
                print("@@@@@@@@@@@@开始录音......")
                recording = True
                print("audio_data_queue_size:", audio_data_queue.qsize())
                while not audio_data_queue.empty():
                    audio_data_queue.get()
                recording_event.set()
                start_record_time = current_time  # 记录录音开始时间

                message_id_orin = get_message_id()
                message_id = message_id_orin
                print("message_id_born:", message_id)
                print("last_message_id:", last_message_id)
                old_message_id=last_message_id
                print("old_message_id:", old_message_id)
                # output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/output{message_id}.pcm"
                #
                # print("output_file_name:", output_file_name)
                # output_pcm_file = open(output_file_name, "wb")
                audio_memory = io.BytesIO()
                # 写入预缓冲中的静音帧，仅在录音开始时
                for frame in pre_buffer:
                    audio_memory.write(frame.tobytes())
                pre_buffer.clear()

            # 写入当前音频帧
            audio_memory.write(indata.tobytes())

            # 如果录音时间超过4秒，立即停止录音
            if current_time - start_record_time > 6:
                print("@@@@@@@@@@@@录音时间超过4秒，停止录音")
                recording = False
                audio_data = audio_memory.getvalue()  # 获取内存中的音频数据
                audio_memory.close()  # 关闭内存流
                audio_memory = None
                # output_pcm_file.close()
                # process_audio(output_file_name, denoise_output_file_name)

                if pop_swtich and audio_data is not None:

                    if not_send_flag==False:
                        # play_qibaozaina=True
                        audio_file_stack.append(audio_data)
                    else:
                        play_haode = True

                    # flag_think = False
                    recording_event.clear()
                    # print("append_output_file_name:", output_file_name)
                    # print("append audio_file_stack:", audio_file_stack)
                # output_pcm_file = None

        else:  # 静音帧
            if recording:
                # 写入当前静音帧
                audio_memory.write(indata.tobytes())
                silence_counter += 1

                # 如果静音超过指定时间或总录音时长超过4秒，立即停止录音
                if current_time - start_record_time > 1.0 and silence_counter >= 2:
                    print("@@@@@@@@@@@@检测到静音，停止录音")
                    recording = False
                    audio_data = audio_memory.getvalue()  # 获取内存中的音频数据
                    audio_memory.close()  # 关闭内存流
                    audio_memory = None
                    # output_pcm_file.close()
                    # process_audio(output_file_name, denoise_output_file_name)
                    if pop_swtich and audio_data  is not None:
                        play_haode=True
                        t_play_haode=time.time()
                        # print("!!!!!!!!!!!!!!!Send_play_haode:", play_haode)
                        if not_send_flag == False:
                            # play_qibaozaina = True
                            audio_file_stack.append(audio_data)
                        else:
                            play_haode = True
                        last_message_id = message_id
                        # flag_think = False
                        recording_event.clear()
                        # print("append_output_file_name:", output_file_name)
                        # print("append audio_file_stack:", audio_file_stack)
                    # output_pcm_file = None
            else:
                # 保存静音帧到预缓冲中，仅在未录音时
                pre_buffer.append(indata.copy())


def callback2(indata, frames, time1, status):
    """每次接收音频数据时调用"""
    global recording2, start_record_time2, audio_memory2, message_id2

    if status:
        print(status, file=sys.stderr)

    # 如果未开始录音，则初始化录音
    if not recording2:
        print("@@@@@@@@@@@@ 开始录音2 ......")
        recording2 = True
        start_record_time2 = time.time()  # 记录开始录音的时间
        message_id2 = get_message_id()  # 获取唯一的消息 ID
        print(f"message_id_born: {message_id2}")

        # 初始化音频存储
        audio_memory2 = io.BytesIO()

    # 将当前帧写入音频内存
    audio_memory2.write(indata.tobytes())

    # 如果录音时间达到 3 秒，结束录音并保存文件
    if time.time() - start_record_time2 >= 3:
        print("@@@@@@@@@@@@ 录音时间达到 3 秒，停止录音2")
        recording2 = False
        audio_data = audio_memory2.getvalue()  # 获取音频数据
        audio_memory2.close()  # 关闭内存流

        # 保存到 WAV 文件
        output_file_name = f"/home/li/vosk-api/python/example/shot_and_recording/audio_{message_id2}.wav"
        with wave.open(output_file_name, 'wb') as wav_file:
            # 设置 WAV 文件参数
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16 位深度 (2 字节)
            wav_file.setframerate(16000)  # 采样率为 16kHz
            wav_file.writeframes(audio_data)

        print(f"音频文件已保存到: {output_file_name}")

        # 清空音频内存
        audio_memory2 = None

    # 如果未录音，准备下一次录音
    if not recording2 and time.time() - start_record_time2 >= 3:
        recording2 = True
        start_record_time2 = time.time()


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
model_path = "/home/li/vosk-model-small-cn-0.22"
text_stack = []
# 定义文件路径
file_path = "/home/li/saved_text.txt"
shared_variable_path = "/home/li/shared_variable.txt"
shared_stop_variable_path = "/home/li/shared_stop_variable.txt"


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
# device_name = "UM10"  # 根据实际设备名称进行设置
# device_name="POROSVOC UAC Dongle"
device_name="Yundea 1076"
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


def find_file_index(sleep_voice_list, li_filename):
    # 遍历 sleep_voice_list 中的每个列表
    for p, voice_list in enumerate(sleep_voice_list):
        # 遍历每个列表中的文件名
        for q, filename in enumerate(voice_list):
            if filename == li_filename:
                return p, q  # 返回对应的 p 和 q 序号
    return None  # 如果没有找到，返回 None


def add_files_to_stack(sleep_voice_list, p, q):
    """从 sleep_voice_list[p][q] 开始，遍历并将后续文件添加到 output_file_stack"""
    # 遍历从 p 开始的子列表
    for i in range(p, len(sleep_voice_list)):  # 遍历从 p 开始的所有子列表
        time.sleep(2)
        # 如果是在当前子列表 (i == p)，从 q + 1 开始到该子列表的末尾
        if i == p:
            for current_q in range(q + 1, len(sleep_voice_list[i])):  # 从 q + 1 开始
                file_name = sleep_voice_list[i][current_q]
                output_file_stack.append(("execute-command", i, f"/home/li/vosk-api/python/example/sound/{file_name}"))
                print(f"Added {file_name} to output_file_stack")
        else:
            # 否则，遍历下一个子列表 (i > p)，从第一个文件开始
            for current_q in range(len(sleep_voice_list[i])):
                file_name = sleep_voice_list[i][current_q]
                output_file_stack.append(("execute-command", i, f"/home/li/vosk-api/python/example/sound/{file_name}"))
                print(f"Added {file_name} to output_file_stack")

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
    # callback2(indata, frames, time1, status)
    # 调用本地 Kaldi 处理的处理函数
    callback10(indata, frames, time1, status)

garbage_flag=0
def process_interupt():
    global garbage_flag, is_garbage_content
    print("Waiting for garbage content event to be set...")
    # 等待事件被触发
    while 1:
        time.sleep(0.05)
        garbage_content_event.wait()  # 等待事件被触发
        print("garbage_content receive")  # 事件触发后打印
        is_garbage_content = True
        garbage_flag=1

thread_process_interupt = threading.Thread(target=process_interupt)
thread_process_interupt.start()
def send_heartbeat():
    global last_t1,t1,last_t2,t2,running2,ws,retries,max_retries
    # try:

    retry_interval = 0.3
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
        while True:  #
            try:
                if ws is None or not ws.connected:
                    print("WebSocket not connected. Attempting to reconnect...")
                    ws = websocket.create_connection(websocket_url)
                    # remote_host, remote_port = ws.sock.getpeername()
                    # print(f"Connected to host: {remote_host}, port: {remote_port}")
                    print("WebSocket reconnected successfully!")
                ws.send(json.dumps(request_heartbeat))
                break
            except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                print(f"WebSocket connection failed: {e}")
                print(f"Retrying7 in {retry_interval} seconds...")
                time.sleep(retry_interval)

            except Exception as e:
                print(f"Unexpected error: {e}")
                print(f"Retrying8 in {retry_interval} seconds...")
                time.sleep(retry_interval)
        # print("heartbeat sent")
        time.sleep(1)
    # finally:
    #     ws.close()

def audio_run():
    global flag_append, audio_file_stack, flag_len, running2, data_id_no_send, generate_photo_base64, shield_after_send, flag_think, flag_think2
    print("audio_run")
    audio_file_stack.clear()
    time.sleep(0.005)  # 保证事件循环可以调度其他任务
    if running2:
        audio_thread_control_event.wait()
        thread_control_event.wait()
        # audio_file_stack.append("/home/orangepi/vosk-api/python/example/output_li.pcm")
        # time.sleep(0.01)
    # time.sleep(0.1)
    con_num=0
    while running2:
        con_num+=1
        # print("flag_think:",flag_think)
        # print("network audio_run!!!")
        audio_thread_control_event.wait()
        thread_control_event.wait()
        flag_len = len(audio_file_stack)
        # print("!!!!!!!!!!!!!!!len(audio_file_stack):",len(audio_file_stack))
        time.sleep(0.005)  # 确保事件循环可以调度其他任务
        # print("Entering while循环")
        # print("发送栈length:", flag_len)
        # if conversion_success==True:
        #     send_audio_request(audio_file_path)
        # if generate_photo_base64:
        #     send_audio_request(audio_file_path)
        if flag_len > 0:
            while len(audio_file_stack) > 1:
                audio_file_stack.pop(0)
            audio_data = audio_file_stack.pop(-1)  # 弹出最老的文件
            flag_think = False
            flag_think2 = True
            # print(f"audio file: {audio_file_path}")
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
            # audio_file_path = os.path.join("/home/orangepi/vosk-api/python/example", audio_file_path)
            # print(f"audio file_full: {audio_file_path}")

            print("send_audio_request")
            send_audio_request(audio_data)

            # run_async(send_audio_request, audio_file_path)
            # success =send_audio_request(audio_file_path)
            # print(f"Send status: {success}")
            # if not success:
            #     # 如果发送失败，继续尝试下一个文件
            #     print("Failed to send audio, retrying with next file.")
            #     continue
        # else:
        #     print("No more audio files to send.")
        #     print("No more audio files to send.")
            # break  # 如果栈空则退出
    print("break from audio_run!")

def stop_threads():
    print("Threads stopped.")

    thread_control_event.clear()  # 停止子线程的执行
log_file_path = "/home/li/vosk-api/python/example/servo_pulse_log.txt"
def start_threads():
    global threads_started,running,audio_file_stack,running2,start_threads_control,start_video_playback_flag,conversation_id
    # 确保线程只启动一次
    print("enter start_threads")

    pulse_once = True
    conversation_id = get_conversation_id()
    print("generate_conversation_id:", conversation_id)
    while running2:
        start_threads_control.wait()
        print("enter start_threads")

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
        # record_2s_thread=threading.Thread(target=record_2s)
        # record_2s_thread.start()
        combine_bgm_sound_thread=threading.Thread(target=combine_bgm_sound)
        combine_bgm_sound_thread.start()
        continue_send_photo_thread = threading.Thread(target=continue_send_photo)
        continue_send_photo_thread.daemon = True  # 设置为守护线程，这样程序退出时线程会自动退出
        continue_send_photo_thread.start()

        LED_thread=threading.Thread(target=breath)
        LED_thread.start()
        scent_spray_thread=threading.Thread(target=scent_spray)
        scent_spray_thread.start()
        face_detection_run_thread=threading.Thread(target=face_detection_run1)
        heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        audio_processing_thread = threading.Thread(target=audio_run)
        # logic_thread = threading.Thread(target=animation_logic)
        receive_audio_request_thread=threading.Thread(target=receive_audio_request)
        receive_audio_request_thread.start()
        # receive_audio_request2_thread=threading.Thread(target=receive_audio_request2)
        # receive_audio_request2_thread.start()
        deal_received_audio_request_thread=threading.Thread(target=deal_received_audio_request)
        deal_received_audio_request_thread.start()

        # playhaode_thread_instance = threading.Thread(target=play_haode_function, daemon=True)
        # playhaode_thread_instance.start()
        # play_qibaozaine_thread_instance = threading.Thread(target=play_qibaozaine_function, daemon=True)
        # play_qibaozaine_thread_instance.start()
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
        face_detection_switch,xiaoqi_detected_count,sleep_detected,standup_flag
    pulse_within_range = False
    while running:
        time.sleep(0.02)
        if recording:
            silent_start_time = time.time()  # 重置计时
            # print("计时重置为 0")
            time.sleep(0.02)  # 避免连续触发

        elapsed_time = time.time() - silent_start_time
        current_step = 2
        # if standup_flag==True:
        if elapsed_time > 1800 and elapsed_time < 1000000 or sleep_detected:  # 超过25秒静音
            print("超过25秒静音，停止线程")
            sleep_detected=False
            pop_swtich = False
            draw_switch = False
            face_detection_switch = False
            stop_threads()  # 停止语音线程
            xiaoqi_detected_count = 0
            time.sleep(0.5)
        else:
            thread_control_event.set()  # 保持事件激活状态，允许线程运行


def kaldi_run2():
    global xiaoqi_detected,silent_start_time,pop_swtich,draw_switch,face_detection_switch,xiaoqi_detected_count,not_send_flag,play_qibaozaina

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
                play_qibaozaina = True
                # not_send_flag = True
                thread_control_event.set()
                start_threads_control.set()  # 启动 start_threads 线程
            elif xiaoqi_detected_count >= 2:
                play_qibaozaina = True
                # not_send_flag = False
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


target_keywords = ["播放音乐", "七七", "停止", "抬头","拍照","休息"]
def detect_keywords(transcription):
    """从转录文本中检测关键词"""

    for word in target_keywords:
        if word in transcription:
            print(f"Keyword detected: {word}")

keywords = '["播放音乐", "七七", "停止", "抬头", "拍照","休息","[unk]"]'##########关键词必须完全一样才行


def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

SPK_MODEL_PATH = "/home/li/vosk-api/python/example/vosk-model-spk-0.4"
model_path = "/home/li/vosk-model-small-cn-0.22"
# spk_li_1=[-0.297443, 0.138541, -0.480268, -0.20816, -0.181298, -0.639442, 0.21267, -0.555786, 1.005074, 0.011552, 1.985099, -0.568444, 0.520695, 0.221619, -0.442219, -0.352981, 1.291161, 0.58134, 1.671874, -1.298758, -0.395653, -0.401662, 2.137376, 0.174206, 0.570289, 0.01595, 1.390286, -0.475607, 1.212984, -0.195779, -0.038047, -0.18157, -0.598267, -0.97167, -0.560137, -0.021336, -1.152562, 0.948739, 0.765162, -0.550215, -1.161016, 1.401901, 0.383774, -0.220877, -0.638535, 1.118744, -0.51617, 0.952701, 0.540488, 0.459646, 0.337441, 1.287117, -1.81413, 0.807996, 0.418737, -1.263778, 0.068068, -1.384879, -1.70511, 1.647274, -0.842112, 0.111097, -0.736788, -2.329749, -2.008974, -1.564938, -0.335628, 0.184886, 0.943496, 0.770639, 1.692765, 0.082376, -1.156951, 0.097683, -1.031321, 1.875823, -1.600061, -1.14648, 0.628454, -0.386903, 1.692657, 0.846197, -0.966381, 1.106492, -0.734312, 0.077541, 0.689925, 0.817806, 0.971107, -0.693128, 0.986192, -0.015493, -1.595232, 0.250718, 0.381887, -0.662012, -0.158801, -0.679696, -0.487889, 2.454968, -1.054998, -1.543859, 0.815683, 1.125827, -0.15894, 1.941532, -0.684257, 0.595867, -0.239138, -1.711226, -0.669706, 1.655171, -1.010642, -0.764074, 1.118967, -1.066784, -1.645003, 0.38828, 0.085089, 0.470405, 0.969876, 0.572148, 0.61563, 0.815989, -0.234343, 2.112524, -0.769253, 0.585631]
spk_li_1=[-0.626114, 0.430365, 0.564255, -0.182698, 0.537145, 0.044097, 0.564515, 0.666896, 1.085733, -0.523695, 2.178851, -0.545808, 0.492513, -0.214256, 0.380257, 0.561458, 1.432191, 0.576447, 1.347584, -1.410213, -0.201343, 1.299883, 0.16591, -0.301386, 1.030398, -0.155679, 1.668122, -0.47749, 1.583658, 1.031789, -0.610194, 0.207826, -2.028657, -0.778005, 0.608732, -1.103482, -0.249394, -0.145279, -0.252108, -0.744611, -0.178013, 0.821876, 1.348644, 0.958709, -1.489057, -0.069446, 0.55689, 0.382191, 1.793885, 0.12014, 1.096465, 1.948748, -0.288994, -0.427686, -0.25332, -0.74351, 1.289284, -0.442085, -1.594271, 0.238896, -0.14475, -1.243948, -0.811971, -1.167681, -1.934597, -2.094246, 0.203778, 0.2246, 0.769156, 3.129627, 1.638138, -0.414724, 0.363555, 1.058113, -0.658691, 0.345854, -1.559133, 0.087666, 0.984442, -0.469354, 1.667347, 0.916898, -2.170697, 0.292812, 0.051197, 1.222564, 1.065773, -0.065279, 0.214764, -0.407425, 0.992222, -0.993893, 0.693716, 0.121084, 1.31698, 1.255295, -0.941613, 0.015467, 0.500375, -1.479744, -0.943895, -0.405701, 1.795941, -0.66203, 1.224589, 0.963079, -0.872087, 0.392804, 1.412374, -0.279257, -0.462107, 0.674435, 0.137653, 0.93439, 2.394885, -0.571315, 0.374555, -0.233448, 0.757664, -0.375494, 0.666074, -0.123803, 1.518769, 0.873773, -0.218161, 1.566089, -0.488127, 0.386693]
model = Model(model_path)
spk_model = SpkModel(SPK_MODEL_PATH)
not_send_flag=False
def kaldi_listener():
    global count2, silent_start_time, silent_end_time, xiaoqi_detected, running2, running,paizhao_voice_command,\
        message_id_get,data_id_no_send,nihao_detected,result_detected,hello_detected,keywords,sleep_detected,\
        nihao_event,is_silent_flag,xiaoqi_event,continue_shot_and_record
    args.samplerate = SAMPLERATE_ORIG

    rec = KaldiRecognizer(model, SAMPLERATE_ORIG, keywords)
    rec.SetSpkModel(spk_model)
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
        xiaoqi_event_triggered = False  # 初始标志
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
            xiaoqi_event_triggered = False
            if is_silent(data):
                # print("检测到静音，跳过此段音频")
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
                # if "spk" in result:
                #     spk_vector = result["spk"]
                #     print("spk_vector:", spk_vector)
                #     print("len(spk_vector):", len(spk_vector))
                #     # print("len(spk_sig):", len(spk_sig))
                #
                #     distance1 = cosine_dist(spk_li_1, spk_vector)
                #     print(f"Speaker distance1: {distance1}")
                #     if distance1>0.5:
                #         print("speaker distance larger than 0.5!!!!!!!!")
                #         continue
                #     # distance2 = cosine_dist(spk_li_2, spk_vector)
                #     # print(f"Speaker distance2: {distance2}")
                if target_keywords[1] in str(transcription) and not xiaoqi_event_triggered:
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")
                    xiaoqi_event.set()
                    xiaoqi_detected = True
                    xiaoqi_event_triggered = True

                    continue
                else:
                    # print("未检测到qibao关键词，xiaoqi_event.clear")
                    xiaoqi_event.clear()

                    # continue
                # if target_keywords[5] in str(transcription):
                #     print(f"检测到sleep关键词: {target_keywords[5]}")
                #     continue_shot_and_record=True
                #     print("continue_shot_and_record0:",continue_shot_and_record)
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
                if target_keywords[1] in str(partial_text)and not xiaoqi_event_triggered:
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")
                    xiaoqi_event.set()
                    xiaoqi_detected = True
                    xiaoqi_event_triggered = True

                    continue
                else:
                    xiaoqi_event.clear()

                    # print("partial未检测到qibao关键词，xiaoqi_event.clear")
                # if target_keywords[5] in str(partial_text):
                #     print(f"检测到sleep关键词: {target_keywords[5]}")
                #     continue_shot_and_record = True
                #     print("continue_shot_and_record1:", continue_shot_and_record)
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


############################################################################
import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18#18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS =64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


light_mode = 'const_color'

def colorWipe2(strip, color, wait_ms=100):
    """Wipe color across display a pixel at a time."""
    # print("colorWipe2 act.")
    # for i in range(strip.numPixels()):
        # strip.setPixelColor(i, color)
        # strip.show()
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=40):
    """Wipe color across display a pixel at a time."""
    # print("colorWipe act.")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
        # time.sleep(wait_ms/1000.0)

def colorWipe_single(strip, color, wait_ms=40):
    """Wipe color across display a pixel at a time."""
    # print("colorWipe_single act.")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    # print("theaterChase act.")
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    # print("wheel act.")
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    # print("rainbow act.")
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    # print("rainbowCycle act.")
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    # print("theaterChaseRainbow act.")
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def breath(r, g, b, waittime = 0.2):
    # print("breath act.")
    # for j in range(255, -1, -1):
    #     for i in range(strip.numPixels()):
    #         strip.setPixelColor(i, Color(j, 255 - j, 0))
    #         # print("j:", j)
    #     strip.show()
    #     time.sleep(0.01)
    # time.sleep(2)
    # for j in range(255):
    #     for i in range(strip.numPixels()):
    #         strip.setPixelColor(i, Color(0, 255, j))
    #         # print("j:", j)
    #     strip.show()
    #     time.sleep(0.01)
    # time.sleep(2)

    print("breath 1")
    # r = 25
    # g = 12
    # b = 12
    m = max(r, g, b)
    r1 = r
    g1 = g
    b1 = b
    while(true):
        if light_mode != 'breath':
            break
        for i in range(m):
            if r1 > 0:
                r1 = r1 - 1
            if g1 > 0:
                g1 = g1 - 1
            if b1 > 0:
                b1 = b1 - 1
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(r1, g1, b1))
            strip.show()
            time.sleep(waittime)

        for i in range(m):
            if r1 < r:
                r1 = r1 + 1
            if g1 > g:
                g1 = g1 + 1
            if b1 > b:
                b1 = b1 + 1
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(r1, g1, b1))
            strip.show()
            time.sleep(waittime)

def const_color(r,g,b):
    print("r,g,b:",r,g,b)
    # for j in range(255):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(r, g, b))
            # print("j:", j)
        strip.show()
        # time.sleep(0.01)
    # time.sleep(2)

def turn_off():
    # print("turn_off act.")
    # for j in range(255, -1, -1):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(0.01)



import RPi.GPIO as GPIO
import time
import subprocess
# 设置GPIO模式
GPIO.setmode(GPIO.BCM)

# 定义按键引脚
# KEY1_PIN = 17  # 对应按键1
KEYA_PIN = 17  # 对应按键A（已修改为GPIO17）
KEYB_PIN = 27  # 对应按键B（已修改为GPIO27）
DJ_PIN = 22  # 对应DJ引脚（模拟输出）

# 初始化GPIO引脚为输入和输出
# GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEYA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEYB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DJ_PIN, GPIO.OUT)
# 延时函数
def delayms(ms):
    time.sleep(ms / 1000.0)  # 转换为秒


# 按键检测函数
def check_keys():
    global jiaodu

    # if GPIO.input(KEY1_PIN) == GPIO.LOW:  # KEY1按下
    #     delayms(10)
    #     if GPIO.input(KEY1_PIN) == GPIO.LOW:  # 按键去抖
    #         jiaodu = 3  # 复位角度
    #         print(f"角度复位: {jiaodu}")

    if GPIO.input(KEYA_PIN) == GPIO.LOW and GPIO.input(KEYB_PIN) == GPIO.HIGH:  # KEYA按下
        delayms(5)
        if GPIO.input(KEYA_PIN) == GPIO.LOW and GPIO.input(KEYB_PIN) == GPIO.HIGH:
            jiaodu -= 1  # 逆时针旋转
            # decrease_volume(5)
            subprocess.run(['xdotool', 'key', 'Down'])  # 模拟按下 "Up" 键
            delayms(5)
            subprocess.run(['xdotool', 'key', 'Down'])  # 模拟按下 "Up" 键
            delayms(5)
            if jiaodu < 1:
                jiaodu = 1  # 限制最小角度
            print(f"逆时针旋转: {jiaodu}")

    elif GPIO.input(KEYA_PIN) == GPIO.HIGH and GPIO.input(KEYB_PIN) == GPIO.LOW:  # KEYB按下
        delayms(5)
        if GPIO.input(KEYA_PIN) == GPIO.HIGH and GPIO.input(KEYB_PIN) == GPIO.LOW:
            jiaodu += 1  # 顺时针旋转
            subprocess.run(['xdotool', 'key', 'Up'])  # 模拟按下 "Up" 键
            delayms(5)
            subprocess.run(['xdotool', 'key', 'Up'])  # 模拟按下 "Up" 键
            delayms(5)
            if jiaodu > 20:
                jiaodu = 20  # 限制最大角度
            print(f"顺时针旋转: {jiaodu}")

def adjust_volume():
    # 定时器模拟
    count = 0
    try:
        while True:
            # 每 0.5ms 触发一次
            delayms(2)
            count += 1

            # 判断当前角度值更新输出
            if count <= jiaodu:
                GPIO.output(DJ_PIN, GPIO.HIGH)  # 高电平输出
            elif count > jiaodu and count <= 40:
                GPIO.output(DJ_PIN, GPIO.LOW)  # 低电平输出
            if count > 40:
                count = 0  # 重新计数

            # 检测按键状态
            check_keys()

    except KeyboardInterrupt:
        print("程序终止")

    finally:
        GPIO.cleanup()
# 初始角度
# jiaodu = 10
# subprocess.Popen(['alsamixer'])
#
# # 等待 alsamixer 打开
# time.sleep(0.2)
#
# # 使用 xdotool 模拟按键 F6（进入声卡选择界面）
# subprocess.run(['xdotool', 'key', 'F6'])
#
# # 等待声卡选择界面加载
# time.sleep(0.2)
#
# # 使用 xdotool 模拟按下 “Down” 键来选择 USB 音频设备
# # 假设 3 USB Audio Device 在列表中是第三个，按两次 "Down" 键
# subprocess.run(['xdotool', 'key', 'Down'])  # 第一次按下 "Down"
# time.sleep(0.2)  # 等待半秒钟（可以根据实际需要调整时间）
# subprocess.run(['xdotool', 'key', 'Down'])  # 第二次按下 "Down"
# time.sleep(0.2)  # 等待半秒钟（可以根据实际需要调整时间）
# subprocess.run(['xdotool', 'key', 'Down'])  # 第一次按下 "Down"
# time.sleep(0.2)  # 等待半秒钟（可以根据实际需要调整时间）
# subprocess.run(['xdotool', 'key', 'Down'])  # 第二次按下 "Down"
# time.sleep(0.2)  # 等待半秒钟（可以根据实际需要调整时间）
# # 然后模拟按下 "Enter" 键选择 3 USB Audio Device
#
# subprocess.run(['xdotool', 'key', 'Return'])
# time.sleep(0.2)
# subprocess.run(["amixer", "cset", "numid=3", "3"])  # 3 表示选择 USB 音频设备
#
#
#
# time.sleep(0.2)
# adjust_volume_thread=threading.Thread(target=adjust_volume)
# adjust_volume_thread.start()


def scent_spray():
    global scent_spray_flag,last_scent_spray_flag
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.OUT)

    while True:
        if last_scent_spray_flag==scent_spray_flag:
            continue
        if scent_spray_flag==True:
            for j in range(30):
                time.sleep(5)
                for i in range(6):
                    GPIO.output(22, GPIO.HIGH)
                    time.sleep(0.1)
                    GPIO.output(22, GPIO.LOW)
                    print("GPIO.HIGH!")
                    time.sleep(7.9)
        if scent_spray_flag == False:
            GPIO.output(22, GPIO.LOW)
            print("GPIO.LOW!")
            time.sleep(1)

        last_scent_spray_flag = scent_spray_flag
        # 程序运行时，GPIO 17 处于高阻态

    # for i in range(10):
    #
    #     print("scent_spray is ON")
    #     time.sleep(20)  # 延时 1 秒
        # GPIO.output(22, GPIO.LOW)
        # print("LED is OFF")
        # time.sleep(1)  # 延时 1 秒






def listen_for_s_key():
    global standup_flag
    while True:
        time.sleep(0.05)  # ���� 0.1 秒，避免 CPU 占用过高
        user_input = input()  # 等待用户输入
        if user_input.lower() == 's':  # 检测是否按下 's' 键
            print("Pressed 's' key!")
            standup_flag = True


            # 在这里可以执行你希望的操作，比如：
            # Do something when 's' is pressed




if __name__ == "__main__":
    # shape_change2()
    #turn_off scent
    print("ABC")
    with open("li_scene_seq.txt", "w") as file_scene:
        file_scene.write(str(0))  # 将li_scene_seq写入文件，确保是数字序号的字符串格式

    GPIO.output(22, GPIO.LOW)
    print("GPIO.LOW!")

    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(60)
    model_file = "opencv_face_detector_uint8.pb"
    config_file = "opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
    threshold = 0.7
    freq = cv2.getTickFrequency()  # 系统频率
    # face_detection_run1()
    init()
    message_id = str(datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-8]+'start')
    message_id2 = str(datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-8]+'start')
    # time.sleep(10)

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    turn_off()


    try:
        if args.samplerate is None:
            print("1111")
            print(sd.query_devices())
            print("args.device:",args.device)
            device_info = sd.query_devices(args.device, "input")
            print("1112")
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info["default_samplerate"])
            print("1113")
        if args.model is None:
            print("2222")
            # model = Model(lang="en-us")
            model = Model(model_path)
        else:
            print("3333")
            # model = Model(lang=args.model)
            model = Model(model_path)

        if args.filename:
            print("4444")
            dump_fn = open(args.filename, "wb")
        else:
            print("5555")
            dump_fn = None
        # kaldi_thread=threading.Thread(target=kaldi_run)
        # kaldi_thread.start()

        key_thread = threading.Thread(target=listen_for_s_key)
        key_thread.daemon = True  # 将线程设为守护线程，这样程序退出时会自动结束线程
        key_thread.start()

        connection_thread=threading.Thread(target=create_connection_with_retries,args=(websocket_url,))
        connection_thread.start()

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






