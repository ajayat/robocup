import ustruct as struct
import sensor
import pyb

import ulogging as logging

logger = logging.Logger(__name__)


class Sensor:
    """A class that represent the Arduino-controlled sensors

    Offers an interface for ultrasonics sensors and line sensors (IR).
    """

    PIN = 2
    SLAVE_ADDRESS = 0x10

    def __init__(self):
        self.__i2c = pyb.I2C(self.PIN)
        self.__i2c.init(pyb.I2C.MASTER)

    def __repr__(self) -> str:
        return "Sensor(pin={}, address={})".format(self.PIN, self.SLAVE_ADDRESS)

    def recv(self) -> tuple:
        """Requests the Arduino controller via I2C and unpack data received 
        from sensors.

        Returns:
            (front_dist, back_dist, line_sensors):
            The front and back distance and a list of four line sensors values.
        """
        # creates a buffer of 12 bytes (6 * typeof(int))
        buffer = bytearray(12)
        # receive data from sensor buffer will be filled in-place
        self.__i2c.recv(buffer, Sensor.SLAVE_ADDRESS)
        # https://docs.python.org/3/library/struct.html
        front_dist, back_dist, *line_sensors = struct.unpack(">6H", buffer)
        return front_dist, back_dist, line_sensors


class Camera:
    """A class to groups functions related to OpenMV Cam

    More infos:
    https://openmv.io/products/openmv-cam-h7

    Attributes:
        width: the screen width in pixels
        height: the screen height in pixels
    """

    # List of thresholds (can be obtained in Open MV) that match the element color
    THRESHOLDS = [
        (0, 100, 127, 42, -128, 127)  # RED COLOR
    ]
    BALL_DIAMETER = 45  # in millimeters
    FOCAL_LENGTH = 2.8
    HFOV = 70.8  # horizontal field of view in degrees
    VFOV = 55.6
    REAL_SIZE = 7  # in millimeters

    def __init__(self):
        """Initialize the LED to show state and setup the camera sensor
        """
        self._red_led = pyb.LED(1)  # Turns led on (red color)
        self._red_led.on()
        # Setup sensor settings
        # https://docs.openmv.io/library/omv.sensor.html#constants
        sensor.reset()
        sensor.set_vflip(True)  # Reverse image on vertical axis
        sensor.set_hmirror(True)  # Reverse image on horizontal axis
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        sensor.set_auto_gain(False)  # Must be turned off for color tracking
        # Must be turned off for color tracking
        sensor.set_auto_whitebal(False)

    @staticmethod
    def distance_to(blob) -> float:
        """Calculate real distance between camera and object.

        Args:
            blob: a blob object (you can get one with ball_blob())

        Returns:
            The distance in millimeters.
        """
        obj_width_on_sensor = (Camera.REAL_SIZE * blob.h()/2) / sensor.width()
        distance = (Camera.BALL_DIAMETER * Camera.FOCAL_LENGTH) / \
            obj_width_on_sensor
        return distance

    @staticmethod
    def get_angle(blob) -> float:
        """Get horizontal relative angle (in degrees) of the blob.

        Args:
            blob: a blob object (you can get one with ball_blob())

        Returns:
            The angle between [-35.4, +35.4]
        """
        rel_angle = Camera.HFOV * \
            (blob.cxf() - sensor.width()/2) / sensor.width()
        return rel_angle

    def shutdown(self):
        """ Shutdown the camera and the LED """
        sensor.shutdown()
        self._red_led.off()

    @staticmethod
    def ball_blob():
        """
        Takes a snapshot and find pixels area matching with thresholds .
        Returns:
            image.blob | None: returns a blob object if visible.
        Additionnal informations can be found here about the blob object:
            https://docs.openmv.io/library/omv.image.html
        """
        img = sensor.snapshot()
        # Only blobs with more 50 pixels and area are returned
        for blob in img.find_blobs(Camera.THRESHOLDS, pixels_threshold=50, area_threshold=50):
            if blob.roundness() < 0.3:
                continue
            if pyb.USB_VCP().debug_mode_enabled():
                # If the cam is connected to OpenMV IDE
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())

            return blob  # we need only one blob
        return None
