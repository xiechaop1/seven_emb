from datetime import datetime
import sounddevice as sd
import re

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
		hw_idx = None
		# 遍历设备列表查找设备索引
		for i, device in enumerate(sd.query_devices()):
			if device_name in device['name'] and device['max_input_channels'] > 0:
				tmp = device['name']
				hw_idx = re.match(r"\(hw:(\d+)\)", tmp).group(1)
				break


		if hw_idx is None:
			raise ValueError(f"找不到匹配的设备 '{device_name}'")
		print(f"找到索引: {hw_idx} - {device_name}")
		return hw_idx