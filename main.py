from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
#from config import settings, L
from base.ws import WebSocketClient
from base.mic import Mic
from base.audio_player import AudioPlayer
from threading import Event
import threading
from common.threading_event import ThreadingEvent
from model.recv import Recv
import asyncio
import cv2

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


if __name__ == "__main__":
    # on_start()
    # L.debug(f"API Listen {settings.LISTEN_IP}:{settings.PORT}")

    websocket_url = "ws://114.55.90.104:9001/ws"
    # ws_cli = asyncio.run(main())
    client = WebSocketClient(websocket_url)
    ws_cli = client.connect()
    # exit(0)
    #ws_cli = WebSocketClient.create_websocket_client(websocket_url)
    # ws_instance = WebSocketClient()
    # ws_cli = await ws_instance.create_websocket_client(websocket_url)

    # ws_cli = ws_instance.get_client()

    # 暂时去掉，等上板子再试
    spray_instance = ""
    # spray_instance = Spray()
    # # spray_thread = threading.Thread(target=spray_instance.deal())
    # # spray_thread.start()
    #

    cv2_instance = cv2.VideoCapture(0)

    # audio_event = threading.Event()
    audio_instance = AudioPlayer(spray_instance)
    audio_stop_thread = threading.Thread(target=audio_instance.audio_stop_event_daemon)
    audio_stop_thread.start()
    audio_play_thread = threading.Thread(target=audio_instance.audio_play_event_daemon)
    audio_play_thread.start()

    mic_instance = Mic(ws_cli, audio_instance)
    mic_thread = threading.Thread(target=mic_instance.daemon)
    mic_thread.start()
    print("mic is ready")

    #
    recv_instance = Recv(ws_cli, client, audio_instance, cv2_instance)
    recv_thread = threading.Thread(target=recv_instance.daemon)
    recv_thread.start()


    # 通过实例调用 create_websocket_client 方法
    # ws_cli = ws_instance.create_websocket_client(websocket_url)

 #    kaldi_listener_thread = threading.Thread(target=kaldi_listener)
	# kaldi_listener_thread.start()

	


