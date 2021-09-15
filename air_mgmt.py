#!/usr/bin/env python3
import json
import requests
import paho.mqtt.client as mqtt
from urllib.request import urlopen
from datetime import datetime
from api import add_equip_log


with open('json/settings.json', 'r') as settings_file:
    settings = json.load(settings_file)
    settings = settings['grow_room']

#Generate current date and time to be referenced throughout script
now = datetime.now() 
timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
hour = now.strftime("%H")
hour = int(hour)	

#Connect to Mosquitto Server for door control
#host = settings['equipment']['air']['door']['host']
#client = mqtt.Client('door')
#client.connect(host)
door = '/vent/openclose'
door_open = 0

#Base min and max humidity params
min_humid = settings['climate_settings']['min_humid']
max_humid = settings['climate_settings']['max_humid']

#JSON URLs for different sensors and data
weather_forecast = settings['equipment']['air']['shared_data']['forecast']['api']
weather_station = settings['equipment']['air']['sensors']['weather_station']['api']
hygrometer = settings['equipment']['air']['sensors']['hygrometer']['api']

def get_weather_forecast():
    """Retrieves NWS hourly forecast for the location of the grow room
    """
    forecast_temps = [] # List to hold extracted forecast temps

    #Opens the cached forecast to check if it is current
    with open('forecast.json', 'r') as forecast_cache:
        last_forecast = json.load(forecast_cache)
    forecast_time = last_forecast[0]['startTime']
    forecast_hour = int(forecast_time[11:13])
    if forecast_hour == hour:
        hourly_forecasts = last_forecast
    else: #If it is not current try to download an updated forecast
        try:
            response = requests.get(weather_forecast)
            data = response.json()
            hourly_forecasts = data['properties']['periods']

            for i in range(23): #Loop through the NWS Forecast deleting all the past hours
                forecast_time = hourly_forecasts[0]['startTime']
                forecast_hour = int(forecast_time[11:13])
                if forecast_hour != hour:
                    hourly_forecasts.pop(0)
                elif forecast_hour == hour: #When the correct hour is found, exit tje loop
                    break
            with open('forecast.json', 'w') as forecast_cache: #Overwrite old forecast with updated one starting at the current hour
                json.dump(hourly_forecasts, forecast_cache)
        except (requests.HTTPError, KeyError): #If the forecast can't be retrieved, find the correct hour in the last forecast and use that data instead
            for i in range(16):
                forecast_time = last_forecast[0]['startTime']
                forecast_hour = int(forecast_time[11:13])
                if forecast_hour != hour:
                    last_forecast.pop(0)
                elif forecast_hour == hour:
                    break
            hourly_forecasts = last_forecast
    
    #Extract the temperature for the next 8 hours
    for i in range(8):
        forecast_temps.append(hourly_forecasts[i]['temperature'])

    return forecast_temps

def get_outdoor_weather():
    """Retrieves weather data from tempest weather station in Backyard
    """
    try: #Attempts to retrieve the lastest reading from the station
        response = requests.get(weather_station)
        data = response.json()
        outdoor_temp = (data['obs'][0]['air_temperature'] * 1.8) + 32
        brightness = data['obs'][0]['brightness']
        with open('weather_station.json', 'w') as weather_cache: #Overwrites old weather data with most recent observation
            json.dump(data, weather_cache)
    except: #If it can't be reached, find other data to use instead to prevent crashing
        with open('weather_station.json', 'r') as weather_cache:
            last_weather = json.load(weather_cache)
        weather_time = datetime.fromtimestamp(last_weather['obs'][0]['timestamp'])
        weather_hour = int(weather_time.strftime("%H"))
        if weather_hour == hour: #Check if the last weather station update is less than an hour old, if it is, use those readings
            outdoor_temp = (last_weather['obs'][0]['air_temperature'] * 1.8) + 32
            brightness = last_weather['obs'][0]['brightness']
        else: #If weather station update > 1 hour old use the forecasted temperature for that hour from the last retrieved weather forecast
            with open('forecast.json', 'r') as forecast_cache:
                forecast = json.load(forecast_cache)
                for hour_forecast in forecast:
                    if hour == int(hour_forecast['startTime'][11:13]):
                        weather = hour_forecast
                        break
            outdoor_temp = weather['temperature']
            #Assume its bright since the weather forecast doesnt provide a lux reading
            brightness = 100000

    return int(outdoor_temp), brightness

