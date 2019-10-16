import logging

class APA102():
    def __init__(self, num_led):
        print("APA DEVICE MOCK: {}".format(num_led))
        self.led_num = None
        self.red = None
        self.green = None
        self.blue = None
        self.bright_percent = 100

    def set_pixel(self, led_num, red, green, blue, bright_percent=100):
        self.led_num = led_num
        self.red = red
        self.green = green
        self.blue = blue
        self.bright_percent = bright_percent

    def show(self):
        logging.debug("APA SHOW: %s/%s/%s/%s", self.led_num, self.red, self.green, self.blue)
