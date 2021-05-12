# Entry point
import pyb

import logging

logger = logging.Logger()
logger.add_handler(logging.FileHandler("robot.log"))

pyb.usb_mode('VCP+MSC')
usb_vcp = pyb.USB_VCP()
usb_vcp.init()

if usb_vcp.debug_mode_enabled():
    logger.add_handler(logging.StreamHandler)
    logger.setLevel("DEBUG")

pyb.usb_mode('VCP+MSC')
pyb.main("main.py")
