# import libraries
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import utils
import actuality
import weather
import pandas as pd
import os


#------------- User settings ---------------------
NB_DAYS_TO_FETCH = 90 # Insert the number of day required between ()
weather.COUNTRY_WEATHER = "toronto"  # Choise country weather
REDDIT_TARGET_URL = "https://new.reddit.com/r/bapcsalescanada/new/"
DEBUG_MODE_ENABLE = True # To save time, use the local file
EXPORT_CSV_ENABLE = True # Exporte dataframe posts
weather.PATH_GECKO_DRIVER = "PLACE HERE YOUR PATH GECKO DRIVER !"
#-------------------------------------------------


#----------- First part -------------


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
              'index', 'id', 'title', 'score'], axis=1, inplace=True)

# Export CSV if needed
if EXPORT_CSV_ENABLE:
    # Create a datas directory
    dataDir = 'data'
    if not os.path.exists(dataDir):
        os.mkdir(dataDir)
    dfPosts.to_csv(dataDir + '/posts_weather.csv')


#----------- Second part -------------


# Analyze et visualize the datas
df_csv = pd.read_csv('data/posts_weather.csv')

# Grouping of comment counters with one total counter per day
dfPostsSum = pd.DataFrame([], columns=['intCreated','strCreated', 'date', 'nbComments','temp_avg','dew_avg','hum_avg','wind_avg','pres_avg'])
lastDay = ""
commentsSum = 0
for i in range(len(df_csv)):
    postDate = utils.timestamp_to_datetime(df_csv['intCreated'].iloc[i])
    weatherMonth = df_csv['date'].iloc[i]
    if lastDay == "":
        lastDay = weatherMonth # First date
    elif lastDay != weatherMonth:
        postDay['nbComments'] = commentsSum
        commentsSum = 0
        lastDay = weatherMonth
        dfPostsSum = dfPostsSum.append(postDay)
    postDay = df_csv.iloc[i][1:]
    commentsSum += df_csv['nbComments'].iloc[i]
    if i == len(df_csv)-1:
        if commentsSum > 0:
            postDay['nbComments'] = commentsSum
            dfPostsSum = dfPostsSum.append(postDay)

# Sorting and reindexing dataframe
dfPostsSum = dfPostsSum.sort_values('intCreated', ascending=True)
dfPostsSum = dfPostsSum.reset_index()

# Showing temperature and comments counters
fig, ax1 = plt.subplots()

# ax1.set_title("Correlation graph between\n Temperature and Comments")  # Add a title to the axes.
plt.xticks(rotation=45)

color1 = 'tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('nb comments', color=color1)
ax1.plot(dfPostsSum['date'], dfPostsSum['nbComments'], label='NbComments', color=color1)
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color2 = 'tab:blue'
ax2.set_ylabel('temp_avg', color=color2)  # we already handled the x-label with ax1
ax2.plot(dfPostsSum['date'], dfPostsSum['temp_avg'], label='TempAvg', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.savefig(dataDir + "/correlation1")
plt.show()


# Adjusting data for stacked bars
maxComments = dfPostsSum['nbComments'].max()
minComments = dfPostsSum['nbComments'].min()
maxTemp = dfPostsSum['temp_avg'].max()
minTemp = dfPostsSum['temp_avg'].min()
ratio = (maxComments - minComments) / (maxTemp-minTemp)
dfPostsSum['temp_avg'] = (dfPostsSum['temp_avg']-minTemp) * ratio

# From raw value to percentage
totals = [i + j for i, j in zip(dfPostsSum['nbComments'], dfPostsSum['temp_avg'])]
commentBars = [i / j * 100 for i, j in zip(dfPostsSum['nbComments'], totals)]
tempBars = [i / j * 100 for i, j in zip(dfPostsSum['temp_avg'], totals)]

# plot
barWidth = 0.85
# Create comments Bars
plt.bar(range(len(dfPostsSum)), commentBars, color='#b5ffb9', edgecolor='white', width=barWidth, label='Comments')
# Create temperature Bars
plt.bar(range(len(dfPostsSum)), tempBars, bottom=commentBars, color='#f9bc86', edgecolor='white', width=barWidth, label='Temp')

# Custom x axis
plt.xticks(range(len(dfPostsSum)), dfPostsSum['date'], rotation=45)
plt.xlabel("date")
plt.legend()
# plt.title("Correlation graph between\n Temperature and Comments")  # Add a title to the axes.
plt.savefig(dataDir + "/correlation2")

# Show graphic
plt.show()
