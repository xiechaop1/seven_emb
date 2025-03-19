from base.messageid import messageid
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
from config.config import Config
import time


class Recv:

	EMPTY_SOUND_CODE = 400

	REC_METHOD_VOICE_CHAT = "voice-chat"
	REC_METHOD_VOICE_EXEC = "execute-command"

	REC_ACTION_SLEEP_ASSISTANT = "sleep_assistant"

	def __init__(self, ws, wsClient, audioPlayerIns, lightIns, cv2Ins):
		self.ws = ws
		self.wsClient = wsClient
		self.recv_daemon = True
		self.audio_player = audioPlayerIns
		self.light = lightIns
		self.cv2 = cv2Ins
		self.undertake = False

	def daemon(self):
		vc_handler = VoiceChat(self.audio_player)

		# self.wsClient.set_callback = ec_handler.undertake
		ec_handler = ExecuteCommand(self.audio_player, self.wsClient, self.cv2)

		last_resp = None
		msg_id_2_type = {}
		retry_ct = 0
		while True:
			if self.recv_daemon == False:
				break

			try:
				# response = self.ws.receive()
				response = self.wsClient.receive()
				# print(response)
			except (websocket.WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
				print(e)
				retry_ct += 1
				if retry_ct >= 3:
					self.undertake = True
				else:
					time.sleep(1)		# 3s以后重试
					continue

			resp = json.loads(response)
			# print(resp)

			if resp is not None:
				if resp["code"] == self.EMPTY_SOUND_CODE:
					print("Received empty sound code")
					self.audio_player.clear_interrupt()
					self.audio_player.replay()
					ThreadingEvent.recv_execute_command_event.set()
					# messageid.cover_with_last(Code.REC_METHOD_VOICE_CHAT)
					if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
						ThreadingEvent.camera_start_event.set()
					continue
				else:
					if resp["method"] == self.REC_METHOD_VOICE_CHAT:
						messageid.confirm_message_id(resp["method"])
						if Config.IS_DEBUG == False:
							self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 255, "g": 255, "b": 255})
							self.audio_player.set_current_light(Code.LIGHT_MODE_BREATHING)

						# 如果已经接到对应message_id的数据，同样的数据动作都是一致的
						# 为sleep-assistant做的处理
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
								# 进入助眠唤醒命令，会有一条 -1的结束，这条pass
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
							# self.audio_player.add(audio_data)
							# self.audio_player.resume_interrupted(None, 1)

							output_file_name = "resources/sound/enter_sleep_mode.mp3"
							print("play enter_sleep_mode!")
							self.audio_player.play_voice_with_file(output_file_name)
							last_resp = resp

						# ec_handler.latest_scene_seq = 0
						else:
							vc_thread = threading.Thread(target=vc_handler.deal, args=(resp,))
							vc_thread.start()
							# vc_handler.deal(resp)
						continue
					elif resp["method"] == Code.REC_METHOD_VOICE_EXEC:
						messageid.confirm_message_id(resp["method"])
						# self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 0, "b": 128})
						print("recv exec event:",ThreadingEvent.recv_execute_command_event.is_set(), resp["message_id"] )
						if ThreadingEvent.recv_execute_command_event.is_set():
							# print("recv event2:", ThreadingEvent.recv_execute_command_event)
							print("pre resp for exec", resp["message_id"])

							ec_thread = threading.Thread(target=ec_handler.deal, args=(resp,))
							ec_thread.start()
							# ec_handler.deal(resp)
						continue

