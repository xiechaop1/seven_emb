import cv2
import time
import numpy as np
import onnxruntime as ort
import math

class yolov5_lite():
    def __init__(self, moter_handler, model_pb_path, label_path, confThreshold=0.5, nmsThreshold=0.5,objThreshold=0.5):
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

        self.MAX_DISTANCE = 60
        self.moter_handler = moter_handler

        self.person_found_flag = False

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
        global x_diff,y_diff,roaming_stop_flag
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

                        if distance < self.MAX_DISTANCE:  # 如果两个人的距离小于阈值
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
                    print("person_found_flag:", self.person_found_flag)
                    self.moter_handler.motor_stop()  # 停止第一个电机
                    self.moter_handler.motor_stop2()  # 停止第二个电机
                    time.sleep(0.05)
                    roaming_stop_flag = True
                    if area>0:
                        self.person_found_flag=True
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