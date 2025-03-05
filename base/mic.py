import os

os.environ["SDL_AUDIODRIVER"] = "alsa"
os.environ["AUDIODEV"] = "hw:3,0"

import wave
import time
import webrtcvad
import logging
import numpy as np
import pyaudio
# import sounddevice as sd
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
from datetime import datetime
import uuid
import json
from vosk import Model, KaldiRecognizer, SpkModel


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

    SILENCE_THRESHOLD = 1000  # 静音阈值
    SILENCE_FRAMES = 10  # 静音帧数量阈值
    PRE_RECORD_FRAMES = 1  # 预录制帧数
    # 定义队列和缓冲区

    MAX_RETRIES = 3

    SPK_MODEL_PATH = "utils/vosk-model-spk-0.4"
    MODEL_PATH = "utils/vosk-model-small-cn-0.22"
    # SPK_MODEL_PATH = "/home/li/vosk-api/python/example/vosk-model-spk-0.4"
    # model_path = "/home/li/vosk-model-small-cn-0.22"

    def __init__(self, ws, audio_player, light, threshold=800, timeout=30, sample_rate=16000, frame_duration=30):
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
        self.vad = webrtcvad.Vad(2)  # VAD模式设置，0为最宽松，3为最严格
        self.stream = None
        self.frames = []
        self.is_recording = False
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
        # self.req_send_time = 0

        self.spk_li_1=[-0.626114, 0.430365, 0.564255, -0.182698, 0.537145, 0.044097, 0.564515, 0.666896, 1.085733, -0.523695, 2.178851, -0.545808, 0.492513, -0.214256, 0.380257, 0.561458, 1.432191, 0.576447, 1.347584, -1.410213, -0.201343, 1.299883, 0.16591, -0.301386, 1.030398, -0.155679, 1.668122, -0.47749, 1.583658, 1.031789, -0.610194, 0.207826, -2.028657, -0.778005, 0.608732, -1.103482, -0.249394, -0.145279, -0.252108, -0.744611, -0.178013, 0.821876, 1.348644, 0.958709, -1.489057, -0.069446, 0.55689, 0.382191, 1.793885, 0.12014, 1.096465, 1.948748, -0.288994, -0.427686, -0.25332, -0.74351, 1.289284, -0.442085, -1.594271, 0.238896, -0.14475, -1.243948, -0.811971, -1.167681, -1.934597, -2.094246, 0.203778, 0.2246, 0.769156, 3.129627, 1.638138, -0.414724, 0.363555, 1.058113, -0.658691, 0.345854, -1.559133, 0.087666, 0.984442, -0.469354, 1.667347, 0.916898, -2.170697, 0.292812, 0.051197, 1.222564, 1.065773, -0.065279, 0.214764, -0.407425, 0.992222, -0.993893, 0.693716, 0.121084, 1.31698, 1.255295, -0.941613, 0.015467, 0.500375, -1.479744, -0.943895, -0.405701, 1.795941, -0.66203, 1.224589, 0.963079, -0.872087, 0.392804, 1.412374, -0.279257, -0.462107, 0.674435, 0.137653, 0.93439, 2.394885, -0.571315, 0.374555, -0.233448, 0.757664, -0.375494, 0.666074, -0.123803, 1.518769, 0.873773, -0.218161, 1.566089, -0.488127, 0.386693]
        self.keywords = '["播放音乐", "七七", "停止", "抬头", "拍照","休息","[unk]"]'
        self.target_keywords = ["播放音乐", "七七", "停止", "抬头","拍照","休息"]
        self.wakeup_keywords = '["七七", "七宝", "七夕", "休息", "嘻嘻"]'

        self.device_name = "Yundea 1076"
        # device_name = "SP002Ua"
        # device_name='JieLi BR21'
        self.device_index = None

    def daemon(self):

        while True:
            if self.handler_interrupt == False:
                break

            # self.wakeup()
            # ThreadingEvent.wakeup_event.wait()

            while True:
                self.stream = self.p.open(format=pyaudio.paInt16,
                                          channels=1,
                                          rate=self.sample_rate,
                                          input=True,
                                          frames_per_buffer=self.sample_rate * self.frame_duration // 1000)
                data = self.stream.read(self.sample_rate * self.frame_duration // 1000, exception_on_overflow = False)
                if self.is_speech(data):
                        # and not self.is_silent(data)):
                    # ThreadingEvent.audio_stop_event.set()
                    self.is_recording = True
                    audio_data = self.start_recording(data)
                    if audio_data is None:
                        continue

                    print("wakeup:", ThreadingEvent.wakeup_event)
                    if ThreadingEvent.wakeup_event.is_set() == False:
                        if self.wakeup(audio_data):
                            # self.wakeup()
                            ThreadingEvent.wakeup_event.set()

                            if Config.IS_DEBUG == False:
                                #唤醒成功了点亮
                                # self.light.set_mode(Code.LIGHT_MODE_BREATHING)
                                self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                                logging.info("set light turned on")
                        else:
                            continue

                    ThreadingEvent.wakeup_event.wait()
                    try:
                        # # 场景化策略（垫音）
                        # # 后面应该单独拆走
                        # if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                        #     output_file_name = "resources/sound/sa_wait_voice.mp3"
                        #     self.audio_player.play_voice_with_file(output_file_name)

                        # 记录发送请求的时间
                        # self.req_send_time = time.time()
                        self.send_request(self.ws, audio_data)
                        self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 254, "g": 211, "b": 76})
                        logging.info("set light to loading mode")
                        # 场景化策略（垫音）
                        # 后面应该单独拆走
                        if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                            output_file_name = "resources/sound/sa_wait_voice.mp3"
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

    def wakeup_check(self, indata):
        model = Model(self.MODEL_PATH)
        rec = KaldiRecognizer(model, self.SAMPLERATE_ORIG, self.wakeup_keywords)

        audio_data = indata
        audio_data = bytes(indata)
        if rec.AcceptWaveform(audio_data):
            result = json.loads(rec.Result())
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

                    # ThreadingEvent.wakeup_event.set()
                    # self.light.start(Code.LIGHT_MODE_BREATHING, {"r": 0, "g": 255, "b": 0})
                    # logging.info("set light turned on")
                    return True
                    # continue
        else:
            partial = json.loads(rec.PartialResult())
            partial_text = partial.get("partial", "")
            print(f"Partial Transcription: {partial_text}")
            for keyword in self.wakeup_keywords:
            # if self.target_keywords[1] in str(transcription):
                if keyword in str(partial_text):
                    # and not xiaoqi_event_triggered:
                    print(f"检测到qibao关键词: {keyword}")

                    # ThreadingEvent.wakeup_event.set()
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

    def wakeup(self, data):
        # model = Model(self.MODEL_PATH)
        # spk_model = SpkModel(self.SPK_MODEL_PATH)
        not_send_flag=False
        # rec = KaldiRecognizer(model, self.SAMPLERATE_ORIG, self.keywords)
        # rec.SetSpkModel(spk_model)
        # rec2 = KaldiRecognizer(model, 44100)
        samplerate = self.SAMPLERATE_ORIG
        # with sd.InputStream(samplerate=samplerate, blocksize=8000, device=self.find_device_index(),
        #                     dtype="int16", channels=1, callback=self.wakeup_check):
        #     while not ThreadingEvent.wakeup_event.is_set():
        #         pass
        # return
        # data16 = np.frombuffer(data.getvalue(), dtype=np.int16)
        with wave.open(data, 'rb') as wf:
            raw_bytes = wf.readframes(wf.getnframes())  # 读取所有帧
            data16 = np.frombuffer(raw_bytes, dtype=np.int16)
        data.seek(0)
        #
        print(len(data16))
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

    def start_recording(self, start_frame = None):
        """开始录音"""
        self.frames = []
        # self.is_recording = True
        logging.info("Recording started...")
        # print("begin")

        # self.audio_player.interrupt()
        # self.audio_player.stop_audio()
        ThreadingEvent.recv_execute_command_event.clear()
        ThreadingEvent.camera_start_event.clear()
        # ThreadingEvent.audio_play_event.clear()

        # volume = np.abs(indata).mean()
        # indata = resample_audio1(indata, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
        start_time = time.time()
        # if volume > SILENCE_THRESHOLD:

        print(time.time() - start_time)

        if start_frame is not None:
            self.frames.append(start_frame)

        while self.is_recording:
            if time.time() - start_time > 0.1:
                self.audio_player.interrupt()
                self.audio_player.stop_audio()
            data = self.stream.read(self.sample_rate * self.frame_duration // 1000, exception_on_overflow = False)
            self.frames.append(data)

            # 静音检测（通过 VAD 检测）
            if (not self.is_speech(data)) or self.is_silent(data):
                print("tag:", self.is_speech(data), self.slience_tag)
                logging.info("Silence detected.")
                break
                # self.stop_recording()
            
            # 超过 timeout 秒自动停止
            if time.time() - start_time > self.timeout:
                logging.info("Recording time exceeded, stopping...")
                break
                # self.stop_recording()

            # audio_memory.write(indata.tobytes())
        if time.time() - start_time > 0.1:
            self.audio_player.interrupt()
            self.audio_player.stop_audio()
            # audio_memory = io.BytesIO()
            # for frame in pre_buffer:
                # audio_memory.write(frame.tobytes())
            # pre_buffer.clear()

            # audio_data = self.save_to_buffer_by_int16()
            audio_data = self.save_to_buffer()
            print("save to buffer")
            self.save_recording(self.filename)
            print("save to file")
            self.slience_tag = True
            self.silence_counter = 0
            self.is_recording = False

            return audio_data
        return None
    
    def send_request(self, ws, audio_data):

        conversation_id = messageid.get_conversation_id()
        message_id = messageid.generate()
        audio_data = base64.b64encode(audio_data.getvalue()).decode('utf-8')
        token = messageid.get_token()

        request = {
            "version": "1.0",
            "method": "voice-chat",
            "conversation_id": conversation_id,
            "message_id": message_id,
            "token": token,
            # "timestamp": datetime.utcnow().isoformat() + "Z",
            "timestamp":Common.get_rfc3339_with_timezone(),
            "data": {
                "content_type": "audio",
                "content": audio_data
            }
        }

        re = 0
        while re < self.MAX_RETRIES:
            try:
                print("Sending request...")
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
    
    def is_silent(self, data):
        """检测是否为静音段。"""
        # 将字节数据转换为 numpy 数组
        audio_data = np.frombuffer(data, dtype=np.int16)
        # print("li_audio_data:",audio_data)
        # 检查最大值是否低于阈值
        print("max, threshold, slic_counter, tag:",np.max(np.abs(audio_data)), self.threshold, self.silence_counter, self.slience_tag)
        if np.max(np.abs(audio_data)) < self.threshold:
            self.silence_counter = self.silence_counter - 1
            if self.slience_tag == False and self.silence_counter > -3:
                return False
            # print("检测到静音")
            self.slience_tag = True
            self.silence_counter = 0
            return True
        else:
            self.silence_counter = self.silence_counter + 1
            if self.slience_tag == True and self.silence_counter < 1:
                return True
            # print("未检测到静音")
            self.silence_tag = False
            return False

    def is_speech(self, data):
        """使用 WebRTC VAD 检测是否为语音"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return self.vad.is_speech(audio_data.tobytes(), self.sample_rate)
    
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
    
    def get_audio_file():
        return self.filename
    
    def record_voice():
        volume = np.abs(indata).mean()
        indata = resample_audio1(indata, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
        if volume >= SILENCE_THRESHOLD:
            flag_think=True
            noise_break_flag = True
            silence_counter = 0  # 重置静音计数器

            if not recording:
                print("@@@@@@@@@@@@开始录音......")
                recording = True
                print("audio_data_queue_size:", self.audio_data_queue.qsize())
                while not self.audio_data_queue.empty():
                    self.audio_data_queue.get()
                recording_event.set()
                start_record_time = current_time  # 记录录音开始时间

                # message_id_orin = get_message_id()
                # message_id = message_id_orin
                # print("message_id_born:", message_id)
                # print("last_message_id:", last_message_id)
                # old_message_id=last_message_id
                # print("old_message_id:", old_message_id)
                # output_file_name = f"/home/orangepi/vosk-api/python/example/send_pcm_folder/output{message_id}.pcm"
                #
                # print("output_file_name:", output_file_name)
                # output_pcm_file = open(output_file_name, "wb")
                self.audio_memory = io.BytesIO()
                # 写入预缓冲中的静音帧，仅在录音开始时
                for frame in self.pre_buffer:
                    self.audio_memory.write(frame.tobytes())
                self.pre_buffer.clear()

            # 写入当前音频帧
            self.audio_memory.write(indata.tobytes())

            # 如果录音时间超过4秒，立即停止录音
            if current_time - start_record_time > 6:
                print("@@@@@@@@@@@@录音时间超过4秒，停止录音")
                recording = False
                audio_data = self.audio_memory.getvalue()  # 获取内存中的音频数据
                self.audio_memory.close()  # 关闭内存流
                self.audio_memory = None
                # output_pcm_file.close()
                # process_audio(output_file_name, denoise_output_file_name)

                # if pop_swtich and audio_data is not None:

                #     if not_send_flag==False:
                #         # play_qibaozaina=True
                #         audio_file_stack.append(audio_data)
                #     else:
                #         play_haode = True

                    # flag_think = False
                    # recording_event.clear()
                    # print("append_output_file_name:", output_file_name)
                    # print("append audio_file_stack:", audio_file_stack)
                # output_pcm_file = None

        else:  # 静音帧
            if self.recording:
                # 写入当前静音帧
                self.audio_memory.write(indata.tobytes())
                silence_counter += 1

                # 如果静音超过指定时间或总录音时长超过4秒，立即停止录音
                if current_time - start_record_time > 1.0 and silence_counter >= 2:
                    print("@@@@@@@@@@@@检测到静音，停止录音")
                    self.recording = False
                    audio_data = self.audio_memory.getvalue()  # 获取内存中的音频数据
                    self.audio_memory.close()  # 关闭内存流
                    self.audio_memory = None
                    # output_pcm_file.close()
                    # process_audio(output_file_name, denoise_output_file_name)
                    # if pop_swtich and audio_data  is not None:
                    #     play_haode=True
                    #     t_play_haode=time.time()
                    #     # print("!!!!!!!!!!!!!!!Send_play_haode:", play_haode)
                    #     if not_send_flag == False:
                    #         # play_qibaozaina = True
                    #         audio_file_stack.append(audio_data)
                    #     else:
                    #         play_haode = True
                    #     last_message_id = message_id
                    #     # flag_think = False
                    #     recording_event.clear()
                        # print("append_output_file_name:", output_file_name)
                        # print("append audio_file_stack:", audio_file_stack)
                    # output_pcm_file = None
            else:
                # 保存静音帧到预缓冲中，仅在未录音时
                self.pre_buffer.append(indata.copy())

    # 初始化 WebRTC AudioProcessing 模块并处理音频
    def process_audio(input_pcm_file, output_pcm_file, sample_rate=16000):
        # 加载原始 PCM 文件
        audio_data = load_pcm(input_pcm_file)
        print(f"Loaded audio data: {len(audio_data)} samples at {sample_rate} Hz")

        # 初始化 WebRTC AudioProcessing 模块
        ap = AP(enable_vad=True, enable_ns=True)
        ap.set_stream_format(sample_rate, 1)  # 设置采样率和单通道

        ap.set_ns_level(3)  # 设置噪声抑制级别（0-3）
        ap.set_vad_level(3)  # 设置语音活动检测级别（0-3）

        # 分块处理音频（10ms 每块）
        frame_size = sample_rate // 100  # 每块 10ms
        processed_audio = []
        for i in range(0, len(audio_data), frame_size):
            audio_chunk = audio_data[i:i+frame_size]
            if len(audio_chunk) < frame_size:
                # 如果最后一块不足 10ms，用 0 填充
                audio_chunk = np.pad(audio_chunk, (0, frame_size - len(audio_chunk)))

            # 处理音频块
            audio_out = ap.process_stream(audio_chunk.tobytes())
            processed_audio.append(np.frombuffer(audio_out, dtype=np.int16))

        # 合并处理后的音频
        processed_audio = np.concatenate(processed_audio)

        # 保存处理后的 PCM 文件
        save_pcm(output_pcm_file, processed_audio)
        print(f"Processed audio saved to {output_pcm_file}")

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