import pyowm
from datetime import datetime
import datetime as dt
import math
import tweepy as twp
import pandas as pd
import numpy as np
import json
keys = {}

with open("key.json","r") as f:
        keys = json.loads(f.read())
#Consumer keys and access tokens, used for OAuth
consumer_key = keys["consumer_key"]
consumer_secret = keys["consumer_secret"]
access_token = keys["access_token"]
access_secret = keys["access_secret"]

# OAuth process, using the keys and tokens
auth = twp.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

#Creation of the interface
api = twp.API(auth)


#Problem: after getting the maximum temperature of the five days, I have to reconstruct the humidity list along with the
# heat index list since they are not all the same length. Use the dateTime list to find the right humidity and reconstruct that?

#retrieve the data from the api
owm = pyowm.OWM(keys["API_key"])
fc = owm.three_hours_forecast('Baltimore')
forecast = fc.get_forecast()
weatherObj = forecast.get_weathers()

tempList = []
humidityList = []
timeList = []

#store the data in the lists:
for weather in weatherObj:
    tempList.append(weather.get_temperature(unit='fahrenheit'))
    humidityList.append(weather.get_humidity())
    timeList.append(weather.get_reference_time('date'))




#store the maximum temperature in a new list
maxTemp = []
for temp in tempList:
    maxTemp.append(math.ceil(temp['temp_max'] * 100 / 100))

#finding the maxTemperature of each day
def maxTemperature(maxTemp, timeList):
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
    outputTemp = maxT + maxT2 + maxT3 + maxT3 + maxT5
    outputDate = newDate0 + newDate1 + newDate2 + newDate3 + newDate4 + newDate5
    return  outputTemp,outputDate



#construct the time list in String format
dayList = []
for day in timeList:
    newDay = day.strftime('%A, %B %d, %H:%m %p')
    dayList.append(newDay)

day = maxTemperature(maxTemp, timeList)[1]

#get the maximum humidity
#def getMaxHumidity(day, dayTime):



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
        return  "Extreme Caution: Heat stroke, heat cramps, or heat exhaustion possible with problonged exposure and/or physical activity"
    elif 103 <= heatIndex <= 124:
        return "Danger: Heat cramps or heat exhaustion likely, and heat stroke possible with prolonged exposure and/or physical activity"
    elif 125 <= heatIndex:
        return  "Extreme Danger: Heat stroke highly likely"


maxTemp = np.array(maxTemp)
humidity = np.array(humidityList)
heatIndex = []
for temperature, humidity in zip(maxTemp, humidityList):
    heatIndex.append(simpleHeatIndex(temperature,humidity))

heatIndex = np.array(heatIndex).tolist()



#turn the list into data frame
table = pd.DataFrame({'Temperature' : maxTemp})
table['Humidity'] = humidityList
table['Time'] = dayList
table['Heat Index'] = heatIndex

#store the tweet for the next five days
tweetList = []
index = len(table)
i = 0
while i < index:
    dict = table.iloc[i].to_dict()
    tweet = 'On ' + dict['Time'] + ' ,the heat index is ' + str(dict['Heat Index']) + ' .The temperature reaches ' + \
            str(dict['Temperature']) + ' with humidity up to ' + str(dict['Humidity']) + ' percent.'
    tweetList.append(tweet)
    i += 1






tweetOut = ''.join(tweetList[0])
#Tweet the list of data
#api.update_status(tweetOut)




