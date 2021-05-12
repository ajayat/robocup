import uasyncio
import ustruct
from pyb import I2C

import logging

logger = logging.getLogger(__name__)


class Sensor:

    PIN = 2
    SLAVE_ADDRESS = 0x10

    def __init__(self, pin, addr):
        """
        pin:: I2C bus
        addr:: slave's address
        """
        self.__i2c = I2C(self.PIN)
        self.__i2c.init(I2C.MASTER)

    def __repr__(self) -> str:
        return "Sensor(pin={}, addr={})".format(self.__pin, self.__addr)

    async def _wait_until_ready(self):
        while not self.__i2c.is_ready(self.SLAVE_ADDRESS):
            await uasyncio.sleep_ms(10)

    async def recv(self):
        """
        Returns data from the sensors if available
        """
        try:
            # wait until I2C is not ready and cancel after 100ms if takes longer
            await uasyncio.wait_for_ms(self._wait_until_ready, 100) 
        except uasyncio.TimeoutError:
            print("The camera was unable to receive data from the sensor")
        else:
            # creates a buffer of 12 bytes (6 * typeof(int))
            buffer = bytearray(12)
            # receive data from sensor buffer will be filled in-place
            self.__i2c.recv(buffer, self.SLAVEADDRESS) 
            # https://docs.python.org/3/library/struct.html
            ahead_dist, behind_dist, *line_sensors = ustruct.unpack(">6H", buffer)
            return (ahead_dist, behind_dist, line_sensors)
        return None
