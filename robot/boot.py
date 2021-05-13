# Entry point
import pyb

import logging
import robot

logger = logging.Logger("root")
usb_vcp = pyb.USB_VCP()

if usb_vcp.debug_mode_enabled():
    logger.add_handler(logging.StreamHandler())
    logger.set_level("DEBUG")
else:
    logger.add_handler(logging.FileHandler("robot.log"))

robot.main()
