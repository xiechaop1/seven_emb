import cv2
import time
import numpy as np
import argparse
import onnxruntime as ort
import math
import matplotlib.pyplot as plt
import queue
import os
# os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["DISPLAY"] = ":0"


person_found_flag=False
MAX_DISTANCE = 60
x_diff=0
y_diff=0
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
        print("delta_time:",delta_time)
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

class yolov5_lite():
    def __init__(self, model_pb_path, label_path, confThreshold=0.5, nmsThreshold=0.5,objThreshold=0.5):
        so = ort.SessionOptions()
        so.log_severity_level = 3
        self.net = ort.InferenceSession(model_pb_path, so)
        self.classes = list(map(lambda x: x.strip(), open(label_path, 'r').readlines()))
        self.num_classes = len(self.classes)
        anchors = [[10, 13, 16, 30, 33, 23], [30, 61, 62, 45, 59, 119], [116, 90, 156, 198, 373, 326]]
        self.nl = len(anchors)
        self.na = len(anchors[0]) // 2
        self.no = self.num_classes + 5
        self.grid = [np.zeros(1)] * self.nl
        self.stride = np.array([8., 16., 32.])
        self.anchor_grid = np.asarray(anchors, dtype=np.float32).reshape(self.nl, -1, 2)
        self.confThreshold = confThreshold
        self.nmsThreshold = nmsThreshold
        self.objThreshold = objThreshold
        self.input_shape = (self.net.get_inputs()[0].shape[2], self.net.get_inputs()[0].shape[3])

    def letterBox(self, srcimg, keep_ratio=True):
        top, left, newh, neww = 0, 0, self.input_shape[0], self.input_shape[1]
        if keep_ratio and srcimg.shape[0] != srcimg.shape[1]:
            hw_scale = srcimg.shape[0] / srcimg.shape[1]
            if hw_scale > 1:
                newh, neww = self.input_shape[0], int(self.input_shape[1] / hw_scale)
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                left = int((self.input_shape[1] - neww) * 0.5)
                img = cv2.copyMakeBorder(img, 0, 0, left, self.input_shape[1] - neww - left, cv2.BORDER_CONSTANT,
                                         value=0)  # add border
            else:
                newh, neww = int(self.input_shape[0] * hw_scale), self.input_shape[1]
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                top = int((self.input_shape[0] - newh) * 0.5)
                img = cv2.copyMakeBorder(img, top, self.input_shape[0] - newh - top, 0, 0, cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.resize(srcimg, self.input_shape, interpolation=cv2.INTER_AREA)
        return img, newh, neww, top, left

    def drawPred(self, frame, classId, conf, x1, y1, x2, y2,person_count=None):
        # Draw a bounding box.
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)

        label = '%.2f' % conf
        text = '%s:%s' % (self.classes[int(classId)], label)

        if person_count is not None:
            text += f" Person ID: {person_count}"  # 将person_count加入到text中

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        y1 = max(y1, labelSize[1])
        cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_TRIPLEX, 0.4, (0, 255, 0), thickness=1)
        # cv2.imshow('frame', frame)
        # cv2.waitKey(0)
        return frame


    def calculate_distance(self,center1, center2):
        return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

    def postprocess(self, frame, outs, pad_hw):
        global person_found_flag,x_diff,y_diff,roaming_stop_flag
        # person_found_flag=False
        newh, neww, padh, padw = pad_hw
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        ratioh, ratiow = frameHeight / newh, frameWidth / neww

        classIds = []
        confidences = []
        boxes = []
        person_count = 0  # 用来给每个person加编号
        prev_person_centers = []
        person_id_dict = {}

        # 遍历每个输出（检测结果）
        for detection in outs:
            # print("Detection shape:", detection.shape)  # 打印输出的形状
            # print("Detection contents:", detection)  # 打印输出的内容

            scores = detection[5:]
            # print("scores:", scores)
            classId = np.argmax(scores)
            # print("classId:", classId)
            confidence = scores[classId]

            # print("confidence:", confidence)
            # print("self.confThreshold:",self.confThreshold)
            # print("x1, y1, x2, y2, conf:", detection[0], detection[1], detection[2], detection[3], detection[4])
            if confidence > self.confThreshold and detection[4] > self.objThreshold:
                center_x = int((detection[0] - padw) * ratiow)
                center_y = int((detection[1] - padh) * ratioh)
                width = int(detection[2] * ratiow)
                height = int(detection[3] * ratioh)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                # print("center_x,center_y,width,height,left,top:",center_x,center_y,width,height,left,top)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

                if classId == 0:  # 如果是person类
                    current_center = (left + width / 2, top + height / 2)
                    matched = False

                    for prev_center in prev_person_centers:
                        distance = self.calculate_distance(current_center, prev_center)
                        print(
                            f"delta_x: {abs(current_center[0] - prev_center[0])}, delta_y: {abs(current_center[1] - prev_center[1])}, distance: {distance}")

                        if distance < MAX_DISTANCE:  # 如果两个人的距离小于阈值
                            matched = True
                            break

                    if matched:
                        pass  # 视为同一个人
                    else:
                        person_count += 1  # 认为是一个新的人
                        print(
                            f"New person detected! Person {person_count}, Confidence: {confidence}, Box: {left, top, width, height}, Center: {current_center}")

                    prev_person_centers.append(current_center)
                    area = width * height
                    print(f"Person {person_count} Area: {area} pixels")
                    print("person_found_flag:",person_found_flag)
                    motor_stop()  # 停止第一个电机
                    motor_stop2()  # 停止第二个电机
                    time.sleep(0.05)
                    roaming_stop_flag = True
                    if area>0:
                        person_found_flag=True
                        print("Person current_center:",current_center)
                        x_diff=current_center[0]-320
                        y_diff=current_center[1]-240-10

                        # 更新上一帧的person中心坐标
                    # prev_person_centers.append(current_center)

            # Perform non maximum suppression to eliminate redundant overlapping boxes with
            # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        for i in indices:
            i = i[0] if isinstance(i, (tuple, list)) else i
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            frame = self.drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height,person_count)
        return frame



    def detect(self, srcimg):
        img, newh, neww, top, left = self.letterBox(srcimg)
        # cv2.imshow('YOLOv5-img', img)
        # cv2.waitKey(0)
        # print("Image shape:", img.shape)
        # print("newh, neww, top, left:",newh, neww, top, left)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        blob = np.expand_dims(np.transpose(img, (2, 0, 1)), axis=0)

        t1 = time.time()
        # print("self.net.get_inputs()[0].name:",self.net.run(None, {self.net.get_inputs()[0].name: blob}))
        outs = self.net.run(None, {self.net.get_inputs()[0].name: blob})[0].squeeze(axis=0)

        cost_time = time.time() - t1
        print("outs.shape:",outs.shape)

        srcimg = self.postprocess(srcimg, outs, (newh, neww, top, left))
        # infer_time = 'Inference Time: ' + str(int(cost_time * 1000)) + 'ms'
        # cv2.putText(srcimg, infer_time, (5, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 0), thickness=1)

        return srcimg

