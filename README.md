The Sun : the worst enemy of social networks ?
================================================


![img](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Ffondation-valentin-ribet.org%2Fwp-content%2Fuploads%2F2016%2F12%2Flogo-simplon.gif&f=1&nofb=1.png)

# Context 

We are part of a team of data scientists in a business selling computer components to individuals (B2C). Our communication primarily involves posting content on social networks, in particular Reddit.

However, communications managers have raised their questions about the publication date of certain content, which seems to have an impact on the number of views and comments posted. One would almost suspect that computer hardware enthusiasts go outside on a sunny day.

Our manager therefore asked you to carry out a study on the impact of weather on the number of returns on company publications. It is important to be able to repeat this analysis throughout the year.


Tracking:

The first step consists of tackle the recovery of the post tracking level on Reddit. For example, we can focus on the number of votes, the number of comments, the length of time on the first page, etc.

Then retrieving the meteorological data for the days concerned. According to the communications team, temperatures, risk of rain, wind strength and other information can be retrieved from many websites, such as weather.com.

This correctly retrieved, processed and cleaned data will then have to be linked, in order to highlight the presence of a possible correlation.


This project is made to compare some weather data and the percentage of subreddit publication, to see if there is a correlation between weather and outings.

## Scraping reddit by using BeautifulSoup4

```bash
$ pip3 install BeautifulSoup4
$ pip3 install requests
```


## Scraping weather underground by using Selenium and BeautifulSoup4

```bash
$ pip3 install Selenium
$ pip3 install Gecko
$ pip3 install selenium
```


## Merging the result in one unique .CSV file

```bash
$ pip3 install pandas

```


## Build plots and charts

```bash
$ pip3 install matplotlib
$ pip3 install seaborn

```
