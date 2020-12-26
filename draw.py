from PIL import ImageDraw, Image, ImageFont
import calendar, datetime, requests

weather_font_dict = {
    '01d': '\uf00d', '02d': '\uf002', '03d': '\uf013',
    '04d': '\uf012', '09d': '\uf01a ', '10d': '\uf019',
    '11d': '\uf01e', '13d': '\uf01b', '50d': '\uf014',
    '01n': '\uf02e', '02n': '\uf013', '03n': '\uf013',
    '04n': '\uf013', '09n': '\uf037', '10n': '\uf036',
    '11n': '\uf03b', '13n': '\uf038', '50n': '\uf023'
}


def image_draw(epd_width, epd_height):
    textfont32 = ImageFont.truetype('CourierStd.otf', 32)
    textfont24 = ImageFont.truetype('CourierStd.otf', 24)
    textfont16 = ImageFont.truetype('CourierStd.otf', 16)
    weatherfont48 = ImageFont.truetype('weathericons-regular-webfont.ttf', 48)
    weatherfont32 = ImageFont.truetype('weathericons-regular-webfont.ttf', 32)
    Himage = Image.new('1', (epd_width, epd_height), 255)
    draw = ImageDraw.Draw(Himage)
    # Generate divider lines
    draw.line((epd_width / 2, 0, epd_width / 2, epd_height), fill=0, width=2)
    draw.line((epd_width / 2, epd_height / 2, epd_width, epd_height / 2), fill=0, width=2)
    # Generate calendar in top-right
    cal = calendar.TextCalendar(calendar.SUNDAY)
    now = datetime.datetime.now()
    monthCal = cal.formatmonth(now.year, now.month)
    cal_topleftx = epd_width / 2
    cal_toplefty = 0
    weather_topleftx = epd_width / 2
    weather_toplefty = epd_height / 2
    draw.text((cal_topleftx + 10, cal_toplefty + 20), monthCal, font=textfont32, fill=0)
    # pull from weather service
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/onecall?lat=37.9514&lon=-91.7713&appid=d2a905d801e8a1b23ac0bcb292ec0949&units=imperial")
    print("request complete")
    weather = r.json()
    draw.text((weather_topleftx + 5, weather_toplefty + 5), "Weather", font=textfont32)
    currentx = weather_topleftx + 30
    forecasty = weather_toplefty + 50

    # Current Weather
    draw.text((currentx, forecasty), "Now", font=textfont32)
    draw.text((currentx + 3, forecasty + 25), weather_font_dict[weather["current"]["weather"][0]["icon"]], font=weatherfont48,
              fill=0)
    draw.text((currentx + 10, forecasty + 100), str(round(weather["current"]["temp"])) + "°", font=textfont24, fill=0)
    draw.text((currentx - 18, forecasty + 128), "Feels Like:", font=textfont16,
              fill=0)
    draw.text((currentx + 10, forecasty + 150), str(round(weather["current"]["feels_like"])) + "°", font=textfont24, fill=0)

    # Today's Forecast
    todayx = currentx + 110
    draw.text((todayx, forecasty), "Today", font=textfont32)
    draw.text((todayx + 15, forecasty + 25), weather_font_dict[weather["daily"][0]["weather"][0]["icon"]],
              font=weatherfont48,
              fill=0)
    todaymintemp = round(weather["daily"][0]["temp"]["min"])
    todaymaxtemp = round(weather["daily"][0]["temp"]["max"])
    draw.text((todayx + 5, forecasty + 100), str(todaymaxtemp) + "°/" + str(todaymintemp) + "°", font=textfont24, fill=0)
    precipxoffset = 10
    precipyoffset = 120
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
    draw.text((todayx+precipxoffset+40, forecasty+precipyoffset+13),str(round(weather["daily"][0]["pop"])) + "%", font=textfont32, fill=0)
    return Himage
