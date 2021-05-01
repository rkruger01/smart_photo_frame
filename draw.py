import calendar
import datetime
import logging
import sys
import os
import requests
from math import floor
from PIL import ImageDraw, Image, ImageFont
import configparser

do_fetch_weather = True
draw_weather_lines = True
do_draw_calendar = True
do_display_news = True
do_draw_border = True

weather_font_dict = {
    '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
    '04d': '\uf012', '09d': '\uf01a ', '10d': '\uf019',
    '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
    '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
    '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
    '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
}

weatherfont48 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'weathericons-regular-webfont.ttf'), 48)
weatherfont32 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'fonts', 'weathericons-regular-webfont.ttf'), 32)
textfont32 = ImageFont.load(os.path.join(os.path.dirname(__file__), 'fonts', 'ter-u32n.pil'))
textfont24 = ImageFont.load(os.path.join(os.path.dirname(__file__), 'fonts', 'ter-u24n.pil'))
textfont16 = ImageFont.load(os.path.join(os.path.dirname(__file__), 'fonts', 'ter-u16n.pil'))
textfont12 = ImageFont.load(os.path.join(os.path.dirname(__file__), 'fonts', 'ter-u12n.pil'))
included_general_news_domains = ["cnn.com", "nytimes.com", "usatoday.com", "reuters.com", "politico.com",
                    "npr.org", "latimes.com", "abcnews.go.com", "nbcnews.com", "cbsnews.com"]
excluded_tech_domains = ["businessinsider.com", "qz.com"]
general_news_non_tech_url = "https://api.thenewsapi.com/v1/news/top?api_token={}&language=en&exclude_categories=tech&locale=us&domains={}"
tech_news_url = "https://api.thenewsapi.com/v1/news/top?api_token={}&language=en&categories=tech&locale=us&exclude_domains={}"


