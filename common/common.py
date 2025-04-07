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