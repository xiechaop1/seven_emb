import queue
import sounddevice as sd
import sys
import time
from vosk import Model, KaldiRecognizer, SpkModel
import json
import threading

SAMPLERATE_ORIG = 16000
SAMPLERATE_TARGET = 16000  # 目标采样率（VAD支持）

q = queue.Queue()

target_keywords = ["播放音乐", "七七", "停止", "抬头","拍照","休息"]
def detect_keywords(transcription):
    """从转录文本中检测关键词"""

    for word in target_keywords:
        if word in transcription:
            print(f"Keyword detected: {word}")

keywords = '["播放音乐", "七七", "停止", "抬头", "拍照","休息","[unk]"]'##########关键词必须完全一样才行
SPK_MODEL_PATH = "utils/vosk-model-spk-0.4"
model_path = "utils/vosk-model-small-cn-0.22"
# spk_li_1=[-0.297443, 0.138541, -0.480268, -0.20816, -0.181298, -0.639442, 0.21267, -0.555786, 1.005074, 0.011552, 1.985099, -0.568444, 0.520695, 0.221619, -0.442219, -0.352981, 1.291161, 0.58134, 1.671874, -1.298758, -0.395653, -0.401662, 2.137376, 0.174206, 0.570289, 0.01595, 1.390286, -0.475607, 1.212984, -0.195779, -0.038047, -0.18157, -0.598267, -0.97167, -0.560137, -0.021336, -1.152562, 0.948739, 0.765162, -0.550215, -1.161016, 1.401901, 0.383774, -0.220877, -0.638535, 1.118744, -0.51617, 0.952701, 0.540488, 0.459646, 0.337441, 1.287117, -1.81413, 0.807996, 0.418737, -1.263778, 0.068068, -1.384879, -1.70511, 1.647274, -0.842112, 0.111097, -0.736788, -2.329749, -2.008974, -1.564938, -0.335628, 0.184886, 0.943496, 0.770639, 1.692765, 0.082376, -1.156951, 0.097683, -1.031321, 1.875823, -1.600061, -1.14648, 0.628454, -0.386903, 1.692657, 0.846197, -0.966381, 1.106492, -0.734312, 0.077541, 0.689925, 0.817806, 0.971107, -0.693128, 0.986192, -0.015493, -1.595232, 0.250718, 0.381887, -0.662012, -0.158801, -0.679696, -0.487889, 2.454968, -1.054998, -1.543859, 0.815683, 1.125827, -0.15894, 1.941532, -0.684257, 0.595867, -0.239138, -1.711226, -0.669706, 1.655171, -1.010642, -0.764074, 1.118967, -1.066784, -1.645003, 0.38828, 0.085089, 0.470405, 0.969876, 0.572148, 0.61563, 0.815989, -0.234343, 2.112524, -0.769253, 0.585631]
spk_li_1=[-0.626114, 0.430365, 0.564255, -0.182698, 0.537145, 0.044097, 0.564515, 0.666896, 1.085733, -0.523695, 2.178851, -0.545808, 0.492513, -0.214256, 0.380257, 0.561458, 1.432191, 0.576447, 1.347584, -1.410213, -0.201343, 1.299883, 0.16591, -0.301386, 1.030398, -0.155679, 1.668122, -0.47749, 1.583658, 1.031789, -0.610194, 0.207826, -2.028657, -0.778005, 0.608732, -1.103482, -0.249394, -0.145279, -0.252108, -0.744611, -0.178013, 0.821876, 1.348644, 0.958709, -1.489057, -0.069446, 0.55689, 0.382191, 1.793885, 0.12014, 1.096465, 1.948748, -0.288994, -0.427686, -0.25332, -0.74351, 1.289284, -0.442085, -1.594271, 0.238896, -0.14475, -1.243948, -0.811971, -1.167681, -1.934597, -2.094246, 0.203778, 0.2246, 0.769156, 3.129627, 1.638138, -0.414724, 0.363555, 1.058113, -0.658691, 0.345854, -1.559133, 0.087666, 0.984442, -0.469354, 1.667347, 0.916898, -2.170697, 0.292812, 0.051197, 1.222564, 1.065773, -0.065279, 0.214764, -0.407425, 0.992222, -0.993893, 0.693716, 0.121084, 1.31698, 1.255295, -0.941613, 0.015467, 0.500375, -1.479744, -0.943895, -0.405701, 1.795941, -0.66203, 1.224589, 0.963079, -0.872087, 0.392804, 1.412374, -0.279257, -0.462107, 0.674435, 0.137653, 0.93439, 2.394885, -0.571315, 0.374555, -0.233448, 0.757664, -0.375494, 0.666074, -0.123803, 1.518769, 0.873773, -0.218161, 1.566089, -0.488127, 0.386693]
model = Model(model_path)
spk_model = SpkModel(SPK_MODEL_PATH)

rec = KaldiRecognizer(model, SAMPLERATE_ORIG, keywords)
rec.SetSpkModel(spk_model)

def main_callback(indata, frames, time1, status):
    global file_counter
    # 调用网络传输的处理函数

    # callback(indata, frames, time1, status)
    # callback2(indata, frames, time1, status)
    # 调用本地 Kaldi 处理的处理函数

    message_id = 1
    audio_data_dic = (bytes(indata), message_id)
    data = bytes(indata)
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # q.put(audio_data_dic)

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
            print(f"检测到qibao关键词: {target_keywords[1]}")
            # print(f"检测到qibao关键词: {phonemes}")

            # continue
        # else:
        #     # print("未检测到qibao关键词，xiaoqi_event.clear")
        #     xiaoqi_event.clear()

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
            print(f"检测到qibao关键词: {target_keywords[1]}")
            # print(f"检测到qibao关键词: {phonemes}")

            # continue
        # else:
        #     xiaoqi_event.clear()

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

    print("final:", rec.FinalResult())


def kaldi_listener():


    with sd.InputStream(samplerate=SAMPLERATE_ORIG, blocksize=8000, device=2,
                        dtype="int16", channels=1, callback=main_callback):
        while True:
            pass
            time.sleep(0.01)
            is_silent_flag = False
            # print("count2:",count2)
            # if count2 == 2:
            #     silent_start_time = time.time()
            # silent_end_time = time.time()
            # print("silent_end_time-slient_start_time:", silent_end_time - silent_start_time)
            # if count2 > 2 and silent_end_time - silent_start_time > 30:
            #     print("morre than 10s break!!!!!")
            #     running2 = False
            #     time.sleep(0.1)
            # running2 = True
            # print("running2:", running2)
            # time.sleep(0.01)
            audio_data_get = q.get()
            data, message_id_get = audio_data_get
            # xiaoqi_event_triggered = False
            # if is_silent(data):
                # print("检测到静音，跳过此段音频")
                # is_silent_flag = True
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
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")

                    continue
                # else:
                #     # print("未检测到qibao关键词，xiaoqi_event.clear")
                #     xiaoqi_event.clear()

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
                    print(f"检测到qibao关键词: {target_keywords[1]}")
                    # print(f"检测到qibao关键词: {phonemes}")

                    continue
                # else:
                #     xiaoqi_event.clear()

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


        print("final:", rec.FinalResult())

if __name__ == "__main__":
    kaldi_listener_thread = threading.Thread(target=kaldi_listener)
    kaldi_listener_thread.start()
