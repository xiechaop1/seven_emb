import json
import logging

from base.messageid import messageid
import base64
import uuid
import datetime
import time

from base.camera import Camera
from base.messageid import messageid
from common.threading_event import ThreadingEvent
from common.common import Common
from common.code import Code


class ExecuteCommand:

	def __init__(self, audioPlayerIns, ws, cv2):
		self.audio_player = audioPlayerIns
		self.latest_scene_seq = 0
		self.take_photo_max_ct = 3
		self.ws = ws
		self.cv2 = cv2
		self.camera = Camera(cv2)
		self.max_seq = 0

	def take_photo(self):
		while True:
			print("camera event: ", ThreadingEvent.camera_start_event.is_set())
			ThreadingEvent.camera_start_event.wait()
			# i = 0

			photo_list = []
			for i in range(self.take_photo_max_ct):
				photo = self.camera.take_photo(f"captured_image_{i}")
				if photo:
					photo_list.append(photo)
				if self.take_photo_max_ct > 1:
					time.sleep(1)

			self.commit(photo_list)
			time.sleep(0.5)


	def commit(self, photo_list):
		latest_played = self.audio_player.get_latest_played()
		conversation_id = messageid.get_conversation_id()
		message_id = messageid.generate(Code.REC_METHOD_VOICE_EXEC)
		token = messageid.get_token()

		status = ""
		scene_seq = 0
		if latest_played is not None:
			if latest_played["type"] == Code.REC_METHOD_VOICE_EXEC:
				seq_id = latest_played["seq_id"]
				scene_seq = latest_played["scene_seq"]
				voice_count = latest_played["voice_count"]

				if scene_seq < 100:
					if self.max_seq < scene_seq:
						if seq_id >= voice_count - 1:
							status = "COMPLETED"
							self.max_seq = scene_seq
						else:
							status = "IN_PROGRESS"
					else:
						status = ""
				else:
					status = ""

				print(status, scene_seq, seq_id, voice_count)

		request = {
			"version": "1.0",
			"method": "report-state",  # 始终使用 "report-state"
			"conversation_id": conversation_id,
			"message_id": message_id,
			"token": token,
			"timestamp": Common.get_rfc3339_with_timezone(),
			"data": {
				"images": {
					"format": "jpeg",
					"data": photo_list
				},
				"scene_exec_status": {
					"scene_seq": scene_seq,
					"status": status
				}
			}
		}

		self.ws.send(json.dumps(request))

		return

	def deal(self, resp):

		resp_msg_id = resp["message_id"]
		resp_conv_id = resp['conversation_id']

		scene_seq = resp["data"]["scene_seq"]

		voice_msg_id = messageid.get_latest_message_id()
		# print("resp_msg_id:", resp_msg_id)
		if voice_msg_id > resp_msg_id:
			# print("voice_msg_id, resp_msg_id:", voice_msg_id, resp_msg_id)
			logging.warn(f"Pass the old req, voice_msg_id: {voice_msg_id} > resp_msg_id: {resp_msg_id}")
			return


		# if self.latest_scene_seq == scene_seq:
		# 	return False

		add_seq_idx = 0 # 添加的index，比这个大的再添加


		# 过滤已经加入列表的数据中，如果场景一样的，就不加了
		audio_list = self.audio_player.get_audio_list()
		if len(audio_list) > 0:
			for curr_audio_list in audio_list:
				if curr_audio_list["type"] == Code.REC_METHOD_VOICE_EXEC:
					if scene_seq < 100 and curr_audio_list["scene_seq"] == scene_seq:
						logging.info(f"pass by audio_list: {curr_audio_list['scene_seq']}, {scene_seq}")
						return False


		# 过滤正在播放的数据，如果场景一样的，或者是对话的（因为对话不止一个请求），就不加了
		playing_data = self.audio_player.get_current_track()
		if playing_data is not None:
			if playing_data["type"] == Code.REC_METHOD_VOICE_EXEC:
				latest_playing_scene_seq = playing_data["scene_seq"]
				if latest_playing_scene_seq == scene_seq:
					logging.info(f"pass by playing_data: {latest_playing_scene_seq}, {scene_seq}")
					return False
			elif playing_data["type"] == Code.REC_METHOD_VOICE_CHAT:
				return False

		# 过滤已经播放的列表，从后面往前找，找到最后一条Execute-Command的，如果场景一致，则找到最后一个声频的index，记录下来
		# 如果场景不一致，并且过去的场景比现在的还靠后，那么现在的就不加了
		# 如果>100的异常场景，和最后一条一致的，也就不加了
		played_list = self.audio_player.get_played_list()
		if len(played_list) > 0:
			idx = 1
			while idx < len(played_list):
				latest_played = played_list[(-1 * idx)]
				if latest_played is not None:
					if latest_played["type"] == Code.REC_METHOD_VOICE_EXEC:
						logging.info("scene_seq: {latest_played['scene_seq']} {scene_seq}")
						if scene_seq < 100:
							if latest_played["scene_seq"] == scene_seq:
								add_seq_idx = latest_played["seq_id"]
							elif latest_played["scene_seq"] > scene_seq:
								return False
						elif scene_seq >= 100:
							if latest_played["scene_seq"] == scene_seq:
								return False
						break
				idx += 1
		# if self.latest_scene_seq == scene_seq:
		# 	logging.info(f"same seq with old: {self.latest_scene_seq} {scene_seq}")
		# 	return False
		print("add_seq_idx: ", add_seq_idx)

		# latest_played = self.audio_player.get_latest_played()
		# # latest_scene_seq = 0
		# if latest_played is not None:
		# 	if latest_played["type"] == Code.REC_METHOD_VOICE_EXEC:
		# 		latest_scene_seq = latest_played["scene_seq"]
		# 		# print("latest_scene_seq:", latest_scene_seq, scene_seq)
		# 		if latest_scene_seq < 100 and scene_seq < 100 and latest_scene_seq >= scene_seq:
		# 			return False
		# 		elif latest_scene_seq == scene_seq:
		# 			return False
		# 	elif latest_played["type"] == Code.REC_METHOD_VOICE_CHAT and self.audio_player.is_playing():
		# 		return False
		# 	# else:
		# 	# 	return False
		# else:
		# 	if self.latest_scene_seq == scene_seq:
		# 		return False

		if scene_seq > 100:
			self.audio_player.reset_interrupt(resp_msg_id, Code.REC_METHOD_VOICE_EXEC, 1)
			self.audio_player.clear_list()

		li_voice = resp["data"]["actions"]["voice"]

		fragrance = resp["data"]["actions"]["fragrance"]
		# print("fragrance:", fragrance)

		fragrance_status = "off"
		if fragrance is not None:
			fragrance_status = fragrance["status"]
			fragrance_level = fragrance["level"]
			fragrance_count = fragrance["count"]
			# print("fragrance_status:", fragrance_status)
			if fragrance_status is not None:
				if fragrance_status == "on":
					scent_spray_flag = True
				if fragrance_status == "off":
					scent_spray_flag = False
			# if fragrance_level is not None:
				# print("fragrance_level:", fragrance_level)
			# if fragrance_count is not None:
				# print("fragrance_count:", fragrance_count)

		bgm = resp["data"]["actions"]["bgm"]
		light = resp["data"]["actions"]["light"]

		# print(bgm)
		if li_voice is not None:
			# print("li_voice:", li_voice)

			li_voices_list = li_voice["voices"]
			print("len(li_voices_list):", len(li_voices_list))

			li_voices_list_len = len(li_voices_list)
			print("li_voices_list_len:", li_voices_list_len)
			for i in range(li_voices_list_len):
				# print("i:", i)
				if i == li_voices_list_len:
					seq_id = -1
				else:
					seq_id = i

				if seq_id < add_seq_idx and seq_id != -1:
					continue
				# li_audio_base64 = li_voices_list[i]["audio_data"]
				li_audio_fomat = li_voices_list[i]["audio_format"]
				# print("li_audio_fomat:", li_audio_fomat)
				# if li_audio_base64 != None:
				li_action = li_voices_list[i]["action"]
				# print("li_action:", li_action)
				li_wait_time = li_voices_list[i]["wait_time"]
				# print("li_wait_time:", li_wait_time)
				if li_wait_time is None:
					li_wait_time = 1
				li_audio_text = li_voices_list[i]["text"]
				print("li_audio_text:", li_audio_text)
				li_filename = li_voices_list[i]["filename"]
				print("li_filename:", li_filename, "appended!")
				output_file_name = "resources/sound/" + str(li_filename)
				audio_data = li_voices_list[i]
				audio_data["filename"] = output_file_name
				audio_data["scene_seq"] = scene_seq
				audio_data["seq_id"] = seq_id

				audio_data["spray"] = fragrance_status
				audio_data["bgm"] = bgm
				audio_data["msg_id"] = resp_msg_id
				audio_data["conversation_id"] = resp_conv_id
				audio_data["type"] = Code.REC_METHOD_VOICE_EXEC
				audio_data["voice_count"] = li_voices_list_len
				audio_data["wait_time"] = li_wait_time
				audio_data["light"] = light

				audio_data["continue"] = True # 设置标志位，打断以后，可以继续播放

				self.audio_player.resume_interrupted(None, 1)
				interrupt = self.audio_player.get_interrupt()
				if interrupt is None:
					self.audio_player.add(audio_data)

			self.latest_scene_seq = scene_seq

		return

