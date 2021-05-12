# Entry point
import pyb
import uasyncio

import logging
import robot

logger = logging.Logger("root")

usb_vcp = pyb.USB_VCP()
usb_vcp.init()

if usb_vcp.debug_mode_enabled():
    logger.add_handler(logging.StreamHandler())
    logger.set_level("DEBUG")
else:
    logger.add_handler(logging.FileHandler("robot.log"))

uasyncio.run(robot.main())
