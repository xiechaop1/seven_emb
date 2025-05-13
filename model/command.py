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

	def deal(self, device, operation, value):

		if device is not None:

			self.light.start_prev()
			if device == Code.REC_ACTION_PARAMS_DEVICE_VOLUME:
				if operation == Code.REC_ACTION_PARAMS_OPER_SOUND_MAIN:
					if value == Code.REC_ACTION_PARAMS_VALUE_UP:
						self.audio_player.set_back_volume_high()
						self.audio_player.set_front_volume_high()
					elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
						self.audio_player.set_back_volume_low()
						self.audio_player.set_front_volume_low()
					elif value == Code.REC_ACTION_PARAMS_VALUE_MUTE:
						self.audio_player.set_front_volume_low(0)
						self.audio_player.set_back_volume_low(0)
				elif operation == Code.REC_ACTION_PARAMS_OPER_VOICE:
					if value == Code.REC_ACTION_PARAMS_VALUE_UP:
						self.audio_player.set_front_volume_high()
					elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
						self.audio_player.set_front_volume_low()
					elif value == Code.REC_ACTION_PARAMS_VALUE_MUTE:
						self.audio_player.set_front_volume_low(0)
				elif operation == Code.REC_ACTION_PARAMS_OPER_BACKSOUND \
						or operation == Code.REC_ACTION_PARAMS_OPER_MUSIC:
					if value == Code.REC_ACTION_PARAMS_VALUE_UP:
						self.audio_player.set_back_volume_high()
					elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
						self.audio_player.set_back_volume_low()
					elif value == Code.REC_ACTION_PARAMS_VALUE_MUTE:
						self.audio_player.set_back_volume_low(0)
			elif device == Code.REC_ACTION_PARAMS_DEVICE_LIGHT:
				if operation == Code.REC_ACTION_PARAMS_OPER_BRIGHTNESS:
					if value == Code.REC_ACTION_PARAMS_VALUE_UP:
						self.light.set_high()
					elif value == Code.REC_ACTION_PARAMS_VALUE_DOWN:
						self.light.set_low()
				elif operation == Code.REC_ACTION_PARAMS_OPER_COLOR:
					if value == Code.REC_ACTION_PARAMS_VALUE_GREEN:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0}, Code.LIGHT_TYPE_DIY)
					elif value == Code.REC_ACTION_PARAMS_VALUE_RED:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 255, "g": 0, "b": 0}, Code.LIGHT_TYPE_DIY)
					elif value == Code.REC_ACTION_PARAMS_VALUE_BLUE:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 0, "b": 255}, Code.LIGHT_TYPE_DIY)
					elif value == Code.REC_ACTION_PARAMS_VALUE_YELLOW:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 255, "g": 255, "b": 0}, Code.LIGHT_TYPE_DIY)
					elif value == Code.REC_ACTION_PARAMS_VALUE_PURPLE:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 128, "g": 0, "b": 128}, Code.LIGHT_TYPE_DIY)
					elif value == Code.REC_ACTION_PARAMS_VALUE_WHITE:
						self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 255, "g": 255, "b": 255}, Code.LIGHT_TYPE_DIY)
			elif device == Code.REC_ACTION_PARAMS_DEVICE_FRAGRANCE:
				# 香氛
				if value == Code.REC_ACTION_PARAMS_VALUE_ON:
					self.spray.turn_on()
				else:
					self.spray.turn_off()
			elif device == Code.REC_ACTION_PARAMS_DEVICE_SYSTEM:
				if value == Code.REC_ACTION_PARAMS_VALUE_SLEEP:
					Common.sleep(self.audio_player, self.light, self.spray)

		self.audio_player.clear_interrupt()
		self.audio_player.replay()

		return


