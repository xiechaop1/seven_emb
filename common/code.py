from gevent._tblib import Code


class Code:

	REC_METHOD_VOICE_CHAT = "voice-chat"
	REC_METHOD_VOICE_EXEC = "execute-command"

	REC_ACTION_SLEEP_ASSISTANT = "sleep_assistant"

	EXECUTE_COMMAND_TIP_VOICE = "execute-command-tip-voice"

	LIGHT_MODE_GRADIENT = "Gradient"
	LIGHT_MODE_BREATHING = "Breathing"
	LIGHT_MODE_STATIC = "Static"

	lightModelMap = {
		"Gradient": Code.LIGHT_MODE_BREATHING,
		"Static": Code.LIGHT_MODE_STATIC,
	}