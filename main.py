#from fastapi import FastAPI
#from fastapi.responses import FileResponse
#from fastapi.staticfiles import StaticFiles
#from config import settings, L
import logging

from base.ws import WebSocketClient
from base.mic import Mic
from base.audio_player import AudioPlayer
from config.config import Config
from GUI.guide import InitManager
if not Config.IS_DEBUG:
    from base.light import Light
    from base.spray import Spray
else:
    from PyQt5.QtWidgets import QApplication
    # from model import ui
    # from base.screen import Screen
if hasattr(Config, "OS"):
    if Config.OS == "pi5":
        from base.screen_pi5 import Screen

if hasattr(Config, "MOTOR_ON"):
    if Config.MOTOR_ON == True:
        from base.motor import Motor

import os
from common.threading_event import ThreadingEvent
from model.recv import Recv
from model.daemon import Daemon
from common.code import Code
from common.common import Common
from GUI import gui
# from model.ui import ScenePage, HomePage, OverlayWidget, MainWindow
# if Config.OS != "lineage":
#     from PyQt5.QtWidgets import QApplication
#     from model import ui

from datetime import time, datetime, timedelta
from model.scheduler import TaskDaemon
from model.task import Task, TaskType, TaskScheduleType, TaskStatus, TaskAction, SoundCommand
import json

os.environ["DISPLAY"] = ":0"  ########screen_modified by lixiaolin ###
if Config.OS == "lineage":
    os.environ["SDL_AUDIODRIVER"] = "pulse"
elif Config.OS == "Mac":
    os.environ["SDL_AUDIODRIVER"] = "coreaudio"
else:
    os.environ["SDL_AUDIODRIVER"] = "alsa"

if Config.IS_DEBUG == True:
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/usr/lib/qt5/plugins/platforms"
# hw_name = "Yundea 1076"
# hw_name = "Yundea A31-1"
if hasattr(Config, "DEVICE_NAME"):
    hw = Common.find_audio_hw(Config.DEVICE_NAME)
else:
    hw = Common.find_audio_hw()
os.environ["AUDIODEV"] = f"hw:{hw}"
# if Config.OS is not None:
#     if Config.OS == "pi5":
#         os.environ["AUDIODEV"] = "hw:2,0"
os.environ["SDL_VIDEODRIVER"] = "x11"  ########screen_modified by lixiaolin ###
os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

import cv2
from threading import Event
import threading
import pygame
import sys
import argparse
from model.undertake_callback import UndertakeCallback
import asyncio
# from pynput import keyboard
import signal
import traceback

#from base.spary import Spray
from model.execute_command import ExecuteCommand
#from base.spary import Spray
from PyQt5.QtCore import QObject, pyqtSignal
from GUI import gui

# async def main():
#     websocket_url = "ws://114.55.90.104:9001/ws"
#     client = WebSocketClient()
#
#     ws = await client.create_websocket_client(websocket_url)  # ✅ 连接 WebSocket
#     if ws:  # 连接成功
#         return ws

# 信号器：定义一个跨线程信号
class Communicator(QObject):
    message = pyqtSignal(str)

parser = argparse.ArgumentParser()
parser.add_argument('--mode', default="", type=str, help='demo mode without screen')
args = parser.parse_args()

if args.mode != "demo":
    from GUI import gui

if args.mode == "zero":
    cv2_instance = cv2.VideoCapture(0)
    motor_instance = Motor(cv2_instance)
    motor_instance.find_zero_pos()
    sys.exit(0)

# exec_tag = None
# if len(sys.argv) > 1:
#     exec_tag = sys.argv[1]


def on_press(key):
    try:
        print(f'{key.char} key pressed')
    except AttributeError:
        print(f'{key} key pressed')

def on_release(key):
    print(f'{key} key released')
    # keychar = key.char
    # if key == keyboard.Key.esc or keychar == 'q' or keychar == 'c':
    #     print("exit")
    #     # motor_instance.motor_stop()
    #     # motor_instance.motor_stop2()
    #     sys.exit()
    #     # return False  # 停止监听

if __name__ == "__main__":
    print(f"Starting with mode {args.mode}")

    # 创建信号槽
    comm = Communicator()
    
    # 创建初始化管理器
    init_manager = InitManager()
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    # 创建主窗口
    window = gui.MainWindow()
    window.show()
    
    # 检查是否需要显示引导页面
    if not init_manager.load_init_data():
        # 如果没有初始化数据，显示引导页面
        window.show_guide()
        print("Showing guide page")
    else:
        # 如果有初始化数据，直接显示主界面
        window.show_main_interface()
        print("Showing main interface")
        
    # 初始化 WebSocket 客户端
    websocket_url = "ws://114.55.90.104:9001/ws"
    client = WebSocketClient()
    ws = asyncio.run(client.create_websocket_client(websocket_url))
    
    # 初始化香氛
    if not Config.IS_DEBUG:
        spray_instance = Spray()
        spray_thread = threading.Thread(target=spray_instance.deal)
        spray_thread.start()
        spray_instance.turn_off()
        logging.info("spray initialized and turn off")
    else:
        spray_instance = None

    # 初始化灯光
    if not Config.IS_DEBUG:
        light_instance = Light()
        light_thread = threading.Thread(target=light_instance.daemon)
        light_thread.start()
        ThreadingEvent.light_daemon_event.clear()
        light_instance.turn_off()
        light_instance.start(Code.LIGHT_MODE_SECTOR_FLOWING, {"mode": "colorful"})
        logging.info("light initialized")
    else:
        light_instance = None

    # 初始化音频播放器
    audio_instance = AudioPlayer(spray_instance, light_instance)
    audio_play_thread = threading.Thread(target=audio_instance.audio_play_event_daemon)
    audio_play_thread.start()
    logging.info("audio is ready")

    # 初始化屏幕
    if args.mode != "demo":
        screen_instance = Screen()
        screen_instance.add("resources/video/main.mp4", 100)
        screen_thread = threading.Thread(target=screen_instance.daemon)
        screen_thread.start()
        screen_instance.play()
    else:
        screen_instance = None

    # 初始化麦克风
    mic_instance = Mic(client, audio_instance, light_instance, screen_instance)
    kaldi_thread = threading.Thread(target=mic_instance.kaldi_listener)
    kaldi_thread.start()
    logging.info("Mic is ready")

    # 初始化任务调度器
    task_daemon = TaskDaemon()
    task_thread = threading.Thread(target=task_daemon.start)
    task_thread.start()
    logging.info("Task scheduler initialized")
    
    
    # 对接槽接口
    comm.message.connect(window.messageHandler)
    
    # 启动应用程序
    sys.exit(app.exec_())


    # 添加任务到调度器
    # task_daemon.scheduler.add_task(task)

    # 获取所有任务
    # all_tasks = task_daemon.get_tasks()
    # print("Schedule List")
    # print(all_tasks)


    # 启动守护进程
    # task_thread = threading.Thread(target=task_daemon.start)


    # 添加任务到调度器
    # task_daemon.scheduler.add_task(task)

    # 获取所有任务
    # all_tasks = task_daemon.get_tasks()
    # print("Schedule List")
    # print(all_tasks)


    # 启动守护进程
    # task_thread = threading.Thread(target=task_daemon.start)