def get_hygrometer_reading():
    """Retrieves the Inside temp and humidity from the Ubibot Rest API for the hygrometer in the grow room
    """
    response = urlopen(hygrometer)
    data = json.loads(response.read().decode())
    current = data['channels'][0]['last_values'].split("\"value\":")
    inside_temp = (float(current[1][0:5]) * 1.8) + 32 #Convert C to F
    inside_humid = int(current[3][0:2])
    return int(inside_temp), inside_humid

def get_temp_limits(outdoor_temp):
    """Set temperature limits based on time, outside temps and forecasted temps for the next 8 hours
    """
    forecast_temps = get_weather_forecast()
    #Standard min and max temps
    min_temp = settings['climate_settings']['min_temp']
    max_temp = settings['climate_settings']['max_temp']
    #Variables to simplify what temperature range the day is
    warm_day = False
    hot_day = False
    cold_day = False
    for forecast_temp in forecast_temps: #Loop through the next 8 hours of forecast temps checking for extreme temps
        if outdoor_temp > 74 or forecast_temp > 74:
            warm_day = True
            if outdoor_temp > 84 or forecast_temp > 84:
                hot_day = True
        if outdoor_temp <= 35 or forecast_temp <= 35:
            cold_day = True
    if hour > 6 and hour < 19: #if the sun is up, need to switch to sunrise and sunset times
        if hot_day and cold_day: #Try to keep the temp in smaller range if there is gonna be a big temp swing
            max_temp -= 3
            min_temp += 3
        elif warm_day and not hot_day: # Try to keep the temp a little cooler if it is gonna be a warm day
            min_temp -= 2
            max_temp -= 2
        elif hot_day and not cold_day: # Try to keep the temp even cooler if it is gonna be beyond warm 
            max_temp -= 5
            min_temp -= 5
        elif cold_day and not hot_day: # Try to keep it a little warmer if it is gonna be cold to fight off overnight lows       
            min_temp += 2
            max_temp += 5
    elif hour > 2 and hour < 9: #IF it is the early morning, start adjsting temp ranges to help ease temp swings in the heat of the day
        if hot_day:
            max_temp -= 5
            min_temp -= 5
        elif warm_day and not hot_day:
            min_temp -= 3
            max_temp -= 3
    else: #OVernight min and max adjustments
        if cold_day:
            min_temp += 3
            max_temp += 2
        elif warm_day and not hot_day:
            min_temp -= 3
            max_temp -= 3
        elif hot_day:
            max_temp -= 5
            min_temp -= 5


    return min_temp, max_temp

