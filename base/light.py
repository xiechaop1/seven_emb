import threading
import time
import argparse
import logging
from common.code import Code
import wheel
from common.threading_event import ThreadingEvent
from config.config import Config
import random
import queue

from rpi_ws281x import *
if not Config.IS_DEBUG:
    if Config.OS is not None:
        if Config.OS == "pi5":
            from rpi_ws281x import PixelStrip, Color


# from adafruit_circuitpython_neopixel import NeoPixel



class Light:

    # LED strip configuration:
    # LED_COUNT = 112  # Number of LED pixels.
    LED_COUNT = 48  # Number of LED pixels.
    LED_PIN = 18  # 18      # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    BRIGHTNESS_MAX = 255

    LED_COUNT_PER_LINE = 6

    LED_LINE_COUNT = 8

    def __init__(self):
        # self.light_mode = ""

        self.strip = None
        if Config.OS is not None:
            if Config.OS == "pi5":
                self.strip = PixelStrip(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT,
                                        self.LED_BRIGHTNESS, self.LED_CHANNEL)
        if self.strip is None:
            self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA,
                                           self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()
        self.light_mode = None
        self.light_type = None
        self.last_light_mode = None
        self.last_light_params = None
        self.light_mode_queue = []
        self.current_color = None
        self.target_color = None
        self.target_params = None
        self.ts = 0
        self.run_ts = 0
        # self.light_nums = [40, 32, 24, 16]
        self.light_nums = [6,6,6,6,6,6,6,6]
        # self.light_sector_step = [
        #     5, 4, 3, 2
        # ]
        self.light_sector_step = [6,6,6,6,6,6,6,6]
        self.current_colors = []
        self.curr_light_buffer = []

        self.brightness = 255

        self.random_point_mode_colors = {
            "star": {
                "fore_colors": [
                    [0, 255, 0],
                ],
                "back_colors": [[4, 0, 20]],
                "group_num": 1,
                "rand_num_per_group": [
                    2,
                ],
                "times": 100,
                "duration": 1000,
            },
            "fire": {
                "fore_colors": [
                    [255, 0, 0],
                    [255, 177, 25]
                ],
                "back_colors": [
                    [0, 0, 0],
                    [255, 0, 0]
                ],
                "group_num": 1,
                "rand_num_per_groups": [
                    2,
                    2
                ],
                "times": 100,
                "duration": 500,
            }
        }

        self.sector_flow_mode_colors = {
            "colorful": [
                [255, 0, 0],
                [255, 3, 255],
                [15, 122, 255],
                [0, 222, 255],
                [3, 255, 3],
                [246, 255, 0],
                [255, 192, 0],
                [255, 96, 0]
            ],
            "star1": [
                [255, 176, 1],
                [1, 23, 61],
                [182, 11, 188],
                [127, 196, 255],
                [235, 113, 66],
                [0, 0, 48],
                [223, 255, 255],
                [0, 32, 65],
            ],
            "star2": [
                [124, 211, 255],
                [41, 0, 206],
                [255, 255, 255],
                [41, 0, 206],
                [124, 211, 255],
                [255, 255, 255],
                [41, 0, 206],
                [255, 255, 255],
            ],
            "star": [
                [0, 0, 0],
                [255, 255, 255],
                [0, 0, 0],
                [255, 255, 255],
                [0, 0, 0],
                [255, 255, 255],
                [0, 0, 0],
                [255, 255, 255],
            ],
            "jellyfish": [
                [0, 107, 239],
                [2, 224, 255],
                [0, 1, 26],
                [3, 100, 247],
                [0, 47, 212],
                [0, 0, 48],
                [3, 85, 255],
                [64, 224, 255],
            ]
        }

        # 把颜色填充
        for i in range(112):
            self.curr_light_buffer.append(Color(0,0,0))

    def daemon(self):
        while True:
            ThreadingEvent.light_daemon_event.wait()

            self.run_ts = time.time()
            light_mode = self.light_mode
            # if light_mode == self.last_light_mode:
            #     continue
            # self.last_light_mode = light_mode

            r = self.target_color["r"]
            g = self.target_color["g"]
            b = self.target_color["b"]

            params = self.target_params
            steps = None
            if "steps" in params:
                steps = params["steps"]

            if light_mode == Code.LIGHT_MODE_SECTOR_FLOWING:
                if "mode" in params:
                    mode = params["mode"]
                else:
                    mode = "colorful"
                self.sector_flowing(mode)
            elif light_mode == Code.LIGHT_MODE_RANDOM_POINT:
                if "fore_colors" in params:
                    fore_colors = params["fore_colors"]
                else:
                    fore_colors = [[255, 255, 255]]

                if "back_colors" in params:
                    back_colors = params["back_colors"]
                else:
                    back_colors = [[0, 0, 0]]

                if "rand_num_per_group" in params:
                    rand_num_per_groups = params["rand_num_per_groups"]
                else:
                    rand_num_per_groups = [1]

                if "group_num" in params:
                    group_num = params["group_num"]
                else:
                    group_num = 4

                if "times" in params:
                    times = params["times"]
                else:
                    times = 100

                if "duration" in params:
                    duration = params["duration"]
                else:
                    duration = 1000

                if "mode" in params:
                    mode = params["mode"]
                else:
                    mode = None


                self.random_point(mode, fore_colors, back_colors, rand_num_per_groups, group_num, times, duration)
            elif light_mode == Code.LIGHT_MODE_WAVE:
                if "fore_color" in params:
                    fore_color = params["fore_color"]
                else:
                    fore_color = [255, 255, 255]

                if "back_color" in params:
                    back_color = params["back_color"]
                else:
                    back_color = None

                if "max_wave_num" in params:
                    max_wave_num = params["max_wave_num"]
                else:
                    max_wave_num = 2

                if "wait_ms" in params:
                    wait_ms = params["wait_ms"]
                else:
                    wait_ms = 100

                self.wave_line(fore_color, back_color, max_wave_num, wait_ms)

            elif light_mode == Code.LIGHT_MODE_STATIC:
                self.Static(r, g, b)
            elif light_mode == Code.LIGHT_MODE_GRADIENT:
                self.Gradient(r, g, b)
            elif light_mode == Code.LIGHT_MODE_BREATHING:
                if steps is None:
                    self.Breathing(r, g, b)
                else:
                    self.Breathing(r, g, b, steps)
            elif light_mode == Code.LIGHT_MODE_CIRCLE:
                keys = ["r1", "g1", "b1", "r2", "g2", "b2", "time_duration", "times"]

                input ={
                    "r1": 0,
                    "g1": 0,
                    "b1": 0,
                    "r2": 255,
                    "g2": 255,
                    "b2": 255,
                    "times": -1,
                    "time_duration": 0,
                }

                for key in keys:
                    if key in params:
                        input[key] = params[key]

                self.circle(input["r1"], input["g1"], input["b1"], input["r2"], input["g2"], input["b2"], input["time_duration"], input["times"])
            elif light_mode == Code.LIGHT_MODE_CIRCLE_RAINBOW:
                color_list = []
                self.rainbow_circle(color_list)
            else:
                self.turn_off()

    def set_brightness(self, brightness):
        self.brightness = brightness

    def set_high(self, duration = 50):
        brightness = self.brightness
        new_brightness = brightness + duration
        if new_brightness > self.BRIGHTNESS_MAX:
            new_brightness = self.BRIGHTNESS_MAX
        self.set_brightness(new_brightness)
        logging.info(f"Set brightness high from {brightness} to {new_brightness}")

    def set_low(self, duration = 50):
        brightness = self.brightness
        new_brightness = brightness - duration
        if new_brightness < 0:
            new_brightness = 0
        self.set_brightness(new_brightness)
        logging.info(f"Set brightness low from {brightness} to {new_brightness}")

    def set_mode(self, mode):
        self.light_mode = mode
        self.ts = time.time()
        ThreadingEvent.light_daemon_event.set()
        return True

    def set_target_params(self, params = {}):
        self.target_params = params
        return True

    def set_target_color(self, rgb_color):
        r, g, b = map(int, rgb_color.split(','))
        self.target_color = {"r": r, "g": g, "b": b}
        return True

    def start_prev(self):
        for last_light_data in self.light_mode_queue[::-1]:
            last_light_mode = last_light_data["light_mode"]
            last_light_params = last_light_data["light_params"]
            last_type = last_light_data["type"]
            if last_type != Code.LIGHT_TYPE_TEMP:
                self.start(last_light_mode, last_light_params)
                break

    def start(self, light_mode, params, type = Code.LIGHT_TYPE_SET):
        if "r" in params:
            r = params["r"]
        else:
            r = 0
        if "g" in params:
            g = params["g"]
        else:
            g = 0
        if "b" in params:
            b = params["b"]
        else:
            b = 255

        self.set_target_params(params)
        self.set_target_color(f"{r},{g},{b}")

        if type == Code.LIGHT_TYPE_SET and self.light_type == Code.LIGHT_TYPE_DIY:
            logging.warn(f"Set light mode to {type} failed, now is DIY")
            return

        if light_mode is not None:
            # self.last_light_mode = self.light_mode
            # self.last_light_params = self.target_params
            self.set_mode(light_mode)

            self.light_mode_queue.append({
                "light_mode": light_mode,
                "light_params": params,
                "type": type
            })
            logging.info(f"Set light mode to mode: {light_mode}, type: {type}, params: {params}")

        return True


    def start_with_code(self, light_code, light_rgb):
        light_mode = None
        code_map = Code.lightModelMap()
        if light_code in code_map:
            light_mode = code_map[light_code]

        self.set_target_color(light_rgb)
        if light_mode is not None:
            self.set_mode(light_mode)

        return True

    def rainbow_circle(self, colors = []):
        if len(colors) == 0:
            colors = [
                # [255, 0, 0],
                # [128, 128, 0],
                # [96, 128, 128],
                # [0, 255, 128],
                # [0, 255, 255],
                # [0, 128, 255],
                # [0, 0, 255]
                [255, 0, 0],
                [255, 3, 255],
                [15, 122, 255],
                [0, 222, 255],
                [3, 255, 3],
                [246, 255, 0],
                [255, 192, 0],
                [255, 96, 0]
            ]

        def_color = [0, 0, 0]

        color_idx = 0
        color_num = 4
        color_buffer = []
        while True:
            if self.light_mode != Code.LIGHT_MODE_CIRCLE_RAINBOW or self.ts > self.run_ts:
                break

            if color_idx >= len(colors):
                color_idx = 0

            # color_buffer = []
            for color_pos in range(len(self.light_nums)):
                # color_buffer.append(colors[color_idx])
                color_i = color_idx + color_pos
                color_i = color_i % len(colors)
                if color_i >= len(colors):
                    color_buffer = def_color
                else:
                    color_buffer = colors[color_i]
                # print(color_buffer_idx, len(color_buffer))
                threading.Thread(target=self.rainbow_circle_exec, args=(color_pos, color_buffer)).start()
                time.sleep(0.01)
            time.sleep(2)

            color_idx += 1


    def rainbow_circle_exec(self, idx, color):
        if idx < len(self.current_colors):
            curr_color = self.current_colors[idx]
        else:
            curr_color = [0, 0, 0]

        curr_r, curr_g, curr_b = curr_color
        r, g, b = color

        num = self.light_nums[idx]
        start = 0
        if idx > 0:
            total = 0
            for light_idx, val in enumerate(self.light_nums):
                if light_idx < idx:
                    start += val

        if idx < len(self.current_colors):
            self.current_colors[idx] = color
        else:
            self.current_colors.append(color)
        self.fade(curr_r, curr_g, curr_b, r, g, b, start, num)


    def wave_line(self, fore_color, back_color = None, max_wave_num = 2, wait_ms = 100):
        if back_color is None:
            back_color = [0, 0, 0]

        # 描绘半层前景色
        start_num = 0
        init_color_buffer = []
        init_color2_buffer = []
        init_start_buffer = []
        init_num_buffer = []
        last_buffer = []
        for idx, light_num in enumerate(self.light_nums):
            half_line = light_num // 2

            init_color_buffer.append(fore_color)
            init_start_buffer.append([start_num])
            init_num_buffer.append([half_line])
            init_color2_buffer.append([0, 0, 0])

            init_color_buffer.append(back_color)
            init_start_buffer.append([half_line])
            init_num_buffer.append([half_line])
            init_color2_buffer.append([0, 0, 0])

            last_buffer.append({
                "buff": 0,
                "add_tag": 1,
                "color": fore_color
            })
            start_num += light_num

        self.fade_total_by_range(init_color_buffer, init_color2_buffer, init_start_buffer, init_num_buffer)

        add_tag = 1
        add_num_buffer = 1
        add_num = 1

        while True:
            if self.light_mode != Code.LIGHT_MODE_WAVE or self.ts > self.run_ts:
                break

            params = []
            last_buffer_temp = []
            start_num = 0
            for idx, light_num in enumerate(self.light_nums):
                half_line = light_num // 2
                if idx > 0:
                    last_buff = last_buffer[idx - 1]
                    buff = last_buff["buff"]
                    curr_color = last_buff["color"]
                else:
                    last_buff = last_buffer[0]
                    buff = last_buff["buff"]

                    if buff == max_wave_num or buff == (-1 * max_wave_num):
                        if add_num_buffer == 1:
                            add_num_buffer = 0
                            add_tag = (-1) * add_tag
                        else:
                            add_num_buffer = 1

                        add_num = add_num_buffer * add_tag

                    buff += add_num

                    # if buff == max_wave_num or buff == (-1 * max_wave_num):
                    #     break

                    if add_tag < 0:
                        curr_color = back_color
                    else:
                        curr_color = fore_color

                start = start_num + half_line + buff

                r, g, b = curr_color

                # start = start_line + buff

                params.append({
                    "r": r,
                    "g": g,
                    "b": b,
                    "start": start,
                    "num": 1
                })

                last_buffer_temp.append({
                    "buff": buff,
                    "add_tag": add_tag,
                    "color": curr_color
                }
                )
                start_num += light_num

                # duration = wait_ms / 1000
            last_buffer = last_buffer_temp
            # if buff == max_wave_num or buff == (-1 * max_wave_num):
            #     continue

            # print("params: ", params)
            # print("last:", last_buffer)
            self.show_color_by_range(params)

            duration = wait_ms / 1000
            time.sleep(duration)



    def wave(self, fore_color, back_color = None, max_wave_num = 2, wait_ms = 100):
        if back_color is None:
            back_color = [0, 0, 0]

        start = 0
        quarter_line = []
        last_buffer = []

        fore_r, fore_g, fore_b = fore_color
        back_r, back_g, back_b = back_color

        init_color_buffer = []
        init_color2_buffer = []
        # init_start_buffer = {
        #     "fore": [],
        #     "back": [],
        # }
        # init_num_buffer = {
        #     "fore": [],
        #     "back": [],
        # }

        init_start_buffer = []
        init_num_buffer = []

        # init_color_buffer.append(fore_color)
        # init_color_buffer.append(back_color)
        #
        # init_color2_buffer.append([0, 0, 0])
        # init_color2_buffer.append([0, 0, 0])

        right_line = []
        for idx, light_num in enumerate(self.light_nums):
            quarter_num = int(light_num / 4)
            half_num = int(light_num / 2)

            quarter_line_r = start + quarter_num
            quarter_line.append(quarter_line_r)
            right_line.append(quarter_line_r)

            init_color_buffer.append(back_color)
            init_start_buffer.append([start])
            init_num_buffer.append([quarter_num])
            init_color2_buffer.append([0, 0, 0])

            init_color_buffer.append(fore_color)
            init_start_buffer.append([quarter_line_r])
            init_num_buffer.append([half_num + 1])
            init_color2_buffer.append([0, 0, 0])

            start += light_num
            last_buffer.append({
                "buff": 0,
                "add_tag": 1,
                "color": fore_color
            })

        start = 0
        left_line = []
        for idx, light_num in enumerate(self.light_nums):
            quarter_num = int(light_num / 4)
            half_num = int(light_num / 2)

            quarter_line_l = start + quarter_num + half_num + 1
            left_line.append(quarter_line_l)

            init_color_buffer.append(back_color)
            init_start_buffer.append([quarter_line_l + 1])
            init_num_buffer.append([quarter_num])
            init_color2_buffer.append([0, 0, 0])
            start += light_num

        for idx, quarter_line_l in enumerate(left_line[::-1]):
            quarter_line.append(quarter_line_l)

            last_buffer.append({
                "buff": 0,
                "add_tag": 1,
                "color": back_color
            })


        # start_buffer = []
        # start_buffer.append(init_start_buffer["fore"])
        # start_buffer.append(init_start_buffer["back"])
        #
        # num_buffer = []
        # num_buffer.append(init_num_buffer["fore"])
        # num_buffer.append(init_num_buffer["back"])

        self.fade_total_by_range(init_color_buffer, init_color2_buffer, init_start_buffer, init_num_buffer)

        add_tag = 1
        add_num_buffer = 1
        add_num = 1
        # params = []
        while True:
            if self.light_mode != Code.LIGHT_MODE_WAVE or self.ts > self.run_ts:
                break

            params = []
            last_buffer_temp = []
            for idx, start_line in enumerate(quarter_line):
                if idx > 0:
                    last_buff = last_buffer[idx - 1]
                    buff = last_buff["buff"]
                    curr_color = last_buff["color"]
                    # if buff == max_wave_num or buff == (-1 * max_wave_num):
                    #     continue
                else:
                    last_buff = last_buffer[0]
                    buff = last_buff["buff"]
                    # curr_color = back_color

                    if buff == max_wave_num or buff == (-1 * max_wave_num):
                        if add_num_buffer == 1:
                            add_num_buffer = 0
                            add_tag = (-1) * add_tag
                        else:
                            add_num_buffer = 1

                        add_num = add_num_buffer * add_tag


                    buff += add_num

                    # if buff == max_wave_num or buff == (-1 * max_wave_num):
                    #     break

                    if add_tag > 0:
                        curr_color = back_color
                    else:
                        curr_color = fore_color

                if start_line in right_line:
                    start = start_line + buff
                else:
                    start = start_line - buff

                r, g, b = curr_color

                # start = start_line + buff

                params.append({
                    "r": r,
                    "g": g,
                    "b": b,
                    "start": start,
                    "num": 1
                })

                last_buffer_temp.append({
                        "buff": buff,
                        "add_tag": add_tag,
                        "color": curr_color
                    }
                )

                # duration = wait_ms / 1000
            last_buffer = last_buffer_temp
            # if buff == max_wave_num or buff == (-1 * max_wave_num):
            #     continue

            # print("params: ", params)
            # print("last:", last_buffer)
            self.show_color_by_range(params)

            duration = wait_ms / 1000
            time.sleep(duration)





        # back_r, back_g, back_b = back_color
        # self.Gradient(back_r, back_g, back_b)




    def random_point(self, mode, fore_colors, back_colors = None, rand_num_per_groups = [], group_num = 3, times = 3, duration = 1000):
        # fore_r, fore_g, fore_b = fore_color
        # self.Gradient(fore_r, fore_g, fore_b)

        if mode is not None:
            if "fore_colors" in self.random_point_mode_colors[mode]:
                fore_colors = self.random_point_mode_colors[mode]["fore_colors"]
            else:
                fore_colors = [[255,255,255]]

            if "back_colors" in self.random_point_mode_colors[mode]:
                back_colors = self.random_point_mode_colors[mode]["back_colors"]
            else:
                back_colors = [[0,0,0]]

            # back_color = self.random_point_mode_colors[mode]["back_colors"]
            if "rand_num_per_groups" in self.random_point_mode_colors[mode]:
                rand_num_per_groups = self.random_point_mode_colors[mode]["rand_num_per_groups"]
            else:
                rand_num_per_groups = [3]

            if "group_num" in self.random_point_mode_colors[mode]:
                group_num = self.random_point_mode_colors[mode]["group_num"]
            else:
                group_num = 1

            if "times" in self.random_point_mode_colors[mode]:
                times = self.random_point_mode_colors[mode]["times"]
            else:
                times = 10

            if "duration" in self.random_point_mode_colors[mode]:
                duration = self.random_point_mode_colors[mode]["duration"]
            else:
                duration = 1000

            # rand_num_per_groups = self.random_point_mode_colors[mode]["rand_num_per_groups"]
            # group_num = self.random_point_mode_colors[mode]["group_num"]
            # times = self.random_point_mode_colors[mode]["times"]
            # duration = self.random_point_mode_colors[mode]["duration"]

        back_color = back_colors[0]

        if back_color is None:
            back_color = [0, 0, 0]

        back_r, back_g, back_b = back_color
        self.Gradient(back_r, back_g, back_b)

        if len(back_colors) > 1:
            bottem_layer = [[
                [16, 9],
                [54, 5]
            ]]
            bottom_starts = []
            bottom_nums = []
            for _, bottom_pos in enumerate(bottem_layer[0]):
                start, num = bottom_pos
                bottom_starts.append(start)
                bottom_nums.append(num)
            self.fade_total_by_range([back_colors[1]], [back_color], [bottom_starts], [bottom_nums])

        if times == -1:
            times = 1000000000

        for i in range(times):
            if self.light_mode != Code.LIGHT_MODE_RANDOM_POINT or self.ts > self.run_ts:
                break

            for group_idx in range(group_num):
                point_starts = []
                point_nums = []
                rgb1 = []
                rgb2 = []

                pre_time = random.randint(0, duration)
                time.sleep(int(pre_time // 1000))
                for fore_idx, fore_color in enumerate(fore_colors):
                    rand_num_per_group = rand_num_per_groups[fore_idx]
                    for j in range(rand_num_per_group):
                        nums = []
                        # 最内两圈灯珠一共40个
                        # rand_pos = random.randint(self.LED_COUNT - 40, self.LED_COUNT - 1)
                        rand_pos = random.randint(0, self.LED_COUNT - 1)
                        point_starts.append([rand_pos])
                        rgb1.append(fore_color)
                        rgb2.append(back_color)
                        nums.append(1)
                        point_nums.append(nums)
                threading.Thread(target=self.random_point_exec, args=(rgb1, rgb2, point_starts, point_nums, duration, pre_time)).start()
            time.sleep(duration / 1000 * 2)

    def random_point_exec(self, rgb1, rgb2, point_starts, nums, duration = 5000, pre_time = 0):
        self.fade_total_by_range(rgb1, rgb2, point_starts, nums)
        time.sleep(int(duration // 1000))
        self.fade_total_by_range(rgb2, rgb1, point_starts, nums)


    def sector_flowing(self, color_mode):
        time_duration = 50           # ms
        sector_num = 8

        colors = self.sector_flow_mode_colors[color_mode]
        # colors = [
        #     [255, 0, 0],
        #     [255, 3, 255],
        #     [15, 122, 255],
        #     [0, 222, 255],
        #     [3, 255, 3],
        #     [246, 255, 0],
        #     [255, 192, 0],
        #     [255, 96, 0]
        # ]

        sector_color_old = []
        # sector_buffer = []
        line_num = 4
        sector_area = []
        sector_step = []
        for idx in range(sector_num):
            sector_buffer = []
            first_num = 0
            for l_idx in range(line_num):

                if l_idx > 0:
                    max_num = self.light_nums[l_idx - 1]
                else:
                    max_num = 0

                first_num += max_num

                sector_start = first_num + self.light_sector_step[l_idx] * idx

                sector_buffer.append(sector_start)
            sector_area.append(sector_buffer)
            sector_step.append(self.light_sector_step)

        steps = 0
        sector_pos = 0
        sector_color_old = []

        while True:
            if self.light_mode != Code.LIGHT_MODE_SECTOR_FLOWING or self.ts > self.run_ts:
                break
            curr_colors = []
            curr_sector = []
            # sector_color_old = []
            for step, color in enumerate(colors):

                sector_pos = step + steps
                show_pos = sector_pos % sector_num

                sector = sector_area[show_pos]
                curr_sector.append(sector)

                if show_pos < len(sector_color_old):
                    old_color = sector_color_old[show_pos]
                else:
                    old_color = [0, 0, 0]
                    sector_color_old.append([0, 0, 0])

                old_r, old_g, old_b = old_color
                curr_r, curr_g, curr_b = color

                curr_colors.append(colors[show_pos])

                # self.fade_by_range(color, old_color, sector, self.light_sector_step)

                # threading.Thread(target=self.fade_total_by_range,
                #                 args=(curr_colors, sector_color_old, sector, self.light_sector_step)).start()

                # if  show_pos < len(sector_color_old):
                #     sector_color_old[step] = colors[show_pos]
                # else:
                #     sector_color_old.append(colors[show_pos])

                # for one_idx, sector_one in enumerate(sector):
                #     # for one_idx in range(sector_one - 1):
                #     threading.Thread(target=self.fade_by_rage, args=(color, old_color, sector_one, self.light_sector_step[one_idx])).start()

            self.fade_total_by_range(curr_colors, sector_color_old, sector_area, sector_step)
            sector_color_old = curr_colors
            steps += 1

            time.sleep(time_duration / 1000)




    def circle2(self, r1, g1, b1, r2, g2, b2, time_duration, times):
        steps = 4
        nums = self.light_nums
        step_r = (r2 - r1) / (steps - 1)
        step_g = (g2 - g1) / (steps - 1)
        step_b = (b2 - b1) / (steps - 1)



    def circle(self, r1, g1, b1, r2, g2, b2, wait_ms = 0, times = -1):

        steps = 4
        # nums = [40, 32, 24, 16]
        nums = self.light_nums

        step_r = (r2 - r1) / (steps - 1)
        step_g = (g2 - g1) / (steps - 1)
        step_b = (b2 - b1) / (steps - 1)

        curr_times = 0
        while True:
            if self.light_mode != Code.LIGHT_MODE_CIRCLE or self.ts > self.run_ts:
                break

            if times > 0 and curr_times >= times:
                break

            params = []
            i = 0
            start = 0
            for i in range(steps):
                r = int(r1 + step_r * i)
                g = int(g1 + step_g * i)
                b = int(b1 + step_b * i)

                params.append({"r": r, "g": g, "b": b, "start": start, "num": nums[i]})
                start = start + nums[i]

            self.show_color_by_range(params, wait_ms / 1000)

            if times > 0 or times == -1:
                time.sleep(1)

                self.clear()

                i = 0
                params = []
                for i in range(steps):
                    r = int(r2 + (-1) * step_r * i)
                    g = int(g2 + (-1) * step_g * i)
                    b = int(b2 + (-1) * step_b * i)

                    nums_idx = steps - i - 1

                    start = start - nums[nums_idx]
                    params.append({"r": r, "g": g, "b": b, "start": start, "num": nums[nums_idx]})

                self.show_color_by_range(params, wait_ms / 1000)

                time.sleep(1)
                self.clear()
            elif times == 0:
                break

            curr_times += 1

        return

    def colorWipe2(self, strip, color, wait_ms=100):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe2 act.")
        # for i in range(self.strip.numPixels()):
            # self.strip.setPixelColor(i, color)
            # self.strip.show()
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    # Define functions which animate LEDs in various ways.
    def colorWipe(self, strip, color, wait_ms=40):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe act.")
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()
            # time.sleep(wait_ms/1000.0)

    def colorWipe_single(self, strip, color, wait_ms=40):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe_single act.")
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
    def theaterChase(self, strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        # print("theaterChase act.")
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)


    def Gradient(self, r, g, b):

        old_color = self.get_color()
        if old_color is None:
            old_color = {
                "r": 0,
                "g": 0,
                "b": 0,
            }

        self.fade(old_color['r'], old_color['g'], old_color['b'], r, g, b)
        self.fill_light_buffer(r, g, b)

        return

    def overflowing(self, line_num = 1, light_num = 7, steps = 5):

        colors = [
            [255, 0, 0],
            [128, 128, 0],
            [96, 128, 128],
            [0, 255, 128],
            [0, 255, 255],
            [0, 128, 255],
            [0, 0, 255]
        ]

        for i in range(line_num):
            line_pos = random.randint(1, 4)
            light_max = self.light_nums[light_num - 1]
            start = random.randint(0, light_max)

            color_idx = random.randint(0, len(colors) - 1)
            color = colors[color_idx]




    def fade_total_by_range(self, rgbs1 = [], old_rgbs2 = [], starts = [], nums = [], steps = 100):
        if len(starts) == 0:
            return

        if len(rgbs1) != len(old_rgbs2) or len(rgbs1) == 0:
            return

        for i in range(steps + 1):
            for idx, rgb1 in enumerate(rgbs1):
                r1, g1, b1 = rgb1
                if idx > len(old_rgbs2):
                    r2 = g2 = b2 = 0
                else:
                    r2, g2, b2 = old_rgbs2[idx]

                step_r = (r1 - r2) / steps
                step_g = (g1 - g2) / steps
                step_b = (b1 - b2) / steps

                r = int(r2 + step_r * i)
                g = int(g2 + step_g * i)
                b = int(b2 + step_b * i)
                self.show_color_by_range_buffer(r, g, b, starts[idx], nums[idx])
            self.show_color_by_buffer()

        return

    def fade(self, r1, g1, b1, r2 = 0, g2 = 0, b2 = 255, start = 0, num = 0, steps = 100, wait_time = 0.2):
        step_r = (r2 - r1) / steps
        step_g = (g2 - g1) / steps
        step_b = (b2 - b1) / steps

        for i in range(steps + 1):
            r = int(r1 + step_r * i)
            g = int(g1 + step_g * i)
            b = int(b1 + step_b * i)
            if start > 0 or num > 0:
                self.show_color(r, g, b, start, num)
            else:
                self.show_color(r, g, b)

        return

    def Gradient1(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        # print("wheel act.")
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def Shadowing(self, strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        # print("rainbow act.")
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self, strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        # print("rainbowCycle act.")
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self, strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        # print("theaterChaseRainbow act.")
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, wheel((i+j) % 255))
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)


    def BreathWithTwoColor(self, r1, g1, b1, r2, g2, b2, wait_time = 0.2):
        rtag = 1
        if r1 > r2:
            rt = r1 - r2
            rtag = -1
        else:
            rt = r2 - r1

        gtag = 1
        if g1 > g2:
            gt = g1 - g2
            gtag = -1
        else:
            gt = g2 - g1

        btag = 1
        if b1 > b2:
            bt = b1 - b2
            btag = -1
        else:
            bt = b2 -b1

        m = max(rt, gt, bt)
        step = 1
        while True:
            if self.light_mode != 'breath2Color':
                break
            for i in range(m):
                if (r1 > r2 and rt > r2 + step) or (r1 < r2 and rt < r2 - step):
                    rt = rt + rtag * step
                else:
                    rt = r2
                if (g1 > g2 and gt > g2 + step) or (g1 < g2 and gt < g2 - step):
                    gt = gt + gtag * step
                else:
                    gt = g2
                if (b1 > b2 and bt > b2 + step) or (b1 < b2 and bt < b2 - step):
                    bt = bt + btag * step
                else:
                    bt = b2
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r2 and gt == g2 and bt == b2:
                    break
                self.strip.show()
                time.sleep(wait_time)

            for i in range(m):
                if (r1 > r2 and rt < r1 - step) or (r1 < r2 and rt > r1 + step):
                    rt = rt - rtag * step
                else:
                    rt = r1
                if (g1 > g2 and gt < g1 - step) or (g1 < g2 and gt > g1 + step):
                    gt = gt - gtag * step
                else:
                    gt = g1
                if (b1 > b2 and bt < b1 - step) or (b1 < b2 and bt > b1 + step):
                    bt = bt - btag * step
                else:
                    bt = b1
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r1 and gt == g1 and bt == b1:
                    break
                self.strip.show()
                time.sleep(wait_time)

    def Breathing(self, r, g, b, steps = 200, wait_ms = 200):
        start = self.LED_COUNT
        start_idx = 0
        while True:
            if self.light_mode != Code.LIGHT_MODE_BREATHING or self.ts > self.run_ts:
                break

            for idx, num in enumerate(self.light_nums[::-1]):
                start -= num
                if idx < start_idx:
                    continue
                self.fade(0, 0, 0, r, g, b, start, num, 50)
            time.sleep(wait_ms/1000.0)
            start = 0
            for idx, num in enumerate(self.light_nums):
                if idx > len(self.light_nums) - 2:
                    start += num
                    continue
                self.fade(r, g, b, 0, 0, 0, start, num, 50)
                start += num
            time.sleep(wait_ms/1000.0)
            start_idx = 1

    def BreathingOld(self, r, g, b, steps = 200, wait_ms = 200):
        """ 计算两个颜色之间的渐变值 """
        # step_r = (color2[0] - color1[0]) / steps
        # step_g = (color2[1] - color1[1]) / steps
        # step_b = (color2[2] - color1[2]) / steps

        rt = r
        gt = g
        bt = b

        while True:
            if self.light_mode != Code.LIGHT_MODE_BREATHING or self.ts > self.run_ts:
                break

            step_r = rt / steps
            step_g = gt / steps
            step_b = bt / steps

            # gradient = []
            for i in range(steps + 1):
                r1 = int(step_r * i)
                g1 = int(step_g * i)
                b1 = int(step_b * i)
                # gradient.append((r1, g1, b1))

                self.show_color(r1, g1, b1)
            time.sleep(wait_ms / 1000.0)

            # time.sleep(wait_ms/1000.0)

            for j in range(steps + 1):
                r2 = r1 - int(step_r * j)
                g2 = g1 - int(step_g * j)
                b2 = b1 - int(step_b * j)
                self.show_color(r2, g2, b2)

            time.sleep(wait_ms / 1000.0)

        # return gradient

    def GradientOld(self, r, g, b, wait_time = 0.2):
        m = max(r, g, b)
        rt = r
        gt = g
        bt = b
        step = 1
        while True:
            if self.light_mode != Code.LIGHT_MODE_GRADIENT:
                break
            for i in range(m):
                if rt > step:
                    rt = rt - step
                else:
                    rt = 0
                if gt > step:
                    gt = gt - step
                else:
                    gt = 0
                if bt > step:
                    bt = bt - step
                else:
                    bt = 0
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == 0 and gt == 0 and bt == 0:
                    break
                self.strip.show()
                time.sleep(wait_time)

            for i in range(m):
                if rt < r:
                    rt = rt + step
                else:
                    rt = r
                if gt > g:
                    gt = gt + 1
                else:
                    gt = g
                if bt > b:
                    bt = bt + 1
                else:
                    bt = b
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r and gt == g and bt == b:
                    break
                self.strip.show()
                time.sleep(wait_time)

    def Static(self, r, g, b):
        # print("r,g,b:",r,g,b)
        # # for j in range(255):
        # for i in range(self.strip.numPixels()):
        #     self.strip.setPixelColor(i, Color(r, g, b))
        #     # print("j:", j)
        # self.strip.show()
        # # time.sleep(0.01)
        # # time.sleep(2)
        self.show_color(r, g, b)



    def get_color(self):
        return self.current_color

    def show_color_by_range(self, params_range = [], time_duration = 0):
        if len(params_range) == 0:
            return

        for p in params_range:
            r, g, b = p["r"], p["g"], p["b"]
            if "start" in p:
                start = p["start"]
            else:
                start = 0

            if "num" in p:
                num = p["num"]
            else:
                num = 0

            self.show_color(r, g, b, start, num)

            if time_duration > 0:
                time.sleep(time_duration)

        return

    def show_color_with_rgb_by_range_buffer(self, rgb, start, num):
        r, g, b = rgb

        self.save_color_to_buffer(r, g, b, start, num)

    def show_color_by_range_buffer(self, r, g, b, starts = [], nums = []):
        if len(starts) == 0:
            return

        for idx, start in enumerate(starts):
            num = nums[idx]

            for i in range(num):
                self.save_color_to_buffer(r, g, b, start, num)

        return

    def fill_light_buffer(self, r, g, b):
        rt = r
        gt = g
        bt = b
        for i in range(self.LED_COUNT):
            if i < self.light_nums[0]:
                r = int(rt / 10)
                g = int(gt / 10)
                b = int(bt / 10)
            else:
                r = rt
                g = gt
                b = bt
            self.curr_light_buffer[i] = Color(r, g, b)

    def calc_color(self, pos, rt, gt, bt):
        if pos < self.light_nums[0]:
            # 最外圈变暗
            r = int(rt / 10)
            g = int(gt / 10)
            b = int(bt / 10)
        else:
            r = rt
            g = gt
            b = bt
        r = int(r * (self.brightness / 255))
        g = int(g * (self.brightness / 255))
        b = int(b * (self.brightness / 255))

        return [r, g, b]

    def save_color_to_buffer(self, r, g, b, start, num):
        rt = r
        gt = g
        bt = b
        for i in range(num):
            pos = i + start
            if pos >= self.LED_COUNT:
                pos = self.LED_COUNT - 1

            r, g, b = self.calc_color(pos, rt, gt, bt)
            # if pos < self.light_nums[0]:
            #     # 最外圈变暗
            #     r = int(rt / 10)
            #     g = int(gt / 10)
            #     b = int(bt / 10)
            # else:
            #     r = rt
            #     g = gt
            #     b = bt
            # r = r * (self.brightness / 100)
            # g = g * (self.brightness / 100)
            # b = b * (self.brightness / 100)
            self.curr_light_buffer[pos] = Color(r, g, b)

    def show_color_by_buffer(self):
        for idx, color in enumerate(self.curr_light_buffer):
            self.strip.setPixelColor(idx, color)
        self.strip.show()

    def show_color(self, r, g, b, start = 0, num = 0):
        # print("r,g,b:", r, g, b)
        # for j in range(255):
        if num == 0:
            num = self.strip.numPixels()

        rt = r
        gt = g
        bt = b
        for i in range(num):
            r, g, b = self.calc_color(i + start, rt, gt, bt)
            # if i + start < self.light_nums[0]:
            #     # 最外圈变暗
            #     r = int(rt / 10)
            #     g = int(gt / 10)
            #     b = int(bt / 10)
            # else:
            #     r = rt
            #     g = gt
            #     b = bt
            # r = r * (self.brightness / 100)
            # g = g * (self.brightness / 100)
            # b = b * (self.brightness / 100)
            self.strip.setPixelColor(i + start, Color(r, g, b))
            # print("j:", j)
        self.strip.show()
        self.current_color = {
            "r": r,
            "g": g,
            "b": b
        }
        # time.sleep(0.01)
        # time.sleep(2)

    def clear(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()

    def turn_off(self):
        # print("turn_off act.")
        # for j in range(255, -1, -1):
        self.set_mode("")
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        #time.sleep(0.01)