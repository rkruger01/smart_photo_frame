#!/usr/bin/python3
import time
import ep_lib
import logging
import os
from draw import image_draw

debug = False


def main():
    try:
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG" if debug else "INFO"))
        epd = ep_lib.EPD()
        img = image_draw(epd.width, epd.height)
        logging.debug("Image complete, waiting on write")
        epd.init()
        logging.debug("Initialization complete, clearing display")
        epd.clear()
        epd.display(epd.getbuffer(img))
        logging.debug("Display complete")
        logging.debug("Entering sleep mode")
        epd.sleep()
    except IOError as e:
        logging.info(e)


if __name__ == '__main__':
    main()
