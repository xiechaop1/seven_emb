#!/usr/bin/env python3

# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import argparse
import queue
import sys
import sounddevice as sd
import json
import time
import threading
import time
import json
import numpy as np
from vosk import Model, KaldiRecognizer

q = queue.Queue(maxsize=500)

xiaoqi_word=['小鸡','我去','小七','小区','小气','消气','小琴','小青','小憩','效期','校区','小觑','小曲','消去','小心','小新','区','亲','青','清','曲']
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def is_silent(data, threshold=1500):
    """检测是否为静音段。"""
    # 将字节数据转换为 numpy 数组
    audio_data = np.frombuffer(data, dtype=np.int16)
    # print("li_audio_data:",audio_data)
    # 检查最大值是否低于阈值
    # print("max:",np.max(np.abs(audio_data)))
    if np.max(np.abs(audio_data)) < threshold:
        # print("检测到静音")
        return True
    else:
        # print("未检测到静音")
        return False

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # print("indata:",bytes(indata))
    q.put(bytes(indata))

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        for i, device in enumerate(device_info):
            print("*****", f"{i}: {device}")
        index = 0
        decvice_info = sd.query_devices(index)
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    if args.model is None:
        # model = Model(lang="en-us")
        model = Model("/home/orangepi/vosk-model-small-cn-0.22")

    else:
        # model = Model(lang=args.model)
        model = Model("/home/orangepi/vosk-model-small-cn-0.22")

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize=4000, device=args.device,
                           dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        print("rec:",rec)

        while True:
            data = q.get()
            if is_silent(data):
                # print("检测到静音，跳过此段音频")
                continue  # 跳过静音段，进入下一个循环
            # 处理音频数据块
            if rec.AcceptWaveform(data):
                # 获取完整识别结果
                result = rec.Result()
                result_dict = json.loads(result)
                print("LI_Result_dict:", result_dict)
                text_content = result_dict['text']
                print(text_content)
                for word in xiaoqi_word:
                    if word in text_content:
                        print(f"识别到: {word}")
                    else:
                        pass
                        # print(f"未识别到 '小七'")
            else:
                pass
                # 处理部分识别结果
                # partial_result = rec.PartialResult()
                # partial_dict = json.loads(partial_result)
                #
                # # 检查部分结果是否包含 "小七"
                # if "小七" in partial_dict.get('partial', ''):
                #     print(f"识别到完整句子: {partial_dict['partial']}")
                #     # 这里可以直接调用 rec.Result() 作为最终结果处理
                #     result = rec.Result()  # 强制获取完整结果
                #     result_dict = json.loads(result)
                #     print(f"最终完整识别结果: {result_dict['text']}")
                # else:
                #     print(f"部分识别结果: {partial_dict['partial']}")



            # if rec.AcceptWaveform(data):
            #     print("rec.Result():",rec.Result())
            # else:
            #     print("rec.PartialResult():",rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))