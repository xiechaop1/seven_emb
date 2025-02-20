import pygame
import os

class AudioPlayer:
    def __init__(self):
        # 初始化 Pygame mixer
        pygame.mixer.init()
        self.audio_list = []  # 用于存储音频文件路径
        self.current_track = None  # 当前正在播放的音频

    def add_audio(self, audio_file):
        """将音频文件路径添加到列表"""
        if os.path.isfile(audio_file):
            self.audio_list.append(audio_file)
            logging.info(f"Added: {audio_file}")
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
            audio_file = self.audio_list[index]
            if self.current_track is not None and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()  # 停止当前播放的音频
            pygame.mixer.music.load(audio_file)  # 加载音频文件
            pygame.mixer.music.play()  # 播放音频
            self.current_track = audio_file
            logging.info(f"Now playing: {audio_file}")
        else:
            logging.error("Error: Invalid index.")

    def play_audio_with_file(self, audio_file):
        """从列表中播放指定索引的音频"""
        # if self.current_track is not None and pygame.mixer.music.get_busy():
        #     pygame.mixer.music.stop()  # 停止当前播放的音频
        pygame.mixer.music.load(audio_file)  # 加载音频文件
        pygame.mixer.music.play()  # 播放音频
        self.current_track = audio_file
        logging.info(f"Now playing: {audio_file}")

    def stop_audio(self):
        """停止当前播放的音频"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            logging.info("Playback stopped.")
            self.current_track = None
        else:
            logging.error("Error: No audio is currently playing.")

    def clear_list(self):
        """清空音频列表"""
        self.audio_list.clear()
        logging.info("Audio list cleared.")

    def get_audio_list(self):
        """返回当前音频列表"""
        return self.audio_list