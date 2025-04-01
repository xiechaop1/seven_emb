import logging
import os

import threading
from operator import contains

import pygame
import pygame_gui
import cv2
import av
import datetime
import time
from config.config import Config

if Config.OS is not None:
    if Config.OS == "pi5":
        import mpv
from common.threading_event import ThreadingEvent
# from screeninfo import get_monitors

class Screen:

    HARD_ACC = 'v4l2'
    # HARD_ACC = 'v4l2_request'
    # HARD_ACC = 'omx'

    def __init__(self):

        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((640, 480), pygame.SCALED)
        self.manager = pygame_gui.UIManager((640, 480))

        self.screen_width, self.screen_height = self.screen.get_size()

        self.current_video = None
        self.play_list = []
        self.fade_out_step = 0
        self.interrupt_event = threading.Event()
        self.clock = pygame.time.Clock()
        self.time_delta = self.clock.tick(30)
        self.running = True
        if Config.OS is not None:
            if Config.OS == "pi5":
                self.mpv_player = mpv.MPV(log_handler=print)
                self.mpv_player.vo = "gpu"
                self.mpv_player.hwdec = "drm"
                self.mpv_player.fps = 30
                self.mpv_player.fullscreen = False


    def add(self, video_path, times):
        self.play_list.append({
            "video_path": video_path,
            "times": times
        })
        logging.info(f"Added video {video_path}")

    def pause(self):
        self.mpv_player.pause = True

    def clear_list(self):
        self.play_list = []
        logging.info(f"Clear video list")

    def stop(self):
        # self.screen.stop()
        self.interrupt_event.clear()
        self.running = False
        time.sleep(0.5)
        logging.info(f"Stopped video list")

    def daemon(self):
        clock_thread = threading.Thread(target=self.update_clock, daemon=True)
        clock_thread.start()

        while True:
            ThreadingEvent.screen_daemon_event.wait()

            play_video = None
            if len(self.play_list) > 0:
                play_video = self.play_list.pop(0)
            if play_video is None:
                logging.warning("No video")
                ThreadingEvent.screen_daemon_event.clear()
                continue
            logging.info("Getting video %s", play_video["video_path"])
            video_path = play_video["video_path"]
            times = play_video["times"]

            self.interrupt_event.wait()
            self.display(video_path, times)
            # self.play()

    def playlist(self):
        self.stop()
        self.interrupt_event.set()
        self.running = True
        self.play()
    # def playlist(self):
    #     for _, play_video in enumerate(self.play_list):
    #
    #         video_path = play_video["video_path"]
    #         times = play_video["times"]
    #
    #         self.interrupt_event.wait()
    #         self.display(video_path, times)

    def play(self):
        self.stop()
        self.mpv_player.pause = False
        ThreadingEvent.screen_daemon_event.set()
        self.interrupt_event.set()
        self.running = True

    def update_clock(self):
        pygame.freetype.init()
        font = pygame.freetype.SysFont("Arial", 80)
        font_color = (255, 255, 255)
        while True:
            self.screen.fill((0, 0, 0, 0))
            now = datetime.datetime.now()
            time_text = now.strftime("%H:%M")
            date_text = now.strftime("%m-%d %A")
            font.render_to(self.screen, (self.screen_width // 3, self.screen_height // 3), time_text, font_color)
            font.render_to(self.screen, (self.screen_width // 3, self.screen_height // 3 + 100), date_text, font_color)
            pygame.display.update()
            time.sleep(1)

    def display(self, video_path, times):

        font_path = "/usr/local/lib/python3.9/dist-packages/pygame_gui/data/NotoSans-Regular.ttf"
        if Config.OS is not None:
            if Config.OS == "pi5":
                font_path = "/usr/local/lib/python3.11/dist-packages/pygame_gui/data/NotoSans-Regular.ttf"
        # font = pygame.font.Font(font_path, 80)
        # clock_label = pygame_gui.elements.UILabel(
        #     relative_rect=pygame.Rect((self.screen_width // 2 - 200, self.screen_height - 120), (120, 100)),
        #     text="",
        #     manager=self.manager
        # )
        if times == -1:
            times = 10000000
        if Config.OS is None:
            container = av.open(video_path, options={'hwaccel': self.HARD_ACC})

            stream = next(s for s in container.streams if s.type == 'video')
            # for i in range(times):
            frame_generator = container.decode(stream)
        curr_times = 0
        font_large = pygame.font.Font(font_path, 50)  # 第一行：时间
        font_small = pygame.font.Font(font_path, 50)  # 第二行：日期
        if Config.OS is not None:
            if Config.OS == "pi5":
                self.mpv_player.play(video_path)

        else:
            while self.running:
                if not self.interrupt_event.is_set():
                    break

                if Config.OS is None:
                    try:
                        frame = next(frame_generator)
                        img = frame.to_ndarray(format="bgr24")
                        img = pygame.surfarray.make_surface(img.swapaxes(0, 1))
                        img = pygame.transform.scale(img, (self.screen_width, self.screen_height))
                        self.screen.blit(img, (0, 0))
                    except StopIteration:
                        curr_times += 1
                        if curr_times > times:
                            break
                        # 视频播放结束后重新播放
                        container.seek(0)
                        frame_generator = container.decode(stream)
                # else:
                #     self.mpv_player.play(video_path)

                # 更新时钟
                # current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # text_surface = font.render(current_time, True, (255, 255, 255))  # 白色字体
                # text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))  # 居中
                now = datetime.datetime.now()
                time_text = now.strftime("%H:%M")  # 小时:分钟
                date_text = now.strftime("%m-%d %a")  # 月-日 星期

                # 渲染时间（第一行）
                time_surface = font_large.render(time_text, True, (255, 255, 255))  # 白色
                time_rect = time_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 150))
                self.screen.blit(time_surface, time_rect)

                # 渲染日期（第二行）
                date_surface = font_small.render(date_text, True, (255, 255, 255))  # 白色
                date_rect = date_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
                # clock_label.set_text(current_time)
                self.screen.blit(date_surface, date_rect)

                # 更新 Pygame GUI
                self.manager.update(self.time_delta)
                self.manager.draw_ui(self.screen)

                # 刷新显示
                pygame.display.flip()
                # container.seek(0)
                # for frame in container.decode(stream):
                #     if not self.interrupt_event.is_set():
                #         break
                #     img = frame.to_ndarray(format="bgr24")
                #     img_resized = cv2.resize(img, (self.screen_width, self.screen_height))
                #     surf = pygame.surfarray.make_surface(img_resized.swapaxes(0, 1))
                #     self.screen.blit(surf, (0, 0))
                #     pygame.display.flip()
                    # clock.tick(30)
            container.close()
            logging.info(f"Finished video {video_path}")

        # pygame.quit()


    def displayX11(self, video_path, times = 3):
        cap = cv2.VideoCapture(video_path)
        logging.info(f"Screen display start, filename: {video_path}, times: {times}, isOpened: {cap.isOpened()}")

        clock = pygame.time.Clock()
        alpha = 255

        if not cap.isOpened():
            return False

        if times == -1:
            times = 10000000
        for i in range(times):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
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
                frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
                # 在 pygame 窗口中显示视频帧
                self.screen.blit(frame, (0, 0))
                pygame.display.flip()

                # 每帧等待 40ms，相当于25帧/秒
                # self.clock.tick(60)
                # pygame.time.delay(1)

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