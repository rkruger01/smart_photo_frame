import calendar
import datetime
import logging
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

textfont32 = ImageFont.truetype('CourierStd.otf', 32)
textfont24 = ImageFont.truetype('CourierStd.otf', 24)
textfont16 = ImageFont.truetype('CourierStd.otf', 16)
textfont12 = ImageFont.truetype('CourierStd.otf', 14)
weatherfont48 = ImageFont.truetype('weathericons-regular-webfont.ttf', 48)
weatherfont32 = ImageFont.truetype('weathericons-regular-webfont.ttf', 32)


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
    draw.rectangle([(cal_topleftx, cal_toplefty), (epd_width, cal_toplefty + 2 * h)], fill=0)
    draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset - 40), cal_header, font=textfont32, fill=255)
    y = 30
    # Draw calendar rows
    days = 'Su Mo Tu We Th Fr Sa'
    draw.text((cal_topleftx + cal_x_offset, cal_toplefty + cal_y_offset), days, font=textfont32)
    for row in cal_with_zeros:
        row = [' ' + (str(x)) if x < 10 else str(x) for x in row]  # list comprehension magic
        row = ['  ' if x == ' 0' else x for x in row]  # Remove zeros from calendar
        line = ' '.join(row)
        logging.debug("Printing calendar row starting at {},{}".format(cal_topleftx + cal_x_offset,
                                                                       cal_toplefty + cal_y_offset + y))
        draw.text((cal_topleftx + cal_x_offset, cal_toplefty + cal_y_offset + y), line, font=textfont32)
        y += 30
    offset_from_zero = now.day + leading_zeroes - 1
    today_x_grid = offset_from_zero % 7
    today_y_grid = floor(offset_from_zero // 7)
    logging.debug("Grid coordinates for today's date: {},{}".format(today_x_grid, today_y_grid))
    true_date_w, true_date_h = draw.textsize(" 00", font=textfont32)
    px_buffer = 4
    square_w, square_h = draw.textsize("00", font=textfont32)
    start_x = cal_topleftx + cal_x_offset + (true_date_w * today_x_grid) - px_buffer
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
        logging.debug("Weather fetched for {}".format(geolocation["data"][0]["label"]))
        weather_lat = geolocation["data"][0]["latitude"]
        weather_long = geolocation["data"][0]["longitude"]
        # pull from weather service
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}&units={}".format(weather_lat,
                                                weather_long,owm_api_key,weather_units))
        logging.debug("Openweathermap returned status code " + str(r.status_code))
        weather = r.json()

        # Current Weather
        weather_header = "Weather"
        weather_topleftx = epd_width / 2
        weather_toplefty = epd_height / 2
        w, h = draw.textsize(weather_header, font=textfont32)
        draw.rectangle([(weather_topleftx, weather_toplefty), (epd_width, weather_toplefty + 2 * h)], fill=0)
        draw.text((weather_topleftx + (cal_topleftx - w) / 2, weather_toplefty + 5), "Weather", font=textfont32,
                  fill=255)
        currentx = weather_topleftx + 30
        forecasty = weather_toplefty + 50
        draw.text((currentx, forecasty), "Now", font=textfont32)
        draw.text((currentx + 10, forecasty + 25), weather_font_dict[weather["current"]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0, )
        draw.text((currentx + 10, forecasty + 100), str(round(weather["current"]["temp"])) + "°", font=textfont24,
                  fill=0)
        draw.text((currentx - 18, forecasty + 128), "Feels Like:", font=textfont16,
                  fill=0)
        draw.text((currentx + 10, forecasty + 150), str(round(weather["current"]["feels_like"])) + "°", font=textfont24,
                  fill=0)

        # Today's Forecast
        todayx = currentx + 100
        draw.text((todayx, forecasty), "Today", font=textfont32)
        draw.text((todayx + 15, forecasty + 25), weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0)
        todaymintemp = round(weather["daily"][0]["temp"]["min"])
        todaymaxtemp = round(weather["daily"][0]["temp"]["max"])
        draw.text((todayx + 5, forecasty + 100), str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24,
                  fill=0)
        precipxoffset = 10
        precipyoffset = 120
        # today's precip chance
        if todaymintemp < 32:
            # snow image!
            draw.text((todayx + precipxoffset, forecasty + precipyoffset), weather_font_dict['13d'],
                      font=weatherfont32,
                      fill=0)
        else:
            # lame, no snow
            draw.text((todayx + precipxoffset, forecasty + precipyoffset), weather_font_dict['10d'],
                      font=weatherfont32,
                      fill=0)
        draw.text((todayx + precipxoffset + 40, forecasty + precipyoffset + 13),
                  str(round(weather["daily"][0]["pop"])) + "%", font=textfont32, fill=0)

        # Tomorrow's Forecast
        tomorrowx = todayx + 110

        draw.text((tomorrowx, forecasty), "Tomorrow", font=textfont32)
        draw.text((tomorrowx + 45, forecasty + 25), weather_font_dict[weather["daily"][1]["weather"][0]["icon"]],
                  font=weatherfont48,
                  fill=0)
        tomorrowmaxtemp = round(weather["daily"][1]["temp"]["max"])
        tomorrowmintemp = round(weather["daily"][1]["temp"]["min"])
        draw.text((tomorrowx + 30, forecasty + 100), str(tomorrowmaxtemp) + "°/" + str(tomorrowmintemp) + "°",
                  font=textfont24,
                  fill=0)
        precipxoffset += 30  # to fix scaling
        # tomorrow's precip chance
        if tomorrowmintemp < 32:
            # snow image!
            draw.text((tomorrowx + precipxoffset, forecasty + precipyoffset), weather_font_dict['13d'],
                      font=weatherfont32,
                      fill=0)
        else:
            # lame, no snow
            draw.text((tomorrowx + precipxoffset, forecasty + precipyoffset), weather_font_dict['10d'],
                      font=weatherfont32,
                      fill=0)
        draw.text((tomorrowx + precipxoffset + 40, forecasty + precipyoffset + 13),
                  str(round(weather["daily"][1]["pop"])) + "%", font=textfont32, fill=0)

        # Draw division lines
        if draw_weather_lines:
            divider_offset = 6
            weather_bottom_divider_offset = 18
            draw.line([(todayx - divider_offset, weather_toplefty + 2 * h),
                       (todayx - divider_offset, epd_height - weather_bottom_divider_offset)], width=2)
            draw.line([(tomorrowx - divider_offset, weather_toplefty + 2 * h),
                       (tomorrowx - divider_offset, epd_height - weather_bottom_divider_offset)], width=2)
            draw.line([(weather_topleftx, epd_height - weather_bottom_divider_offset),
                       (epd_width, epd_height - weather_bottom_divider_offset)], width=2)
            pass
        # Print weather location, update time
        draw.text((weather_topleftx + 8, epd_height - 12), "{}".format(geolocation["data"][0]["label"]),
                  font=textfont12)
        draw.text((epd_width - 110, epd_height - 12), "Updated {}:{}".format(now.hour, now.minute), font=textfont12)
    return Himage
