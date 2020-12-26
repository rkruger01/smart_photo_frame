#!/usr/bin/python3
import time
import ep_lib
import logging
from draw import image_draw


def main():
    try:
        epd = ep_lib.EPD()
        epd.init()
        epd.clear()
        img = image_draw(epd.width, epd.height)
        epd.display(epd.getbuffer(img))
        wait = input()
        epd.clear()
        epd.sleep()
    except IOError as e:
        logging.info(e)


if __name__ == '__main__':
    main()
