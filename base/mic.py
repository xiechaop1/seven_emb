import pyaudio
import wave
import time
import webrtcvad
import logging
import numpy as np

class Microphone:
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

    def __init__(self, threshold=800, timeout=4, sample_rate=16000, frame_duration=30):
        """
        初始化麦克风参数
        :param threshold: 静音检测阈值（音频幅度超过该值视为非静音）
        :param timeout: 录音超时（秒），超过此时间自动停止录音
        :param sample_rate: 采样率，默认为16000
        :param frame_duration: 每帧的时长（毫秒），默认为30ms
        """
        self.threshold = threshold
        self.timeout = timeout
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.p = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(2)  # VAD模式设置，0为最宽松，3为最严格
        self.stream = None
        self.frames = []
        self.is_recording = False
    
    def start_recording(self):
        """开始录音"""
        self.frames = []
        self.is_recording = True
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.sample_rate * self.frame_duration // 1000)
        logging.info("Recording started...")

        start_time = time.time()
        while self.is_recording:
            data = self.stream.read(self.sample_rate * self.frame_duration // 1000)
            self.frames.append(data)

            # 静音检测（通过 VAD 检测）
            if not self.is_speech(data):
                logging.info("Silence detected.")
            
            # 超过 timeout 秒自动停止
            if time.time() - start_time > self.timeout:
                logging.info("Recording time exceeded, stopping...")
                self.stop_recording()

        self.save_recording()
    
    def stop_recording(self):
        """停止录音"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.is_recording = False
        logging.info("Recording stopped.")
    
    def is_silent(data, threshold=150):
        """检测是否为静音段。"""
        # 将字节数据转换为 numpy 数组
        audio_data = np.frombuffer(data, dtype=np.int16)
        # print("li_audio_data:",audio_data)
        # 检查最大值是否低于阈值
        # print("max:",np.max(np.abs(audio_data)))
        if np.max(np.abs(audio_data)) < self.threshold:
            # print("检测到静音")
            return True
        else:
            # print("未检测到静音")
            return False

    def is_speech(self, data):
        """使用 WebRTC VAD 检测是否为语音"""
        audio_data = np.frombuffer(data, dtype=np.int16)
        return self.vad.is_speech(audio_data.tobytes(), self.sample_rate)
    
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