import os

import threading
import pygame
import cv2
# from screeninfo import get_monitors

class Screen:

    def __init__(self):

        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((640, 480))
        self.screen_width, self.screen_height = self.screen.get_size()

        video_playing=False
        executed_once = False
        video_event = threading.Event()
        # video_path = '/home/li/listen2.mp4'
        video_path2 = '/home/li/speak_modify2.mp4'         ########screen_modified by lixiaolin ###
        # video_path2 = '/home/li/think2.mp4'
        video_path = '/home/li/breath_modify.mp4'            ########screen_modified by lixiaolin ###
        video_path3 = '/home/li/jelly_modify2.mp4'              ########screen_modified by lixiaolin ###
        # pygame.display.set_caption('Eye Animation')
        start_video_playback_flag=False

    def display(self, video_path, times = 3):
        cap = cv2.VideoCapture(video_path)

        if times == -1:
            times = 10000000
        for i in range(times):
            while cap.isOpened():
                ret, frame = cap.read()  # 读取一帧
                if not ret:  # 如果没有读取到帧，视频结束
                    print("End of video.")
                    return
                # 将 OpenCV 的帧转换为 pygame 可用的格式
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换颜色格式
                frame = pygame.surfarray.make_surface(frame)  # 转换为pygame surface
                # 旋转帧 90 度
                frame = pygame.transform.rotate(frame, -90)
                # 缩放帧以适应屏幕大小
                frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
                # 在 pygame 窗口中显示视频帧
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()

                # 每帧等待 40ms，相当于25帧/秒
                pygame.time.delay(5)

        cap.release()

    def start_video_playback(self):
        """ 在后台线程中播放视频 """
        global video_playing, flag_think, video_path, video_path2, flag_think2, video_path3
        print("enter start_video_playback!")
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
            print("Video playing!!!")
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
                frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
                # 在 pygame 窗口中显示视频帧
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()

                # 每帧等待 40ms，相当于25帧/秒
                pygame.time.delay(5)
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
        # video_event.set()
        print("Video playback finished.")
        cap.release()