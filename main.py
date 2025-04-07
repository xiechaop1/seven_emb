#from fastapi import FastAPI
#from fastapi.responses import FileResponse
#from fastapi.staticfiles import StaticFiles
#from config import settings, L
import logging

from base.ws import WebSocketClient
from base.mic import Mic
from base.audio_player import AudioPlayer
from base.motor import Motor
from config.config import Config
if not Config.IS_DEBUG:
    from base.light import Light
    from base.spray import Spray

from base.screen import Screen
if Config.OS is not None:
    if Config.OS == "pi5":
        from base.screen_pi5 import Screen


import os
import cv2
from threading import Event
import threading
from common.threading_event import ThreadingEvent
from model.recv import Recv
from model.daemon import Daemon
from common.code import Code
from common.common import Common
import pygame
import sys
import argparse
from model.undertake_callback import UndertakeCallback
import asyncio
import keyboard

#from base.spary import Spray
from model.execute_command import ExecuteCommand
#from base.spary import Spray

# async def main():
#     websocket_url = "ws://114.55.90.104:9001/ws"
#     client = WebSocketClient()
#
#     ws = await client.create_websocket_client(websocket_url)  # ✅ 连接 WebSocket
#     if ws:  # 连接成功
#         return ws

parser = argparse.ArgumentParser()
parser.add_argument('--mode', default="", type=str, help='demo mode without screen')
args = parser.parse_args()

# exec_tag = None
# if len(sys.argv) > 1:
#     exec_tag = sys.argv[1]


if Config.IS_DEBUG == False:
    os.environ["SDL_AUDIODRIVER"] = "alsa"
    hw = Common.find_audio_hw()
    os.environ["AUDIODEV"] = f"hw:{hw}"
    if Config.OS is not None:
        if Config.OS == "pi5":
            os.environ["AUDIODEV"] = "hw:2,0"

    os.environ["SDL_VIDEODRIVER"] = "x11"  ########screen_modified by lixiaolin ###
    # os.environ["SDL_VIDEODRIVER"] = "quartz"
    os.environ["DISPLAY"] = ":0"  ########screen_modified by lixiaolin ###
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"


if __name__ == "__main__":
    # on_start()
    # L.debug(f"API Listen {settings.LISTEN_IP}:{settings.PORT}")

    websocket_url = "ws://114.55.90.104:9001/ws"
    # ws_cli = asyncio.run(main())
    client = WebSocketClient(websocket_url)
    # client.set_callback(UndertakeCallback.undertake)
    ws_cli = client.connect()
    pygame.init()
    # exit(0)
    #ws_cli = WebSocketClient.create_websocket_client(websocket_url)
    # ws_instance = WebSocketClient()
    # ws_cli = await ws_instance.create_websocket_client(websocket_url)

    # ws_cli = ws_instance.get_client()

    cv2_instance = cv2.VideoCapture(0)

    if not Config.IS_DEBUG:
        # 暂时去掉，等上板子再试
        # spray_instance = ""
        spray_instance = Spray()
        spray_thread = threading.Thread(target=spray_instance.deal)
        spray_thread.start()

        spray_instance.turn_off()
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
    audio_play_thread.start()
    logging.info("audio is ready")

    if args.mode != "demo":
        screen_instance = Screen()
        screen_instance.add("resources/video/main.mp4", 100)
        screen_thread = threading.Thread(target=screen_instance.daemon)
        screen_thread.start()
        screen_instance.play()
    else:
        screen_instance = None

    motor_instance = Motor(cv2_instance)
    motor_instance.start()

    # screen = Screen()
    # screen.display("resources/video/think.mp4")

    mic_instance = Mic(client, audio_instance, light_instance, screen_instance)
    kaldi_thread = threading.Thread(target=mic_instance.kaldi_listener)
    kaldi_thread.start()

    # mic_thread = threading.Thread(target=mic_instance.daemon)
    # mic_thread.start()
    logging.info("Mic is ready")

    #
    recv_instance = Recv(ws_cli, client, audio_instance, light_instance, cv2_instance, screen_instance)
    recv_thread = threading.Thread(target=recv_instance.daemon)
    recv_thread.start()
    # logging.info("Starting receive websocket data ...")

    daemon_instance = Daemon(audio_instance, light_instance, spray_instance)
    daemon_thread = threading.Thread(target=daemon_instance.deal)
    daemon_thread.start()
    # 通过实例调用 create_websocket_client 方法
    # ws_cli = ws_instance.create_websocket_client(websocket_url)

 #    kaldi_listener_thread = threading.Thread(target=kaldi_listener)
	# kaldi_listener_thread.start()



