import pygame
import os
from common.threading_event import ThreadingEvent
import logging
import time
from base.messageid import messageid

class AudioPlayer:

    PATH = "/tmp/"

    def __init__(self, spray):
        # 初始化 Pygame mixer
        pygame.mixer.init()
        self.audio_list = []  # 用于存储音频文件路径
        self.current_track = None  # 当前正在播放的音频
        self.is_interrupted = False
        self.played_list = []
        self.spray = spray
        self.i = 0


    def audio_play_event_daemon(self):
        self.i = 0
        while True:
            ThreadingEvent.audio_play_event.wait()
            plCount = len(self.audio_list)
            logging.info(f"AudioPlayer audio_list length:{plCount}")

            while self.i < plCount:
                if pygame.mixer.music.get_busy() == False:
                    self.play_audio(self.i)
                    self.i = self.i + 1
                time.sleep(0.5)

            if self.i >= len(self.audio_list):
                self.i = 0
                ThreadingEvent.audio_play_event.clear()


    def audio_stop_event_daemon(self):
        ThreadingEvent.audio_stop_event.wait()
        self.stop_audio()
        self.is_interrupted = True
        ThreadingEvent.audio_stop_event.clear()

    def save(self, audio_data, audio_file_tag = ""):
        path = self.PATH
        output_file_name = f"{path}{audio_file_tag}.mp3"
        with open(output_file_name, "wb") as pcm_file:
            pcm_file.write(audio_data)
        return output_file_name

    def add(self, audio_data, audio_file_tag = ""):
        """将音频文件路径添加到列表"""
        audio_file = audio_data["filename"]
        msg_id = audio_data["msg_id"]
        # type = audio_file["type"]
        # wait_time = audio_file["wait_time"]
        if os.path.isfile(audio_file):
            # audio_data = {
            #     "filename": audio_file,
            #     "msg_id": msg_id,
            #     "type": type,
            #     "wait_time": wait_time
            # }
            self.audio_list.append(audio_data)
            ThreadingEvent.audio_play_event.set()
            logging.info(f"Added: {audio_file} {msg_id}")
        else:
            logging.error(f"Error: {audio_file} does not exist.")

    def remove_audio(self, audio_file):
        """从列表中删除音频文件"""
        if audio_file in self.audio_list:
            self.audio_list.remove(audio_file)
            logging.info(f"Removed: {audio_file}")
        else:
            logging.error(f"Error: {audio_file} not found in list.")

    def play_audio(self, index):
        """从列表中播放指定索引的音频"""
        if 0 <= index < len(self.audio_list):
            self.is_interrupted = False
            audio_data = self.audio_list[index]
            msg_id = audio_data["msg_id"]
            # audio_file = audio_data["filename"]
            # type = audio_data["type"]
            # wait_time = audio_data["wait_time"]
            latest_msg_id = messageid.get_latest_message_id()
            if latest_msg_id != msg_id:
                return
            if self.current_track is not None and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()  # 停止当前播放的音频

            self.play(audio_data)

        else:
            logging.error("Error: Invalid index.")

    def play_audio_with_data(self, audio_data, is_temp_save = True):
        """从列表中播放指定索引的音频"""
        # if self.current_track is not None and pygame.mixer.music.get_busy():
        #     pygame.mixer.music.stop()  # 停止当前播放的音频
        # pygame.mixer.music.load(audio_file)  # 加载音频文件
        # pygame.mixer.music.play()  # 播放音频

        self.is_interrupted = False
        self.play(audio_data)

        if is_temp_save == True:
            self.current_track = audio_data
        # logging.info(f"Now playing: {audio_file}")

    def play(self, audio_data):
        if audio_data["filename"] == "" or audio_data["filename"] is None:
            return
        audio_file = audio_data["filename"]
        type = audio_data["type"]
        wait_time = audio_data["wait_time"]
        # spray = audio_data["spray"]
        if "bgm" in audio_data:
            bgm = audio_data["bgm"]
        else:
            bgm = ""

        # if spray == "on":
        #     # ThreadingEvent.spray_start_event.set()
        #     self.spray.shoot()

        if bgm:
            bgm_file = bgm["filename"]
            if os.path.isfile(bgm_file):
                pygame.mixer.music.load(bgm_file)  # 加载音频文件
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()

        self.current_track = audio_data
        voice = pygame.mixer.Sound(audio_file)
        voice_channel = pygame.mixer.Channel(1)
        voice_channel.play(voice)

        # pygame.mixer.music.load(audio_file)  # 加载音频文件
        # ThreadingEvent.audio_play_event.set()
        # pygame.mixer.music.play()  # 播放音频
        while voice_channel.get_busy():
            pygame.time.wait(50)
        # ThreadingEvent.audio_play_event.clear()
        if wait_time > 0 and self.is_interrupted == False:
            # 如果不是被打断的，就需要等待一点时间
            pygame.time.wait(wait_time)
        logging.info(f"Now playing: {audio_file}")
        self.played_list.append(audio_data)

    def replay(self):
        audio_data = self.current_track
        print("replay:", audio_data)
        if audio_data is not None:
            self.play_audio_with_data(audio_data, False)
        return

    def stop_audio(self):
        """停止当前播放的音频"""
        voice_channel = pygame.mixer.Channel(1)
        if voice_channel.get_busy():
            voice_channel.stop()
            logging.info("Playback stopped.")
            self.current_track = None
            ThreadingEvent.audio_play_event.clear()
        else:
            logging.warn("Error: No audio is currently playing.")

    def clear_list(self):
        """清空音频列表"""
        self.audio_list.clear()
        self.i = 0
        logging.info("Audio list cleared.")

    def get_audio_list(self):
        """返回当前音频列表"""
        return self.audio_list

    def get_played_list(self):
        return self.played_list

    def get_current_track(self):
        return self.current_track

    def get_latest_played(self):
        if len(self.played_list) > 0:
            return self.played_list[-1]
        else:
            return None