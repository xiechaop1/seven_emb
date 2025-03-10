import threading

from base.messageid import messageid
from common.code import Code
import logging
import base64

class VoiceChat:


	def __init__(self, audioPlayerIns):
		self.audio_player = audioPlayerIns
		self.file_counter = 0
		self.exec_lock = threading.Lock()

	def deal(self, resp):

		resp_msg_id = resp["message_id"]
		resp_conv_id = resp['conversation_id']

		msg_id = messageid.get_latest_message_id()

		if resp_msg_id != msg_id:
			logging.warn(f"Pass voice old req, resp_msg_id: {resp_msg_id}, msg_id: {msg_id}")
			# print("resp_msg_id, msg_id", resp_msg_id, msg_id)
			return

		if self.exec_lock.acquire():

			self.audio_player.reset_interrupt(msg_id, Code.REC_METHOD_VOICE_CHAT, 2)

			seq_li = resp["data"]["stream_seq"]
			if seq_li == 1:
				# 第一条数据之前清除列表
				self.audio_player.clear_list()

			resp_format = resp["data"]["audio_format"]
			audio_base64 = resp["data"]["audio_data"]
			# tmp_resp = resp
			# del tmp_resp["data"]["audio_data"]
			# print(tmp_resp)
			audio_data = None
			if audio_base64 != None:
				audio_bytes = base64.b64decode(audio_base64)
				response_text = resp["data"]["text"]
				print("response_text:", response_text)
				# self.file_counter += 1  # 递增文件计数器
				self.file_counter = seq_li
				flag_think2 = False
				if str(resp_format) == 'mp3':
					# msg_id = messageid.get_latest_message_id()
					# output_file_name = f"/home/li/vosk-api/python/example/send_pcm_folder/{msg_id}_{file_counter}.mp3"
					# with open(output_file_name, "wb") as pcm_file:
					# 	pcm_file.write(audio_bytes)
					output_file_name = self.audio_player.save(audio_bytes, f"{msg_id}_{self.file_counter}")
					audio_data = {
						"filename": output_file_name,
						"msg_id": msg_id,
						"conversion_id": resp_conv_id,
						"type":resp["method"],
						"wait_time":0,
						"seq_id":seq_li
					}
					# print("audio_data:", audio_data)
					# self.audio_player.add(audio_data)
			elif seq_li == -1:
				audio_data = {
					"filename": "",
					"msg_id": msg_id,
					"conversion_id": resp_conv_id,
					"type": resp["method"],
					"wait_time": 0,
					"seq_id": seq_li
				}

			if audio_data is not None:
				# print("audio_data:", audio_data)
				self.audio_player.add(audio_data)
				self.audio_player.resume_interrupted(msg_id, 2)

			self.exec_lock.release()

		return

