import pyowm
from datetime import datetime
import datetime as dt
import math
import tweepy as twp
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors
import matplotlib.patches as mpatches

########################### CONFIG ############################
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

# finding the maxTemperature of each day
def getTempTimeData():
    tempoTempData = getData()[0]
    tempoTimeData = getData()[2]
    minimum0 = 0
    minimum1 = 0
    minimum2 = 0
    minimum3 = 0
    minimum4 = 0
    minimum5 = 0
    listTempTime = zip(tempoTempData, tempoTimeData)
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

# Obtain the highest humidity of the day with the highest temperature
def getHumidity():
    tempoHumidityData = getData()[1]
    timeFinalData = getTempTimeData()[1]
    tempoTimeData = getData()[2]
    listHumidity = zip(tempoHumidityData,tempoTimeData)
    humidityList = []
    for humidity,timeTempo in listHumidity:
        for time in timeFinalData:
            if(time == timeTempo):
                humidityList.append(humidity)

    return humidityList

#Format time Object into String
def dayInString():
    timeFinalData = getTempTimeData()[1]
    dayString = []
    for day in timeFinalData:
        newDay = day.strftime('%A %m/%d at %-I%p')
        dayString.append(newDay)
    return dayString

#the formula is calculated first
def simpleHeatIndex(temperature, humidity):
    answer = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (humidity * 0.094))
    return math.ceil(answer * 100 / 100)

#the heat index is then compared. If it is 80 or higher, the full formula is applied
def fullHeatIndex(temperature, humidity):
    heatIndex = -42.379 + 2.04901523 * temperature + 10.14333127 * humidity - .22475541 * temperature * humidity - \
                .00683783 * temperature * temperature - .05481717 * humidity * humidity + .00122874 * temperature * \
                temperature * humidity + .00085282 * temperature * humidity * humidity - \
                .00000199 * temperature * temperature * humidity * humidity

    if temperature > 80 and temperature < 112 and humidity < 0.13:
        subtractionheat = ((13 - humidity)/4) * math.sqrt((17 - abs(temperature - 95)) / 17)
        return heatIndex - subtractionheat
    elif humidity > 0.85 and temperature > 80 and temperature < 87:
        additionheat = ((humidity - 85) / 10) * ((87 - temperature ) / 5)
        return heatIndex + additionheat
    else:
        return math.ceil(heatIndex * 100 / 100)

#determine the actual heat index
def finalHeatIndex(temperature, humidity):
    if simpleHeatIndex(temperature,humidity) >= 80:
        return round(fullHeatIndex(temperature, humidity))
    else:
        return round(simpleHeatIndex(temperature,humidity))

#determine the recommendation
def recommendation(heatIndex):
    if 80 <= heatIndex < 90:
        return "Caution: Fatigue possible with prolonged exposure and/or physical activity"
    elif 90 <= heatIndex < 103:
        return "Extreme Caution: Heat stroke, heat cramps, or heat exhaustion possible with problonged exposure " \
               "and/or physical activity"
    elif 103 <= heatIndex <= 124:
        return "Danger: Heat cramps or heat exhaustion likely, and heat stroke possible with prolonged exposure " \
               "and/or physical activity"
    elif 125 <= heatIndex:
        return "Extreme Danger: Heat stroke highly likely"

# Calculate the heat data using the temperature data and humidity data
# return heat indexes as a list
def getHeatData(temperatureFinalData, humidityFinalData):
    maxTemp = np.array(temperatureFinalData)
    humidityList = np.array(humidityFinalData)
    heatIndex = []
    for temperature, humidity in zip(maxTemp, humidityList):
       heatIndex.append(finalHeatIndex(temperature,humidity))

    heatIndex = np.array(heatIndex).tolist()
    return heatIndex