def check_air(inside_temp, outdoor_temp, outdoor_brightness, inside_humid, min_temp, max_temp):
    """Makes a decision on actions to take depending on the temperature and humidity 
      both inside and outside of the grow room
    """
    tasks = [] #List to hold tasks decided on depending on the data
    temp_range = max_temp - min_temp
    

    if inside_temp <= min_temp: 
        if outdoor_temp - 10 > inside_temp: #If it is much warmer outside, open the door and pull in the air to save on heating costs
            tasks.append('door-5')
            tasks.append('b-fan-on')
        else: 
            tasks.append('heater-on')
            tasks.append('door-0')
        if inside_humid <= min_humid: #Turn the cooler on for humiditiy purposes, need to add a humidifier
            tasks.append('cooler-on')
    elif inside_temp >= max_temp: #Start trying to cool with just the swamp cooler and circulation fan to try to preserve humidity
        tasks.append('cooler-on')
        tasks.append('circ-fan-on')
        
        if outdoor_brightness < 60000 or hour > 13 or hour < 6: #If it is a sunny day and the during the hours the door gets sun, open it less to fight heat
            tasks.append('door-2')
        else:
            tasks.append('door-1')
        
        if inside_temp > max_temp + 1: #If the temp is still rising, turn on the ventilation and open the door wider
            tasks.append('u-fan-on')
            if 'door-1' in tasks:
                tasks.remove('door-1')
            if 'door-2' in tasks:
                tasks.remove('door-2')
            if outdoor_brightness < 60000:
                tasks.append('door-3')
            else:
                tasks.append('door-2')
            if inside_temp > max_temp + 4: #Last Resort kills the humidity but turns on the bottom ventilation fan
                tasks.append('b-fan-on')
            else: #If the temp is less than max_temp + 2, turn the bottom fan back off to try to rebuild humidity
                if settings['equipment']['air']['bottom-fan']['status'] == 'on':
                    tasks.append('b-fan-off')
                
        if inside_humid <= min_humid:
            tasks.append('cooler-on')
        
        if inside_humid >= max_humid:
            tasks.append('cooler-off')
            tasks.append('door-3')
    elif inside_temp - (temp_range/3) > min_temp and inside_temp + (temp_range/3) < max_temp: #If the temp is in the middle third of the temp range start turning things off
        tasks.append('heater-off')
        tasks.append('b-fan-off')
        tasks.append('u-fan-off')
        if inside_humid <= min_humid: #If the humidity is still to low, close the door but keep the cooler and circfan o
            tasks.append('cooler-on')
            tasks.append('circ-fan-on')
            tasks.append('door-0')
        elif inside_humid >= max_humid: #If its too high, turn off the cooler and open door
            tasks.append('cooler-off')
            tasks.append('door-3')
        else: #If the humiditiy is in range too turn everything else off and make sure the door is closed
            tasks.append('cooler-off')
            tasks.append('circ-fan-off')
            tasks.append('door-0')
    else: #If the temp is right, just try to alter the humidity
        if inside_humid <= min_humid:
            tasks.append('cooler-on')
            tasks.append('circ-fan-off')
        elif inside_humid >= max_humid:
            #Turn off humidifer and or swamp cooler and open door
            tasks.append('cooler-off')
            tasks.append('door-2')
            if outdoor_temp >= 50 and inside_temp > max_temp - (temp_range / 2): # Make sure its not dry because of the heater before blowing the air out
                tasks.append('circ-fan-on')
        elif inside_humid >= min_humid:
            tasks.append('humid-off')
    
    for task in tasks:
        if task == 'cooler-on':
            if settings['equipment']['air']['cooler']['status'] == 'off':
                settings['equipment']['air']['cooler']['status'] = 'on'
                settings['equipment']['air']['cooler']['last-on'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/swamp_cooler_on/with/key/beLHb8ZjZAJVzHxB1nSatB")
        elif task == 'cooler-off':
            if settings['equipment']['air']['cooler']['status'] == 'on':
                settings['equipment']['air']['cooler']['status'] = 'off'
                settings['equipment']['air']['cooler']['last-off'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/swamp_cooler_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                add_equip_log(settings['equipment']['air']['cooler'])
        elif task == 'humid-off':
            if settings['equipment']['air']['door']['status'] == 0:
                if settings['equipment']['air']['cooler']['status'] == 'on':
                    settings['equipment']['air']['cooler']['status'] = 'off'
                    settings['equipment']['air']['cooler']['last-off'] = timestamp
                    requests.get(url = "https://maker.ifttt.com/trigger/swamp_cooler_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                    add_equip_log(settings['equipment']['air']['cooler'])
        elif task == 'heater-on':
            if settings['equipment']['air']['heater']['status'] == 'off':
                settings['equipment']['air']['heater']['status'] = 'on'
                settings['equipment']['air']['heater']['last-on'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/heater_on/with/key/beLHb8ZjZAJVzHxB1nSatB")
        elif task == 'heater-off':
            if settings['equipment']['air']['heater']['status'] == 'on':
                settings['equipment']['air']['heater']['status'] = 'off'
                settings['equipment']['air']['heater']['last-off'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/heater_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                add_equip_log(settings['equipment']['air']['heater'])
        elif task == 'b-fan-on':
            if settings['equipment']['air']['bottom-fan']['status'] == 'off':
                settings['equipment']['air']['bottom-fan']['status'] = 'on'
                settings['equipment']['air']['bottom-fan']['last-on'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/bottom_fan_on/with/key/beLHb8ZjZAJVzHxB1nSatB")
        elif task == 'b-fan-off':
            if settings['equipment']['air']['bottom-fan']['status'] == 'on':
                settings['equipment']['air']['bottom-fan']['status'] = 'off'
                settings['equipment']['air']['bottom-fan']['last-off'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/bottom_fan_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                add_equip_log(settings['equipment']['air']['bottom-fan'])
        elif task == 'u-fan-on':
            if settings['equipment']['air']['upper-fan']['status'] == 'off':
                settings['equipment']['air']['upper-fan']['status'] = 'on'
                settings['equipment']['air']['upper-fan']['last-on'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/upper_fan_on/with/key/beLHb8ZjZAJVzHxB1nSatB")
        elif task == 'u-fan-off':
            if settings['equipment']['air']['upper-fan']['status'] == 'on':
                settings['equipment']['air']['upper-fan']['status'] = 'off'
                settings['equipment']['air']['upper-fan']['last-off'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/upper_fan_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                add_equip_log(settings['equipment']['air']['upper-fan'])
        elif task == 'circ-fan-on':
            if settings['equipment']['air']['circulation-fan']['status'] == 'off':
                settings['equipment']['air']['circulation-fan']['status'] = 'on'
                settings['equipment']['air']['circulation-fan']['last-on'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/circulation_fan_on/with/key/beLHb8ZjZAJVzHxB1nSatB")
        elif task == 'circ-fan-off':
            if settings['equipment']['air']['circulation-fan']['status'] == 'on':
                settings['equipment']['air']['circulation-fan']['status'] = 'off'
                settings['equipment']['air']['circulation-fan']['last-off'] = timestamp
                requests.get(url = "https://maker.ifttt.com/trigger/circulation_fan_off/with/key/beLHb8ZjZAJVzHxB1nSatB")
                add_equip_log(settings['equipment']['air']['circulation-fan'])
        elif task == 'door-0':
            if settings['equipment']['air']['door']['status'] != 0:
                settings['equipment']['air']['door']['status'] = 0
                settings['equipment']['air']['door']['last-close'] = timestamp
                #client.publish(door, door_open)
        elif task == 'door-1':
            if settings['equipment']['air']['door']['status'] == 1:
                pass
            else:
                if settings['equipment']['air']['door']['status'] == 0:
                    settings['equipment']['air']['door']['last-open'] = timestamp
                door_open = (settings['equipment']['air']['door']['status'] - 1) * -1
                settings['equipment']['air']['door']['status'] = 1
                #client.publish(door, door_open)
        elif task == 'door-2':
            if settings['equipment']['air']['door']['status'] == 2:
                pass
            else:
                if settings['equipment']['air']['door']['status'] == 0:
                    settings['equipment']['air']['door']['last-open'] = timestamp
                door_open = (settings['equipment']['air']['door']['status'] - 2) * -1
                settings['equipment']['air']['door']['status'] = 2
                #client.publish(door, door_open) 
        elif task == 'door-3':
            if settings['equipment']['air']['door']['status'] == 3:
                pass
            else:
                if settings['equipment']['air']['door']['status'] == 0:
                    settings['equipment']['air']['door']['last-open'] = timestamp
                door_open = (settings['equipment']['air']['door']['status'] - 3) * -1
                settings['equipment']['air']['door']['status'] = 3
                #client.publish(door, door_open) 
        elif task == 'door-4':
            if settings['equipment']['air']['door']['status'] == 4:
                pass
            else:
                if settings['equipment']['air']['door']['status'] == 0:
                    settings['equipment']['air']['door']['last-open'] = timestamp
                door_open = (settings['equipment']['air']['door']['status'] - 4) * -1
                settings['equipment']['air']['door']['status'] = 2
                #client.publish(door, door_open) 
                
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file)
            
outdoor_temp, outdoor_brightness = get_outdoor_weather()
min_temp, max_temp = get_temp_limits(outdoor_temp)
inside_temp, inside_humid = get_hygrometer_reading()
check_air(inside_temp, outdoor_temp, outdoor_brightness, inside_humid, min_temp, max_temp)
