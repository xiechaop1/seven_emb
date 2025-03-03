from model.voice_chat import VoiceChat
from model.execute_command import ExecuteCommand
from websocket import WebSocketException, WebSocketConnectionClosedException
import json
import threading
import websocket
# from base.ws import WebSocketClient
from common.threading_event import ThreadingEvent


class Recv:

	EMPTY_SOUND_CODE = 400

	REC_METHOD_VOICE_CHAT = "voice-chat"
	REC_METHOD_VOICE_EXEC = "execute-command"

	REC_ACTION_SLEEP_ASSISTANT = "sleep_assistant"

	def __init__(self, ws, wsClient, audioPlayerIns, cv2Ins):
		self.ws = ws
		self.wsClient = wsClient
		self.recv_daemon = True
		self.audio_player = audioPlayerIns
		self.cv2 = cv2Ins

	def daemon(self):
		vc_handler = VoiceChat(self.audio_player)
		ec_handler = ExecuteCommand(self.audio_player, self.ws, self.cv2)

		while True:
			if self.recv_daemon == False:
				break

			try:
				# response = self.ws.receive()
				response = self.wsClient.receive()
				# print(response)
			except (websocket.WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
				print(e)
				break

			resp = json.loads(response)
			# print(resp)

			if resp is not None:
				if resp["code"] == self.EMPTY_SOUND_CODE:
					self.audio_player.replay()
					continue
				else:
					if resp['method'] == self.REC_METHOD_VOICE_CHAT:
						act = resp["data"]["action"]
						if act == self.REC_ACTION_SLEEP_ASSISTANT:
							# 线程判断，如果已经启动线程，就不再启动
							# 需要处理 by choice
							tp_thread = threading.Thread(target=ec_handler.take_photo)
							# print(tp_thread)
							if not ThreadingEvent.camera_start_event.is_set() and not tp_thread.is_alive():
								# print(tp_thread)
								tp_thread.start()
							ThreadingEvent.camera_start_event.set()
						vc_handler.deal(resp)
						continue
					elif resp['method'] == self.REC_METHOD_VOICE_EXEC:
						ec_handler.deal(resp)
						continue

