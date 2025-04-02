import RPi.GPIO as GPIO
import time
import subprocess

from common.threading_event import ThreadingEvent


class Spray:
    # 延时函数

    SPRAY_PIN = 22

    def __init__(self):

        # # 设置GPIO模式
        # GPIO.setmode(GPIO.BCM)
        #
        # # 定义按键引脚
        # # KEY1_PIN = 17  # 对应按键1
        # KEYA_PIN = 17  # 对应按键A（已修改为GPIO17）
        # KEYB_PIN = 27  # 对应按键B（已修改为GPIO27）
        # DJ_PIN = 22  # 对应DJ引脚（模拟输出）
        #
        # # 初始化GPIO引脚为输入和输出
        # # GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.setup(KEYA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.setup(KEYB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.setup(DJ_PIN, GPIO.OUT)

        last_scent_spray_flag = ''

        # def scent_spray(scent_spray_flag):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SPRAY_PIN, GPIO.OUT)

        # self.gpio = GPIO

    def delayms(ms):
        time.sleep(ms / 1000.0)  # 转换为秒

    def turn_off(self):
        GPIO.output(self.SPRAY_PIN, GPIO.LOW)

    def shoot(self, times = 4, wait_time = 30):
        for i in range(times):
            for j in range(3):
                GPIO.output(self.SPRAY_PIN, GPIO.HIGH)
                time.sleep(0.08)
                GPIO.output(self.SPRAY_PIN, GPIO.LOW)
                time.sleep(0.05)
            print("GPIO.HIGH!")
            time.sleep(wait_time)

    def deal(self, times = 3, wait_time = 30):
        while True:
            ThreadingEvent.spray_start_event.wait()
            self.shoot(times, wait_time)
