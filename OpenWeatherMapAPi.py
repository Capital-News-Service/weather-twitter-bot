import pyowm
from datetime import datetime
import datetime as dt
import math
import tweepy as twp
import pandas as pd
import numpy as np
import json

########################### CONFIG ############################
keys = {}
with open("key.json","r") as f:
        keys = json.loads(f.read())
#Consumer keys and access tokens, used for OAuth
consumer_key =  keys["consumer_key"]
consumer_secret = keys["consumer_secret"]
access_token =  keys["access_token"]
access_secret = keys["access_secret"]

# OAuth process, using the keys and tokens
auth = twp.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

#Creation of the interface
api = twp.API(auth)

#retrieve the data from the api
owm = pyowm.OWM(keys["API_key"])
fc = owm.three_hours_forecast('Baltimore')
forecast = fc.get_forecast()
weatherObj = forecast.get_weathers()

########################### CODE ############################

#store the data in the lists:
def getData():
    temperatureData = []
    humidityData = []
    timeData = []
    for weather in weatherObj:
        temperatureData.append(weather.get_temperature(unit='fahrenheit'))
        humidityData.append(weather.get_humidity())
        timeData.append(weather.get_reference_time('date'))

    maxTemperatureData = []
    for temp in temperatureData:
        maxTemperatureData.append(math.ceil(temp['temp_max'] * 100 / 100))

    return maxTemperatureData, humidityData, timeData

#assign data to three list for future extraction
tempoTempData = getData()[0]
tempoHumidityData = getData()[1]
tempoTimeData = getData()[2]

#finding the maxTemperature of each day
def getTempTimeData(maxTemp, timeList):
    minimum0 = 0
    minimum1 = 0
    minimum2 = 0
    minimum3 = 0
    minimum4 = 0
    minimum5 = 0
    listTempTime = zip(maxTemp, timeList)
    for temp, time in listTempTime:
        if time.date() == datetime.today().date():
            if(temp > minimum0):
                maxT = []
                newDate0 = []
                newDate0.append(time)
                maxT.append(temp)
                minimum0 = temp
        elif time.date() == datetime.today().date() + dt.timedelta(days=1):
            if(temp > minimum1):
                maxT1 = []
                newDate1 = []
                maxT1.append(temp)
                newDate1.append(time)
                minimum1 = temp
        elif time.date() == datetime.today().date() + dt.timedelta(days=2):
            if (temp > minimum2):
                maxT2 = []
                newDate2 = []
                maxT2.append(temp)
                newDate2.append(time)
                minimum2 = temp
        elif time.date() == datetime.today().date() + dt.timedelta(days=3):
            if (temp > minimum3):
                maxT3 = []
                newDate3 = []
                maxT3.append(temp)
                newDate3.append(time)
                minimum3 = temp
        elif time.date() == datetime.today().date() + dt.timedelta(days=4):
            if (temp > minimum4):
                maxT4 = []
                newDate4 = []
                maxT4.append(temp)
                newDate4.append(time)
                minimum4 = temp
        else:
            if (temp > minimum5):
                maxT5 = []
                newDate5 = []
                maxT5.append(temp)
                newDate5.append(time)
                minimum5 = temp
    outputTemp = maxT + maxT1+ maxT2 + maxT3 + maxT4 + maxT5
    outputDate = newDate0 + newDate1 + newDate2 + newDate3 + newDate4 + newDate5
    return  outputTemp,outputDate

#Obtain the highest humidity of the day with the highest temperature
def getHumidity(humidityData, timeFinalData, timeTempoData):
    listHumidity = zip(humidityData,timeTempoData)
    humidityList = []
    for humidity,timeTempo in listHumidity:
        for time in timeFinalData:
            if(time == timeTempo):
                humidityList.append(humidity)

    return humidityList

