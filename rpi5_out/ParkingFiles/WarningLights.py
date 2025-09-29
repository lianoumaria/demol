import time
import board
import neopixel_spi as neopixel

NUM_PIXELS = 12
PIXEL_ORDER = neopixel.GRB
COLORS = ['0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000', '0x000000']
DELAY = 0.1
BRIGHTNESS = 0.5

class LEDArray:
    def __init__(self):
        self.spi = board.SPI()
        self.pixels = neopixel.NeoPixel_SPI(
            self.spi,
            NUM_PIXELS,
            brightness=BRIGHTNESS,
            pixel_order=PIXEL_ORDER,
            auto_write=True
        )

    def set_action(self, **params):
        # Extract parameters with defaults
        colors = params.get('colors', COLORS)
        delay = params.get('delay', DELAY)
        brightness = params.get('brightness', BRIGHTNESS)
        
        # Update brightness if provided
        if 'brightness' in params:
            self.pixels.brightness = brightness
        
        # Turn the colors into integers so the neopixel library will understand.
        colors = [int(x, 16) for x in colors]
        # Execute the LED sequence
        i = 0
        for color in colors:
            if i >= NUM_PIXELS:  # Don't exceed the number of available pixels
                break
            self.pixels[i] = color
            i += 1
            time.sleep(delay)
        self.pixels.fill(0)

    def disconnect(self):
        self.pixels.fill(0)