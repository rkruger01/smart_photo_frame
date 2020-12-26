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
    weatherfont = ImageFont.truetype('weathericons-regular-webfont.ttf', 48)
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
    draw.text((weather_topleftx + 5, weather_toplefty + 5), "Weather", font=textfont32)
    colx = weather_topleftx + 30
    coly = weather_toplefty + 50
    draw.text((colx, coly), "Now", font=textfont32)
    r = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=37.9514&lon=-91.7713&appid=d2a905d801e8a1b23ac0bcb292ec0949&units=imperial")
    weather = r.json()
    #Current Weather
    draw.text((colx + 5, coly + 30), weather_font_dict[weather["current"]["weather"][0]["icon"]], font=weatherfont, fill=0)
    draw.text((colx, coly + 100), str(weather["current"]["feels_like"]) + "°", font=textfont24, fill=0)
    print(weather["current"]["feels_like"], "f degrees")
    return Himage
