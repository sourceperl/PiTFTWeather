import os, syslog
import pygame
import signal
import time
import pywapi
import string


# global vars
is_run = True
# weather icons path
iconsPath = "./icons/"
# location for Lille, FR on weather.com
weatherDotComLocationCode = 'FRXX0052'
# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

# update interval
updateRate = 600 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        # raspberry official display is on framebuffer 0
        os.putenv('SDL_FBDEV', '/dev/fb0')
        # init pygame
        pygame.display.init()
        size = (pygame.display.Info().current_w,
                pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # clear screen
        self.screen.fill((0, 0, 0))
        # init font
        pygame.font.init()
        # update screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."
        pygame.quit()

# exit handler
def sigterm_handler(signum, frame):
   global is_run
   is_run = False

# manage SIGTERM for clean exit with supervisord
signal.signal(signal.SIGTERM, sigterm_handler)

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 2 sizes
font = pygame.font.Font(fontpath, 20)
fontSm = pygame.font.Font(fontpath, 18)

while(is_run):
    # retrieve data from weather.com
    #TODO catch error and retry
    weather = pywapi.get_weather_from_weather_com(weatherDotComLocationCode,
                                                  units='metric')
    # extract current data for today
    station = weather['current_conditions']['station']
    today = weather['forecasts'][0]['day_of_week'][0:3] + " " \
          + weather['forecasts'][0]['date'][4:] + " " \
          + weather['forecasts'][0]['date'][:3]
    windSpeed = int(weather['current_conditions']['wind']['speed'])
    currWind = "{:.0f} km/h ".format(windSpeed) \
               + weather['current_conditions']['wind']['text']
    currTemp = weather['current_conditions']['temperature'] \
               + " "+ u'\N{DEGREE SIGN}' + "C"
    currPress = weather['current_conditions']['barometer']['reading'][:-3] \
                + " hPa"
    uv = "UV {}".format(weather['current_conditions']['uv']['text'])
    humid = "Hum {} %".format(weather['current_conditions']['humidity'])
    # extract forecast data
    forecastDays = {}
    forecaseHighs = {}
    forecaseLows = {}
    forecastPrecips = {}
    forecastWinds = {}
    start = 0
    try:
        test = float(weather['forecasts'][0]['day']['wind']['speed'])
    except ValueError:
        start = 1
    for i in range(start, 5):
        if not(weather['forecasts'][i]):
            break
        forecastDays[i] = weather['forecasts'][i]['day_of_week'][0:3]
        forecaseHighs[i] = weather['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
        forecaseLows[i] = weather['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
        forecastPrecips[i] = weather['forecasts'][i]['day']['chance_precip'] + "% (pluie)"
        forecastWinds[i] = "{:.0f}".format(int(weather['forecasts'][i]['day']['wind']['speed'])) + \
                           " km/h "+weather['forecasts'][i]['day']['wind']['text']
    # blank the screen
    mytft.screen.fill(colourBlack)
    # Render the weather logo at 0,0
    icon = iconsPath+ (weather['current_conditions']['icon']) + ".png"
    logo = pygame.image.load(icon).convert_alpha()
    mytft.screen.blit(logo, (0, 0))
    # set the anchor for the current weather data text
    textAnchorX = 190
    textAnchorY = 5
    textYoffset = 20
    # add current weather data text artifacts to the screen
    text_surface = font.render(station, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(today, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(currTemp, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(currWind, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(currPress, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(uv, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    textAnchorY+=textYoffset
    text_surface = font.render(humid, True, colourWhite)
    mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
    # set X axis text anchor for the forecast text
    textAnchorX = 0
    textXoffset = 140
    # add each days forecast text
    for i in forecastDays:
        textAnchorY = 180
        text_surface = fontSm.render(forecastDays[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = fontSm.render(forecaseHighs[int(i)]+"/"+forecaseLows[int(i)], \
                                     True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = fontSm.render(forecastPrecips[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorY+=textYoffset
        text_surface = fontSm.render(forecastWinds[int(i)], True, colourWhite)
        mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
        textAnchorX+=textXoffset
    # refresh the screen with all the changes
    pygame.display.update()
    # Wait
    time.sleep(updateRate)