#store the tweet for the next five days
#turn the data into data frame and return a list of String for the tweet.
def getTweet():
    temperatureFinalData = getTempTimeData()[0]
    humidityFinalData = getHumidity()
    timeFinalData = dayInString()
    heatFinalData = getHeatData(temperatureFinalData, humidityFinalData)
    table = pd.DataFrame({'Temperature': temperatureFinalData})
    table['Humidity'] = humidityFinalData
    table['Time'] = timeFinalData
    table['Heat Index'] = heatFinalData
    tweetList = []
    index = len(table)
    i = 0
    while i < index - 3:
        dict = table.iloc[i].to_dict()
        tweet = dict['Time'] + ', Heat Index: ' + str(dict['Heat Index']) + ', Temperature: ' + str(dict['Temperature']) \
                + 'F and Humidity: ' + str(dict['Humidity']) + '%.' + "\n" + "\n"
       # tweet = 'On ' + dict['Time'] + ' , the heat index is ' + str(dict['Heat Index']) + '.The temperature is ' + \
       #         str(dict['Temperature']) + ' with humidity reaches ' + str(dict['Humidity']) + '%.' + "\n"
        tweetList.append(tweet)
        i += 1

    # add recommendation line
    # currHeat = table.iloc[0].to_dict()
    # tweetList.append(recommendation(currHeat['Heat Index']))

    #return the tweet and the data for the upcoming five days
    return tweetList, table.iloc[0], table.iloc[1],table.iloc[2], table.iloc[3],table.iloc[4]

# return the maximum temperature and humidity for the current day
def getMaxTempandHumidity():
    dict = getTweet()[1].to_dict()
    return dict['Temperature'],dict['Humidity']

# return the maximum temperature and humidity for the first next day
def getMaxTempandHumidityFirst():
    dict = getTweet()[2].to_dict()
    return dict['Temperature'], dict['Humidity']

# return the maximum temperature and humidity for the second next day
def getMaxTempandHumiditySecond():
    dict = getTweet()[3].to_dict()
    return dict['Temperature'], dict['Humidity']

# return the maximum temperature and humidity for the third next day
def getMaxTempandHumidityThird():
    dict = getTweet()[4].to_dict()
    return dict['Temperature'], dict['Humidity']

# return the maximum temperature and humidity for the fourth next day
def getMaxTempandHumidityFourth():
    dict = getTweet()[5].to_dict()
    return dict['Temperature'], dict['Humidity']

#get the index to plot on the graph
def getIndex(humidity, temperature, table_matrix):
        xIndex = 0
        yIndex = 0
        counterX = 0
        counterY = 0
        for temperatureInTable in table_matrix.columns:
            if temperature == temperatureInTable:
                xIndex = counterX
            counterX += 1

        for humidityInTable in table_matrix.index:
            if humidity == humidityInTable:
                yIndex = counterY
            counterY += 1

        if yIndex != 0:
            yIndex = yIndex - 1

        if xIndex != 0:
            xIndex = xIndex - 1

        return xIndex, yIndex

#rounding for temperature -> testCode -> make an edit
def roundTemp(temperature):
    if 80 <= temperature <= 100:
        if 80 <= temperature <= 82:
            temperature = 82
        elif 82 <= temperature <= 84:
            temperature = 84
        elif 84 <= temperature <= 86:
            temperature = 86
        elif 86 <= temperature <= 88:
            temperature = 88
        elif 88 <= temperature <= 90:
            temperature = 90
        elif 90 <= temperature <= 92:
            temperature = 92
        elif 92 <= temperature <= 94:
            temperature = 94
        elif 94 <= temperature <= 96:
            temperature = 96
        elif 96 <= temperature <= 98:
            temperature = 98
        elif 98 <= temperature <= 100:
            temperature = 100
    return temperature


#rounding for humidity -> test code
def roundHumidity(humidity):
    if 40 <= humidity <= 110:
        if 40 <= humidity <= 45:
            humidity = 45
        elif 45 <= humidity <= 50:
            humidity = 50
        elif 50 <= humidity <= 55:
            humidity = 55
        elif 55 <= humidity <= 60:
            humidity = 60
        elif 60 <= humidity <= 65:
            humidity = 65
        elif 65 <= humidity <= 70:
            humidity = 70
        elif 70 <= humidity <= 75:
            humidity = 75
        elif 75 <= humidity <= 80:
            humidity = 80
        elif 80 <= humidity <= 85:
            humidity = 85
        elif 85 <= humidity <= 90:
            humidity = 90
        elif 90 <= humidity <= 95:
            humidity = 95
        elif 95 <= humidity <= 100:
            humidity = 100
        elif 100 <= humidity <= 105:
            humidity = 105
        elif 105 <= humidity <= 110:
            humidity = 110

        return humidity


