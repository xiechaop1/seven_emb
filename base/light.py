import time
import argparse
from common.code import Code
import wheel
from common.threading_event import ThreadingEvent
from config.config import Config

if not Config.IS_DEBUG:
    from rpi_ws281x import *


class Light:

    # LED strip configuration:
    LED_COUNT = 200  # Number of LED pixels.
    LED_PIN = 18  # 18      # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 64  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    def __init__(self):
        # self.light_mode = ""
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()
        self.light_mode = None
        self.last_light_mode = None
        self.current_color = None
        self.target_color = None
        self.target_params = None
        self.ts = 0
        self.run_ts = 0
        self.light_nums = [40, 32, 24, 16]
        self.current_colors = []

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

            if light_mode == Code.LIGHT_MODE_STATIC:
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

    def start(self, light_mode, params):
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

        if light_mode is not None:
            self.set_mode(light_mode)

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
                [255, 0, 0],
                [0, 255, 0],
                [0, 0, 255],
                [128, 128, 0],
                [0, 128, 128],
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

            color_buffer = []
            for color_i in range(color_num):
                color_buffer_idx = color_idx + color_i
                if color_buffer_idx >= len(colors):
                    color_buffer.insert(color_buffer_idx, def_color)
                else:
                    color_buffer.insert(color_buffer_idx, colors[color_buffer_idx])

                self.rainbow_circle_exec(color_buffer_idx, color_buffer[color_buffer_idx])
                time.sleep(0.2)

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
            start += num

        self.fade(curr_r, curr_g, curr_b, r, g, b, start, num)
        self.insert(idx, color)


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

        self.fade(old_color['r'], old_color['g'], old_color['b'], r, g, b)

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


    def show_color(self, r, g, b, start = 0, num = 0):
        # print("r,g,b:", r, g, b)
        # for j in range(255):
        if num == 0:
            num = self.strip.numPixels()

        for i in range(num):
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