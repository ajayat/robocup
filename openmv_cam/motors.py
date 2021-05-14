from pyb import I2C, delay
import ustruct

import logging

logger = logging.Logger(__name__)


class Motor:
    """
    A class to represent a motor and offers an API to control it.

    Methods:
        scan(): Scan slaves.
        run(speed, time=None): Runs the motor.
        move(angle, speed): Move the motor for a specified angle
        get_speed(): Returns the current motor speed
        stop(): Stop the motor.

    Additionnal documentation can be found here:
        http://learn.makeblock.com/en/me-encoder-motor-driver/
        https://github.com/Makeblock-official/Makeblock-Libraries/blob/master/src/MeEncoderMotor.cpp
    """

    HEADER = [0xA5, 0x01]
    END = 0x5A
    CMD_MOVE_SPD = 0x05
    CMD_MOVE_SPD_TIME = 0x08
    CMD_RESET = 0x07
    CMD_GET_SPD = 0x09
    CMD_MOVE_AGL = 0x11

    def __init__(self, pin: int, addr: int, slot: int):
        """
        Initialize I2C communication to motor.
        Parameters:
            pin (int): I2C bus' pin (2 or 4)
            addr (int): slave's address
            slot (int): motor's slot (1 or 2)
        """
        self.__slot = slot - 1
        self.__addr = addr
        self.__i2c = I2C(pin)
        self.__i2c.init(I2C.MASTER)

    def __send_data(self, data: list):
        """
        Creates a trame from the data and send it to motor via I2C.
        Parameters:
            data (list): [slot, CMD, args]: data to send
        """
        lrc = self._lrc_calc(data)
        data_size = self._to_bytes("l", len(data))
        trame = Motor.HEADER + data_size + data + [lrc, Motor.END]
        self.__i2c.send(bytearray(trame), self.__addr)
        delay(10)  # A few wait time is needed for the motor.

    def __recv_data(self, length: int):
        """
        Receives data from I2C slave's address
        Parameters:
            length (int): number of bytes to receive
        Returns:
            buffer (bytearray): data received in bytes
        """
        buffer = bytearray(length)
        self.__i2c.recv(buffer, self.__addr)
        return buffer

    def scan(self):
        """
        Scan slaves connected to the current I2C pin.
        Returns:
            list_of_slaves (list): addresses of slaves that respond
        """
        list_of_slaves = self.__i2c.scan()
        return list_of_slaves

    def run(self, speed: float, time=None):
        """
        Controls motor rotation with speed given for an optional time.
        Parameters:
            speed (float): rotation speed (RPM) in [-200, +200]
            time (float, default None): in milli-seconds, runs for a specified time
        """
        if self.__i2c.is_ready(self.__addr):
            # Sets time limits to [-200 , +200] and convert it in bytes
            speed_bytes = self._to_bytes("f", min(200, max(speed, -200)))
            time_bytes = self._to_bytes("f", max(time, 0))
            if time:
                data = [self.__slot, Motor.CMD_MOVE_SPD_TIME] + speed_bytes + time_bytes
            else:
                data = [self.__slot, Motor.CMD_MOVE_SPD] + speed_bytes
            self.__send_data(data)
        else:
            logger.error(
                "The motor {} cannot be run. "
                "Please check that the motor is powered.".format(self.__slot+1)
            )
    
    def move(self, angle: float, speed: float):
        """
        Move motor of angle degrees at a speed given.
        Parameters:
            speed (float): rotation speed (RPM) in [-200, +200]
            angle (float): angle in degrees to rotate.
        """
        if self.__i2c.is_ready(self.__addr):
            # Sets time limits to [-200 , +200] and convert it in bytes
            speed_bytes = self._to_bytes("f", min(200, max(speed, -200)))
            angle_bytes = self._to_bytes("f", angle)
            data = [self.__slot, Motor.CMD_MOVE_AGL] + speed_bytes + angle_bytes
            self.__send_data(data)
        else:
            logger.error(
                "The motor {} cannot be move. "
                "Please check that the motor is powered.".format(self.__slot+1)
            )
            
    def get_speed(self):
        """ Returns the current motor speed """
        data = [self.__slot, Motor.CMD_GET_SPD]
        self.__send_data(data)
        speed_bf = self.__recv_data(length=len(data))
        return ustruct.unpack("f", speed_bf[2:])

    def stop(self):
        """ Reset motor position to 0 and reinitialize data received. """
        data = [self.__slot, Motor.CMD_RESET]
        self.__send_data(data)

    def _lrc_calc(self, data):
        """
        Calculate the Longitudinal Redondancy Check (LRC)
        Returns:
            lrc (int): the value of LRC
        """
        lrc = 0x00
        for byte in data :
            lrc ^= byte
        return lrc

    def _to_bytes(self, format: str, data) -> list:
        """
        Convert and pack data with a given format, the list of available formats
        can be found here: https://docs.python.org/3/library/struct.html
        Parameters:
            format (str): string used to pack the data from a given format.
            data (any): data to be converted to bytes.
        Returns:
            data_bytes (list): a list of each element of data converted to bytes.
        """
        data_bytes = list(ustruct.pack(format, data))
        return data_bytes
