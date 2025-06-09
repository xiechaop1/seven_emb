import os

# os.environ["SDL_AUDIODRIVER"] = "alsa"
# os.environ["AUDIODEV"] = "hw:3,0"

import wave
import time
import webrtcvad
import logging
import numpy as np
import pyaudio
import sounddevice as sd
import collections
from collections import deque
import queue
import io
from base.messageid import messageid
from common.threading_event import ThreadingEvent
from common.common import Common
from common.scence import Scence
from common.code import Code
from config.config import Config
import base64
from websocket import WebSocketException, WebSocketConnectionClosedException
from datetime import datetime
import uuid
import json
from vosk import Model, KaldiRecognizer, SpkModel
from scipy import signal
# from GUI.gui import Communicator


class Mic:
    """麦克风控制类，负责录音和语音活动检测（VAD）"""

    # 定义帧大小
    # SAMPLERATE_ORIG = 48000#44100  # 原始采样率（您的麦克风采样率）
    SAMPLERATE_ORIG = 16000
    SAMPLERATE_TARGET = 16000  # 目标采样率（VAD支持）
    FRAME_DURATION = 30  # ms
    # FRAME_SIZE = int(16000 * FRAME_DURATION / 1000)  # assuming 16kHz sample rate
    BUFFER_DURATION = 300  # mss
    # SAMPLE_RATE = 44100  # 采样率
    SAMPLE_RATE = 16000  # 采样率
    CHANNELS = 1  # 单声道

    SILENCE_THRESHOLD = 200  # 静音阈值
    SILENCE_FRAMES = 4  # 静音帧数量阈值
    PRE_RECORD_FRAMES = 1  # 预录制帧数
    # 定义队列和缓冲区

    MAX_RETRIES = 3

    # VOLUME_THRESHOLD = 200

    SPK_MODEL_PATH = "utils/vosk-model-spk-0.4"
    MODEL_PATH = "utils/vosk-model-small-cn-0.22"

    # SPK_MODEL_PATH = "/home/li/vosk-api/python/example/vosk-model-spk-0.4"
    # model_path = "/home/li/vosk-model-small-cn-0.22"

    def __init__(self, ws, audio_player, light, screen, communicator, threshold=800, timeout=30, sample_rate=16000, frame_duration=30):
        """
        初始化麦克风参数
        :param threshold: 静音检测阈值（音频幅度超过该值视为非静音）
        :param timeout: 录音超时（秒），超过此时间自动停止录音
        :param sample_rate: 采样率，默认为16000
        :param frame_duration: 每帧的时长（毫秒），默认为30ms
        """
        self.threshold = self.SILENCE_THRESHOLD
        self.timeout = timeout
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.p = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(0)  # VAD模式设置，0为最宽松，3为最严格
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_status = "Waiting"
        self.filename = "temp_audio.wav"

        self.de_frames = collections.deque(maxlen=int(self.BUFFER_DURATION / self.FRAME_DURATION))
        self.pre_buffer = deque(maxlen=self.PRE_RECORD_FRAMES)  # 环形缓冲区，用于保存开头静音

        self.audio_data_queue = queue.Queue()
        self.handler_interrupt = True
        self.silence_counter = 0
        self.slience_tag = True

        self.ws = ws
        self.audio_player = audio_player
        self.light = light
        self.screen = screen
        # self.req_send_time = 0

        self.spk_li_1 = [-0.626114, 0.430365, 0.564255, -0.182698, 0.537145, 0.044097, 0.564515, 0.666896, 1.085733,
                         -0.523695, 2.178851, -0.545808, 0.492513, -0.214256, 0.380257, 0.561458, 1.432191, 0.576447,
                         1.347584, -1.410213, -0.201343, 1.299883, 0.16591, -0.301386, 1.030398, -0.155679, 1.668122,
                         -0.47749, 1.583658, 1.031789, -0.610194, 0.207826, -2.028657, -0.778005, 0.608732, -1.103482,
                         -0.249394, -0.145279, -0.252108, -0.744611, -0.178013, 0.821876, 1.348644, 0.958709, -1.489057,
                         -0.069446, 0.55689, 0.382191, 1.793885, 0.12014, 1.096465, 1.948748, -0.288994, -0.427686,
                         -0.25332, -0.74351, 1.289284, -0.442085, -1.594271, 0.238896, -0.14475, -1.243948, -0.811971,
                         -1.167681, -1.934597, -2.094246, 0.203778, 0.2246, 0.769156, 3.129627, 1.638138, -0.414724,
                         0.363555, 1.058113, -0.658691, 0.345854, -1.559133, 0.087666, 0.984442, -0.469354, 1.667347,
                         0.916898, -2.170697, 0.292812, 0.051197, 1.222564, 1.065773, -0.065279, 0.214764, -0.407425,
                         0.992222, -0.993893, 0.693716, 0.121084, 1.31698, 1.255295, -0.941613, 0.015467, 0.500375,
                         -1.479744, -0.943895, -0.405701, 1.795941, -0.66203, 1.224589, 0.963079, -0.872087, 0.392804,
                         1.412374, -0.279257, -0.462107, 0.674435, 0.137653, 0.93439, 2.394885, -0.571315, 0.374555,
                         -0.233448, 0.757664, -0.375494, 0.666074, -0.123803, 1.518769, 0.873773, -0.218161, 1.566089,
                         -0.488127, 0.386693]
        self.keywords = '["播放音乐", "七七", "停止", "抬头", "拍照","休息","[unk]"]'
        self.target_keywords = ["播放音乐", "七七", "停止", "抬头", "拍照", "休息", "Yuyu", "Test"]
        # self.wakeup_keywords = '["七七", "七宝", "七夕", "休息", "嘻嘻"]'
        self.wakeup_keywords = '["播放音乐", "七七", "停止", "抬头", "拍照","休息","[unk]", "Test"]'
        # self.command_keywords = '["关机"]'

        # self.device_name = "Yundea 1076"
        if hasattr(Config, "DEVICE_NAME"):
            self.device_name = Config.DEVICE_NAME
        else:
            self.device_name = "Yundea 1076"
        # device_name = "SP002Ua"
        # device_name='JieLi BR21'
        self.device_index = None

        self.model = Model(self.MODEL_PATH)
        self.spk_model = SpkModel(self.SPK_MODEL_PATH)
        self.rec = KaldiRecognizer(self.model, self.SAMPLERATE_ORIG, self.wakeup_keywords)
        self.rec.SetSpkModel(self.spk_model)
        self.voice_buffer = None
        self.buffer_size = 4096
        self.sd_blocksize = 6000
        self.speech_buffer_size = self.sample_rate * self.frame_duration // 1000
        self.audio_memory = io.BytesIO()
        self.start_time = time.time()

        self.comm = communicator
        self.framNo = 0

    def kaldi_listener(self):

        while True:
            if not ThreadingEvent.wakeup_event.is_set():
                if Config.IS_DEBUG == True:

                    # device_idx = 2
                    device_idx = self.find_device_index()

                else:
                    device_idx = self.find_device_index()

                with sd.InputStream(samplerate=self.sample_rate, blocksize=self.sd_blocksize, device=device_idx,
                                    dtype="int16", channels=1, callback=self.main_callback):
                    while True:
                        pass

    def main_callback(self, indata, frames, time1, status):
        if status != 0:
            print(status)
            # return
        if not ThreadingEvent.wakeup_event.is_set():
            self.wake_callback(indata, frames, time1, status)

        # ThreadingEvent.wakeup_event.wait(1)
        if not ThreadingEvent.wakeup_event.is_set():
            return
        self.voice_callback(indata, frames, time1, status)

    def voice_callback(self, indata, frames, time1, status):
        # print("voice")
        data = indata.tobytes()
        volume = np.abs(indata).mean()
        indata = self.resample_audio1(indata, self.SAMPLERATE_ORIG, self.SAMPLERATE_TARGET)

        # print(volume, self.recording_status)
        if self.recording_status != "Recording" and self.is_speech_by_volume(indata, volume) and not self.is_silent(data, volume):
            self.is_recording = True
            self.audio_memory = io.BytesIO()
            self.audio_memory.seek(0)
            self.audio_memory.truncate(0)
            # self.frames = []
            self.has_interrupt = False
            self.start_time = time.time()
            self.silence_counter = 0
            self.recording_status = "Recording"
            logging.info("Recording started...")

        # print(self.recording_status)

        audio_data = None
        if self.recording_status == "Recording":
            # indata = self.resample_audio1(indata, self.SAMPLERATE_ORIG, self.SAMPLERATE_TARGET)
            self.framNo += 1
            audio_data = self.start_recording(indata, volume)
        else:
            self.frames.append({"data": indata, "ts": time.time()})

        if self.recording_status == "Save" and audio_data is not None:
            logging.info("Recording saving...")
            self.comm.message.emit("voice disappear")  # 发信号到主线程
            try:
                # # 场景化策略（垫音）
                # # 后面应该单独拆走
                # if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                #     output_file_name = "resources/sound/sa_wait_voice.mp3"
                #     self.audio_player.play_voice_with_file(output_file_name)

                # 记录发送请求的时间
                # self.req_send_time = time.time()
                self.send_request(self.ws, audio_data)
                self.recording_status = "Waiting"
                if Config.IS_DEBUG == False:
                    self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 254, "g": 211, "b": 76}, Code.LIGHT_TYPE_TEMP)
                    logging.info("set light to loading mode")
                # 场景化策略（垫音）
                # 后面应该单独拆走
                if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                    output_file_name = "resources/sound/sa_wait_voice.mp3"
                    print("play en!")
                    self.audio_player.play_voice_with_file(output_file_name)

            except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                print(f"WebSocket connection failed: {e}")

            except Exception as e:
                print(f"Unexpected error: {e}")

    def wake_callback(self, indata, frames, time1, status):
        global file_counter
        # 调用网络传输的处理函数

        # callback(indata, frames, time1, status)
        # callback2(indata, frames, time1, status)
        # 调用本地 Kaldi 处理的处理函数

        if ThreadingEvent.wakeup_event.is_set():
            return

        data = bytes(indata)
        """This is called (from a separate thread) for each audio block."""
        # if status:
            # print(status, file=sys.stderr)
        # q.put(audio_data_dic)

        if self.rec.AcceptWaveform(data):
            result = json.loads(self.rec.Result())
            print("LI_Result_dict_keyword:", result)
            transcription = result.get("text", "")
            print(f"Transcription@@: {transcription}")
            
            # 检测关键词
            if self.target_keywords[1] in str(transcription) or "Test" in str(transcription):
                print(f"检测到唤醒词: {self.target_keywords[1] if self.target_keywords[1] in str(transcription) else 'Test'}")
                self.voice_buffer = indata
                ThreadingEvent.wakeup_event.set()
                self.rec = KaldiRecognizer(self.model, self.SAMPLERATE_ORIG, self.wakeup_keywords)
                if Config.IS_DEBUG == False:
                    self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0}, Code.LIGHT_TYPE_TEMP)
                    logging.info("turn on the light for wakeup")
        else:
            partial = json.loads(self.rec.PartialResult())
            partial_text = partial.get("partial", "")
            print(f"Partial Transcription: {partial_text}")
            if self.target_keywords[1] in str(partial_text) or "Test" in str(partial_text):
                print(f"检测到唤醒词: {self.target_keywords[1] if self.target_keywords[1] in str(partial_text) else 'Test'}")
                self.voice_buffer = indata
                ThreadingEvent.wakeup_event.set()
                self.rec = KaldiRecognizer(self.model, self.SAMPLERATE_ORIG, self.wakeup_keywords)
                if Config.IS_DEBUG == False:
                    self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0}, Code.LIGHT_TYPE_TEMP)
                    logging.info("turn on the light for wakeup")


        # print("final:", self.rec.FinalResult())

    def daemon(self):

        while True:
            if self.handler_interrupt == False:
                break

            # if ThreadingEvent.wakeup_event.is_set() == False:
            #     # self.p.terminate()
            #     self.wakeup()
            #
            # if ThreadingEvent.wakeup_event.is_set() == False:
            #     continue

            ThreadingEvent.wakeup_event.wait()

            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.sample_rate,
                                      # input_device_index=self.find_device_index(),
                                      input=True,
                                      # frames_per_buffer=self.buffer_size
                                      frames_per_buffer = 1024
                                      )

            # self.stream = self.p.open(format=pyaudio.paInt16,
            #                           channels=1,
            #                           rate=self.sample_rate,
            #                           # blocksize=8000,
            #                           # input_device_index=self.find_device_index(),
            #                           input=True,
            #                           # frames_per_buffer=self.sample_rate * self.frame_duration // 1000,
            #                           frames_per_buffer=8000,
            #                           output=True)

            # if self.voice_buffer is not None:
            #     # print("a")
            #     self.stream.write(self.voice_buffer.tobytes())

            # self.wakeup()


                    #     if Config.IS_DEBUG == False:
                    #         # 唤醒成功了点亮
                    #         # self.light.set_mode(Code.LIGHT_MODE_BREATHING)
                    #         self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                    #         logging.info("set light turned on")
                    # else:
                    #     continue

            # ThreadingEvent.wakeup_event.wait()
            while True:
                # self.stream = self.p.open(format=pyaudio.paInt16,
                #                           channels=1,
                #                           rate=self.sample_rate,
                #                           # input_device_index=self.find_device_index(),
                #                           input=True,
                #                           frames_per_buffer=self.sample_rate * self.frame_duration // 1000)
                # if self.voice_buffer is not None:
                #     data = self.voice_buffer
                #     # data = self.audio_encode(data)
                #     data = self.resample_audio1(data, self.SAMPLERATE_ORIG, self.sample_rate * self.frame_duration // 1000)
                #     # data = np.frombuffer(self.voice_buffer, dtype=np.int16)
                #     data = data.tobytes()
                #     self.voice_buffer = None
                # else:
                data = self.stream.read(self.speech_buffer_size, exception_on_overflow=False)
                if (self.is_speech(data) and not self.is_silent(data)) or self.voice_buffer is not None:
                # if not self.is_silent(data) or self.voice_buffer is not None:
                    # 暂时去掉，再start_recording里判断静音
                    # and not self.is_silent(data)


                    # ThreadingEvent.audio_stop_event.set()
                    if self.voice_buffer is None:
                        self.is_recording = True
                        audio_data = self.start_recording(data)
                        if audio_data is None:
                            continue
                    else:
                        audio_data = self.save_to_buffer_with_audio(self.voice_buffer)
                        self.voice_buffer = None
                        if audio_data is None:
                            continue

                    # print("wakeup:", ThreadingEvent.wakeup_event)
                    # if ThreadingEvent.wakeup_event.is_set() == False:
                    #     if self.wakeup(audio_data):
                    #         # self.wakeup()
                    #         ThreadingEvent.wakeup_event.set()
                    #         # ThreadingEvent.sleep_daemon_event.set()
                    #
                    #         if Config.IS_DEBUG == False:
                    #             # 唤醒成功了点亮
                    #             # self.light.set_mode(Code.LIGHT_MODE_BREATHING)
                    #             self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                    #             logging.info("set light turned on")
                    #     else:
                    #         continue

                    # ThreadingEvent.wakeup_event.wait()
                    if not ThreadingEvent.wakeup_event.is_set():
                        # audio_data = None
                        continue
                    try:
                        # # 场景化策略（垫音）
                        # # 后面应该单独拆走
                        # if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                        #     output_file_name = "resources/sound/sa_wait_voice.mp3"
                        #     self.audio_player.play_voice_with_file(output_file_name)

                        # 记录发送请求的时间
                        # self.req_send_time = time.time()
                        self.send_request(self.ws, audio_data)
                        if Config.IS_DEBUG == False:
                            self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 254, "g": 211, "b": 76}, Code.LIGHT_TYPE_TEMP)
                            logging.info("set light to loading mode")
                        # 场景化策略（垫音）
                        # 后面应该单独拆走
                        if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                            output_file_name = "resources/sound/sa_wait_voice.mp3"
                            print("play en!")
                            self.audio_player.play_voice_with_file(output_file_name)

                    except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                        print(f"WebSocket connection failed: {e}")

                    except Exception as e:
                        print(f"Unexpected error: {e}")

    # def get_req_send_time(self):
    #     return self.req_send_time

    def find_device_index(self):
        global device_index
        # 遍历设备列表查找设备索引
        for i, device in enumerate(sd.query_devices()):
            print(f"Device {i}: {device['name']}")
            if self.device_name in device['name'] and device['max_input_channels'] > 0:
                device_index = i
                break
        if device_index is None:
            raise ValueError(f"找不到匹配的设备 '{self.device_name}'")
        print(f"使用设备: {device_index} - {self.device_name}")
        return device_index

    # def command_check(self, indata, keywords = None):
    #     model = Model(self.MODEL_PATH)
    #     if keywords is None:
    #         keywords = self.keywords
    #     rec = KaldiRecognizer(model, self.SAMPLERATE_ORIG, self.wakeup_keywords)

    def wakeup_check(self, indata, frames, time, status):

        # data16 = self.audio_encode(indata)
        # audio_data = data16.tobytes()
        # indata = self.resample_audio1(indata, self.SAMPLERATE_ORIG, self.SAMPLERATE_TARGET)
        # audio_data1 = indata.tobytes()
        # audio_data = bytes(indata)
        # print("audio_data:", audio_data)
        audio_data = bytes(indata)
        if self.rec.AcceptWaveform(audio_data):
            result = json.loads(self.rec.Result())
            print("LI_Result_dict_keyword:", result)
            transcription = result.get("text", "")
            print(f"Transcription@@: {transcription}")
            # detect_keywords(transcription)
            # print("keywords[1]:",target_keywords[1])
            # 检测关键词
            # for word, phonemes in qibao_phonemes.items():
            #     if any(phoneme in recognized_phonemes for phoneme in phonemes):
            # if "spk" in result:
            #     spk_vector = result["spk"]
            #     print("spk_vector:", spk_vector)
            #     print("len(spk_vector):", len(spk_vector))
            #     # print("len(spk_sig):", len(spk_sig))
            #
            #     distance1 = cosine_dist(spk_li_1, spk_vector)
            #     print(f"Speaker distance1: {distance1}")
            #     if distance1>0.5:
            #         print("speaker distance larger than 0.5!!!!!!!!")
            #         continue
            #     # distance2 = cosine_dist(spk_li_2, spk_vector)
            #     # print(f"Speaker distance2: {distance2}")
            for keyword in self.wakeup_keywords:
                # if self.target_keywords[1] in str(transcription):
                if keyword in transcription:
                    # and not xiaoqi_event_triggered:
                    print(f"检测到qibao关键词: {keyword}")

                    ThreadingEvent.wakeup_event.set()
                    # self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                    # logging.info("set light turned on")
                    return True
                    # continue
        else:
            partial = json.loads(self.rec.PartialResult())
            partial_text = partial.get("partial", "")
            print(f"Partial Transcription: {partial_text}")
            for keyword in self.wakeup_keywords:
                # if self.target_keywords[1] in str(transcription):
                if keyword in str(partial_text):
                    # and not xiaoqi_event_triggered:
                    print(f"检测到qibao关键词: {keyword}")

                    ThreadingEvent.wakeup_event.set()
                    # self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                    # logging.info("set light turned on")
                    return True
                    # continue
            # if self.target_keywords[1] in str(partial_text):
            #     # and not xiaoqi_event_triggered:
            #     print(f"检测到qibao关键词: {self.target_keywords[1]}")
            #     return True

            # continue
            # else:
            # xiaoqi_event.clear()

            # print("partial未检测到qibao关键词，xiaoqi_event.clear")
        return

    def audio_encode(self, data):
        with wave.open(data, 'rb') as wf:
            raw_bytes = wf.readframes(wf.getnframes())  # 读取所有帧
            data16 = np.frombuffer(raw_bytes, dtype=np.int16)
        data.seek(0)
        return data16

    def command(self, data):
        data16 = self.audio_encode(data)
        audio_data = data16.tobytes()

        return

    def wakeup(self):
               # , data):
        # model = Model(self.MODEL_PATH)
        # spk_model = SpkModel(self.SPK_MODEL_PATH)
        not_send_flag = False
        # rec = KaldiRecognizer(model, self.SAMPLERATE_ORIG, self.keywords)
        # rec.SetSpkModel(spk_model)
        # rec2 = KaldiRecognizer(model, 44100)
        samplerate = self.SAMPLERATE_ORIG
        # self.find_device_index()
        with sd.InputStream(samplerate=samplerate, blocksize=8000, device=0,
                            dtype="int16", channels=1, callback=self.wakeup_check):
            while not ThreadingEvent.wakeup_event.is_set():
                time.sleep(1)
                return
                # pass

        return
        # data16 = np.frombuffer(data.getvalue(), dtype=np.int16)
        data16 = self.audio_encode(data)
        #
        # print(len(data16))
        audio_data = data16.tobytes()
        return self.wakeup_check(audio_data)
        # if rec.AcceptWaveform(audio_data):
        #     result = json.loads(rec.Result())
        #     print("LI_Result_dict_keyword:", result)
        #     transcription = result.get("text", "")
        #     print(f"Transcription@@: {transcription}")
        #             # detect_keywords(transcription)
        #             # print("keywords[1]:",target_keywords[1])
        #             # 检测关键词
        #             # for word, phonemes in qibao_phonemes.items():
        #             #     if any(phoneme in recognized_phonemes for phoneme in phonemes):
        #             # if "spk" in result:
        #             #     spk_vector = result["spk"]
        #             #     print("spk_vector:", spk_vector)
        #             #     print("len(spk_vector):", len(spk_vector))
        #             #     # print("len(spk_sig):", len(spk_sig))
        #             #
        #             #     distance1 = cosine_dist(spk_li_1, spk_vector)
        #             #     print(f"Speaker distance1: {distance1}")
        #             #     if distance1>0.5:
        #             #         print("speaker distance larger than 0.5!!!!!!!!")
        #             #         continue
        #             #     # distance2 = cosine_dist(spk_li_2, spk_vector)
        #             #     # print(f"Speaker distance2: {distance2}")
        #     for keyword in self.wakeup_keywords:
        #     # if self.target_keywords[1] in str(transcription):
        #         if keyword in transcription:
        #             # and not xiaoqi_event_triggered:
        #             print(f"检测到qibao关键词: {keyword}")
        #
        #             return True
        #             # continue
        # else:
        #     partial = json.loads(rec.PartialResult())
        #     partial_text = partial.get("partial", "")
        #     print(f"Partial Transcription: {partial_text}")
        #     for keyword in self.wakeup_keywords:
        #     # if self.target_keywords[1] in str(transcription):
        #         if keyword in str(partial_text):
        #             # and not xiaoqi_event_triggered:
        #             print(f"检测到qibao关键词: {keyword}")
        #
        #             return True
        #             # continue
        #     # if self.target_keywords[1] in str(partial_text):
        #     #     # and not xiaoqi_event_triggered:
        #     #     print(f"检测到qibao关键词: {self.target_keywords[1]}")
        #     #     return True
        #
        #         # continue
        #     # else:
        #         # xiaoqi_event.clear()
        #
        #         # print("partial未检测到qibao关键词，xiaoqi_event.clear")
        #
        # return

    def stop_daemon(self):
        self.handler_interrupt = True

    def start_recording(self, indata, volume, start_frame = None):
        """开始录音"""
        # self.frames = []
        # self.is_recording = True
        # logging.info("Recording started...")
        # print("begin")

        # self.audio_player.interrupt()
        # self.audio_player.stop_audio()
        # ThreadingEvent.recv_execute_command_event.clear()
        # ThreadingEvent.camera_start_event.clear()
        # ThreadingEvent.audio_play_event.clear()

        # volume = np.abs(indata).mean()
        # indata = resample_audio1(indata, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
        # start_time = time.time()
        # if volume > SILENCE_THRESHOLD:

        # print(time.time() - start_time)

        # if start_frame is not None:
        # #     self.frames.append(start_frame)
        #     self.audio_memory.write(start_frame)
        # if len(self.frames) > 0:
        #     for _, frame_data in enumerate(self.frames):
        #         frame = frame_data["data"]
        #         ts = frame_data["ts"]
        #         now_time = time.time()
        #         if now_time - ts > 1:
        #             # 把1s以内的声音也放进来
        #             continue
        #         self.audio_memory.write(frame)
        #     self.frames = []

        if len(self.frames) > 0:
            self.comm.message.emit("voice appear")  # 发信号到主线程
            # 取最后 3 帧（如果不足3帧就取全部），按正序排列
            last_frames = self.frames[-3:]
            for frame_dict in last_frames:
                frame = frame_dict["data"]
                self.audio_memory.write(frame)
            self.frames = []

        # time_duration = time.time() - self.start_time
        # if time_duration > 0.4 and self.has_interrupt == False:
        #     if self.screen is not None:
        #         self.screen.add("resources/video/main1.mp4", 100)
        #         self.screen.play()
        #     self.audio_player.interrupt()
        #     self.audio_player.stop_audio()
        #     ThreadingEvent.recv_execute_command_event.clear()
        #     ThreadingEvent.camera_start_event.clear()
        #     self.has_interrupt = True
        
        if self.has_interrupt == False:
            # if self.screen is not None:
            #     self.screen.add("resources/video/main1.mp4", 100)
            #     self.screen.play()
            if self.framNo > 1: 
                self.audio_player.interrupt()
                self.audio_player.stop_audio()
                ThreadingEvent.recv_execute_command_event.clear()
                ThreadingEvent.camera_start_event.clear()
                self.has_interrupt = True

        self.audio_memory.write(indata.tobytes())
        # self.frames.append(indata.tobytes())

        # 静音检测（通过 VAD 检测）
        if self.is_silent(indata, volume):
            # (not self.is_speech(data)) or 暂时去掉


            # print("tag:", self.is_speech(data), self.slience_tag)
            logging.info("Silence detected.")
            self.recording_status = "Save"
            self.framNo = 0
            # self.stop_recording()

        # 超过 timeout 秒自动停止
        if time.time() - self.start_time > self.timeout:
            logging.info("Recording time exceeded, stopping...")
            self.recording_status = "Save"
            self.framNo = 0
            # self.stop_recording()

        # audio_memory.write(indata.tobytes())
        if self.recording_status == "Save":
            # time_duration = time.time() - self.start_time
            # if time_duration > 0.4:
            #     self.audio_player.interrupt()
            #     self.audio_player.stop_audio()
            #     ThreadingEvent.recv_execute_command_event.clear()
            #     ThreadingEvent.camera_start_event.clear()
            audio_data = self.audio_memory.getvalue()
            # self.save_recording()
            # audio_data = self.save_to_buffer()
            return audio_data

            # audio_data = self.save_to_buffer_by_int16()
            # audio_data = self.save_to_buffer()
            # # print("save to buffer")
            # self.save_recording(self.filename)
            # # print("save to file")
            # self.slience_tag = True
            # self.silence_counter = 0
            #
            # self.is_recording = False
            # print("voice duration:", (time.time() - start_time))
            #
            # return audio_data
        # else:
            # print("cancel with short time, ", time_duration)

        # self.silence_counter = 0
        return None

    def send_request(self, ws, audio_data):

        conversation_id = messageid.get_conversation_id()
        message_id = messageid.generate()
        # audio_data = base64.b64encode(audio_data.getvalue()).decode('utf-8')
        audio_data = base64.b64encode(audio_data).decode('utf-8')
        token = messageid.get_token()

        request = {
            "version": "1.0",
            "method": "voice-chat",
            "conversation_id": conversation_id,
            "message_id": message_id,
            "token": token,
            # "timestamp": datetime.utcnow().isoformat() + "Z",
            "timestamp": Common.get_rfc3339_with_timezone(),
            "data": {
                "content_type": "audio",
                "content": audio_data
            }
        }

        re = 0
        while re < self.MAX_RETRIES:
            try:
                print("Sending request...", re)
                ws.send(json.dumps(request))
                break
                # return ret
            except Exception as e:
                print(f"Unexpected error: {e}")
                logging.warn(f"Error send request: {e}.")
                re = re + 1

    def stop_recording(self):
        """停止录音"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.is_recording = False
        logging.info("Recording stopped.")

    def is_silent(self, data, volume):
        """检测是否为静音段。"""
        # 将字节数据转换为 numpy 数组
        # audio_data = np.frombuffer(data, dtype=np.int16)
        # volume = np.max(np.abs(audio_data))
        # print("li_audio_data:",audio_data)
        # 检查最大值是否低于阈值
        print("max, threshold, slic_counter, tag, time:", volume, self.threshold, self.silence_counter,
              self.slience_tag, time.time())
        if volume < self.threshold:
            if self.silence_counter > 0:
                self.silence_counter = 0
            self.silence_counter = self.silence_counter - 1
            if self.slience_tag == False and self.silence_counter > (-1 * self.SILENCE_FRAMES):
                return False
            # print("检测到静音")
            self.slience_tag = True
            self.silence_counter = 0
            return True
        else:
            if self.silence_counter < 0:
                self.silence_counter = 0
            self.silence_counter = self.silence_counter + 1
            if self.slience_tag == True and self.silence_counter < 2:
                return True
            # print("未检测到静音")
            self.slience_tag = False
            return False

    def is_speech_by_volume(self, indata, volume):
        # volume = np.abs(indata).mean()
        # indata = self.resample_audio1(indata, self.SAMPLERATE_ORIG, self.SAMPLERATE_TARGET)

        if volume > self.SILENCE_THRESHOLD:
            return True
        else:
            return False

    def is_speech(self, data):
        """使用 WebRTC VAD 检测是否为语音"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return self.vad.is_speech(audio_data.tobytes(), self.sample_rate)

    def save_to_buffer_with_audio(self, audio_data):
        memory_file = io.BytesIO()
        with wave.open(memory_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(audio_data))

        # 将文件指针重置为开头，以便读取
        memory_file.seek(0)
        # print(memory_file)
        return memory_file

    def save_to_buffer(self):
        if not self.frames:
            logging.warning("No audio data recorded.")
            return
        memory_file = io.BytesIO()

        with wave.open(memory_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))

        # 将文件指针重置为开头，以便读取
        memory_file.seek(0)
        # print(memory_file)
        return memory_file

    def save_to_buffer_by_int16(self):
        if not self.frames:
            logging.warning("No audio data recorded.")
            return
        memory_file = io.BytesIO()

        audio_data = ""
        with wave.open(memory_file, 'rb') as wf:
            raw_bytes = wf.readframes(wf.getnframes())  # 读取所有帧
            int16_array = np.frombuffer(raw_bytes, dtype=np.int16)

        return int16_array

    def save_recording(self, filename="recording.wav"):
        """保存录音到文件"""
        if not self.frames:
            logging.warning("No audio data recorded.")
            return

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
        logging.info(f"Recording saved as {filename}")

    def get_audio_file(self):
        return self.filename

    def resample_audio1(self, audio_data, orig_rate, target_rate):
        """重采样音频数据"""
        # 计算重采样后的长度
        new_length = int(len(audio_data) * target_rate / orig_rate)
        # 执行重采样
        resampled = signal.resample(audio_data, new_length)
        return resampled.astype(np.int16)

    def close(self):
        """关闭麦克风流"""
        if self.stream:
            self.stream.close()
        self.p.terminate()

# # 使用示例
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     mic = Microphone()
#     mic.start_recording()

#     # 录音结束后，关闭麦克风
#     mic.close()