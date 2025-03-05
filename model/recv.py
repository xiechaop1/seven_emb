from model.voice_chat import VoiceChat
from model.execute_command import ExecuteCommand
from websocket import WebSocketException, WebSocketConnectionClosedException
import json
import threading
import websocket
# from base.ws import WebSocketClient
from common.threading_event import ThreadingEvent
from common.scence import Scence
from common.code import Code


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

		last_resp = None
		msg_id_2_type = {}
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
					ThreadingEvent.recv_execute_command_event.set()
					continue
				else:
					if resp["method"] == self.REC_METHOD_VOICE_CHAT:
						if resp["message_id"] in msg_id_2_type:
							# method = msg_id_2_type[resp["message_id"]]["method"]
							act = msg_id_2_type[resp["message_id"]]["action"]
						else:
							# method = resp["method"]
							act = resp["data"]["action"]

						msg_id_2_type[resp["message_id"]] = {
							# "method": method,
							"action": act
						}
						# act = resp["data"]["action"]
						if act == Code.REC_ACTION_SLEEP_ASSISTANT:
							if resp['data']['stream_seq'] == -1:
								continue
							# 线程判断，如果已经启动线程，就不再启动
							# 需要处理 by choice
							tp_thread = threading.Thread(target=ec_handler.take_photo)
							# print(tp_thread)
							if not ThreadingEvent.camera_start_event.is_set() and not tp_thread.is_alive():
								# print(tp_thread)
								tp_thread.start()
							ThreadingEvent.camera_start_event.set()
							ThreadingEvent.recv_execute_command_event.set()

							Scence.scence = Code.REC_ACTION_SLEEP_ASSISTANT

							# print("sleep assistant", resp)

							if last_resp is not None:
								last_resp = None
								continue

							msg_id = resp["message_id"]
							resp_conv_id = resp["conversation_id"]
							output_file_name = "resources/sound/enter_sleep_mode.mp3"
							audio_data = {
								"filename": output_file_name,
								"msg_id": msg_id,
								"conversion_id": resp_conv_id,
								"type": Code.EXECUTE_COMMAND_TIP_VOICE,
								"wait_time": 0,
								"seq_id": -1
							}
							self.audio_player.clear_list()
							self.audio_player.add(audio_data)
							last_resp = resp

						# ec_handler.latest_scene_seq = 0
						else:
							vc_handler.deal(resp)
						continue
					elif resp["method"] == Code.REC_METHOD_VOICE_EXEC:
						print("recv event:",ThreadingEvent.recv_execute_command_event.is_set())
						if ThreadingEvent.recv_execute_command_event.is_set():
							# print("recv event2:", ThreadingEvent.recv_execute_command_event)
							ec_handler.deal(resp)
						continue

