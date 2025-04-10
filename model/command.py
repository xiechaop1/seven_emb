import json
import logging
import traceback

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
import threading


class Command:


	MAX_SCENE = 6	# 最大场景ID

	def __init__(self, audioPlayerIns, light, spray, ws, cv2):
		self.audio_player = audioPlayerIns
		self.light = light
		self.spray = spray
		self.ws = ws
		self.cv2 = cv2

	def deal(self, resp):

		resp_msg_id = resp["message_id"]
		resp_conv_id = resp['conversation_id']

		scene_seq = resp["data"]["scene_seq"]

		action = resp["data"]["action"]


		params = resp["data"]["action_params"]
		device = None
		operation = None
		value = None
		if params is not None:
			if "device" in params:
				device = params["device"]
			if "operation" in params:
				operation = params["operation"]
			if "value" in params:
				value = params["value"]

		print("dov", device, operation, value)

		if device == Code.REC_ACTION_PARAMS_DEVICE_VOLUME:
			if operation == Code.REC_ACTION_PARAMS_OPER_SOUND_MAIN:
				if value == Code.REC_ACTION_PARAMS_VALUE_UP:
					self.audio_player.set_back_volume_high()
					self.audio_player.set_front_volume_high()
				elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
					print("a")
					self.audio_player.set_back_volume_low()
					self.audio_player.set_front_volume_low()
			elif operation == Code.REC_ACTION_PARAMS_OPER_VOICE:
				if value == Code.REC_ACTION_PARAMS_VALUE_UP:
					self.audio_player.set_front_volume_high()
				elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
					self.audio_player.set_front_volume_low()
			elif operation == Code.REC_ACTION_PARAMS_OPER_BACKSOUND \
					or operation == Code.REC_ACTION_PARAMS_OPER_MUSIC:
				if value == Code.REC_ACTION_PARAMS_VALUE_UP:
					self.audio_player.set_back_volume_low()
				elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
					self.audio_player.set_back_volume_low()
		elif device == Code.REC_ACTION_PARAMS_DEVICE_LIGHT:
			if operation == Code.REC_ACTION_PARAMS_OPER_BRIGHTNESS:
				if value == Code.REC_ACTION_PARAMS_VALUE_UP:
					self.light.set_high()
				elif params == Code.REC_ACTION_PARAMS_VALUE_DOWN:
					self.light.set_low()
		elif device == Code.REC_ACTION_PARAMS_DEVICE_SYSTEM:
			if value == Code.REC_ACTION_PARAMS_VALUE_SLEEP:
				Common.sleep(self.audio_player, self.light, self.spray)

		return


