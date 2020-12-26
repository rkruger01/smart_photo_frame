from PIL import ImageDraw, Image, ImageFont
import calendar, datetime


def image_draw(epd_width, epd_height):
    font = ImageFont.truetype('CourierStd.otf', 32)
    Himage = Image.new('1', (epd_width, epd_height), 255)
    draw = ImageDraw.Draw(Himage)
    cal = calendar.TextCalendar(calendar.SUNDAY)
    now = datetime.datetime.now()
    monthCal = cal.formatmonth(now.year, now.month)
    cal_topleftx = epd_width/2
    cal_toplefty = 0
    draw.text((cal_topleftx+10, cal_toplefty+20), monthCal, font=font, fill=0)
    draw.line((epd_width / 2, 0, epd_width / 2, epd_height), fill=0, width=2)
    draw.line((epd_width / 2, epd_height / 2, epd_width, epd_height / 2), fill=0, width=2)
    draw.text((epd_width / 2 + 10, epd_height / 2 + 10), "Weather", font=font)
    return Himage