def display_news(epd_width, epd_height, draw: ImageDraw, config: configparser.ConfigParser):
    # This function could use a refactor because of all of the code reuse, but it works
    news_rightx = epd_width / 2
    general_news_header = "Top USA Headlines"
    tech_news_header = "Top Tech Headlines"
    header_font = textfont32
    headline_font = textfont16
    headline_offset_from_side = 10
    second_line_x_offset_from_headline = 10
    first_headline_offset_from_top = 50
    try:
        api_key = config['Config']['newsapi_key']
    except configparser.MissingSectionHeaderError as e:
        logging.error(e)
        sys.exit(1)
    # Draw header rectangle
    w, h = draw.textsize(general_news_header, font=header_font)
    draw.text(((news_rightx - w) / 2, 10), general_news_header, font=header_font)
    y = first_headline_offset_from_top
    r = requests.get(general_news_non_tech_url.format(api_key, ",".join(included_general_news_domains)))
    results = r.json()
    general_articles = results['data']
    # Process article headers
    titles_with_source = []
    for article in general_articles:
        titles_with_source.append([article['source'], article['title']])
    # For each headline: Calculate size, trim remainder, display
    for headline in titles_with_source:
        article_source = headline[0]
        article_title = headline[1]
        second_line = ""
        text_to_display = article_source + ": " + article_title
        text_to_display = text_to_display.encode('latin-1', 'ignore')
        w, h = draw.textsize(text_to_display, font=headline_font)
        # Split text into at most 2 lines
        while w + headline_offset_from_side > news_rightx:
            article_title, excess_word = article_title.rsplit(" ", 1)
            second_line = excess_word + " " + second_line
            text_to_display = article_source + ": " + article_title
            text_to_display = text_to_display.encode('latin-1', 'ignore')
            w, h = draw.textsize(text_to_display, font=headline_font)
        draw.text((headline_offset_from_side, y), text_to_display, font=headline_font)
        y += h
        if second_line:
            # trim excess characters and replace with "..." at the end
            second_line = second_line.encode('latin-1', 'ignore')
            encoded_space = " ".encode('latin-1')
            encoded_ellipse = "...".encode('latin-1')
            w, h = draw.textsize(second_line, font=headline_font)
            w_periods, h = draw.textsize("...", font=headline_font)
            needs_periods = False
            if w + headline_offset_from_side + second_line_x_offset_from_headline > news_rightx:
                while w + w_periods + headline_offset_from_side + second_line_x_offset_from_headline > news_rightx:
                    needs_periods = True
                    second_line = second_line[:-1]
                    w, h = draw.textsize(second_line, font=headline_font)
            if needs_periods:
                if second_line.endswith(encoded_space):
                    # Removes floating space issue
                    second_line = second_line[:-1]
                second_line = second_line + encoded_ellipse
            draw.text((headline_offset_from_side + second_line_x_offset_from_headline, y), second_line,
                      font=headline_font)
            y += 1.3 * h
    # Do Tech news here

    w, h = draw.textsize(tech_news_header, font=header_font)
    draw.text(((news_rightx - w) / 2, y), tech_news_header, font=header_font)
    y += 1.2*h
    r = requests.get(tech_news_url.format(api_key, ",".join(excluded_tech_domains)))
    results = r.json()
    general_articles = results['data']

    # Process article headers
    titles_with_source = []
    for article in general_articles:
        titles_with_source.append([article['source'], article['title']])

    # For each headline: Calculate size, trim remainder, display
    for headline in titles_with_source:
        article_source = headline[0]
        article_title = headline[1]
        second_line = ""
        text_to_display = article_source + ": " + article_title
        text_to_display = text_to_display.encode('latin-1', 'ignore')
        w, h = draw.textsize(text_to_display, font=headline_font)
        # Split text into at most 2 lines
        while w + headline_offset_from_side > news_rightx:
            article_title, excess_word = article_title.rsplit(" ", 1)
            second_line = excess_word + " " + second_line
            text_to_display = article_source + ": " + article_title
            text_to_display = text_to_display.encode('latin-1', 'ignore')
            w, h = draw.textsize(text_to_display, font=headline_font)
        draw.text((headline_offset_from_side, y), text_to_display, font=headline_font)
        y += h
        if second_line:
            # trim excess characters and replace with "..." at the end
            second_line = second_line.encode('latin-1', 'ignore')
            encoded_space = " ".encode('latin-1')
            encoded_ellipse = "...".encode('latin-1')
            w, h = draw.textsize(second_line, font=headline_font)
            w_periods, h = draw.textsize("...", font=headline_font)
            needs_periods = False
            if w + headline_offset_from_side + second_line_x_offset_from_headline > news_rightx:
                while w + w_periods + headline_offset_from_side + second_line_x_offset_from_headline > news_rightx:
                    needs_periods = True
                    second_line = second_line[:-1]
                    w, h = draw.textsize(second_line, font=headline_font)
            if needs_periods:
                if second_line.endswith(encoded_space):
                    # Removes floating space issue
                    second_line = second_line[:-1]
                second_line = second_line + encoded_ellipse
            draw.text((headline_offset_from_side + second_line_x_offset_from_headline, y), second_line,
                      font=headline_font)
            y += 1.5 * h
        else:
            y += .6*h
    return


