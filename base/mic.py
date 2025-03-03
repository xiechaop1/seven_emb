import wave
import time
import webrtcvad
import logging
import numpy as np
import pyaudio
import collections
from collections import deque
import queue
import io
from base.messageid import messageid
from common.threading_event import ThreadingEvent
from common.common import Common
import base64
from datetime import datetime
import uuid
import json
# from vosk import Model, KaldiRecognizer


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

    SILENCE_THRESHOLD = 800  # 静音阈值
    SILENCE_FRAMES = 10  # 静音帧数量阈值
    PRE_RECORD_FRAMES = 1  # 预录制帧数
    # 定义队列和缓冲区

    MAX_RETRIES = 3

    SPK_MODEL_PATH = "vosk-model-spk-0.4"
    MODEL_PATH = "vosk-model-small-cn-0.22"

    def __init__(self, ws, audio_player, threshold=800, timeout=30, sample_rate=16000, frame_duration=30):
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

        self.spk_li_1=[-0.626114, 0.430365, 0.564255, -0.182698, 0.537145, 0.044097, 0.564515, 0.666896, 1.085733, -0.523695, 2.178851, -0.545808, 0.492513, -0.214256, 0.380257, 0.561458, 1.432191, 0.576447, 1.347584, -1.410213, -0.201343, 1.299883, 0.16591, -0.301386, 1.030398, -0.155679, 1.668122, -0.47749, 1.583658, 1.031789, -0.610194, 0.207826, -2.028657, -0.778005, 0.608732, -1.103482, -0.249394, -0.145279, -0.252108, -0.744611, -0.178013, 0.821876, 1.348644, 0.958709, -1.489057, -0.069446, 0.55689, 0.382191, 1.793885, 0.12014, 1.096465, 1.948748, -0.288994, -0.427686, -0.25332, -0.74351, 1.289284, -0.442085, -1.594271, 0.238896, -0.14475, -1.243948, -0.811971, -1.167681, -1.934597, -2.094246, 0.203778, 0.2246, 0.769156, 3.129627, 1.638138, -0.414724, 0.363555, 1.058113, -0.658691, 0.345854, -1.559133, 0.087666, 0.984442, -0.469354, 1.667347, 0.916898, -2.170697, 0.292812, 0.051197, 1.222564, 1.065773, -0.065279, 0.214764, -0.407425, 0.992222, -0.993893, 0.693716, 0.121084, 1.31698, 1.255295, -0.941613, 0.015467, 0.500375, -1.479744, -0.943895, -0.405701, 1.795941, -0.66203, 1.224589, 0.963079, -0.872087, 0.392804, 1.412374, -0.279257, -0.462107, 0.674435, 0.137653, 0.93439, 2.394885, -0.571315, 0.374555, -0.233448, 0.757664, -0.375494, 0.666074, -0.123803, 1.518769, 0.873773, -0.218161, 1.566089, -0.488127, 0.386693]

        self.call_on = True
    
    def daemon(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.sample_rate * self.frame_duration // 1000)
        
        while True:
            if self.handler_interrupt == False:
                break
            data = self.stream.read(self.sample_rate * self.frame_duration // 1000)
            if self.is_speech(data) and not self.is_silent(data):
                ThreadingEvent.audio_stop_event.set()
                if self.call_on == False:
                    audio_data = self.start_recording()
                    #self.callup(audio_data)
                else:
                    self.is_recording = True
                    audio_data = self.start_recording()
                    try:
                        self.send_request(self.ws, audio_data)
                    except (WebSocketException, BrokenPipeError, WebSocketConnectionClosedException) as e:
                        print(f"WebSocket connection failed: {e}")

                    except Exception as e:
                        print(f"Unexpected error: {e}")


    def callup(self, data):
        

        model = Model(MODEL_PATH)
        spk_model = SpkModel(SPK_MODEL_PATH)
        not_send_flag=False
        rec = KaldiRecognizer(model, SAMPLERATE_ORIG, keywords)
        rec.SetSpkModel(spk_model)
        # rec2 = KaldiRecognizer(model, 44100)
        # with sd.InputStream(samplerate=args.samplerate, blocksize=8000, device=find_device_index(),
        #                     dtype="int16", channels=1, callback=main_callback):
        #     print("#" * 80)
        #     print("Press Ctrl+C to stop the recording1")
        #     print("#" * 80)
        #     # rec = KaldiRecognizer(model, args.samplerate,'["播放音乐","七宝", "停止", "停", "[unk]"]')
        #     # print("args.samplerate:", args.samplerate)
        #     # start_threads()
        #     count2 = 0
        #     xiaoqi_detected_count=0
        #     xiaoqi_event_triggered = False  # 初始标志
        #     while True:
        #         time.sleep(0.01)
        #         count2 += 1
        #         is_silent_flag=False
        #         # print("count2:",count2)
        #         # if count2 == 2:
        #         #     silent_start_time = time.time()
        #         # silent_end_time = time.time()
        #         # print("silent_end_time-slient_start_time:", silent_end_time - silent_start_time)
        #         # if count2 > 2 and silent_end_time - silent_start_time > 30:
        #         #     print("morre than 10s break!!!!!")
        #         #     running2 = False
        #         #     time.sleep(0.1)
        #         # running2 = True
        #         # print("running2:", running2)
        #         # time.sleep(0.01)
        #         audio_data_get = q.get()
                # data, message_id_get = audio_data_get
                # xiaoqi_event_triggered = False
                # if is_silent(data):
                    # print("检测到静音，跳过此段音频")
                    # is_silent_flag=True
                    # continue  # 跳过静音段，进入下一个循环
                # frames.append(data)
                # print("data_id_get:", data_id_get)
                # if rec2.AcceptWaveform(data):
                #     # print(rec.Result())
                #     result2 = json.loads(rec2.Result())
                #     print("LI_Result_dict_flow:2", result2)
                #     if result2:
                #         result_detected=True
                # else:
                #     partial2 = json.loads(rec2.PartialResult())
                #     print("LI_Result_dict:partial2", partial2)
                #     partial_text2 = partial2.get("partial2", "")
                #     print(f"Partial Transcription2: {partial_text2}")
                    # detect_keywords(partial_text2)
        if rec.AcceptWaveform(data):
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
            if target_keywords[1] in str(transcription):
                # and not xiaoqi_event_triggered:
                print(f"检测到qibao关键词: {target_keywords[1]}")
                # print(f"检测到qibao关键词: {phonemes}")
                # xiaoqi_event.set()
                # xiaoqi_detected = True
                # xiaoqi_event_triggered = True
                self.call_on = True
                # continue
            # else:
                # print("未检测到qibao关键词，xiaoqi_event.clear")
                # xiaoqi_event.clear()

                        # continue
                    # if target_keywords[5] in str(transcription):
                    #     print(f"检测到sleep关键词: {target_keywords[5]}")
                    #     continue_shot_and_record=True
                    #     print("continue_shot_and_record0:",continue_shot_and_record)
                    #     # print(f"检测到qibao关键词: {phonemes}")
                    #     sleep_detected = True
                    # if target_keywords[2] in str(transcription) :
                    #     print(f"检测到stop_phonemes关键词: {target_keywords[2] }")
                    #     # print(f"检测到stop_phonemes关键词: {phonemes}")
                    #     nihao_detected=True
                    #     nihao_event.set()
                    #     continue
                    # if target_keywords[3] in str(transcription):
                    #     print(f"检测到stop_phonemes关键词: {target_keywords[3]}")
                    #     # print(f"检测到stop_phonemes关键词: {phonemes}")
                    #     nihao_detected = True
                    # if target_keywords[4] in str(transcription):
                    #     print(f"识别到paizhao_word: {target_keywords[4]}")
                    #     paizhao_voice_command=True
                    #     data_id_no_send=int(data_id_get)
                    #     print("time_data_id_no_send:", time.time())
                    #     print("data_id_no_send:",data_id_no_send)
                        # write_variable("1")
                        # print("共享变量已改为 1")
        else:
            partial = json.loads(rec.PartialResult())
            partial_text = partial.get("partial", "")
            print(f"Partial Transcription: {partial_text}")
            if target_keywords[1] in str(partial_text):
                # and not xiaoqi_event_triggered:
                print(f"检测到qibao关键词: {target_keywords[1]}")
                # print(f"检测到qibao关键词: {phonemes}")
                # xiaoqi_event.set()
                # xiaoqi_detected = True
                # xiaoqi_event_triggered = True
                self.call_on = True

                # continue
            # else:
                # xiaoqi_event.clear()

                # print("partial未检测到qibao关键词，xiaoqi_event.clear")
            # if target_keywords[5] in str(partial_text):
            #     print(f"检测到sleep关键词: {target_keywords[5]}")
            #     continue_shot_and_record = True
            #     print("continue_shot_and_record1:", continue_shot_and_record)
            #     # print(f"检测到qibao关键词: {phonemes}")
            #     sleep_detected = True
            # if target_keywords[2] in str(partial_text):
            #     print(f"检测到stop_phonemes关键词: {target_keywords[2]}")
            #     nihao_event.set()
            #     # print(f"检测到stop_phonemes关键词: {phonemes}")
            #     nihao_detected = True
            #     continue

        if dump_fn is not None:
            dump_fn.write(data)
        print("final:",rec.FinalResult())

    def stop_daemon(self):
        self.handler_interrupt = True

    def start_recording(self):
        """开始录音"""
        self.frames = []
        # self.is_recording = True
        logging.info("Recording started...")
        # print("begin")

        self.audio_player.stop_audio()

        # volume = np.abs(indata).mean()
        # indata = resample_audio1(indata, SAMPLERATE_ORIG, SAMPLERATE_TARGET)
        start_time = time.time()
        # if volume > SILENCE_THRESHOLD:
        while self.is_recording:
            data = self.stream.read(self.sample_rate * self.frame_duration // 1000)
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

        # audio_memory = io.BytesIO()
        # for frame in pre_buffer:
            # audio_memory.write(frame.tobytes())
        # pre_buffer.clear()

        audio_data = self.save_to_buffer()
        print("save to buffer")
        self.save_recording(self.filename)
        print("save to file")
        self.slience_tag = True
        self.silence_counter = 0
        self.is_recording = False

        return audio_data
    
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
        print("max:",np.max(np.abs(audio_data)), self.threshold, self.silence_counter, self.slience_tag)
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
            if self.slience_tag == True and self.silence_counter < 3:
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
        print(memory_file)
        return memory_file

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