from pyb import I2C
import uasyncio as asyncio
import ustruct as struct

from utils import Timer
import ulogging as logging

logger = logging.Logger(__name__)


class Motor:
    """A class to represent a motor and offers an API to control it.

    Additionnal documentation can be found here:
        - http://learn.makeblock.com/en/me-encoder-motor-driver/
        - https://github.com/Makeblock-official/Makeblock-Libraries/blob/master/src/MeEncoderMotor.cpp
    """

    HEADER = [0xA5, 0x01]
    END = 0x5A
    CMD_MOVE_SPD = 0x05
    CMD_MOVE_SPD_TIME = 0x08
    CMD_RESET = 0x07
    CMD_MOVE_AGL = 0x11

    def __init__(self, pin: int, addr: int, slot: int):
        """Initialize I2C communication to motor.

        Args:
            pin: I2C bus' pin (2 or 4)
            addr: slave's address
            slot: motor's slot (1 or 2)
        """
        self.__slot = slot - 1
        self.__addr = addr
        self.__i2c = I2C(pin)
        self.__i2c.init(I2C.MASTER)
        self.__speed = 0
        self._stopper = Timer(callback=self.stop)

    @property
    def speed(self):
        return self.__speed

    async def __send_data(self, data: list):
        """Creates a trame from the data and send it to motor via I2C.

        Args:
            data: [slot, CMD, args]: data to send
        """
        lrc = self._lrc_calc(data)
        data_size = self._to_bytes("l", len(data))
        trame = Motor.HEADER + data_size + data + [lrc, Motor.END]
        self.__i2c.send(bytearray(trame), self.__addr)
        await asyncio.sleep_ms(20)  # A few wait time is needed for the motor.

    def __recv_data(self, length: int) -> bytearray:
        """Receives data from I2C slave's address

        Args:
            length number of bytes to receive

        Returns:
            buffer: data received in bytes
        """
        buffer = bytearray(length)
        self.__i2c.recv(buffer, self.__addr)
        return buffer

    def scan(self) -> list:
        """Scan slaves connected to the current I2C pin.

        Returns:
            list_of_slaves: addresses of slaves that respond
        """
        list_of_slaves = self.__i2c.scan()
        return list_of_slaves

    async def run(self, speed: float, time=None) -> None:
        """Controls motor rotation with speed given for an optional time.

        Args:
            speed: rotation speed (RPM) in [-200, +200]
            time: in seconds, runs for a specified time
        """
        if self.__i2c.is_ready(self.__addr):
            # Sets time limits to [-200 , +200] and convert it in bytes
            if speed < -200:
                speed = -200
            elif speed > 200:
                speed = 200
            if speed != self.__speed:
                speed_bytes = self._to_bytes("f", speed)
                data = [self.__slot, Motor.CMD_MOVE_SPD] + speed_bytes
                self.__speed = speed
                await self.__send_data(data)
            if time:
                self._stopper.cancel()
                self._stopper.start(timeout=time)
        else:
            raise RuntimeError("Motor {} cannot be run.".format(self.__slot))

    async def move(self, angle: float, speed: float) -> None:
        """Move motor of angle degrees at a speed given.

        Args:
            speed: rotation speed (RPM) in [-200, +200]
            angle: angle in degrees to rotate.
        """
        if speed < -200:
            speed = -200
        elif speed > 200:
            speed = 200
        if speed != self.__speed:
            self.__speed = speed
            time = (angle / 360 * 60) / speed
            await self.run(speed, time)

    async def stop(self):
        """ Reset motor position to 0 and reinitialize data received. """
        data = [self.__slot, Motor.CMD_RESET]
        await self.__send_data(data)
        self.__speed = 0

    @staticmethod
    def _lrc_calc(data) -> int:
        """Calculate the Longitudinal Redondancy Check (LRC)

        Returns:
            lrc: the value of LRC
        """
        lrc = 0x00
        for byte in data:
            lrc ^= byte
        return lrc

    @staticmethod
    def _to_bytes(fmt: str, data) -> list:
        """Convert and pack data with a given format

        The list of available formats can be found here: 
        https://docs.python.org/3/library/struct.html

        Args:
            fmt: string used to pack the data from a given format.
            data: data to be converted to bytes.

        Returns:
            data_bytes: a list of each element of data converted to bytes.
        """
        data_bytes = list(struct.pack(fmt, data))
        return data_bytes