#########################################################################################################################
import cv2
import numpy as np
import tensorflow as tf
import time

# 关节连接
EDGES = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y',
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y',
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
}

# 关键点名称映射
KEYPOINT_NAMES = [
    'Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear',
    'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow',
    'Left Wrist', 'Right Wrist', 'Left Hip', 'Right Hip',
    'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle'
]

# 保存所有循环的坐标列表


all_keypoints=[]
# 画关键点函数
def draw_keypoints(frame, keypoints, confidence_threshold):
    global all_keypoints
    all_keypoints = []
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))  # 恢复为原图大小
    current_keypoints = []  # 用于保存每一帧的关键点坐标

    for i, kp in enumerate(shaped):
        ky, kx, kp_conf = kp
        if kp_conf > confidence_threshold:
            cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)
            cv2.putText(frame, KEYPOINT_NAMES[i], (int(kx), int(ky) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        2)

            # 打印并保存每个关键点的坐标
            print(f"{KEYPOINT_NAMES[i]}: ({kx}, {ky})")
            current_keypoints.append((KEYPOINT_NAMES[i], (kx, ky)))  # 保存当前帧的坐标

        else:
            # 如果置信度低于阈值，保存为 (None, None)
            print(f"{KEYPOINT_NAMES[i]}: (None, None)")
            current_keypoints.append((KEYPOINT_NAMES[i], (None, None)))  # 保存为 (None, None)

    # 将当前帧的关键点坐标添加到所有关键点的列表中
    all_keypoints.append(current_keypoints)
    # print("all_keypoints:",all_keypoints)


# 画骨骼函数
def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))  # 恢复为原图大小

    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)


img_share=None
def yolo_run(img, done_event):
    global person_found_flag
    # 直接在 img 上绘制 YOLO 检测结果（假设 net.detect 返回绘制了人体框的图像）
    img[:] = net.detect(img)  # 注意：net.detect 需要直接修改 img
    done_event.set()  # 标记 YOLO 处理完成

# MoveNet 推理线程
def fastnet_run(img, keypoints_queue, done_event):
    # 图片预处理
    img_resized = cv2.resize(img, (192, 192))
    img_resized = np.expand_dims(img_resized, axis=0)
    input_image = tf.cast(img_resized, dtype=tf.float32)
    model_path = '/home/li/Downloads/Pose-detection/lite-model_movenet_singlepose_lightning_3.tflite'
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    # 执行推理
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
    interpreter.invoke()

    # 获取推理结果
    keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])

    # 画出关键点和骨骼（直接在 img 上绘制）
    draw_connections(img, keypoints_with_scores, EDGES, 0.4)
    draw_keypoints(img, keypoints_with_scores, 0.4)

    # 将关键点存储到队列
    keypoints_queue.put(keypoints_with_scores)
    done_event.set()  # 标记 MoveNet 处理完成

def run_keypoint_main():
    global person_found_flag, all_keypoints

    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    frame_counter = 0
    last_processed_img = None  # 保存最近一次处理后的图像
    while True:
        ret, img = cap.read()
        if not ret:
            print("无法读取视频流")
            break

        # 获取图像的宽度和高度
        height, width, channels = img.shape
        print(f"pic width: {width}, pic height: {height}")

        if frame_counter % 4 == 0:  # 每 2 帧处理一次
            # 创建事件对象，用于同步线程
            yolo_done = threading.Event()
            fastnet_done = threading.Event()

            # 创建队列存储关键点
            keypoints_queue = queue.Queue()

            # 启动 YOLO 检测线程
            yolo_thread = threading.Thread(target=yolo_run, args=(img, yolo_done))
            yolo_thread.daemon = True
            yolo_thread.start()

            # 启动 MoveNet 推理线程
            fastnet_thread = threading.Thread(target=fastnet_run, args=(img, keypoints_queue, fastnet_done))
            fastnet_thread.daemon = True
            fastnet_thread.start()

            # 等待两个线程完成
            yolo_done.wait()
            fastnet_done.wait()

            # 从队列获取关键点
            if not keypoints_queue.empty():
                keypoints_with_scores = keypoints_queue.get()
                all_keypoints.append(keypoints_with_scores)

            last_processed_img = img.copy()  # 保存处理后的图像

        # 显示结果
        if last_processed_img is not None:
            cv2.imshow("MoveNet Lightning", last_processed_img)
        else:
            cv2.imshow("MoveNet Lightning", img)  # 如果没有处理结果，显示原始帧

        frame_counter += 1

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 打印所有帧的关键点
    print("\nAll Keypoints Detected:")
    for frame_idx, keypoints in enumerate(all_keypoints):
        print(f"Frame {frame_idx + 1}:")
        for point_name, coords in keypoints:
            print(f"  {point_name}: {coords}")

#########################################################################################################################

##############################################################
import time
import Adafruit_ADS1x15
import threading
import RPi.GPIO as GPIO
import math
# 初始化ADS1115模块，选择I2C地址0x48（默认地址）
adc = Adafruit_ADS1x15.ADS1115(address=0x48)

# 设置增益（Gain）为1，适用于0-4.096V范围
GAIN = 1

# 采样率设置（单位：每秒样本数）
SAMPLE_RATE = 1

