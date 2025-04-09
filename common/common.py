from datetime import datetime
import sounddevice as sd
import re
from common.threading_event import ThreadingEvent
from common.scence import Scence
from config.config import Config

class Common:

	latest_active_time = 0

	@staticmethod
	def __init__():
		pass

	@staticmethod
	def get_rfc3339_with_timezone():
	    # tz = pytz.timezone('Asia/Shanghai')
	    return datetime.now().isoformat()

	@staticmethod
	def get_latest_active_time():
	    return Common.latest_active_time

	@staticmethod
	def set_latest_active_time(time):
		Common.latest_active_time = time
		return True;

	@staticmethod
	def find_audio_hw(device_name = "Yundea 1076"):
		hw = None
		# 遍历设备列表查找设备索引
		for i, device in enumerate(sd.query_devices()):
			if device_name in device['name'] and device['max_input_channels'] > 0:
				tmp = device['name']
				hw_idx = re.findall(r"\(hw:(\d+,\d+)", tmp)
				if hw_idx is not None:
					hw = hw_idx[0]
				print(f"找到索引: {hw} - {device_name}")
				break


		if hw is None:
			hw = "1,0"
		return hw

	@staticmethod
	def get_params_from_act(action, format = None):
		if format is None:
			format = r"(\w+)\[(\w+)]"

		ret = re.findall(format, action)

		return ret

	@staticmethod
	def sleep(audio_player, light = None, spray = None):
		Scence.scence = None
		ThreadingEvent.audio_play_event.clear()
		ThreadingEvent.camera_start_event.clear()
		ThreadingEvent.spray_start_event.clear()
		ThreadingEvent.recv_execute_command_event.clear()
		ThreadingEvent.light_daemon_event.clear()
		# ThreadingEvent.wakeup_event.clear()

		audio_player.stop_audio()
		audio_player.stop_music()
		audio_player.clear_list()
		if Config.IS_DEBUG == False:
			if light is not None:
				light.turn_off()
			if spray is not None:
				spray.turn_off()

		ThreadingEvent.wakeup_event.clear()