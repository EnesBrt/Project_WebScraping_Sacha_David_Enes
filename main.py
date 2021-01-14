# import libraries
from datetime import datetime, timedelta
import utils
import actuality
import weather
import pandas as pd

#------------- User settings ---------------------
NB_DAYS_TO_FETCH = 90
REDDIT_TARGET_URL = "https://new.reddit.com/r/bapcsalescanada/new/"
DEBUG_MODE_ENABLE = True # To save time, use the local file
#-------------------------------------------------

# Retrieve the publications of the last days
startDate = datetime.now()
tillDate = startDate.today() - timedelta(NB_DAYS_TO_FETCH)
dfPosts = actuality.getLastPosts(REDDIT_TARGET_URL, tillDate, debugMode=DEBUG_MODE_ENABLE)

# Get the weather conditions for the last few months, from the first posting to the last
firstDate = utils.timestamp_to_datetime(dfPosts['intCreated'].iloc[0])
lastDate = utils.timestamp_to_datetime(dfPosts['intCreated'].iloc[-1])
dfWeathers = weather.getMonthly(firstDate, lastDate, debugMode=DEBUG_MODE_ENABLE)

# list weather columns
columns=['temp_avg', 'temp_min', 'dew_max', 'dew_avg', 'dew_min', 'hum_max',
                     'hum_avg', 'hum_min', 'wind_max', 'wind_avg', 'wind_min', 'pres_max',
                     'pres_avg', 'pres_min', 'precipitation', 'date']

# Match the weather data corresponding to each message
listWeatherPosts = []
dfWeatherPosts = pd.DataFrame([], columns=columns)
for i in range(len(dfPosts)):
    postDate = utils.timestamp_to_datetime(dfPosts['intCreated'].iloc[i])
    weatherMonth = str(postDate.year) + '-' + str(postDate.month) + '-' + str(postDate.day)
    weatherDay = dfWeathers.loc[dfWeathers['date'] == weatherMonth]
    dfWeatherPosts = pd.concat([dfWeatherPosts, weatherDay], axis=0)

# Reindex weather dataframe before merge with post dataframe
dfWeatherPosts = dfWeatherPosts.reset_index()
dfPosts = pd.concat([dfPosts, dfWeatherPosts], axis=1)
# Drop optional columns
dfPosts.drop(['temp_min', 'dew_max', 'dew_min', 'hum_max',
              'hum_min', 'wind_max', 'wind_min', 'pres_max',
              'pres_min', 'precipitation', 'upVoteRatio',
              'date', 'index', 'id', 'title', 'score'], axis=1, inplace=True)

# Export CSV if needed
dfPosts.to_csv('temp/soleil.csv')

