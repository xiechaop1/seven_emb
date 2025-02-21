import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18#18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS =64     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class light

    light_mode = 'const_color'

    def colorWipe2(strip, color, wait_ms=100):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe2 act.")
        # for i in range(strip.numPixels()):
            # strip.setPixelColor(i, color)
            # strip.show()
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
    # Define functions which animate LEDs in various ways.
    def colorWipe(strip, color, wait_ms=40):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe act.")
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
            # time.sleep(wait_ms/1000.0)

    def colorWipe_single(strip, color, wait_ms=40):
        """Wipe color across display a pixel at a time."""
        # print("colorWipe_single act.")
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
    def theaterChase(strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        # print("theaterChase act.")
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)

    def Gradient(pos):
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

    def Shadowing(strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        # print("rainbow act.")
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        # print("rainbowCycle act.")
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        # print("theaterChaseRainbow act.")
        for j in range(256):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, 0)


    def BreathWithTwoColor(r1, g1, b1, r2, g2, b2, wait_time = 0.2)
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
        inter = 1
        while(true):
            if self.light_mode != 'breath2Color':
                break
            for i in range(m):
                if (r1 > r2 and rt > r2 + inter) or (r1 < r2 and rt < r2 - inter):
                    rt = rt + rtag * inter
                else:
                    rt = r2
                if (g1 > g2 and gt > g2 + inter) or (g1 < g2 and gt < g2 - inter):
                    gt = gt + gtag * inter
                else:
                    gt = g2
                if (b1 > b2 and bt > b2 + inter) or (b1 < b2 and bt < b2 - inter):
                    bt = bt + btag * inter
                else:
                    bt = b2
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r2 and gt == g2 and bt == b2:
                    break
                strip.show()
                time.sleep(wait_time)

            for i in range(m):
                if (r1 > r2 and rt < r1 - inter) or (r1 < r2 and rt > r1 + inter):
                    rt = rt - rtag * inter
                else:
                    rt = r1
                if (g1 > g2 and gt < g1 - inter) or (g1 < g2 and gt > g1 + inter):
                    gt = gt - gtag * inter
                else:
                    gt = g1
                if (b1 > b2 and bt < b1 - inter) or (b1 < b2 and bt > b1 + inter):
                    bt = bt - btag * inter
                else:
                    bt = b1
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r1 and gt == g1 and bt == b1:
                    break
                strip.show()
                time.sleep(wait_time)

    def Breathing(r, g, b, wait_time = 0.2):
        m = max(r, g, b)
        rt = r
        gt = g
        bt = b
        inter = 1
        while(true):
            if self.light_mode != 'breath':
                break
            for i in range(m):
                if rt > inter:
                    rt = rt - inter
                else:
                    rt = 0
                if gt > inter:
                    gt = gt - inter
                else:
                    gt = 0
                if bt > inter:
                    bt = bt - inter
                else:
                    bt = 0
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == 0 and gt == 0 and bt == 0:
                    break
                strip.show()
                time.sleep(wait_time)

            for i in range(m):
                if rt < r:
                    rt = rt + inter
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
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, Color(rt, gt, bt))
                if rt == r and gt == g and bt == b:
                    break
                strip.show()
                time.sleep(wait_time)

    def Static(r,g,b):
        print("r,g,b:",r,g,b)
        # for j in range(255):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(r, g, b))
                # print("j:", j)
            strip.show()
            # time.sleep(0.01)
        # time.sleep(2)

    def turn_off():
        # print("turn_off act.")
        # for j in range(255, -1, -1):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        #time.sleep(0.01)