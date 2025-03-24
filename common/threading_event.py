import threading

class ThreadingEvent:

	audio_stop_event = threading.Event()
	audio_play_event = threading.Event()
	audio_playing_event = threading.Event()
	camera_start_event = threading.Event()
	spray_start_event = threading.Event()
	recv_execute_command_event = threading.Event()
	light_daemon_event = threading.Event()
	screen_daemon_event = threading.Event()

	wakeup_event = threading.Event()

	execute_command_undertake = threading.Event()

	interrupt_lock = None

	# interrupt_lock = threading.Lock()

	# sleep_daemon_event = threading.Event()