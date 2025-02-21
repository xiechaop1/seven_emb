import RPi.GPIO as GPIO
import time
import subprocess
# 设置GPIO模式
GPIO.setmode(GPIO.BCM)

# 定义按键引脚
# KEY1_PIN = 17  # 对应按键1
KEYA_PIN = 17  # 对应按键A（已修改为GPIO17）
KEYB_PIN = 27  # 对应按键B（已修改为GPIO27）
DJ_PIN = 22  # 对应DJ引脚（模拟输出）

# 初始化GPIO引脚为输入和输出
# GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEYA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEYB_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DJ_PIN, GPIO.OUT)
# 延时函数
def delayms(ms):
    time.sleep(ms / 1000.0)  # 转换为秒

class Spray:

    last_scent_spray_flag = ''

    def scent_spray(scent_spray_flag):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.OUT)

    while True:
        if self.last_scent_spray_flag == scent_spray_flag:
            continue
        if scent_spray_flag==True:
            for j in range(30):
                for i in range(3):
                    GPIO.output(22, GPIO.HIGH)
                    time.sleep(0.3)
                    GPIO.output(22, GPIO.LOW)
                    print("GPIO.HIGH!")
                    time.sleep(7.9)
        if scent_spray_flag == False:
            GPIO.output(22, GPIO.LOW)
            print("GPIO.LOW!")
            time.sleep(1)

        self.last_scent_spray_flag = scent_spray_flag

# # 使用示例
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     mic = Microphone()
#     mic.start_recording()

#     # 录音结束后，关闭麦克风
#     mic.close()