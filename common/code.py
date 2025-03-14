# from common.code import Code


class Code:

	REC_METHOD_VOICE_CHAT = "voice-chat"
	REC_METHOD_VOICE_EXEC = "execute-command"

	REC_ACTION_SLEEP_ASSISTANT = "sleep_assistant"

	EXECUTE_COMMAND_TIP_VOICE = "execute-command-tip-voice"

	LIGHT_MODE_GRADIENT = "Gradient"
	LIGHT_MODE_BREATHING = "Breathing"
	LIGHT_MODE_CIRCLE = "Circle"
	LIGHT_MODE_CIRCLE_RAINBOW = "CircleRainbow"
	LIGHT_MODE_STATIC = "Static"

	@staticmethod
	def lightModelMap():
		return {
			"Gradient": Code.LIGHT_MODE_BREATHING,
			"Static": Code.LIGHT_MODE_GRADIENT,
			"Circle": Code.LIGHT_MODE_CIRCLE,
			"CircleRainbow": Code.LIGHT_MODE_CIRCLE_RAINBOW,
		}
		
