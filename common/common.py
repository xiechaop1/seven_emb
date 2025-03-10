from datetime import datetime

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