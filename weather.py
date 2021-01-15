from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import reduce
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime
import time
import re
import os

from Reddit import utils

PATH_GECKO_DRIVER = ""
COUNTRY_WEATHER = ""

def _convert_units(df):
    """
    Convert string to numeric units :
        - Fahrenheit to Celsius,
        - mph to kmh,
        - Hg to milibar,
        - in to mm

    :param df: pandas DataFrame to convert
    :return: pandas DataFrame converted
    """

    # First we need to convert the dataframe to numeric type
    # Select all the columns except Date
    cols = df.columns.drop('date')
    # Convert all columns except date to numeric
    df[cols] = df[cols].apply(pd.to_numeric)

    # select columns to apply the Fahrenheit to Celsius formula to
    cols_convert = df.columns[1:7]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: (x - 32) * 5 / 9)

    # select columns to apply the mph to kmh formula to
    cols_convert = df.columns[10:13]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x * 1.60934)

    # select columns to apply the Hg to milibar formula to
    cols_convert = df.columns[13:16]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x * 33.8639)

    # select columns to apply the in to mm formula to
    cols_convert = df.columns[16]
    # apply formula to those columns
    df[cols_convert] = df[cols_convert].apply(lambda x: x * 25.4)

    return df


def _render_page(targetUrl: str, debugMode: bool = False) -> str:
    """
    Fetch html page after loading javascript with using webDriver.
    Nota: This function use an interactive window. Firstly you must
    copy gecko engine and You must authorize access to the network

    :param targetUrl: URL of target website
    :param debugMode: True means that use local file and create if needed
    :return: dynamic html content
    """

    # Create a temporary directory if needed
    tempDir = 'temp'
    if not os.path.exists(tempDir):
        os.mkdir(tempDir)

    fileName = ""
    pattern = r"[^\/]+$"
    matches = re.search(pattern, targetUrl)
    if matches:
        fileName = matches.group(0)
    # The local file name is built with the date
    localFile = tempDir + "\\weather_" + fileName + '.html'
    if not debugMode or (debugMode and not os.path.isfile(localFile)):
        # Download web page

        driver = webdriver.Firefox(
            executable_path = PATH_GECKO_DRIVER)
        driver.get(targetUrl)
        # Wait for javascript render
        try:
            simpleWait = True
            if simpleWait:
                # Simple pause
                time.sleep(3)
            else:
                # Waiting specific element
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "legend-key"))
                )
        finally:
            webpage = driver.page_source
            driver.quit()

        # Save web page in local file
        f = open(localFile, mode="w", encoding='utf-8')
        f.write(webpage)  # Save pretty format
        f.close()

    else:
        # Read the file containing the web page
        f = open(localFile, mode="r", encoding='utf-8')
        webpage = f.read()
        f.close()

    return webpage


def _scraper(page: str, dates: [], debugMode: bool = False) -> pd.DataFrame:
    """
    Scraping weather page and build a summary table

    :param page: first part of target website url
    :param dates: months table
    :return: list summary of weather months
    """
    output = pd.DataFrame()

    for d in dates:

        url = str(str(page) + str(d))

        webpage = _render_page(url, debugMode)

        soup = BeautifulSoup(webpage, "html.parser")
        container = soup.find('lib-city-history-observation')
        check = container.find('tbody')

        data = []

        for c in check.find_all('tr', class_='ng-star-inserted'):
            for i in c.find_all('td', class_='ng-star-inserted'):
                trial = i.text
                trial = trial.strip('  ')
                data.append(trial)

        nbDays = list.index(data, 'Max')
        date = pd.DataFrame(data[1:nbDays], columns=['date'])

        data = data[nbDays:] # Drop element date
        temperature = pd.DataFrame([data[3:nbDays*3][x:x + 3] for x in range(0, nbDays*3, 3)][:-1],
                                   columns=['temp_max', 'temp_avg', 'temp_min'])
        data = data[nbDays*3:] # Drop element temperature
        dew_point = pd.DataFrame([data[3:nbDays*3][x:x + 3] for x in range(0, nbDays*3, 3)][:-1],
                                   columns=['dew_max', 'dew_avg', 'dew_min'])
        data = data[nbDays*3:] # Drop element temperature
        humidity = pd.DataFrame([data[3:nbDays*3][x:x + 3] for x in range(0, nbDays*3, 3)][:-1],
                                   columns=['hum_max', 'hum_avg', 'hum_min'])
        data = data[nbDays*3:] # Drop element humidity
        wind = pd.DataFrame([data[3:nbDays*3][x:x + 3] for x in range(0, nbDays*3, 3)][:-1],
                                   columns=['wind_max', 'wind_avg', 'wind_min'])
        data = data[nbDays*3:] # Drop element wind
        pressure = pd.DataFrame([data[3:nbDays*3][x:x + 3] for x in range(0, nbDays*3, 3)][:-1],
                                   columns=['pres_max', 'pres_avg', 'pres_min'])
        data = data[nbDays*3:] # Drop element pressure
        precipitation = pd.DataFrame(data[1:nbDays], columns=['precipitation'])

        dfs = [date, temperature, dew_point, humidity, wind, pressure, precipitation]
        df_final = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True), dfs)

        df_final['date'] = pd.to_datetime(df_final.iloc[:, 0].astype(int), unit='D', origin=(pd.Timestamp(str(d)+'-01') - pd.Timedelta(days=1)))

        # Convert untis : Fahrenheit to Celsius, mph to kmh, etc.
        df_final = _convert_units(df_final)

        output = output.append(df_final)

        print("Weather month : " + str(d) )

    print('--- Weather scraper done! ---')

    output = output[['temp_avg', 'temp_min', 'dew_max', 'dew_avg', 'dew_min', 'hum_max',
                     'hum_avg', 'hum_min', 'wind_max', 'wind_avg', 'wind_min', 'pres_max',
                     'pres_avg', 'pres_min', 'precipitation', 'date']]

    return output


def getMonthly(firstDate: datetime, lastDate: datetime, debugMode: bool = False) -> pd.DataFrame:
    """
    get sommary weather

    :param month:
    :return:
    """

    months = []
    nbMonth = utils.diff_month(firstDate, lastDate) + 1
    for i in range(nbMonth):
        months.append(str(firstDate.year) + '-' + str(firstDate.month))
        firstDate = firstDate - relativedelta(months=1)

    # months = ['2020-12', '2021-1'] #Example
    page = "https://www.wunderground.com/history/monthly/ca/" + COUNTRY_WEATHER + "/CYTZ/date/"
    df_output = _scraper(page, months, debugMode)
    return df_output
