# http://docs.micropython.org/en/latest/library/pyb.html
import uasyncio as asyncio
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
        rotate(angle: float, speed: float)
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

    @property
    def moving(self):
        return self.lmotor.speed != 0 or self.rmotor.speed != 0

    @staticmethod
    def time_for_distance(distance: float, speed: float) -> float:
        """
        Returns needed time in seconds to travel a specified distance
        at a given speed.
        Parameters:
            distance (float): in millimeters
            speed (float): in RPM
        """
        turns = distance / (Robot.WHEEL_DIAMETER * math.pi)
        time = turns * 60 / abs(speed)
        return time

    async def stop(self, *_):
        """ Stop all motors and timer """
        logger.debug("Stopping motors...")
        await self.rmotor.stop()
        await self.lmotor.stop()

    async def rotate(self, speed: float, angle: float):
        """
        Turns itself in clockwise.
        Parameters:
           speed: the speed [-200; 200] in RPM
           angle: the angle [-180, 180] in degrees to turn
        The recommended speed is 100.
        """
        if angle < 0:
            angle, speed = -angle, -speed
        section_dist = (angle % 360) / 360 * math.pi * Robot.ROT_DIAMETER
        # 0.8 is a correction factor (turn is limited by frictions on the surface)
        time = self.time_for_distance(section_dist, speed)
        await self.rmotor.run(speed, time)
        await self.lmotor.run(speed, time)
        # await asyncio.sleep_ms(round(time * 1000))

    async def move_to(self, distance: float, speed: float):
        """
        Move to the object position at a given speed.
        Parameters:
           distance (float): distance to run
           speed: the speed [-200; 200] in RPM
        """
        time = self.time_for_distance(distance, speed)
        await self.rmotor.run(-speed, time)
        await self.lmotor.run(speed, time)


async def main():
    """ The main function, interact with sensors and Robot class"""
    robot = Robot()
    logger.info("Robot is ready")

    while True:
        ball_blob = robot.camera.ball_blob()
        # if the ball was detected
        if ball_blob:
            angle = robot.camera.get_angle(ball_blob)
            if abs(angle) >= 5:
                await robot.rotate(speed=100, angle=angle)
            if not robot.moving:
                dist = robot.camera.distance_to(ball_blob)
                await robot.move_to(dist, speed=150)
        elif not robot.moving:
            await robot.rmotor.run(100)
            await robot.lmotor.run(100)
            # TODO: fix: ball can be stuck to robot

        await asyncio.sleep_ms(40)  # 25 FPS, this time is needed to run tasks
