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

	TURN_OFF_DURATION = 600   # (s)

	def __init__(self, audio_ins, light_ins, spray_ins):
		self.light = light_ins
		self.spray = spray_ins
		self.audio_player = audio_ins

	def deal(self):

		while True:

			ThreadingEvent.wakeup_event.wait()

			latest_active_time = Common.get_latest_active_time()
			now_time = time.time()

			duration = now_time - latest_active_time
			if latest_active_time > 0 and duration > self.TURN_OFF_DURATION:
				logging.info(f"Rest time over {self.TURN_OFF_DURATION} seconds, sleeping ..., duration: {duration}")
				# 超过时间没有活动（没有声音）
				self.sleep()

			time.sleep(10)

		return

	def sleep(self):
		Scence.scence = None
		ThreadingEvent.audio_play_event.clear()
		ThreadingEvent.camera_start_event.clear()
		ThreadingEvent.spray_start_event.clear()
		ThreadingEvent.recv_execute_command_event.clear()
		ThreadingEvent.light_daemon_event.clear()
		# ThreadingEvent.wakeup_event.clear()

		self.audio_player.stop_audio()
		self.audio_player.stop_music()
		self.audio_player.clear_list()
		if Config.IS_DEBUG == False:
			self.light.turn_off()
			self.spray.stop()

		ThreadingEvent.wakeup_event.clear()