# 用于读取电流的转换关系，假设0-3V输出，0-2000mA电流
VOLTAGE_TO_CURRENT_CONVERSION = 2000 / 3.0  # 每伏特对应的电流值（mA/V）

# 设置GPIO模式
GPIO.setmode(GPIO.BCM)

# 定义控制电机的GPIO引脚
# INA_PIN = 13  # 控制电机A的GPIO引脚
# INB_PIN = 12  # 控制电机B的GPIO引脚

INA_PIN = 6  # 控制电机A的GPIO引脚
INB_PIN = 5  # 控制电机B的GPIO引脚

# 设置引脚为输出
GPIO.setup(INA_PIN, GPIO.OUT)
GPIO.setup(INB_PIN, GPIO.OUT)

# 设置PWM频率（一般直流电机使用频率50Hz ~ 100Hz比较合适）
pwmINA = GPIO.PWM(INA_PIN, 100)  # 设置INA引脚为PWM输出，频率100Hz
pwmINB = GPIO.PWM(INB_PIN, 100)  # 设置INB引脚为PWM输出，频率100Hz
#
# 启动PWM
pwmINA.start(0)  # 初始占空比0，即停止
pwmINB.start(0)  # 初始占空比0，即停止

# 控制电机的函数
def motor_forward(speed):
    pwmINA.ChangeDutyCycle(speed)  # 设置电机A的占空比（控制电机正转速度）
    pwmINB.ChangeDutyCycle(0)  # 电机B保持不动

def motor_reverse(speed):
    pwmINA.ChangeDutyCycle(0)  # 电机A保持不动
    pwmINB.ChangeDutyCycle(speed)  # 设置电机B的占空比（控制电机反转速度）

def motor_stop():
    pwmINA.ChangeDutyCycle(0)  # 停止电机A
    pwmINB.ChangeDutyCycle(0)  # 停止电机B

# def motor_forward():
#     GPIO.output(INA_PIN, GPIO.HIGH)  # 电机A正转
#     GPIO.output(INB_PIN, GPIO.LOW)   # 电机B停止
#
# def motor_reverse():
#     GPIO.output(INA_PIN, GPIO.LOW)   # 电机A停止
#     GPIO.output(INB_PIN, GPIO.HIGH)  # 电机B反转
#
# def motor_stop():
#     GPIO.output(INA_PIN, GPIO.LOW)   # 停止电机A
#     GPIO.output(INB_PIN, GPIO.LOW)   # 停止电机B

motor_degree=0
angle_def=30
motor_speed=100
current_pos=0

INA_PIN2 = 13  # 控制电机A的GPIO引脚
INB_PIN2 = 12  # 控制电机B的GPIO引脚

# INA_PIN = 6  # 控制电机A的GPIO引脚
# INB_PIN = 5  # 控制电机B的GPIO引脚

# 设置引脚为输出
GPIO.setup(INA_PIN2, GPIO.OUT)
GPIO.setup(INB_PIN2, GPIO.OUT)

# 设置PWM频率（一般直流电机使用频率50Hz ~ 100Hz比较合适）
pwmINA2 = GPIO.PWM(INA_PIN2, 100)  # 设置INA引脚为PWM输出，频率100Hz
pwmINB2 = GPIO.PWM(INB_PIN2, 100)  # 设置INB引脚为PWM输出，频率100Hz

# 启动PWM
pwmINA2.start(0)  # 初始占空比0，即停止
pwmINB2.start(0)  # 初始占空比0，即停止


# 控制电机的函数
def motor_forward2(speed):
    pwmINA2.ChangeDutyCycle(speed)  # 设置电机A的占空比（控制电机正转速度）
    pwmINB2.ChangeDutyCycle(0)  # 电机B保持不动
    # GPIO.output(INA_PIN2, GPIO.HIGH)  # 电机A正转
    # GPIO.output(INB_PIN2, GPIO.LOW)   # 电机B停止

def motor_reverse2(speed):
    pwmINA2.ChangeDutyCycle(0)  # 电机A保持不动
    pwmINB2.ChangeDutyCycle(speed)  # 设置电机B的占空比（控制电机反转速度）
    # GPIO.output(INA_PIN2, GPIO.LOW)  # 电机A停止
    # GPIO.output(INB_PIN2, GPIO.HIGH)  # 电机B反转

def motor_stop2():
    pwmINA2.ChangeDutyCycle(0)  # 停止电机A
    pwmINB2.ChangeDutyCycle(0)  # 停止电机B
    # GPIO.output(INA_PIN2, GPIO.LOW)  # 停止电机A
    # GPIO.output(INB_PIN2, GPIO.LOW)  # 停止电机B

motor_degree=0
angle_def2=30
motor_speed2=100
current_pos2=0
last_angle1=10
last_angle2=10
roaming_stop_flag=False


def check_body_keypoints(all_keypoints):
    if not all_keypoints or not isinstance(all_keypoints[0], list):
        print("Error: all_keypoints is empty or not in the expected format.")
        return -1  # or handle as needed

    # 定义需要检查的关键点名称
    required_keypoints = [
        # 'Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear',
        'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow',
        'Left Wrist', 'Right Wrist', 'Left Hip', 'Right Hip',
        'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle'
    ]

    # 遍历 all_keypoints
    for keypoint in all_keypoints[0]:  # 只处理列表中的第一项
        keypoint_name, coords = keypoint
        # 判断关键点是否在所需列表中
        if keypoint_name in required_keypoints:
            # 如果该关键点的坐标为 (None, None)
            if coords == (None, None):
                print(f"{keypoint_name} 坐标为 (None, None)")
            else:
                print(f"{keypoint_name} 坐标: {coords}")
                # 如果有一个坐标不为 (None, None)，返回 1
                return 1

    # 如果所有关键点的坐标都为 (None, None)，返回 -1
    return -1