def draw_calendar(epd_width, draw: ImageDraw, now: datetime):
    # Generate calendar in top-right
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
    y = h - 3
    # Draw calendar rows
    days = 'Su Mo Tu We Th Fr Sa'
    w, h = draw.textsize(days, font=textfont24)
    draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset), days, font=textfont24)
    for row in cal_with_zeros:
        row = [' ' + (str(x)) if x < 10 else str(x) for x in row]  # list comprehension magic
        row = ['  ' if x == ' 0' else x for x in row]  # Remove zeros from calendar
        line = ' '.join(row)
        logging.debug("Printing calendar row starting at {},{}".format(cal_topleftx + cal_x_offset,
                                                                       cal_toplefty + cal_y_offset + y))
        draw.text((cal_topleftx + (cal_topleftx - w) / 2, cal_toplefty + cal_y_offset + y), line, font=textfont24)
        y += h + 3
    offset_from_zero = now.day + leading_zeroes - 1
    today_x_grid = offset_from_zero % 7
    today_y_grid = floor(offset_from_zero // 7)
    logging.debug("Grid coordinates for today's date: {},{}".format(today_x_grid, today_y_grid))
    true_date_w, true_date_h = draw.textsize(" 00", font=textfont24)
    px_buffer = 3
    square_w, square_h = draw.textsize("00", font=textfont24)
    start_x = cal_topleftx + (cal_topleftx - w) / 2 + (true_date_w * today_x_grid) - px_buffer
    start_y = cal_toplefty + cal_y_offset + (today_y_grid * 30) + true_date_h - px_buffer
    logging.debug("Square starting at {},{}".format(start_x, start_y))
    draw.rectangle([(start_x, start_y), (start_x + square_w + 2 * px_buffer, start_y + square_h + 2 * px_buffer)],
                   width=2)
    return


def fetch_weather(epd_width, epd_height, draw: ImageDraw, now: datetime, config: configparser.ConfigParser):
    try:
        owm_api_key = config['Config']['owm_api_key']
        mapbox_api_key = config['Config']['mapbox_api_key']
        weather_units = config['Config']['units']
        weather_zip = config['Config']['city_zip_code']
        weather_country = config['Config']['city_country_code']
    except configparser.MissingSectionHeaderError as e:
        logging.error(e)
        sys.exit(1)
    # geomap address to coordinates
    query = weather_zip + "," + weather_country
    r = requests.get(
        "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?access_token={}".format(query,mapbox_api_key))
    geolocation = r.json()

    try:
        logging.debug("Weather fetched for {}".format(geolocation["features"][0]["place_name"]))
    except TypeError:
        logging.error("Error occured when trying to fetch weather location")
        sys.exit(1)
    weather_long = geolocation["features"][0]["center"][0]
    weather_lat = geolocation["features"][0]["center"][1]
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
    w, h = draw.textsize(str(round(weather["current"]["feels_like"]))
                         + "°", font=textfont24)
    draw.text((weather_topleftx + ((todayx - weather_topleftx) - w) / 2, forecasty + 145),
              str(round(weather["current"]["feels_like"])) + "°", font=textfont24,
              fill=0)

    # Today's Forecast
    w, h = draw.textsize("Today", font=textfont32)
    draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty), "Today", font=textfont32)
    w, h = draw.textsize(weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
                         font=weatherfont48)
    draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty + weather_image_offset),
              weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
              font=weatherfont48,
              fill=0)
    todaymintemp = round(weather["daily"][0]["temp"]["min"])
    todaymaxtemp = round(weather["daily"][0]["temp"]["max"])
    w, h = draw.textsize(str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24)
    draw.text((todayx + ((tomorrowx - todayx) - w) / 2, forecasty + tempoffset),
              str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24,
              fill=0)
    precipxoffset = 40
    precipyoffset = 120
    # today's precip chance
    if todaymintemp < 32:
        # snow image!
        w_image, h = draw.textsize(weather_font_dict['13d'], font=weatherfont32)
        w_text, h = draw.textsize(str(round(weather["daily"][0]["pop"])), font=textfont32)
        sum_w = w_image + w_text + precipxoffset / 2
        draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2, forecasty + precipyoffset),
                  weather_font_dict['13d'],
                  font=weatherfont32,
                  fill=0)
    else:
        # lame, no snow
        w_image, h = draw.textsize(weather_font_dict['10d'], font=weatherfont32)
        w_text, h = draw.textsize(str(round(weather["daily"][0]["pop"])), font=textfont32)
        sum_w = w_image + w_text + precipxoffset / 2
        draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2, forecasty + precipyoffset),
                  weather_font_dict['10d'],
                  font=weatherfont32,
                  fill=0)
    draw.text((todayx + ((tomorrowx - todayx) - sum_w) / 2 + precipxoffset, forecasty + precipyoffset + 13),
              str(round(weather["daily"][0]["pop"])) + "%", font=textfont32, fill=0)

    # Tomorrow's Forecast

    w, h = draw.textsize("Tomorrow", font=textfont32)
    draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty), "Tomorrow", font=textfont32)
    w, h = draw.textsize(weather_font_dict[weather["daily"][1]["weather"][0]["icon"]], font=weatherfont48)
    draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty + weather_image_offset),
              weather_font_dict[weather["daily"][1]["weather"][0]["icon"]],
              font=weatherfont48,
              fill=0)
    tomorrowmaxtemp = round(weather["daily"][1]["temp"]["max"])
    tomorrowmintemp = round(weather["daily"][1]["temp"]["min"])
    w, h = draw.textsize(str(tomorrowmaxtemp) + "°/" + str(tomorrowmintemp) + "°", font=textfont24)

    draw.text((tomorrowx + ((epd_width - tomorrowx) - w) / 2, forecasty + tempoffset),
              str(tomorrowmaxtemp) + "°/" + str(tomorrowmintemp) + "°",
              font=textfont24,
              fill=0)
    # tomorrow's precip chance
    if tomorrowmintemp < 32:
        # snow image!
        w_image, h = draw.textsize(weather_font_dict['13d'], font=weatherfont32)
        w_text, h = draw.textsize(str(round(weather["daily"][1]["pop"])), font=textfont32)
        sum_w = w_image + w_text + precipxoffset / 2
        draw.text((tomorrowx + ((epd_width - tomorrowx) - sum_w) / 2, forecasty + precipyoffset),
                  weather_font_dict['13d'],
                  font=weatherfont32,
                  fill=0)
    else:
        # lame, no snow
        w_image, h = draw.textsize(weather_font_dict['10d'], font=weatherfont32)
        w_text, h = draw.textsize(str(round(weather["daily"][1]["pop"])), font=textfont32)
        sum_w = w_image + w_text + precipxoffset / 2
        draw.text((tomorrowx + ((epd_width - tomorrowx) - sum_w) / 2, forecasty + precipyoffset),
                  weather_font_dict['10d'],
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
    w, h = draw.textsize("{}".format(geolocation["features"][0]["place_name"]), font=textfont12)
    draw.text((weather_topleftx + 8, epd_height - h-2), "{}".format(geolocation["features"][0]["place_name"]),
              font=textfont12)


def image_draw(epd_width, epd_height, config_file_name="config.txt"):
    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(os.path.dirname(__file__), config_file_name))
    except configparser.MissingSectionHeaderError as e:
        logging.error(e)
        exit(1)

    Himage = Image.new('1', (epd_width, epd_height), 255)
    draw = ImageDraw.Draw(Himage)

    # Generate divider lines
    draw.line((epd_width / 2, 0, epd_width / 2, epd_height), fill=0, width=2)
    draw.line((epd_width / 2, epd_height / 2, epd_width, epd_height / 2), fill=0, width=2)
    now = datetime.datetime.now()
    if do_draw_calendar:
        draw_calendar(epd_width, draw, now)
    if do_fetch_weather:
        fetch_weather(epd_width, epd_height, draw, now, config)
    if do_display_news:
        display_news(epd_width, epd_height, draw, config)
    if do_draw_border:
        draw.line([(0, 0), (0, epd_height)])
        draw.line([(0,0),(epd_width,0)])
        draw.line([(0,epd_height),(epd_width,epd_height)], width=3)
        draw.line([(epd_width,0),(epd_width,epd_height)], width=3)
    # Draw current time (not for clock, mostly to make sure it's running correctly
    w, h = draw.textsize("Updated {}:{}".format(now.hour, str(now.minute).zfill(2)), font=textfont12)
    draw.text((epd_width - w - 5, epd_height - h - 2), "Updated {}:{}".format(now.hour, str(now.minute).zfill(2)),
              font=textfont12)
    return Himage
