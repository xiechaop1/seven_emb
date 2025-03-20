from model.voice_chat import VoiceChat
from model.execute_command import ExecuteCommand
from common.scence import Scence
from common.code import Code
import threading


class UndertakeCallback:


	def __init__(self, Exe):
		self.undertake_lock = threading.Lock()

		self.execute_command = ExecuteCommand()

		self.voice = VoiceChat()

	def undertake(self):
		if self.undertake_lock.acquire(False):
			if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
				ExecuteCommand.undertake()

		self.undertake_lock.release()