#assign the data to final lists of temperature, time and humidity data
temperatureFinalData = getTempTimeData(tempoTempData, tempoTimeData)[0]
timeFinalData = getTempTimeData(tempoTempData, tempoTimeData)[1]
humidityFinalData = getHumidity(tempoHumidityData, timeFinalData, tempoTimeData)

#Format time Object into String
def dayInString(timeFinalData):
    dayString = []
    for day in timeFinalData:
        newDay = day.strftime('%A, %B %d, %H:%M %p')
        dayString.append(newDay)
    return dayString

#Reassign time in String to timeFinalData list
timeFinalData = dayInString(timeFinalData)

#the formula is calculated first
def simpleHeatIndex(temperature, humidity):
    answer = 0.5 * (temperature + 61.0 + [(temperature - 68.0) * 1.2] + (humidity * 0.094))
    return math.ceil(answer * 100 / 100)

#the heat index is then compared. If it is 80 or higher, the full formula is applied
def fullHeatIndex(temperature, humidity):
    heatIndex = -42.379 + 2.04901523 * temperature + 10.1433127 * humidity - 0.22475541 * temperature * humidity
    - 0.00683783 * temperature * temperature - 0.05481717 * humidity * humidity + 0.00085282 * temperature * humidity * \
    humidity - 0.00000199 * temperature * temperature * humidity * humidity

    if temperature > 80 and temperature < 112 and humidity < 13:
        subtractionheat = ((13 - humidity)/4) * math.sqrt((17 - abs(temperature - 95)) / 17)
        return heatIndex - subtractionheat
    elif humidity > 85 and temperature > 80 and temperature < 87:
        additionheat = ((humidity - 85) / 10) * ((87 - temperature ) / 5)
        return heatIndex + additionheat
    else:
        return math.ceil(heatIndex * 100 / 100)

#determine the actual heat index
def finalHeatIndex(temperature, humidity):
    if simpleHeatIndex(temperature,humidity) >= 80:
        return fullHeatIndex(temperature, humidity)

#determine the recommendation
def recommendation(heatIndex):
    if 80 <= heatIndex < 90:
        return "Caution: Fatigue possible with prolonged exposure and/or physical activity"
    elif 90 <= heatIndex < 103:
        return "Extreme Caution: Heat stroke, heat cramps, or heat exhaustion possible with problonged exposure and/or physical activity"
    elif 103 <= heatIndex <= 124:
        return "Danger: Heat cramps or heat exhaustion likely, and heat stroke possible with prolonged exposure and/or physical activity"
    elif 125 <= heatIndex:
        return "Extreme Danger: Heat stroke highly likely"

#Calculate the heat data using the temperature data and humidity data
#return heat indexes as a list
def getHeatData(temperatureFinalData, humidityFinalData):
    maxTemp = np.array(temperatureFinalData)
    humidityList = np.array(humidityFinalData)
    heatIndex = []
    for temperature, humidity in zip(maxTemp, humidityList):
       heatIndex.append(simpleHeatIndex(temperature,humidity))

    heatIndex = np.array(heatIndex).tolist()
    return heatIndex

#Obtain the heat data
heatFinalData = getHeatData(temperatureFinalData,humidityFinalData)


#store the tweet for the next five days
#turn the data into data frame and return a list of String for the tweet.
def getTweet():
    table = pd.DataFrame({'Temperature': temperatureFinalData})
    table['Humidity'] = humidityFinalData
    table['Time'] = timeFinalData
    table['Heat Index'] = heatFinalData
    tweetList = []
    index = len(table)
    i = 0
    while i < index:
        dict = table.iloc[i].to_dict()
        tweet = 'On ' + dict['Time'] + ' ,the heat index is ' + str(dict['Heat Index']) + ' .The temperature reaches ' + \
                str(dict['Temperature']) + ' with humidity up to ' + str(dict['Humidity']) + ' percent.'
        tweetList.append(tweet)
        i += 1

    return tweetList

#Run the bot
def runBot():
    tweetOut = ''.join(getTweet()[0])
    # Tweet the list of data
    api.update_status(tweetOut)

#runBot()