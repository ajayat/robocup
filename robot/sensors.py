import ustruct
import sensor
import pyb

import logging

logger = logging.Logger(__name__)

THRESHOLDS = [
    (0, 100, 127, 42, -128, 127)  # Red
]

class Sensor:

    PIN = 2
    SLAVE_ADDRESS = 0x10

    def __init__(self):
        self.__i2c = pyb.I2C(self.PIN)
        self.__i2c.init(pyb.I2C.MASTER)

    def __repr__(self) -> str:
        return "Sensor(pin={}, addr={})".format(self.__pin, self.__addr)

    def recv(self):
        """
        Returns data from the sensors if available
        """
        # creates a buffer of 12 bytes (6 * typeof(int))
        buffer = bytearray(12)
        # receive data from sensor buffer will be filled in-place
        self.__i2c.recv(buffer, Sensor.SLAVE_ADDRESS)
        # https://docs.python.org/3/library/struct.html
        ahead_dist, behind_dist, *line_sensors = ustruct.unpack(">6H", buffer)
        return (ahead_dist, behind_dist, line_sensors)


class Camera:

    def __init__(self):
        self.red_led = pyb.LED(1)  # Turns led on (red color)
        self.red_led.on()
        # Setup sensor settings
        sensor.reset()
        sensor.set_vflip(True) # Reverse image on vertical axis
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        sensor.set_auto_gain(False) # Must be turned off for color tracking
        sensor.set_auto_whitebal(False) # Must be turned off for color tracking

    @property
    def width(self):
        return sensor.width()

    @property
    def height(self):
        return sensor.height()

    def shutdown(self):
        sensor.shutdown()
        self.red_led.off()

    @staticmethod
    def ball_blob():
        """ Returns the ball blob object if it was found. """
        img = sensor.snapshot()
        # Only blobs with more 50 pixels and area are returned
        for blob in img.find_blobs(THRESHOLDS, pixels_threshold=50, area_threshold=50):
            if pyb.USB_VCP().debug_mode_enabled():
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())
            return blob
        return None
