#from fastapi import FastAPI
#from fastapi.responses import FileResponse
#from fastapi.staticfiles import StaticFiles
#from config import settings, L
import logging

from base.ws import WebSocketClient
from base.mic import Mic
from base.audio_player import AudioPlayer
from config.config import Config
if not Config.IS_DEBUG:
    from base.light import Light
    from base.spray import Spray
else:
    from PyQt5.QtWidgets import QApplication
    from model import ui
    from base.screen import Screen
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
# from model.ui import ScenePage, HomePage, OverlayWidget, MainWindow
# if Config.OS != "lineage":
#     from PyQt5.QtWidgets import QApplication
#     from model import ui

os.environ["DISPLAY"] = ":0"  ########screen_modified by lixiaolin ###
if Config.OS == "lineage":
    os.environ["SDL_AUDIODRIVER"] = "pulse"
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

if args.mode != "demo" and args.mode != "show":
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
    keychar = key.char
    if key == keyboard.Key.esc or keychar == 'q' or keychar == 'c':
        print("exit")
        # motor_instance.motor_stop()
        # motor_instance.motor_stop2()
        sys.exit()
        # return False  # 停止监听

if __name__ == "__main__":
    print(f"Starting with mode {args.mode}")
    if Config.IS_DEBUG == True:
        if Config.OS == "lineage":
            pass
        else:
            if args.mode != "show":
                try:
                    app = QApplication(sys.argv)
                    window = gui.MainWindow()
                    window.show()
                    exit_code = app.exec_()
                    sys.exit(exit_code)
                except Exception as e:
                    print(e)
                    traceback.print_exc()

    # websocket_url = "ws://114.55.90.104:9001/ws"
    # if "WEBSOCKET_URL" in Config:
    if hasattr(Config, "WEBSOCKET_URL"):
        websocket_url = Config.WEBSOCKET_URL
    else:
        websocket_url = "ws://114.55.90.104:9001/ws"
    client = WebSocketClient(websocket_url)
    ws_cli = client.connect()
    pygame.init()

    cv2_instance = cv2.VideoCapture(0)
    
    #创建信号槽
    comm = Communicator()
    
    if not Config.IS_DEBUG:
        # 暂时去掉，等上板子再试
        # spray_instance = ""
        spray_instance = Spray()
        spray_thread = threading.Thread(target=spray_instance.deal)
        spray_thread.start()

        spray_instance.init_off(Spray.SPRAY_PIN)
        spray_instance.init_off(Spray.SPRAY_PIN2)
        spray_instance.init_off(Spray.SPRAY_PIN3)
        logging.info("spray initialized and turn off")
        #


        light_instance = Light()
        light_thread = threading.Thread(target=light_instance.daemon)
        light_thread.start()

        ThreadingEvent.light_daemon_event.clear()
        light_instance.turn_off()
        # light_instance.start(Code.LIGHT_MODE_WAVE, {"fore_color": [0, 0, 255]})
        # light_instance.start(Code.LIGHT_MODE_BREATHING, {"r":0, "g":0, "b":255, "steps": 200})
        # light_instance.start(Code.LIGHT_MODE_CIRCLE, {"r1": 0, "g1": 0, "b1": 255, "r2": 0, "g2": 255, "b2": 0, "time_duration": 100, "times": -1})
        light_instance.start(Code.LIGHT_MODE_SECTOR_FLOWING, {"mode": "colorful"})
        # light_instance.start(Code.LIGHT_MODE_CIRCLE_RAINBOW, {"mode": "colorful"})
        # light_instance.start(Code.LIGHT_MODE_RANDOM_POINT, {"fore_colors": [[0, 255, 0]], "back_colors": [[4, 0, 20]], "group_num": 1, "rand_num_per_groups": [1], "times": 100})
        # light_instance.start(Code.LIGHT_MODE_RANDOM_POINT,{"mode": "fire"})
        logging.info("light initialized")
    else:
        spray_instance = ""
        light_instance = ""

        # light_instance.set_mode(Code.LIGHT_MODE_BREATHING)

    # Intialize the library (must be called once before other functions).
    # strip.begin()

    # audio_event = threading.Event()
    audio_instance = AudioPlayer(spray_instance, light_instance)
    # audio_stop_thread = threading.Thread(target=audio_instance.audio_stop_event_daemon)
    # audio_stop_thread.start()
    audio_play_thread = threading.Thread(target=audio_instance.audio_play_event_daemon)
    # audio_play_thread.start()
    logging.info("audio is ready")

    if args.mode != "demo" and args.mode != "show":
        screen_instance = Screen()
        screen_instance.add("resources/video/main.mp4", 100)
        screen_thread = threading.Thread(target=screen_instance.daemon)
        screen_thread.start()
        screen_instance.play()

        if hasattr(Config, "MOTOR_ON"):
            if Config.MOTOR_ON == True:
                motor_instance = Motor(cv2_instance)
                motor_instance.start()
    else:
        screen_instance = None


    # screen = Screen()
    # screen.display("resources/video/think.mp4")

    mic_instance = Mic(client, audio_instance, light_instance, screen_instance, comm)
    kaldi_thread = threading.Thread(target=mic_instance.kaldi_listener)
    # kaldi_thread.start()

    # mic_thread = threading.Thread(target=mic_instance.daemon)
    # mic_thread.start()
    logging.info("Mic is ready")

    #
    recv_instance = Recv(ws_cli, client, audio_instance, light_instance, cv2_instance, screen_instance, spray_instance, comm)
    recv_thread = threading.Thread(target=recv_instance.daemon)
    # recv_thread.start()
    # logging.info("Starting receive websocket data ...")

    daemon_instance = Daemon(audio_instance, light_instance, spray_instance)
    daemon_thread = threading.Thread(target=daemon_instance.deal)
    # daemon_thread.start()
    # 通过实例调用 create_websocket_client 方法
    # ws_cli = ws_instance.create_websocket_client(websocket_url)

 #    kaldi_listener_thread = threading.Thread(target=kaldi_listener)
	# kaldi_listener_thread.start()
    # with keyboard.Listener(
    #         on_press=on_press,
    #         on_release=on_release) as listener:
    #     listener.join()
    
    # app = QApplication(sys.argv)
    # window = gui.MainWindow()
    # window.show()
    #对接槽接口   
    # comm.message.connect(window.messageHandler)
    audio_play_thread.start()
    kaldi_thread.start()
    recv_thread.start()
    daemon_thread.start()
    
    # sys.exit(app.exec_())

    

def signal_handler(sig, frame):
    print("Now exiting...")
    print("Stop motor")
    if motor_instance is not None:
        motor_instance.motor_stop()
        motor_instance.motor_stop2()
    print("Stop spray")
    if spray_instance is not None:
        spray_instance.turn_off()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
