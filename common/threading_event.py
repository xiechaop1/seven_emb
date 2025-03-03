import threading

class ThreadingEvent:

	audio_stop_event = threading.Event()
	audio_play_event = threading.Event()

	camera_start_event = threading.Event()

	spray_start_event = threading.Event()