def check_head_keypoints(all_keypoints):
    if not all_keypoints or not isinstance(all_keypoints[0], list):
        print("Error: all_keypoints is empty or not in the expected format.")
        return -1  # or handle as needed

    # 定义需要检查的关键点名称
    required_keypoints = ['Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear']

    # 遍历 all_keypoints
    for keypoint in all_keypoints[0]:  # 只处理列表中的第一项
        keypoint_name, coords = keypoint
        # 判断关键点是否在所需列表中
        if keypoint_name in required_keypoints:
            # 如果该关键点的坐标为 (None, None)
            if coords == (None, None):
                print(f"{keypoint_name} 坐标为 (None, None)")
            else:
                print(f"{keypoint_name} 坐标: {coords}")
                # 如果有一个坐标不为 (None, None)，返回 1
                return 1

    # 如果所有关键点的坐标都为 (None, None)，返回 -1
    return -1
def person_tracking_whole():
    global x_diff,y_diff,all_keypoints
    pid_x = PIDController(Kp=0.3, Ki=0, Kd=0)  # 水平方向的 PID 控制器
    pid_y = PIDController(Kp=0.4, Ki=0, Kd=0)  # 竖直方向的 PID 控制器

    x_adust_degree=0
    y_adust_degree=0

    while True:
        print("x_dif,y_difff:", x_diff, y_diff)
        if abs(x_diff)>13 or abs(y_diff)>13:
            x_diff_div_20=int(x_diff / 10)
            y_diff_div_20=int(y_diff / 9)
            print("int(x_diff_div_20):",x_diff_div_20)
            print("int(y_diff_div_20):",y_diff_div_20 )
            # x_input = x_diff * (60 / 640)  # 像素到角度转换
            # y_input = y_diff * (40 / 480)
            x_adust_degree = pid_x.update(x_diff_div_20)
            y_adust_degree = pid_y.update(y_diff_div_20)
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@x_adust_degree:",x_adust_degree)
            print("@@@@y_adust_degree:", y_adust_degree)

            person_tracking(int(y_adust_degree*2),-int(x_adust_degree*2),100)
            print("int(y_adust_degree):",int(y_adust_degree))
            print("-int(x_adust_degree):",-int(x_adust_degree))
            # time.sleep(1)
            if abs(x_diff)<50 and abs(y_diff)<50:
                print("all_keypoints:", all_keypoints)
                head_resl=check_head_keypoints(all_keypoints)
                print("head_resl:",head_resl)
                body_resl=check_body_keypoints(all_keypoints)
                print("body_resl:", body_resl)
                if head_resl==-1 and body_resl==1:
                    print("detect body no head!!")
                    person_tracking(-40, -int(x_adust_degree*2), 100)


        elif x_diff<=13 and y_diff<=13:
            print("target reached!")
            time.sleep(0.2)
            # break


