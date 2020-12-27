import calendar
import datetime
import logging
import sys

import requests
from math import floor
from PIL import ImageDraw, Image, ImageFont
import configparser

fetch_weather = True
draw_weather_lines = True
weather_font_dict = {
    '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
    '04d': '\uf012', '09d': '\uf01a ', '10d': '\uf019',
    '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
    '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
    '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
    '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
}
weatherfont48 = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 48)
weatherfont32 = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 32)
textfont32 = ImageFont.load('fonts/ter-u32n.pil')
textfont24 = ImageFont.load('fonts/ter-u24n.pil')
textfont16 = ImageFont.load('fonts/ter-u16n.pil')
textfont12 = ImageFont.load('fonts/ter-u12n.pil')


def image_draw(epd_width, epd_height, config_file_name="config.txt"):
    config = configparser.ConfigParser()
    try:
        config.read(config_file_name)
        owm_api_key = config['Config']['owm_api_key']
        positionstack_api_key = config['Config']['positionstack_api_key']
        weather_units = config['Config']['units']
        weather_zip = config['Config']['city_zip_code']
        weather_country = config['Config']['city_country_code']
    except configparser.MissingSectionHeaderError as e:
        logging.error(e)
        exit(1)

    Himage = Image.new('1', (epd_width, epd_height), 255)
    draw = ImageDraw.Draw(Himage)

    # Generate divider lines
    draw.line((epd_width / 2, 0, epd_width / 2, epd_height), fill=0, width=2)
    draw.line((epd_width / 2, epd_height / 2, epd_width, epd_height / 2), fill=0, width=2)

    # Generate calendar in top-right
    now = datetime.datetime.now()
    cal_topleftx = epd_width / 2
    cal_toplefty = 0
    cal_x_offset = 10
    cal_y_offset = 50

    # Configure Calendar settings
    calendar.setfirstweekday(calendar.SUNDAY)
    cal_with_zeros = calendar.monthcalendar(now.year, now.month)
    leading_zeroes = cal_with_zeros[0].count(0)
    # Calculate header format
    cal_header = calendar.month_name[now.month] + ' ' + str(now.year)
    w, h = draw.textsize(cal_header, font=textfont32)
    draw.rectangle([(cal_topleftx, cal_toplefty), (epd_width, cal_toplefty + 1.5 * h)], fill=0)
    draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset - 40), cal_header, font=textfont32,
              fill=255)
    y = 30
    # Draw calendar rows
    days = 'Su Mo Tu We Th Fr Sa'
    w, h = draw.textsize(days, font=textfont32)
    draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset), days, font=textfont32)
    for row in cal_with_zeros:
        row = [' ' + (str(x)) if x < 10 else str(x) for x in row]  # list comprehension magic
        row = ['  ' if x == ' 0' else x for x in row]  # Remove zeros from calendar
        line = ' '.join(row)
        logging.debug("Printing calendar row starting at {},{}".format(cal_topleftx + cal_x_offset,
                                                                       cal_toplefty + cal_y_offset + y))
        draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset + y), line, font=textfont32)
        y += 30
    offset_from_zero = now.day + leading_zeroes - 1
    today_x_grid = offset_from_zero % 7
    today_y_grid = floor(offset_from_zero // 7)
    logging.debug("Grid coordinates for today's date: {},{}".format(today_x_grid, today_y_grid))
    true_date_w, true_date_h = draw.textsize(" 00", font=textfont32)
    px_buffer = 4
    square_w, square_h = draw.textsize("00", font=textfont32)
    start_x = cal_topleftx + (cal_topleftx - w) / 2 + (true_date_w * today_x_grid) - px_buffer
    start_y = cal_toplefty + cal_y_offset + (today_y_grid * 30) + 28
    logging.debug("Square starting at {},{}".format(start_x, start_y))
    draw.rectangle([(start_x, start_y), (start_x + square_w + 2 * px_buffer, start_y + square_h + 2 * px_buffer)],
                   width=2)

    if fetch_weather:
        # geomap address to coordinates
        query = weather_zip + "," + weather_country
        r = requests.get(
            "http://api.positionstack.com/v1/forward?access_key={}&query={}&limit=1".format(positionstack_api_key,
                                                                                            query))
        geolocation = r.json()
        try:
            logging.debug("Weather fetched for {}".format(geolocation["data"][0]["label"]))
        except TypeError:
            logging.error("Error occured when trying to fetch weather location")
            sys.exit(1)
        weather_lat = geolocation["data"][0]["latitude"]
        weather_long = geolocation["data"][0]["longitude"]
        # pull from weather service
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}&units={}".format(weather_lat,
                                                                                                     weather_long,
                                                                                                     owm_api_key,
                                                                                                     weather_units))
        logging.debug("Openweathermap returned status code " + str(r.status_code))
        weather = r.json()
        # Current Weather
        weather_header = "Weather"
        weather_topleftx = epd_width / 2
        weather_toplefty = epd_height / 2
        todayx = weather_topleftx + 100
        forecasty = weather_toplefty + 50
        tomorrowx = todayx + 130
        weather_image_offset = 30
        tempoffset = 100
        w, h = draw.textsize(weather_header, font=textfont32)
        draw.rectangle([(weather_topleftx, weather_toplefty), (epd_width, weather_toplefty + 1.5 * h)], fill=0)
        draw.text((weather_topleftx + (weather_topleftx - w) / 2, weather_toplefty + 5), "Weather", font=textfont32,
                  fill=255)
        w, h = draw.textsize("Now", font=textfont32)
        draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty), "Now", font=textfont32)
        w, h = draw.textsize(weather_font_dict[weather["current"]["weather"][0]["icon"]], font=weatherfont48)
        draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty + weather_image_offset),
                  weather_font_dict[weather["current"]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0, )
        w, h = draw.textsize(str(round(weather["current"]["temp"])) + "°", font=textfont24)
        draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty + tempoffset),
                  str(round(weather["current"]["temp"])) + "°", font=textfont24,
                  fill=0)
        w, h = draw.textsize("Feels Like:", font=textfont16)
        draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty + 128), "Feels Like:",
                  font=textfont16,
                  fill=0)
        w, h = draw.textsize(str(round(weather["current"]["feels_like"])) + "°", font=textfont24)
        draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty + 145),
                  str(round(weather["current"]["feels_like"])) + "°", font=textfont24,
                  fill=0)

        # Today's Forecast
        w, h = draw.textsize("Today", font=textfont32)
        draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty), "Today", font=textfont32)
        w, h = draw.textsize(weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
                  font=weatherfont48)
        draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty + weather_image_offset), weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0)
        todaymintemp = round(weather["daily"][0]["temp"]["min"])
        todaymaxtemp = round(weather["daily"][0]["temp"]["max"])
        w, h = draw.textsize(str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24)
        draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty + tempoffset), str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24,
                  fill=0)
        precipxoffset = 40
        precipyoffset = 120
        # today's precip chance
        if todaymintemp < 32:
            # snow image!
            w_image, h = draw.textsize( weather_font_dict['13d'],font=weatherfont32)
            w_text, h = draw.textsize(str(round(weather["daily"][0]["pop"])), font=textfont32)
            sum_w = w_image + w_text + precipxoffset/2
            draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2, forecasty + precipyoffset), weather_font_dict['13d'],
                      font=weatherfont32,
                      fill=0)
        else:
            # lame, no snow
            w_image, h = draw.textsize(weather_font_dict['10d'], font=weatherfont32)
            w_text, h = draw.textsize(str(round(weather["daily"][0]["pop"])), font=textfont32)
            sum_w = w_image + w_text + precipxoffset/2
            draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2, forecasty + precipyoffset), weather_font_dict['10d'],
                      font=weatherfont32,
                      fill=0)
        draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2 + precipxoffset, forecasty + precipyoffset + 13),
                  str(round(weather["daily"][0]["pop"])) + "%", font=textfont32, fill=0)

        # Tomorrow's Forecast

        w, h = draw.textsize("Tomorrow", font=textfont32)
        draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty), "Tomorrow", font=textfont32)
        w, h = draw.textsize(weather_font_dict[weather["daily"][1]["weather"][0]["icon"]], font=weatherfont48)
        draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty + weather_image_offset), weather_font_dict[weather["daily"][1]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0)
        tomorrowmaxtemp = round(weather["daily"][1]["temp"]["max"])
        tomorrowmintemp = round(weather["daily"][1]["temp"]["min"])
        w, h = draw.textsize(str(tomorrowmaxtemp) + "°/" + str(tomorrowmintemp) + "°", font=textfont24)

        draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty + tempoffset), str(tomorrowmaxtemp) + "°/" + str(tomorrowmintemp) + "°",
                  font=textfont24,
                  fill=0)
        # tomorrow's precip chance
        if tomorrowmintemp < 32:
            # snow image!
            w_image, h = draw.textsize(weather_font_dict['13d'], font=weatherfont32)
            w_text, h = draw.textsize(str(round(weather["daily"][1]["pop"])), font=textfont32)
            sum_w = w_image + w_text + precipxoffset / 2
            draw.text((tomorrowx + ((epd_width - tomorrowx) - sum_w) / 2, forecasty + precipyoffset), weather_font_dict['13d'],
                      font=weatherfont32,
                      fill=0)
        else:
            # lame, no snow
            w_image, h = draw.textsize(weather_font_dict['10d'], font=weatherfont32)
            w_text, h = draw.textsize(str(round(weather["daily"][1]["pop"])), font=textfont32)
            sum_w = w_image + w_text + precipxoffset / 2
            draw.text((tomorrowx + ((epd_width - tomorrowx) - sum_w) / 2, forecasty + precipyoffset), weather_font_dict['10d'],
                      font=weatherfont32,
                      fill=0)
        draw.text((tomorrowx + ((epd_width - tomorrowx) - sum_w) / 2 + precipxoffset, forecasty + precipyoffset + 13),
                  str(round(weather["daily"][1]["pop"])) + "%", font=textfont32, fill=0)

        # Draw division lines
        if draw_weather_lines:
            weather_bottom_divider_offset = 18
            draw.line([(todayx, weather_toplefty + 1.5 * h),
                       (todayx, epd_height - weather_bottom_divider_offset)], width=2)
            draw.line([(tomorrowx, weather_toplefty + 1.5 * h),
                       (tomorrowx, epd_height - weather_bottom_divider_offset)], width=2)
            draw.line([(weather_topleftx, epd_height - weather_bottom_divider_offset),
                       (epd_width, epd_height - weather_bottom_divider_offset)], width=2)
        # Print weather location, update time
        draw.text((weather_topleftx + 8, epd_height - 12), "{}".format(geolocation["data"][0]["label"]),
                  font=textfont12)
        draw.text((epd_width - 110, epd_height - 12), "Updated {}:{}".format(now.hour, str(now.minute).zfill(2)), font=textfont12)
    return Himage
