# http://docs.micropython.org/en/latest/library/pyb.html
from pyb import delay

import logging
from motors import Motor
from sensors import Camera

logger = logging.Logger(__name__)


class Robot:
    """
    A class that represents the robot and offers shortcuts functions 
    to runs two motors.

    Attributes:
        rmotor: The right-side motor
        lmotor: The left-side motor
    Methods:
        run_two_motors(self, rspeed, lspeed)
        turn_left(self, speed)
        turn_right(self, speed)
        stop(self)
    """

    def __init__(self):
        self.rmotor = Motor(4, 0x09, 1)
        self.lmotor = Motor(4, 0x09, 2)

    def run_two_motors(self, rspeed, lspeed):
        logger.debug("Running motors at speed {} and {}".format(rspeed, lspeed))
        self.rmotor.run(rspeed)
        self.lmotor.run(-lspeed)

    def turn_left(self, speed):
        self.run_two_motors(0, speed)

    def turn_right(self, speed):
        self.run_two_motors(speed, 0)

    def stop(self):
        logger.info("Stopping motors...")
        self.rmotor.stop()
        self.lmotor.stop()


def main():
    """ The main function, interact with sensors and Robot class"""
    try:
        robot = Robot()
        robot.run_two_motors(200, 200)
        delay(5000)  # sleep for 5 seconds
        robot.turn_left(200)

        camera = Camera()
        while True:
            ball_blob = camera.ball_blob()

    except Exception as error:
        if str(error) == "IDE interrupt":
            robot.stop()
            logger.critical("The script was stopped by Open MV IDE")
        else:
            raise error
