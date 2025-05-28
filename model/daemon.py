import threading
from datetime import time

from base.messageid import messageid
import logging
from common.common import Common
from common.threading_event import ThreadingEvent
from common.scence import Scence
from config.config import Config
import time

class Daemon:

	TURN_OFF_DURATION = 300   # (s)
 	NAP_DURATION = 30 #(s)

	def __init__(self, audio_ins, light_ins, spray_ins):
		self.light = light_ins
		self.spray = spray_ins
		self.audio_player = audio_ins

	def deal(self):

		while True:

			ThreadingEvent.wakeup_event.wait()

			latest_active_time = Common.get_latest_active_time()
			latest_voice_time = Common.get_latest_voice_time()
			now_time = time.time()

			duration = now_time - latest_active_time
			voice_duration = now_time - latest_voice_time
			if latest_voice_time > 0 and voice_duration > self.NAP_DURATION and ThreadingEvent.wakeup_event.is_set():
				logging.info(f"No activity detected for {voice_duration} seconds, over {self.NAP_DURATION} secs, taking a nap ...")
				self.nap()
			if latest_active_time > 0 and duration > self.TURN_OFF_DURATION:
				logging.info(f"Rest time over {self.TURN_OFF_DURATION} seconds, sleeping ..., duration: {duration}")
				# 超过时间没有活动（没有声音）
				self.sleep()

			time.sleep(10)

		return

	def nap(self):
		ThreadingEvent.wakeup_event.clear()
		Common.set_latest_voice_time(0)


	def sleep(self):
		Common.sleep(self.audio_player, self.light, self.spray)
		# Scence.scence = None
		# ThreadingEvent.audio_play_event.clear()
		# ThreadingEvent.camera_start_event.clear()
		# ThreadingEvent.spray_start_event.clear()
		# ThreadingEvent.recv_execute_command_event.clear()
		# ThreadingEvent.light_daemon_event.clear()
		# # ThreadingEvent.wakeup_event.clear()
		#
		# self.audio_player.stop_audio()
		# self.audio_player.stop_music()
		# self.audio_player.clear_list()
		# if Config.IS_DEBUG == False:
		# 	self.light.turn_off()
		# 	self.spray.turn_off()
		#
		# ThreadingEvent.wakeup_event.clear()




