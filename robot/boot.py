# This program is the entry point of the Open MV Cam
import pyb

import logging
import robot

# Creates the root logger (all loggers are herited from it by default)
logger = logging.Logger("root")
usb_vcp = pyb.USB_VCP()

if usb_vcp.debug_mode_enabled():
    # Logs will be displayed in the console output
    logger.add_handler(logging.StreamHandler())
    logger.set_level("DEBUG")
else:
    logger.add_handler(logging.FileHandler("robot.log"))

robot.main()  # Runs the main script
