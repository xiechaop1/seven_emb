from base.messageid import messageid
from model.voice_chat import VoiceChat
from model.execute_command import ExecuteCommand
from model.command import Command
from websocket import WebSocketException, WebSocketConnectionClosedException
import json
import threading
import websocket
# from base.ws import WebSocketClient
from common.threading_event import ThreadingEvent
from common.scence import Scence
from common.code import Code
from config.config import Config
import time


class Interface:

	def __init__(self, ws, wsClient, audioPlayerIns, lightIns, cv2Ins, screenIns, sprayIns):
		self.ws = ws
		self.ws_client = wsClient
		self.recv_daemon = True
		self.audio_player = audioPlayerIns
		self.light = lightIns
		self.cv2 = cv2Ins
		self.screen = screenIns
		self.spray = sprayIns

		self.ec_handler = ExecuteCommand(self.audio_player, self.ws_client, self.cv2)
		self.co_handler = Command(self.audio_player, self.light, self.spray, self.ws_client, self.cv2)
		# self.vc_handler = VoiceChat(self.audio_player)

	def sleep_assistant(self):
		last_resp = None
		# ec_handler = ExecuteCommand(audio_player, ws_client, cv2)
		# 线程判断，如果已经启动线程，就不再启动
		# 需要处理 by choice
		tp_thread = threading.Thread(target=self.ec_handler.take_photo)
		# print(tp_thread)
		if not ThreadingEvent.camera_start_event.is_set() and not tp_thread.is_alive():
			# print(tp_thread)
			tp_thread.start()
		ThreadingEvent.camera_start_event.set()
		ThreadingEvent.recv_execute_command_event.set()

		Scence.scence = Code.REC_ACTION_SLEEP_ASSISTANT

		# print("sleep assistant", resp)

		# msg_id = resp["message_id"]
		# resp_conv_id = resp["conversation_id"]
		# output_file_name = "resources/sound/enter_sleep_mode.mp3"
		# audio_data = {
		# 	"filename": output_file_name,
		# 	"msg_id": msg_id,
		# 	"conversion_id": resp_conv_id,
		# 	"type": Code.EXECUTE_COMMAND_TIP_VOICE,
		# 	"wait_time": 0,
		# 	"seq_id": -1
		# }
		self.audio_player.clear_list()
		self.audio_player.stop_audio()
		self.audio_player.clear_interrupt()
		# self.audio_player.add(audio_data)
		# self.audio_player.resume_interrupted(None, 1)

	def command(self, device, operation, value):
		co_handler = Command(self.audio_player, self.light, self.spray, self.ws_client, self.cv2)
		co_thread = threading.Thread(target=co_handler.deal, args=(device,operation,value,))
		co_thread.start()