def getTableMatrix():
    # Relative Humidity
    RH = [40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40,
          45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,
          50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50,
          55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55,
          60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
          65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65,
          70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70,
          75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75,
          80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80,
          85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85, 85,
          90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90,
          95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95,
          100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    RH.sort(reverse=True)

    # Temperature in F
    T = [80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110,
         80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110]

    # Heat Index
    HI = [87, 95, 103, 112, 121, 132, 143, 155, 168, 181, 195, 210, 226, 243, 260, 278,
          86, 93, 100, 108, 117, 127, 137, 148, 160, 172, 185, 199, 214, 229, 245, 262,
          86, 91, 98, 105, 113, 122, 131, 141, 152, 164, 176, 189, 202, 216, 231, 247,
          85, 90, 96, 102, 110, 117, 126, 135, 145, 155, 167, 179, 191, 204, 218, 233,
          84, 89, 94, 100, 106, 113, 121, 129, 138, 148, 158, 169, 181, 193, 205, 219,
          84, 88, 92, 97, 103, 109, 116, 124, 132, 141, 150, 160, 171, 182, 193, 206,
          83, 86, 90, 95, 100, 105, 112, 119, 126, 134, 143, 152, 161, 172, 182, 194,
          82, 85, 89, 93, 98, 103, 108, 114, 121, 128, 136, 144, 153, 162, 172, 182,
          82, 84, 88, 91, 95, 100, 105, 110, 116, 123, 129, 137, 145, 153, 162, 171,
          81, 84, 88, 89, 93, 97, 101, 106, 112, 117, 124, 130, 137, 145, 153, 161,
          81, 83, 85, 88, 91, 95, 99, 103, 108, 113, 118, 124, 131, 137, 144, 152,
          80, 82, 84, 87, 89, 93, 96, 100, 104, 109, 114, 119, 124, 130, 137, 143,
          80, 81, 83, 85, 88, 91, 94, 97, 101, 105, 109, 114, 119, 124, 130, 136]

    # Turn the data into a table
    table = pd.DataFrame({"Relative Humidity": RH})
    table["Temperature"] = T
    table["Heat Index"] = HI

    # Turn the data into matrix
    table_matrix = table.pivot("Relative Humidity", "Temperature", "Heat Index")

    return table_matrix



def getCurrIndex():

    #check the temp and humdiity for rounding
    maxTemp = roundTemp(getMaxTempandHumidity()[0])
    maxHumidity = roundHumidity(getMaxTempandHumidity()[1])
    table_matrix = getTableMatrix()

    #get the index
    xIndex = getIndex(maxHumidity, maxTemp, table_matrix)
    yIndex = getIndex(maxHumidity, maxTemp, table_matrix)

   # print(maxTemp, maxHumidity)

    return xIndex, yIndex
# return the index for the following first day
def getFirsDayIndex():
    # check the temp and humdiity for rounding
    maxTemp = roundTemp(getMaxTempandHumidityFirst()[0])
    maxHumidity = roundHumidity(getMaxTempandHumidityFirst()[1])
    table_matrix = getTableMatrix()

    # get the index
    xIndex = getIndex(maxHumidity, maxTemp, table_matrix)
    yIndex = getIndex(maxHumidity, maxTemp, table_matrix)

    return xIndex, yIndex

# return the index for the following second day
def getSecondDayIndex():
    # check the temp and humdiity for rounding
    maxTemp = roundTemp(getMaxTempandHumiditySecond()[0])
    maxHumidity = roundHumidity(getMaxTempandHumiditySecond()[1])
    table_matrix = getTableMatrix()

    # get the index
    xIndex = getIndex(maxHumidity, maxTemp, table_matrix)
    yIndex = getIndex(maxHumidity, maxTemp, table_matrix)

    return xIndex, yIndex

# return the index for the following third day
def getThirdDayIndex():
    # check the temp and humdiity for rounding
    maxTemp = roundTemp(getMaxTempandHumidityThird()[0])
    maxHumidity = roundHumidity(getMaxTempandHumidityThird()[1])
    table_matrix = getTableMatrix()

    # get the index
    xIndex = getIndex(maxHumidity, maxTemp, table_matrix)
    yIndex = getIndex(maxHumidity, maxTemp, table_matrix)

    return xIndex, yIndex

# return the index for the following fourth day
def getFourthDayIndex():
    # check the temp and humdiity for rounding
    maxTemp = roundTemp(getMaxTempandHumidityFourth()[0])
    maxHumidity = roundHumidity(getMaxTempandHumidityFourth()[1])
    table_matrix = getTableMatrix()

    # get the index
    xIndex = getIndex(maxHumidity, maxTemp, table_matrix)
    yIndex = getIndex(maxHumidity, maxTemp, table_matrix)

    return xIndex, yIndex



#Function to construct the heat map and plot today's index
def runGraph():
    # set up the color ranges
    cmap = colors.ListedColormap(['gold', 'goldenrod', 'orange', 'red'])
    bounds = [80, 90, 103, 124, 278]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    # set up the heat map
    plt.figure()
    fig, ax = plt.subplots(1, 1, figsize=(11, 8))

    # get the table matrix for plotting
    table_matrix = getTableMatrix()

    ax.imshow(table_matrix, cmap=cmap, norm=norm)  # make the heatmap

    #get the indexes for five days
    currXIndex = getCurrIndex()[0]
    currYIndex = getCurrIndex()[1]

    onedayXIndex = getFirsDayIndex()[0]
    onedayYIndex = getFirsDayIndex()[1]

    seconddayXIndex = getSecondDayIndex()[0]
    secondayYIndex = getSecondDayIndex()[1]

    thirddayxIndex = getThirdDayIndex()[0]
    thirddayyIndex = getThirdDayIndex()[1]

    fourthdayxIndex = getFourthDayIndex()[0]
    fourthdayyIndex = getFourthDayIndex()[1]

    #plot the indexes
    # ax.scatter(currXIndex, currYIndex, color = 'black', linewidth = 10)
    # ax.scatter(onedayXIndex, onedayYIndex, color = 'gray', linewidth = 10)
    # ax.scatter(seconddayXIndex, secondayYIndex, color = 'gray', linewidth = 10)
    # ax.scatter(thirddayxIndex, thirddayyIndex, color = 'gray', linewidth = 10)
    # ax.scatter(fourthdayxIndex, fourthdayyIndex, color = 'gray', linewidth = 10)


    # set up the axis and title
    ax.set_xticklabels(table_matrix.columns)
    ax.set_yticklabels(table_matrix.index)
    tick_spacing = 1
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax.set_title("Heat Index Chart", loc = 'left')
    ax.set_xlabel('Temperature (F)', fontsize = 14)
    ax.xaxis.set_label_position('top')
    ax.set_ylabel('Relative Humidity (%)', fontsize = 14)
    ax.xaxis.tick_top()

    # Set up the labeling colors and legend
    gold_patch = mpatches.Patch(color='gold', label='Caution')
    goldenrod_patch = mpatches.Patch(color='goldenrod', label='Extreme Caution')
    orange_patch = mpatches.Patch(color='orange', label='Danger')
    red_patch = mpatches.Patch(color='red', label='Extreme Danger')
    point_patch = mpatches.Patch(color='black', label='Today Weather Feels')
    future_patch = mpatches.Patch(color='gray', label = 'Upcoming Five Days Feel')
    past_patch = mpatches.Patch(color = 'silver', label = 'Hottest Day in 2018')
    plt.legend(handles=[gold_patch, goldenrod_patch, orange_patch, red_patch, point_patch, future_patch, past_patch],
               loc='upper center', bbox_to_anchor=(0.5, -0.0125), fancybox=True, shadow=True, ncol=4,
               title = 'Likelihood of Heat Disorders with Prolonged Exposure or Strenous Activity')

    # show the heatmap
    plt.show()

# Run the bot
def runBot():
    tweetOut = ''.join(getTweet()[0])
    # Tweet the list of data
    api.update_status(tweetOut)

runBot()
#runGraph()
