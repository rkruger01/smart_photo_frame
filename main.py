#!/usr/bin/python3
from PIL import ImageDraw, Image, ImageFont
import time
import ep_lib
import logging


def image_draw(epd_width, epd_height):
    font24 = ImageFont.truetype('Font.ttc', 24)
    Himage = Image.new('1', (epd_width, epd_height), 255)
    draw = ImageDraw.Draw(Himage)
    draw.text((10, 0), 'hello world', font=font24, fill=0)
    draw.text((10, 20), '7.5inch e-Paper', font=font24, fill=0)
    draw.text((150, 0), u'微雪电子', font=font24, fill=0)
    draw.line((20, 50, 70, 100), fill=0)
    draw.line((70, 50, 20, 100), fill=0)
    draw.rectangle((20, 50, 70, 100), outline=0)
    draw.line((epd_width / 2, 0, epd_width / 2, epd_height), fill=0, width=2)
    draw.line((165, 50, 165, 100), fill=0)
    draw.line((140, 75, 190, 75), fill=0)
    draw.arc((140, 50, 190, 100), 0, 360, fill=0)
    draw.rectangle((80, 50, 130, 100), fill=0)
    draw.chord((200, 50, 250, 100), 0, 360, fill=0)
    return Himage


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
