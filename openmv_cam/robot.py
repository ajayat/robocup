# http://docs.micropython.org/en/latest/library/pyb.html
from pyb import delay
import math

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

    WHEEL_DIAMETER = 80  # in millimeters
    ROT_DIAMETER = 270  # distance (mm) between two wheels

    def __init__(self):
        self.lmotor = Motor(4, 0x09, 1)
        self.rmotor = Motor(4, 0x09, 2)

    def run_two_motors(self, rspeed: float, lspeed: float, time=None):
        """ Runs two motors with a given speed.
        Parameters:
            rspeed: speed of right motor
            lspeed: speed of left motor
            time (float): if set, motors will runs for time seconds.
        """
        self.rmotor.run(rspeed, time)
        self.lmotor.run(-lspeed, time)

    def turn_itself(self, angle: float, speed: float):
        """
        Turns itself in clockwise.
        Parameters:
           angle: the angle [0, 360] in degrees to turn
           speed: the speed [-200; 200] in RPM
        The recommended speed is 100.
        """
        section_dist = (angle % 361) / 360 * math.pi * Robot.ROT_DIAMETER
        turns = section_dist / (Robot.WHEEL_DIAMETER * math.pi) / 2
        # 1.55 is a correction factor (turn is limited by frictions on the surface)
        time = round((1.55 * turns * 60) / abs(speed), 3)
        self.rmotor.run(speed, time)
        self.lmotor.run(speed, time)

    def stop(self):
        """ Stop all motors """
        logger.info("Stopping motors...")
        self.rmotor.stop()
        self.lmotor.stop()


def main():
    """ The main function, interact with sensors and Robot class"""
    try:
        robot = Robot()
        robot.turn_itself(360, 100)
        camera = Camera()
        while True:
            ball_blob = camera.ball_blob()

    except Exception as error:
        if str(error) == "IDE interrupt":
            robot.stop()
            logger.critical("The script was stopped by Open MV IDE")
        else:
            raise error
