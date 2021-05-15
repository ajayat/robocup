# http://docs.micropython.org/en/latest/library/pyb.html
from pyb import delay
import math

import logging
from motors import Motor
from sensors import Camera, Sensor

logger = logging.Logger(__name__)


class Robot:
    """
    A class that represents the robot and offers shortcuts functions
    to runs two motors.

    Attributes:
        rmotor: The right-side motor
        lmotor: The left-side motor
    Methods:
        turn_itself(angle: float, speed: float)
        move_to(blob, speed: float)
        stop(self)
    """

    WHEEL_DIAMETER = 80  # in millimeters
    ROT_DIAMETER = 270  # distance (mm) between two wheels

    def __init__(self):
        self.lmotor = Motor(4, 0x09, 1)
        self.rmotor = Motor(4, 0x09, 2)
        self.camera = Camera()
        self.sensor = Sensor()

    @staticmethod
    def time_for_distance(distance: float, speed: float) -> float:
        """
        Returns needed time in seconds to travel a specified distance
        at a given speed.
        """
        turns = distance / (Robot.WHEEL_DIAMETER * math.pi)
        time = turns * 60 / abs(speed)
        return time

    def turn_itself(self, angle: float, speed: float, wait=False):
        """
        Turns itself in clockwise.
        Parameters:
           angle: the angle [0, 360] in degrees to turn
           speed: the speed [-200; 200] in RPM
        The recommended speed is 100.
        """
        section_dist = (angle % 360) / 360 * math.pi * Robot.ROT_DIAMETER
        # 0.8 is a correction factor (turn is limited by frictions on the surface)
        time = round(0.8 * self.time_for_distance(section_dist, speed), 3)
        self.rmotor.run(speed, time)
        self.lmotor.run(speed, time)
        if wait:
            delay(time*1000)

    def stop(self):
        """ Stop all motors """
        logger.info("Stopping motors...")
        self.rmotor.stop()
        self.lmotor.stop()

    def move_to(self, blob, speed: float):
        """
        Move to the object position at a given speed.
        Parameters:
           blob: a blob object (you can get one with camera.ball_blob())
           speed: the speed [-200; 200] in RPM
        """
        distance = round(self.camera.distance_to(blob) / 10, 1)
        angle = round(self.camera.get_angle(blob))
        logger.info("Ball distance: {}cm, horizontal angle: {}°. ".format(distance, angle))
        if angle < 0:
            self.turn_itself(-angle, -100)
        else:
            self.turn_itself(angle, 100)
        time = round(self.time_for_distance(distance, speed), 3)
        self.rmotor.run(speed, time)
        self.lmotor.run(-speed, time)


def main():
    """ The main function, interact with sensors and Robot class"""
    robot = Robot()
    # robot.turn_itself(180, 100)
    while True:
        ball_blob = robot.camera.ball_blob()
        if ball_blob:
            robot.move_to(ball_blob)
        else:
            # TODO: turn until ball was found but ball can be stuck to robot
            robot.turn_itself(360, 100)
        delay(33)  # 30 fps
