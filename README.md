# E-Ink Photo Frame

### Description

This is the source code for a Raspberry Pi-powered e-ink photo frame that I've been working on for a week or two. It draws from several online services to provide up-to-date headlines, a calendar of the month, and the weather in your area.

### Requirements

 - E-Ink display (I use a [Waveshare 7.5 inch 800x480](https://www.amazon.com/waveshare-7-5inch-HAT-Raspberry-Consumption/dp/B075R4QY3L). Instructions are for this device.)
 - Raspberry Pi with internet access
 - Python3 with requests package
 - [OpenWeatherMap](https://openweathermap.org/), [positionstack](https://positionstack.com/), and [TheNewsAPI](https://www.thenewsapi.com/) accounts & API keys  
 - (Technically optional, but highly recommended) Mounting hardware - photo frame, nail, etc.

### Installation

1. Configure the Raspberry Pi with the necessary drivers and applications as described by [Waveshare](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT#Enable_SPI_interface).
2. Clone the repository to your Raspberry Pi:  ```git clone https://github.com/rkruger01/e_ink_display.git```
3. Open config.txt and enter your configuration information. 
           
        [Config]
        owm_api_key = <OpenWeatherMap API key goes here>
        positionstack_api_key = <positionstack API key goes here>
        units = <imperial or metric (for weather)>
        city_zip_code = <Zip code used for positionstack geolocation lookup>
        city_country_code = <Country code used for positionstack geolocation lookup>
        newsapi_key = <TheNewsAPI key goes here>

4. Run main.py. In about 30 seconds, your e-ink display should update with US news & Tech news headlines, the monthly calendar, and your local weather. If it doesn't work, you can enable ```Debug=True``` in main.py to find any issues.

### Now what?

- Feel free to customize my code and make it your own! I currently have a specific list of websites I want news headlines from, which can be easily changed in draw.py.
- You can set up a cron job to automatically run main.py at a rate you want. Keep in mind, some APIs have daily/weekly/monthly call limits.