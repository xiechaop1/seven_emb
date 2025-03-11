from xmlrpc.client import DateTime

import pygame
import os
from common.threading_event import ThreadingEvent
import logging
import time
import random
from base.messageid import messageid
from common.scence import Scence
from common.code import Code
from common.common import Common
from config.config import Config
from datetime import datetime

class AudioPlayer:

    PATH = "/tmp/"

    def __init__(self, spray, light):
        # 初始化 Pygame mixer
        pygame.mixer.init()
        # pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(1.0)
        self.audio_list = []  # 用于存储音频文件路径
        self.current_track = None  # 当前正在播放的音频
        self.current_bgm = None
        self.current_light = None
        self.current_spray = None

        self.current_audio_method = None

        self.is_interrupted = None
        self.played_list = []
        # self.playing_list = []
        self.spray = spray
        self.light = light
        self.i = 0
        self.voice_channel = pygame.mixer.Channel(1)
        self.continue_track = None

        # self.replay_idx = 0


    def audio_play_event_daemon(self):
        self.i = 0
        while True:
            print("playing event:",ThreadingEvent.audio_play_event.is_set())
            ThreadingEvent.audio_play_event.wait()
            # plCount = len(self.audio_list)
            # logging.info(f"AudioPlayer audio_list length:{self.i} {plCount}")

            if self.voice_channel.get_busy():
                time.sleep(0.5)
                continue

            # ThreadingEvent.audio_play_event.clear()
            self.play_audio(self.i)

            # while self.i < plCount:
            #     if self.voice_channel.get_busy() == False:
            #         print("play event:", ThreadingEvent.audio_play_event)
            #         if ThreadingEvent.audio_play_event.is_set():
            #             self.play_audio(self.i)
            #             self.i = self.i + 1
            #         else:
            #             break
            #     time.sleep(0.5)
            #
            # if self.i >= len(self.audio_list):
            #     # self.i = 0
            #     ThreadingEvent.audio_play_event.clear()
            #
            #     # 如果已经进入了助眠场景，语音播放完，解开阻塞
            #     if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
            #         logging.info("Sleep assistance event pass!")
            #         ThreadingEvent.camera_start_event.set()
            #         ThreadingEvent.recv_execute_command_event.set()
            #         # if self.replay_idx > 0:
            #         #     self.i = self.i + self.replay_idx - 1




    def audio_stop_event_daemon(self):
        ThreadingEvent.audio_stop_event.wait()
        self.stop_audio()
        # self.is_interrupted = 1
        self.interrupt()
        ThreadingEvent.audio_stop_event.clear()

    def save(self, audio_data, audio_file_tag = ""):
        path = self.PATH
        output_file_name = f"{path}{audio_file_tag}.mp3"
        with open(output_file_name, "wb") as pcm_file:
            pcm_file.write(audio_data)
        return output_file_name

    def add(self, audio_data, audio_file_tag = ""):
        """将音频文件路径添加到列表"""
        audio_data["timestamp"] = time.time()
        audio_data["i_datetime"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        audio_file = audio_data["filename"]
        msg_id = audio_data["msg_id"]
        # type = audio_file["type"]
        # wait_time = audio_file["wait_time"]
        if os.path.isfile(audio_file) or audio_data["seq_id"] == -1:
            # audio_data = {
            #     "filename": audio_file,
            #     "msg_id": msg_id,
            #     "type": type,
            #     "wait_time": wait_time
            # }
            self.audio_list.append(audio_data)

            # self.resume_interrupted()
            # if self.is_interrupted == 1 and self.voice_channel.get_busy():
            #     logging.info("set interrupted for add after playing")
            #     self.is_interrupted = 2     # 播完以后再重置
            # else:
            #     logging.info("set interrupted for add")
            #     ThreadingEvent.audio_play_event.set()
            #     self.is_interrupted = 0
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
            # self.is_interrupted = 0
            # self.clear_interrupt()
            audio_data = self.audio_list[index]
            logging.info(f"Playing: {index} {audio_data}")
            msg_id = audio_data["msg_id"]
            # audio_file = audio_data["filename"]
            # type = audio_data["type"]
            # wait_time = audio_data["wait_time"]
            latest_msg_id = messageid.get_latest_message_id()
            # if latest_msg_id != msg_id:
                # logging.error(f"Error: {msg_id} != {latest_msg_id}")
                # return
            if self.current_track is not None and self.voice_channel.get_busy():
                self.voice_channel.stop()  # 停止当前播放的音频

            # print("ad:",audio_data, self.audio_list)
            self.set_current_audio_method(audio_data["type"])
            self.play(audio_data)

            if audio_data["type"] == Code.REC_METHOD_VOICE_CHAT:
                if audio_data["seq_id"] == -1:

                    # self.resume_interrupted(msg_id, 2)

                    if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
                        time.sleep(5)
                        interrupt_flag = self.get_interrupt()
                        if interrupt_flag is None:
                            resume_rand_idx = random.randint(1, 6)
                            resume_audio_filename = f"resources/sound/flow_resume_0{resume_rand_idx}.mp3"
                        # self.play_voice_with_file(resume_audio_filename)

                            tmp_audio_data = {
                                "filename": resume_audio_filename,
                                "type": Code.EXECUTE_COMMAND_TIP_VOICE,
                                "wait_time": 0,
                                "msg_id": msg_id,
                                "seq_id": -1
                            }
                            # self.clear_list()

                            self.add(tmp_audio_data)

                            logging.info("Sleep assistance event pass!")
                            ThreadingEvent.camera_start_event.set()
                            ThreadingEvent.recv_execute_command_event.set()
                    # self.resume_interrupted(msg_id, 2)
                # else:
                #     if self.is_interrupted == 0:
                #         print("voice: set play event bec of interrupt is 0")
                #         ThreadingEvent.audio_play_event.set()

            elif audio_data["type"] == Code.REC_METHOD_VOICE_EXEC:
                if audio_data["scene_seq"] < 100:
                    if audio_data["scene_seq"] == audio_data["voice_count"] - 1:
                        ThreadingEvent.camera_start_event.set()
                        ThreadingEvent.recv_execute_command_event.set()
                    # else:
                    #     if self.is_interrupted == 0:
                    #         print("exec: set play event because of interrupt is 0")
                    #         ThreadingEvent.audio_play_event.set()
                else:
                    ThreadingEvent.camera_start_event.set()
                    ThreadingEvent.recv_execute_command_event.set()

                    if audio_data["scene_seq"] == audio_data["voice_count"] - 1:
                        self.resume_interrupted(msg_id, 1)

                    # 可能的bug，当正在播放坐起身，然后说话了，可能就没有打断，忽略了打断
                    # 想办法解决
            # elif audio_data["type"] == Code.EXECUTE_COMMAND_TIP_VOICE:
            #     ThreadingEvent.camera_start_event.set()
            #     ThreadingEvent.recv_execute_command_event.set()

            interrupt_flag = self.get_interrupt()
            print("play audio interrupt flag:", interrupt_flag)
            if interrupt_flag is None:
                print("self.i add,", self.i)
                # print(self.audio_list)
                self.i = self.i + 1
            else:
                if interrupt_flag["msg_id"] == msg_id:
                    print("self.i add by msg self,", self.i)
                    # print(self.audio_list)
                    self.i = self.i + 1

                if interrupt_flag["type"] == 2:
                    self.clear_interrupt()     # 如果是2，播完以后重置
                    logging.info("set interrupt to 0 from 2")
                    # ThreadingEvent.audio_play_event.set()

            # if self.i < len(self.audio_list):
            #     print("audio play event bec of len")
            #     ThreadingEvent.audio_play_event.set()

        else:
            logging.error(f"Error: Invalid index. {index} {len(self.audio_list)}")
            ThreadingEvent.audio_play_event.clear()
            # if len(self.audio_list) > 0:
                # self.i = 0
                # ThreadingEvent.audio_play_event.set()

    def play_audio_with_data(self, audio_data, is_temp_save = True):
        """从列表中播放指定索引的音频"""
        # if self.current_track is not None and pygame.mixer.music.get_busy():
        #     pygame.mixer.music.stop()  # 停止当前播放的音频
        # pygame.mixer.music.load(audio_file)  # 加载音频文件
        # pygame.mixer.music.play()  # 播放音频

        # self.is_interrupted = 0
        # self.clear_interrupt()
        logging.info("play with data")
        self.play(audio_data)

        if is_temp_save == True:
            self.current_track = audio_data
        # logging.info(f"Now playing: {audio_file}")

    def play_voice_with_file(self, filename):
        if filename == "" or filename is None:
            return
        logging.info(f"Playing voice with file:{filename}")
        voice = pygame.mixer.Sound(filename)
        self.voice_channel.play(voice)
        while self.voice_channel.get_busy():
            time.sleep(0.5)

        return

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

        if "light" in audio_data:
            if Config.IS_DEBUG == False:
                light = audio_data["light"]
                if light is not None:
                    if "rgb" in light:
                        light_rgb = light["rgb"]
                        # r, g, b = map(int, light_rgb.split(','))
                        light_mode = light["mode"]
                        # light_params = {
                        #     "r": r,
                        #     "g": g,
                        #     "b": b
                        # }
                        if light_mode != self.current_light:
                            # if light_mode == Code.LIGHT_MODE_STATIC:
                            self.light.start_with_code(light_mode, light_rgb)
                            self.current_light = light_mode

        # if "continue" in audio_data:
        #     if audio_data["continue"] == True:
        #         self.continue_track = audio_data

        if "spray" in audio_data:
            if audio_data["spray"] == "on" and audio_data["type"] != self.current_spray:
                self.current_spray = audio_data["spray"]
                ThreadingEvent.spray_start_event.set()
                # self.spray.shoot()
            elif audio_data["spray"] == "off" and audio_data["type"] != self.current_spray:
                ThreadingEvent.spray_start_event.clear()

        if bgm and bgm != self.current_bgm:
            bgm_file = "resources/background_music/" + bgm["filename"]
            logging.debug("start playing bgm, bgm_file: ", bgm_file)
            if os.path.isfile(bgm_file):
                pygame.mixer.music.load(bgm_file)  # 加载音频文件
                pygame.mixer.music.play(-1)
                self.current_bgm = bgm
        # else:
        #     pygame.mixer.music.stop()

        self.current_track = audio_data
        voice = pygame.mixer.Sound(audio_file)

        # self.playing_list.append(audio_data)
        # print("play")
        Common.set_latest_active_time(time.time())
        self.voice_channel.play(voice)

        # pygame.mixer.music.load(audio_file)  # 加载音频文件
        # ThreadingEvent.audio_play_event.set()
        # pygame.mixer.music.play()  # 播放音频
        while self.voice_channel.get_busy():
            time.sleep(0.05)
            # pygame.time.wait(50)
        # ThreadingEvent.audio_play_event.clear()
        # print("played")
        # if self.is_interrupted != 1:
        interrupt_flag = self.get_interrupt()
        print("play after interrupt flag:", interrupt_flag)
        if interrupt_flag is None:
            if wait_time > 0:
                # 如果不是被打断的，就需要等待一点时间
                time.sleep(wait_time)

            logging.info(f"Played: {audio_file}")
            self.played_list.append(audio_data)
            self.current_track = None
            self.continue_track = None
            # self.replay_idx = 0

            # if audio_data["type"] == Code.REC_METHOD_VOICE_CHAT:
            #     # 这里需要改一下，后端返回的需要是-1才能知道是结束
            #     if audio_data["seq_id"] == -1:
            #         if Scence.scence == Code.REC_ACTION_SLEEP_ASSISTANT:
            #             time.sleep(3)
            #             resume_rand_idx = random.randint(1, 6)
            #             resume_audio_filename = f"resources/sound/flow_resume_0{resume_rand_idx}.mp3"
            #             # self.play_voice_with_file(resume_audio_filename)
            #
            #             tmp_audio_data = {
            #                 "filename": resume_audio_filename,
            #                 "type": Code.EXECUTE_COMMAND_TIP_VOICE,
            #                 "wait_time": 0
            #             }
            #             self.add(tmp_audio_data)
            #
            #             logging.info("Sleep assistance event pass!")
            #             ThreadingEvent.camera_start_event.set()
            #             ThreadingEvent.recv_execute_command_event.set()
            #     else:
            #         ThreadingEvent.audio_play_event.set()
            #
            # elif audio_data["type"] == Code.REC_METHOD_VOICE_EXEC:
            #     if audio_data["scene_seq"] < 100:
            #         if audio_data["scene_seq"] == audio_data["voice_count"] - 1:
            #             ThreadingEvent.camera_start_event.set()
            #             ThreadingEvent.recv_execute_command_event.set()
            #         else:
            #             ThreadingEvent.audio_play_event.set()
            #     else:
            #         ThreadingEvent.camera_start_event.set()
            #         ThreadingEvent.recv_execute_command_event.set()
            # elif audio_data["type"] == Code.EXECUTE_COMMAND_TIP_VOICE:
            #     ThreadingEvent.camera_start_event.set()
            #     ThreadingEvent.recv_execute_command_event.set()

            # self.i = self.i + 1
            # ThreadingEvent.audio_play_event.set()
                # if self.replay_idx > 0:
                #     self.i = self.i + self.replay_idx - 1

    def replay(self):
        # audio_data = self.current_track
        logging.debug("replay")
        # if audio_data is not None:
        #     self.play_audio_with_data(audio_data, False)
        # ThreadingEvent.audio_play_event.set()
        # self.is_interrupted = 0
        self.resume_interrupted()
        return

    def resume_interrupted(self, msg_id = None, level = 1):
        # print("resume interrupted")
        interrupt_flag = self.get_interrupt()

        if interrupt_flag is not None:
            if interrupt_flag["level"] == level:
                if self.voice_channel.get_busy() and self.current_track is not None:
                    if msg_id is not None:
                        if interrupt_flag["msg_id"] == msg_id:
                            self.reset_interrupt(None, None, 0, 2)
                            logging.info(f"Resume interrupted after played: {msg_id}")
                        else:
                            logging.info(f"Can't resume interrupted after played: {msg_id}, {interrupt_flag['msg_id']}")
                    else:
                        self.reset_interrupt(None, None, 0, 2)
                        logging.info(f"Resume interrupted after played: None")
                else:
                    if interrupt_flag["msg_id"] is not None:
                        if msg_id is not None:
                            if interrupt_flag["msg_id"] == msg_id:
                                self.clear_interrupt()
                                ThreadingEvent.audio_play_event.set()
                                logging.info(f"Resume interrupted immediately: {msg_id}")
                        else:
                            self.clear_interrupt()
                            ThreadingEvent.audio_play_event.set()
                            logging.info(f"Resume interrupted immediately: None")
                    else:
                        self.clear_interrupt()
                        ThreadingEvent.audio_play_event.set()
                        logging.info(f"Resume interrupted immediately: flag no msg_id")



            else:
                print(f"Can't resume, {msg_id} - {interrupt_flag['msg_id']}, {level} - {interrupt_flag['level']}")
        else:
            logging.info(f"Resume interrupted with no interrupt")
            ThreadingEvent.audio_play_event.set()


        # if self.is_interrupted == 1 and self.voice_channel.get_busy() and self.current_track is not None:
        #     logging.info("Resume interrupted after played")
        #     self.is_interrupted = 2
        # else:
        #     logging.info("Resume interrupted now")
        #     self.is_interrupted = 0
        #     ThreadingEvent.audio_play_event.set()

    def stop_audio(self):
        """停止当前播放的音频"""
        playing_voice = self.get_current_track()
        if playing_voice is not None:
        #     print(playing_voice)
            if "continue" in playing_voice:
                if playing_voice["continue"] == True:
                    self.continue_track = playing_voice
        #             self.replay_idx = self.i
        #
        # print("replay_idx", self.replay_idx)

        if self.voice_channel.get_busy():
            self.voice_channel.stop()
            # print(self.voice_channel.get_busy())
            logging.info("Playback stopped.")
            self.current_track = None

        else:
            logging.warn("No audio is currently playing.")
        ThreadingEvent.audio_play_event.clear()

    def get_interrupt(self ):
        return self.is_interrupted

    def clear_interrupt(self):
        self.is_interrupted = None

    def reset_interrupt(self, msg_id = None, method = Code.REC_METHOD_VOICE_CHAT, level = 1, type = 1):
        interrupt_flag = self.get_interrupt()
        if interrupt_flag is None:
            interrupt_flag = {}
        if msg_id is not None:
            interrupt_flag["msg_id"] = msg_id
        if method is not None:
            interrupt_flag["method"] = method
        if level != 0:
            interrupt_flag["level"] = level
        if type != 0:
            interrupt_flag["type"] = type

        self.is_interrupted = interrupt_flag

    def interrupt(self, msg_id = None, method = Code.REC_METHOD_VOICE_CHAT, level = 1, type = 1):
        playing_voice = self.get_current_track()
        if playing_voice is not None:
            #     print(playing_voice)
            if "continue" in playing_voice:
                if playing_voice["continue"] == True:
                    self.continue_track = playing_voice

        # if self.voice_channel.get_busy():
        #     self.is_interrupted = 2
        # else:
        self.is_interrupted = {
            "method": method,
            "level": level,
            "type": type,
            "msg_id": msg_id
        }
        ThreadingEvent.audio_play_event.clear()
        logging.info("set interrupted")

    def stop_music(self):
        pygame.mixer.music.stop()
        ThreadingEvent.audio_play_event.clear()

    def clear_list(self):
        """清空音频列表"""
        self.audio_list.clear()
        self.i = 0
        logging.info("Audio list cleared.")

    def set_current_audio_method(self, method = Code.REC_METHOD_VOICE_CHAT):
        self.current_audio_method = method

    def get_current_audio_method(self):
        return self.current_audio_method

    def set_play_index(self, idx):
        self.i = idx

    def get_audio_list(self):
        """返回当前音频列表"""
        return self.audio_list

    def get_last_audio_list(self):
        if len(self.audio_list) > 0:
            return self.audio_list[-1]
        else:
            return None

    def get_played_list(self):
        return self.played_list

    def get_current_track(self):
        return self.current_track

    def set_current_light(self, mode):
        self.current_light = mode

    # def get_latest_playing(self):
    #     if len(self.played_list) == 0:
    #         return self.played_list[-1]
    #     else:
    #         return None

    def get_latest_played(self):
        if len(self.played_list) > 0:
            return self.played_list[-1]
        else:
            return None

    def is_playing(self):
        return self.voice_channel.get_busy()