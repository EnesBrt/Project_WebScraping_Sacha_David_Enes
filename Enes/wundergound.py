import requests
from bs4 import BeautifulSoup as BS
import pandas as pd
from functools import reduce
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
url = "https://www.wunderground.com/history/monthly/pt/lisbon/LPPT/date/"

def render_page(url):
    firefoxOptions = Options()
    firefoxOptions.add_argument("-headless")
    driver = webdriver.Firefox(executable_path='/home/enes/geckodriver')
    driver.get(url)
    time.sleep(3)
    r = driver.page_source
    driver.quit()
    return r
render_page('https://www.wunderground.com/history/monthly/pt/lisbon/LPPT/date/') 

def convert_units(df):
    # First we need to convert the dataframe to numeric type
    # Select all the columns except Date
    cols = df.columns.drop('Date')
    # Convert all columns except date to numeric
    df[cols] = df[cols].apply(pd.to_numeric)

    # select columns to apply the Fahrenheit to Celsius formula to
    cols_convert = df.columns[0:6]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: (x-32)*5/9)

    # select columns to apply the mph to kmh formula to
    cols_convert = df.columns[9:12]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x*1.60934)

    # select columns to apply the Hg to milibar formula to
    cols_convert = df.columns[12:15]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x*33.8639)

    # select columns to apply the in to mm formula to
    cols_convert = df.columns[15:16]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x*25.4)
    
    return df

def scraper(page,dates):
    output = pd.DataFrame()

    for d in dates:

        url = str(str(page)+str(d))

        r = render_page(url)

        soup = BS(r, "html.parser")
        container = soup.find('lib-city-history-observation')
        check = container.find('tbody')

        data=[]

        for c in check.find_all('tr',class_='ng-star-inserted'):
            for i in c.find_all('td',class_='ng-star-inserted'):
                trial = i.text
                trial = trial.strip('  ')
                data.append(trial)

        if round(len(data)/17-1)==31:
            Temperature = pd.DataFrame([data[32:128][x:x+3] for x in range(0, len(data[32:128]),3)][1:],columns=['Temp_max','Temp_avg','Temp_min'])
            Dew_Point = pd.DataFrame([data[128:224][x:x+3] for x in range(0, len(data[128:224]),3)][1:],columns=['Dew_max','Dew_avg','Dew_min'])
            Humidity = pd.DataFrame([data[224:320][x:x+3] for x in range(0, len(data[224:320]),3)][1:],columns=['Hum_max','Hum_avg','Hum_min'])
            Wind = pd.DataFrame([data[320:416][x:x+3] for x in range(0, len(data[320:416]),3)][1:],columns=['Wind_max','Wind_avg','Wind_min'])
            Pressure = pd.DataFrame([data[416:512][x:x+3] for x in range(0, len(data[416:512]),3)][1:],columns=['Pres_max','Pres_avg','Pres_min'])
            Date = pd.DataFrame(data[:32][1:],columns=data[:1])
            Precipitation = pd.DataFrame(data[512:][1:],columns=['Precipitation'])
            print(str(str(d)+' finished!'))
        elif round(len(data)/17-1)==28:
            Temperature = pd.DataFrame([data[29:116][x:x+3] for x in range(0, len(data[29:116]),3)][1:],columns=['Temp_max','Temp_avg','Temp_min'])
            Dew_Point = pd.DataFrame([data[116:203][x:x+3] for x in range(0, len(data[116:203]),3)][1:],columns=['Dew_max','Dew_avg','Dew_min'])
            Humidity = pd.DataFrame([data[203:290][x:x+3] for x in range(0, len(data[203:290]),3)][1:],columns=['Hum_max','Hum_avg','Hum_min'])
            Wind = pd.DataFrame([data[290:377][x:x+3] for x in range(0, len(data[290:377]),3)][1:],columns=['Wind_max','Wind_avg','Wind_min'])
            Pressure = pd.DataFrame([data[377:464][x:x+3] for x in range(0, len(data[377:463]),3)][1:],columns=['Pres_max','Pres_avg','Pres_min'])
            Date = pd.DataFrame(data[:29][1:],columns=data[:1])
            Precipitation = pd.DataFrame(data[464:][1:],columns=['Precipitation'])
            print(str(str(d)+' finished!'))
        elif round(len(data)/17-1)==29:
            Temperature = pd.DataFrame([data[30:120][x:x+3] for x in range(0, len(data[30:120]),3)][1:],columns=['Temp_max','Temp_avg','Temp_min'])
            Dew_Point = pd.DataFrame([data[120:210][x:x+3] for x in range(0, len(data[120:210]),3)][1:],columns=['Dew_max','Dew_avg','Dew_min'])
            Humidity = pd.DataFrame([data[210:300][x:x+3] for x in range(0, len(data[210:300]),3)][1:],columns=['Hum_max','Hum_avg','Hum_min'])
            Wind = pd.DataFrame([data[300:390][x:x+3] for x in range(0, len(data[300:390]),3)][1:],columns=['Wind_max','Wind_avg','Wind_min'])
            Pressure = pd.DataFrame([data[390:480][x:x+3] for x in range(0, len(data[390:480]),3)][1:],columns=['Pres_max','Pres_avg','Pres_min'])
            Date = pd.DataFrame(data[:30][1:],columns=data[:1])
            Precipitation = pd.DataFrame(data[480:][1:],columns=['Precipitation'])
            print(str(str(d)+' finished!'))
        elif round(len(data)/17-1)==30:
            Temperature = pd.DataFrame([data[31:124][x:x+3] for x in range(0, len(data[31:124]),3)][1:],columns=['Temp_max','Temp_avg','Temp_min'])
            Dew_Point = pd.DataFrame([data[124:217][x:x+3] for x in range(0, len(data[124:217]),3)][1:],columns=['Dew_max','Dew_avg','Dew_min'])
            Humidity = pd.DataFrame([data[217:310][x:x+3] for x in range(0, len(data[217:310]),3)][1:],columns=['Hum_max','Hum_avg','Hum_min'])
            Wind = pd.DataFrame([data[310:403][x:x+3] for x in range(0, len(data[310:403]),3)][1:],columns=['Wind_max','Wind_avg','Wind_min'])
            Pressure = pd.DataFrame([data[403:496][x:x+3] for x in range(0, len(data[403:496]),3)][1:],columns=['Pres_max','Pres_avg','Pres_min'])
            Date = pd.DataFrame(data[:31][1:],columns=data[:1])
            Precipitation = pd.DataFrame(data[496:][1:],columns=['Precipitation'])
            print(str(str(d)+' finished!'))
        else:
            print('Data not in normal length')

        dfs = [Date, Temperature, Dew_Point, Humidity, Wind, Pressure, Precipitation]

        df_final =reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True), dfs)

        df_final['Date'] = str(d) +"-"+ df_final.iloc[:,:1].astype(str)
        
        df_final = convert_units(df_final)
        
        output = output.append(df_final)
        
    print('Scraper done!')

    output = output[['Temp_avg', 'Temp_min', 'Dew_max', 'Dew_avg', 'Dew_min', 'Hum_max',
                        'Hum_avg', 'Hum_min', 'Wind_max', 'Wind_avg', 'Wind_min', 'Pres_max',
                        'Pres_avg', 'Pres_min', 'Precipitation', 'Date']]
    
    return output

dates = ['2020-5']
page = 'https://www.wunderground.com/history/monthly/pt/lisbon/LPPT/date/'

scraper(page,dates)