def person_tracking(angle1=angle_def, angle2=angle_def2, total_speed=motor_speed):
    global current_pos, clog_flag, current_pos2, clog_flag2,person_found_flag,roaming_stop_flag,last_angle1,last_angle2

    print("angle_def1:", angle1)
    with open("motor_degree.txt", "r") as file_status:
        current_pos = int(file_status.read().strip())  # 读取并去除任何多余的空白字符

    print("angle_def2:", angle2)
    with open("motor_degree2.txt", "r") as file_status:
        current_pos2 = int(file_status.read().strip())  # 读取并去除任何多余的空白字符

    # 计算勾股定理中的斜边长度
    # hypotenuse = math.sqrt(angle1**2 + angle2**2)
    #
    # # 根据角度和勾股定理调整每个电机的速度
    # speed1_adjusted = total_speed * (abs(angle1) / hypotenuse)  # 轴1的速度
    # speed2_adjusted = total_speed * (abs(angle2) / hypotenuse)  # 轴2的速度
    #
    # print(f"Adjusted speeds -> motor1: {speed1_adjusted}, motor2: {speed2_adjusted}")

    # 控制电机同时运动
    for i in range(max(abs(angle1), abs(angle2))):  # 根据最大角度进行循环
        print("i:",i)
        # time.sleep(0.1)
        # print("person_found_flag2:", person_found_flag)
        # if person_found_flag==True:
        #     motor_stop()  # 停止第一个电机
        #     motor_stop2()  # 停止第二个电机
        #     time.sleep(0.1)
        #     roaming_stop_flag=True
        #     print("person found motor_forward_together2 break!")
        #     last_angle1=angle1
        #     last_angle2=angle2
        #     person_found_flag=False
        #     break
        # 控制第一个电机
        if angle1 > 0:
            motor_forward(total_speed)  # 控制第一个电机正转
        elif angle1 < 0:
            motor_reverse(total_speed)  # 控制第一个电机反转

        # 控制第二个电机
        if angle2 > 0:
            motor_forward2(total_speed)  # 控制第二个电机正转
        elif angle2 < 0:
            motor_reverse2(total_speed)  # 控制第二个电机反转

        # 检查电机是否堵转
        if clog_flag == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 1!!!!!!!!!!!!!!")
            motor_stop()  # 停止第一个电机
            clog_flag = False
            with open("motor_degree.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第一个电机的角度
            time.sleep(0.1)
            break

        if clog_flag2 == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 2!!!!!!!!!!!!!!")
            motor_stop2()  # 停止第二个电机
            clog_flag2 = False
            with open("motor_degree2.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第二个电机的角度
            time.sleep(0.1)
            break

        # 更新电机角度
        with open("motor_degree.txt", "w") as file_status:
            current_pos = current_pos + 1
            print("current_pos+:", current_pos)
            file_status.write(str(current_pos))  # 更新第一个电机角度

        with open("motor_degree2.txt", "w") as file_status:
            current_pos2 = current_pos2 + 1
            print("current_pos2+:", current_pos2)
            file_status.write(str(current_pos2))  # 更新第二个电机角度

    print("电机forward停止")
    motor_stop()  # 停止第一个电机
    motor_stop2()  # 停止第二个电机
    time.sleep(0.05)


# def motor_forward_together2(angle1=angle_def, angle2=angle_def2, total_speed=motor_speed):
#     global current_pos, clog_flag, current_pos2, clog_flag2, person_found_flag, roaming_stop_flag, last_angle1, last_angle2
#
#     print("angle_def1:", angle1)
#     with open("motor_degree.txt", "r") as file_status:
#         current_pos = int(file_status.read().strip())
#
#     print("angle_def2:", angle2)
#     with open("motor_degree2.txt", "r") as file_status:
#         current_pos2 = int(file_status.read().strip())
#
#     # 正弦波参数
#     amplitude = abs(angle1)  # x 轴正弦波振幅
#     period = 4.0  # 正弦波周期（秒），可根据需要调整
#     omega = 2 * math.pi / period  # 角频率 ω = 2π/T
#     y_speed_per_sec = angle2 / period  # y 轴每秒移动角度（度数/秒）
#
#     # 运动持续时间（一个周期）
#     duration = period
#
#     # 时间步长（秒）
#     time_step = 0.1
#
#     # 初始化时间
#     start_time = time.time()
#     elapsed_time = 0
#
#     # 上一次的角度，用于计算差值
#     last_angle1 = 0
#     last_angle2 = 0
#
#     while elapsed_time < duration:
#         elapsed_time = time.time() - start_time
#
#         # 计算 x 轴正弦波角度：current_angle1 = amplitude * sin(ωt)
#         current_angle1 = amplitude * math.sin(omega * elapsed_time)
#
#         # 计算 y 轴线性变化角度：current_angle2 = angle2 * (t / T)
#         current_angle2 = y_speed_per_sec * elapsed_time
#
#         # 计算角度差
#         delta_angle1 = current_angle1 - last_angle1
#         delta_angle2 = current_angle2 - last_angle2
#
#         print("current_angle1, current_angle2:", current_angle1, current_angle2)
#         print("delta_angle1, delta_angle2:", delta_angle1, delta_angle2)
#
#         # 计算勾股定理中的斜边长度
#         hypotenuse = math.sqrt(delta_angle1**2 + delta_angle2**2)
#
#         # 根据角度差调整电机速度
#         if hypotenuse > 0:  # 防止除以 0
#             speed1_adjusted = total_speed * (abs(delta_angle1) / hypotenuse)
#             speed2_adjusted = total_speed * (abs(delta_angle2) / hypotenuse)
#         else:
#             speed1_adjusted = 0
#             speed2_adjusted = 0
#
#         print(f"Adjusted speeds -> motor1: {speed1_adjusted}, motor2: {speed2_adjusted}")
#
#         # 控制电机运动
#         if abs(delta_angle1) > 0.1 or abs(delta_angle2) > 0.1:  # 仅在角度差足够大时调整
#             # 控制第一个电机（x 轴）
#             if delta_angle1 > 0:
#                 motor_forward(speed1_adjusted)
#             elif delta_angle1 < 0:
#                 motor_reverse(speed1_adjusted)
#
#             # 控制第二个电机（y 轴）
#             if delta_angle2 > 0:
#                 motor_forward2(speed2_adjusted)
#             elif delta_angle2 < 0:
#                 motor_reverse2(speed2_adjusted)
#
#             # 更新电机角度文件
#             with open("motor_degree.txt", "w") as file_status:
#                 current_pos += int(math.copysign(1, delta_angle1)) if abs(delta_angle1) > 0.1 else 0
#                 print("current_pos+:", current_pos)
#                 file_status.write(str(current_pos))
#
#             with open("motor_degree2.txt", "w") as file_status:
#                 current_pos2 += int(math.copysign(1, delta_angle2)) if abs(delta_angle2) > 0.1 else 0
#                 print("current_pos2+:", current_pos2)
#                 file_status.write(str(current_pos2))
#
#         # 检查人脸检测标志
#         print("person_found_flag2:", person_found_flag)
#         if person_found_flag:
#             motor_stop()
#             motor_stop2()
#             time.sleep(0.1)
#             roaming_stop_flag = True
#             print("person found motor_forward_together2 break!")
#             last_angle1 = angle1
#             last_angle2 = angle2
#             break
#
#         # 检查电机堵转
#         if clog_flag:
#             print("!!!!!!!!!!!!!!!!clog forward for motor 1!!!!!!!!!!!!!!")
#             motor_stop()
#             clog_flag = False
#             with open("motor_degree.txt", "w") as file_status:
#                 file_status.write(str(0))
#             time.sleep(0.1)
#             break
#
#         if clog_flag2:
#             print("!!!!!!!!!!!!!!!!clog forward for motor 2!!!!!!!!!!!!!!")
#             motor_stop2()
#             clog_flag2 = False
#             with open("motor_degree2.txt", "w") as file_status:
#                 file_status.write(str(0))
#             time.sleep(0.1)
#             break
#
#         # 更新上一次角度
#         last_angle1 = current_angle1
#         last_angle2 = current_angle2
#
#         # 等待时间步长
#         time.sleep(time_step)
#
#     print("电机forward停止")
#     motor_stop()
#     motor_stop2()
#     time.sleep(0.1)



def motor_forward_together2(angle1=angle_def, angle2=angle_def2, total_speed=motor_speed):
    global current_pos, clog_flag, current_pos2, clog_flag2,person_found_flag,roaming_stop_flag,last_angle1,last_angle2

    print("angle_def1:", angle1)
    with open("motor_degree.txt", "r") as file_status:
        current_pos = int(file_status.read().strip())  # 读取并去除任何多余的空白字符

    print("angle_def2:", angle2)
    with open("motor_degree2.txt", "r") as file_status:
        current_pos2 = int(file_status.read().strip())  # 读取并去除任何多余的空白字符

    # 计算勾股定理中的斜边长度
    hypotenuse = math.sqrt(angle1**2 + angle2**2)

    # 根据角度和勾股定理调整每个电机的速度
    speed1_adjusted = total_speed * (abs(angle1) / hypotenuse)  # 轴1的速度
    speed2_adjusted = total_speed * (abs(angle2) / hypotenuse)  # 轴2的速度

    print(f"Adjusted speeds -> motor1: {speed1_adjusted}, motor2: {speed2_adjusted}")

    # 控制电机同时运动
    for i in range(max(abs(angle1), abs(angle2))):  # 根据最大角度进行循环
        time.sleep(0.1)
        print("person_found_flag2:", person_found_flag)
        if person_found_flag==True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            roaming_stop_flag=True
            print("person found motor_forward_together2 break!")
            last_angle1=angle1
            last_angle2=angle2
            break
        # 控制第一个电机
        if angle1 > 0:
            motor_forward(total_speed)  # 控制第一个电机正转
        elif angle1 < 0:
            motor_reverse(total_speed)  # 控制第一个电机反转

        # 控制第二个电机
        if angle2 > 0:
            motor_forward2(total_speed)  # 控制第二个电机正转
        elif angle2 < 0:
            motor_reverse2(total_speed)  # 控制第二个电机反转

        # 检查电机是否堵转
        if clog_flag == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 1!!!!!!!!!!!!!!")
            motor_stop()  # 停止第一个电机
            clog_flag = False
            with open("motor_degree.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第一个电机的角度
            time.sleep(0.1)
            break

        if clog_flag2 == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 2!!!!!!!!!!!!!!")
            motor_stop2()  # 停止第二个电机
            clog_flag2 = False
            with open("motor_degree2.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第二个电机的角度
            time.sleep(0.1)
            break

        # 更新电机角度
        with open("motor_degree.txt", "w") as file_status:
            current_pos = current_pos + 1
            print("current_pos+:", current_pos)
            file_status.write(str(current_pos))  # 更新第一个电机角度

        with open("motor_degree2.txt", "w") as file_status:
            current_pos2 = current_pos2 + 1
            print("current_pos2+:", current_pos2)
            file_status.write(str(current_pos2))  # 更新第二个电机角度

    print("电机forward停止")
    motor_stop()  # 停止第一个电机
    motor_stop2()  # 停止第二个电机
    time.sleep(0.1)

def motor_forward_together2_no_break(angle1=angle_def, angle2=angle_def2, total_speed=motor_speed):
    global current_pos, clog_flag, current_pos2, clog_flag2,person_found_flag,roaming_stop_flag,last_angle1,last_angle2

    print("angle_def1:", angle1)
    try:
        with open("motor_degree.txt", "r") as file_status:
            current_pos = int(file_status.read().strip())  # 读取并去除任何多余的空白字符
            current_pos = int(current_pos) if current_pos else 0  # 若为空，则默认赋值为 0
    except (ValueError, FileNotFoundError):
        current_pos = 0  #
    print("angle_def2:", angle2)
    try:
        with open("motor_degree2.txt", "r") as file_status2:
            current_pos2 = int(file_status2.read().strip())  # 读取并去除任何多余的空白字符
            current_pos2 = int(current_pos2) if current_pos2 else 0  # 若为空，则默认赋值为 0
    except (ValueError, FileNotFoundError):
        current_pos2 = 0  #
    # 计算勾股定理中的斜边长度
    # hypotenuse = math.sqrt(angle1**2 + angle2**2)
    #
    # # 根据角度和勾股定理调整每个电机的速度
    # speed1_adjusted = total_speed * (abs(angle1) / hypotenuse)  # 轴1的速度
    # speed2_adjusted = total_speed * (abs(angle2) / hypotenuse)  # 轴2的速度
    #
    # print(f"Adjusted speeds -> motor1: {speed1_adjusted}, motor2: {speed2_adjusted}")

    # 控制电机同时运动
    for i in range(max(abs(angle1), abs(angle2))):  # 根据最大角度进行循环
        time.sleep(0.05)
        # print("person_found_flag2:", person_found_flag)
        # if person_found_flag==True:
        #     motor_stop()  # 停止第一个电机
        #     motor_stop2()  # 停止第二个电机
        #     time.sleep(0.1)
        #     roaming_stop_flag=True
        #     print("person found motor_forward_together2 break!")
        #     last_angle1=angle1
        #     last_angle2=angle2
        #     break
        # 控制第一个电机
        if angle1 > 0:
            motor_forward(total_speed)  # 控制第一个电机正转
        elif angle1 < 0:
            motor_reverse(total_speed)  # 控制第一个电机反转

        # 控制第二个电机
        if angle2 > 0:
            motor_forward2(total_speed)  # 控制第二个电机正转
        elif angle2 < 0:
            motor_reverse2(total_speed)  # 控制第二个电机反转

        # 检查电机是否堵转
        if clog_flag == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 1!!!!!!!!!!!!!!")
            motor_stop()  # 停止第一个电机
            clog_flag = False
            with open("motor_degree.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第一个电机的角度
            time.sleep(0.1)
            break

        if clog_flag2 == True:
            print("!!!!!!!!!!!!!!!!clog forward for motor 2!!!!!!!!!!!!!!")
            motor_stop2()  # 停止第二个电机
            clog_flag2 = False
            with open("motor_degree2.txt", "w") as file_status:
                file_status.write(str(0))  # 更新第二个电机的角度
            time.sleep(0.1)
            break

        # 更新电机角度
        with open("motor_degree.txt", "w") as file_status:
            current_pos = current_pos + 1
            print("current_pos+:", current_pos)
            file_status.write(str(current_pos))  # 更新第一个电机角度

        with open("motor_degree2.txt", "w") as file_status:
            current_pos2 = current_pos2 + 1
            print("current_pos2+:", current_pos2)
            file_status.write(str(current_pos2))  # 更新第二个电机角度

    print("电机forward停止")
    motor_stop()  # 停止第一个电机
    motor_stop2()  # 停止第二个电机
    time.sleep(0.1)

# 运行电机

# for i in range(3):
#     motor_forward(motor_speed)  # 电机正转，速度50%
#     time.sleep(3)
#     motor_stop()  # 停止电机
#     time.sleep(1)
#     motor_reverse(motor_speed)
#     time.sleep(3)
#     motor_stop()  # 停止电机
#     time.sleep(1)


def motor_forward_angle(angle=angle_def,speed=motor_speed):
    global current_pos,clog_flag
    print("angle_def1:", angle)
    with open("motor_degree.txt", "r") as file_status:
        current_pos = int(file_status.read().strip())  # 读取并去除任何多余的空白字符
    for i in range(angle):
        time.sleep(0.2)
        motor_forward(speed)  # 电机正转，速度50%
        # print("clog_flag2:", clog_flag)
        if clog_flag==True:
            print("!!!!!!!!!!!!!!!!clog forward!!!!!!!!!!!!!!")
            motor_stop()

            clog_flag = False
            with open("motor_degree.txt", "w") as file_status:
                file_status.write(str(0))  # 更新文件
            time.sleep(0.1)
            break

        with open("motor_degree.txt", "w") as file_status:

            current_pos = current_pos +1
            print("current_pos+:", current_pos)
            file_status.write(str(current_pos))  # 更新文件



    print("电机forward停止")
    motor_stop()  # 停止电机
    time.sleep(0.1)

def motor_backward_angle(angle=angle_def,speed=motor_speed):
    global current_pos,clog_flag
    print("angle_def2:", angle)
    with open("motor_degree.txt", "r") as file_status:
        current_pos = int(file_status.read().strip())  # 读取并去除任何多余的空白字符
    for i in range(angle):
        time.sleep(0.2)
        motor_reverse(speed)  # 电机反转，速度50%
        # print("clog_flag3:", clog_flag)
        if clog_flag == True:
            print("!!!!!!!!!!!!!!!!clog backward!!!!!!!!!!!!!!")
            motor_stop()

            clog_flag=False


            with open("motor_degree.txt", "w") as file_status:
                file_status.write(str(0))  # 更新文件
            time.sleep(0.1)
            break
        with open("motor_degree.txt", "w") as file_status:
            current_pos = current_pos -1
            print("current_pos-:", current_pos)
            file_status.write(str(current_pos))  # 更新文件



    print("电机backward停止")
    motor_stop()  # 停止电机
    time.sleep(0.1)
def read_voltage():
    # 读取 A0 引脚上的电压值，返回一个值范围在-32768 到 32767之间
    value = adc.read_adc(2, gain=GAIN)

    # 将读取的值转换为电压值（范围0-4.096V）
    voltage = value * 4.096 / 32768.0

    return voltage


def motor_forward_angle2(angle=angle_def2,speed=motor_speed2):
    global current_pos2,clog_flag2
    print("angle_def1:", angle)
    with open("motor_degree2.txt", "r") as file_status:
        current_pos2 = int(file_status.read().strip())  # 读取并去除任何多余的空白字符
    for i in range(angle):
        time.sleep(0.2)
        motor_forward2(speed)  # 电机正转，速度50%
        # print("clog_flag2:", clog_flag2)
        if clog_flag2==True:
            print("!!!!!!!!!!!!!!!!clog forward!!!!!!!!!!!!!!")
            motor_stop2()

            clog_flag2 = False
            with open("motor_degree2.txt", "w") as file_status:
                file_status.write(str(0))  # 更新文件
            time.sleep(0.1)
            break

        with open("motor_degree2.txt", "w") as file_status:

            current_pos2 = current_pos2 +1
            print("current_pos2+:", current_pos2)
            file_status.write(str(current_pos2))  # 更新文件



    print("电机forward停止")
    motor_stop2()  # 停止电机
    time.sleep(0.1)

def motor_backward_angle2(angle=angle_def2,speed=motor_speed2):
    global current_pos2,clog_flag2
    print("angle_def2:", angle)
    with open("motor_degree2.txt", "r") as file_status:
        current_pos2 = int(file_status.read().strip())  # 读取并去除任何多余的空白字符
    for i in range(angle):
        time.sleep(0.2)
        motor_reverse2(speed)  # 电机反转，速度50%
        # print("clog_flag3:", clog_flag)
        if clog_flag2 == True:
            print("!!!!!!!!!!!!!!!!clog backward!!!!!!!!!!!!!!")
            motor_stop2()

            clog_flag2=False


            with open("motor_degree2.txt", "w") as file_status:
                file_status.write(str(0))  # 更新文件
            time.sleep(0.1)
            break
        with open("motor_degree2.txt", "w") as file_status:
            current_pos2 = current_pos2 -1
            print("current_pos2-:", current_pos2)
            file_status.write(str(current_pos2))  # 更新文件



    print("电机backward停止")
    motor_stop2()  # 停止电机
    time.sleep(0.1)
# def read_voltage():
#     # 读取 A0 引脚上的电压值，返回一个值范围在-32768 到 32767之间
#     value = adc.read_adc(2, gain=GAIN)
#
#     # 将读取的值转换为电压值（范围0-4.096V）
#     voltage = value * 4.096 / 32768.0
#
#     return voltage


def read_voltage2():
    # 读取 A0 引脚上的电压值，返回一个值范围在-32768 到 32767之间
    value = adc.read_adc(0, gain=GAIN)

    # 将读取的值转换为电压值（范围0-4.096V）
    voltage = value * 4.096 / 32768.0

    return voltage







def voltage_to_current(voltage):
    # 将电压转换为电流（mA）
    current = voltage * VOLTAGE_TO_CURRENT_CONVERSION
    return current
current=0

clog_flag=False
clog_flag2=False
def read_adc():
    global current, clog_flag
    current_values = []  # 用来存储电流值
    start_time = time.time()  # 记录开始时间

    try:
        while True:
            # 读取电压值
            voltage = read_voltage()

            # 将电压转换为电流值
            current = voltage_to_current(voltage)

            # 添加当前电流值到列表
            current_values.append(current)

            # 打印电流值
            print(f"电压: {voltage:.2f} V, 电流: {current:.2f} mA")

            # 每秒读取一次
            if time.time() - start_time >= 0.8:
                # 计算过去1秒的平均电流值
                avg_current = sum(current_values) / len(current_values)
                # print(f"avg_current: {avg_current:.2f} mA")

                # 如果平均电流大于52mA，表示电机可能堵转
                if avg_current > 42:
                    clog_flag = True
                    # print("clog_flag1:", clog_flag)
                    print("get clogged!")
                # else:
                #     clog_flag = False



                # 清空电流列表，为下一秒准备
                current_values.clear()
                start_time = time.time()  # 重置时间

            time.sleep(0.05)  # 每50毫秒读取一次电流

    except KeyboardInterrupt:
        print("程序已中断")
        # 在程序退出时可以检查最终的堵转标志
        if clog_flag:
            print("检测到电机堵转")
        else:
            print("电机未堵转")

def read_adc2():
    global current2, clog_flag2
    current_values = []  # 用来存储电流值
    start_time = time.time()  # 记录开始时间

    try:
        while True:
            # 读取电压值
            voltage = read_voltage2()

            # 将电压转换为电流值
            current2 = voltage_to_current(voltage)

            # 添加当前电流值到列表
            current_values.append(current2)

            # 打印电流值
            print(f"电压2: {voltage:.2f} V, 电流2: {current2:.2f} mA")

            # 每秒读取一次
            if time.time() - start_time >= 0.8:
                # 计算过去1秒的平均电流值
                avg_current = sum(current_values) / len(current_values)
                # print(f"avg_current: {avg_current:.2f} mA")

                # 如果平均电流大于52mA，表示电机可能堵转
                if avg_current > 42:
                    clog_flag2 = True
                    # print("clog_flag1:", clog_flag2)
                    print("get clogged!")
                # else:
                #     clog_flag2 = False



                # 清空电流列表，为下一秒准备
                current_values.clear()
                start_time = time.time()  # 重置时间

            time.sleep(0.05)  # 每50毫秒读取一次电流

    except KeyboardInterrupt:
        print("程序已中断")
        # 在程序退出时可以检查最终的堵转标志
        if clog_flag2:
            print("检测到电机堵转")
        else:
            print("电机未堵转")
def find_zero_pos():
    global current,clog_flag
    for i in range(1):
        print("enter find_zero_pos")
        # motor_forward_angle(20,100)
        # time.sleep(1)
        # motor_forward_angle(80, 100)
        # time.sleep(1)
        motor_backward_angle(120, 100)



def find_zero_pos2():
    global current2,clog_flag2
    for i in range(1):
        print("enter find_zero_pos")
        # motor_forward_angle(20,100)
        # time.sleep(1)
        # motor_forward_angle(80, 100)
        # time.sleep(1)
        motor_backward_angle2(120, 100)


def find_person_roaming():
    global roaming_stop_flag,last_angle1,last_angle2
    while True:
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break1")
            print("last_angle1,last_angle2:",last_angle1,last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break

        motor_forward_together2(-25, -18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break2")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, -18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break3")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(-25, -18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break4")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, -18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break5")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(-25, -18, 100)
        print("roaming_stop_flag:", roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break4")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, -18, 100)
        print("roaming_stop_flag:", roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break5")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(-25, 18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break6")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, 18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break7")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(-25, 18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break8")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, 18, 100)
        print("roaming_stop_flag:",roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break9")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(-25, 18, 100)
        print("roaming_stop_flag:", roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break8")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.8)
        motor_forward_together2(25, 18, 100)
        print("roaming_stop_flag:", roaming_stop_flag)
        if roaming_stop_flag == True:
            motor_stop()  # 停止第一个电机
            motor_stop2()  # 停止第二个电机
            time.sleep(0.1)
            print("enter find_person break9")
            print("last_angle1,last_angle2:", last_angle1, last_angle2)
            person_tracking_whole()
            print("finish tracking!!!!")
            break
        time.sleep(0.5)
    # print("start tracking!!!!")
    # motor_forward_together2(last_angle1,last_angle2, 70)



if __name__ == '__main__':
    # motor_forward_together2_no_break(0, 40, 100)

    motor_forward_together2_no_break(50, 120, 100)
    # time.sleep(1)
    find_zero_pos()
    motor_forward_together2_no_break(60, 0, 100)

    parser = argparse.ArgumentParser()
    parser.add_argument('--imgpath', type=str, default='/home/li/Downloads/YOLOv5-Lite/python_demo/onnxruntime/bus.jpg', help="image path")
    parser.add_argument('--modelpath', type=str, default='/home/li/Downloads/YOLOv5-Lite/models/v5lite-e.onnx', help="onnx filepath")
    parser.add_argument('--classfile', type=str, default='coco.names', help="classname filepath")
    parser.add_argument('--confThreshold', default=0.5, type=float, help='class confidence')
    parser.add_argument('--nmsThreshold', default=0.6, type=float, help='nms iou thresh')
    args = parser.parse_args()

    # motor_forward_together2_no_break(30, 0, 100)
    # print("f1")
    # motor_forward_together2_no_break(0, -20, 100)
    # print("f2")
    # time.sleep(20)
    # Open webcam
    # motor_reverse()
    # time.sleep(4)
    # motor_forward()
    # time.sleep(4)
    #
    # motor_reverse2()
    # time.sleep(4)
    # motor_forward2()
    # time.sleep(4)
    with open("motor_degree.txt", "w") as file_status:
        file_status.write(str(0))  # 更新第一个电机的角度
    with open("motor_degree2.txt", "w") as file_status:
        file_status.write(str(0))  # 更新第二个电机的角度



    net = yolov5_lite(args.modelpath, args.classfile, confThreshold=args.confThreshold, nmsThreshold=args.nmsThreshold)



    # 载入 MoveNet 模型
    # model_path = '/home/li/Downloads/Pose-detection/lite-model_movenet_singlepose_lightning_3.tflite'
    # interpreter = tf.lite.Interpreter(model_path=model_path)
    # interpreter.allocate_tensors()

    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 摄像头索引，0表示默认摄像头

    run_keypoint_main_thread= threading.Thread(target=run_keypoint_main)
    run_keypoint_main_thread.start()
    read_adc2_thread = threading.Thread(target=read_adc2)
    read_adc2_thread.start()
    read_adc_thread = threading.Thread(target=read_adc)
    read_adc_thread.start()
    # find_zero_pos()
    # person_tracking(5,0,100)
    # time.sleep(10)
    # motor_forward_angle2(angle=15, speed=100)
    # time.sleep(5)


    #
    # # for i in range(5):
    # #     motor_forward_together2(20, 0, 100)
    # #     time.sleep(3)
    # #     motor_forward_together2(0, 20, 100)
    # #     time.sleep(3)
    # #     motor_forward_together2(-20, 0, 100)
    # #     time.sleep(3)
    # #     motor_forward_together2(0, -20, 100)
    # #     time.sleep(3)
    #
    #
    #
    #
    # # time.sleep(3)
    # # for i in range(5):
    # #     person_tracking(-10,0,100)
    # #     time.sleep(2)
    #
    find_person_roaming_thread = threading.Thread(target=find_person_roaming)
    find_person_roaming_thread.start()
    #
    # time.sleep(5)







