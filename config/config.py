# from common.code import Code
import os
import logging

# L = logging.getLogger(__name__)
# L.setLevel(logging.DEBUG)
# L.propagate = False  # 确保日志不会向上传递
#
# log_file = os.getenv('LOG_FILE', 'emb.log')
# handler = logging.FileHandler(log_file, encoding='utf-8')
# handler.setLevel(logging.DEBUG)
#
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s')
# handler.setFormatter(formatter)
#
# L.addHandler(handler)

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(threadName)s - %(module)s"
		   " - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(message)s",
	datefmt="%m/%d/%Y %I:%M:%S %p",
	# filename="./log/seven_emb.log",
	# filemode="a"
)

class Config:

	IS_DEBUG = False
	OS = None

	SPRAY_ON = True
	MOTOR_ON = False
	DEVICE_NAME = "Yundea A31-1"
	# DEVICE_NAME = "Yundea 1076"