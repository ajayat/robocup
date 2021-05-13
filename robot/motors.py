# http://learn.makeblock.com/en/me-encoder-motor-driver/
# https://github.com/Makeblock-official/Makeblock-Libraries/blob/master/src/MeEncoderMotor.cpp

from pyb import I2C, delay
import ustruct

import logging

logger = logging.Logger(__name__)


class Motor :

    HEADER = [0xA5, 0x01]
    END = 0x5A

    CMD_MOVE_SPD = 0x05
    CMD_RESET = 0x07
    CMD_MOVE_SPD_TIME = 0x08
    CMD_GET_SPD = 0x09
    CMD_MOVE_AGL = 0x11

    def __init__(self, pin, addr, slot) :
        """
        pin : I2C bus' pin (2 ou 4)
        addr : slave's address
        slot : motor's slot (1 ou 2)
        """
        self.__slot = slot - 1
        self.__addr = addr
        self.__i2c = I2C(pin)
        self.__i2c.init(I2C.MASTER)

    def __send_data(self, data: list):
        """
        Send trame to I2C
        data:: data to send : [slot, CMD, args]
        """

        lrc = self.lrc_calc(data)
        data_size = self.to_bytes("l", len(data))
        trame = Motor.HEADER + data_size + data + [lrc, Motor.END]
        self.__i2c.send(bytearray(trame), self.__addr)
        delay(10)  # A few wait time is needed for the motor.

    def __recv_data(self, length):
        """
        Recv data from I2C slave's address
        length:: message's length to receive
        """
        return self.__i2c.recv(length, self.__addr)

    def scan(self) :
        """
        Scan slaves connected to thecurrent I2C pin
        arg[out] -> list of slaves addresses
        """
        return self.__i2c.scan()

    def run_speed(self, speed) :
        """
        Controls motor rotation with speed given
        speed:: rotation speed [-200, + 200]
        """
        if self.__i2c.is_ready(self.__addr):
            data = [self.__slot, Motor.CMD_MOVE_SPD] + self.to_bytes("f", speed)
            self.__send_data(data)
        else:
            logger.error(
                "The motor {} cannot be run. "
                "Please check that the motor is powered.".format(self.__slot+1)
            )

    def stop(self) :
        """
        Reset motor position to 0.
        """
        data = [self.__slot, Motor.CMD_RESET]
        self.__send_data(data)

    def lrc_calc(self, data) :
        lrc = 0x00
        for byte in data :
            lrc ^= byte
        return lrc

    def to_bytes(self, format: str, data) -> list:
        """
        Format data with a given format, the list of available formats
        can be found here: https://docs.python.org/3/library/struct.html
        """
        return list(ustruct.pack(format, data))
